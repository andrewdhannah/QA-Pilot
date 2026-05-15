// build.js — QA Pilot Desktop bundler
//
// Produces three outputs from the modular source files:
//
//   1. os.bundle.js  — dev bundle loaded by index.html during development
//                      (requires a local file server or DevTools cache-disabled)
//
//   2. dist.html     — single self-contained file, fully offline
//                      Safe for file://, OneNote embeds, USB, SharePoint, email.
//                      No external requests — everything is inlined.
//
//   3. capstone.html — auto-synced after each build.
//                      The QA Pilot Academy lesson platform (one level up) uses
//                      capstone.html to embed the OS as a full-screen srcdoc iframe.
//                      This step replaces the getOSContent() return value with the
//                      freshly-built dist.html so both are always in sync.
//                      If capstone.html is not found (e.g. standalone OS repo),
//                      this step is silently skipped.
//
// Run with:  node build.js

const fs   = require("fs");
const path = require("path");

// ─── Paths ────────────────────────────────────────────────────────────────────
const ROOT           = __dirname;
const APPS_DIR       = path.join(ROOT, "apps");
const SCENARIOS_DIR  = path.join(ROOT, "scenarios");
const CORE_PATH      = path.join(ROOT, "src", "os-core.js");
const CSS_PATH       = path.join(ROOT, "os.css");
const INDEX_PATH     = path.join(ROOT, "index.html");
const BUNDLE_OUT     = path.join(ROOT, "os.bundle.js");
const DIST_OUT       = path.join(ROOT, "dist.html");
// capstone.html lives one level up in the Academy root.
// When the desktop/ folder is inside the combined QA Pilot project, this path
// resolves to the lesson platform's capstone.html automatically.
const CAPSTONE_PATH  = path.join(ROOT, "..", "capstone.html");

// ─── Read + embed app HTML files ─────────────────────────────────────────────
// Each .html file in /apps is read and stored in APP_HTML keyed by its
// filename (lowercase, no extension) so it matches the app IDs in os-core.js.
//
// BUG FIX: previously "Ado.html" produced key "Ado" but the engine
//          looks for "ado" — .toLowerCase() ensures they always match.
function readApps() {
  const files = fs.readdirSync(APPS_DIR).filter((f) => f.endsWith(".html"));
  const appHtml = {};

  for (const file of files) {
    // Normalise key to lowercase so it matches APPS{} in os-core.js
    const id   = path.basename(file, ".html").toLowerCase();
    const full = path.join(APPS_DIR, file);
    let   html = fs.readFileSync(full, "utf8");

    // Step 1 — pull out <script> blocks so we never escape their internals
    const scripts = [];
    html = html.replace(/<script[\s\S]*?<\/script>/gi, (block) => {
      scripts.push(block);
      return `__SCRIPT_BLOCK_${scripts.length - 1}__`;
    });

    // Step 2 — escape special template-literal chars in the non-script HTML
    html = html
      .replace(/\\/g,   "\\\\")  // backslash first (order matters)
      .replace(/`/g,    "\\`")   // backtick
      .replace(/\$\{/g, "\\${"); // template placeholder

    // Step 3 — restore the untouched script blocks
    html = html.replace(/__SCRIPT_BLOCK_(\d+)__/g, (_, i) => scripts[i]);

    appHtml[id] = html;
  }

  return appHtml;
}

// ─── Read + combine scenario JS files ────────────────────────────────────────
// Each scenario file already contains its own  window.SCENARIOS = ... || {}
// guard, so we do NOT add a duplicate header here.
function readScenarios() {
  if (!fs.existsSync(SCENARIOS_DIR)) return "";

  const files = fs.readdirSync(SCENARIOS_DIR).filter((f) => f.endsWith(".js"));

  // CRITICAL: initialise the registry BEFORE any scenario file tries to write
  // to it.  Without this, `window.SCENARIOS["case-001"] = ...` throws
  // `TypeError: Cannot set properties of undefined` and the entire script
  // crashes — locking the UI (frozen clock, unclickable lock screen, etc.).
  let combined = "// Scenario registry — must exist before individual scenario files run.\n";
  combined    += "window.SCENARIOS = window.SCENARIOS || {};\n\n";

  for (const file of files) {
    const full = path.join(SCENARIOS_DIR, file);
    combined += fs.readFileSync(full, "utf8") + "\n";
  }

  return combined;
}

// ─── Build ────────────────────────────────────────────────────────────────────
function build() {
  const core       = fs.readFileSync(CORE_PATH,  "utf8");
  const css        = fs.readFileSync(CSS_PATH,   "utf8");
  const indexHtml  = fs.readFileSync(INDEX_PATH, "utf8");
  const apps       = readApps();
  const scenariosJs = readScenarios();

  // APP_HTML is declared as a plain const so os-core.js can reference it
  const appHtmlDecl = "const APP_HTML = " + JSON.stringify(apps, null, 2) + ";\n";

  // Wrap os-core.js in an IIFE so its variables don't pollute the global scope
  const wrappedCore = "(function(){\n" + core + "\n})();\n";

  // ── Output 1: os.bundle.js (for local dev with index.html) ────────────────
  const bundleContent =
    "// os.bundle.js — generated by build.js — do not edit by hand\n\n" +
    appHtmlDecl + "\n" +
    scenariosJs + "\n" +
    wrappedCore;

  fs.writeFileSync(BUNDLE_OUT, bundleContent, "utf8");
  console.log("✓ Built:", BUNDLE_OUT);

  // ── Output 2: dist.html (single self-contained file) ─────────────────────
  // This file has zero external dependencies — safe to open via file://
  // or embed in OneNote because the browser never needs to make a network
  // (or local-filesystem) request for a secondary resource.
  const inlineStyle  = "<style>\n"  + css + "\n</style>";

  // IMPORTANT: when JS is inlined inside an HTML <script> tag, the browser's
  // HTML parser scans the raw text for </script> to find the end of the block.
  // Any </script> inside our JSON strings (from the app HTML files) would
  // terminate the script prematurely → black screen.
  // Fix: replace every </script with <\/script — the HTML parser won't match
  // it but the JS engine treats the forward-slash as harmless.
  const safeJs = (appHtmlDecl + "\n" + scenariosJs + "\n" + wrappedCore)
    .replace(/<\/script/gi, "<\\/script");

  const inlineScript = "<script>\n" + safeJs + "\n</script>";

  // Replace <link rel="stylesheet" href="os.css" …> with the inlined CSS
  let distHtml = indexHtml.replace(
    /<link[^>]+href=["']os\.css["'][^>]*\/?>/i,
    inlineStyle
  );

  // Replace <script src="os.bundle.js"></script> with the inlined JS
  distHtml = distHtml.replace(
    /<script[^>]+src=["']os\.bundle\.js["'][^>]*><\/script>/i,
    inlineScript
  );

  fs.writeFileSync(DIST_OUT, distHtml, "utf8");
  console.log("✓ Built:", DIST_OUT);

  // ── Output 3: sync capstone.html with current OS content ─────────────────
  // capstone.html (in the Academy root, one level up) embeds the OS as a
  // full-screen srcdoc iframe via a getOSContent() function that returns the
  // complete dist.html as a JS template-literal string.
  //
  // This step keeps them in sync automatically — no more manual copy-paste.
  // If capstone.html is not found (standalone OS install), we skip gracefully.
  if (fs.existsSync(CAPSTONE_PATH)) {

    let capstone = fs.readFileSync(CAPSTONE_PATH, "utf8");

    // Escape dist.html so it can live safely inside a JS template literal.
    // Order matters: backslashes must be escaped FIRST before we add new ones.
    const escapedDist = distHtml
      .replace(/\\/g,   "\\\\")   // 1. escape existing backslashes
      .replace(/`/g,    "\\`")    // 2. escape backticks (template delimiter)
      .replace(/\$\{/g, "\\${")   // 3. escape ${ (template placeholder opener)
      .replace(/<\//g,  "<\\/");  // 4. escape </ so inner </script> doesn't close the outer script tag

    // Target: everything between the BUILD:OS_START and BUILD:OS_END marker comments.
    // These markers are in capstone.html and survive all future edits to the function.
    // The regex replaces the entire function body between the markers, so the format
    // of getOSContent() (template literal, string concat, etc.) never matters.
    //
    // Use indexOf (not regex) to locate the markers. A regex applied to a
    // multi-thousand-line file containing arbitrary HTML/JS can silently
    // fail when the captured content contains regex special characters or
    // when the start/end positions don't satisfy the greedy match rules.
    // indexOf is exact and gives clear "not found" (-1) semantics.
    //
    // Marker format in capstone.html:
    //   /* BUILD:OS_START */
    //   function getOSContent() { return `...`; }
    //   /* BUILD:OS_END */
    const START_MARKER = "/* BUILD:OS_START */";
    const END_MARKER   = "/* BUILD:OS_END */";

    const startIdx = capstone.indexOf(START_MARKER);
    // Search for END_MARKER starting AFTER start so we never match an
    // END_MARKER that appears before START_MARKER in an unexpected layout.
    const endIdx   = capstone.indexOf(END_MARKER, startIdx + 1);

    if (startIdx === -1 || endIdx === -1 || endIdx <= startIdx) {
      console.warn("⚠  capstone.html sync skipped — BUILD:OS_START / BUILD:OS_END markers not found.");
      console.warn("   Add these comment markers around the getOSContent() function in capstone.html.");
    } else {
      const replacement =
        "/* BUILD:OS_START */\n" +
        "        function getOSContent() {\n" +
        "            // Auto-updated by desktop/build.js on every `node build.js` run.\n" +
        "            // Do not edit between the BUILD:OS_START and BUILD:OS_END markers.\n" +
        "            return `" + escapedDist + "`;\n" +
        "        }\n" +
        "        /* BUILD:OS_END */";

      const newContent =
        capstone.substring(0, startIdx) +
        replacement +
        capstone.substring(endIdx + END_MARKER.length);

      fs.writeFileSync(CAPSTONE_PATH, newContent, "utf8");
      console.log("✓ Synced: capstone.html (getOSContent updated with current OS build)");
    }

  } else {
    console.log("ℹ  capstone.html not found at:", CAPSTONE_PATH);
    console.log("   This is expected if running the OS standalone (no Academy folder above).");
    console.log("   Move desktop/ inside the QA Pilot Academy root to enable auto-sync.");
  }

  console.log("\n✓ QA Pilot Desktop build complete.");
  console.log("  → dist.html   : share this file (fully self-contained)");
  console.log("  → os.bundle.js: use with index.html for local development");
}

build();
