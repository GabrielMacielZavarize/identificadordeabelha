from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from beeai.db.session import get_db
from beeai.schemas.history import HistorySourceFilter, IdentificationHistoryPage
from beeai.services.history_service import HistoryService

router = APIRouter(prefix="/history", tags=["history"])
_service = HistoryService()


@router.get("", response_model=IdentificationHistoryPage)
def list_identification_history(
    source: HistorySourceFilter = Query(default="all"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return _service.list_history(db, source=source, limit=limit, offset=offset)
