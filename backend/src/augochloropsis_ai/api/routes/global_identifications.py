from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from augochloropsis_ai.core.exceptions import InvalidRequestError
from augochloropsis_ai.schemas.global_identification import GlobalIdentificationResponse
from augochloropsis_ai.services.global_identification_service import GlobalIdentificationService

router = APIRouter(prefix="/global-identifications", tags=["global-identifications"])


@router.post("", response_model=GlobalIdentificationResponse, status_code=status.HTTP_201_CREATED)
async def create_global_identification(file: Annotated[UploadFile, File(...)]):
    service = GlobalIdentificationService()
    try:
        return await service.identify(file)
    except InvalidRequestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
