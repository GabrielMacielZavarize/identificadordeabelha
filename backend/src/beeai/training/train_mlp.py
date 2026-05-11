from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from beeai.ml.classifier import MLPClassifier


def _import_torch():
    try:
        import torch
        import torch.nn as nn
    except ImportError as exc:
        raise RuntimeError("PyTorch is required for training the classifier.") from exc
    return torch, nn


@dataclass(slots=True)
class TrainingArtifacts:
    output_dir: Path
    version: str
    label_map: dict[int, str]
    classifier_state_path: Path
    training_config_path: Path
    training_summary_path: Path
    input_dim: int
    hidden_dims: tuple[int, ...]
    dropout: float


def _load_embedding_split(path: Path) -> tuple[np.ndarray, list[str]]:
    payload = np.load(path, allow_pickle=True)
    return payload["embeddings"].astype(np.float32), payload["species_codes"].tolist()


def _build_label_map(
    train_codes: list[str], val_codes: list[str]
) -> tuple[list[str], dict[str, int], dict[int, str]]:
    label_codes = sorted(set(train_codes) | set(val_codes))
    label_to_index = {code: i for i, code in enumerate(label_codes)}
    label_map = {i: code for code, i in label_to_index.items()}
    return label_codes, label_to_index, label_map


def _run_training_loop(
    classifier: Any,
    optimizer: Any,
    criterion: Any,
    torch: Any,
    train_tensor: Any,
    train_targets: Any,
    val_tensor: Any,
    val_targets: Any,
    *,
    epochs: int,
    batch_size: int,
) -> tuple[dict, float, float]:
    best_state = copy.deepcopy(classifier.state_dict())
    best_val_loss = float("inf")
    best_val_accuracy = 0.0

    for _ in range(epochs):
        classifier.train()
        permutation = torch.randperm(train_tensor.size(0))
        for start in range(0, train_tensor.size(0), batch_size):
            indices = permutation[start : start + batch_size]
            optimizer.zero_grad()
            loss = criterion(classifier(train_tensor[indices]), train_targets[indices])
            loss.backward()
            optimizer.step()

        classifier.eval()
        with torch.no_grad():
            val_logits = classifier(val_tensor)
            val_loss = criterion(val_logits, val_targets).item()
            val_accuracy = float((val_logits.argmax(dim=1) == val_targets).float().mean())

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_val_accuracy = val_accuracy
            best_state = copy.deepcopy(classifier.state_dict())

    return best_state, best_val_loss, best_val_accuracy


def _save_training_artifacts(
    output_dir: Path,
    *,
    best_state: dict,
    torch: Any,
    label_map: dict[int, str],
    label_codes: list[str],
    best_val_loss: float,
    best_val_accuracy: float,
    version: str,
    encoder_name: str,
    input_dim: int,
    hidden_dims: tuple[int, ...],
    dropout: float,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    weight_decay: float,
) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    classifier_state_path = output_dir / "classifier_state.pt"
    training_config_path = output_dir / "training_config.yaml"
    training_summary_path = output_dir / "training_summary.json"
    label_map_path = output_dir / "label_map.json"

    torch.save(best_state, classifier_state_path)
    label_map_path.write_text(json.dumps(label_map, indent=2), encoding="utf-8")
    training_config_path.write_text(
        yaml.safe_dump(
            {
                "version": version,
                "encoder_name": encoder_name,
                "classifier_type": "mlp",
                "input_dim": input_dim,
                "hidden_dims": list(hidden_dims),
                "dropout": dropout,
                "epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "weight_decay": weight_decay,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    training_summary_path.write_text(
        json.dumps(
            {
                "best_val_loss": best_val_loss,
                "best_val_accuracy": best_val_accuracy,
                "classes": label_codes,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return classifier_state_path, training_config_path, training_summary_path


def train_classifier(
    *,
    train_embeddings_path: Path,
    val_embeddings_path: Path,
    output_dir: Path,
    version: str = "dinov2_base_mlp_v001",
    encoder_name: str = "facebook/dinov2-base",
    hidden_dims: tuple[int, ...] = (256, 128),
    dropout: float = 0.2,
    epochs: int = 40,
    batch_size: int = 16,
    learning_rate: float = 1e-3,
    weight_decay: float = 1e-4,
) -> TrainingArtifacts:
    torch, nn = _import_torch()

    train_embeddings, train_codes = _load_embedding_split(train_embeddings_path)
    val_embeddings, val_codes = _load_embedding_split(val_embeddings_path)

    label_codes, label_to_index, label_map = _build_label_map(train_codes, val_codes)

    train_labels = np.asarray([label_to_index[c] for c in train_codes], dtype=np.int64)
    val_labels = np.asarray([label_to_index[c] for c in val_codes], dtype=np.int64)
    input_dim = int(train_embeddings.shape[1])

    classifier = MLPClassifier(
        input_dim=input_dim,
        num_classes=len(label_map),
        hidden_dims=hidden_dims,
        dropout=dropout,
    )
    optimizer = torch.optim.AdamW(classifier.parameters(), lr=learning_rate, weight_decay=weight_decay)
    criterion = nn.CrossEntropyLoss()

    train_tensor = torch.tensor(train_embeddings, dtype=torch.float32)
    train_targets = torch.tensor(train_labels, dtype=torch.long)
    val_tensor = torch.tensor(val_embeddings, dtype=torch.float32)
    val_targets = torch.tensor(val_labels, dtype=torch.long)

    best_state, best_val_loss, best_val_accuracy = _run_training_loop(
        classifier, optimizer, criterion, torch,
        train_tensor, train_targets, val_tensor, val_targets,
        epochs=epochs,
        batch_size=batch_size,
    )

    classifier_state_path, training_config_path, training_summary_path = _save_training_artifacts(
        output_dir,
        best_state=best_state,
        torch=torch,
        label_map=label_map,
        label_codes=label_codes,
        best_val_loss=best_val_loss,
        best_val_accuracy=best_val_accuracy,
        version=version,
        encoder_name=encoder_name,
        input_dim=input_dim,
        hidden_dims=hidden_dims,
        dropout=dropout,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
    )

    return TrainingArtifacts(
        output_dir=output_dir,
        version=version,
        label_map=label_map,
        classifier_state_path=classifier_state_path,
        training_config_path=training_config_path,
        training_summary_path=training_summary_path,
        input_dim=input_dim,
        hidden_dims=hidden_dims,
        dropout=dropout,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the MLP classifier on cached embeddings.")
    parser.add_argument("--train-embeddings", type=Path, required=True)
    parser.add_argument("--val-embeddings", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--version", type=str, default="dinov2_base_mlp_v001")
    parser.add_argument("--encoder-name", type=str, default="facebook/dinov2-base")
    args = parser.parse_args()
    train_classifier(
        train_embeddings_path=args.train_embeddings,
        val_embeddings_path=args.val_embeddings,
        output_dir=args.output_dir,
        version=args.version,
        encoder_name=args.encoder_name,
    )


if __name__ == "__main__":
    main()
