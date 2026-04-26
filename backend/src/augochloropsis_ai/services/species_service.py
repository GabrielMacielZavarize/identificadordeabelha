from __future__ import annotations

from sqlalchemy.orm import Session

from augochloropsis_ai.core.exceptions import ConflictError, NotFoundError
from augochloropsis_ai.db.models import Species
from augochloropsis_ai.repositories.species_repository import SpeciesRepository
from augochloropsis_ai.schemas.species import SpeciesCreate, SpeciesUpdate


class SpeciesService:
    def __init__(self, repository: SpeciesRepository | None = None) -> None:
        self.repository = repository or SpeciesRepository()

    def list_species(self, db: Session, include_inactive: bool = False) -> list[Species]:
        return list(self.repository.list_species(db, include_inactive=include_inactive))

    def create_species(self, db: Session, payload: SpeciesCreate) -> Species:
        existing = self.repository.get_by_code(db, payload.code)
        if existing is not None:
            raise ConflictError(f"Species code '{payload.code}' already exists.")
        species = self.repository.create(
            db,
            code=payload.code.strip(),
            scientific_name=payload.scientific_name.strip(),
            description=payload.description,
        )
        db.commit()
        db.refresh(species)
        return species

    def update_species(self, db: Session, species_id: int, payload: SpeciesUpdate) -> Species:
        species = self.repository.get_by_id(db, species_id)
        if species is None:
            raise NotFoundError("Species not found.")

        if payload.scientific_name is not None:
            species.scientific_name = payload.scientific_name.strip()
        if payload.description is not None:
            species.description = payload.description
        if payload.is_active is not None:
            species.is_active = payload.is_active

        self.repository.save(db, species)
        db.commit()
        db.refresh(species)
        return species

    def delete_species(self, db: Session, species_id: int) -> Species:
        species = self.repository.get_by_id(db, species_id)
        if species is None:
            raise NotFoundError("Species not found.")

        species.is_active = False
        self.repository.save(db, species)
        db.commit()
        db.refresh(species)
        return species
