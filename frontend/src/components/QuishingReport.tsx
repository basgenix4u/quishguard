"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress, ProgressIndicator } from "@/components/ui/progress";
import { formatConfidence } from "@/lib/utils";
import { ExternalLink, AlertTriangle, CheckCircle } from "lucide-react";
import type { QRAnalysis } from "@/types";

interface QuishingReportProps {
  analysis: QRAnalysis;
}

export function QuishingReport({ analysis }: QuishingReportProps) {
  if (!analysis.qr_detected) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle>🛡️ QR / Quishing Detection</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">No QR code detected in this image.</p>
        </CardContent>
      </Card>
    );
  }

  const verdictVariant = analysis.quishing_verdict === "malicious" ? "malicious"
    : analysis.quishing_verdict === "suspicious" ? "suspicious" : "safe";

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <span>🛡️ QR / Quishing Detection</span>
          <Badge variant={verdictVariant} className="text-sm uppercase">
            {analysis.quishing_verdict || "unknown"}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Decoded URL */}
        {analysis.decoded_url && (
          <div className="rounded-lg bg-muted p-3">
            <p className="text-xs text-muted-foreground mb-1">Decoded URL:</p>
            <a
              href={analysis.decoded_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-primary hover:underline break-all"
            >
              {analysis.decoded_url}
              <ExternalLink className="inline h-3 w-3 ml-1" />
            </a>
          </div>
        )}

        {/* Confidence */}
        {analysis.quishing_confidence !== null && (
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-muted-foreground">Risk Confidence</span>
              <span className="text-sm font-semibold">{formatConfidence(analysis.quishing_confidence)}</span>
            </div>
            <Progress>
              <ProgressIndicator value={analysis.quishing_confidence * 100} />
            </Progress>
          </div>
        )}

        {/* URL Lexical Score */}
        {analysis.details.url_lexical_score !== null && (
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-muted-foreground">URL Lexical Risk</span>
              <span className="text-sm font-semibold">{formatConfidence(analysis.details.url_lexical_score)}</span>
            </div>
            <Progress>
              <ProgressIndicator value={analysis.details.url_lexical_score * 100} />
            </Progress>
          </div>
        )}

        {/* Visual Tampering */}
        {analysis.details.visual_tampering_score !== null && (
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-muted-foreground">Visual Tampering Risk</span>
              <span className="text-sm font-semibold">{formatConfidence(analysis.details.visual_tampering_score)}</span>
            </div>
            <Progress>
              <ProgressIndicator value={analysis.details.visual_tampering_score * 100} />
            </Progress>
          </div>
        )}

        {/* Threat Intel */}
        {analysis.details.threat_intel && (
          <div className="rounded-lg border p-3 space-y-2">
            <p className="text-xs font-semibold text-muted-foreground">Threat Intelligence</p>
            {analysis.details.threat_intel.safe_browsing && (
              <div className="flex items-center gap-2">
                {analysis.details.threat_intel.safe_browsing === "MALICIOUS" ? (
                  <AlertTriangle className="h-4 w-4 text-malicious" />
                ) : (
                  <CheckCircle className="h-4 w-4 text-safe" />
                )}
                <span className="text-sm">
                  Google Safe Browsing: <strong>{analysis.details.threat_intel.safe_browsing}</strong>
                </span>
              </div>
            )}
            {analysis.details.threat_intel.urlscan && (
              <div className="flex items-center gap-2">
                {analysis.details.threat_intel.urlscan === "MALICIOUS" ? (
                  <AlertTriangle className="h-4 w-4 text-malicious" />
                ) : (
                  <CheckCircle className="h-4 w-4 text-safe" />
                )}
                <span className="text-sm">
                  urlscan.io: <strong>{analysis.details.threat_intel.urlscan}</strong>
                </span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
