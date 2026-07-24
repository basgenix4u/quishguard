"""
QuishGuard — Three-Tier Threat Intelligence Aggregator

Combines results from all three tiers:
- Tier 1: Local heuristic URL classifier (always runs)
- Tier 2: urlscan.io (runs if Tier 1 score > 0.3)
- Tier 3: Google Safe Browsing (runs if either Tier 1 or 2 score > 0.5)

Aggregates using weighted ensemble:
- Local: 30%, urlscan: 30%, Google Safe Browsing: 40%
"""

from typing import Dict, Optional

from loguru import logger

from app.ml.threat_intel.google_safe_browsing import GoogleSafeBrowsingClient
from app.ml.threat_intel.local_heuristics import LocalHeuristicsEngine
from app.ml.threat_intel.urlscan_client import UrlscanClient


class ThreatIntelAggregator:
    """
    Three-tier threat intelligence aggregation service.

    Orchestrates the progressive analysis pipeline and combines
    results from all available tiers.
    """

    # Aggregation weights
    WEIGHTS = {
        "local": 0.30,
        "urlscan": 0.30,
        "google_safe_browsing": 0.40,
    }

    # Thresholds for progressive tier activation
    TIER2_THRESHOLD = 0.3  # Run urlscan.io if local score > 0.3
    TIER3_THRESHOLD = 0.5  # Run GSB if any previous score > 0.5

    # Verdict thresholds
    SAFE_THRESHOLD = 0.3
    MALICIOUS_THRESHOLD = 0.7

    def __init__(self):
        self.local_engine = LocalHeuristicsEngine()
        self.urlscan_client = UrlscanClient()
        self.gsb_client = GoogleSafeBrowsingClient()

    async def analyze(self, url: str) -> Dict:
        """
        Run progressive three-tier analysis on a URL.

        Args:
            url: The decoded URL from a QR code.

        Returns:
            {
                "final_verdict": "safe" | "suspicious" | "malicious",
                "final_score": float (0–1),
                "tiers": {
                    "local": dict,
                    "urlscan": dict | None,
                    "google_safe_browsing": dict | None,
                },
                "contributing_factors": list of strings,
            }
        """
        tiers: Dict[str, Optional[Dict]] = {
            "local": None,
            "urlscan": None,
            "google_safe_browsing": None,
        }

        contributing_factors = []

        # === Tier 1: Local heuristics (always runs) ===
        local_result = self.local_engine.analyze(url)
        tiers["local"] = local_result
        local_score = local_result["score"]

        if local_result["is_phishing"]:
            contributing_factors.append(f"Local classifier flagged URL (score: {local_score:.2f})")

        # === Tier 2: urlscan.io (conditional) ===
        urlscan_result = None
        if local_score > self.TIER2_THRESHOLD:
            try:
                urlscan_result = await self.urlscan_client.analyze(url)
                tiers["urlscan"] = urlscan_result
            except Exception as e:
                logger.warning(f"Tier 2 (urlscan.io) failed: {e}")

        # === Tier 3: Google Safe Browsing (conditional) ===
        gsb_result = None
        max_previous_score = local_score
        if urlscan_result:
            max_previous_score = max(local_score, urlscan_result.get("score", 0))

        if max_previous_score > self.TIER3_THRESHOLD and self.gsb_client.api_key:
            try:
                gsb_result = await self.gsb_client.analyze(url)
                tiers["google_safe_browsing"] = gsb_result
            except Exception as e:
                logger.warning(f"Tier 3 (GSB) failed: {e}")

        # === Aggregate results ===
        final_score = self._aggregate_scores(tiers)

        if gsb_result and gsb_result.get("status") == "MALICIOUS":
            contributing_factors.append("Google Safe Browsing: MALICIOUS")
        if urlscan_result and urlscan_result.get("is_malicious"):
            contributing_factors.append("urlscan.io: flagged as malicious")
        if local_result.get("is_phishing"):
            contributing_factors.append("Local heuristic: phishing indicators detected")

        # Determine final verdict
        if final_score >= self.MALICIOUS_THRESHOLD:
            verdict = "malicious"
        elif final_score >= self.SAFE_THRESHOLD:
            verdict = "suspicious"
        else:
            verdict = "safe"

        return {
            "final_verdict": verdict,
            "final_score": float(final_score),
            "tiers": tiers,
            "contributing_factors": contributing_factors,
        }

    def _aggregate_scores(self, tiers: Dict) -> float:
        """Aggregate scores from available tiers using weighted ensemble."""
        scores: Dict[str, float] = {}

        if tiers["local"]:
            scores["local"] = tiers["local"]["score"]

        if tiers["urlscan"]:
            scores["urlscan"] = tiers["urlscan"]["score"]

        if tiers["google_safe_browsing"] and tiers["google_safe_browsing"].get("status") != "SKIPPED":
            scores["google_safe_browsing"] = tiers["google_safe_browsing"]["score"]

        if not scores:
            return 0.5

        # Normalize weights for available tiers
        available_weights = {k: self.WEIGHTS[k] for k in scores.keys()}
        total_weight = sum(available_weights.values())

        if total_weight == 0:
            return 0.5

        # Weighted average
        aggregated = sum(
            scores[k] * available_weights[k] for k in scores.keys()
        ) / total_weight

        return aggregated

    async def close(self) -> None:
        """Close all HTTP clients."""
        await self.urlscan_client.close()
        await self.gsb_client.close()
