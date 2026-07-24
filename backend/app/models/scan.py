"""
QuishGuard — Scan ORM Model

Compatible with both PostgreSQL (UUID, JSONB) and SQLite (String, JSON).
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image_filename = Column(String(255), nullable=False, index=True)
    image_hash = Column(String(80), nullable=False, unique=True, index=True)

    # AI Image Analysis Results
    ai_verdict = Column(String(10), nullable=True)  # 'real' | 'fake' | 'uncertain'
    ai_confidence = Column(Float, nullable=True)
    ai_details = Column(JSON, nullable=True, default=dict)

    # QR Analysis Results
    qr_detected = Column(Boolean, default=False)
    qr_payload = Column(Text, nullable=True)

    # Quishing Analysis Results
    quish_verdict = Column(String(15), nullable=True)  # 'safe' | 'suspicious' | 'malicious'
    quish_confidence = Column(Float, nullable=True)
    quish_details = Column(JSON, nullable=True, default=dict)

    # Metadata
    status = Column(String(20), default="completed")  # 'completed' | 'processing' | 'failed'
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # API Key that performed the scan
    api_key_id = Column(String(36), ForeignKey("api_keys.id"), nullable=True)
    api_key = relationship("ApiKey", back_populates="scans")

    def __repr__(self) -> str:
        return f"<Scan(id={self.id}, ai_verdict={self.ai_verdict}, quish_verdict={self.quish_verdict})>"
