from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class GlobalIdentificationProbability(BaseModel):
    code: str
    scientific_name: str
    common_name: str
    probability: float


class GlobalIdentificationFeedbackUpdate(BaseModel):
    user_feedback: bool


class GlobalIdentificationResponse(BaseModel):
    global_identification_id: int
    image_url: str
    predicted_code: str
    predicted_scientific_name: str
    predicted_common_name: str
    confidence: float
    probabilities: list[GlobalIdentificationProbability]
    model_name: str
    created_at: datetime
    inference_ms: float
    note: str
    user_feedback: bool | None = None
