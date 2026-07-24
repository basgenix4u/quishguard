"""
QuishGuard — API Key ORM Model

Compatible with both PostgreSQL (UUID) and SQLite (String).
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=100)  # requests per hour
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc))
    expires_at = Column(DateTime, nullable=True)

    scans = relationship("Scan", back_populates="api_key")

    def __repr__(self) -> str:
        return f"<ApiKey(id={self.id}, name={self.name}, is_active={self.is_active})>"
