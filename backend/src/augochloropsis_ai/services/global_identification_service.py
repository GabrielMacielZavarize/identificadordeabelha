from __future__ import annotations

import json
from time import perf_counter

from fastapi import UploadFile
from sqlalchemy.orm import Session

from augochloropsis_ai.core.config import Settings, get_settings
from augochloropsis_ai.db.models import GlobalIdentification
from augochloropsis_ai.ml.global_identifier import ClipGlobalIdentifier, get_global_identifier
from augochloropsis_ai.repositories.global_identification_repository import (
    GlobalIdentificationRepository,
)
from augochloropsis_ai.core.exceptions import NotFoundError
from augochloropsis_ai.schemas.global_identification import (
    GlobalIdentificationFeedbackUpdate,
    GlobalIdentificationProbability,
    GlobalIdentificationResponse,
)
from augochloropsis_ai.services.storage_service import StorageService

GLOBAL_IDENTIFICATION_NOTE = (
    "Baseline global zero-shot. Use como comparacao ampla; "
    "o modelo especifico do projeto continua separado."
)


class GlobalIdentificationService:
    def __init__(
        self,
        *,
        settings: Settings | None = None,
        storage_service: StorageService | None = None,
        identifier: ClipGlobalIdentifier | None = None,
        repository: GlobalIdentificationRepository | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.storage_service = storage_service or StorageService(self.settings)
        self.identifier = identifier
        self.repository = repository or GlobalIdentificationRepository()

    async def identify(self, db: Session, upload_file: UploadFile) -> GlobalIdentificationResponse:
        stored_upload = await self.storage_service.store_upload(upload_file)
        started_at = perf_counter()
        identifier = self.identifier or get_global_identifier()
        result = identifier.identify_bytes(stored_upload.content)
        inference_ms = (perf_counter() - started_at) * 1000
        probabilities = [
            {
                "code": item.code,
                "scientific_name": item.scientific_name,
                "common_name": item.common_name,
                "probability": item.probability,
            }
            for item in result.probabilities
        ]

        identification = self.repository.create_global_identification(
            db,
            original_filename=stored_upload.original_filename,
            stored_path=stored_upload.relative_path,
            sha256=stored_upload.sha256,
            predicted_code=result.predicted_code,
            predicted_scientific_name=result.predicted_scientific_name,
            predicted_common_name=result.predicted_common_name,
            confidence=result.confidence,
            probabilities_json=json.dumps(probabilities),
            model_name=result.model_name,
            inference_ms=inference_ms,
            note=GLOBAL_IDENTIFICATION_NOTE,
        )
        db.commit()
        db.refresh(identification)
        return self._build_response(identification, probabilities)

    def list_global_identifications(
        self,
        db: Session,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[GlobalIdentificationResponse]:
        identifications = self.repository.list_global_identifications(
            db,
            limit=limit,
            offset=offset,
        )
        return [self._build_response(identification) for identification in identifications]

    def set_feedback(self, db: Session, identification_id: int, body: GlobalIdentificationFeedbackUpdate) -> GlobalIdentificationResponse:
        identification = self.repository.update_feedback(db, identification_id, body.user_feedback)
        if identification is None:
            raise NotFoundError("Global identification not found.")
        db.commit()
        db.refresh(identification)
        return self._build_response(identification)

    def _build_response(
        self,
        identification: GlobalIdentification,
        probabilities: list[dict[str, object]] | None = None,
    ) -> GlobalIdentificationResponse:
        payload = probabilities or json.loads(identification.probabilities_json)
        return GlobalIdentificationResponse(
            global_identification_id=identification.id,
            image_url=f"{self.settings.uploads_mount_path}/{identification.stored_path}",
            predicted_code=identification.predicted_code,
            predicted_scientific_name=identification.predicted_scientific_name,
            predicted_common_name=identification.predicted_common_name,
            confidence=identification.confidence,
            probabilities=[
                GlobalIdentificationProbability(
                    code=str(item["code"]),
                    scientific_name=str(item["scientific_name"]),
                    common_name=str(item["common_name"]),
                    probability=float(item["probability"]),
                )
                for item in payload
            ],
            model_name=identification.model_name,
            created_at=identification.created_at,
            inference_ms=identification.inference_ms,
            note=identification.note,
            user_feedback=identification.user_feedback,
        )
