"use client";

import React, { useCallback, useState, useRef } from "react";
import { Upload, X, Loader2, Shield, FileImage } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface ImageUploaderProps {
  onScanComplete: (result: any) => void;
  onScanError: (error: string) => void;
}

export function ImageUploader({ onScanComplete, onScanError }: ImageUploaderProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [aiCheck, setAiCheck] = useState(true);
  const [qrCheck, setQrCheck] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((file: File) => {
    // Validate file type
    const allowed = ["png", "jpg", "jpeg", "webp"];
    const ext = file.name.split(".").pop()?.toLowerCase() || "";
    if (!allowed.includes(ext)) {
      onScanError(`Invalid file type "${ext}". Accepted: PNG, JPG, WEBP`);
      return;
    }
    // Validate size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      onScanError("File exceeds 10MB limit");
      return;
    }
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  }, [onScanError]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, [handleFile]);

  const handlePaste = useCallback((e: React.ClipboardEvent) => {
    if (e.clipboardData.files && e.clipboardData.files[0]) {
      handleFile(e.clipboardData.files[0]);
    }
  }, [handleFile]);

  const clearFile = useCallback(() => {
    setSelectedFile(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
  }, [previewUrl]);

  const submitScan = useCallback(async () => {
    if (!selectedFile) return;
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("scan_options", JSON.stringify({ ai_check: aiCheck, qr_check: qrCheck }));

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/scans`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: response.statusText }));
        onScanError(err.detail || `Error: ${response.status}`);
        return;
      }

      const result = await response.json();
      onScanComplete(result);
    } catch (err: any) {
      onScanError(err.message || "Network error — check that the backend is running");
    } finally {
      setUploading(false);
    }
  }, [selectedFile, aiCheck, qrCheck, onScanComplete, onScanError]);

  return (
    <Card
      className={cn("transition-all", dragActive && "ring-2 ring-primary")}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onPaste={handlePaste}
    >
      <CardContent className="p-6">
        {previewUrl ? (
          <div className="space-y-4">
            <div className="relative rounded-lg overflow-hidden border bg-muted">
              <img src={previewUrl} alt="Preview" className="w-full h-auto max-h-64 object-contain" />
              <button
                onClick={clearFile}
                className="absolute top-2 right-2 bg-black/70 text-white rounded-full p-1 hover:bg-black/90 transition"
                aria-label="Remove image"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <p className="text-sm text-muted-foreground text-center">{selectedFile?.name} ({((selectedFile?.size || 0) / 1024).toFixed(1)} KB)</p>

            {/* Scan Options */}
            <div className="flex gap-4 justify-center">
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input type="checkbox" checked={aiCheck} onChange={(e) => setAiCheck(e.target.checked)} className="rounded" />
                🖼️ AI-Image Detection
              </label>
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input type="checkbox" checked={qrCheck} onChange={(e) => setQrCheck(e.target.checked)} className="rounded" />
                🛡️ Quishing Detection
              </label>
            </div>

            <Button onClick={submitScan} disabled={uploading} className="w-full" size="lg">
              {uploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Shield className="mr-2 h-4 w-4" />
                  Scan Image
                </>
              )}
            </Button>
          </div>
        ) : (
          <div
            className="flex flex-col items-center justify-center py-12 cursor-pointer"
            onClick={() => inputRef.current?.click()}
          >
            <div className="rounded-full bg-muted p-6 mb-4">
              <Upload className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="font-semibold text-lg mb-1">Upload Image for Analysis</h3>
            <p className="text-muted-foreground text-sm mb-2">
              Drag & drop, paste from clipboard, or click to browse
            </p>
            <p className="text-xs text-muted-foreground">
              Supports PNG, JPG, WEBP • Max 10MB
            </p>
            <input
              ref={inputRef}
              type="file"
              accept="png,jpg,jpeg,webp"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
              className="hidden"
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
