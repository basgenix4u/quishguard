"use client";

import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const endpoints = [
  { method: "POST", path: "/scans", desc: "Submit image for unified scan (multipart form)", response: "201 Created → ScanResponse" },
  { method: "GET", path: "/scans/{id}", desc: "Retrieve scan result by ID", response: "200 OK → ScanResponse" },
  { method: "GET", path: "/scans/{id}/heatmap", desc: "Get artifact heatmap PNG image", response: "200 OK → image/png" },
  { method: "GET", path: "/scans/history", desc: "Paginated scan history with filters", response: "200 OK → ScanHistoryResponse" },
  { method: "GET", path: "/scans/stats", desc: "Dashboard statistics", response: "200 OK → ScanStats" },
  { method: "POST", path: "/api-keys", desc: "Create API key", response: "201 Created → ApiKeyResponse" },
  { method: "GET", path: "/api-keys", desc: "List API keys (masked)", response: "200 OK → List[ApiKeyListResponse]" },
  { method: "GET", path: "/health", desc: "Health check", response: "200 OK → { status, version }" },
];

const methodColors: Record<string, string> = {
  GET: "bg-green-100 text-green-700",
  POST: "bg-blue-100 text-blue-700",
};

export default function ApiDocsPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 container px-4 md:px-8 py-8">
        <div className="max-w-3xl mx-auto space-y-6">
          <h1 className="text-2xl font-bold">📖 API Documentation</h1>
          <p className="text-muted-foreground">
            QuishGuard REST API — Base URL: <code className="text-primary font-mono">http://localhost:8000/api/v1</code>
          </p>

          <Card>
            <CardHeader>
              <CardTitle>Authentication</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <p>Include your API key in the <code className="bg-muted px-1 rounded">X-API-Key</code> header:</p>
              <pre className="bg-muted p-3 rounded-lg text-xs font-mono overflow-x-auto">
curl -H "X-API-Key: qg_live_your_key_here" http://localhost:8000/api/v1/scans/history
              </pre>
              <p className="text-muted-foreground mt-2">See the full interactive docs at <code className="text-primary font-mono">/docs</code> (Swagger UI)</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Endpoints</CardTitle>
            </CardHeader>
            <CardContent className="text-sm">
              <table className="w-full">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    <th className="py-2 text-left">Method</th>
                    <th className="py-2 text-left">Path</th>
                    <th className="py-2 text-left">Description</th>
                    <th className="py-2 text-left">Response</th>
                  </tr>
                </thead>
                <tbody>
                  {endpoints.map((ep) => (
                    <tr key={`${ep.method}-${ep.path}`} className="border-b">
                      <td className="py-2">
                        <span className={`px-2 py-0.5 rounded text-xs font-bold ${methodColors[ep.method] || ""}`}>
                          {ep.method}
                        </span>
                      </td>
                      <td className="py-2 font-mono text-xs">{ep.path}</td>
                      <td className="py-2">{ep.desc}</td>
                      <td className="py-2 font-mono text-xs">{ep.response}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Scan Response Example</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted p-4 rounded-lg text-xs font-mono overflow-x-auto">
{JSON.stringify({
  id: "a1b2c3d4-...",
  status: "completed",
  image_hash: "sha256:abc123...",
  ai_image_analysis: {
    verdict: "fake",
    confidence: 0.92,
    details: {
      frequency_score: 0.88,
      noise_score: 0.95,
      artifact_heatmap_url: "/api/v1/scans/{id}/heatmap"
    }
  },
  qr_analysis: {
    qr_detected: true,
    decoded_url: "https://evil-phish.com/login",
    quishing_verdict: "malicious",
    quishing_confidence: 0.97,
    details: {
      url_lexical_score: 0.91,
      visual_tampering_score: 0.72,
      threat_intel: {
        safe_browsing: "MALICIOUS",
        urlscan: "MALICIOUS",
        reported: true
      }
    }
  },
  created_at: "2026-07-24T10:30:00Z"
}, null, 2)}
              </pre>
            </CardContent>
          </Card>
        </div>
      </main>
      <Footer />
    </div>
  );
}
