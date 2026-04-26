from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from augochloropsis_ai.db.session import get_db
from augochloropsis_ai.repositories.model_repository import ModelRepository
from augochloropsis_ai.schemas.model import ModelVersionRead

router = APIRouter(prefix="/models", tags=["models"])
repository = ModelRepository()


@router.get("/active", response_model=ModelVersionRead)
def get_active_model(db: Session = Depends(get_db)):
    model_version = repository.get_active_model(db)
    if model_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active model version is registered.",
        )
    return model_version
