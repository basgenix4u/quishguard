import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "QuishGuard — AI-Image & QR Phishing Detector",
  description: "Multimodal Deep Learning Framework for Detecting AI-Generated Images and QR Phishing (Quishing)",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
