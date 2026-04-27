from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from augochloropsis_ai.core.exceptions import InvalidRequestError
from augochloropsis_ai.db.session import get_db
from augochloropsis_ai.schemas.global_identification import GlobalIdentificationResponse
from augochloropsis_ai.services.global_identification_service import GlobalIdentificationService

router = APIRouter(prefix="/global-identifications", tags=["global-identifications"])


@router.post("", response_model=GlobalIdentificationResponse, status_code=status.HTTP_201_CREATED)
async def create_global_identification(
    file: Annotated[UploadFile, File(...)],
    db: Session = Depends(get_db),
):
    service = GlobalIdentificationService()
    try:
        return await service.identify(db, file)
    except InvalidRequestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("", response_model=list[GlobalIdentificationResponse])
def list_global_identifications(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    service = GlobalIdentificationService()
    return service.list_global_identifications(db, limit=limit, offset=offset)
