export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full text-center">
        <h1 className="text-4xl font-bold tracking-tight text-primary mb-4">
          🛡️ QuishGuard
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          Multimodal Deep Learning Framework for Detecting AI-Generated Images &amp; QR Phishing
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto">
          <div className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
            <h2 className="text-lg font-semibold mb-2">🔍 AI-Image Detection</h2>
            <p className="text-sm text-muted-foreground">
              Detect AI-generated/synthetic images using EfficientNet-B4, frequency analysis, and noise inconsistency mapping.
            </p>
          </div>
          <div className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
            <h2 className="text-lg font-semibold mb-2">🛡️ Quishing Detection</h2>
            <p className="text-sm text-muted-foreground">
              Decode QR codes and analyze embedded URLs for phishing using hybrid threat intelligence and visual tampering detection.
            </p>
          </div>
        </div>
        <div className="mt-8 text-sm text-muted-foreground">
          Frontend smoke test — ✅ Next.js operational
        </div>
      </div>
    </main>
  );
}
