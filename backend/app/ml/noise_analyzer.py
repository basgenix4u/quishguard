"""
QuishGuard — Noise Inconsistency Analyzer

AI-generated images often exhibit noise patterns that differ from
natural photographs:
- GANs produce inconsistent noise across different image regions
- Diffusion models leave subtle denoising artifacts
- Real photos have uniform sensor noise characteristics

This module analyzes local noise patterns for inconsistencies.
"""

from pathlib import Path
from typing import Dict

import cv2
import numpy as np
from loguru import logger


class NoiseAnalyzer:
    """
    Noise inconsistency analysis for AI-generated image detection.

    Extracts local noise residuals from multiple image patches and
    measures statistical inconsistency across them.
    """

    # Patch size for local noise analysis
    PATCH_SIZE = 64
    # Number of patches to sample
    NUM_PATCHES = 16
    # Threshold for inconsistency
    INCONSISTENCY_THRESHOLD = 0.3

    def analyze(self, image_path: Path | str) -> Dict:
        """
        Analyze noise inconsistency across an image.

        Args:
            image_path: Path to the image file.

        Returns:
            {
                "score": float (0–1, probability of being AI-generated),
                "variance_inconsistency": float,
                "kurtosis_inconsistency": float,
                "heatmap": np.ndarray (2D anomaly map, 0–1 range),
            }
        """
        image_path = Path(image_path)
        img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)

        if img is None:
            logger.warning(f"Could not read image: {image_path}")
            return {
                "score": 0.5,
                "variance_inconsistency": 0.5,
                "kurtosis_inconsistency": 0.5,
                "heatmap": np.zeros((100, 100), dtype=np.float32),
            }

        # Extract noise residual using high-pass filter
        noise_residual = self._extract_noise_residual(img)

        # Sample patches and compute local noise statistics
        patch_stats = self._compute_patch_statistics(noise_residual, img.shape)

        # Measure inconsistency across patches
        variance_inconsistency = self._measure_variance_inconsistency(patch_stats)
        kurtosis_inconsistency = self._measure_kurtosis_inconsistency(patch_stats)

        # Generate heatmap
        heatmap = self._generate_noise_heatmap(noise_residual, img.shape[:2])

        # Aggregate into composite score
        composite_score = self._aggregate(
            variance_inconsistency, kurtosis_inconsistency
        )

        return {
            "score": float(composite_score),
            "variance_inconsistency": float(variance_inconsistency),
            "kurtosis_inconsistency": float(kurtosis_inconsistency),
            "heatmap": heatmap,
        }

    def _extract_noise_residual(self, img: np.ndarray) -> np.ndarray:
        """Extract noise residual using a high-pass filter.

        Uses a Wiener-like filter approach: residual = original - denoised.
        """
        # Convert to grayscale for noise analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)

        # Apply Gaussian blur as simple denoising
        denoised = cv2.GaussianBlur(gray, (5, 5), sigmaX=1.0)

        # Noise residual = original - denoised
        residual = gray - denoised

        return residual

    def _compute_patch_statistics(
        self, noise_residual: np.ndarray, img_shape: tuple
    ) -> list:
        """Compute noise statistics for multiple patches of the image."""
        h, w = img_shape[:2]
        patch_h, patch_w = self.PATCH_SIZE, self.PATCH_SIZE

        patches = []
        rng = np.random.default_rng(42)

        # Sample random patches
        for _ in range(self.NUM_PATCHES):
            y = rng.integers(0, max(1, h - patch_h))
            x = rng.integers(0, max(1, w - patch_w))

            patch = noise_residual[y:y + patch_h, x:x + patch_w]

            stats = {
                "variance": float(np.var(patch)),
                "kurtosis": float(self._compute_kurtosis(patch)),
                "mean": float(np.mean(patch)),
                "std": float(np.std(patch)),
            }
            patches.append(stats)

        return patches

    def _compute_kurtosis(self, data: np.ndarray) -> float:
        """Compute kurtosis of a distribution (excess kurtosis)."""
        n = len(data.flatten())
        if n < 4:
            return 0.0

        mean = np.mean(data)
        std = np.std(data)

        if std == 0:
            return 0.0

        # Excess kurtosis
        kurtosis = np.mean(((data - mean) / std) ** 4) - 3.0
        return float(kurtosis)

    def _measure_variance_inconsistency(self, patch_stats: list) -> float:
        """Measure how inconsistent noise variance is across patches.

        Real photos have relatively uniform noise variance.
        AI-generated images often have wildly varying local noise levels.
        """
        variances = [s["variance"] for s in patch_stats]
        mean_var = np.mean(variances)

        if mean_var == 0:
            return 0.5

        # Coefficient of variation of variance across patches
        cv_var = np.std(variances) / mean_var

        # Map to score (higher CV → more inconsistent → more likely AI)
        score = min(1.0, cv_var / self.INCONSISTENCY_THRESHOLD)

        return float(score)

    def _measure_kurtosis_inconsistency(self, patch_stats: list) -> float:
        """Measure how inconsistent noise kurtosis is across patches.

        Real sensor noise is Gaussian (kurtosis ≈ 0).
        AI-generated noise may have varying kurtosis (non-Gaussian).
        """
        kurtoses = [s["kurtosis"] for s in patch_stats]
        mean_kurt = np.mean(kurtoses)

        # Measure deviation from Gaussian (kurtosis = 0)
        deviation = np.mean(np.abs(np.array(kurtoses)))

        # Also measure spread of kurtosis values
        spread = np.std(kurtoses)

        # Map to score
        score = min(1.0, (deviation + spread) / 3.0)

        return float(score)

    def _generate_noise_heatmap(
        self, noise_residual: np.ndarray, img_shape: tuple
    ) -> np.ndarray:
        """Generate a 2D anomaly heatmap from noise residual."""
        h, w = img_shape

        # Compute local variance map
        local_var = self._local_variance_map(noise_residual, block_size=32)

        # Compute deviation from global variance
        global_var = np.var(noise_residual)
        if global_var == 0:
            return np.zeros((h // 32, w // 32), dtype=np.float32)

        # Anomaly = deviation of local variance from global
        anomaly = np.abs(local_var - global_var) / (global_var + 1e-8)
        anomaly = np.clip(anomaly / 3.0, 0.0, 1.0)

        return anomaly.astype(np.float32)

    def _local_variance_map(
        self, residual: np.ndarray, block_size: int = 32
    ) -> np.ndarray:
        """Compute local variance in non-overlapping blocks."""
        h, w = residual.shape
        bh, bw = h // block_size, w // block_size

        var_map = np.zeros((bh, bw), dtype=np.float32)

        for i in range(bh):
            for j in range(bw):
                block = residual[
                    i * block_size:(i + 1) * block_size,
                    j * block_size:(j + 1) * block_size,
                ]
                var_map[i, j] = np.var(block)

        return var_map

    def _aggregate(
        self,
        variance_inconsistency: float,
        kurtosis_inconsistency: float,
    ) -> float:
        """Aggregate sub-scores into composite noise inconsistency score."""
        composite = 0.6 * variance_inconsistency + 0.4 * kurtosis_inconsistency
        return composite
