from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "image_id",
    "specimen_id",
    "species_code",
    "file_path",
    "source",
    "view_type",
    "annotator",
    "label_status",
    "sha256",
]


def build_clean_manifest(raw_catalog_path: Path, output_path: Path) -> pd.DataFrame:
    dataframe = pd.read_csv(raw_catalog_path)
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in raw catalog: {missing_columns}")

    cleaned = dataframe.copy()
    cleaned["species_code"] = cleaned["species_code"].astype(str).str.strip().str.lower()
    cleaned["label_status"] = cleaned["label_status"].fillna("pending")
    cleaned = cleaned[cleaned["label_status"].ne("discarded")]
    cleaned = cleaned.dropna(subset=["image_id", "specimen_id", "species_code", "file_path"])
    cleaned = cleaned.drop_duplicates(subset=["sha256"], keep="first")
    cleaned = cleaned.sort_values(["species_code", "specimen_id", "image_id"]).reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_path, index=False)
    return cleaned


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean and validate the raw image catalog.")
    parser.add_argument("--raw-catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build_clean_manifest(args.raw_catalog, args.output)


if __name__ == "__main__":
    main()
