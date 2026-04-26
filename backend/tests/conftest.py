from __future__ import annotations

import base64
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from augochloropsis_ai.core.config import get_settings
from augochloropsis_ai.db.session import get_engine, get_session_factory


@pytest.fixture
def app_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    database_path = tmp_path / "test.sqlite3"
    uploads_dir = tmp_path / "uploads"
    artifacts_dir = tmp_path / "artifacts"

    monkeypatch.setenv("AUGOCHLOROPSIS_AI_DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setenv("AUGOCHLOROPSIS_AI_UPLOAD_DIR", str(uploads_dir))
    monkeypatch.setenv("AUGOCHLOROPSIS_AI_ARTIFACTS_DIR", str(artifacts_dir))
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()

    from augochloropsis_ai.api.main import create_app

    return create_app()


@pytest.fixture
def test_client(app_environment):
    with TestClient(app_environment) as client:
        yield client


@pytest.fixture
def db_session(app_environment):
    session_factory = get_session_factory(get_settings().database_url)
    with session_factory() as db:
        yield db
