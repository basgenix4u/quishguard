"""
QuishGuard — QR Extractor & Quishing Detector Tests
"""

import io
import tempfile
from pathlib import Path
import pytest

from PIL import Image

from app.services.qr_extractor import QRExtractorService
from app.ml.url_classifier import URLClassifierService, URLFeatureExtractor


@pytest.fixture
def test_image_no_qr():
    """Create a test image without a QR code."""
    img = Image.new("RGB", (200, 200), color=(255, 0, 0))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name)
        yield Path(f.name)


def test_qr_extractor_no_qr(test_image_no_qr):
    """Test QR extractor on an image with no QR code."""
    extractor = QRExtractorService()
    result = extractor.extract(test_image_no_qr)

    assert result["qr_detected"] == False
    assert result["qr_codes"] == []
    assert result["total_found"] == 0


class TestURLClassifier:
    """Test URL lexical classifier."""

    def test_suspicious_url(self):
        """Test classification of a suspicious/phishing URL."""
        classifier = URLClassifierService()
        result = classifier.classify(
            "http://login-secure-account.verify-now.xyz/banking/password-reset"
        )

        assert "lexical_score" in result
        assert result["lexical_score"] > 0.3  # Should flag suspicious keywords
        assert "features" in result
        assert "method" in result

    def test_legitimate_url(self):
        """Test classification of a legitimate URL."""
        classifier = URLClassifierService()
        result = classifier.classify("https://www.google.com/search?q=test")

        assert "lexical_score" in result
        # Google.com should score relatively low on phishing probability
        assert result["lexical_score"] < 0.7

    def test_ip_address_url(self):
        """Test classification of an IP-based URL (suspicious)."""
        classifier = URLClassifierService()
        result = classifier.classify("http://192.168.1.1/admin/login.php")

        assert result["features"]["has_ip"] == True
        assert result["lexical_score"] > 0.1  # IP addresses add suspicion

    def test_feature_extractor(self):
        """Test URL feature extraction."""
        extractor = URLFeatureExtractor()
        features = extractor.extract("https://www.example.com/path?query=test&id=1")

        assert len(features) == 24  # 24-dimensional feature vector
        assert features[0] > 0  # URL length > 0
        assert features[9] > 0  # Entropy > 0


def test_url_classifier_heuristic_mode():
    """Test that classifier works in heuristic mode (no pretrained model)."""
    classifier = URLClassifierService()
    result = classifier.classify(
        "http://free-gift-prize.claim-now.xyz/urgent-action-required"
    )

    assert result["method"] == "heuristic"
    assert result["lexical_score"] > 0.3  # Should flag suspicious keywords
