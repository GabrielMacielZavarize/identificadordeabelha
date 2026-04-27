from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from augochloropsis_ai.core.config import Settings, get_settings
from augochloropsis_ai.core.exceptions import ModelNotReadyError
from augochloropsis_ai.db.models import ModelVersion
from augochloropsis_ai.ml.classifier import load_classifier_state


@dataclass(slots=True)
class LoadedArtifacts:
    version: str
    encoder_name: str
    classifier_type: str
    label_map: dict[int, str]
    classifier: Any
    config: dict[str, Any]
    metrics: dict[str, Any]


class ArtifactLoader:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def load(self, model_version: ModelVersion) -> LoadedArtifacts:
        artifact_dir = self._resolve_artifact_dir(model_version)
        if not artifact_dir.exists():
            raise ModelNotReadyError(f"Artifact directory not found: {artifact_dir}")

        classifier_path = artifact_dir / "classifier_state.pt"
        label_map_path = artifact_dir / "label_map.json"
        training_config_path = artifact_dir / "training_config.yaml"
        metrics_path = artifact_dir / "metrics.json"

        for required_path in (classifier_path, label_map_path, training_config_path):
            if not required_path.exists():
                raise ModelNotReadyError(f"Missing artifact file: {required_path.name}")

        label_map_raw = json.loads(label_map_path.read_text(encoding="utf-8"))
        label_map = {int(key): value for key, value in label_map_raw.items()}
        training_config = yaml.safe_load(training_config_path.read_text(encoding="utf-8")) or {}
        metrics = (
            json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
        )

        classifier = load_classifier_state(
            classifier_path,
            input_dim=int(training_config.get("input_dim", 768)),
            num_classes=len(label_map),
            hidden_dims=tuple(training_config.get("hidden_dims", [256])),
            dropout=float(training_config.get("dropout", 0.2)),
        )

        return LoadedArtifacts(
            version=model_version.version,
            encoder_name=training_config.get("encoder_name", model_version.encoder_name),
            classifier_type=model_version.classifier_type,
            label_map=label_map,
            classifier=classifier,
            config=training_config,
            metrics=metrics,
        )

    def _resolve_artifact_dir(self, model_version: ModelVersion) -> Path:
        stored_path = Path(model_version.artifact_dir)
        if stored_path.exists():
            return stored_path

        configured_path = self.settings.artifacts_dir / stored_path.name
        if configured_path.exists():
            return configured_path

        return stored_path
