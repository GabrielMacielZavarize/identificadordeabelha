from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import random
import shutil

import pandas as pd

SPLITS = ("train", "val", "test")


def assign_split_labels(
    manifest: pd.DataFrame,
    *,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
) -> pd.DataFrame:
    if abs((train_ratio + val_ratio + test_ratio) - 1.0) > 1e-6:
        raise ValueError("Split ratios must sum to 1.0.")

    required_columns = {"specimen_id", "species_code"}
    if missing := required_columns.difference(manifest.columns):
        raise ValueError(f"Missing required columns for splitting: {sorted(missing)}")

    group_manifest = (
        manifest.groupby("specimen_id", as_index=False)
        .agg(species_code=("species_code", "first"), image_count=("image_id", "count"))
        .sort_values(["species_code", "specimen_id"])
    )

    rng = random.Random(seed)
    assignments: dict[str, str] = {}

    for species_code, species_groups in group_manifest.groupby("species_code"):
        specimen_ids = species_groups["specimen_id"].tolist()
        rng.shuffle(specimen_ids)
        group_count = len(specimen_ids)

        if group_count < 3:
            split_targets = {"train": group_count, "val": 0, "test": 0}
        else:
            test_count = max(1, round(group_count * test_ratio))
            val_count = max(1, round(group_count * val_ratio)) if group_count >= 5 else 0
            if test_count + val_count >= group_count:
                overflow = (test_count + val_count) - (group_count - 1)
                val_count = max(0, val_count - overflow)
            split_targets = {
                "train": group_count - test_count - val_count,
                "val": val_count,
                "test": test_count,
            }

        split_order = (
            ["train"] * split_targets["train"]
            + ["val"] * split_targets["val"]
            + ["test"] * split_targets["test"]
        )
        for specimen_id, split_name in zip(specimen_ids, split_order, strict=True):
            assignments[str(specimen_id)] = split_name

    split_manifest = manifest.copy()
    split_manifest["split"] = split_manifest["specimen_id"].astype(str).map(assignments)
    split_manifest["split"] = split_manifest["split"].fillna("train")
    return split_manifest


def materialize_split_directories(split_manifest: pd.DataFrame, processed_root: Path) -> None:
    for split_name in SPLITS:
        (processed_root / split_name).mkdir(parents=True, exist_ok=True)

    for record in split_manifest.itertuples(index=False):
        source_path = Path(record.file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Image file not found while materializing splits: {source_path}")
        target_path = processed_root / record.split / record.species_code / source_path.name
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)


def summarize_split(split_manifest: pd.DataFrame) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = defaultdict(dict)
    for split_name, split_rows in split_manifest.groupby("split"):
        species_counts = split_rows.groupby("species_code")["image_id"].count().to_dict()
        summary[split_name] = {str(key): int(value) for key, value in species_counts.items()}
    return dict(summary)


def split_dataset(
    clean_catalog_path: Path,
    output_manifest_path: Path,
    processed_root: Path,
    *,
    seed: int = 42,
    materialize: bool = True,
) -> pd.DataFrame:
    manifest = pd.read_csv(clean_catalog_path)
    split_manifest = assign_split_labels(manifest, seed=seed)
    output_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    split_manifest.to_csv(output_manifest_path, index=False)
    if materialize:
        materialize_split_directories(split_manifest, processed_root)
    return split_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Split the cleaned dataset into train, val and test.")
    parser.add_argument("--clean-catalog", type=Path, required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument("--processed-root", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-materialize", action="store_true")
    args = parser.parse_args()

    split_dataset(
        clean_catalog_path=args.clean_catalog,
        output_manifest_path=args.output_manifest,
        processed_root=args.processed_root,
        seed=args.seed,
        materialize=not args.skip_materialize,
    )


if __name__ == "__main__":
    main()
