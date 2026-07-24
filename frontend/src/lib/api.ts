/**
 * QuishGuard — API Client
 */

import { Scan, ScanHistoryResponse, ScanStats, ScanOptions } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `API Error: ${response.status}`);
    }

    return response.json();
  }

  /** Submit image for unified scan */
  async submitScan(
    file: File,
    scanOptions: ScanOptions = { ai_check: true, qr_check: true }
  ): Promise<Scan> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("scan_options", JSON.stringify(scanOptions));

    return this.request<Scan>("/scans", {
      method: "POST",
      body: formData,
    });
  }

  /** Retrieve scan result by ID */
  async getScan(scanId: string): Promise<Scan> {
    return this.request<Scan>(`/scans/${scanId}`);
  }

  /** Get paginated scan history */
  async getScanHistory(params: {
    page?: number;
    per_page?: number;
    ai_verdict?: string;
    quish_verdict?: string;
    date_from?: string;
    date_to?: string;
  } = {}): Promise<ScanHistoryResponse> {
    const query = new URLSearchParams();
    if (params.page) query.set("page", params.page.toString());
    if (params.per_page) query.set("per_page", params.per_page.toString());
    if (params.ai_verdict) query.set("ai_verdict", params.ai_verdict);
    if (params.quish_verdict) query.set("quish_verdict", params.quish_verdict);
    if (params.date_from) query.set("date_from", params.date_from);
    if (params.date_to) query.set("date_to", params.date_to);

    return this.request<ScanHistoryResponse>(`/scans/history?${query.toString()}`);
  }

  /** Get dashboard statistics */
  async getScanStats(): Promise<ScanStats> {
    return this.request<ScanStats>("/scans/stats");
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
export default apiClient;
