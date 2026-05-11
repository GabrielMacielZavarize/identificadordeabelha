from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from beeai.core.exceptions import InvalidRequestError, NotFoundError
from beeai.db.session import get_db
from beeai.schemas.global_identification import (
    GlobalIdentificationFeedbackUpdate,
    GlobalIdentificationResponse,
)
from beeai.services.global_identification_service import GlobalIdentificationService

router = APIRouter(prefix="/global-identifications", tags=["global-identifications"])
_service = GlobalIdentificationService()


@router.post("", response_model=GlobalIdentificationResponse, status_code=status.HTTP_201_CREATED)
async def create_global_identification(
    file: Annotated[UploadFile, File(...)],
    db: Session = Depends(get_db),
):
    try:
        return await _service.identify(db, file)
    except InvalidRequestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("", response_model=list[GlobalIdentificationResponse])
def list_global_identifications(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return _service.list_global_identifications(db, limit=limit, offset=offset)


@router.patch("/{identification_id}/feedback", response_model=GlobalIdentificationResponse)
async def set_global_identification_feedback(
    identification_id: int,
    body: GlobalIdentificationFeedbackUpdate,
    db: Session = Depends(get_db),
):
    try:
        return _service.set_feedback(db, identification_id, body)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
