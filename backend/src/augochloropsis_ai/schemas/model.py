from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ModelVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version: str
    encoder_name: str
    classifier_type: str
    artifact_dir: str
    metrics_json: str
    is_active: bool
    created_at: datetime
