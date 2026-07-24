/**
 * QuishGuard — TypeScript Type Definitions
 */

// === Scan Types ===

export interface AIImageAnalysis {
  verdict: "real" | "fake" | "uncertain";
  confidence: number;
  details: {
    frequency_score: number;
    noise_score: number;
    artifact_heatmap_url: string;
  };
}

export interface QRAnalysis {
  qr_detected: boolean;
  decoded_url: string | null;
  quishing_verdict: "safe" | "suspicious" | "malicious" | null;
  quishing_confidence: number | null;
  details: {
    url_lexical_score: number | null;
    visual_tampering_score: number | null;
    threat_intel: {
      safe_browsing: string | null;
      urlscan: string | null;
      reported: boolean | null;
    } | null;
  };
}

export interface Scan {
  id: string;
  status: "completed" | "processing" | "failed";
  image_hash: string;
  ai_image_analysis: AIImageAnalysis;
  qr_analysis: QRAnalysis;
  created_at: string;
}

export interface ScanHistoryResponse {
  items: Scan[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface ScanStats {
  total_scans: number;
  ai_fake_count: number;
  ai_real_count: number;
  ai_uncertain_count: number;
  qr_detected_count: number;
  quish_malicious_count: number;
  quish_suspicious_count: number;
  quish_safe_count: number;
  avg_ai_confidence: number;
  scans_last_7_days: number;
}

// === API Key Types ===

export interface ApiKey {
  id: string;
  name: string;
  key?: string; // Only present on creation response
  rate_limit: number;
  is_active: boolean;
  created_at: string;
  expires_at: string | null;
}

// === Upload Types ===

export interface ScanOptions {
  ai_check: boolean;
  qr_check: boolean;
}

export interface UploadError {
  detail: string;
}
