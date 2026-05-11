from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SpeciesSummary(BaseModel):
    id: int
    code: str
    scientific_name: str


class ModelVersionSummary(BaseModel):
    id: int
    version: str
    encoder_name: str
    classifier_type: str


class PredictionProbability(BaseModel):
    species_code: str
    scientific_name: str | None = None
    probability: float


class PredictionFeedbackUpdate(BaseModel):
    user_feedback: bool


class PredictionResponse(BaseModel):
    prediction_id: int
    image_url: str
    predicted_species: SpeciesSummary
    confidence: float
    probabilities: list[PredictionProbability]
    model_version: ModelVersionSummary
    created_at: datetime
    inference_ms: float
    user_feedback: bool | None = None
