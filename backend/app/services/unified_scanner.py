"""
QuishGuard — Unified Scanner Service

Orchestrates the complete scan pipeline:
- Always runs AI-image detection (if requested)
- If QR detected, runs quishing detection (if requested)
- Combines results into a unified scan result
"""

from pathlib import Path
from typing import Dict

from loguru import logger

from app.schemas.scan import AIImageAnalysis, QRAnalysis, ScanCreate, ScanOptions, ScanResponse
from app.services.ai_image_detector import AIImageDetectorService
from app.services.quishing_detector import QuishingDetectorService


class UnifiedScannerService:
    """
    Unified Scanner Service — the master orchestrator.

    Accepts an image and scan options, auto-routes to the
    appropriate detection pipelines, and combines results.
    """

    def __init__(self):
        self.ai_detector = AIImageDetectorService()
        self.quishing_detector = QuishingDetectorService()

    async def scan(self, image_path: Path | str, options: ScanOptions) -> ScanCreate:
        """
        Run the unified scan pipeline on an uploaded image.

        Args:
            image_path: Path to the uploaded image file.
            options: ScanOptions specifying which pipelines to run.

        Returns:
            ScanCreate Pydantic model with all detection results.
        """
        image_path = Path(image_path)

        ai_analysis = AIImageAnalysis()
        qr_analysis = QRAnalysis()

        # === AI-Image Detection Pipeline ===
        if options.ai_check:
            try:
                ai_analysis = self.ai_detector.analyze(image_path)
                logger.info(
                    f"AI detection result: verdict={ai_analysis.verdict}, "
                    f"confidence={ai_analysis.confidence:.2f}"
                )
            except Exception as e:
                logger.error(f"AI detection pipeline failed: {e}")
                ai_analysis = AIImageAnalysis(
                    verdict="uncertain",
                    confidence=0.0,
                )

        # === Quishing Detection Pipeline ===
        if options.qr_check:
            try:
                qr_analysis = await self.quishing_detector.analyze(image_path)
                logger.info(
                    f"QR detection result: detected={qr_analysis.qr_detected}, "
                    f"quish_verdict={qr_analysis.quishing_verdict}"
                )
            except Exception as e:
                logger.error(f"Quishing detection pipeline failed: {e}")
                qr_analysis = QRAnalysis(qr_detected=False)

        # === Build unified result ===
        scan_result = ScanCreate(
            image_filename=image_path.name,
            image_hash="",  # Will be set by the API endpoint
            ai_verdict=ai_analysis.verdict,
            ai_confidence=ai_analysis.confidence,
            ai_details={
                "frequency_score": ai_analysis.details.frequency_score,
                "noise_score": ai_analysis.details.noise_score,
                "artifact_heatmap_url": ai_analysis.details.artifact_heatmap_url,
            },
            qr_detected=qr_analysis.qr_detected,
            qr_payload=qr_analysis.decoded_url,
            quish_verdict=qr_analysis.quishing_verdict,
            quish_confidence=qr_analysis.quishing_confidence,
            quish_details={
                "url_lexical_score": qr_analysis.details.url_lexical_score,
                "visual_tampering_score": qr_analysis.details.visual_tampering_score,
                "threat_intel": qr_analysis.details.threat_intel,
            } if qr_analysis.qr_detected else {},
        )

        return scan_result

    async def close(self) -> None:
        """Close all sub-service resources."""
        await self.quishing_detector.close()
