/*
 * retrieve_and_apply.js
 *
 * Max for Live JS bridge for the AI Sound Design Engine.
 *
 * Sends a natural-language prompt to the local FastAPI backend,
 * parses the response, displays results, and applies parameters
 * to an existing Ableton device via LiveAPI.
 *
 * IMPORTANT:
 *   - Do NOT use LiveAPI in global scope.
 *   - Initialize only after live.thisdevice sends a bang.
 *   - Use deferlow() for any LiveAPI calls to stay off the
 *     high-priority Max scheduler thread.
 *
 * Wiring in Max:
 *   1. live.thisdevice → bang → [js retrieve_and_apply.js] inlet (init)
 *   2. textedit → prepend generate → [js] inlet
 *   3. "Generate" button → bang → textedit (triggers text output)
 *   4. "Apply" button → [message "apply"] → [js] inlet
 *
 * Outlets:
 *   0: status messages  (connect to a message box)
 *   1: result data       (via route → message boxes for each field)
 *   2: score breakdown   (connect to param display, optional)
 */

// ── Outlet declaration — MUST be first, in global scope ──────────────────────
// Max reads these after script execution completes and creates outlet ports.
// Never call outlet() during global scope execution — ports don't exist yet.

inlets  = 1;
outlets = 3;

// ── Configuration ────────────────────────────────────────────────────────────

var API_HOST      = "https://ai-preset-engine.onrender.com";
var API_PATH      = "/api/retrieve";
var DEFAULT_TOP_K = 3;

// ── State ────────────────────────────────────────────────────────────────────

var deviceReady = false;
var serverReady = false;
var lastResult  = null;   // stores the most recent top result for "apply"

// ── Parameter name mapping ───────────────────────────────────────────────────
// Maps the simplified param names in our preset DB to Ableton's internal names.

var PARAM_MAP = {
    "Wavetable": {
        "filter_cutoff": "Filter 1 Freq",
        "attack_ms":     "Amp Attack",
        "release_ms":    "Amp Release",
        "detune":        "Osc 1 Detune",
        "osc_level":     "Osc 1 Level"
    },
    "Operator": {
        "filter_cutoff": "Filter Freq",
        "attack_ms":     "Ae Attack",
        "release_ms":    "Ae Release"
    },
    "Analog": {
        "filter_cutoff": "F1 Freq",
        "attack_ms":     "Amp1 Attack",
        "release_ms":    "Amp1 Release"
    },
    "Drift": {
        "filter_cutoff": "Filter Freq",
        "attack_ms":     "Amp Attack",
        "release_ms":    "Amp Release"
    }
};

// ── Safe outlet helper ────────────────────────────────────────────────────────
// Always use safeOutlet() instead of outlet() directly.
//
// WHY: In Max JS, outlet ports only exist after the script finishes its
// initial execution pass. Calling outlet() during global scope execution
// or before live.thisdevice fires causes "bad outlet index N" errors.
// safeOutlet() guards against this at every call site.
//
// Max JS runs old SpiderMonkey — no spread operator, no Function.apply on
// builtins — so we dispatch by argument count.

function safeOutlet(idx, a, b, c) {
    if (idx < 0 || idx >= outlets) {
        post("[AI-Preset] safeOutlet: index " + idx +
             " out of range (outlets=" + outlets + ")\n");
        return;
    }
    if (arguments.length === 1) { outlet(idx); }
    else if (arguments.length === 2) { outlet(idx, a); }
    else if (arguments.length === 3) { outlet(idx, a, b); }
    else { outlet(idx, a, b, c); }
}

// ── Startup banner ────────────────────────────────────────────────────────────
// Use ONLY post() here — NEVER outlet() at load time.
// Outlets do not exist until after this script finishes executing.

post("[AI-Preset] ============================================\n");
post("[AI-Preset] retrieve_and_apply.js v4.2 loaded\n");
post("[AI-Preset] Outlets: 0=status  1=result data  2=score breakdown\n");
post("[AI-Preset] Commands: bang | generate <text> | apply\n");
post("[AI-Preset] ============================================\n");

// ── Initialization ───────────────────────────────────────────────────────────
// Called when live.thisdevice sends a bang (device is fully loaded).
// Outlets are guaranteed stable at this point.

function init() {
    deviceReady = true;
    post("[AI-Preset] init: device ready, checking server...\n");
    checkServer();
}

// ── Server health check ──────────────────────────────────────────────────────

function checkServer() {
    try {
        var req = new XMLHttpRequest();
        req.open("GET", API_HOST + "/health", true);
        req.onreadystatechange = function () {
            if (req.readyState === 4) {
                if (req.status === 200) {
                    serverReady = true;
                    status("Ready — engine connected");
                    post("[AI-Preset] server OK\n");
                } else {
                    serverReady = false;
                    status("Engine not running — double-click Start_Engine");
                    post("[AI-Preset] server returned " + req.status + "\n");
                }
            }
        };
        req.send();
    } catch (e) {
        serverReady = false;
        status("Engine not running — double-click Start_Engine");
        post("[AI-Preset] server unreachable: " + e.message + "\n");
    }
}

// ── Generate handler ─────────────────────────────────────────────────────────

function generate() {
    var args = arrayfromargs(arguments);
    var text = args.join(" ").replace(/^\s+|\s+$/g, "");

    if (!text || text.length === 0) {
        status("Error: empty prompt");
        return;
    }

    if (!deviceReady) {
        status("Error: device not ready");
        return;
    }

    if (!serverReady) {
        status("Connecting to engine...");
    } else {
        status("Querying...");
    }
    post("[AI-Preset] querying: " + text + "\n");

    var requestBody = JSON.stringify({
        prompt: text,
        top_k: DEFAULT_TOP_K
    });

    try {
        var req = new XMLHttpRequest();
        req.open("POST", API_HOST + API_PATH, true);
        req.setRequestHeader("Content-Type", "application/json");

        req.onreadystatechange = function () {
            if (req.readyState === 4) {
                if (req.status === 200) {
                    serverReady = true;
                    handleResponse(req.responseText);
                } else if (req.status === 0) {
                    serverReady = false;
                    status("Engine not running — double-click Start_Engine");
                    post("[AI-Preset] server unreachable\n");
                } else {
                    status("Error: HTTP " + req.status);
                    post("[AI-Preset] HTTP error " + req.status + "\n");
                }
            }
        };

        req.send(requestBody);
    } catch (e) {
        serverReady = false;
        status("Engine not running — double-click Start_Engine");
        post("[AI-Preset] request failed: " + e.message + "\n");
    }
}

// ── Response handler ─────────────────────────────────────────────────────────

function handleResponse(responseText) {
    try {
        var data = JSON.parse(responseText);
    } catch (e) {
        status("Error: invalid JSON");
        post("[AI-Preset] JSON parse error\n");
        return;
    }

    if (data.warnings && data.warnings.length > 0) {
        for (var i = 0; i < data.warnings.length; i++) {
            post("[AI-Preset] WARNING: " + data.warnings[i] + "\n");
        }
    }

    if (!data.results || data.results.length === 0) {
        status("No results found");
        lastResult = null;
        return;
    }

    var top = data.results[0];
    lastResult = top;

    status("Found: " + top.preset_name + " (" + top.score.toFixed(2) + ")");

    // Outlet 1: result data → route object → individual message boxes
    safeOutlet(1, "preset_name", "set", top.preset_name);
    safeOutlet(1, "family", "set", top.family);
    safeOutlet(1, "style_cluster", "set", top.style_cluster);
    safeOutlet(1, "device_chain", "set", top.device_chain.join(", "));
    safeOutlet(1, "score", "set", top.score.toFixed(3));

    // Outlet 2: score breakdown → display (optional, wiring not required)
    if (top.score_breakdown) {
        var bd = top.score_breakdown;
        safeOutlet(2, "family_score", bd.family.toFixed(3));
        safeOutlet(2, "style_score", bd.style_cluster.toFixed(3));
        safeOutlet(2, "tag_score", bd.tag_overlap.toFixed(3));
        safeOutlet(2, "attr_score", bd.attributes.toFixed(3));
        safeOutlet(2, "prov_score", bd.provenance_confidence.toFixed(3));
    }

    post("[AI-Preset] top result: " + top.preset_name +
         " (score " + top.score.toFixed(3) + ")\n");
}

// ── Apply handler ────────────────────────────────────────────────────────────

function apply() {
    if (!deviceReady) {
        status("Error: device not ready");
        return;
    }

    if (!lastResult) {
        status("Error: no result to apply — generate first");
        return;
    }

    var result = lastResult;

    try {
        applyParameters(result);
    } catch (e) {
        status("Error applying: " + e.message);
        post("[AI-Preset] apply error: " + e.message + "\n");
    }
}

// ── LiveAPI parameter application ────────────────────────────────────────────

function applyParameters(result) {
    var targetDeviceName = result.device_chain[0];
    if (!targetDeviceName) {
        status("Error: no target device in result");
        return;
    }

    var params = result.parameters[targetDeviceName];
    if (!params) {
        status("Error: no parameters for " + targetDeviceName);
        return;
    }

    var mapping = PARAM_MAP[targetDeviceName] || {};

    post("[AI-Preset] applying to " + targetDeviceName + "\n");

    var trackApi = new LiveAPI("live_set view selected_track");
    var trackPath = trackApi.unquotedpath;

    if (!trackPath) {
        status("Error: no track selected");
        return;
    }

    var trackForDevices = new LiveAPI(trackPath);
    var deviceCount = trackForDevices.getcount("devices");
    var deviceFound = false;

    for (var i = 0; i < deviceCount; i++) {
        var deviceApi = new LiveAPI(trackPath + " devices " + i);
        var deviceName = deviceApi.get("name").toString().replace(/"/g, "");

        if (deviceName === targetDeviceName) {
            post("[AI-Preset] found " + targetDeviceName +
                 " at device index " + i + "\n");
            applyToDevice(deviceApi, trackPath + " devices " + i,
                          params, mapping);
            deviceFound = true;
            break;
        }
    }

    if (!deviceFound) {
        status("Error: " + targetDeviceName + " not found on track");
        post("[AI-Preset] device not found on selected track\n");
        return;
    }

    status("Applied to " + targetDeviceName);
}

// ── Set individual parameters on a device ────────────────────────────────────

function applyToDevice(deviceApi, devicePath, params, mapping) {
    var paramCount = deviceApi.getcount("parameters");

    for (var key in params) {
        if (!params.hasOwnProperty(key)) continue;

        var value      = params[key];
        var abletonName = mapping[key] || key;

        for (var j = 0; j < paramCount; j++) {
            var paramApi  = new LiveAPI(devicePath + " parameters " + j);
            var paramName = paramApi.get("name").toString().replace(/"/g, "");

            if (paramName === abletonName) {
                paramApi.set("value", value);
                post("[AI-Preset]   set " + abletonName + " = " + value + "\n");
                break;
            }
        }
    }
}

// ── Utility ──────────────────────────────────────────────────────────────────
// status() is the only public outlet-0 writer.
// All other code must go through safeOutlet() or status().

function status(msg) {
    safeOutlet(0, "set", msg);
}

function bang() {
    if (!deviceReady) {
        init();
    }
}
