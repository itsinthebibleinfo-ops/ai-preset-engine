import { NextRequest, NextResponse } from "next/server"

// For demo purposes, we'll return mock data that matches the API structure
// In production, this would proxy to the Python backend

const mockPresets = [
  {
    rank: 1,
    preset_id: "pad_001",
    preset_name: "Haze Haze",
    family: "pad",
    genre: "rnb",
    style_cluster: "contemporary_rnb_pad",
    tags: ["warm", "airy", "wide", "lush"],
    score: 12.5,
    breakdown: {
      family: 4.0,
      genre: 3.0,
      subgenre: 2.0,
      style_cluster: 2.333,
      tag_overlap: 3.0,
      attribute_alignment: 0.75,
      mood: 0.0,
      provenance: 0.5,
    },
    device_chain: ["Wavetable", "Chorus-Ensemble", "Hybrid Reverb", "Utility"],
    attributes: {
      brightness: 0.26,
      warmth: 0.62,
      stereo_width: 0.8,
      motion: 0.35,
      reverb: 0.44,
      attack_ms: 1158,
      release_ms: 3659,
    },
    parameters: {
      Wavetable: {
        filter_cutoff: 3109,
        attack_ms: 714,
        release_ms: 2851,
        detune: 0.29,
        osc_level: 0.77,
      },
    },
  },
  {
    rank: 2,
    preset_id: "pad_011",
    preset_name: "Velvet Sky",
    family: "pad",
    genre: "rnb",
    style_cluster: "contemporary_rnb_pad",
    tags: ["warm", "dreamy", "wide", "soft"],
    score: 11.2,
    breakdown: {
      family: 4.0,
      genre: 3.0,
      subgenre: 1.5,
      style_cluster: 2.0,
      tag_overlap: 2.5,
      attribute_alignment: 0.7,
      mood: 0.0,
      provenance: 0.5,
    },
    device_chain: ["Wavetable", "Chorus-Ensemble", "Hybrid Reverb"],
    attributes: {
      brightness: 0.32,
      warmth: 0.68,
      stereo_width: 0.85,
      motion: 0.28,
      reverb: 0.52,
      attack_ms: 980,
      release_ms: 3200,
    },
    parameters: {
      Wavetable: {
        filter_cutoff: 2800,
        attack_ms: 650,
        release_ms: 2400,
        detune: 0.22,
        osc_level: 0.82,
      },
    },
  },
  {
    rank: 3,
    preset_id: "pad_002",
    preset_name: "Grace Wash",
    family: "pad",
    genre: "gospel",
    style_cluster: "gospel_swell_pad",
    tags: ["swell", "heavenly", "wide", "bright"],
    score: 9.8,
    breakdown: {
      family: 4.0,
      genre: 0.0,
      subgenre: 1.0,
      style_cluster: 1.8,
      tag_overlap: 2.0,
      attribute_alignment: 0.5,
      mood: 0.5,
      provenance: 0.5,
    },
    device_chain: [
      "Wavetable",
      "Chorus-Ensemble",
      "Hybrid Reverb",
      "EQ Eight",
      "Utility",
    ],
    attributes: {
      brightness: 0.64,
      warmth: 0.54,
      stereo_width: 0.85,
      motion: 0.16,
      reverb: 0.61,
      attack_ms: 1127,
      release_ms: 4275,
    },
    parameters: {
      Wavetable: {
        filter_cutoff: 3706,
        attack_ms: 1284,
        release_ms: 3513,
        detune: 0.34,
        osc_level: 0.79,
      },
    },
  },
  {
    rank: 4,
    preset_id: "pad_003",
    preset_name: "Ether Space",
    family: "pad",
    genre: "ambient",
    style_cluster: "ambient_texture",
    tags: ["vast", "ethereal", "textured", "deep"],
    score: 8.5,
    breakdown: {
      family: 4.0,
      genre: 0.0,
      subgenre: 0.5,
      style_cluster: 1.5,
      tag_overlap: 1.5,
      attribute_alignment: 0.5,
      mood: 0.5,
      provenance: 0.0,
    },
    device_chain: [
      "Wavetable",
      "Hybrid Reverb",
      "Echo",
      "Auto Filter",
      "Utility",
    ],
    attributes: {
      brightness: 0.25,
      warmth: 0.51,
      stereo_width: 0.95,
      motion: 0.5,
      reverb: 0.74,
      attack_ms: 2872,
      release_ms: 5093,
    },
    parameters: {
      Wavetable: {
        filter_cutoff: 1800,
        attack_ms: 2787,
        release_ms: 6533,
        detune: 0.57,
        osc_level: 0.71,
      },
    },
  },
  {
    rank: 5,
    preset_id: "pad_008",
    preset_name: "Crinkle Haze",
    family: "pad",
    genre: "lofi",
    style_cluster: "lofi_hazy_pad",
    tags: ["dusty", "lo-fi", "warm", "dreamy"],
    score: 7.2,
    breakdown: {
      family: 4.0,
      genre: 0.0,
      subgenre: 0.0,
      style_cluster: 1.2,
      tag_overlap: 1.5,
      attribute_alignment: 0.3,
      mood: 0.2,
      provenance: 0.0,
    },
    device_chain: ["Analog", "Saturator", "EQ Eight", "Reverb"],
    attributes: {
      brightness: 0.39,
      warmth: 0.67,
      stereo_width: 0.67,
      motion: 0.17,
      reverb: 0.49,
      attack_ms: 328,
      release_ms: 1762,
    },
    parameters: {
      Analog: {
        filter_cutoff: 2000,
        attack_ms: 219,
        release_ms: 1729,
        osc1_level: 0.88,
        osc2_level: 0.56,
      },
    },
  },
]

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { prompt, top_k = 5 } = body

    if (!prompt) {
      return NextResponse.json({ error: "Prompt is required" }, { status: 400 })
    }

    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 800))

    // Return mock response matching the v2/generate endpoint
    return NextResponse.json({
      query: {
        raw: prompt,
        parsed_family: "pad",
        parsed_genre: prompt.includes("rnb") ? "rnb" : null,
        parsed_tags: prompt.split(" ").filter((w: string) => w.length > 2),
        parsed_moods: [],
        style_cluster_hints: prompt.split(" "),
      },
      results: mockPresets.slice(0, top_k),
      metadata: {
        total_presets_searched: 1000,
        results_returned: Math.min(top_k, mockPresets.length),
        top_score: mockPresets[0].score,
      },
    })
  } catch {
    return NextResponse.json(
      { error: "Failed to process request" },
      { status: 500 }
    )
  }
}
