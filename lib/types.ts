export interface ScoreBreakdown {
  family: number
  genre: number
  subgenre: number
  style_cluster: number
  tag_overlap: number
  attribute_alignment: number
  mood: number
  provenance: number
}

export interface PresetAttributes {
  brightness: number
  warmth: number
  stereo_width: number
  motion: number
  reverb: number
  attack_ms: number
  release_ms: number
}

export interface PresetResult {
  rank: number
  preset_id: string
  preset_name: string
  family: string
  genre: string
  style_cluster: string
  tags: string[]
  score: number
  breakdown: ScoreBreakdown
  device_chain: string[]
  attributes: PresetAttributes
  parameters: Record<string, Record<string, number | string>>
}

export interface ParsedQuery {
  raw: string
  parsed_family: string | null
  parsed_genre: string | null
  parsed_tags: string[]
  parsed_moods: string[]
  style_cluster_hints: string[]
}

export interface ResponseMetadata {
  total_presets_searched: number
  results_returned: number
  top_score: number
}

export interface GenerateResponse {
  query: ParsedQuery
  results: PresetResult[]
  metadata: ResponseMetadata
}

export interface TaxonomyResponse {
  genres: string[]
  sound_families: string[]
  style_clusters: string[]
}
