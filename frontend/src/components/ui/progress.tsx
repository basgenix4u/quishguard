import * as React from "react";
import { cn } from "@/lib/utils";

const Progress = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("relative h-4 w-full overflow-hidden rounded-full bg-secondary", className)} {...props} />
  )
);
Progress.displayName = "Progress";

const ProgressIndicator = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement> & { value?: number }>(
  ({ className, value = 0, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("h-full w-full flex-1 bg-primary transition-all", className)}
      style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
      {...props}
    />
  )
);
ProgressIndicator.displayName = "ProgressIndicator";

export { Progress, ProgressIndicator };
