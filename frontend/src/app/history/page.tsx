"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { StatsOverview } from "@/components/StatsOverview";
import { ScanHistoryTable } from "@/components/ScanHistoryTable";
import { Loader2 } from "lucide-react";
import type { Scan, ScanHistoryResponse, ScanStats } from "@/types";

export default function HistoryPage() {
  const [history, setHistory] = useState<ScanHistoryResponse | null>(null);
  const [stats, setStats] = useState<ScanStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

  const fetchData = async () => {
    try {
      const [histRes, statsRes] = await Promise.all([
        fetch(`${apiUrl}/scans/history?page=${page}&per_page=20`),
        fetch(`${apiUrl}/scans/stats`),
      ]);

      if (histRes.ok) setHistory(await histRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
    } catch (err) {
      console.error("Failed to fetch data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [page]);

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 container px-4 md:px-8 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          <h1 className="text-2xl font-bold">📊 Scan History & Statistics</h1>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : (
            <>
              {stats && <StatsOverview stats={stats} />}
              {history && (
                <ScanHistoryTable
                  scans={history.items}
                  total={history.total}
                  page={history.page}
                  pages={history.pages}
                  onPageChange={setPage}
                />
              )}
            </>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}
