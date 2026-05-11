from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

from beeai.ml.artifact_loader import ArtifactLoader
from beeai.ml.classifier import predict_probabilities
from beeai.db.models import ModelVersion


def evaluate_classifier(run_dir: Path, test_embeddings_path: Path) -> dict:
    payload = np.load(test_embeddings_path, allow_pickle=True)
    embeddings = payload["embeddings"].astype(np.float32)
    species_codes = payload["species_codes"].tolist()

    model_version = ModelVersion(
        version=run_dir.name,
        encoder_name="facebook/dinov2-base",
        classifier_type="mlp",
        artifact_dir=str(run_dir),
        metrics_json="{}",
        is_active=False,
    )
    artifacts = ArtifactLoader().load(model_version)
    code_to_index = {code: index for index, code in artifacts.label_map.items()}
    y_true = np.asarray([code_to_index[code] for code in species_codes], dtype=np.int64)

    y_pred = []
    for embedding in embeddings:
        probabilities = predict_probabilities(artifacts.classifier, embedding)
        y_pred.append(int(np.argmax(probabilities)))
    y_pred_array = np.asarray(y_pred, dtype=np.int64)

    precision, recall, f1_score, _ = precision_recall_fscore_support(
        y_true,
        y_pred_array,
        average="weighted",
        zero_division=0,
    )
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred_array)),
        "precision_weighted": float(precision),
        "recall_weighted": float(recall),
        "f1_weighted": float(f1_score),
    }

    metrics_path = run_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    labels = [artifacts.label_map[index] for index in sorted(artifacts.label_map)]
    confusion = confusion_matrix(y_true, y_pred_array, labels=sorted(artifacts.label_map))
    figure = plt.figure(figsize=(10, 8))
    sns.heatmap(confusion, annot=True, fmt="d", cmap="YlGnBu", xticklabels=labels, yticklabels=labels)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    confusion_path = run_dir / "confusion_matrix.png"
    figure.tight_layout()
    figure.savefig(confusion_path, dpi=200)
    plt.close(figure)

    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a trained classifier on the test split.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--test-embeddings", type=Path, required=True)
    args = parser.parse_args()
    evaluate_classifier(args.run_dir, args.test_embeddings)


if __name__ == "__main__":
    main()
