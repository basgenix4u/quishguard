"""
QuishGuard — Quishing Detection Service

High-level service that orchestrates the QR phishing detection pipeline:
1. QR code extraction and decoding
2. QR visual tampering detection
3. URL threat intelligence (three-tier aggregator)

Combines results into a unified quishing verdict.
"""

from pathlib import Path
from typing import Dict, Optional

from loguru import logger

from app.ml.qr_tampering_detector import QRTamperingDetector
from app.ml.threat_intel.aggregator import ThreatIntelAggregator
from app.schemas.scan import QuishingDetails, QRAnalysis, ThreatIntelResult
from app.services.qr_extractor import QRExtractorService


class QuishingDetectorService:
    """
    QR Phishing (Quishing) Detection Service.

    Orchestrates the full quishing pipeline:
    1. Extract and decode QR codes
    2. Check for visual tampering
    3. Analyze decoded URLs for phishing threats
    """

    # Aggregation weights for quishing verdict
    WEIGHT_URL = 0.50
    WEIGHT_TAMPERING = 0.30
    WEIGHT_QR_QUALITY = 0.20

    def __init__(self):
        self.qr_extractor = QRExtractorService()
        self.tampering_detector = QRTamperingDetector()
        self.threat_intel = ThreatIntelAggregator()

    async def analyze(self, image_path: Path | str) -> QRAnalysis:
        """
        Run full quishing detection pipeline on an image.

        Args:
            image_path: Path to the uploaded image file.

        Returns:
            QRAnalysis Pydantic model with detection results.
        """
        image_path = Path(image_path)

        # Step 1: Extract and decode QR codes
        qr_result = self.qr_extractor.extract(image_path)

        if not qr_result["qr_detected"]:
            return QRAnalysis(
                qr_detected=False,
                decoded_url=None,
                quishing_verdict=None,
                quishing_confidence=None,
                details=QuishingDetails(),
            )

        # Get the first (primary) QR code
        primary_qr = qr_result["qr_codes"][0]
        decoded_url = primary_qr["data"]
        qr_rect = primary_qr["rect"]

        # Step 2: Check for visual tampering
        tampering_result = self.tampering_detector.analyze(image_path, qr_rect)
        tampering_score = tampering_result["tampering_score"]

        # Step 3: Run URL threat intelligence
        url_threat_result = await self.threat_intel.analyze(decoded_url)
        url_score = url_threat_result["final_score"]

        # Step 4: Aggregate into final quishing verdict
        # Factor in QR quality (lower quality = less reliable = slightly more suspicious)
        quality_factor = 1.0 - primary_qr["quality"] * 0.3  # Low quality adds uncertainty

        composite_score = (
            self.WEIGHT_URL * url_score
            + self.WEIGHT_TAMPERING * tampering_score
            + self.WEIGHT_QR_QUALITY * quality_factor
        )

        # Determine verdict
        if composite_score >= 0.7:
            quish_verdict = "malicious"
        elif composite_score >= 0.35:
            quish_verdict = "suspicious"
        else:
            quish_verdict = "safe"

        # Confidence: distance from midpoint
        confidence = abs(composite_score - 0.5) * 2.0
        confidence = max(0.0, min(1.0, confidence))

        # Build threat intel result from tiers
        threat_intel_data = self._build_threat_intel_result(url_threat_result)

        return QRAnalysis(
            qr_detected=True,
            decoded_url=decoded_url,
            quishing_verdict=quish_verdict,
            quishing_confidence=float(confidence),
            details=QuishingDetails(
                url_lexical_score=url_threat_result["tiers"]["local"]["score"] if url_threat_result["tiers"]["local"] else None,
                visual_tampering_score=float(tampering_score),
                threat_intel=threat_intel_data,
            ),
        )

    def _build_threat_intel_result(self, url_threat_result: Dict) -> Optional[ThreatIntelResult]:
        """Build ThreatIntelResult from tier data."""
        gsb = url_threat_result["tiers"]["google_safe_browsing"]
        urlscan = url_threat_result["tiers"]["urlscan"]

        gsb_status = None
        reported = None

        if gsb:
            gsb_status = gsb.get("status")
            if gsb_status == "MALICIOUS":
                reported = True
            elif gsb_status == "SAFE":
                reported = False

        urlscan_status = None
        if urlscan:
            urlscan_status = "MALICIOUS" if urlscan.get("is_malicious") else "SAFE"

        return ThreatIntelResult(
            safe_browsing=gsb_status,
            urlscan=urlscan_status,
            reported=reported,
        )

    async def close(self) -> None:
        """Close threat intelligence HTTP clients."""
        await self.threat_intel.close()
