"use client"

import { useState, FormEvent } from "react"
import { Search, Sparkles, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface SearchInputProps {
  onSearch: (prompt: string) => void
  isLoading: boolean
}

const examplePrompts = [
  "warm dreamy pad for rnb",
  "dark menacing drill bass",
  "bright future bass lead",
  "ethereal ambient texture",
  "punchy trap 808",
]

export function SearchInput({ onSearch, isLoading }: SearchInputProps) {
  const [prompt, setPrompt] = useState("")

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (prompt.trim() && !isLoading) {
      onSearch(prompt.trim())
    }
  }

  const handleExampleClick = (example: string) => {
    setPrompt(example)
    onSearch(example)
  }

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe your sound... e.g., warm dreamy pad for rnb"
            className={cn(
              "h-14 w-full rounded-xl border border-border bg-card pl-12 pr-32 text-base text-foreground placeholder:text-muted-foreground",
              "focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20",
              "transition-all duration-200"
            )}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!prompt.trim() || isLoading}
            className={cn(
              "absolute right-2 top-1/2 -translate-y-1/2 flex h-10 items-center gap-2 rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground",
              "transition-all duration-200",
              "disabled:cursor-not-allowed disabled:opacity-50",
              "hover:bg-primary/90"
            )}
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="hidden sm:inline">Searching</span>
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                <span className="hidden sm:inline">Generate</span>
              </>
            )}
          </button>
        </div>
      </form>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <span className="text-sm text-muted-foreground">Try:</span>
        {examplePrompts.map((example) => (
          <button
            key={example}
            onClick={() => handleExampleClick(example)}
            disabled={isLoading}
            className={cn(
              "rounded-full border border-border bg-secondary px-3 py-1.5 text-xs font-medium text-secondary-foreground",
              "transition-all duration-200",
              "hover:border-primary hover:text-primary",
              "disabled:cursor-not-allowed disabled:opacity-50"
            )}
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  )
}
