"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress, ProgressIndicator } from "@/components/ui/progress";
import { formatConfidence, verdictColor } from "@/lib/utils";
import type { AIImageAnalysis } from "@/types";

interface AIImageReportProps {
  analysis: AIImageAnalysis;
}

export function AIImageReport({ analysis }: AIImageReportProps) {
  const verdictVariant = analysis.verdict === "fake" ? "fake"
    : analysis.verdict === "real" ? "real" : "uncertain";

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <span>🖼️ AI-Image Detection</span>
          <Badge variant={verdictVariant} className="text-sm uppercase">
            {analysis.verdict}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Confidence Score */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-muted-foreground">Confidence</span>
            <span className="text-sm font-semibold">{formatConfidence(analysis.confidence)}</span>
          </div>
          <Progress>
            <ProgressIndicator value={analysis.confidence * 100} />
          </Progress>
        </div>

        {/* Frequency Score */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-muted-foreground">Frequency Anomaly</span>
            <span className="text-sm font-semibold">{formatConfidence(analysis.details.frequency_score)}</span>
          </div>
          <Progress>
            <ProgressIndicator value={analysis.details.frequency_score * 100} />
          </Progress>
        </div>

        {/* Noise Score */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-muted-foreground">Noise Inconsistency</span>
            <span className="text-sm font-semibold">{formatConfidence(analysis.details.noise_score)}</span>
          </div>
          <Progress>
            <ProgressIndicator value={analysis.details.noise_score * 100} />
          </Progress>
        </div>

        {/* Heatmap link */}
        {analysis.details.artifact_heatmap_url && (
          <div className="text-sm text-muted-foreground pt-2">
            📊 <a href={analysis.details.artifact_heatmap_url} className="text-primary hover:underline">View Artifact Heatmap</a>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
