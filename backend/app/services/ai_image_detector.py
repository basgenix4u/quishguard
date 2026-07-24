"""
QuishGuard — AI-Generated Image Detection Service

High-level service that orchestrates the AI-image detection pipeline.
Wraps the EfficientNetB4Classifier with frequency and noise analysis.
"""

from pathlib import Path
from typing import Dict

from app.ml.efficientnet_classifier import AIImageDetectorService as MLDetector
from app.schemas.scan import AIImageAnalysis, AIImageDetails


class AIImageDetectorService:
    """
    AI-Generated Image Detection Service.

    Thin orchestration layer that wraps the ML detector
    and formats results into the API response schema.
    """

    def __init__(self):
        self.ml_detector = MLDetector()

    def analyze(self, image_path: Path | str) -> AIImageAnalysis:
        """
        Run AI-generated image detection on an uploaded image.

        Args:
            image_path: Path to the uploaded image file.

        Returns:
            AIImageAnalysis Pydantic model with verdict, confidence, and details.
        """
        result = self.ml_detector.analyze(image_path)

        return AIImageAnalysis(
            verdict=result["verdict"],
            confidence=result["confidence"],
            details=AIImageDetails(
                frequency_score=result["details"]["frequency_score"],
                noise_score=result["details"]["noise_score"],
                artifact_heatmap_url=result["details"]["artifact_heatmap_url"],
            ),
        )
