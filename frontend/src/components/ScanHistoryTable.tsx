"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatDate, formatConfidence, verdictColor } from "@/lib/utils";
import Link from "next/link";
import type { Scan } from "@/types";

interface ScanHistoryTableProps {
  scans: Scan[];
  total: number;
  page: number;
  pages: number;
  onPageChange: (page: number) => void;
}

export function ScanHistoryTable({ scans, total, page, pages, onPageChange }: ScanHistoryTableProps) {
  if (scans.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-muted-foreground">No scans found. Upload an image to start scanning!</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle>Scan History ({total} total)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-muted-foreground">
                <th className="py-3 px-2 text-left">Date</th>
                <th className="py-3 px-2 text-left">AI Verdict</th>
                <th className="py-3 px-2 text-left">Confidence</th>
                <th className="py-3 px-2 text-left">QR Detected</th>
                <th className="py-3 px-2 text-left">Quish Verdict</th>
                <th className="py-3 px-2 text-right">View</th>
              </tr>
            </thead>
            <tbody>
              {scans.map((scan) => (
                <tr key={scan.id} className="border-b hover:bg-muted/50 transition">
                  <td className="py-3 px-2">{formatDate(scan.created_at)}</td>
                  <td className="py-3 px-2">
                    <Badge variant={scan.ai_image_analysis.verdict === "fake" ? "fake" : scan.ai_image_analysis.verdict === "real" ? "real" : "uncertain"}>
                      {scan.ai_image_analysis.verdict}
                    </Badge>
                  </td>
                  <td className="py-3 px-2">{formatConfidence(scan.ai_image_analysis.confidence)}</td>
                  <td className="py-3 px-2">{scan.qr_analysis.qr_detected ? "✅ Yes" : "❌ No"}</td>
                  <td className="py-3 px-2">
                    {scan.qr_analysis.quishing_verdict ? (
                      <Badge variant={scan.qr_analysis.quishing_verdict === "malicious" ? "malicious" : scan.qr_analysis.quishing_verdict === "suspicious" ? "suspicious" : "safe"}>
                        {scan.qr_analysis.quishing_verdict}
                      </Badge>
                    ) : "—"}
                  </td>
                  <td className="py-3 px-2 text-right">
                    <Link href={`/scan/${scan.id}`}>
                      <Button variant="outline" size="sm">View</Button>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between pt-4">
          <p className="text-sm text-muted-foreground">
            Page {page} of {pages}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= pages}
              onClick={() => onPageChange(page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
