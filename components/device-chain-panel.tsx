"use client";

import { cn } from "@/lib/utils";
import type { DeviceChainItem, DeviceType } from "@/types/preset";
import { ChevronRight, Disc3, Sliders, Zap } from "lucide-react";

const deviceTypeConfig: Record<
  DeviceType,
  { icon: React.ReactNode; color: string; bgColor: string }
> = {
  instrument: {
    icon: <Disc3 className="w-4 h-4" />,
    color: "text-primary",
    bgColor: "bg-primary/10 border-primary/30",
  },
  effect: {
    icon: <Sliders className="w-4 h-4" />,
    color: "text-info",
    bgColor: "bg-info/10 border-info/30",
  },
  utility: {
    icon: <Zap className="w-4 h-4" />,
    color: "text-muted-foreground",
    bgColor: "bg-secondary border-border",
  },
};

function getDeviceType(name: string): DeviceType {
  const lowerName = name.toLowerCase();
  const instruments = [
    "wavetable",
    "operator",
    "analog",
    "drift",
    "simpler",
    "sampler",
    "bass",
    "keys",
    "pad",
    "lead",
    "synth",
  ];
  const effects = [
    "reverb",
    "delay",
    "chorus",
    "filter",
    "eq",
    "compressor",
    "saturator",
    "phaser",
    "flanger",
    "distortion",
    "overdrive",
  ];

  if (instruments.some((i) => lowerName.includes(i))) return "instrument";
  if (effects.some((e) => lowerName.includes(e))) return "effect";
  return "utility";
}

interface DeviceBlockProps {
  device: DeviceChainItem | string;
  isLast?: boolean;
}

function DeviceBlock({ device, isLast }: DeviceBlockProps) {
  const name = typeof device === "string" ? device : device.name;
  const type = typeof device === "string" ? getDeviceType(device) : device.type;
  const params =
    typeof device === "string" ? undefined : device.parameters;
  const config = deviceTypeConfig[type];

  return (
    <div className="flex items-center">
      <div
        className={cn(
          "flex flex-col rounded-lg border p-3 min-w-[140px] max-w-[180px]",
          config.bgColor
        )}
      >
        {/* Device Header */}
        <div className="flex items-center gap-2 mb-2">
          <span className={config.color}>{config.icon}</span>
          <span className="text-xs font-medium text-foreground truncate">
            {name}
          </span>
        </div>

        {/* Device Type */}
        <span
          className={cn(
            "text-[9px] uppercase tracking-wider font-medium mb-2",
            config.color
          )}
        >
          {type}
        </span>

        {/* Parameters Preview */}
        {params && Object.keys(params).length > 0 && (
          <div className="space-y-1 pt-2 border-t border-border/50">
            {Object.entries(params)
              .slice(0, 3)
              .map(([key, value]) => (
                <div
                  key={key}
                  className="flex items-center justify-between text-[10px]"
                >
                  <span className="text-muted-foreground truncate">{key}</span>
                  <span className="text-foreground font-mono">
                    {typeof value === "number"
                      ? value.toFixed(2)
                      : String(value)}
                  </span>
                </div>
              ))}
            {Object.keys(params).length > 3 && (
              <span className="text-[9px] text-muted-foreground">
                +{Object.keys(params).length - 3} more
              </span>
            )}
          </div>
        )}
      </div>

      {/* Connection Line */}
      {!isLast && (
        <div className="flex items-center px-2">
          <div className="w-4 h-px bg-border" />
          <ChevronRight className="w-4 h-4 text-muted-foreground" />
          <div className="w-4 h-px bg-border" />
        </div>
      )}
    </div>
  );
}

interface DeviceChainPanelProps {
  devices: (DeviceChainItem | string)[];
  parameters?: Record<string, unknown>;
}

export function DeviceChainPanel({
  devices,
  parameters,
}: DeviceChainPanelProps) {
  const hasDevices = devices.length > 0;

  // Convert string devices to DeviceChainItem with parameters
  const enrichedDevices: DeviceChainItem[] = devices.map((d, i) => {
    if (typeof d === "string") {
      // If it's the first device (instrument) and we have parameters, attach them
      const deviceParams =
        i === 0 && parameters ? parameters : undefined;
      return {
        name: d,
        type: getDeviceType(d),
        parameters: deviceParams as Record<string, unknown> | undefined,
      };
    }
    return d;
  });

  return (
    <div className="flex flex-col h-full bg-panel rounded-lg border border-border overflow-hidden">
      {/* Panel Header */}
      <div className="h-10 px-4 flex items-center justify-between border-b border-border bg-panel-header">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium text-foreground">
            Device Chain
          </span>
        </div>
        <span className="text-xs text-muted-foreground">
          {hasDevices ? `${devices.length} devices` : "No devices"}
        </span>
      </div>

      {/* Panel Content */}
      <div className="flex-1 overflow-x-auto p-4">
        {hasDevices ? (
          <div className="flex items-stretch min-w-max">
            {enrichedDevices.map((device, i) => (
              <DeviceBlock
                key={i}
                device={device}
                isLast={i === enrichedDevices.length - 1}
              />
            ))}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <Sliders className="w-8 h-8 text-muted-foreground/30 mx-auto mb-2" />
              <p className="text-sm text-muted-foreground">
                No device chain to display
              </p>
              <p className="text-xs text-muted-foreground/60 mt-1">
                Query a preset to see its device chain
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
