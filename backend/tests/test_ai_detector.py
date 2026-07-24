"""
QuishGuard — AI Image Detector Service Tests
"""

import io
import tempfile
from pathlib import Path
import pytest

from PIL import Image

from app.ml.frequency_analyzer import FrequencyAnalyzer
from app.ml.noise_analyzer import NoiseAnalyzer
from app.ml.efficientnet_classifier import AIImageDetectorService
from app.services.ai_image_detector import AIImageDetectorService as ServiceLayer


@pytest.fixture
def test_image_path():
    """Create a temporary test image."""
    img = Image.new("RGB", (256, 256), color=(128, 128, 128))
    # Add some noise to make it more realistic
    import numpy as np
    arr = np.array(img)
    noise = np.random.normal(0, 10, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    noisy_img = Image.fromarray(arr)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        noisy_img.save(f.name)
        yield Path(f.name)


def test_frequency_analyzer(test_image_path):
    """Test frequency domain analysis."""
    analyzer = FrequencyAnalyzer()
    result = analyzer.analyze(test_image_path)

    assert "score" in result
    assert 0.0 <= result["score"] <= 1.0
    assert "spectral_decay_score" in result
    assert "spike_score" in result
    assert "hf_energy_score" in result
    assert "heatmap" in result
    assert result["heatmap"].dtype.name.startswith("float")


def test_noise_analyzer(test_image_path):
    """Test noise inconsistency analysis."""
    analyzer = NoiseAnalyzer()
    result = analyzer.analyze(test_image_path)

    assert "score" in result
    assert 0.0 <= result["score"] <= 1.0
    assert "variance_inconsistency" in result
    assert "kurtosis_inconsistency" in result
    assert "heatmap" in result


def test_ai_detector_service(test_image_path):
    """Test full AI image detector service (heuristic mode)."""
    service = ServiceLayer()
    result = service.analyze(test_image_path)

    assert result.verdict in ["real", "fake", "uncertain"]
    assert 0.0 <= result.confidence <= 1.0
    assert result.details.frequency_score >= 0.0
    assert result.details.noise_score >= 0.0
