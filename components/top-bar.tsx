"use client";

import { cn } from "@/lib/utils";
import type { ConnectionStatus } from "@/types/preset";
import { Activity, Radio, Server } from "lucide-react";

interface StatusIndicatorProps {
  label: string;
  status: ConnectionStatus;
  icon: React.ReactNode;
}

function StatusIndicator({ label, status, icon }: StatusIndicatorProps) {
  const statusColors: Record<ConnectionStatus, string> = {
    connected: "bg-success",
    connecting: "bg-warning",
    disconnected: "bg-destructive",
  };

  const statusLabels: Record<ConnectionStatus, string> = {
    connected: "Connected",
    connecting: "Connecting...",
    disconnected: "Offline",
  };

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-secondary/50 border border-border">
      <span className="text-muted-foreground">{icon}</span>
      <span className="text-xs text-muted-foreground">{label}</span>
      <div className="flex items-center gap-1.5">
        <div
          className={cn(
            "w-2 h-2 rounded-full",
            statusColors[status],
            status === "connecting" && "animate-pulse"
          )}
        />
        <span
          className={cn(
            "text-xs font-medium",
            status === "connected" && "text-success",
            status === "connecting" && "text-warning",
            status === "disconnected" && "text-destructive"
          )}
        >
          {statusLabels[status]}
        </span>
      </div>
    </div>
  );
}

interface TopBarProps {
  apiStatus: ConnectionStatus;
  bridgeStatus: ConnectionStatus;
  engineStatus: ConnectionStatus;
}

export function TopBar({ apiStatus, bridgeStatus, engineStatus }: TopBarProps) {
  return (
    <header className="h-14 px-4 flex items-center justify-between border-b border-border bg-panel-header">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-md bg-primary/10 flex items-center justify-center">
            <Activity className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h1 className="text-sm font-semibold text-foreground leading-tight">
              AI Preset Engine
            </h1>
            <p className="text-[10px] text-muted-foreground leading-tight">
              Sound Design Control Panel
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <StatusIndicator
          label="API"
          status={apiStatus}
          icon={<Server className="w-3.5 h-3.5" />}
        />
        <StatusIndicator
          label="Bridge"
          status={bridgeStatus}
          icon={<Radio className="w-3.5 h-3.5" />}
        />
        <StatusIndicator
          label="Engine"
          status={engineStatus}
          icon={<Activity className="w-3.5 h-3.5" />}
        />
      </div>
    </header>
  );
}
