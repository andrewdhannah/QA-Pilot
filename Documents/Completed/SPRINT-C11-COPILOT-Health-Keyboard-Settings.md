# Sprint C-11 — OBD2 Health Checks + Keyboard Shortcut Registry + Settings Panel
## Copilot Prompt — GitHub repo: andrewdhannah/QA-Pilot

You are working in the QA Pilot repository.
No CDN links, no external imports, no fetch(). File:// safe architecture.
Run `node build.js` from the `desktop/` folder after making changes.

**Prerequisites:** SPRINT-C10 must be merged and the build must be current.
This sprint adds three tightly coupled systems. Implement them in the order listed.

---

## Overview

This sprint wires two new runtime systems into the OS shell:

1. **Health Check Registry** (`src/health-checks.js`) — An OBD2-style self-diagnostic
   engine. On boot it silently tests every critical subsystem. Any failure surfaces as
   a toast notification — no developer tools, no console, no log file required. A full
   diagnostics panel (`Ctrl+Shift+D`) shows every check with pass/fail/warn status.

2. **Keyboard Shortcut Registry** (`src/keyboard-shortcuts.js`) — A single source of
   truth for all keyboard shortcuts. The keydown handler is driven by this registry;
   the Settings app reads the same registry to render a "Keyboard Shortcuts" reference
   panel. Adding a shortcut in one place wires the behaviour AND documents it.

3. **Settings "Keyboard Shortcuts" panel** — A new sidebar section in `apps/settings.html`
   that reads `window.parent.QA_SHORTCUTS.getAll()` and renders shortcuts grouped by
   category, styled to match the existing Settings design.

---

## Part 1 — `src/health-checks.js`

Create `desktop/src/health-checks.js`. This file defines `window.QA_HEALTH`.

### Structure

```javascript
/**
 * health-checks.js — OBD2-style runtime self-diagnostic engine
 * ============================================================
 * QA Pilot OS — Sprint C11
 *
 * Exposes: window.QA_HEALTH
 *
 * Usage (called from os-core.js init()):
 *   window.QA_HEALTH.runBoot();        // critical checks only, toasts on failure
 *   window.QA_HEALTH.openPanel();      // full diagnostics overlay (Ctrl+Shift+D)
 *
 * Adding a new check:
 *   Push an entry to CHECKS. Set critical:true if the OS cannot function without it.
 */

(function() {
  "use strict";

  // ── SECTION 1: CHECK DEFINITIONS ─────────────────────────────────────────────
  // Each check: { id, name, critical, test: fn→bool, failMsg }
  // test() must be synchronous and side-effect-free.
  // critical:true → failure toasts on boot and shows 🔴 in the panel.
  // critical:false → failure shows 🟡 (warning) in the panel only.

  var CHECKS = [

    // ── Scoring engine ──────────────────────────────────────────────────────────
    {
      id:       "scoring-loaded",
      name:     "Scoring engine (scoring.js bundled)",
      critical: true,
      test:     function() { return typeof window.evaluateSubmission === "function"; },
      failMsg:  "scoring.js not bundled — Submit for Certification will silently fail.",
    },

    // ── Architecture layers ─────────────────────────────────────────────────────
    {
      id:       "eventbus-loaded",
      name:     "EventBus (event-bus.js bundled)",
      critical: true,
      test:     function() {
        return typeof window.EventBus !== "undefined" &&
               typeof window.EventBus.emit === "function";
      },
      failMsg:  "EventBus not found — inter-module messaging will not work.",
    },
    {
      id:       "compositor-loaded",
      name:     "Compositor (compositor.js bundled)",
      critical: true,
      test:     function() {
        return typeof window.QA_COMPOSITOR !== "undefined" &&
               typeof window.QA_COMPOSITOR.openWindow === "function";
      },
      failMsg:  "Compositor not found — windows cannot be opened.",
    },
    {
      id:       "workspaces-loaded",
      name:     "Workspaces (workspaces.js bundled)",
      critical: false,
      test:     function() {
        return typeof window.QA_WORKSPACES !== "undefined";
      },
      failMsg:  "Workspaces not found — session save/restore unavailable.",
    },
    {
      id:       "db-loaded",
      name:     "Academy DB bridge (db.js bundled)",
      critical: false,
      test:     function() {
        return typeof window.QA_DB !== "undefined";
      },
      failMsg:  "DB bridge not found — IndexedDB result writes will fail.",
    },

    // ── OS state ────────────────────────────────────────────────────────────────
    {
      id:       "qa-os-exposed",
      name:     "QA_OS global API exposed",
      critical: true,
      test:     function() {
        return typeof window.QA_OS !== "undefined" &&
               typeof window.QA_OS.openApp === "function";
      },
      failMsg:  "QA_OS not found — app iframes cannot communicate with the OS.",
    },
    {
      id:       "app-html-loaded",
      name:     "APP_HTML bundle (app HTML declared)",
      critical: true,
      test:     function() {
        return typeof window.APP_HTML !== "undefined" &&
               Object.keys(window.APP_HTML).length > 0;
      },
      failMsg:  "APP_HTML empty — no apps will open.",
    },
    {
      id:       "scenarios-loaded",
      name:     "Scenarios data (SCENARIOS declared)",
      critical: false,
      test:     function() {
        return typeof window.SCENARIOS !== "undefined" &&
               Object.keys(window.SCENARIOS).length > 0;
      },
      failMsg:  "SCENARIOS not found — capstone mode will not work.",
    },

    // ── Required apps registered ────────────────────────────────────────────────
    {
      id:       "app-dynamics-registered",
      name:     "Dynamics CRM app registered",
      critical: false,
      test:     function() {
        return typeof window.APP_HTML !== "undefined" &&
               !!window.APP_HTML["dynamics"];
      },
      failMsg:  "dynamics app not in APP_HTML bundle.",
    },
    {
      id:       "app-ado-registered",
      name:     "Azure DevOps app registered",
      critical: false,
      test:     function() {
        return typeof window.APP_HTML !== "undefined" &&
               !!window.APP_HTML["ado"];
      },
      failMsg:  "ado app not in APP_HTML bundle.",
    },
    {
      id:       "app-browser-registered",
      name:     "Browser app registered",
      critical: false,
      test:     function() {
        return typeof window.APP_HTML !== "undefined" &&
               !!window.APP_HTML["browser"];
      },
      failMsg:  "browser app not in APP_HTML bundle.",
    },

    // ── DOM shell elements ──────────────────────────────────────────────────────
    {
      id:       "dom-taskbar",
      name:     "Taskbar element present",
      critical: true,
      test:     function() { return !!document.querySelector(".qa-taskbar"); },
      failMsg:  "Taskbar (.qa-taskbar) not found in DOM.",
    },
    {
      id:       "dom-workspace",
      name:     "Workspace element present",
      critical: true,
      test:     function() { return !!document.querySelector(".qa-workspace"); },
      failMsg:  "Workspace (.qa-workspace) not found in DOM.",
    },
    {
      id:       "dom-start-menu",
      name:     "Start menu element present",
      critical: false,
      test:     function() { return !!document.querySelector(".qa-start-menu"); },
      failMsg:  "Start menu element not found — Start button may not work.",
    },
    {
      id:       "dom-notify-centre",
      name:     "Notification centre element present",
      critical: false,
      test:     function() { return !!document.getElementById("qa-notify-centre"); },
      failMsg:  "Notification centre not found.",
    },

    // ── Storage availability ────────────────────────────────────────────────────
    {
      id:       "localstorage-available",
      name:     "localStorage available",
      critical: false,
      test:     function() {
        try {
          localStorage.setItem("_qa_health_probe", "1");
          localStorage.removeItem("_qa_health_probe");
          return true;
        } catch(e) { return false; }
      },
      failMsg:  "localStorage not available — theme/state persistence will fail.",
    },
    {
      id:       "indexeddb-available",
      name:     "IndexedDB available",
      critical: false,
      test:     function() { return typeof indexedDB !== "undefined"; },
      failMsg:  "IndexedDB not available — workspace save/restore will fail.",
    },

    // ── Keyboard shortcut registry ──────────────────────────────────────────────
    {
      id:       "shortcuts-loaded",
      name:     "Keyboard shortcut registry loaded",
      critical: false,
      test:     function() {
        return typeof window.QA_SHORTCUTS !== "undefined" &&
               typeof window.QA_SHORTCUTS.getAll === "function";
      },
      failMsg:  "keyboard-shortcuts.js not bundled — shortcuts and Settings panel unavailable.",
    },

  ];


  // ── SECTION 2: RUNNER ────────────────────────────────────────────────────────

  /**
   * run(options)
   * Runs all checks (or only critical ones if options.criticalOnly is true).
   * Returns array of result objects: { id, name, critical, passed, failMsg }
   */
  function run(options) {
    var opts    = options || {};
    var subset  = opts.criticalOnly
      ? CHECKS.filter(function(c) { return c.critical; })
      : CHECKS;

    return subset.map(function(check) {
      var passed = false;
      try { passed = !!check.test(); } catch(e) { passed = false; }
      return {
        id:       check.id,
        name:     check.name,
        critical: check.critical,
        passed:   passed,
        failMsg:  check.failMsg,
      };
    });
  }


  // ── SECTION 3: BOOT RUNNER ───────────────────────────────────────────────────

  /**
   * runBoot()
   * Runs critical checks only. For each failure, fires a toast via EventBus.
   * Silent if all critical checks pass (no "All systems go" message on success —
   * a healthy OS should feel quiet, like a car that doesn't beep when nothing is wrong).
   * Called from os-core.js init() after all modules are initialised.
   */
  function runBoot() {
    var results = run({ criticalOnly: true });
    results.forEach(function(r) {
      if (!r.passed) {
        // Use EventBus if available, fall back to console
        if (typeof window.EventBus !== "undefined" && window.EventBus.emit) {
          window.EventBus.emit("notify", "🔴 " + r.name + " — " + r.failMsg);
        } else {
          // EventBus itself may be the thing that failed — last resort
          console.warn("[QA_HEALTH boot]", r.name, "FAILED:", r.failMsg);
        }
      }
    });
  }


  // ── SECTION 4: DIAGNOSTICS PANEL ─────────────────────────────────────────────

  /**
   * openPanel()
   * Renders a full-screen diagnostic overlay listing all checks.
   * Triggered by Ctrl+Shift+D (wired in keyboard-shortcuts.js).
   * Closes on Escape or clicking the × button.
   * Re-runs checks fresh each time it opens.
   */
  function openPanel() {
    // Remove any existing panel
    var existing = document.getElementById("qa-health-panel");
    if (existing) { existing.remove(); return; } // toggle: second press closes

    var results  = run({ criticalOnly: false });
    var total    = results.length;
    var passed   = results.filter(function(r) { return r.passed; }).length;
    var critical = results.filter(function(r) { return !r.passed && r.critical; }).length;
    var warnings = results.filter(function(r) { return !r.passed && !r.critical; }).length;

    // ── Build panel HTML ──────────────────────────────────────────────────────
    var summaryColor = critical > 0 ? "#e74c3c" : warnings > 0 ? "#f39c12" : "#27ae60";
    var summaryText  = critical > 0
      ? critical + " critical failure" + (critical > 1 ? "s" : "")
      : warnings > 0
        ? warnings + " warning" + (warnings > 1 ? "s" : "")
        : "All systems operational";

    // Group results: critical failures → warnings → passes
    var critFails = results.filter(function(r) { return !r.passed && r.critical; });
    var warnFails = results.filter(function(r) { return !r.passed && !r.critical; });
    var passes    = results.filter(function(r) { return r.passed; });

    function row(r) {
      var icon   = r.passed ? "✅" : r.critical ? "🔴" : "🟡";
      var detail = r.passed ? "" :
        '<div style="font-size:11px;color:#aaa;margin-top:3px;padding-left:20px;">' +
        r.failMsg + '</div>';
      return '<div style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.06);">' +
             '<span style="font-size:13px;">' + icon + ' ' + r.name + '</span>' +
             detail + '</div>';
    }

    var rowsHtml = critFails.concat(warnFails).concat(passes)
                            .map(row).join("");

    var panel = document.createElement("div");
    panel.id  = "qa-health-panel";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "System Diagnostics");
    panel.style.cssText = [
      "position:fixed", "inset:0", "z-index:99999",
      "background:rgba(0,0,0,0.72)",
      "display:flex", "align-items:center", "justify-content:center",
      "font-family:var(--qa-font,'Segoe UI',sans-serif)",
    ].join(";");

    panel.innerHTML =
      '<div style="background:#1e1e2e;border:1px solid rgba(255,255,255,0.12);' +
      'border-radius:10px;width:560px;max-width:94vw;max-height:80vh;' +
      'display:flex;flex-direction:column;overflow:hidden;">' +

        // Header
        '<div style="display:flex;align-items:center;justify-content:space-between;' +
        'padding:16px 20px;border-bottom:1px solid rgba(255,255,255,0.1);">' +
          '<div>' +
            '<div style="font-size:15px;font-weight:600;color:#e0e0e0;">System Diagnostics</div>' +
            '<div style="font-size:12px;color:' + summaryColor + ';margin-top:2px;">' +
              summaryText + ' · ' + passed + '/' + total + ' checks passed' +
            '</div>' +
          '</div>' +
          '<button id="qa-health-close" ' +
            'style="background:none;border:none;color:#aaa;font-size:20px;' +
            'cursor:pointer;line-height:1;padding:4px 8px;" ' +
            'aria-label="Close">×</button>' +
        '</div>' +

        // Body
        '<div style="overflow-y:auto;padding:12px 20px;flex:1;color:#ddd;">' +
          rowsHtml +
        '</div>' +

        // Footer
        '<div style="padding:12px 20px;border-top:1px solid rgba(255,255,255,0.1);' +
        'display:flex;justify-content:space-between;align-items:center;">' +
          '<span style="font-size:11px;color:#666;">Press Ctrl+Shift+D or Esc to close</span>' +
          '<button id="qa-health-rerun" ' +
            'style="background:#3a3a5c;border:1px solid rgba(255,255,255,0.15);' +
            'color:#e0e0e0;border-radius:5px;padding:6px 14px;font-size:12px;' +
            'cursor:pointer;">Run Again</button>' +
        '</div>' +

      '</div>';

    document.body.appendChild(panel);

    // ── Wire close/re-run ─────────────────────────────────────────────────────
    document.getElementById("qa-health-close").addEventListener("click", function() {
      panel.remove();
    });
    document.getElementById("qa-health-rerun").addEventListener("click", function() {
      panel.remove();
      // Small delay so the panel fully removes before re-opening
      setTimeout(openPanel, 50);
    });
    panel.addEventListener("click", function(e) {
      if (e.target === panel) { panel.remove(); } // click backdrop to close
    });
  }


  // ── SECTION 5: PUBLIC API ─────────────────────────────────────────────────────

  window.QA_HEALTH = {
    run:       run,       // run all or critical checks — returns results array
    runBoot:   runBoot,   // called by os-core.js init() — toasts critical failures
    openPanel: openPanel, // called by keyboard shortcut Ctrl+Shift+D
  };

})();
```

---

## Part 2 — `src/keyboard-shortcuts.js`

Create `desktop/src/keyboard-shortcuts.js`. This file defines `window.QA_SHORTCUTS`.

### Structure

```javascript
/**
 * keyboard-shortcuts.js — Centralised keyboard shortcut registry
 * ===============================================================
 * QA Pilot OS — Sprint C11
 *
 * Exposes: window.QA_SHORTCUTS
 *
 * Usage (called from os-core.js init()):
 *   window.QA_SHORTCUTS.init();       // registers the keydown handler
 *   window.QA_SHORTCUTS.getAll();     // returns shortcuts grouped by category
 *
 * Adding a new shortcut:
 *   Push an entry to SHORTCUTS with { category, keys, description, action }.
 *   action() will fire when the combo is matched.
 *   The Settings panel reads getAll() automatically — no further changes needed.
 *
 * Key matching:
 *   Each entry specifies { ctrl, shift, alt, key } as a subset — unspecified
 *   modifiers default to false. 'key' matches e.key (case-insensitive).
 */

(function() {
  "use strict";


  // ── SECTION 1: SHORTCUT DEFINITIONS ──────────────────────────────────────────
  // { category, keys (display string), description, action, ctrl, shift, alt, key }
  // 'action' is optional for documentation-only entries (e.g. double-click actions).

  var SHORTCUTS = [

    // ── Diagnostics ─────────────────────────────────────────────────────────────
    {
      category:    "Diagnostics",
      keys:        "Ctrl + Shift + D",
      description: "Open system diagnostics panel",
      ctrl: true, shift: true, alt: false, key: "d",
      action: function() {
        if (typeof window.QA_HEALTH !== "undefined") {
          window.QA_HEALTH.openPanel();
        }
      },
    },

    // ── Start Menu ───────────────────────────────────────────────────────────────
    {
      category:    "Start Menu",
      keys:        "Win / Ctrl + Esc",
      description: "Open / close Start menu",
      // documented-only — Start button click is the primary trigger.
      // Ctrl+Esc wiring is added below via the keydown handler directly.
      ctrl: true, shift: false, alt: false, key: "Escape",
      action: function() {
        // toggleStartMenu is on QA_OS
        if (typeof window.QA_OS !== "undefined" && window.QA_OS.toggleStartMenu) {
          window.QA_OS.toggleStartMenu();
        }
      },
    },

    // ── Windows ──────────────────────────────────────────────────────────────────
    {
      category:    "Windows",
      keys:        "Escape",
      description: "Close open menus and panels (context menu, panels)",
      // This is handled in os-core.js keydown handler for context menus.
      // Listed here for discoverability. No action — handled elsewhere.
      ctrl: false, shift: false, alt: false, key: "Escape",
      action: null, // handled by os-core.js Escape handler
    },

    // ── Settings (documentation only — no keyboard action) ────────────────────
    {
      category:    "Navigation",
      keys:        "Double-click desktop icon",
      description: "Open app",
      action: null, // mouse action, listed for reference
    },
    {
      category:    "Navigation",
      keys:        "Right-click desktop icon",
      description: "Open context menu",
      action: null,
    },
    {
      category:    "Windows",
      keys:        "Right-click title bar",
      description: "Window context menu (snap, close, minimise)",
      action: null,
    },
    {
      category:    "Windows",
      keys:        "Right-click taskbar button",
      description: "Close window",
      action: null,
    },
    {
      category:    "Windows",
      keys:        "Drag title bar",
      description: "Move window",
      action: null,
    },
    {
      category:    "Windows",
      keys:        "Drag window edge",
      description: "Resize window",
      action: null,
    },
    {
      category:    "Windows",
      keys:        "Hover maximise button",
      description: "Show snap layout flyout",
      action: null,
    },

  ];


  // ── SECTION 2: KEY MATCHER ────────────────────────────────────────────────────

  /**
   * matches(e, shortcut)
   * Returns true if KeyboardEvent e matches the shortcut's combo.
   * Only checks shortcuts that have a 'key' property and an 'action'.
   */
  function matches(e, s) {
    if (!s.key || !s.action) return false;
    var ctrlOk  = !!s.ctrl  === e.ctrlKey;
    var shiftOk = !!s.shift === e.shiftKey;
    var altOk   = !!s.alt   === e.altKey;
    var keyOk   = e.key.toLowerCase() === s.key.toLowerCase();
    return ctrlOk && shiftOk && altOk && keyOk;
  }


  // ── SECTION 3: KEYDOWN HANDLER ────────────────────────────────────────────────

  /**
   * init()
   * Registers a single document keydown listener that checks every shortcut.
   * Called once from os-core.js init() after the DOM is ready.
   * Guards against double-registration.
   */
  var _initialised = false;
  function init() {
    if (_initialised) return;
    _initialised = true;

    document.addEventListener("keydown", function(e) {
      // Don't fire shortcuts when user is typing in an input/textarea
      var tag = e.target && e.target.tagName ? e.target.tagName.toLowerCase() : "";
      if (tag === "input" || tag === "textarea" || tag === "select") return;

      for (var i = 0; i < SHORTCUTS.length; i++) {
        if (matches(e, SHORTCUTS[i])) {
          e.preventDefault();
          SHORTCUTS[i].action();
          return; // first match wins
        }
      }
    });
  }


  // ── SECTION 4: SETTINGS READER ────────────────────────────────────────────────

  /**
   * getAll()
   * Returns shortcuts grouped by category.
   * Shape: { "Category Name": [ { keys, description }, ... ], ... }
   * Used by apps/settings.html to render the Keyboard Shortcuts panel.
   */
  function getAll() {
    var groups = {};
    SHORTCUTS.forEach(function(s) {
      var cat = s.category || "Other";
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push({ keys: s.keys, description: s.description });
    });
    return groups;
  }


  // ── SECTION 5: PUBLIC API ─────────────────────────────────────────────────────

  window.QA_SHORTCUTS = {
    init:   init,   // called by os-core.js init()
    getAll: getAll, // called by settings.html
  };

})();
```

---

## Part 3 — Update `desktop/build.js`

Add both new source files to the build. **Read `build.js` before editing.**

### Step 1 — Add path constants

After the existing `SCORING_PATH` constant (added in C10), add:

```javascript
const HEALTH_PATH     = path.join(ROOT, "src", "health-checks.js");
const SHORTCUTS_PATH  = path.join(ROOT, "src", "keyboard-shortcuts.js");
```

### Step 2 — Read both files in `build()`

After the existing `scoringJs` read, add:

```javascript
const healthJs = fs.existsSync(HEALTH_PATH)
  ? fs.readFileSync(HEALTH_PATH, "utf8") + "\n"
  : "// health-checks.js not found\n";

const shortcutsJs = fs.existsSync(SHORTCUTS_PATH)
  ? fs.readFileSync(SHORTCUTS_PATH, "utf8") + "\n"
  : "// keyboard-shortcuts.js not found\n";
```

### Step 3 — Append to `bundleContent`

Add both after `scoringJs` in the bundle string:

```javascript
const bundleContent =
  "// os.bundle.js — generated by build.js — do not edit by hand\n\n" +
  dbJs        + "\n" +
  eventBusJs  + "\n" +
  compositorJs+ "\n" +
  workspacesJs+ "\n" +
  appHtmlDecl + "\n" +
  scenariosJs + "\n" +
  wrappedCore + "\n" +
  scoringJs   + "\n" +   // from C10
  shortcutsJs + "\n" +   // ← ADD (before health — shortcuts must exist for health to check)
  healthJs;              // ← ADD (last — checks all the above)
```

### Step 4 — Append to `safeJs`

Find the `safeJs` concatenation and add the same two files at the end, before `.replace(...)`:

```javascript
const safeJs = (dbJs + "\n" + eventBusJs + "\n" + compositorJs + "\n" +
                workspacesJs + "\n" + appHtmlDecl + "\n" + scenariosJs + "\n" +
                wrappedCore + "\n" + scoringJs + "\n" +
                shortcutsJs + "\n" + healthJs)   // ← ADD both here
  .replace(/<\/script/gi, "<\\/script");
```

**Load order rationale:**
`db → event-bus → compositor → workspaces → APP_HTML → scenarios → os-core (IIFE) → scoring → keyboard-shortcuts → health-checks`
Health runs last so it can test every module above it.

---

## Part 4 — Update `src/os-core.js`

**Read `os-core.js` before editing. Make only the targeted additions.**

### In `init()`

Find the end of the `init()` function — after all DOM bindings are complete
(after `bindEvents()` is called, before or after the boot animation starts).
Add these two lines:

```javascript
// Initialise keyboard shortcut registry (must run after DOM is ready)
if (window.QA_SHORTCUTS) window.QA_SHORTCUTS.init();

// Run boot-time health checks (after all modules are wired — toasts on failure)
if (window.QA_HEALTH) window.QA_HEALTH.runBoot();
```

Place `QA_SHORTCUTS.init()` BEFORE `QA_HEALTH.runBoot()` so the shortcuts health
check finds the registry already initialised when the health check runs.

**Do not modify any existing logic.** These are two additive lines only.

---

## Part 5 — Update `apps/settings.html`

**Read `apps/settings.html` before editing.**

### Add a "Keyboard Shortcuts" sidebar nav item

Find the existing sidebar `<nav>` or list of settings sections. Add a new entry:

```html
<li data-section="shortcuts" class="settings-nav-item">
  <span class="settings-nav-icon">⌨</span>
  Keyboard Shortcuts
</li>
```

Match the structure and class names of the existing nav items exactly.

### Add the Keyboard Shortcuts content panel

Find where existing section panels are defined (e.g. `<div class="settings-section" id="section-display">`).
Add a new sibling panel:

```html
<div class="settings-section" id="section-shortcuts" style="display:none;">
  <h2 class="settings-section-title">Keyboard Shortcuts</h2>
  <p class="settings-section-desc">
    All available keyboard shortcuts. Mouse and touch actions are listed for reference.
  </p>
  <div id="shortcuts-list"></div>
</div>
```

### Add JavaScript to populate the shortcuts panel

In `settings.html`'s `<script>` block, add a function to render the shortcuts
when the section is shown. Call it when the sidebar nav item is clicked.

```javascript
/**
 * renderShortcuts()
 * Reads window.parent.QA_SHORTCUTS.getAll() and renders grouped shortcut rows
 * into #shortcuts-list. Safe to call multiple times (clears on each call).
 */
function renderShortcuts() {
  var container = document.getElementById("shortcuts-list");
  if (!container) return;
  container.innerHTML = "";

  // Graceful degradation if registry not available
  if (!window.parent || !window.parent.QA_SHORTCUTS) {
    container.innerHTML =
      '<p style="color:var(--qa-text-muted,#888);font-size:13px;">' +
      'Shortcut registry not available.</p>';
    return;
  }

  var groups = window.parent.QA_SHORTCUTS.getAll();

  Object.keys(groups).forEach(function(category) {
    // Category heading
    var heading = document.createElement("div");
    heading.style.cssText =
      "font-size:11px;font-weight:600;text-transform:uppercase;" +
      "letter-spacing:0.06em;color:var(--qa-text-muted,#888);" +
      "margin:20px 0 8px;padding-bottom:4px;" +
      "border-bottom:1px solid var(--qa-border,rgba(0,0,0,0.12));";
    heading.textContent = category;
    container.appendChild(heading);

    // Rows
    groups[category].forEach(function(shortcut) {
      var row = document.createElement("div");
      row.style.cssText =
        "display:flex;justify-content:space-between;align-items:center;" +
        "padding:7px 0;font-size:13px;" +
        "border-bottom:1px solid var(--qa-border,rgba(0,0,0,0.06));";

      var desc = document.createElement("span");
      desc.style.color = "var(--qa-text,#222)";
      desc.textContent = shortcut.description;

      var keys = document.createElement("kbd");
      keys.style.cssText =
        "font-family:var(--qa-font-mono,'Consolas','Courier New',monospace);" +
        "font-size:11px;padding:2px 8px;border-radius:4px;" +
        "background:var(--qa-surface-2,#f0f0f0);" +
        "border:1px solid var(--qa-border,rgba(0,0,0,0.18));" +
        "color:var(--qa-text,#333);white-space:nowrap;";
      keys.textContent = shortcut.keys;

      row.appendChild(desc);
      row.appendChild(keys);
      container.appendChild(row);
    });
  });
}
```

### Wire the nav click to show the panel and populate it

Find the existing section-switching logic in `settings.html`. It likely looks
like a `data-section` click handler that shows/hides `.settings-section` panels.
In that handler, after showing the shortcuts section, call `renderShortcuts()`:

```javascript
// Inside the existing section-switch click handler:
if (section === "shortcuts") {
  renderShortcuts();
}
```

If the existing handler already calls a generic `showSection(id)` function,
just ensure `renderShortcuts()` is called when `section-shortcuts` becomes visible.
Do not rewrite the existing switching logic — add only the one conditional call.

---

## Build & verify

```bash
cd desktop
node build.js
```

Expected output: `✓ Built: dist.html` (no errors).

Open `dist.html` in a browser:

1. **Boot health checks** — If `scoring.js` was fixed in C10, no critical toasts should appear on boot.
2. **Ctrl+Shift+D** — Diagnostics panel opens. Verify: all rows show ✅ except any known stubs (training, reports, inspector apps show 🟡 if not registered). Panel closes on Esc, backdrop click, or × button. "Run Again" reopens it.
3. **Settings → Keyboard Shortcuts** — Panel renders all categories and shortcuts from the registry.
4. **No regressions** — Open an app, drag a window, use Start menu, right-click desktop. All existing behaviour unchanged.

---

## After all changes are applied

Update `FEATURE-STATUS.md` in the repo root — add or change the following rows:

### In OS Shell → Start Menu:
| Row | New status |
|-----|-----------|
| Keyboard shortcut registry (`keyboard-shortcuts.js`) | ✅ |

### Add a new section "Diagnostics" under OS Shell:
| Feature | Status | Notes |
|---------|--------|-------|
| Health check registry (`health-checks.js`) | ✅ | OBD2-style self-test; toasts critical failures on boot |
| Diagnostics panel (Ctrl+Shift+D) | ✅ | Full check list with pass/warn/fail; Re-run button |

### In Apps → Settings:
| Feature | Status | Notes |
|---------|--------|-------|
| Keyboard Shortcuts panel | ✅ | Reads from `window.parent.QA_SHORTCUTS.getAll()` |

### In Build Pipeline:
| Step | Status | Notes |
|------|--------|-------|
| `health-checks.js` bundled into output | ✅ | After keyboard-shortcuts.js |
| `keyboard-shortcuts.js` bundled into output | ✅ | After scoring.js |

---

## What NOT to Change

- Do not modify `os.css`
- Do not modify `scoring.js`
- Do not modify any lesson files or `capstone.html`
- Do not add CDN links or external dependencies
- Do not rewrite existing functions in `os-core.js` or `settings.html` — only add lines

---

## Definition of Done

- [ ] `src/health-checks.js` created — `window.QA_HEALTH` defined with `run`, `runBoot`, `openPanel`
- [ ] `src/keyboard-shortcuts.js` created — `window.QA_SHORTCUTS` defined with `init`, `getAll`
- [ ] `build.js` — `HEALTH_PATH` and `SHORTCUTS_PATH` constants added
- [ ] `build.js` — `healthJs` and `shortcutsJs` read from filesystem
- [ ] `build.js` — both appended to `bundleContent` and `safeJs` after `scoringJs`, in order: `shortcutsJs` then `healthJs`
- [ ] `os-core.js` — `QA_SHORTCUTS.init()` and `QA_HEALTH.runBoot()` called in `init()`
- [ ] `settings.html` — "Keyboard Shortcuts" nav item added to sidebar
- [ ] `settings.html` — `#section-shortcuts` content panel added
- [ ] `settings.html` — `renderShortcuts()` called when section becomes visible
- [ ] `node build.js` completes without errors
- [ ] Boot: no spurious toasts when all systems working; critical failures toast clearly
- [ ] `Ctrl+Shift+D` opens diagnostics panel; second press or Esc closes it
- [ ] Diagnostics panel shows correct pass/warn/fail for each check; "Run Again" re-runs fresh
- [ ] Settings → Keyboard Shortcuts shows grouped shortcuts table styled consistently
- [ ] No existing features broken
