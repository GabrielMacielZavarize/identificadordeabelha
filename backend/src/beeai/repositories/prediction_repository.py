from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from beeai.db.models import ModelVersion, Prediction, Species


class PredictionRepository:
    def list_predictions(self, db: Session, limit: int = 50, offset: int = 0) -> list[Prediction]:
        stmt = (
            select(Prediction)
            .options(joinedload(Prediction.predicted_species), joinedload(Prediction.model_version))
            .order_by(Prediction.created_at.desc(), Prediction.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.scalars(stmt).unique().all())

    def count_predictions(self, db: Session) -> int:
        return db.scalar(select(func.count()).select_from(Prediction)) or 0

    def get_prediction(self, db: Session, prediction_id: int) -> Prediction | None:
        stmt = (
            select(Prediction)
            .options(joinedload(Prediction.predicted_species), joinedload(Prediction.model_version))
            .where(Prediction.id == prediction_id)
        )
        return db.scalar(stmt)

    def update_feedback(self, db: Session, prediction_id: int, user_feedback: bool) -> Prediction | None:
        prediction = self.get_prediction(db, prediction_id)
        if prediction is None:
            return None
        prediction.user_feedback = user_feedback
        db.flush()
        return prediction

    def create_prediction(
        self,
        db: Session,
        *,
        original_filename: str,
        stored_path: str,
        sha256: str,
        predicted_species: Species,
        confidence: float,
        probabilities_json: str,
        model_version: ModelVersion,
        inference_ms: float,
    ) -> Prediction:
        prediction = Prediction(
            original_filename=original_filename,
            stored_path=stored_path,
            sha256=sha256,
            predicted_species=predicted_species,
            confidence=confidence,
            probabilities_json=probabilities_json,
            model_version=model_version,
            inference_ms=inference_ms,
        )
        db.add(prediction)
        db.flush()
        return prediction
