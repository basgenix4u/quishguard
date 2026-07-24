"""
QuishGuard — API Key Management Endpoints

POST /api-keys — Create a new API key
GET /api-keys — List all API keys (keys masked)
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import generate_api_key, mask_api_key, verify_api_key
from app.models.api_key import ApiKey
from app.models.scan import Scan
from app.schemas.auth import ApiKeyCreate, ApiKeyListResponse, ApiKeyResponse

router = APIRouter()


@router.post("", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_create: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    api_key: ApiKey = Depends(verify_api_key),
):
    """
    Create a new API key.

    Requires a valid existing API key for authorization.
    The raw key is returned ONLY on this response — store it securely.
    """
    raw_key, hashed_key = generate_api_key()

    new_key = ApiKey(
        key_hash=hashed_key,
        name=key_create.name,
        rate_limit=key_create.rate_limit,
        is_active=True,
    )
    db.add(new_key)
    await db.flush()

    # Refresh to get the generated ID
    await db.refresh(new_key)

    return ApiKeyResponse(
        id=str(new_key.id),
        name=new_key.name,
        key=raw_key,  # Show only on creation
        is_active=new_key.is_active,
        rate_limit=new_key.rate_limit,
        created_at=new_key.created_at,
        expires_at=new_key.expires_at,
    )


@router.get("", response_model=List[ApiKeyListResponse])
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    api_key: ApiKey = Depends(verify_api_key),
):
    """
    List all API keys (with keys masked for security).

    Requires a valid API key for authorization.
    """
    result = await db.execute(select(ApiKey).order_by(ApiKey.created_at.desc()))
    keys = result.scalars().all()

    return [
        ApiKeyListResponse(
            id=str(k.id),
            name=k.name,
            key_masked=mask_api_key(k.key_hash[:8] + "..." + k.key_hash[-4:]) if k.key_hash else "???",
            is_active=k.is_active,
            rate_limit=k.rate_limit,
            created_at=k.created_at,
            expires_at=k.expires_at,
        )
        for k in keys
    ]
