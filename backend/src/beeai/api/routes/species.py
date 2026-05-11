from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from beeai.core.exceptions import ConflictError, NotFoundError
from beeai.db.session import get_db
from beeai.schemas.species import SpeciesCreate, SpeciesRead, SpeciesUpdate
from beeai.services.species_service import SpeciesService

router = APIRouter(prefix="/species", tags=["species"])
service = SpeciesService()


@router.get("", response_model=list[SpeciesRead])
def list_species(
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    return service.list_species(db, include_inactive=include_inactive)


@router.post("", response_model=SpeciesRead, status_code=status.HTTP_201_CREATED)
def create_species(payload: SpeciesCreate, db: Session = Depends(get_db)):
    try:
        return service.create_species(db, payload)
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.put("/{species_id}", response_model=SpeciesRead)
def update_species(species_id: int, payload: SpeciesUpdate, db: Session = Depends(get_db)):
    try:
        return service.update_species(db, species_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{species_id}", response_model=SpeciesRead)
def delete_species(species_id: int, db: Session = Depends(get_db)):
    try:
        return service.delete_species(db, species_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
