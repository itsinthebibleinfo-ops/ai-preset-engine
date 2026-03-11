"use client";

import { cn } from "@/lib/utils";
import type { PresetResult } from "@/types/preset";
import { AlertTriangle, ChevronRight, Music, Tag } from "lucide-react";

interface ScoreBarProps {
  label: string;
  value: number;
  maxValue?: number;
}

function ScoreBar({ label, value, maxValue = 1 }: ScoreBarProps) {
  const percentage = Math.min((value / maxValue) * 100, 100);

  return (
    <div className="flex items-center gap-2">
      <span className="text-[10px] text-muted-foreground w-16 truncate">
        {label}
      </span>
      <div className="flex-1 h-1.5 bg-secondary rounded-full overflow-hidden">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-500",
            percentage >= 70
              ? "bg-success"
              : percentage >= 40
                ? "bg-warning"
                : "bg-muted-foreground"
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-[10px] text-muted-foreground w-8 text-right font-mono">
        {value.toFixed(2)}
      </span>
    </div>
  );
}

interface PresetCardProps {
  preset: PresetResult;
  rank: number;
  isSelected?: boolean;
  onSelect?: () => void;
  warnings?: string[];
}

export function PresetCard({
  preset,
  rank,
  isSelected,
  onSelect,
  warnings = [],
}: PresetCardProps) {
  const { preset_name, family, style_cluster, score, score_breakdown } = preset;

  return (
    <div
      onClick={onSelect}
      className={cn(
        "group relative flex flex-col rounded-lg border transition-all cursor-pointer",
        "bg-card hover:bg-card/80",
        isSelected
          ? "border-primary ring-1 ring-primary/30"
          : "border-border hover:border-muted-foreground/50"
      )}
    >
      {/* Rank Badge */}
      <div
        className={cn(
          "absolute -top-2 -left-2 w-6 h-6 rounded-full flex items-center justify-center",
          "text-[10px] font-bold",
          rank === 1
            ? "bg-primary text-primary-foreground"
            : "bg-secondary text-muted-foreground border border-border"
        )}
      >
        {rank}
      </div>

      {/* Card Header */}
      <div className="p-4 pb-3 border-b border-border">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-foreground truncate">
              {preset_name || "Unnamed Preset"}
            </h3>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-primary/10 text-primary font-medium">
                {family || "Unknown"}
              </span>
              {style_cluster && (
                <span className="text-[10px] text-muted-foreground">
                  {style_cluster}
                </span>
              )}
            </div>
          </div>
          <div className="flex flex-col items-end">
            <div
              className={cn(
                "text-lg font-bold font-mono",
                score >= 0.5
                  ? "text-success"
                  : score >= 0.25
                    ? "text-warning"
                    : "text-muted-foreground"
              )}
            >
              {(score * 100).toFixed(0)}
            </div>
            <span className="text-[10px] text-muted-foreground">score</span>
          </div>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="p-4 space-y-2">
        <div className="flex items-center gap-1.5 mb-3">
          <Tag className="w-3 h-3 text-muted-foreground" />
          <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
            Score Breakdown
          </span>
        </div>

        <ScoreBar label="Family" value={score_breakdown.family} />
        <ScoreBar label="Style" value={score_breakdown.style_cluster} />
        <ScoreBar label="Tags" value={score_breakdown.tag_overlap} />
        <ScoreBar label="Attributes" value={score_breakdown.attributes} />
        <ScoreBar
          label="Confidence"
          value={score_breakdown.provenance_confidence}
        />
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="px-4 pb-3">
          {warnings.map((warning, i) => (
            <div
              key={i}
              className="flex items-start gap-2 p-2 rounded bg-warning/10 border border-warning/20"
            >
              <AlertTriangle className="w-3.5 h-3.5 text-warning shrink-0 mt-0.5" />
              <span className="text-[11px] text-warning">{warning}</span>
            </div>
          ))}
        </div>
      )}

      {/* Device Chain Preview */}
      {preset.device_chain.length > 0 && (
        <div className="px-4 pb-4">
          <div className="flex items-center gap-1.5 mb-2">
            <Music className="w-3 h-3 text-muted-foreground" />
            <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
              Device Chain
            </span>
          </div>
          <div className="flex items-center gap-1 overflow-x-auto pb-1">
            {preset.device_chain.slice(0, 4).map((device, i) => (
              <div key={i} className="flex items-center">
                <span className="text-[10px] px-2 py-1 rounded bg-secondary text-foreground whitespace-nowrap">
                  {device}
                </span>
                {i < Math.min(preset.device_chain.length, 4) - 1 && (
                  <ChevronRight className="w-3 h-3 text-muted-foreground shrink-0" />
                )}
              </div>
            ))}
            {preset.device_chain.length > 4 && (
              <span className="text-[10px] text-muted-foreground ml-1">
                +{preset.device_chain.length - 4}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Selection Indicator */}
      {isSelected && (
        <div className="absolute inset-0 rounded-lg pointer-events-none">
          <div className="absolute inset-0 bg-primary/5 rounded-lg" />
        </div>
      )}
    </div>
  );
}

// Skeleton loader for preset card
export function PresetCardSkeleton() {
  return (
    <div className="flex flex-col rounded-lg border border-border bg-card animate-pulse">
      <div className="p-4 pb-3 border-b border-border">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1">
            <div className="h-4 w-32 bg-secondary rounded" />
            <div className="flex items-center gap-2 mt-2">
              <div className="h-4 w-16 bg-secondary rounded" />
              <div className="h-3 w-20 bg-secondary rounded" />
            </div>
          </div>
          <div className="h-8 w-10 bg-secondary rounded" />
        </div>
      </div>
      <div className="p-4 space-y-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="flex items-center gap-2">
            <div className="h-2 w-14 bg-secondary rounded" />
            <div className="flex-1 h-1.5 bg-secondary rounded-full" />
            <div className="h-2 w-8 bg-secondary rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}
