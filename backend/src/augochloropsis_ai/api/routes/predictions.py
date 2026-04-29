from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from augochloropsis_ai.core.exceptions import InvalidRequestError, ModelNotReadyError, NotFoundError
from augochloropsis_ai.db.session import get_db
from augochloropsis_ai.schemas.prediction import PredictionFeedbackUpdate, PredictionResponse
from augochloropsis_ai.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    file: UploadFile = File(...),
    model_version: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
):
    service = PredictionService()
    try:
        return await service.create_prediction(db, file, model_version=model_version)
    except InvalidRequestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ModelNotReadyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("", response_model=list[PredictionResponse])
def list_predictions(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    service = PredictionService()
    return service.list_predictions(db, limit=limit, offset=offset)


@router.get("/{prediction_id}", response_model=PredictionResponse)
def get_prediction(prediction_id: int, db: Session = Depends(get_db)):
    service = PredictionService()
    try:
        return service.get_prediction(db, prediction_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{prediction_id}/feedback", response_model=PredictionResponse)
def set_prediction_feedback(
    prediction_id: int,
    body: PredictionFeedbackUpdate,
    db: Session = Depends(get_db),
):
    service = PredictionService()
    try:
        return service.set_feedback(db, prediction_id, body)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
