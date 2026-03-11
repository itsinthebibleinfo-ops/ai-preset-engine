"use client";

import { cn } from "@/lib/utils";
import type { LogEntry } from "@/types/preset";
import {
  AlertTriangle,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  Info,
  Terminal,
  XCircle,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";

const logTypeConfig = {
  info: {
    icon: <Info className="w-3.5 h-3.5" />,
    color: "text-info",
    bgColor: "bg-info/10",
  },
  success: {
    icon: <CheckCircle className="w-3.5 h-3.5" />,
    color: "text-success",
    bgColor: "bg-success/10",
  },
  warning: {
    icon: <AlertTriangle className="w-3.5 h-3.5" />,
    color: "text-warning",
    bgColor: "bg-warning/10",
  },
  error: {
    icon: <XCircle className="w-3.5 h-3.5" />,
    color: "text-destructive",
    bgColor: "bg-destructive/10",
  },
};

function formatTimestamp(date: Date): string {
  return date.toLocaleTimeString("en-US", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

interface LogConsoleProps {
  logs: LogEntry[];
  defaultExpanded?: boolean;
}

export function LogConsole({ logs, defaultExpanded = true }: LogConsoleProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (scrollRef.current && isExpanded) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, isExpanded]);

  return (
    <div
      className={cn(
        "flex flex-col bg-panel rounded-lg border border-border overflow-hidden transition-all duration-200",
        isExpanded ? "h-48" : "h-10"
      )}
    >
      {/* Console Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="h-10 px-4 flex items-center justify-between border-b border-border bg-panel-header hover:bg-panel-header/80 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium text-foreground">
            Console
          </span>
          {logs.length > 0 && (
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-secondary text-muted-foreground">
              {logs.length}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {!isExpanded && logs.length > 0 && (
            <span className="text-xs text-muted-foreground truncate max-w-[300px]">
              {logs[logs.length - 1]?.message}
            </span>
          )}
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          ) : (
            <ChevronUp className="w-4 h-4 text-muted-foreground" />
          )}
        </div>
      </button>

      {/* Console Content */}
      {isExpanded && (
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-2 font-mono text-xs space-y-1"
        >
          {logs.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <span className="text-muted-foreground/50">
                Console output will appear here
              </span>
            </div>
          ) : (
            logs.map((log) => {
              const config = logTypeConfig[log.type];
              return (
                <div
                  key={log.id}
                  className={cn(
                    "flex items-start gap-2 px-2 py-1 rounded",
                    config.bgColor
                  )}
                >
                  <span className="text-muted-foreground shrink-0">
                    [{formatTimestamp(log.timestamp)}]
                  </span>
                  <span className={cn("shrink-0", config.color)}>
                    {config.icon}
                  </span>
                  <span className={cn("break-all", config.color)}>
                    {log.message}
                  </span>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
