"""
QuishGuard — FastAPI Dependencies (Auth, Rate Limiting)
"""

import hashlib
import secrets
import uuid

from fastapi import Depends, Header, HTTPException, Request, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.api_key import ApiKey


def generate_api_key() -> tuple[str, str]:
    """Generate a new API key. Returns (raw_key, hashed_key)."""
    raw_key = f"{settings.api_key_prefix}{secrets.token_hex(24)}"
    hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, hashed_key


def mask_api_key(raw_key: str) -> str:
    """Mask an API key for display: 'qg_live_abc...xyz'"""
    if len(raw_key) < 10:
        return raw_key
    prefix = raw_key[:8]
    suffix = raw_key[-4:]
    return f"{prefix}...{suffix}"


async def verify_api_key(
    request: Request,
    x_api_key: str = Header(default=None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> ApiKey | None:
    """
    Verify API key from X-API-Key header.
    Returns the ApiKey object if valid, None if no key provided.
    Raises 401 if key is invalid or inactive.
    """
    if x_api_key is None:
        # No API key provided — allow for now (will be enforced later)
        return None

    key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()

    result = await db.execute(
        select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.is_active == True)
    )
    api_key_obj = result.scalar_one_or_none()

    if api_key_obj is None:
        logger.warning(f"Invalid API key attempt: {mask_api_key(x_api_key)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
        )

    # Check expiration
    if api_key_obj.expires_at and api_key_obj.expires_at < request.state._now if hasattr(request.state, "_now") else __import__("datetime").datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired",
        )

    return api_key_obj


def validate_file_type(filename: str) -> str:
    """Validate that the uploaded file has an allowed extension."""
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{ext}'. Accepted: {', '.join(settings.allowed_extensions_list)}",
        )
    return ext


def validate_file_size(file_size: int) -> None:
    """Validate that the uploaded file doesn't exceed size limits."""
    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.max_file_size_mb}MB limit",
        )
