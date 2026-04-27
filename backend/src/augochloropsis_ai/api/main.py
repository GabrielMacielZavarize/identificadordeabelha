from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from augochloropsis_ai.api.routes import (
    global_identifications,
    history,
    health,
    models,
    predictions,
    species,
)
from augochloropsis_ai.core.config import get_settings
from augochloropsis_ai.core.logging import configure_logging
from augochloropsis_ai.db.session import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    settings.ensure_runtime_dirs()
    init_db(settings)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    settings.ensure_runtime_dirs()
    configure_logging(settings.debug)

    app = FastAPI(
        title=settings.project_name,
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "Accept"],
    )
    app.mount(
        settings.uploads_serve_path,
        StaticFiles(directory=str(settings.upload_dir)),
        name="uploads",
    )
    app.include_router(health.router, prefix=settings.api_v1_prefix)
    app.include_router(species.router, prefix=settings.api_v1_prefix)
    app.include_router(predictions.router, prefix=settings.api_v1_prefix)
    app.include_router(global_identifications.router, prefix=settings.api_v1_prefix)
    app.include_router(history.router, prefix=settings.api_v1_prefix)
    app.include_router(models.router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
