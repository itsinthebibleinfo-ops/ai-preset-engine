"use client"

import { motion } from "framer-motion"
import { Brain, Database, Layers, Tag } from "lucide-react"
import type { ParsedQuery, ResponseMetadata } from "@/lib/types"

interface QueryInfoProps {
  query: ParsedQuery
  metadata: ResponseMetadata
}

export function QueryInfo({ query, metadata }: QueryInfoProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-border bg-card p-5"
    >
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Brain className="h-4 w-4 text-primary" />
        <span>AI parsed your prompt</span>
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {query.parsed_family && (
          <div className="flex items-start gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-cyan-500/10">
              <Layers className="h-4 w-4 text-cyan-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Sound Family</p>
              <p className="text-sm font-medium capitalize text-foreground">
                {query.parsed_family}
              </p>
            </div>
          </div>
        )}

        {query.parsed_genre && (
          <div className="flex items-start gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-orange-500/10">
              <Tag className="h-4 w-4 text-orange-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Genre</p>
              <p className="text-sm font-medium capitalize text-foreground">
                {query.parsed_genre.replace(/_/g, " ")}
              </p>
            </div>
          </div>
        )}

        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-pink-500/10">
            <Tag className="h-4 w-4 text-pink-400" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Detected Tags</p>
            <div className="mt-0.5 flex flex-wrap gap-1">
              {query.parsed_tags.slice(0, 4).map((tag) => (
                <span
                  key={tag}
                  className="rounded bg-secondary px-1.5 py-0.5 text-xs text-secondary-foreground"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-500/10">
            <Database className="h-4 w-4 text-emerald-400" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Search Results</p>
            <p className="text-sm font-medium text-foreground">
              {metadata.results_returned} of {metadata.total_presets_searched.toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
