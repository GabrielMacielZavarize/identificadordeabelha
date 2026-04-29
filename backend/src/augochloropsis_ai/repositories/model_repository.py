from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from augochloropsis_ai.db.models import ModelVersion


class ModelRepository:
    def get_active_model(self, db: Session) -> ModelVersion | None:
        stmt = select(ModelVersion).where(ModelVersion.is_active.is_(True)).limit(1)
        return db.scalar(stmt)

    def list_model_versions(self, db: Session) -> list[ModelVersion]:
        stmt = select(ModelVersion).order_by(
            ModelVersion.is_active.desc(),
            ModelVersion.created_at.desc(),
        )
        return list(db.scalars(stmt))

    def get_by_version(self, db: Session, version: str) -> ModelVersion | None:
        stmt = select(ModelVersion).where(ModelVersion.version == version).limit(1)
        return db.scalar(stmt)

    def register_model_version(
        self,
        db: Session,
        *,
        version: str,
        encoder_name: str,
        classifier_type: str,
        artifact_dir: Path,
        metrics: dict,
        activate: bool = True,
    ) -> ModelVersion:
        existing = self.get_by_version(db, version)
        if activate:
            db.execute(update(ModelVersion).values(is_active=False))

        if existing:
            existing.encoder_name = encoder_name
            existing.classifier_type = classifier_type
            existing.artifact_dir = str(artifact_dir)
            existing.metrics_json = json.dumps(metrics)
            existing.is_active = activate
            db.flush()
            return existing

        model_version = ModelVersion(
            version=version,
            encoder_name=encoder_name,
            classifier_type=classifier_type,
            artifact_dir=str(artifact_dir),
            metrics_json=json.dumps(metrics),
            is_active=activate,
        )
        db.add(model_version)
        db.flush()
        return model_version
