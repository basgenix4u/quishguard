"""
QuishGuard — ML Image Preprocessing Utilities
"""

import io
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np
from PIL import Image

from app.config import settings


def load_image_as_array(image_path: Path | str) -> Tuple[np.ndarray, Image.Image]:
    """Load an image file as both a numpy array (cv2 format) and PIL Image.

    Returns:
        (cv2_image, pil_image) — cv2_image is BGR uint8, pil_image is RGB.
    """
    pil_image = Image.open(image_path).convert("RGB")
    cv2_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    return cv2_image, pil_image


def preprocess_for_efficientnet(
    pil_image: Image.Image, input_size: int = 380
) -> np.ndarray:
    """Preprocess a PIL image for EfficientNet-B4 inference.

    Steps: Resize → CenterCrop → Normalize (ImageNet stats)
    Returns a (1, 3, H, W) float32 numpy array.
    """
    # Resize maintaining aspect ratio, then center crop
    img = pil_image.resize((input_size, input_size), Image.Resampling.BILINEAR)

    # Convert to float32 numpy array [0, 1]
    img_array = np.array(img, dtype=np.float32) / 255.0

    # Normalize with ImageNet stats
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img_array = (img_array - mean) / std

    # Transpose to CHW format and add batch dimension
    img_array = np.transpose(img_array, (2, 0, 1))  # (H, W, C) → (C, H, W)
    img_array = np.expand_dims(img_array, axis=0)  # (C, H, W) → (1, C, H, W)

    return img_array


def compute_image_hash(image_path: Path | str) -> str:
    """Compute SHA-256 hash of an image file."""
    import hashlib
    h = hashlib.sha256()
    with open(image_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def save_heatmap(heatmap_array: np.ndarray, scan_id: str) -> Path:
    """Save a heatmap numpy array as a PNG file in the uploads directory.

    Args:
        heatmap_array: 2D float array (0–1 range)
        scan_id: Unique scan identifier

    Returns:
        Path to the saved heatmap image.
    """
    # Normalize heatmap to 0-255 range
    heatmap_normalized = (heatmap_array * 255).astype(np.uint8)
    # Apply color map (JET for visibility)
    heatmap_colored = cv2.applyColorMap(heatmap_normalized, cv2.COLORMAP_JET)

    output_dir = settings.upload_path / "heatmaps"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{scan_id}_heatmap.png"
    cv2.imwrite(str(output_path), heatmap_colored)

    return output_path
