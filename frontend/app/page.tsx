"use client"

import { useState } from "react"
import useSWRMutation from "swr/mutation"
import { Header } from "@/components/header"
import { SearchInput } from "@/components/search-input"
import { PresetResults } from "@/components/preset-results"
import { EmptyState } from "@/components/empty-state"
import type { GenerateResponse } from "@/lib/types"

async function generatePresets(
  url: string,
  { arg }: { arg: { prompt: string; top_k?: number } }
) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(arg),
  })

  if (!response.ok) {
    throw new Error("Failed to generate presets")
  }

  return response.json() as Promise<GenerateResponse>
}

export default function HomePage() {
  const [lastPrompt, setLastPrompt] = useState<string | null>(null)

  const { data, error, isMutating, trigger } = useSWRMutation(
    "/api/generate",
    generatePresets
  )

  const handleSearch = async (prompt: string) => {
    setLastPrompt(prompt)
    try {
      await trigger({ prompt, top_k: 5 })
    } catch (err) {
      console.error("Search failed:", err)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="mb-10 text-center">
          <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            Find the perfect preset
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-pretty text-lg text-muted-foreground">
            Describe the sound you&apos;re looking for in natural language. Our
            AI will search through thousands of presets to find the best
            matches.
          </p>
        </section>

        <section className="mx-auto max-w-3xl">
          <SearchInput onSearch={handleSearch} isLoading={isMutating} />
        </section>

        {error && (
          <div className="mx-auto mt-8 max-w-3xl rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center text-destructive">
            <p>Failed to search presets. Please try again.</p>
          </div>
        )}

        <section className="mt-10">
          {data ? (
            <PresetResults data={data} />
          ) : lastPrompt === null ? (
            <EmptyState />
          ) : null}
        </section>
      </main>

      <footer className="border-t border-border bg-card/50 py-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <p className="text-sm text-muted-foreground">
              AI Preset Engine for Ableton Live
            </p>
            <div className="flex items-center gap-4">
              <a
                href="#"
                className="text-sm text-muted-foreground transition-colors hover:text-foreground"
              >
                API Docs
              </a>
              <a
                href="#"
                className="text-sm text-muted-foreground transition-colors hover:text-foreground"
              >
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
