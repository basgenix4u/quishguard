"""
QuishGuard — Scan API Endpoints

POST /scans — Submit image for unified scan
GET /scans/{scan_id} — Retrieve scan result
GET /scans/{scan_id}/heatmap — Get artifact heatmap image

Note: stats and history endpoints are in history.py and must be
registered BEFORE the {scan_id} catch-all route.
"""

import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import validate_file_size, validate_file_type, verify_api_key
from app.models.api_key import ApiKey
from app.models.scan import Scan
from app.schemas.scan import ScanOptions, ScanResponse, QRAnalysis, AIImageAnalysis, AIImageDetails
from app.services.unified_scanner import UnifiedScannerService

router = APIRouter()

# Singleton scanner service (initialized once)
scanner_service: Optional[UnifiedScannerService] = None


def get_scanner_service() -> UnifiedScannerService:
    """Get or initialize the unified scanner service."""
    global scanner_service
    if scanner_service is None:
        scanner_service = UnifiedScannerService()
    return scanner_service


@router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    file: UploadFile = File(..., description="Image file (PNG, JPG, WEBP)"),
    scan_options: str = Form(default='{"ai_check": true, "qr_check": true}', description="JSON scan options"),
    db: AsyncSession = Depends(get_db),
    api_key: Optional[ApiKey] = Depends(verify_api_key),
):
    """
    Submit an image for unified threat scan.
    """
    # Validate file type
    ext = validate_file_type(file.filename or "unknown.jpg")

    # Read file content
    content = await file.read()

    # Validate file size
    validate_file_size(len(content))

    # Parse scan options
    import json
    try:
        options_dict = json.loads(scan_options)
        options = ScanOptions(**options_dict)
    except (json.JSONDecodeError, Exception):
        options = ScanOptions()

    # Save uploaded file
    scan_id = str(uuid.uuid4())
    filename = f"{scan_id}.{ext}"
    upload_path = settings.upload_path / filename
    upload_path.parent.mkdir(parents=True, exist_ok=True)

    import aiofiles
    async with aiofiles.open(str(upload_path), "wb") as f:
        await f.write(content)

    # Compute image hash
    from app.ml.utils import compute_image_hash
    image_hash = compute_image_hash(upload_path)

    # Check if this exact image was already scanned
    existing = await db.execute(
        select(Scan).where(Scan.image_hash == image_hash)
    )
    existing_scan = existing.scalar_one_or_none()
    if existing_scan:
        logger.info(f"Returning cached scan result for hash: {image_hash}")
        return _scan_to_response(existing_scan)

    # Run unified scan pipeline
    scanner = get_scanner_service()
    scan_result = await scanner.scan(upload_path, options)

    # Update scan_result with computed hash
    scan_result.image_hash = image_hash

    # Save to database
    db_scan = Scan(
        id=scan_id,
        image_filename=filename,
        image_hash=image_hash,
        ai_verdict=scan_result.ai_verdict,
        ai_confidence=scan_result.ai_confidence,
        ai_details=scan_result.ai_details,
        qr_detected=scan_result.qr_detected,
        qr_payload=scan_result.qr_payload,
        quish_verdict=scan_result.quish_verdict,
        quish_confidence=scan_result.quish_confidence,
        quish_details=scan_result.quish_details,
        status="completed",
        api_key_id=api_key.id if api_key else None,
    )
    db.add(db_scan)
    await db.flush()

    return _scan_to_response(db_scan)


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a scan result by ID."""
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    db_scan = result.scalar_one_or_none()

    if db_scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found",
        )

    return _scan_to_response(db_scan)


@router.get("/{scan_id}/heatmap")
async def get_heatmap(
    scan_id: str,
):
    """Get the artifact heatmap image for a scan."""
    from fastapi.responses import FileResponse

    heatmap_path = settings.upload_path / "heatmaps" / f"{scan_id}_heatmap.png"

    if not heatmap_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Heatmap not found for this scan",
        )

    return FileResponse(
        path=str(heatmap_path),
        media_type="image/png",
        filename=f"{scan_id}_heatmap.png",
    )


def _scan_to_response(db_scan: Scan) -> ScanResponse:
    """Convert a Scan ORM object to a ScanResponse Pydantic model."""
    ai_details_dict = db_scan.ai_details or {}
    ai_analysis = AIImageAnalysis(
        verdict=db_scan.ai_verdict or "uncertain",
        confidence=db_scan.ai_confidence or 0.0,
        details=AIImageDetails(
            frequency_score=ai_details_dict.get("frequency_score", 0.0),
            noise_score=ai_details_dict.get("noise_score", 0.0),
            artifact_heatmap_url=ai_details_dict.get("artifact_heatmap_url", ""),
        ),
    )

    quish_details_dict = db_scan.quish_details or {}
    threat_intel_data = quish_details_dict.get("threat_intel", {})

    from app.schemas.scan import QuishingDetails, ThreatIntelResult

    qr_analysis = QRAnalysis(
        qr_detected=db_scan.qr_detected or False,
        decoded_url=db_scan.qr_payload,
        quishing_verdict=db_scan.quish_verdict,
        quishing_confidence=db_scan.quish_confidence,
        details=QuishingDetails(
            url_lexical_score=quish_details_dict.get("url_lexical_score"),
            visual_tampering_score=quish_details_dict.get("visual_tampering_score"),
            threat_intel=ThreatIntelResult(
                safe_browsing=threat_intel_data.get("safe_browsing"),
                urlscan=threat_intel_data.get("urlscan"),
                reported=threat_intel_data.get("reported"),
            ) if threat_intel_data else None,
        ),
    )

    return ScanResponse(
        id=str(db_scan.id),
        status=db_scan.status,
        image_hash=db_scan.image_hash,
        ai_image_analysis=ai_analysis,
        qr_analysis=qr_analysis,
        created_at=db_scan.created_at,
    )
