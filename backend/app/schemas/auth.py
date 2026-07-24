"""
QuishGuard — Auth Pydantic Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100, description="Descriptive name for the API key")
    rate_limit: int = Field(default=100, ge=10, le=10000, description="Max requests per hour")


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key: Optional[str] = Field(default=None, description="Full API key (shown only on creation)")
    is_active: bool = True
    rate_limit: int = 100
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ApiKeyListResponse(BaseModel):
    id: str
    name: str
    key_masked: str = Field(description="Masked key for display (e.g., 'qg_live_abc...xyz')")
    is_active: bool
    rate_limit: int
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
