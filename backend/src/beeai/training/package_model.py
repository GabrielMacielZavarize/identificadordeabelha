from __future__ import annotations

import argparse
from pathlib import Path
import shutil


REQUIRED_FILES = [
    "classifier_state.pt",
    "label_map.json",
    "training_config.yaml",
    "metrics.json",
    "confusion_matrix.png",
]


def package_model(run_dir: Path, destination_dir: Path) -> Path:
    if destination_dir.exists():
        shutil.rmtree(destination_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)

    for filename in REQUIRED_FILES:
        source = run_dir / filename
        if not source.exists():
            raise FileNotFoundError(f"Cannot package model. Missing file: {source}")
        shutil.copy2(source, destination_dir / filename)

    training_summary = run_dir / "training_summary.json"
    if training_summary.exists():
        shutil.copy2(training_summary, destination_dir / training_summary.name)

    return destination_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Package the trained model into the artifacts directory.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--destination-dir", type=Path, required=True)
    args = parser.parse_args()
    package_model(args.run_dir, args.destination_dir)


if __name__ == "__main__":
    main()
