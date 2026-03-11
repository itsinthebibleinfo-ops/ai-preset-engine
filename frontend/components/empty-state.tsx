"use client"

import { Waves, Mic2, Music2, Headphones } from "lucide-react"

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="relative mb-6">
        <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/20 to-accent/20">
          <Waves className="h-10 w-10 text-primary" />
        </div>
        <div className="absolute -right-2 -top-2 flex h-8 w-8 items-center justify-center rounded-full bg-secondary">
          <Mic2 className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="absolute -bottom-2 -left-2 flex h-8 w-8 items-center justify-center rounded-full bg-secondary">
          <Music2 className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="absolute -bottom-1 -right-3 flex h-7 w-7 items-center justify-center rounded-full bg-secondary">
          <Headphones className="h-3.5 w-3.5 text-muted-foreground" />
        </div>
      </div>

      <h2 className="text-xl font-semibold text-foreground">
        Describe your sound
      </h2>
      <p className="mt-2 max-w-md text-muted-foreground">
        Use natural language to find the perfect preset. Try describing the
        mood, texture, genre, or sonic characteristics you&apos;re looking for.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        {[
          {
            title: "Texture & Mood",
            examples: ["warm", "airy", "dark", "ethereal"],
          },
          { title: "Genre", examples: ["rnb", "trap", "ambient", "lofi"] },
          {
            title: "Sound Type",
            examples: ["pad", "bass", "lead", "pluck"],
          },
        ].map((category) => (
          <div
            key={category.title}
            className="rounded-lg border border-border bg-card p-4 text-left"
          >
            <h3 className="text-sm font-medium text-foreground">
              {category.title}
            </h3>
            <div className="mt-2 flex flex-wrap gap-1">
              {category.examples.map((example) => (
                <span
                  key={example}
                  className="rounded bg-secondary px-2 py-0.5 text-xs text-muted-foreground"
                >
                  {example}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
