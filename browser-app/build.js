// build.js — QA Pilot Desktop bundler
//
// Produces three outputs from the modular source files:
//
//   1. os.bundle.js  — dev bundle loaded by desktop/index.html during development
//                      (requires a local file server or DevTools cache-disabled)
//
//   2. QASimulator.html — single self-contained file, fully offline
//                      Safe for file://, OneNote embeds, USB, SharePoint, email.
//                      No external requests — everything is inlined.
//
//   3. capstone.html — auto-synced after each build (getOSContent updated).
//
// Run with:  node build.js

const fs   = require("fs");
const path = require("path");

// ─── Paths (all relative to QA Pilot root) ────────────────────────────────────
const ROOT           = __dirname;
const APPS_DIR       = path.join(ROOT, "apps");
const SCENARIOS_DIR  = path.join(ROOT, "scenarios");
const CORE_PATH      = path.join(ROOT, "src", "os-core.js");
const EVENT_BUS_PATH = path.join(ROOT, "src", "event-bus.js");
const COMPOSITOR_PATH= path.join(ROOT, "src", "compositor.js");
const WORKSPACES_PATH= path.join(ROOT, "src", "workspaces.js");
const CSS_PATH       = path.join(ROOT, "os.css");
// OS HTML template (lock screen, desktop, taskbar shell skeleton)
const INDEX_PATH     = path.join(ROOT, "desktop", "index.html");
// Shared db.js — loaded via <script src="js/db.js"> in QASimulator.html output
const DB_PATH = path.join(ROOT, "js", "db.js");
// Centralized bug key constants — loaded before scenarios in both outputs
const BUG_KEYS_PATH = path.join(ROOT, "data", "bug-keys.js");
const SCORING_PATH   = path.join(ROOT, "src", "scoring.js");
const HEALTH_PATH    = path.join(ROOT, "src", "health-checks.js");
const SHORTCUTS_PATH = path.join(ROOT, "src", "keyboard-shortcuts.js");
const BUNDLE_OUT     = path.join(ROOT, "os.bundle.js");
const DIST_OUT       = path.join(ROOT, "QASimulator.html");
// Desktop copies — for desktop/index.html dev workflow (OS loads os.bundle.js relative)
const DESKTOP_BUNDLE_OUT = path.join(ROOT, "desktop", "os.bundle.js");
const DESKTOP_DIST_OUT   = path.join(ROOT, "desktop", "dist.html");
const CAPSTONE_PATH   = path.join(ROOT, "capstone.html");
const CAPSTONE2_PATH  = path.join(ROOT, "capstone-2.html");

// ─── Read + embed app HTML files ─────────────────────────────────────────────
// Each .html file in /apps is read and stored in APP_HTML keyed by its
// filename (lowercase, no extension) so it matches the app IDs in os-core.js.
//
// BUG FIX: previously "Ado.html" produced key "Ado" but the engine
//          looks for "ado" — .toLowerCase() ensures they always match.
function readApps() {
  const files = fs.readdirSync(APPS_DIR).filter((f) => f.endsWith(".html"));
  const appHtml = {};

  // Pre-read sprite images for inlining into QTube
  const VIDEOS_DIR = path.join(ROOT, "desktop", "videos");
  const spriteCache = {};
  if (fs.existsSync(VIDEOS_DIR)) {
    const spriteFiles = fs.readdirSync(VIDEOS_DIR).filter((f) => f.endsWith(".png"));
    for (const sf of spriteFiles) {
      const fullPath = path.join(VIDEOS_DIR, sf);
      const data = fs.readFileSync(fullPath);
      spriteCache[sf] = "data:image/png;base64," + data.toString("base64");
    }
  }

  for (const file of files) {
    // Normalise key to lowercase so it matches APPS{} in os-core.js
    const id   = path.basename(file, ".html").toLowerCase();
    const full = path.join(APPS_DIR, file);
    let   html = fs.readFileSync(full, "utf8");

    // Inline sprite images as base64 data URIs for srcdoc iframe compatibility
    if (spriteCache) {
      html = html.replace(/url\(['"]?videos\/([^'")]+)['"]?\)/gi, function (match, filename) {
        if (spriteCache[filename]) {
          return "url('" + spriteCache[filename] + "')";
        }
        return match;
      });
    }

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

// ─── Architecture layers (read if they exist) ──────────────────────────────────
function readArchLayer(filePath, label) {
  if (fs.existsSync(filePath)) {
    return fs.readFileSync(filePath, "utf8") + "\n";
  }
  console.warn("⚠  " + label + " not found at:", filePath);
  return "// " + label + " not found — skipped\n";
}

// ─── Build ────────────────────────────────────────────────────────────────────
function build() {
  const core        = fs.readFileSync(CORE_PATH,  "utf8");
  const css         = fs.readFileSync(CSS_PATH,   "utf8");
  const indexHtml   = fs.readFileSync(INDEX_PATH, "utf8");
  const apps        = readApps();
  const scenariosJs = readScenarios();
  const dbJs = fs.existsSync(DB_PATH)
              ? fs.readFileSync(DB_PATH, "utf8")
              : "// db.js not found — IndexedDB bridge disabled\n";

// Read centralized bug keys (declares window.BUG_KEYS)
const bugKeysJs = fs.existsSync(BUG_KEYS_PATH)
                  ? fs.readFileSync(BUG_KEYS_PATH, "utf8") + "\n"
                  : "// bug-keys.js not found — BUG_KEYS unavailable\n";

// Bug 1: Read scoring.js
const scoringJs = fs.existsSync(SCORING_PATH)
                    ? fs.readFileSync(SCORING_PATH, "utf8") + "\n"
                    : "// scoring.js not found — scoring disabled\n";

// Read health-checks.js
const healthJs = fs.existsSync(HEALTH_PATH)
                    ? fs.readFileSync(HEALTH_PATH, "utf8") + "\n"
                    : "// health-checks.js not found\n";

// Read keyboard-shortcuts.js
const shortcutsJs = fs.existsSync(SHORTCUTS_PATH)
                    ? fs.readFileSync(SHORTCUTS_PATH, "utf8") + "\n"
                    : "// keyboard-shortcuts.js not found\n";

// Architecture layers — loaded in dependency order
const eventBusJs    = readArchLayer(EVENT_BUS_PATH,  "event-bus.js");
  const compositorJs  = readArchLayer(COMPOSITOR_PATH, "compositor.js");
  const workspacesJs  = readArchLayer(WORKSPACES_PATH, "workspaces.js");

  // APP_HTML is declared as a plain const so os-core.js can reference it
  const appHtmlDecl = "const APP_HTML = " + JSON.stringify(apps, null, 2) + ";\n";

  // Wrap os-core.js in an IIFE so its variables don't pollute the global scope
  const wrappedCore = "(function(){\n" + core + "\n})();\n";

   // ── Output 1: os.bundle.js (for local dev with index.html) ────────────────
   const bundleContent =
     "// os.bundle.js — generated by build.js — do not edit by hand\n\n" +
     dbJs        + "\n" +   // Academy IndexedDB layer
     bugKeysJs   + "\n" +   // Centralized bug key constants (before scenarios)
     eventBusJs  + "\n" +   // Event Bus — decoupled pub/sub
     compositorJs+ "\n" +   // Compositor — window layout engine
     workspacesJs+ "\n" +   // Workspaces — IndexedDB session persistence
     appHtmlDecl + "\n" +
     scenariosJs + "\n" +
     wrappedCore + "\n" +
     scoringJs   + "\n" +   // from C10
     shortcutsJs + "\n" +   // ← ADD (before health — shortcuts must exist for health to check)
     healthJs;              // ← ADD (last — checks all the above)

  fs.writeFileSync(BUNDLE_OUT, bundleContent, "utf8");
  console.log("✓ Built:", BUNDLE_OUT);

   // ── Output 2: QASimulator.html (single self-contained file) ──────────────
   // This file has zero external dependencies — safe to open via file://
   // or embed in OneNote because the browser never needs to make a network
   // (or local-filesystem) request for a secondary resource.
   // db.js is NOT inlined — it's loaded via <script src="js/db.js"> so it can
   // be shared between the course pages and the OS shell.
   const inlineStyle  = "<style>\n"  + css + "\n</style>";

   // IMPORTANT: when JS is inlined inside an HTML <script> tag, the browser's
   // HTML parser scans the raw text for </script> to find the end of the block.
   // Any </script> inside our JSON strings (from the app HTML files) would
   // terminate the script prematurely → black screen.
   // Fix: replace every </script with <\/script — the HTML parser won't match
   // it but the JS engine treats the forward-slash as harmless.
   // NOTE: dbJs is NOT included here — it loads externally as a script tag.
   // bugKeysJs IS included here (inlined) so BUG_KEYS is available before scenarios.
   const safeJs = (bugKeysJs + "\n" + eventBusJs + "\n" + compositorJs + "\n" + workspacesJs + "\n" + appHtmlDecl + "\n" + scenariosJs + "\n" + wrappedCore + "\n" + scoringJs + "\n" + shortcutsJs + "\n" + healthJs)
     .replace(/<\/script/gi, "<\\/script");

    const inlineScript = "<script>\n" + safeJs + "\n</script>";
    const dbScriptTag  = '<script src="js/db.js"><\/script>';
    const i18nScriptTags = '<script src="js/i18n.js"><\/script>\n' +
                           '    <script src="js/lang-en.js"><\/script>\n' +
                           '    <script src="js/lang-fr.js"><\/script>';

    // Replace <link rel="stylesheet" href="os.css" …> with the inlined CSS
    let distHtml = indexHtml.replace(
      /<link[^>]+href=["']os\.css["'][^>]*\/?>/i,
      inlineStyle
    );

    // Inject i18n scripts and shared db.js script tag in the <head>
    distHtml = distHtml.replace(
      /(<\/head>)/i,
      '  ' + i18nScriptTags + '\n  ' + dbScriptTag + '\n$1'
    );

    // Replace <script src="os.bundle.js"></script> with the inlined JS
    // IMPORTANT: use a function callback, NOT a string — the inlined JS
    // contains $&, $`, $' patterns (regex replacement strings in app HTML)
    // which String.prototype.replace() interprets as special patterns.
    distHtml = distHtml.replace(
      /<script[^>]+src=["']os\.bundle\.js["'][^>]*><\/script>/i,
      function() { return inlineScript; }
    );

   fs.writeFileSync(DIST_OUT, distHtml, "utf8");
   console.log("✓ Built:", DIST_OUT);

   // ── Output 2b: desktop/ copies for dev workflow ─────────────────────────
   // desktop/index.html loads os.bundle.js relative, so it needs a copy there.
   // desktop/dist.html is the canonical dist file for the Open Work / built-in browser.
   fs.writeFileSync(DESKTOP_BUNDLE_OUT, bundleContent, "utf8");
   console.log("✓ Built:", DESKTOP_BUNDLE_OUT);
   // Fix db.js path for desktop/ subdirectory — use ../js/db.js to reach root
   const desktopDistHtml = distHtml.replace(
     '<script src="js/db.js">',
     '<script src="../js/db.js">'
   );
   fs.writeFileSync(DESKTOP_DIST_OUT, desktopDistHtml, "utf8");
   console.log("✓ Built:", DESKTOP_DIST_OUT);

  // ── Output 3: sync capstone pages with current OS content ──────────────
  // capstone.html and capstone-2.html embed the OS as a full-screen srcdoc
  // iframe via a getOSContent() function that returns the complete dist.html
  // as a JS template-literal string.
  //
  // This step keeps them in sync automatically — no more manual copy-paste.
  // If a file is not found (standalone OS install), we skip gracefully.
  const START_MARKER = "/* BUILD:OS_START */";
  const END_MARKER   = "/* BUILD:OS_END */";

  // Escape dist.html so it can live safely inside a JS template literal.
  // Order matters: backslashes must be escaped FIRST before we add new ones.
  const escapedDist = distHtml
    .replace(/\\/g,   "\\\\")   // 1. escape existing backslashes
    .replace(/`/g,    "\\`")    // 2. escape backticks (template delimiter)
    .replace(/\$\{/g, "\\${")   // 3. escape ${ (template placeholder opener)
    .replace(/<\//g,  "<\\/");  // 4. escape </ so inner </script> doesn't close the outer script tag

  /**
   * syncCapstonePage(path, indent)
   *
   * Replaces the OS content between BUILD:OS_START and BUILD:OS_END markers
   * in a capstone HTML file with the freshly-built dist.html.
   *
   * @param {string} filePath - Absolute path to the capstone HTML file.
   * @param {string} indent   - Whitespace indentation for the getOSContent()
   *                            function declaration (e.g. "        " for 8 spaces).
   */
  function syncCapstonePage(filePath, indent) {
    if (!fs.existsSync(filePath)) {
      console.log("ℹ  " + path.basename(filePath) + " not found at:", filePath);
      return;
    }

    let content = fs.readFileSync(filePath, "utf8");

    const startIdx = content.indexOf(START_MARKER);
    const endIdx   = content.indexOf(END_MARKER, startIdx + 1);

    if (startIdx === -1 || endIdx === -1 || endIdx <= startIdx) {
      console.warn("⚠  " + path.basename(filePath) + " sync skipped — BUILD:OS markers not found.");
      console.warn("   Add these comment markers around the getOSContent() function.");
      return;
    }

    const bodyIndent = indent + "    "; // 4 more spaces for the return statement

    const replacement =
      START_MARKER + "\n" +
      indent + "function getOSContent() {\n" +
      bodyIndent + "// Auto-updated by build.js on every `node build.js` run.\n" +
      bodyIndent + "// Do not edit between the BUILD:OS_START and BUILD:OS_END markers.\n" +
      bodyIndent + "return `" + escapedDist + "`;\n" +
      indent + "}\n" +
      indent + END_MARKER;

    const newContent =
      content.substring(0, startIdx) +
      replacement +
      content.substring(endIdx + END_MARKER.length);

    fs.writeFileSync(filePath, newContent, "utf8");
    console.log("✓ Synced: " + path.basename(filePath) + " (getOSContent updated with current OS build)");
  }

  syncCapstonePage(CAPSTONE_PATH,  "        ");  // 8 spaces
  syncCapstonePage(CAPSTONE2_PATH, "                    "); // 20 spaces

  console.log("\n✓ QA Pilot Desktop build complete.");
  console.log("  → QASimulator.html   : share this file (fully self-contained)");
  console.log("  → os.bundle.js       : use with desktop/index.html for local development");
}

build();
