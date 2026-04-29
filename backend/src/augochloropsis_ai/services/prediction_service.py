from __future__ import annotations

import json
from collections.abc import Mapping

from fastapi import UploadFile
from sqlalchemy.orm import Session

from augochloropsis_ai.core.config import Settings, get_settings
from augochloropsis_ai.core.exceptions import ModelNotReadyError, NotFoundError
from augochloropsis_ai.db.models import Prediction
from augochloropsis_ai.ml.inference_pipeline import InferencePipeline, InferenceProbability
from augochloropsis_ai.repositories.model_repository import ModelRepository
from augochloropsis_ai.repositories.prediction_repository import PredictionRepository
from augochloropsis_ai.repositories.species_repository import SpeciesRepository
from augochloropsis_ai.schemas.prediction import (
    ModelVersionSummary,
    PredictionFeedbackUpdate,
    PredictionProbability,
    PredictionResponse,
    SpeciesSummary,
)
from augochloropsis_ai.services.storage_service import StorageService


class PredictionService:
    def __init__(
        self,
        *,
        settings: Settings | None = None,
        prediction_repository: PredictionRepository | None = None,
        species_repository: SpeciesRepository | None = None,
        model_repository: ModelRepository | None = None,
        storage_service: StorageService | None = None,
        inference_pipeline: InferencePipeline | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.prediction_repository = prediction_repository or PredictionRepository()
        self.species_repository = species_repository or SpeciesRepository()
        self.model_repository = model_repository or ModelRepository()
        self.storage_service = storage_service or StorageService(self.settings)
        self.inference_pipeline = inference_pipeline or InferencePipeline()

    async def create_prediction(
        self,
        db: Session,
        upload_file: UploadFile,
        model_version: str | None = None,
    ) -> PredictionResponse:
        selected_model = (
            self.model_repository.get_by_version(db, model_version)
            if model_version
            else self.model_repository.get_active_model(db)
        )
        if selected_model is None:
            if model_version:
                raise NotFoundError(f"Model version not found: {model_version}")
            raise ModelNotReadyError("No active model version is registered.")

        stored_upload = await self.storage_service.store_upload(upload_file)
        try:
            inference = self.inference_pipeline.predict_bytes(stored_upload.content, selected_model)
        except RuntimeError as exc:
            raise ModelNotReadyError(str(exc)) from exc

        codes = [item.species_code for item in inference.probabilities]
        species_map = self.species_repository.list_by_codes(db, codes)
        predicted_species = species_map.get(inference.predicted_species_code)
        if predicted_species is None:
            raise ModelNotReadyError(
                "The predicted species is not registered in the species table."
            )

        serialized_probabilities = self._serialize_probabilities(
            inference.probabilities,
            species_map,
        )
        prediction = self.prediction_repository.create_prediction(
            db,
            original_filename=stored_upload.original_filename,
            stored_path=stored_upload.relative_path,
            sha256=stored_upload.sha256,
            predicted_species=predicted_species,
            confidence=inference.confidence,
            probabilities_json=json.dumps(serialized_probabilities),
            model_version=selected_model,
            inference_ms=inference.inference_ms,
        )
        db.commit()
        db.refresh(prediction)
        return self._build_response(prediction, serialized_probabilities)

    def list_predictions(
        self,
        db: Session,
        limit: int = 50,
        offset: int = 0,
    ) -> list[PredictionResponse]:
        predictions = self.prediction_repository.list_predictions(db, limit=limit, offset=offset)
        return [self._build_response(prediction) for prediction in predictions]

    def get_prediction(self, db: Session, prediction_id: int) -> PredictionResponse:
        prediction = self.prediction_repository.get_prediction(db, prediction_id)
        if prediction is None:
            raise NotFoundError("Prediction not found.")
        return self._build_response(prediction)

    def set_feedback(
        self,
        db: Session,
        prediction_id: int,
        body: PredictionFeedbackUpdate,
    ) -> PredictionResponse:
        prediction = self.prediction_repository.update_feedback(
            db,
            prediction_id,
            body.user_feedback,
        )
        if prediction is None:
            raise NotFoundError("Prediction not found.")
        db.commit()
        db.refresh(prediction)
        return self._build_response(prediction)

    def _serialize_probabilities(
        self,
        probabilities: list[InferenceProbability],
        species_map: Mapping[str, object],
    ) -> list[dict[str, object]]:
        serialized = []
        for item in probabilities:
            species = species_map.get(item.species_code)
            serialized.append(
                {
                    "species_code": item.species_code,
                    "scientific_name": getattr(species, "scientific_name", None),
                    "probability": item.probability,
                }
            )
        return serialized

    def _build_response(
        self,
        prediction: Prediction,
        probabilities: list[dict[str, object]] | None = None,
    ) -> PredictionResponse:
        payload = probabilities or json.loads(prediction.probabilities_json)
        return PredictionResponse(
            prediction_id=prediction.id,
            image_url=f"{self.settings.uploads_mount_path}/{prediction.stored_path}",
            predicted_species=SpeciesSummary(
                id=prediction.predicted_species.id,
                code=prediction.predicted_species.code,
                scientific_name=prediction.predicted_species.scientific_name,
            ),
            confidence=prediction.confidence,
            probabilities=[PredictionProbability(**item) for item in payload],
            model_version=ModelVersionSummary(
                id=prediction.model_version.id,
                version=prediction.model_version.version,
                encoder_name=prediction.model_version.encoder_name,
                classifier_type=prediction.model_version.classifier_type,
            ),
            created_at=prediction.created_at,
            inference_ms=prediction.inference_ms,
            user_feedback=prediction.user_feedback,
        )
