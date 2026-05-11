from __future__ import annotations

import argparse
import json
from pathlib import Path

from beeai.core.config import get_settings
from beeai.db.session import get_session_factory, init_db
from beeai.repositories.model_repository import ModelRepository
from beeai.training.build_manifest import build_clean_manifest
from beeai.training.evaluate_model import evaluate_classifier
from beeai.training.extract_embeddings import extract_embeddings
from beeai.training.package_model import package_model
from beeai.training.split_dataset import split_dataset
from beeai.training.train_mlp import train_classifier


def run_pipeline(
    *,
    raw_catalog: Path,
    clean_catalog: Path,
    split_manifest: Path,
    processed_root: Path,
    embeddings_dir: Path,
    artifacts_root: Path,
    version: str,
    encoder_name: str,
) -> Path:
    build_clean_manifest(raw_catalog, clean_catalog)
    split_dataset(clean_catalog, split_manifest, processed_root)
    embedding_files = extract_embeddings(split_manifest, embeddings_dir, model_name=encoder_name)

    run_dir = artifacts_root / "_runs" / version
    training_artifacts = train_classifier(
        train_embeddings_path=embedding_files["train"],
        val_embeddings_path=embedding_files["val"],
        output_dir=run_dir,
        version=version,
        encoder_name=encoder_name,
    )
    metrics = evaluate_classifier(training_artifacts.output_dir, embedding_files["test"])
    packaged_dir = package_model(run_dir, artifacts_root / version)

    settings = get_settings()
    init_db(settings)
    session_factory = get_session_factory(settings.database_url)
    with session_factory() as db:
        ModelRepository().register_model_version(
            db,
            version=version,
            encoder_name=encoder_name,
            classifier_type="mlp",
            artifact_dir=packaged_dir,
            metrics=metrics,
            activate=True,
        )
        db.commit()

    return packaged_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the offline end-to-end training pipeline.")
    parser.add_argument("--raw-catalog", type=Path, required=True)
    parser.add_argument("--clean-catalog", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--processed-root", type=Path, default=Path("../data/processed"))
    parser.add_argument("--embeddings-dir", type=Path, default=Path("../data/interim/embeddings"))
    parser.add_argument("--artifacts-root", type=Path, default=Path("../artifacts/models"))
    parser.add_argument("--version", type=str, default="dinov2_small_mlp_demo_v001")
    parser.add_argument("--encoder-name", type=str, default="facebook/dinov2-small")
    args = parser.parse_args()

    packaged_dir = run_pipeline(
        raw_catalog=args.raw_catalog.resolve(),
        clean_catalog=args.clean_catalog.resolve(),
        split_manifest=args.split_manifest.resolve(),
        processed_root=args.processed_root.resolve(),
        embeddings_dir=args.embeddings_dir.resolve(),
        artifacts_root=args.artifacts_root.resolve(),
        version=args.version,
        encoder_name=args.encoder_name,
    )
    print(json.dumps({"packaged_dir": str(packaged_dir)}, indent=2))


if __name__ == "__main__":
    main()
