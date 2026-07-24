"""
QuishGuard — URL Lexical Classifier (XGBoost)

Classifies URLs as phishing/malicious or legitimate based on
lexical features extracted from the URL string itself.

Features include: length, entropy, brand impersonation keywords,
TLD suspiciousness, subdomain depth, special character patterns, etc.
"""

import math
import re
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from loguru import logger

from app.config import settings


# Suspicious keywords often used in phishing URLs
SUSPICIOUS_KEYWORDS = [
    "login", "signin", "account", "verify", "secure", "update",
    "confirm", "password", "credential", "auth", "token",
    "banking", "wallet", "payment", "transfer", "recover",
    "free", "gift", "bonus", "offer", "discount", "prize",
    "urgent", "immediate", "action", "required", "expire",
    "suspend", "restrict", "unlock", "reset", "alert",
]

# Legitimate brand names often impersonated
BRAND_KEYWORDS = [
    "google", "facebook", "apple", "amazon", "microsoft",
    "paypal", "netflix", "twitter", "instagram", "whatsapp",
    "bank", "chase", "wells", "citibank", "hsbc",
    "outlook", "gmail", "yahoo", "aol", "hotmail",
    "ebay", "linkedin", "dropbox", "slack", "zoom",
]

# Suspicious TLDs commonly used in phishing
SUSPICIOUS_TLDS = [
    ".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top",
    ".pw", ".cc", ".biz", ".info", ".click", ".link",
    ".win", ".download", ".loan", ".work", ".party",
]


class URLFeatureExtractor:
    """Extract lexical features from a URL string for phishing classification."""

    def extract(self, url: str) -> np.ndarray:
        """Extract a feature vector from a URL.

        Returns a 23-dimensional feature vector:
        [length, hostname_len, path_len, num_dots, num_hyphens, num_slashes,
         num_digits, num_special_chars, entropy, has_ip, num_subdomains,
         max_subdomain_len, has_https, has_suspicious_kw, num_suspicious_kw,
         has_brand_kw, is_brand_in_domain, has_suspicious_tld, num_at_symbols,
         num_percent_symbols, query_len, fragment_len, ratio_digits]
        """
        features = []

        # Basic length features
        features.append(len(url))                                     # 0: total length
        parsed = self._parse_url(url)

        hostname = parsed.get("hostname", "")
        path = parsed.get("path", "")
        query = parsed.get("query", "")
        fragment = parsed.get("fragment", "")

        features.append(len(hostname))                                # 1: hostname length
        features.append(len(path))                                    # 2: path length
        features.append(query.count("&") + 1 if query else 0)        # 3: number of query params

        # Character composition features
        features.append(url.count("."))                               # 4: number of dots
        features.append(url.count("-"))                               # 5: number of hyphens
        features.append(url.count("/"))                               # 6: number of slashes
        features.append(sum(c.isdigit() for c in url))               # 7: number of digits
        special_chars = sum(not c.isalnum() and c not in "./:_-=?&=#" for c in url)
        features.append(special_chars)                                # 8: special characters

        # Shannon entropy of the URL
        features.append(self._compute_entropy(url))                   # 9: entropy

        # IP address check
        features.append(float(self._has_ip_address(hostname)))        # 10: has IP address

        # Subdomain features
        subdomains = hostname.split(".")
        num_subdomains = len(subdomains) - 2 if len(subdomains) > 2 else 0
        features.append(num_subdomains)                               # 11: subdomain depth
        max_subdomain_len = max(len(s) for s in subdomains) if subdomains else 0
        features.append(max_subdomain_len)                            # 12: max subdomain length

        # HTTPS check
        features.append(float(url.startswith("https://")))           # 13: has HTTPS

        # Suspicious keyword features
        has_susp = any(kw in url.lower() for kw in SUSPICIOUS_KEYWORDS)
        num_susp = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in url.lower())
        features.append(float(has_susp))                              # 14: has suspicious keyword
        features.append(num_susp)                                     # 15: count of suspicious keywords

        # Brand impersonation features
        has_brand = any(kw in url.lower() for kw in BRAND_KEYWORDS)
        is_brand_in_domain = any(kw in hostname.lower() for kw in BRAND_KEYWORDS)
        features.append(float(has_brand))                             # 16: has brand keyword
        features.append(float(is_brand_in_domain))                   # 17: brand keyword in domain

        # Suspicious TLD features
        has_susp_tld = any(hostname.lower().endswith(tld) for tld in SUSPICIOUS_TLDS)
        features.append(float(has_susp_tld))                          # 18: suspicious TLD

        # Other suspicious characters
        features.append(url.count("@"))                               # 19: @ symbols
        features.append(url.count("%"))                               # 20: percent symbols

        # Length ratios
        features.append(len(query))                                   # 21: query string length
        features.append(len(fragment))                                 # 22: fragment length

        # Ratio of digits to total characters
        digit_ratio = sum(c.isdigit() for c in url) / max(len(url), 1)
        features.append(digit_ratio)                                  # 23: digit ratio

        return np.array(features, dtype=np.float32)

    def _parse_url(self, url: str) -> Dict[str, str]:
        """Parse URL into components without using urllib (more robust)."""
        result = {}

        # Remove protocol
        if url.startswith("https://"):
            result["protocol"] = "https"
            url_no_proto = url[8:]
        elif url.startswith("http://"):
            result["protocol"] = "http"
            url_no_proto = url[7:]
        else:
            result["protocol"] = ""
            url_no_proto = url

        # Split hostname from path
        slash_idx = url_no_proto.find("/")
        if slash_idx >= 0:
            hostname = url_no_proto[:slash_idx]
            path_and_rest = url_no_proto[slash_idx:]
        else:
            hostname = url_no_proto
            path_and_rest = ""

        # Remove port from hostname
        if ":" in hostname:
            hostname = hostname.split(":")[0]

        result["hostname"] = hostname

        # Split path, query, fragment
        parts = path_and_rest
        if "#" in parts:
            path_part, fragment = parts.split("#", 1)
            result["fragment"] = fragment
        else:
            path_part = parts
            result["fragment"] = ""

        if "?" in path_part:
            path, query = path_part.split("?", 1)
            result["path"] = path
            result["query"] = query
        else:
            result["path"] = path_part
            result["query"] = ""

        return result

    def _compute_entropy(self, url: str) -> float:
        """Compute Shannon entropy of a URL string."""
        if not url:
            return 0.0

        char_counts = {}
        for c in url:
            char_counts[c] = char_counts.get(c, 0) + 1

        entropy = 0.0
        length = len(url)
        for count in char_counts.values():
            p = count / length
            if p > 0:
                entropy -= p * math.log2(p)

        return entropy

    def _has_ip_address(self, hostname: str) -> bool:
        """Check if hostname is an IP address."""
        ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
        return bool(re.match(ip_pattern, hostname))


class URLClassifierService:
    """
    URL Lexical Classification Service using XGBoost.

    Loads a pretrained XGBoost model if available; otherwise
    uses a heuristic rule-based scoring system.
    """

    # Heuristic rule weights (used when no XGBoost model is loaded)
    RULE_WEIGHTS = {
        "suspicious_keywords": 0.20,
        "brand_impersonation": 0.25,
        "url_length": 0.10,
        "entropy": 0.10,
        "suspicious_tld": 0.15,
        "ip_address": 0.10,
        "subdomain_depth": 0.10,
    }

    def __init__(self):
        self.model: Optional[object] = None
        self.feature_extractor = URLFeatureExtractor()
        self.model_loaded = False
        self._load_model()

    def _load_model(self) -> None:
        """Attempt to load pretrained XGBoost model."""
        model_path = Path(settings.url_classifier_model_path)

        if model_path.exists():
            try:
                import xgboost as xgb
                self.model = xgb.XGBClassifier()
                self.model.load_model(str(model_path))
                self.model_loaded = True
                logger.info(f"✅ Loaded URL classifier model from {model_path}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load URL classifier: {e}. Using heuristic mode.")
                self.model = None
                self.model_loaded = False
        else:
            logger.info(f"ℹ️ No pretrained URL classifier at {model_path}. Using heuristic mode.")

    def classify(self, url: str) -> Dict:
        """
        Classify a URL as phishing or legitimate.

        Args:
            url: The decoded URL string from a QR code.

        Returns:
            {
                "lexical_score": float (0–1, phishing probability),
                "is_phishing": bool,
                "features": dict of extracted feature names and values,
                "method": "xgboost" | "heuristic",
            }
        """
        features = self.feature_extractor.extract(url)

        if self.model_loaded:
            score = self._predict_xgboost(features)
            method = "xgboost"
        else:
            score = self._predict_heuristic(url, features)
            method = "heuristic"

        is_phishing = score >= 0.5

        return {
            "lexical_score": float(score),
            "is_phishing": is_phishing,
            "features": {
                "url_length": int(features[0]),
                "hostname_length": int(features[1]),
                "num_dots": int(features[4]),
                "num_hyphens": int(features[5]),
                "entropy": float(features[9]),
                "has_ip": bool(features[10]),
                "subdomain_depth": int(features[11]),
                "has_suspicious_kw": bool(features[14]),
                "num_suspicious_kw": int(features[15]),
                "has_brand_kw": bool(features[16]),
                "brand_in_domain": bool(features[17]),
                "has_suspicious_tld": bool(features[18]),
                "digit_ratio": float(features[23]),
            },
            "method": method,
        }

    def _predict_xgboost(self, features: np.ndarray) -> float:
        """Run XGBoost prediction. Returns phishing probability."""
        try:
            prob = self.model.predict_proba(features.reshape(1, -1))[0][1]
            return float(prob)
        except Exception as e:
            logger.warning(f"XGBoost prediction failed: {e}")
            return 0.5

    def _predict_heuristic(self, url: str, features: np.ndarray) -> float:
        """Rule-based heuristic scoring when no ML model is available."""
        score = 0.0

        url_lower = url.lower()

        # Suspicious keywords
        susp_count = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in url_lower)
        score += self.RULE_WEIGHTS["suspicious_keywords"] * min(1.0, susp_count / 3.0)

        # Brand impersonation
        brand_in_domain = any(kw in url_lower.split("/")[2] if "/" in url_lower[:8] else "" for kw in BRAND_KEYWORDS)
        score += self.RULE_WEIGHTS["brand_impersonation"] * float(brand_in_domain)

        # URL length (longer URLs are more suspicious)
        url_len = len(url)
        score += self.RULE_WEIGHTS["url_length"] * min(1.0, url_len / 150.0)

        # Entropy (higher entropy = more random = more suspicious)
        entropy = features[9]
        score += self.RULE_WEIGHTS["entropy"] * min(1.0, entropy / 5.0)

        # Suspicious TLD
        hostname = ""
        if url.startswith("http"):
            parts = url.split("/")[2] if "/" in url[8:] else url.split("/")[2:]
            hostname = parts if isinstance(parts, str) else ""
        has_susp_tld = any(hostname.lower().endswith(tld) for tld in SUSPICIOUS_TLDS)
        score += self.RULE_WEIGHTS["suspicious_tld"] * float(has_susp_tld)

        # IP address
        score += self.RULE_WEIGHTS["ip_address"] * float(features[10])

        # Subdomain depth
        subdomain_depth = features[11]
        score += self.RULE_WEIGHTS["subdomain_depth"] * min(1.0, subdomain_depth / 4.0)

        return min(1.0, score)
