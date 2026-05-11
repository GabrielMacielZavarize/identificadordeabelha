from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from beeai.core.config import Settings, get_settings
from beeai.db.models import Base


@lru_cache
def get_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, future=True)


@lru_cache
def get_session_factory(database_url: str):
    return sessionmaker(bind=get_engine(database_url), autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    settings = get_settings()
    session_factory = get_session_factory(settings.database_url)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def init_db(settings: Settings | None = None) -> None:
    runtime_settings = settings or get_settings()
    runtime_settings.ensure_runtime_dirs()
    Base.metadata.create_all(bind=get_engine(runtime_settings.database_url))
