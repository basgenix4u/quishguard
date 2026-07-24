"""
QuishGuard — Google Safe Browsing API Client

Tier 3 of the three-tier threat intelligence system.
Industry-standard, free (up to 10K requests/day with API key).
Provides authoritative malicious/safe verdicts.
"""

from typing import Dict, List

import httpx
from loguru import logger

from app.config import settings


class GoogleSafeBrowsingClient:
    """
    Google Safe Browsing API client for URL threat checking.

    Requires a Google API key (optional — skips if not configured).
    Free tier allows up to 10,000 requests/day.
    """

    BASE_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

    # Threat types we check for
    THREAT_TYPES = [
        "MALWARE",
        "SOCIAL_ENGINEERING",
        "UNWANTED_SOFTWARE",
        "POTENTIALLY_HARMFUL_APPLICATION",
    ]

    # Platform types
    PLATFORM_TYPES = ["ANY_PLATFORM"]

    def __init__(self):
        self.api_key = settings.google_safe_browsing_api_key
        self.client_id = settings.google_safe_browsing_client_id
        self.client = httpx.AsyncClient(timeout=10.0)

    async def analyze(self, url: str) -> Dict:
        """
        Check a URL against Google Safe Browsing database.

        Returns:
            {
                "tier": 3,
                "source": "google_safe_browsing",
                "status": "MALICIOUS" | "SAFE" | "UNKNOWN",
                "score": float (0–1),
                "threat_types": list,
                "latency_ms": float,
            }
        """
        if not self.api_key:
            return {
                "tier": 3,
                "source": "google_safe_browsing",
                "status": "SKIPPED",
                "score": 0.5,
                "threat_types": [],
                "latency_ms": 0,
                "reason": "No API key configured",
            }

        import time
        start = time.time()

        try:
            result = await self._lookup_url(url)

            latency_ms = (time.time() - start) * 1000

            if result.get("matches"):
                threat_types = [m["threatType"] for m in result["matches"]]
                score = 0.95  # High confidence malicious
                status = "MALICIOUS"
            else:
                threat_types = []
                score = 0.05  # High confidence safe
                status = "SAFE"

            return {
                "tier": 3,
                "source": "google_safe_browsing",
                "status": status,
                "score": float(score),
                "threat_types": threat_types,
                "latency_ms": round(latency_ms, 2),
            }

        except Exception as e:
            logger.warning(f"Google Safe Browsing lookup failed: {e}")
            return {
                "tier": 3,
                "source": "google_safe_browsing",
                "status": "ERROR",
                "score": 0.5,
                "threat_types": [],
                "latency_ms": 0,
                "reason": str(e),
            }

    async def _lookup_url(self, url: str) -> Dict:
        """Submit URL lookup to Google Safe Browsing API."""
        payload = {
            "client": {
                "clientId": self.client_id,
                "clientVersion": "1.0.0",
            },
            "threatInfo": {
                "threatTypes": self.THREAT_TYPES,
                "platformTypes": self.PLATFORM_TYPES,
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}],
            },
        }

        response = await self.client.post(
            f"{self.BASE_URL}?key={self.api_key}",
            json=payload,
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"GSB API returned status {response.status_code}")
            return {}

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
