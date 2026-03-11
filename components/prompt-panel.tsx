"use client";

import { cn } from "@/lib/utils";
import { Loader2, Search, Sparkles, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

const EXAMPLE_PROMPTS = [
  "warm airy neo soul pad",
  "dark trap bell",
  "nostalgic gospel keys",
  "ambient cinematic texture",
  "gritty lo-fi bass",
  "ethereal choir lead",
  "punchy analog kick",
  "shimmering arpeggio",
];

const TARGET_DEVICES = [
  { value: "wavetable", label: "Wavetable" },
  { value: "operator", label: "Operator" },
  { value: "analog", label: "Analog" },
  { value: "drift", label: "Drift" },
];

const TOP_K_OPTIONS = [1, 3, 5, 10];

interface PromptPanelProps {
  onQuery: (prompt: string, topK: number, device: string) => void;
  onApply: () => void;
  onClear: () => void;
  isQuerying: boolean;
  hasResults: boolean;
}

export function PromptPanel({
  onQuery,
  onApply,
  onClear,
  isQuerying,
  hasResults,
}: PromptPanelProps) {
  const [prompt, setPrompt] = useState("");
  const [topK, setTopK] = useState(3);
  const [targetDevice, setTargetDevice] = useState("wavetable");
  const [placeholderIndex, setPlaceholderIndex] = useState(0);

  // Cycle through placeholder prompts
  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((prev) => (prev + 1) % EXAMPLE_PROMPTS.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (prompt.trim() && !isQuerying) {
        onQuery(prompt.trim(), topK, targetDevice);
      }
    },
    [prompt, topK, targetDevice, isQuerying, onQuery]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
        handleSubmit(e);
      }
    },
    [handleSubmit]
  );

  return (
    <div className="flex flex-col h-full bg-panel rounded-lg border border-border overflow-hidden">
      {/* Panel Header */}
      <div className="h-10 px-4 flex items-center justify-between border-b border-border bg-panel-header">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium text-foreground">
            Sound Prompt
          </span>
        </div>
        <span className="text-xs text-muted-foreground">
          Describe your sound
        </span>
      </div>

      {/* Panel Content */}
      <div className="flex-1 p-4 flex flex-col gap-4">
        {/* Prompt Input */}
        <form onSubmit={handleSubmit} className="flex-1 flex flex-col gap-4">
          <div className="relative flex-1">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={EXAMPLE_PROMPTS[placeholderIndex]}
              className={cn(
                "w-full h-full min-h-[120px] resize-none",
                "bg-secondary/50 border border-border rounded-md",
                "px-4 py-3 text-sm text-foreground",
                "placeholder:text-muted-foreground/50",
                "focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary",
                "transition-colors"
              )}
            />
            <div className="absolute bottom-3 right-3 text-xs text-muted-foreground">
              {prompt.length}/500
            </div>
          </div>

          {/* Controls Row */}
          <div className="flex items-center gap-3 flex-wrap">
            {/* Top-K Selector */}
            <div className="flex items-center gap-2">
              <label className="text-xs text-muted-foreground whitespace-nowrap">
                Results:
              </label>
              <div className="flex items-center bg-secondary/50 border border-border rounded-md overflow-hidden">
                {TOP_K_OPTIONS.map((k) => (
                  <button
                    key={k}
                    type="button"
                    onClick={() => setTopK(k)}
                    className={cn(
                      "px-3 py-1.5 text-xs font-medium transition-colors",
                      topK === k
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                    )}
                  >
                    {k}
                  </button>
                ))}
              </div>
            </div>

            {/* Target Device */}
            <div className="flex items-center gap-2">
              <label className="text-xs text-muted-foreground whitespace-nowrap">
                Target:
              </label>
              <select
                value={targetDevice}
                onChange={(e) => setTargetDevice(e.target.value)}
                className={cn(
                  "bg-secondary/50 border border-border rounded-md",
                  "px-3 py-1.5 text-xs text-foreground",
                  "focus:outline-none focus:ring-2 focus:ring-primary/50",
                  "cursor-pointer"
                )}
              >
                {TARGET_DEVICES.map((device) => (
                  <option key={device.value} value={device.value}>
                    {device.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Spacer */}
            <div className="flex-1" />

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClear}
                disabled={!prompt && !hasResults}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-md",
                  "text-xs font-medium transition-colors",
                  "border border-border",
                  "text-muted-foreground hover:text-foreground hover:bg-secondary",
                  "disabled:opacity-50 disabled:cursor-not-allowed"
                )}
              >
                <Trash2 className="w-3.5 h-3.5" />
                Clear
              </button>

              <button
                type="button"
                onClick={onApply}
                disabled={!hasResults}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-md",
                  "text-xs font-medium transition-colors",
                  "border border-primary/50 bg-primary/10",
                  "text-primary hover:bg-primary/20",
                  "disabled:opacity-50 disabled:cursor-not-allowed"
                )}
              >
                Apply
              </button>

              <button
                type="submit"
                disabled={!prompt.trim() || isQuerying}
                className={cn(
                  "flex items-center gap-2 px-5 py-2 rounded-md",
                  "text-xs font-medium transition-colors",
                  "bg-primary text-primary-foreground",
                  "hover:bg-primary/90",
                  "disabled:opacity-50 disabled:cursor-not-allowed"
                )}
              >
                {isQuerying ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    Querying...
                  </>
                ) : (
                  <>
                    <Search className="w-3.5 h-3.5" />
                    Query
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
