"""
QuishGuard — Scan Pydantic Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# === AI Image Analysis ===

class AIImageDetails(BaseModel):
    frequency_score: float = Field(default=0.0, ge=0.0, le=1.0, description="FFT frequency domain anomaly score")
    noise_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Noise inconsistency score")
    artifact_heatmap_url: str = Field(default="", description="URL to artifact heatmap image")


class AIImageAnalysis(BaseModel):
    verdict: str = Field(default="uncertain", description="Detection verdict: 'real', 'fake', or 'uncertain'")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score 0.0–1.0")
    details: AIImageDetails = Field(default_factory=AIImageDetails)


# === QR / Quishing Analysis ===

class ThreatIntelResult(BaseModel):
    safe_browsing: Optional[str] = None
    urlscan: Optional[str] = None
    reported: Optional[bool] = None


class QuishingDetails(BaseModel):
    url_lexical_score: Optional[float] = None
    visual_tampering_score: Optional[float] = None
    threat_intel: Optional[ThreatIntelResult] = None


class QRAnalysis(BaseModel):
    qr_detected: bool = False
    decoded_url: Optional[str] = None
    quishing_verdict: Optional[str] = None  # 'safe' | 'suspicious' | 'malicious'
    quishing_confidence: Optional[float] = None
    details: QuishingDetails = Field(default_factory=QuishingDetails)


# === Scan Response ===

class ScanResponse(BaseModel):
    id: str
    status: str = "completed"
    image_hash: str
    ai_image_analysis: AIImageAnalysis
    qr_analysis: QRAnalysis
    created_at: datetime

    model_config = {"from_attributes": True}


# === Scan History ===

class ScanHistoryResponse(BaseModel):
    items: List[ScanResponse]
    total: int
    page: int
    per_page: int
    pages: int


# === Scan Stats ===

class ScanStats(BaseModel):
    total_scans: int = 0
    ai_fake_count: int = 0
    ai_real_count: int = 0
    ai_uncertain_count: int = 0
    qr_detected_count: int = 0
    quish_malicious_count: int = 0
    quish_suspicious_count: int = 0
    quish_safe_count: int = 0
    avg_ai_confidence: float = 0.0
    scans_last_7_days: int = 0


# === Scan Options ===

class ScanOptions(BaseModel):
    ai_check: bool = True
    qr_check: bool = True


# === Scan Create (internal) ===

class ScanCreate(BaseModel):
    image_filename: str
    image_hash: str
    ai_verdict: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_details: Optional[Dict[str, Any]] = None
    qr_detected: bool = False
    qr_payload: Optional[str] = None
    quish_verdict: Optional[str] = None
    quish_confidence: Optional[float] = None
    quish_details: Optional[Dict[str, Any]] = None
    api_key_id: Optional[str] = None
