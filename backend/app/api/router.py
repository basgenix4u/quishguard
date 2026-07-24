"""
QuishGuard — API Root Router

Route ordering matters: /scans/stats and /scans/history must be
registered BEFORE /scans/{scan_id} to avoid the catch-all route
matching "stats" or "history" as a scan_id.
"""

from fastapi import APIRouter

from app.api.endpoints import auth, history, scan

api_router = APIRouter()

# Register stats and history routes FIRST (before catch-all {scan_id})
api_router.include_router(history.router, prefix="/scans", tags=["History"])

# Then register scan routes (includes {scan_id} catch-all)
api_router.include_router(scan.router, prefix="/scans", tags=["Scans"])

# Auth / API Key endpoints
api_router.include_router(auth.router, prefix="/api-keys", tags=["API Keys"])
