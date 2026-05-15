from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    project_name: str = "BeeAI"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = f"sqlite:///{REPO_ROOT / 'data/db/app.sqlite3'}"
    upload_dir: Path = REPO_ROOT / "data/uploads"
    artifacts_dir: Path = REPO_ROOT / "artifacts/models"
    max_upload_size_mb: int = 15
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    allowed_image_extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png")
    allowed_mime_types: tuple[str, ...] = ("image/jpeg", "image/png")

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_jwt_secret: str = ""

    # Hugging Face
    hf_token: str = ""
    hf_model_repo: str = ""

    model_config = SettingsConfigDict(
        env_prefix="BEEAI_",
        env_file=REPO_ROOT / ".env",
        extra="ignore",
    )

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    uploads_base_url: str = ""

    @property
    def uploads_serve_path(self) -> str:
        """Path usado pelo FastAPI para montar os arquivos estáticos — sempre /uploads."""
        return "/uploads"

    @property
    def uploads_mount_path(self) -> str:
        """Prefixo usado nas URLs de imagem retornadas pela API. Em staging/prod inclui o host."""
        return f"{self.uploads_base_url}/uploads"

    def ensure_runtime_dirs(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        (REPO_ROOT / "data/db").mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
