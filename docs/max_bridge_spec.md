# Max for Live Bridge MVP Spec

## Goal
Enable prompt-to-preset in Ableton by posting prompts to `POST /api/retrieve` and applying returned parameters to an already loaded stock device (MVP: Wavetable).

## UI Elements
- `textedit` (Prompt Input)
- `textbutton` (Generate)
- `textbutton` (Apply)
- `comment` / `message` (Status)
- Result display fields:
  - Preset Name
  - Family
  - Style Cluster
  - Device Chain

## Message Flow
1. `live.thisdevice` bangs when ready.
2. JS bridge initializes API + LiveAPI access only after readiness bang.
3. Generate button sends prompt to JS (`generate <prompt>`).
4. JS calls `http://127.0.0.1:8000/api/retrieve`.
5. JS parses JSON and updates UI outlets with:
   - preset name
   - family
   - style cluster
   - device chain
6. Apply button sends `apply` to JS.
7. JS locates selected existing device and applies parameter map.

## Recommended Max Object Layout
- `live.thisdevice` -> `js retrieve_and_apply.js`
- `textedit` -> `prepend generate` -> `js`
- `button` -> `message apply` -> `js`
- JS outlets -> UI comments/messages for status + result

## Data Contract Expectations
API response must include:
- `prompt`
- `results[]`
- Top result fields:
  - `preset_name`
  - `family`
  - `style_cluster`
  - `device_chain`
  - `parameters`
  - `score`
  - `score_breakdown`
- `warnings[]`

## MVP Scope
- Applies parameters to an existing loaded device.
- No automatic device-chain creation in MVP.
- Wavetable first; keep mapping extension-ready for Operator/Analog/Drift.
