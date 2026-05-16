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
        return typeof window.QA_OS !== "undefined" &&
               typeof window.QA_OS.EventBus !== "undefined" &&
               typeof window.QA_OS.EventBus.emit === "function";
      },
      failMsg:  "EventBus not found — inter-module messaging will not work.",
    },
    {
      id:       "compositor-loaded",
      name:     "Compositor (compositor.js bundled)",
      critical: true,
      test:     function() {
        return typeof window.QA_OS !== "undefined" &&
               typeof window.QA_OS.Compositor !== "undefined" &&
               typeof window.QA_OS.Compositor.openWindow === "function";
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
        if (typeof window.QA_OS !== "undefined" && window.QA_OS.EventBus && window.QA_OS.EventBus.emit) {
          window.QA_OS.EventBus.emit("notify", "🔴 " + r.name + " — " + r.failMsg);
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