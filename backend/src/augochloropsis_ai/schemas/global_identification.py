from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class GlobalIdentificationProbability(BaseModel):
    code: str
    scientific_name: str
    common_name: str
    probability: float


class GlobalIdentificationResponse(BaseModel):
    image_url: str
    predicted_code: str
    predicted_scientific_name: str
    predicted_common_name: str
    confidence: float
    probabilities: list[GlobalIdentificationProbability]
    model_name: str
    created_at: datetime
    note: str
