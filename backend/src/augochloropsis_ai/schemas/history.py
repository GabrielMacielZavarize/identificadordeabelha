from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

HistorySource = Literal["specific", "openai"]
HistorySourceFilter = Literal["all", "specific", "openai"]


class IdentificationHistoryItem(BaseModel):
    item_id: int
    source: HistorySource
    source_label: str
    image_url: str
    predicted_code: str
    predicted_scientific_name: str
    predicted_common_name: str | None = None
    confidence: float
    model_name: str
    inference_ms: float | None = None
    created_at: datetime


class IdentificationHistoryPage(BaseModel):
    items: list[IdentificationHistoryItem]
    total: int
    limit: int
    offset: int
