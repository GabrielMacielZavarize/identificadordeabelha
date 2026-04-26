from __future__ import annotations

from fastapi import APIRouter

from augochloropsis_ai import __version__

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "version": __version__}
