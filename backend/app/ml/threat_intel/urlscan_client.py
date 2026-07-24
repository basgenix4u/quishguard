"""
QuishGuard — urlscan.io Client

Tier 2 of the three-tier threat intelligence system.
Free API (no key required for basic use), provides detailed scan results
including page screenshot, redirected URLs, and security assessments.
"""

from typing import Dict, Optional

import httpx
from loguru import logger

from app.config import settings


class UrlscanClient:
    """
    urlscan.io API client for URL reputation checking.

    Submits a URL for scanning and retrieves the analysis result.
    Free tier allows ~100 scans/day without API key.
    """

    BASE_URL = "https://urlscan.io/api/v1"

    def __init__(self):
        self.api_key = settings.urlscan_api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def analyze(self, url: str) -> Dict:
        """
        Submit a URL to urlscan.io for analysis and retrieve results.

        Returns:
            {
                "tier": 2,
                "source": "urlscan",
                "score": float (0–1, phishing probability),
                "is_malicious": bool,
                "details": dict with scan results,
                "latency_ms": float,
            }
        """
        import time
        start = time.time()

        try:
            # Step 1: Submit URL for scanning
            submit_result = await self._submit_scan(url)

            if not submit_result.get("uuid"):
                logger.warning(f"urlscan.io submission failed for {url}")
                return self._fallback_result()

            # Step 2: Wait briefly and retrieve result
            scan_uuid = submit_result["uuid"]

            # Wait a few seconds for the scan to complete
            import asyncio
            await asyncio.sleep(3)

            # Step 3: Retrieve scan result
            scan_result = await self._retrieve_result(scan_uuid)

            # Parse result into our format
            score, is_malicious, details = self._parse_result(scan_result)

            latency_ms = (time.time() - start) * 1000

            return {
                "tier": 2,
                "source": "urlscan",
                "score": float(score),
                "is_malicious": is_malicious,
                "details": details,
                "latency_ms": round(latency_ms, 2),
            }

        except Exception as e:
            logger.warning(f"urlscan.io analysis failed: {e}")
            return self._fallback_result()

    async def _submit_scan(self, url: str) -> Dict:
        """Submit a URL for scanning on urlscan.io."""
        headers = {}
        if self.api_key:
            headers["API-Key"] = self.api_key

        payload = {
            "url": url,
            "visibility": "public",
        }

        response = await self.client.post(
            f"{self.BASE_URL}/scan/",
            json=payload,
            headers=headers,
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"urlscan.io submit returned status {response.status_code}")
            return {}

    async def _retrieve_result(self, scan_uuid: str) -> Dict:
        """Retrieve the scan result from urlscan.io."""
        response = await self.client.get(
            f"{self.BASE_URL}/result/{scan_uuid}/",
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {}

    def _parse_result(self, scan_result: Dict) -> tuple:
        """Parse urlscan.io result into our standard format."""
        if not scan_result:
            return 0.5, False, {}

        verdicts = scan_result.get("verdicts", {})
        overall = verdicts.get("overall", {})

        # urlscan.io overall verdict
        is_malicious = overall.get("malicious", False)
        tags = overall.get("tags", [])

        # Score based on verdicts
        if is_malicious:
            score = 0.85
        elif tags:
            score = 0.6 + min(0.3, len(tags) * 0.1)
        else:
            score = 0.15  # Likely safe

        details = {
            "malicious": is_malicious,
            "tags": tags,
            "scan_uuid": scan_result.get("task", {}).get("uuid", ""),
            "page_url": scan_result.get("task", {}).get("reportURL", ""),
            "redirects": len(scan_result.get("data", {}).get("requests", [])),
        }

        return score, is_malicious, details

    def _fallback_result(self) -> Dict:
        """Return neutral result when urlscan.io is unavailable."""
        return {
            "tier": 2,
            "source": "urlscan",
            "score": 0.5,
            "is_malicious": False,
            "details": {"error": "urlscan.io unavailable"},
            "latency_ms": 0,
        }

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
