"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Shield, AlertTriangle, Image, QrCode, BarChart3 } from "lucide-react";
import { formatConfidence } from "@/lib/utils";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
} from "recharts";
import type { ScanStats } from "@/types";

interface StatsOverviewProps {
  stats: ScanStats;
}

const PIE_COLORS = ["#3b82f6", "#ef4444", "#f59e0b", "#22c55e", "#a855f7", "#f97316"];
const QUI_COLORS = ["#22c55e", "#f59e0b", "#ef4444"];

export function StatsOverview({ stats }: StatsOverviewProps) {
  const aiData = [
    { name: "Real", value: stats.ai_real_count },
    { name: "Fake", value: stats.ai_fake_count },
    { name: "Uncertain", value: stats.ai_uncertain_count },
  ];

  const quishData = [
    { name: "Safe", value: stats.quish_safe_count },
    { name: "Suspicious", value: stats.quish_suspicious_count },
    { name: "Malicious", value: stats.quish_malicious_count },
  ];

  const barData = [
    { name: "Total Scans", value: stats.total_scans },
    { name: "AI Fake", value: stats.ai_fake_count },
    { name: "QR Detected", value: stats.qr_detected_count },
    { name: "Quishing", value: stats.quish_malicious_count + stats.quish_suspicious_count },
  ];

  return (
    <div className="space-y-4">
      {/* Quick Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <Image className="h-6 w-6 text-blue-500 mx-auto mb-2" />
            <p className="text-2xl font-bold">{stats.total_scans}</p>
            <p className="text-xs text-muted-foreground">Total Scans</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <AlertTriangle className="h-6 w-6 text-red-500 mx-auto mb-2" />
            <p className="text-2xl font-bold">{stats.ai_fake_count}</p>
            <p className="text-xs text-muted-foreground">AI-Generated</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <QrCode className="h-6 w-6 text-orange-500 mx-auto mb-2" />
            <p className="text-2xl font-bold">{stats.qr_detected_count}</p>
            <p className="text-xs text-muted-foreground">QR Codes Found</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <Shield className="h-6 w-6 text-green-500 mx-auto mb-2" />
            <p className="text-2xl font-bold">{stats.quish_malicious_count + stats.quish_suspicious_count}</p>
            <p className="text-xs text-muted-foreground">Quishing Threats</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Bar Chart */}
        <Card className="md:col-span-1">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Scan Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={barData}>
                <XAxis dataKey="name" fontSize={10} />
                <YAxis fontSize={10} />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* AI Verdict Pie */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">AI Verdict Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {stats.total_scans > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={aiData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} dataKey="value" label={({ name, value }) => `${name}: ${value}`} fontSize={10}>
                    {aiData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-muted-foreground py-8">No data yet</p>
            )}
          </CardContent>
        </Card>

        {/* Quishing Verdict Pie */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Quishing Verdict Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {stats.qr_detected_count > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={quishData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} dataKey="value" label={({ name, value }) => `${name}: ${value}`} fontSize={10}>
                    {quishData.map((_, i) => <Cell key={i} fill={QUI_COLORS[i]} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-muted-foreground py-8">No QR scans yet</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Avg confidence + recent */}
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Avg AI Confidence</p>
            <p className="text-lg font-bold">{formatConfidence(stats.avg_ai_confidence)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Scans (Last 7 Days)</p>
            <p className="text-lg font-bold">{stats.scans_last_7_days}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
