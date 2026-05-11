from __future__ import annotations

import argparse
import csv
from pathlib import Path

from beeai.db.session import get_session_factory, init_db
from beeai.core.config import get_settings
from beeai.repositories.species_repository import SpeciesRepository


def seed_species(csv_path: Path) -> None:
    settings = get_settings()
    init_db(settings)
    repository = SpeciesRepository()
    session_factory = get_session_factory(settings.database_url)

    with session_factory() as db:
        with csv_path.open("r", encoding="utf-8") as file_handle:
            reader = csv.DictReader(file_handle)
            for row in reader:
                code = row["code"].strip()
                scientific_name = row["scientific_name"].strip()
                description = row.get("description") or None
                existing = repository.get_by_code(db, code)
                if existing is None:
                    repository.create(
                        db,
                        code=code,
                        scientific_name=scientific_name,
                        description=description,
                    )
                else:
                    existing.scientific_name = scientific_name
                    existing.description = description
                    existing.is_active = True
                    repository.save(db, existing)
        db.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the species registry from a CSV file.")
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("../data/raw/metadata/species_seed.example.csv"),
    )
    args = parser.parse_args()
    seed_species(args.csv.resolve())


if __name__ == "__main__":
    main()
