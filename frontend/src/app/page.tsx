"use client";

import { useState } from "react";
import { ImageUploader } from "@/components/ImageUploader";
import { ScanResultCard } from "@/components/ScanResultCard";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import type { Scan } from "@/types";

export default function ScanPage() {
  const [scanResult, setScanResult] = useState<Scan | null>(null);
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 container px-4 md:px-8 py-8">
        <div className="max-w-3xl mx-auto space-y-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold tracking-tight mb-2">🛡️ QuishGuard Scanner</h1>
            <p className="text-muted-foreground">
              Upload an image to detect AI-generated content and QR phishing attacks
            </p>
          </div>

          <ImageUploader
            onScanComplete={(result) => {
              setScanResult(result);
              setError(null);
            }}
            onScanError={(err) => {
              setError(err);
              setScanResult(null);
            }}
          />

          {error && (
            <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive text-sm">
              ❌ {error}
            </div>
          )}

          {scanResult && <ScanResultCard scan={scanResult} />}
        </div>
      </main>
      <Footer />
    </div>
  );
}
