"""
QuishGuard — API Root Router
"""

from fastapi import APIRouter

from app.api.endpoints import auth, history, scan

api_router = APIRouter()

# Scan endpoints
api_router.include_router(scan.router, prefix="/scans", tags=["Scans"])

# History endpoints
api_router.include_router(history.router, prefix="/scans", tags=["History"])

# Auth / API Key endpoints
api_router.include_router(auth.router, prefix="/api-keys", tags=["API Keys"])
