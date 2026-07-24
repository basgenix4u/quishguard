"use client";

import Link from "next/link";
import { Shield, History, BarChart3, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "Scan", icon: Shield },
  { href: "/history", label: "History", icon: History },
  { href: "/api-docs", label: "API Docs", icon: FileText },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center px-4 md:px-8">
        <Link href="/" className="flex items-center space-x-2 mr-6">
          <Shield className="h-6 w-6 text-primary" />
          <span className="font-bold text-lg">QuishGuard</span>
        </Link>
        <nav className="flex items-center space-x-6 text-sm font-medium">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "transition-colors hover:text-primary flex items-center gap-1.5",
                pathname === item.href ? "text-primary" : "text-muted-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
