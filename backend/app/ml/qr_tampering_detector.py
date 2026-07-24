"""
QuishGuard — QR Code Visual Tampering Detector

Detects visual modifications to QR codes that may indicate a quishing attack:
- Overlay/ sticker attacks (a sticker placed over the real QR code)
- Logo injections (central logo that disrupts QR data)
- Color modifications (changing QR foreground/background)
- Structural modifications (adding/removing modules)

Uses a fine-tuned ResNet-18 when weights are available,
falls back to heuristic geometric analysis.
"""

from pathlib import Path
from typing import Dict, Optional

import cv2
import numpy as np
from loguru import logger

from app.config import settings


class QRTamperingDetector:
    """
    Visual QR tampering detection service.

    Analyzes detected QR code regions for signs of visual manipulation.
    """

    def __init__(self):
        self.model: Optional[object] = None
        self.model_loaded = False
        self._load_model()

    def _load_model(self) -> None:
        """Attempt to load pretrained ResNet-18 QR tampering model."""
        model_path = Path(settings.qr_tampering_model_path)

        if model_path.exists():
            try:
                import torch
                import torch.nn as nn
                from torchvision.models import resnet18, ResNet18_Weights

                self.model = resnet18(weights=ResNet18_Weights.DEFAULT)
                # Replace final layer for 2-class: tampered / authentic
                self.model.fc = nn.Linear(self.model.fc.in_features, 2)
                state_dict = torch.load(model_path, map_location="cpu", weights_only=True)
                self.model.load_state_dict(state_dict)
                self.model.eval()
                self.model_loaded = True
                logger.info(f"✅ Loaded QR tampering model from {model_path}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load QR tampering model: {e}. Using heuristic mode.")
                self.model = None
                self.model_loaded = False
        else:
            logger.info(f"ℹ️ No pretrained QR tampering model at {model_path}. Using heuristic mode.")

    def analyze(self, image_path: Path | str, qr_region: Optional[Dict] = None) -> Dict:
        """
        Analyze a QR code region for visual tampering.

        Args:
            image_path: Path to the full image.
            qr_region: Dict with "x", "y", "w", "h" bounding box of the QR code.

        Returns:
            {
                "tampering_score": float (0–1, probability of tampering),
                "overlay_detected": bool,
                "logo_injection_detected": bool,
                "color_modification_detected": bool,
                "structural_score": float,
                "method": "resnet18" | "heuristic",
            }
        """
        image_path = Path(image_path)
        img = cv2.imread(str(image_path))

        if img is None:
            logger.warning(f"Could not read image: {image_path}")
            return self._default_result()

        # Extract QR region if bounding box provided
        qr_img = self._extract_qr_region(img, qr_region)

        if self.model_loaded:
            result = self._analyze_deep(qr_img)
            result["method"] = "resnet18"
        else:
            result = self._analyze_heuristic(qr_img)
            result["method"] = "heuristic"

        return result

    def _extract_qr_region(self, img: np.ndarray, qr_region: Optional[Dict]) -> np.ndarray:
        """Extract the QR code region from the full image."""
        if qr_region is None:
            # Use the entire image
            return img

        x, y, w, h = qr_region["x"], qr_region["y"], qr_region["w"], qr_region["h"]
        # Add padding
        pad = 10
        x = max(0, x - pad)
        y = max(0, y - pad)
        w = min(img.shape[1] - x, w + 2 * pad)
        h = min(img.shape[0] - y, h + 2 * pad)

        return img[y:y + h, x:x + w]

    def _analyze_deep(self, qr_img: np.ndarray) -> Dict:
        """Run ResNet-18 inference on the QR region."""
        try:
            import torch
            from torchvision import transforms

            # Convert to PIL for torchvision transforms
            qr_rgb = cv2.cvtColor(qr_img, cv2.COLOR_BGR2RGB)
            from PIL import Image as PILImage
            pil_img = PILImage.fromarray(qr_rgb)

            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])

            input_tensor = transform(pil_img).unsqueeze(0)

            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                tampered_prob = probabilities[0][1].item()

            return {
                "tampering_score": float(tampered_prob),
                "overlay_detected": tampered_prob > 0.6,
                "logo_injection_detected": tampered_prob > 0.5,
                "color_modification_detected": False,
                "structural_score": float(tampered_prob),
            }
        except Exception as e:
            logger.warning(f"Deep QR tampering analysis failed: {e}")
            return self._analyze_heuristic(qr_img)

    def _analyze_heuristic(self, qr_img: np.ndarray) -> Dict:
        """Heuristic analysis of QR code visual properties."""
        # Resize for consistent analysis
        qr_resized = cv2.resize(qr_img, (256, 256))
        gray = cv2.cvtColor(qr_resized, cv2.COLOR_BGR2GRAY)

        score = 0.0

        # Check 1: Overlay detection (color inconsistency in QR region)
        overlay_detected, overlay_score = self._detect_overlay(qr_resized)
        score += overlay_score * 0.35

        # Check 2: Logo injection (central region disruption)
        logo_detected, logo_score = self._detect_logo_injection(gray)
        score += logo_score * 0.35

        # Check 3: Color modification check
        color_mod, color_score = self._check_color_modification(qr_resized)
        score += color_score * 0.15

        # Check 4: Structural consistency
        structural_score = self._check_structural_consistency(gray)
        score += structural_score * 0.15

        return {
            "tampering_score": min(1.0, score),
            "overlay_detected": overlay_detected,
            "logo_injection_detected": logo_detected,
            "color_modification_detected": color_mod,
            "structural_score": float(structural_score),
        }

    def _detect_overlay(self, qr_img: np.ndarray) -> tuple:
        """Detect overlay/sticker attacks by checking for color inconsistencies."""
        hsv = cv2.cvtColor(qr_img, cv2.COLOR_BGR2HSV)

        # Check for unusual color regions (overlays often use different color)
        # Standard QR codes are black on white, unusual colors suggest overlay
        h_std = np.std(hsv[:, :, 0])

        overlay_detected = h_std > 30  # High hue variation suggests overlay
        score = min(1.0, h_std / 60.0)

        return overlay_detected, float(score)

    def _detect_logo_injection(self, gray: np.ndarray) -> tuple:
        """Detect logo injection by analyzing the central region of the QR code."""
        h, w = gray.shape
        center_region = gray[h // 3:2 * h // 3, w // 3:2 * w // 3]

        # Check if center region has unusual patterns (not pure black/white modules)
        center_std = np.std(center_region)
        center_mean = np.mean(center_region)

        # QR code center should be mostly black/white modules
        # A logo injection creates intermediate gray values
        logo_detected = center_std > 20 and abs(center_mean - 128) < 80
        score = min(1.0, center_std / 50.0)

        return logo_detected, float(score)

    def _check_color_modification(self, qr_img: np.ndarray) -> tuple:
        """Check if QR code colors have been modified from standard black/white."""
        gray = cv2.cvtColor(qr_img, cv2.COLOR_BGR2GRAY)

        # Standard QR: mostly 0 (black) or 255 (white)
        histogram = np.histogram(gray, bins=256, range=(0, 255))[0]

        # Count pixels in intermediate range (50–200) — these suggest color modification
        intermediate = histogram[50:200].sum()
        total = histogram.sum()

        ratio = intermediate / total if total > 0 else 0
        detected = ratio > 0.15
        score = min(1.0, ratio / 0.3)

        return detected, float(score)

    def _check_structural_consistency(self, gray: np.ndarray) -> float:
        """Check structural consistency of QR modules."""
        # Apply adaptive threshold to isolate modules
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Check module size consistency using connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary, connectivity=8
        )

        if num_labels < 3:
            return 0.5

        # Filter small components (noise)
        sizes = stats[1:, cv2.CC_STAT_AREA]
        sizes = sizes[sizes > 5]  # Remove noise

        if len(sizes) == 0:
            return 0.5

        # Consistent QR modules should have similar sizes
        size_std = np.std(sizes)
        size_mean = np.mean(sizes)

        if size_mean == 0:
            return 0.5

        # High variation in module sizes suggests tampering
        cv = size_std / size_mean
        score = min(1.0, cv / 1.0)

        return float(score)

    def _default_result(self) -> Dict:
        """Return default result when image cannot be processed."""
        return {
            "tampering_score": 0.5,
            "overlay_detected": False,
            "logo_injection_detected": False,
            "color_modification_detected": False,
            "structural_score": 0.5,
            "method": "heuristic",
        }
