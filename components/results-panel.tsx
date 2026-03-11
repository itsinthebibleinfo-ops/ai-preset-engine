"use client";

import { cn } from "@/lib/utils";
import type { PresetResult } from "@/types/preset";
import { Layers, Search } from "lucide-react";
import { PresetCard, PresetCardSkeleton } from "./preset-card";

interface ResultsPanelProps {
  results: PresetResult[];
  selectedIndex: number | null;
  onSelectResult: (index: number) => void;
  isLoading: boolean;
  warnings?: string[];
}

export function ResultsPanel({
  results,
  selectedIndex,
  onSelectResult,
  isLoading,
  warnings = [],
}: ResultsPanelProps) {
  const hasResults = results.length > 0;

  return (
    <div className="flex flex-col h-full bg-panel rounded-lg border border-border overflow-hidden">
      {/* Panel Header */}
      <div className="h-10 px-4 flex items-center justify-between border-b border-border bg-panel-header">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium text-foreground">
            Retrieval Results
          </span>
        </div>
        <span className="text-xs text-muted-foreground">
          {hasResults ? `${results.length} presets found` : "Awaiting query"}
        </span>
      </div>

      {/* Panel Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {isLoading ? (
          <div className="grid gap-4">
            {[1, 2, 3].map((i) => (
              <PresetCardSkeleton key={i} />
            ))}
          </div>
        ) : hasResults ? (
          <div className="grid gap-4">
            {results.map((preset, index) => (
              <PresetCard
                key={`${preset.preset_name}-${index}`}
                preset={preset}
                rank={index + 1}
                isSelected={selectedIndex === index}
                onSelect={() => onSelectResult(index)}
                warnings={index === 0 ? warnings : undefined}
              />
            ))}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <Search className="w-8 h-8 text-muted-foreground/30 mx-auto mb-2" />
              <p className="text-sm text-muted-foreground">
                No results to display
              </p>
              <p className="text-xs text-muted-foreground/60 mt-1">
                Enter a sound prompt and click Query
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
