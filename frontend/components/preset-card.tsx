"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  ChevronDown,
  ChevronUp,
  Zap,
  Music,
  Layers,
  Volume2,
} from "lucide-react"
import { cn } from "@/lib/utils"
import type { PresetResult } from "@/lib/types"

interface PresetCardProps {
  preset: PresetResult
  index: number
}

const familyIcons: Record<string, typeof Music> = {
  pad: Layers,
  bass: Volume2,
  lead: Zap,
  keys: Music,
}

const familyColors: Record<string, string> = {
  pad: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  bass: "bg-orange-500/10 text-orange-400 border-orange-500/20",
  lead: "bg-pink-500/10 text-pink-400 border-pink-500/20",
  keys: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  default: "bg-primary/10 text-primary border-primary/20",
}

function AttributeBar({
  label,
  value,
  color,
}: {
  label: string
  value: number
  color: string
}) {
  return (
    <div className="flex items-center gap-3">
      <span className="w-20 text-xs text-muted-foreground">{label}</span>
      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-secondary">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value * 100}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className={cn("h-full rounded-full", color)}
        />
      </div>
      <span className="w-10 text-right text-xs tabular-nums text-muted-foreground">
        {Math.round(value * 100)}%
      </span>
    </div>
  )
}

function ScoreBreakdown({
  breakdown,
}: {
  breakdown: PresetResult["breakdown"]
}) {
  const items = [
    { key: "family", label: "Family", max: 4 },
    { key: "genre", label: "Genre", max: 4 },
    { key: "subgenre", label: "Subgenre", max: 3 },
    { key: "style_cluster", label: "Style", max: 3 },
    { key: "tag_overlap", label: "Tags", max: 4 },
    { key: "attribute_alignment", label: "Attributes", max: 2 },
    { key: "mood", label: "Mood", max: 2 },
    { key: "provenance", label: "Source", max: 1 },
  ]

  return (
    <div className="grid grid-cols-2 gap-x-6 gap-y-2 sm:grid-cols-4">
      {items.map(({ key, label, max }) => {
        const value = breakdown[key as keyof typeof breakdown]
        const percentage = value / max
        return (
          <div key={key} className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">{label}</span>
            <div className="h-1 flex-1 overflow-hidden rounded-full bg-secondary">
              <div
                className="h-full rounded-full bg-primary transition-all duration-300"
                style={{ width: `${percentage * 100}%` }}
              />
            </div>
            <span className="w-8 text-right text-xs tabular-nums text-muted-foreground">
              {value.toFixed(1)}
            </span>
          </div>
        )
      })}
    </div>
  )
}

export function PresetCard({ preset, index }: PresetCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const Icon = familyIcons[preset.family] || Music
  const colorClass = familyColors[preset.family] || familyColors.default

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className="overflow-hidden rounded-xl border border-border bg-card"
    >
      <div className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div
              className={cn(
                "flex h-12 w-12 shrink-0 items-center justify-center rounded-lg border",
                colorClass
              )}
            >
              <Icon className="h-6 w-6" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="rounded bg-secondary px-2 py-0.5 text-xs font-medium text-muted-foreground">
                  #{preset.rank}
                </span>
                <h3 className="truncate text-lg font-semibold text-foreground">
                  {preset.preset_name}
                </h3>
              </div>
              <div className="mt-1 flex flex-wrap items-center gap-2">
                <span className={cn("rounded-md border px-2 py-0.5 text-xs font-medium", colorClass)}>
                  {preset.family}
                </span>
                <span className="rounded-md bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground">
                  {preset.genre}
                </span>
              </div>
            </div>
          </div>

          <div className="flex flex-col items-end gap-1">
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-bold tabular-nums text-primary">
                {preset.score.toFixed(1)}
              </span>
              <span className="text-xs text-muted-foreground">pts</span>
            </div>
            <span className="text-xs text-muted-foreground">match score</span>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-1.5">
          {preset.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-secondary px-2.5 py-1 text-xs text-secondary-foreground"
            >
              {tag}
            </span>
          ))}
        </div>

        <div className="mt-5 space-y-2">
          <AttributeBar
            label="Brightness"
            value={preset.attributes.brightness}
            color="bg-amber-400"
          />
          <AttributeBar
            label="Warmth"
            value={preset.attributes.warmth}
            color="bg-orange-400"
          />
          <AttributeBar
            label="Stereo"
            value={preset.attributes.stereo_width}
            color="bg-cyan-400"
          />
          <AttributeBar
            label="Motion"
            value={preset.attributes.motion}
            color="bg-pink-400"
          />
          <AttributeBar
            label="Reverb"
            value={preset.attributes.reverb}
            color="bg-indigo-400"
          />
        </div>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="mt-4 flex w-full items-center justify-center gap-1 rounded-lg border border-border bg-secondary/50 py-2 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
        >
          {isExpanded ? (
            <>
              <span>Hide Details</span>
              <ChevronUp className="h-4 w-4" />
            </>
          ) : (
            <>
              <span>Show Details</span>
              <ChevronDown className="h-4 w-4" />
            </>
          )}
        </button>
      </div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="border-t border-border bg-secondary/30 p-5">
              <div className="mb-4">
                <h4 className="mb-2 text-sm font-medium text-foreground">
                  Score Breakdown
                </h4>
                <ScoreBreakdown breakdown={preset.breakdown} />
              </div>

              <div className="mb-4">
                <h4 className="mb-2 text-sm font-medium text-foreground">
                  Device Chain
                </h4>
                <div className="flex flex-wrap gap-2">
                  {preset.device_chain.map((device, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <span className="rounded-md border border-border bg-card px-2.5 py-1 text-xs font-medium text-foreground">
                        {device}
                      </span>
                      {i < preset.device_chain.length - 1 && (
                        <span className="text-muted-foreground">→</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="mb-2 text-sm font-medium text-foreground">
                  Envelope
                </h4>
                <div className="flex gap-6">
                  <div className="text-center">
                    <span className="text-lg font-semibold tabular-nums text-foreground">
                      {preset.attributes.attack_ms}
                    </span>
                    <span className="ml-1 text-xs text-muted-foreground">ms</span>
                    <p className="text-xs text-muted-foreground">Attack</p>
                  </div>
                  <div className="text-center">
                    <span className="text-lg font-semibold tabular-nums text-foreground">
                      {preset.attributes.release_ms}
                    </span>
                    <span className="ml-1 text-xs text-muted-foreground">ms</span>
                    <p className="text-xs text-muted-foreground">Release</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
