from __future__ import annotations

from types import SimpleNamespace

from augochloropsis_ai.core.config import Settings
from augochloropsis_ai.ml.artifact_loader import ArtifactLoader


def test_resolves_legacy_absolute_artifact_path_from_configured_artifacts_dir(tmp_path):
    artifacts_dir = tmp_path / "artifacts" / "models"
    expected_dir = artifacts_dir / "model_v1"
    expected_dir.mkdir(parents=True)
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'app.sqlite3'}",
        upload_dir=tmp_path / "uploads",
        artifacts_dir=artifacts_dir,
    )
    loader = ArtifactLoader(settings)
    model_version = SimpleNamespace(
        artifact_dir="/legacy/project/artifacts/models/model_v1",
    )

    assert loader._resolve_artifact_dir(model_version) == expected_dir
