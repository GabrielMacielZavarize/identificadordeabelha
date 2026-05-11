from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from beeai.db.models import Species


class SpeciesRepository:
    def list_species(self, db: Session, include_inactive: bool = False) -> Sequence[Species]:
        stmt = select(Species).order_by(Species.scientific_name.asc())
        if not include_inactive:
            stmt = stmt.where(Species.is_active.is_(True))
        return db.scalars(stmt).all()

    def list_by_codes(self, db: Session, codes: Sequence[str]) -> dict[str, Species]:
        if not codes:
            return {}
        stmt = select(Species).where(Species.code.in_(codes))
        return {species.code: species for species in db.scalars(stmt).all()}

    def get_by_id(self, db: Session, species_id: int) -> Species | None:
        return db.get(Species, species_id)

    def get_by_code(self, db: Session, code: str) -> Species | None:
        stmt = select(Species).where(Species.code == code)
        return db.scalar(stmt)

    def create(self, db: Session, *, code: str, scientific_name: str, description: str | None) -> Species:
        species = Species(code=code, scientific_name=scientific_name, description=description)
        db.add(species)
        db.flush()
        return species

    def save(self, db: Session, species: Species) -> Species:
        db.add(species)
        db.flush()
        return species
