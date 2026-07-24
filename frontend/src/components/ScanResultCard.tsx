"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate, formatConfidence } from "@/lib/utils";
import { AIImageReport } from "@/components/AIImageReport";
import { QuishingReport } from "@/components/QuishingReport";
import type { Scan } from "@/types";

interface ScanResultCardProps {
  scan: Scan;
}

export function ScanResultCard({ scan }: ScanResultCardProps) {
  return (
    <div className="space-y-4">
      {/* Scan Summary Header */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between">
            <span>Scan Report</span>
            <div className="flex gap-2">
              <Badge variant="outline">ID: {scan.id.slice(0, 8)}...</Badge>
              <Badge variant={scan.status === "completed" ? "safe" : "suspicious"}>
                {scan.status}
              </Badge>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Scanned on {formatDate(scan.created_at)} • Hash: {scan.image_hash.slice(0, 16)}...
          </p>
        </CardContent>
      </Card>

      {/* AI-Image Analysis */}
      <AIImageReport analysis={scan.ai_image_analysis} />

      {/* QR / Quishing Analysis */}
      <QuishingReport analysis={scan.qr_analysis} />
    </div>
  );
}
