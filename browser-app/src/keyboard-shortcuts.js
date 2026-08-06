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