"use client";

import { DeviceChainPanel } from "@/components/device-chain-panel";
import { LogConsole } from "@/components/log-console";
import { PromptPanel } from "@/components/prompt-panel";
import { ResultsPanel } from "@/components/results-panel";
import { TopBar } from "@/components/top-bar";
import type {
  ConnectionStatus,
  LogEntry,
  PresetResult,
  RetrieveResponse,
} from "@/types/preset";
import { useCallback, useEffect, useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function generateLogId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export default function Home() {
  // Connection states
  const [apiStatus, setApiStatus] = useState<ConnectionStatus>("connecting");
  const [bridgeStatus, setBridgeStatus] =
    useState<ConnectionStatus>("disconnected");
  const [engineStatus, setEngineStatus] =
    useState<ConnectionStatus>("connecting");

  // Query state
  const [isQuerying, setIsQuerying] = useState(false);
  const [results, setResults] = useState<PresetResult[]>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  // Logs
  const [logs, setLogs] = useState<LogEntry[]>([]);

  // Add log helper
  const addLog = useCallback(
    (type: LogEntry["type"], message: string) => {
      setLogs((prev) => [
        ...prev,
        {
          id: generateLogId(),
          timestamp: new Date(),
          type,
          message,
        },
      ]);
    },
    []
  );

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
          setApiStatus("connected");
          setEngineStatus("connected");
          addLog("success", "Connected to AI Preset Engine API");
        } else {
          throw new Error("API not healthy");
        }
      } catch {
        setApiStatus("disconnected");
        setEngineStatus("disconnected");
        addLog(
          "warning",
          "API not available. Using demo mode with simulated responses."
        );
      }
    };

    addLog("info", "Initializing AI Preset Engine...");
    checkHealth();
  }, [addLog]);

  // Query handler
  const handleQuery = useCallback(
    async (prompt: string, topK: number, device: string) => {
      setIsQuerying(true);
      setSelectedIndex(null);
      addLog("info", `Querying: "${prompt}" (top_k=${topK}, target=${device})`);

      try {
        // Try to call the real API
        const response = await fetch(`${API_BASE_URL}/api/retrieve`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt, top_k: topK }),
        });

        if (response.ok) {
          const data: RetrieveResponse = await response.json();
          setResults(data.results);
          setWarnings(data.warnings);
          setSelectedIndex(data.results.length > 0 ? 0 : null);
          addLog(
            "success",
            `Retrieved ${data.results.length} presets`
          );
          if (data.warnings.length > 0) {
            data.warnings.forEach((w) => addLog("warning", w));
          }
        } else {
          throw new Error("API error");
        }
      } catch {
        // Demo mode: generate simulated results
        addLog("info", "Using demo mode with simulated results");
        const demoResults = generateDemoResults(prompt, topK);
        setResults(demoResults);
        setWarnings([]);
        setSelectedIndex(0);
        addLog("success", `Generated ${demoResults.length} demo presets`);
      } finally {
        setIsQuerying(false);
      }
    },
    [addLog]
  );

  // Apply handler
  const handleApply = useCallback(() => {
    if (selectedIndex !== null && results[selectedIndex]) {
      const preset = results[selectedIndex];
      addLog("info", `Applying preset: ${preset.preset_name}`);

      // In production, this would send to the Max for Live bridge
      if (bridgeStatus === "connected") {
        addLog("success", `Preset "${preset.preset_name}" applied to Ableton`);
      } else {
        addLog(
          "warning",
          "Ableton bridge not connected. Preset saved locally."
        );
      }
    }
  }, [selectedIndex, results, bridgeStatus, addLog]);

  // Clear handler
  const handleClear = useCallback(() => {
    setResults([]);
    setWarnings([]);
    setSelectedIndex(null);
    addLog("info", "Cleared results");
  }, [addLog]);

  // Get selected preset's device chain and parameters
  const selectedPreset =
    selectedIndex !== null ? results[selectedIndex] : null;

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      <TopBar
        apiStatus={apiStatus}
        bridgeStatus={bridgeStatus}
        engineStatus={engineStatus}
      />

      <main className="flex-1 p-4 flex flex-col gap-4 overflow-hidden">
        {/* Top Row: Prompt + Results */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-0">
          <PromptPanel
            onQuery={handleQuery}
            onApply={handleApply}
            onClear={handleClear}
            isQuerying={isQuerying}
            hasResults={results.length > 0}
          />
          <ResultsPanel
            results={results}
            selectedIndex={selectedIndex}
            onSelectResult={setSelectedIndex}
            isLoading={isQuerying}
            warnings={warnings}
          />
        </div>

        {/* Device Chain Panel */}
        <div className="h-40 shrink-0">
          <DeviceChainPanel
            devices={selectedPreset?.device_chain || []}
            parameters={selectedPreset?.parameters}
          />
        </div>

        {/* Log Console */}
        <LogConsole logs={logs} />
      </main>
    </div>
  );
}

// Demo result generator for when API is not available
function generateDemoResults(prompt: string, topK: number): PresetResult[] {
  const families = ["Pad", "Lead", "Bass", "Keys", "Bell", "Texture"];
  const clusters = [
    "Warm Analog",
    "Digital Crisp",
    "Lo-Fi",
    "Cinematic",
    "Ambient",
  ];
  const devices = [
    ["Wavetable", "Chorus", "Reverb"],
    ["Operator", "Filter", "Delay", "Compressor"],
    ["Analog", "Saturator", "EQ Eight"],
    ["Drift", "Phaser", "Reverb", "Utility"],
  ];

  return Array.from({ length: topK }, (_, i) => {
    const familyIndex = Math.floor(Math.random() * families.length);
    const clusterIndex = Math.floor(Math.random() * clusters.length);
    const deviceIndex = Math.floor(Math.random() * devices.length);
    const score = Math.max(0.2, 1 - i * 0.15 - Math.random() * 0.1);

    return {
      preset_name: `${clusters[clusterIndex]} ${families[familyIndex]} ${i + 1}`,
      family: families[familyIndex],
      style_cluster: clusters[clusterIndex],
      device_chain: devices[deviceIndex],
      parameters: {
        Osc1_Level: Math.random(),
        Filter_Freq: Math.random() * 20000,
        Filter_Res: Math.random(),
        Amp_Attack: Math.random() * 2,
        Amp_Release: Math.random() * 5,
      },
      score,
      score_breakdown: {
        family: Math.random() * 0.3,
        style_cluster: Math.random() * 0.3,
        tag_overlap: Math.random() * 0.2,
        attributes: Math.random() * 0.1,
        provenance_confidence: Math.random() * 0.1,
      },
      provenance: {
        source_dataset: "unified_sound_knowledge",
        confidence: score,
      },
    };
  });
}
