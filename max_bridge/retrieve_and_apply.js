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

// ── Configuration ────────────────────────────────────────────────────────────

inlets  = 1;
outlets = 3;

var API_HOST = "https://ai-preset-engine.onrender.com";
var API_PATH = "/api/retrieve";
var DEFAULT_TOP_K = 3;

// ── State ────────────────────────────────────────────────────────────────────

var deviceReady = false;
var serverReady = false;
var lastResult  = null;   // stores the most recent top result for "apply"

// ── Parameter name mapping ───────────────────────────────────────────────────
// Maps the simplified param names in our preset DB to Ableton's internal names.
// Extend per device as needed.

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

// ── Initialization ───────────────────────────────────────────────────────────
// Called when live.thisdevice sends a bang (device is fully loaded).

function init() {
    deviceReady = true;
    post("retrieve_and_apply: device initialized, checking server...\n");
    checkServer();
}

// ── Server health check ──────────────────────────────────────────────────────
// Pings GET / on the API to verify the server is running.

function checkServer() {
    try {
        var req = new XMLHttpRequest();
        req.open("GET", API_HOST + "/health", true);
        req.onreadystatechange = function () {
            if (req.readyState === 4) {
                if (req.status === 200) {
                    serverReady = true;
                    status("Ready — engine connected");
                    post("retrieve_and_apply: server OK\n");
                } else {
                    serverReady = false;
                    status("⚠ Engine not running — double-click Start_Engine");
                    post("retrieve_and_apply: server returned " + req.status + "\n");
                }
            }
        };
        req.send();
    } catch (e) {
        serverReady = false;
        status("⚠ Engine not running — double-click Start_Engine");
        post("retrieve_and_apply: server unreachable: " + e.message + "\n");
    }
}

// ── Generate handler ─────────────────────────────────────────────────────────
// Receives "generate <text>" from the Max patch (via prepend generate).

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

    // If server wasn't ready before, re-check now
    if (!serverReady) {
        status("Connecting to engine...");
    } else {
        status("Querying...");
    }
    post("retrieve_and_apply: querying \"" + text + "\"\n");

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
                    status("⚠ Engine not running — double-click Start_Engine");
                    post("retrieve_and_apply: server unreachable\n");
                } else {
                    status("Error: HTTP " + req.status);
                    post("retrieve_and_apply: HTTP error " + req.status + "\n");
                }
            }
        };

        req.send(requestBody);
    } catch (e) {
        serverReady = false;
        status("⚠ Engine not running — double-click Start_Engine");
        post("retrieve_and_apply: request failed: " + e.message + "\n");
    }
}

// ── Response handler ─────────────────────────────────────────────────────────

function handleResponse(responseText) {
    try {
        var data = JSON.parse(responseText);
    } catch (e) {
        status("Error: invalid JSON");
        post("retrieve_and_apply: JSON parse error\n");
        return;
    }

    // Check for warnings
    if (data.warnings && data.warnings.length > 0) {
        for (var i = 0; i < data.warnings.length; i++) {
            post("retrieve_and_apply WARNING: " + data.warnings[i] + "\n");
        }
    }

    // Extract top result
    if (!data.results || data.results.length === 0) {
        status("No results found");
        lastResult = null;
        return;
    }

    var top = data.results[0];
    lastResult = top;

    // Output status
    status("Found: " + top.preset_name + " (" + top.score.toFixed(2) + ")");

    // Output result data to outlet 1 (route → message boxes)
    // Each message is: <selector> set <value>
    // so that route strips the selector and "set <value>" goes to message box
    outlet(1, "preset_name", "set", top.preset_name);
    outlet(1, "family", "set", top.family);
    outlet(1, "style_cluster", "set", top.style_cluster);
    outlet(1, "device_chain", "set", top.device_chain.join(", "));
    outlet(1, "score", "set", top.score.toFixed(3));

    // Output score breakdown to outlet 2
    if (top.score_breakdown) {
        var bd = top.score_breakdown;
        outlet(2, "family_score", bd.family.toFixed(3));
        outlet(2, "style_score", bd.style_cluster.toFixed(3));
        outlet(2, "tag_score", bd.tag_overlap.toFixed(3));
        outlet(2, "attr_score", bd.attributes.toFixed(3));
        outlet(2, "prov_score", bd.provenance_confidence.toFixed(3));
    }

    post("retrieve_and_apply: top result = " + top.preset_name +
         " (score " + top.score.toFixed(3) + ")\n");
}

// ── Apply handler ────────────────────────────────────────────────────────────
// Called when the user clicks the "Apply" button.
// Uses LiveAPI to set parameters on the target device.

function apply() {
    if (!deviceReady) {
        status("Error: device not ready");
        return;
    }

    if (!lastResult) {
        status("Error: no result to apply");
        return;
    }

    // Defer LiveAPI work off the scheduler thread
    var result = lastResult;

    try {
        applyParameters(result);
    } catch (e) {
        status("Error applying: " + e.message);
        post("retrieve_and_apply: apply error: " + e.message + "\n");
    }
}

// ── LiveAPI parameter application ────────────────────────────────────────────
// Finds the target device on the current track and sets parameter values.
//
// MVP: applies to the first device matching the target name (e.g. "Wavetable").
// Does NOT instantiate new devices.

function applyParameters(result) {
    // Determine target device name (first in device_chain)
    var targetDeviceName = result.device_chain[0];
    if (!targetDeviceName) {
        status("Error: no target device in result");
        return;
    }

    // Get parameter values for the target device
    var params = result.parameters[targetDeviceName];
    if (!params) {
        status("Error: no parameters for " + targetDeviceName);
        return;
    }

    // Get the parameter name mapping for this device
    var mapping = PARAM_MAP[targetDeviceName] || {};

    post("retrieve_and_apply: applying to " + targetDeviceName + "\n");

    // ── Navigate to the current track's devices ──
    // LiveAPI must NOT be called in global scope.
    // This function is only called after init() confirms deviceReady.

    var trackApi = new LiveAPI("live_set view selected_track");
    var trackPath = trackApi.unquotedpath;

    if (!trackPath) {
        status("Error: no track selected");
        return;
    }

    // Count devices on this track
    var devicesApi = new LiveAPI(trackPath + " devices");
    // LiveAPI children count approach:
    var trackForDevices = new LiveAPI(trackPath);
    var deviceCount = trackForDevices.getcount("devices");

    var deviceFound = false;

    for (var i = 0; i < deviceCount; i++) {
        var deviceApi = new LiveAPI(trackPath + " devices " + i);
        var deviceName = deviceApi.get("name").toString().replace(/"/g, "");

        if (deviceName === targetDeviceName) {
            post("retrieve_and_apply: found " + targetDeviceName +
                 " at device index " + i + "\n");

            // Apply each parameter
            applyToDevice(deviceApi, trackPath + " devices " + i,
                          params, mapping);
            deviceFound = true;
            break;
        }
    }

    if (!deviceFound) {
        status("Error: " + targetDeviceName + " not found on track");
        post("retrieve_and_apply: device not found on selected track\n");
        return;
    }

    status("Applied to " + targetDeviceName);
}

// ── Set individual parameters on a device ────────────────────────────────────

function applyToDevice(deviceApi, devicePath, params, mapping) {
    // Get parameter count
    var paramCount = deviceApi.getcount("parameters");

    for (var key in params) {
        if (!params.hasOwnProperty(key)) continue;

        var value = params[key];
        var abletonName = mapping[key] || key;  // fallback to raw name

        // Search for the matching parameter
        for (var j = 0; j < paramCount; j++) {
            var paramApi = new LiveAPI(devicePath + " parameters " + j);
            var paramName = paramApi.get("name").toString().replace(/"/g, "");

            if (paramName === abletonName) {
                paramApi.set("value", value);
                post("retrieve_and_apply:   set " + abletonName +
                     " = " + value + "\n");
                break;
            }
        }
    }
}

// ── Utility ──────────────────────────────────────────────────────────────────

function status(msg) {
    outlet(0, "set", msg);
}

function bang() {
    // A bang on inlet triggers init if not already done
    if (!deviceReady) {
        init();
    }
}
