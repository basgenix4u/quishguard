"""
QuishGuard — EfficientNet-B4 AI-Generated Image Classifier

Uses a fine-tuned EfficientNet-B4 model to classify images as
'real' (authentic photograph) or 'fake' (AI-generated / synthetic).

When pretrained weights are unavailable, falls back to heuristic analysis
using frequency and noise patterns.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from loguru import logger
from PIL import Image

from app.config import settings
from app.ml.frequency_analyzer import FrequencyAnalyzer
from app.ml.noise_analyzer import NoiseAnalyzer
from app.ml.utils import preprocess_for_efficientnet


class EfficientNetB4Classifier(nn.Module):
    """EfficientNet-B4 with a custom 2-class classification head."""

    def __init__(self, num_classes: int = 2):
        super().__init__()
        # Build EfficientNet-B4 backbone
        self.backbone = self._build_backbone()
        # Custom classifier head
        in_features = self.backbone.classifier[1].in_features  # 1792 for B4
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_features, num_classes),
        )

    def _build_backbone(self) -> nn.Module:
        """Build EfficientNet-B4 from torchvision."""
        from torchvision.models import efficientnet_b4, EfficientNet_B4_Weights
        weights = EfficientNet_B4_Weights.DEFAULT
        model = efficientnet_b4(weights=weights)
        return model

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)


class AIImageDetectorService:
    """
    AI-Generated Image Detection Service.

    Orchestrates an ensemble of:
    1. EfficientNet-B4 deep classifier (if weights available)
    2. FFT frequency-domain analysis
    3. Noise inconsistency analysis

    Aggregates results into a unified verdict.
    """

    # Verdict labels
    VERDICT_REAL = "real"
    VERDICT_FAKE = "fake"
    VERDICT_UNCERTAIN = "uncertain"

    # Ensemble weights when all three are available
    WEIGHTS_DEEP = 0.55
    WEIGHTS_FREQ = 0.25
    WEIGHTS_NOISE = 0.20

    # Ensemble weights when only heuristic methods available (no pretrained model)
    WEIGHTS_FREQ_NO_MODEL = 0.55
    WEIGHTS_NOISE_NO_MODEL = 0.45

    def __init__(self):
        self.model: Optional[EfficientNetB4Classifier] = None
        self.device = torch.device("cpu")
        self.model_loaded = False

        self.freq_analyzer = FrequencyAnalyzer()
        self.noise_analyzer = NoiseAnalyzer()

        self._load_model()

    def _load_model(self) -> None:
        """Attempt to load pretrained EfficientNet-B4 weights."""
        model_path = Path(settings.ai_detector_model_path)

        if model_path.exists():
            try:
                self.model = EfficientNetB4Classifier(num_classes=2)
                state_dict = torch.load(model_path, map_location=self.device, weights_only=True)
                self.model.load_state_dict(state_dict)
                self.model.eval()
                self.model_loaded = True
                logger.info(f"✅ Loaded AI detector model from {model_path}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load AI detector model: {e}. Using heuristic-only mode.")
                self.model = None
                self.model_loaded = False
        else:
            logger.info(f"ℹ️ No pretrained model at {model_path}. Running in heuristic-only mode.")
            # Still initialize the model architecture for training script reference
            self.model = EfficientNetB4Classifier(num_classes=2)
            self.model.eval()
            self.model_loaded = False

    def analyze(self, image_path: Path | str) -> Dict:
        """
        Run full AI-image detection pipeline on an uploaded image.

        Returns:
            {
                "verdict": "real" | "fake" | "uncertain",
                "confidence": 0.0–1.0,
                "details": {
                    "deep_classifier_score": float | None,
                    "frequency_score": float,
                    "noise_score": float,
                    "artifact_heatmap_url": str,
                }
            }
        """
        image_path = Path(image_path)

        # Run frequency analysis
        freq_result = self.freq_analyzer.analyze(image_path)
        frequency_score = freq_result["score"]

        # Run noise analysis
        noise_result = self.noise_analyzer.analyze(image_path)
        noise_score = noise_result["score"]

        # Run deep classifier if available
        deep_score: Optional[float] = None
        if self.model_loaded:
            deep_score = self._run_deep_classifier(image_path)

        # Aggregate scores into verdict
        verdict, confidence = self._aggregate_scores(
            deep_score=deep_score,
            frequency_score=frequency_score,
            noise_score=noise_score,
        )

        # Generate artifact heatmap
        heatmap = self._generate_heatmap(freq_result["heatmap"], noise_result["heatmap"])
        from app.ml.utils import save_heatmap
        import uuid
        scan_id = str(uuid.uuid4())
        heatmap_path = save_heatmap(heatmap, scan_id)
        heatmap_url = f"/api/v1/scans/{scan_id}/heatmap"

        return {
            "verdict": verdict,
            "confidence": confidence,
            "details": {
                "deep_classifier_score": deep_score,
                "frequency_score": frequency_score,
                "noise_score": noise_score,
                "artifact_heatmap_url": heatmap_url,
            },
        }

    def _run_deep_classifier(self, image_path: Path) -> float:
        """Run EfficientNet-B4 inference. Returns fake probability (0–1)."""
        try:
            pil_image = Image.open(image_path).convert("RGB")
            input_tensor = preprocess_for_efficientnet(pil_image)
            input_tensor = torch.from_numpy(input_tensor).to(self.device)

            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                # Class 1 = fake/synthetic
                fake_prob = probabilities[0][1].item()

            return fake_prob
        except Exception as e:
            logger.warning(f"Deep classifier inference failed: {e}")
            return None

    def _aggregate_scores(
        self,
        deep_score: Optional[float],
        frequency_score: float,
        noise_score: float,
    ) -> Tuple[str, float]:
        """Aggregate multiple detection scores into a final verdict.

        Each score represents probability of being AI-generated (0–1).

        Returns:
            (verdict: str, confidence: float)
        """
        if deep_score is not None:
            # Full ensemble: deep + freq + noise
            composite = (
                self.WEIGHTS_DEEP * deep_score
                + self.WEIGHTS_FREQ * frequency_score
                + self.WEIGHTS_NOISE * noise_score
            )
        else:
            # Heuristic-only: freq + noise
            composite = (
                self.WEIGHTS_FREQ_NO_MODEL * frequency_score
                + self.WEIGHTS_NOISE_NO_MODEL * noise_score
            )

        # Determine verdict based on composite score
        if composite >= 0.7:
            verdict = self.VERDICT_FAKE
        elif composite <= 0.3:
            verdict = self.VERDICT_REAL
        else:
            verdict = self.VERDICT_UNCERTAIN

        # Confidence: distance from the 0.5 midpoint, scaled to 0–1
        confidence = abs(composite - 0.5) * 2.0
        confidence = max(0.0, min(1.0, confidence))

        return verdict, confidence

    def _generate_heatmap(
        self, freq_heatmap: np.ndarray, noise_heatmap: np.ndarray
    ) -> np.ndarray:
        """Combine frequency and noise heatmaps into a unified artifact map."""
        # Ensure both heatmaps are the same shape
        if freq_heatmap.shape != noise_heatmap.shape:
            # Resize noise heatmap to match freq heatmap
            import cv2
            noise_heatmap = cv2.resize(
                noise_heatmap,
                (freq_heatmap.shape[1], freq_heatmap.shape[0]),
            )

        # Weighted average
        combined = 0.5 * freq_heatmap + 0.5 * noise_heatmap
        # Normalize to 0-1
        combined = np.clip(combined, 0.0, 1.0)

        return combined
