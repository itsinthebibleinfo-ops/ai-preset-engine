"use client"

import { motion } from "framer-motion"
import { PresetCard } from "./preset-card"
import { QueryInfo } from "./query-info"
import type { GenerateResponse } from "@/lib/types"

interface PresetResultsProps {
  data: GenerateResponse
}

export function PresetResults({ data }: PresetResultsProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      <QueryInfo query={data.query} metadata={data.metadata} />

      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-foreground">
          Recommended Presets
        </h2>
        <p className="text-sm text-muted-foreground">
          Top score:{" "}
          <span className="font-medium text-primary">
            {data.metadata.top_score.toFixed(1)}
          </span>
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {data.results.map((preset, index) => (
          <PresetCard key={preset.preset_id} preset={preset} index={index} />
        ))}
      </div>
    </motion.div>
  )
}
