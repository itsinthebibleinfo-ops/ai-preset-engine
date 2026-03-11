// Types matching the backend API models

export interface ScoreBreakdown {
  family: number;
  style_cluster: number;
  tag_overlap: number;
  attributes: number;
  provenance_confidence: number;
}

export interface Provenance {
  source_dataset: string;
  confidence: number;
}

export interface PresetResult {
  preset_name: string;
  family: string;
  style_cluster: string;
  device_chain: string[];
  parameters: Record<string, unknown>;
  score: number;
  score_breakdown: ScoreBreakdown;
  provenance: Provenance;
}

export interface RetrieveResponse {
  prompt: string;
  results: PresetResult[];
  warnings: string[];
}

export interface RetrieveRequest {
  prompt: string;
  top_k: number;
}

// UI State types
export type ConnectionStatus = "connected" | "connecting" | "disconnected";

export interface LogEntry {
  id: string;
  timestamp: Date;
  type: "info" | "success" | "warning" | "error";
  message: string;
}

export type DeviceType = "instrument" | "effect" | "utility";

export interface DeviceChainItem {
  name: string;
  type: DeviceType;
  parameters?: Record<string, unknown>;
}
