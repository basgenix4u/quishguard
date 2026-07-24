"""
QuishGuard — Local Heuristic URL Analysis Engine

Tier 1 of the three-tier threat intelligence system.
Always runs, no external dependency, <5ms response time.
Uses the URL lexical classifier for initial phishing probability.
"""

from typing import Dict

from app.ml.url_classifier import URLClassifierService


class LocalHeuristicsEngine:
    """
    Local heuristic URL analysis — always available, no external API dependency.

    Uses the URLClassifierService (XGBoost or rule-based) to compute
    a lexical phishing score.
    """

    def __init__(self):
        self.url_classifier = URLClassifierService()

    def analyze(self, url: str) -> Dict:
        """
        Run local heuristic analysis on a URL.

        Returns:
            {
                "tier": 1,
                "source": "local_heuristics",
                "score": float (0–1, phishing probability),
                "is_phishing": bool,
                "features": dict,
                "method": "xgboost" | "heuristic",
                "latency_ms": float,
            }
        """
        import time
        start = time.time()

        result = self.url_classifier.classify(url)

        latency_ms = (time.time() - start) * 1000

        return {
            "tier": 1,
            "source": "local_heuristics",
            "score": result["lexical_score"],
            "is_phishing": result["is_phishing"],
            "features": result["features"],
            "method": result["method"],
            "latency_ms": round(latency_ms, 2),
        }
