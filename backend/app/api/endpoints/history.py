"""
QuishGuard — History & Stats API Endpoints

GET /scans/history — Paginated scan history with filters
GET /scans/stats — Dashboard statistics
"""

import math
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.scan import Scan
from app.schemas.scan import ScanHistoryResponse, ScanStats, ScanResponse
from app.api.endpoints.scan import _scan_to_response

router = APIRouter()


@router.get("/history", response_model=ScanHistoryResponse)
async def get_scan_history(
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    ai_verdict: Optional[str] = Query(default=None, description="Filter by AI verdict: real, fake, uncertain"),
    quish_verdict: Optional[str] = Query(default=None, description="Filter by quish verdict: safe, suspicious, malicious"),
    date_from: Optional[str] = Query(default=None, description="Start date (ISO8601)"),
    date_to: Optional[str] = Query(default=None, description="End date (ISO8601)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated scan history with optional filters.
    """
    # Build base query with filters
    query = select(Scan)

    if ai_verdict:
        query = query.where(Scan.ai_verdict == ai_verdict)
    if quish_verdict:
        query = query.where(Scan.quish_verdict == quish_verdict)
    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from)
            query = query.where(Scan.created_at >= dt_from)
        except ValueError:
            pass
    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to)
            query = query.where(Scan.created_at <= dt_to)
        except ValueError:
            pass

    # Count total matching records
    count_query = select(func.count(Scan.id))
    if ai_verdict:
        count_query = count_query.where(Scan.ai_verdict == ai_verdict)
    if quish_verdict:
        count_query = count_query.where(Scan.quish_verdict == quish_verdict)
    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from)
            count_query = count_query.where(Scan.created_at >= dt_from)
        except ValueError:
            pass
    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to)
            count_query = count_query.where(Scan.created_at <= dt_to)
        except ValueError:
            pass

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.order_by(Scan.created_at.desc()).offset(offset).limit(per_page)

    result = await db.execute(query)
    scans = result.scalars().all()

    items = [_scan_to_response(scan) for scan in scans]
    total_pages = math.ceil(total / per_page) if total > 0 else 1

    return ScanHistoryResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=total_pages,
    )


@router.get("/stats", response_model=ScanStats)
async def get_scan_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    Get dashboard statistics for all scans.
    """
    total_result = await db.execute(select(func.count(Scan.id)))
    total_scans = total_result.scalar() or 0

    ai_fake_count = (await db.execute(select(func.count(Scan.id)).where(Scan.ai_verdict == "fake"))).scalar() or 0
    ai_real_count = (await db.execute(select(func.count(Scan.id)).where(Scan.ai_verdict == "real"))).scalar() or 0
    ai_uncertain_count = (await db.execute(select(func.count(Scan.id)).where(Scan.ai_verdict == "uncertain"))).scalar() or 0

    qr_detected_count = (await db.execute(select(func.count(Scan.id)).where(Scan.qr_detected == True))).scalar() or 0

    quish_malicious_count = (await db.execute(select(func.count(Scan.id)).where(Scan.quish_verdict == "malicious"))).scalar() or 0
    quish_suspicious_count = (await db.execute(select(func.count(Scan.id)).where(Scan.quish_verdict == "suspicious"))).scalar() or 0
    quish_safe_count = (await db.execute(select(func.count(Scan.id)).where(Scan.quish_verdict == "safe"))).scalar() or 0

    avg_result = await db.execute(select(func.avg(Scan.ai_confidence)).where(Scan.ai_confidence.isnot(None)))
    avg_ai_confidence = avg_result.scalar() or 0.0

    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    scans_last_7_days = (await db.execute(select(func.count(Scan.id)).where(Scan.created_at >= seven_days_ago))).scalar() or 0

    return ScanStats(
        total_scans=total_scans,
        ai_fake_count=ai_fake_count,
        ai_real_count=ai_real_count,
        ai_uncertain_count=ai_uncertain_count,
        qr_detected_count=qr_detected_count,
        quish_malicious_count=quish_malicious_count,
        quish_suspicious_count=quish_suspicious_count,
        quish_safe_count=quish_safe_count,
        avg_ai_confidence=float(avg_ai_confidence) if avg_ai_confidence else 0.0,
        scans_last_7_days=scans_last_7_days,
    )
