from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from augochloropsis_ai.db.models import GlobalIdentification


class GlobalIdentificationRepository:
    def list_global_identifications(
        self,
        db: Session,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[GlobalIdentification]:
        stmt = (
            select(GlobalIdentification)
            .order_by(GlobalIdentification.created_at.desc(), GlobalIdentification.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def count_global_identifications(self, db: Session) -> int:
        return db.scalar(select(func.count()).select_from(GlobalIdentification)) or 0

    def update_feedback(self, db: Session, identification_id: int, user_feedback: bool) -> GlobalIdentification | None:
        stmt = select(GlobalIdentification).where(GlobalIdentification.id == identification_id)
        identification = db.scalar(stmt)
        if identification is None:
            return None
        identification.user_feedback = user_feedback
        db.flush()
        return identification

    def create_global_identification(
        self,
        db: Session,
        *,
        original_filename: str,
        stored_path: str,
        sha256: str,
        predicted_code: str,
        predicted_scientific_name: str,
        predicted_common_name: str,
        confidence: float,
        probabilities_json: str,
        model_name: str,
        inference_ms: float,
        note: str,
    ) -> GlobalIdentification:
        identification = GlobalIdentification(
            original_filename=original_filename,
            stored_path=stored_path,
            sha256=sha256,
            predicted_code=predicted_code,
            predicted_scientific_name=predicted_scientific_name,
            predicted_common_name=predicted_common_name,
            confidence=confidence,
            probabilities_json=probabilities_json,
            model_name=model_name,
            inference_ms=inference_ms,
            note=note,
        )
        db.add(identification)
        db.flush()
        return identification
