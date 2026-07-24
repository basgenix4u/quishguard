"""
QuishGuard — FFT Frequency-Domain Analyzer

AI-generated images often exhibit distinct frequency-domain artifacts:
- GAN/diffusion models produce spectral signatures in high-frequency bands
- Synthetic images show periodic patterns in FFT magnitude spectrum
- Real photographs have natural, smooth spectral decay

This module analyzes the 2D FFT magnitude spectrum to detect these artifacts.
"""

from pathlib import Path
from typing import Dict

import cv2
import numpy as np
from loguru import logger


class FrequencyAnalyzer:
    """
    Frequency-domain analysis for AI-generated image detection.

    Analyzes the 2D FFT magnitude spectrum for:
    1. Spectral decay pattern (natural vs. artificial)
    2. Periodic frequency spikes (GAN grid artifacts)
    3. High-frequency energy distribution anomalies
    """

    # Threshold for frequency anomaly detection
    DECAY_ANOMALY_THRESHOLD = 0.15
    SPIKE_THRESHOLD = 3.0  # Standard deviations above mean
    HF_ENERGY_THRESHOLD = 0.25

    def analyze(self, image_path: Path | str) -> Dict:
        """
        Analyze an image's frequency domain for AI-generation artifacts.

        Args:
            image_path: Path to the image file.

        Returns:
            {
                "score": float (0–1, probability of being AI-generated),
                "spectral_decay_score": float,
                "spike_score": float,
                "hf_energy_score": float,
                "heatmap": np.ndarray (2D anomaly map, 0–1 range),
            }
        """
        image_path = Path(image_path)
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

        if img is None:
            logger.warning(f"Could not read image: {image_path}")
            return {
                "score": 0.5,
                "spectral_decay_score": 0.5,
                "spike_score": 0.0,
                "hf_energy_score": 0.5,
                "heatmap": np.zeros((100, 100), dtype=np.float32),
            }

        # Resize to standard size for consistent analysis
        img = cv2.resize(img, (512, 512))

        # Compute 2D FFT
        fft = np.fft.fft2(img)
        fft_shifted = np.fft.fftshift(fft)
        magnitude_spectrum = np.log1p(np.abs(fft_shifted))

        # Normalize magnitude spectrum
        magnitude_norm = magnitude_spectrum / magnitude_spectrum.max()

        # === Analysis 1: Spectral Decay ===
        spectral_decay_score = self._analyze_spectral_decay(magnitude_norm)

        # === Analysis 2: Frequency Spikes ===
        spike_score = self._analyze_frequency_spikes(magnitude_norm)

        # === Analysis 3: High-Frequency Energy ===
        hf_energy_score = self._analyze_hf_energy(magnitude_norm)

        # Generate anomaly heatmap
        heatmap = self._generate_frequency_heatmap(magnitude_norm)

        # Aggregate into composite score
        composite_score = self._aggregate(
            spectral_decay_score, spike_score, hf_energy_score
        )

        return {
            "score": float(composite_score),
            "spectral_decay_score": float(spectral_decay_score),
            "spike_score": float(spike_score),
            "hf_energy_score": float(hf_energy_score),
            "heatmap": heatmap,
        }

    def _analyze_spectral_decay(self, magnitude: np.ndarray) -> float:
        """Analyze how smoothly the spectrum decays from center to edges.

        Natural images have smooth, monotonic spectral decay.
        AI-generated images often have irregular decay patterns.
        """
        h, w = magnitude.shape
        center_y, center_x = h // 2, w // 2

        # Create radial distance map
        y_coords, x_coords = np.ogrid[:h, :w]
        radial_dist = np.sqrt(
            (y_coords - center_y) ** 2 + (x_coords - center_x) ** 2
        )
        radial_dist_norm = radial_dist / radial_dist.max()

        # Expected natural decay (exponential)
        expected_decay = np.exp(-3.0 * radial_dist_norm)

        # Actual average spectrum at each radial distance
        actual_decay = np.zeros_like(expected_decay)
        bins = np.linspace(0, 1, 50)
        for i in range(len(bins) - 1):
            mask = (radial_dist_norm >= bins[i]) & (radial_dist_norm < bins[i + 1])
            if mask.any():
                actual_decay[mask] = magnitude[mask].mean()

        # Normalize actual decay
        actual_decay_norm = actual_decay / actual_decay.max() if actual_decay.max() > 0 else actual_decay

        # Compute deviation from natural decay
        deviation = np.mean(np.abs(actual_decay_norm - expected_decay))

        # Map deviation to score (higher deviation → more likely AI-generated)
        score = min(1.0, deviation / self.DECAY_ANOMALY_THRESHOLD * 2.0)

        return float(score)

    def _analyze_frequency_spikes(self, magnitude: np.ndarray) -> float:
        """Detect periodic frequency spikes characteristic of GAN grid artifacts.

        GANs often produce grid-like patterns that manifest as
        regular spikes in the frequency domain.
        """
        mean_val = magnitude.mean()
        std_val = magnitude.std()

        if std_val == 0:
            return 0.0

        # Find peaks that exceed threshold
        threshold = mean_val + self.SPIKE_THRESHOLD * std_val
        peaks = magnitude > threshold

        # Count peaks and compute their regularity
        peak_count = peaks.sum()

        # Check for periodic patterns in peak locations
        if peak_count < 10:
            return 0.0

        # Compute regularity of peak spacing
        peak_rows, peak_cols = np.where(peaks)

        # If peaks form grid patterns, they'll have consistent row/column spacing
        if len(peak_rows) > 2 and len(peak_cols) > 2:
            row_spacing = np.diff(np.sort(np.unique(peak_rows)))
            col_spacing = np.diff(np.sort(np.unique(peak_cols)))

            # Regular grid patterns have consistent spacing
            row_regularity = 1.0 - (np.std(row_spacing) / (np.mean(row_spacing) + 1))
            col_regularity = 1.0 - (np.std(col_spacing) / (np.mean(col_spacing) + 1))

            regularity = (row_regularity + col_regularity) / 2.0

            # Map to score
            score = regularity * min(1.0, peak_count / 100.0)
        else:
            score = 0.0

        return float(score)

    def _analyze_hf_energy(self, magnitude: np.ndarray) -> float:
        """Analyze high-frequency energy distribution.

        AI-generated images often have unusual high-frequency energy
        patterns — either too much (upsampling artifacts) or too little
        (diffusion model smoothing).
        """
        h, w = magnitude.shape
        center_y, center_x = h // 2, w // 2

        # Define high-frequency region (outer 30% of spectrum)
        y_coords, x_coords = np.ogrid[:h, :w]
        radial_dist = np.sqrt(
            (y_coords - center_y) ** 2 + (x_coords - center_x) ** 2
        )
        max_dist = radial_dist.max()

        hf_mask = radial_dist > 0.7 * max_dist
        lf_mask = radial_dist <= 0.3 * max_dist

        hf_energy = magnitude[hf_mask].mean() if hf_mask.any() else 0.0
        lf_energy = magnitude[lf_mask].mean() if lf_mask.any() else 0.0

        if lf_energy == 0:
            return 0.5

        # Ratio of high-frequency to low-frequency energy
        ratio = hf_energy / lf_energy

        # Natural images typically have ratio ~0.05–0.15
        # AI-generated images often have ratio outside this range
        if ratio < 0.05 or ratio > 0.3:
            score = min(1.0, abs(ratio - 0.1) / 0.2)
        else:
            score = 0.0

        return float(score)

    def _generate_frequency_heatmap(self, magnitude: np.ndarray) -> np.ndarray:
        """Generate a 2D anomaly heatmap from the frequency spectrum."""
        mean_val = magnitude.mean()
        std_val = magnitude.std()

        if std_val == 0:
            return np.zeros_like(magnitude)

        # Anomaly = deviation from expected smooth decay
        anomaly = np.abs(magnitude - mean_val) / (std_val + 1e-8)
        anomaly = np.clip(anomaly / 5.0, 0.0, 1.0)  # Scale to 0-1

        return anomaly.astype(np.float32)

    def _aggregate(
        self,
        spectral_decay: float,
        spike: float,
        hf_energy: float,
    ) -> float:
        """Aggregate sub-scores into composite frequency anomaly score."""
        weights = {
            "decay": 0.35,
            "spike": 0.40,
            "hf_energy": 0.25,
        }

        composite = (
            weights["decay"] * spectral_decay
            + weights["spike"] * spike
            + weights["hf_energy"] * hf_energy
        )

        return composite
