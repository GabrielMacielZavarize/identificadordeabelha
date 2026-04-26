from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from augochloropsis_ai.ml.embedder import get_embedder


def extract_embeddings(
    split_manifest_path: Path,
    output_dir: Path,
    *,
    model_name: str = "facebook/dinov2-base",
) -> dict[str, Path]:
    manifest = pd.read_csv(split_manifest_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    embedder = get_embedder(model_name)
    generated_files: dict[str, Path] = {}

    for split_name, split_rows in manifest.groupby("split"):
        embeddings: list[np.ndarray] = []
        species_codes: list[str] = []
        image_paths: list[str] = []

        for row in split_rows.itertuples(index=False):
            image_path = Path(row.file_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found for embedding extraction: {image_path}")
            embedding = embedder.embed_bytes(image_path.read_bytes())
            embeddings.append(embedding)
            species_codes.append(str(row.species_code))
            image_paths.append(str(image_path))

        output_path = output_dir / f"{split_name}_embeddings.npz"
        np.savez_compressed(
            output_path,
            embeddings=np.asarray(embeddings, dtype=np.float32),
            species_codes=np.asarray(species_codes, dtype=object),
            image_paths=np.asarray(image_paths, dtype=object),
        )
        generated_files[split_name] = output_path

    return generated_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract DINOv2 embeddings for each dataset split.")
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-name", type=str, default="facebook/dinov2-base")
    args = parser.parse_args()
    extract_embeddings(args.split_manifest, args.output_dir, model_name=args.model_name)


if __name__ == "__main__":
    main()
