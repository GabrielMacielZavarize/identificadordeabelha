from __future__ import annotations

import jwt
from fastapi import Header, HTTPException, status

from beeai.core.config import get_settings


def get_optional_user(authorization: str | None = Header(default=None)) -> dict | None:
    """Valida o JWT do Supabase se presente. Retorna None se não houver token."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    settings = get_settings()
    if not settings.supabase_jwt_secret:
        return None
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    """Exige autenticação. Lança 401 se não houver token válido."""
    user = get_optional_user(authorization)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
