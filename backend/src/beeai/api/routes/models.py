from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from beeai.db.session import get_db
from beeai.repositories.model_repository import ModelRepository
from beeai.schemas.model import ModelVersionRead

router = APIRouter(prefix="/models", tags=["models"])
repository = ModelRepository()


@router.get("", response_model=list[ModelVersionRead])
def list_model_versions(db: Session = Depends(get_db)):
    return repository.list_model_versions(db)


@router.get("/active", response_model=ModelVersionRead)
def get_active_model(db: Session = Depends(get_db)):
    model_version = repository.get_active_model(db)
    if model_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active model version is registered.",
        )
    return model_version
