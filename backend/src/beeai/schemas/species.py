from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SpeciesBase(BaseModel):
    code: str = Field(min_length=2, max_length=100)
    scientific_name: str = Field(min_length=3, max_length=255)
    description: str | None = None


class SpeciesCreate(SpeciesBase):
    pass


class SpeciesUpdate(BaseModel):
    scientific_name: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = None
    is_active: bool | None = None


class SpeciesRead(SpeciesBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
