import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Format a confidence score (0.0–1.0) as a percentage string */
export function formatConfidence(score: number): string {
  return `${Math.round(score * 100)}%`;
}

/** Format an ISO date string for display */
export function formatDate(isoDate: string): string {
  return new Date(isoDate).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Get verdict badge color class */
export function verdictColor(verdict: string): string {
  switch (verdict) {
    case "real":
    case "safe":
      return "text-safe bg-safe/10 border-safe";
    case "fake":
    case "malicious":
      return "text-malicious bg-malicious/10 border-malicious";
    case "uncertain":
    case "suspicious":
      return "text-suspicious bg-suspicious/10 border-suspicious";
    default:
      return "text-muted-foreground bg-muted border-border";
  }
}
