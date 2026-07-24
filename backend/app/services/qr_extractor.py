"""
QuishGuard — QR Code Extraction & Decoding Service

Detects QR codes in uploaded images using OpenCV + pyzbar,
decodes the payload URL, and returns bounding box coordinates
for subsequent tampering analysis.
"""

from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np
from loguru import logger
from pyzbar.pyzbar import decode as pyzbar_decode


class QRExtractorService:
    """
    QR code extraction and decoding service.

    Uses OpenCV for detection and pyzbar for decoding.
    Returns decoded URLs and bounding box coordinates.
    """

    def extract(self, image_path: Path | str) -> Dict:
        """
        Detect and decode QR codes in an image.

        Args:
            image_path: Path to the image file.

        Returns:
            {
                "qr_detected": bool,
                "qr_codes": [
                    {
                        "data": str (decoded URL/payload),
                        "type": str ("QR_CODE"),
                        "rect": {"x": int, "y": int, "w": int, "h": int},
                        "quality": float (0-1, detection confidence),
                    }
                ],
                "total_found": int,
            }
        """
        image_path = Path(image_path)
        img = cv2.imread(str(image_path))

        if img is None:
            logger.warning(f"Could not read image: {image_path}")
            return {"qr_detected": False, "qr_codes": [], "total_found": 0}

        # Decode QR codes using pyzbar
        decoded_objects = pyzbar_decode(img)

        if not decoded_objects:
            # Try preprocessing to improve detection
            decoded_objects = self._enhanced_detection(img)

        qr_codes = []
        for obj in decoded_objects:
            if obj.type == "QRCODE":
                # Extract bounding rectangle
                x, y, w, h = obj.rect.left, obj.rect.top, obj.rect.width, obj.rect.height

                # Compute quality metric based on module clarity
                quality = self._compute_qr_quality(img, x, y, w, h)

                qr_data = obj.data.decode("utf-8", errors="replace")

                qr_codes.append({
                    "data": qr_data,
                    "type": obj.type,
                    "rect": {"x": x, "y": y, "w": w, "h": h},
                    "quality": float(quality),
                })

        return {
            "qr_detected": len(qr_codes) > 0,
            "qr_codes": qr_codes,
            "total_found": len(qr_codes),
        }

    def _enhanced_detection(self, img: np.ndarray) -> list:
        """
        Enhanced QR detection with image preprocessing.
        Handles cases where direct detection fails (low contrast, blur, etc.)
        """
        results = []

        # Strategy 1: Grayscale + threshold
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        decoded = pyzbar_decode(binary)
        if decoded:
            results.extend(decoded)

        # Strategy 2: Sharpening
        if not results:
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            sharpened = cv2.filter2D(gray, -1, kernel)
            decoded = pyzbar_decode(sharpened)
            if decoded:
                results.extend(decoded)

        # Strategy 3: Resize (small images may need upscaling)
        if not results:
            h, w = gray.shape
            if h < 300 or w < 300:
                scale = 3.0
                resized = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
                decoded = pyzbar_decode(resized)
                if decoded:
                    results.extend(decoded)

        return results

    def _compute_qr_quality(self, img: np.ndarray, x: int, y: int, w: int, h: int) -> float:
        """
        Compute a quality score for a detected QR code region.

        Higher quality = clearer modules = more reliable decoding.
        """
        # Extract QR region
        pad = 5
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(img.shape[1], x + w + pad)
        y2 = min(img.shape[0], y + h + pad)

        qr_region = img[y1:y2, x1:x2]
        gray = cv2.cvtColor(qr_region, cv2.COLOR_BGR2GRAY)

        # Compute clarity metrics
        contrast = np.std(gray) / 128.0  # Normalized contrast
        sharpness = self._compute_sharpness(gray)

        # Quality = weighted combination
        quality = 0.6 * min(contrast, 1.0) + 0.4 * min(sharpness, 1.0)

        return float(np.clip(quality, 0.0, 1.0))

    def _compute_sharpness(self, gray: np.ndarray) -> float:
        """Compute image sharpness using Laplacian variance."""
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        # Normalize: variance > 500 is typically sharp
        return min(1.0, variance / 500.0)
