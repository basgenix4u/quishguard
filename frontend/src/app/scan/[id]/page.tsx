"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ScanResultCard } from "@/components/ScanResultCard";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import Link from "next/link";
import type { Scan } from "@/types";

export default function ScanDetailPage() {
  const params = useParams();
  const scanId = params?.id as string;
  const [scan, setScan] = useState<Scan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!scanId) return;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    fetch(`${apiUrl}/scans/${scanId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Scan not found (${res.status})`);
        return res.json();
      })
      .then((data) => { setScan(data); setError(null); })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [scanId]);

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 container px-4 md:px-8 py-8">
        <div className="max-w-3xl mx-auto">
          <Link href="/">
            <Button variant="ghost" size="sm" className="mb-4">← Back to Scanner</Button>
          </Link>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
              <span className="ml-2 text-muted-foreground">Loading scan...</span>
            </div>
          ) : error ? (
            <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive text-sm">
              ❌ {error}
            </div>
          ) : scan ? (
            <ScanResultCard scan={scan} />
          ) : null}
        </div>
      </main>
      <Footer />
    </div>
  );
}
