// src/os-core.js — QA Pilot Desktop OS engine (expects global APP_HTML + window.SCENARIOS)
//
// APPS registry — the single source of truth for every app in the OS.
// Each entry controls the Start menu tile, taskbar button, and window title.
// To add a new app:
//   1. Add an entry here with a unique lowercase id
//   2. Create apps/<id>.html
//   3. Add a desktop icon button in index.html (data-app="<id>")
//   4. Run `node build.js`

const APPS = {
  // ── Dynamics CRM — blue document/database icon ──────────────────────────
  dynamics: {
    id: "dynamics",
    title: "Dynamics CRM — Case Investigation",
    short: "Dynamics",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="5" width="26" height="22" rx="4" fill="#0078D4"/><rect x="11" y="2" width="10" height="7" rx="2" fill="#004B8C"/><rect x="7" y="13" width="18" height="2.5" rx="1.25" fill="white" opacity="0.95"/><rect x="7" y="18" width="13" height="2" rx="1" fill="white" opacity="0.7"/><rect x="7" y="23" width="9" height="2" rx="1" fill="white" opacity="0.5"/></svg>`,
  },

  // ── Azure DevOps — purple pipeline icon ─────────────────────────────────
  ado: {
    id: "ado",
    title: "Azure DevOps — Bug Report",
    short: "ADO",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="28" height="28" rx="6" fill="#5C2D91"/><circle cx="8" cy="16" r="3" fill="white" opacity="0.9"/><circle cx="16" cy="8" r="3" fill="white" opacity="0.9"/><circle cx="24" cy="16" r="3" fill="white" opacity="0.9"/><circle cx="16" cy="24" r="3" fill="white" opacity="0.9"/><line x1="8" y1="16" x2="16" y2="8" stroke="white" stroke-width="1.8" opacity="0.6"/><line x1="16" y1="8" x2="24" y2="16" stroke="white" stroke-width="1.8" opacity="0.6"/><line x1="24" y1="16" x2="16" y2="24" stroke="white" stroke-width="1.8" opacity="0.6"/></svg>`,
  },

  // ── Acceptance Criteria — green checklist icon ───────────────────────────
  ac: {
    id: "ac",
    title: "Acceptance Criteria",
    short: "AC",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="3" width="26" height="26" rx="5" fill="#107C10"/><path d="M9 16 L13 20 L23 10" stroke="white" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/><rect x="9" y="23" width="14" height="2" rx="1" fill="white" opacity="0.5"/></svg>`,
  },

  // ── QA Browser — tabbed workspace (Dynamics + ADO + AC in one window) ───
  // NOTE: also add a desktop icon button in index.html for this app
  browser: {
    id: "browser",
    title: "QA Browser",
    short: "Browser",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="4" width="28" height="24" rx="5" fill="#0099BC"/><rect x="2" y="4" width="28" height="9" rx="5" fill="#007A99"/><rect x="2" y="9" width="28" height="4" fill="#007A99"/><circle cx="7" cy="9" r="2" fill="#00C2EB" opacity="0.8"/><circle cx="13" cy="9" r="2" fill="#00C2EB" opacity="0.5"/><circle cx="19" cy="9" r="2" fill="#00C2EB" opacity="0.3"/><rect x="6" y="18" width="20" height="2" rx="1" fill="white" opacity="0.7"/><rect x="6" y="22" width="14" height="2" rx="1" fill="white" opacity="0.4"/></svg>`,
  },

  // ── Training — orange scenario launcher icon ─────────────────────────────
  training: {
    id: "training",
    title: "Training — Scenarios",
    short: "Training",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="28" height="28" rx="6" fill="#CA5010"/><path d="M16 8 L28 14 L16 20 L4 14 Z" fill="white" opacity="0.9"/><path d="M8 17 L8 23 Q16 27 24 23 L24 17" stroke="white" stroke-width="2" fill="none" stroke-linecap="round"/></svg>`,
  },

  // ── Teams — purple chat icon ──────────────────────────────────────────────
  teams: {
    id: "teams",
    title: "Microsoft Teams — QA Channel",
    short: "Teams",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="28" height="28" rx="6" fill="#6264A7"/><circle cx="11" cy="12" r="4.5" fill="white" opacity="0.95"/><path d="M6 22c0-2.8 2.2-5 5-5s5 2.2 5 5v1H6v-1z" fill="white" opacity="0.95"/><circle cx="22" cy="13" r="3.5" fill="white" opacity="0.8"/><path d="M18 22c0-2.2 1.8-4 4-4s4 1.8 4 4v1h-8v-1z" fill="white" opacity="0.8"/></svg>`,
  },

  // ── Settings — dark gear icon ────────────────────────────────────────────
  settings: {
    id: "settings",
    title: "Settings",
    short: "Settings",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="28" height="28" rx="6" fill="#2B2B2B"/><circle cx="16" cy="16" r="4.5" fill="none" stroke="white" stroke-width="2.5"/><path d="M16 6 L16 9 M16 23 L16 26 M6 16 L9 16 M23 16 L26 16 M8.9 8.9 L11 11 M21 21 L23.1 23.1 M23.1 8.9 L21 11 M11 21 L8.9 23.1" stroke="white" stroke-width="2.2" stroke-linecap="round"/></svg>`,
  },

  // ── Word — blue document icon ────────────────────────────────────────────
  word: {
    id: "word",
    title: "Word — Document Editor",
    short: "Word",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="28" height="28" rx="4" fill="#185ABD"/><path d="M10 10h12v2H10zm0 5h12v2H10zm0 5h8v2H10z" fill="white"/></svg>`,
  },

  // ── Excel — green spreadsheet icon ───────────────────────────────────────
  excel: {
    id: "excel",
    title: "Excel — Spreadsheet",
    short: "Excel",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="28" height="28" rx="4" fill="#107C10"/><path d="M8 8h16v2H8zm0 5h16v2H8zm0 5h12v2H8z" fill="white"/></svg>`,
  },

  // ── PowerPoint — orange presentation icon ─────────────────────────────────
  powerpoint: {
    id: "powerpoint",
    title: "PowerPoint — Presentations",
    short: "PowerPoint",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="28" height="28" rx="4" fill="#C43E1C"/><path d="M10 10h12v2H10zm0 5h12v2H10zm0 5h8v2H10z" fill="white"/></svg>`,
  },

  // ── Reports — teal bar-chart icon ────────────────────────────────────────
  reports: {
    id: "reports",
    title: "Reports — QA Analytics",
    short: "Reports",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="28" height="28" rx="6" fill="#038387"/><rect x="7" y="20" width="4" height="6" rx="1.5" fill="white" opacity="0.9"/><rect x="14" y="14" width="4" height="12" rx="1.5" fill="white" opacity="0.9"/><rect x="21" y="9" width="4" height="17" rx="1.5" fill="white" opacity="0.9"/><path d="M9 18 L16 12 L23 7" stroke="white" stroke-width="1.5" fill="none" stroke-linecap="round" opacity="0.6"/></svg>`,
  },

  // ── Scenario Inspector — grey magnifying glass icon ──────────────────────
  inspector: {
    id: "inspector",
    title: "Scenario Inspector",
    short: "Inspector",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="28" height="28" rx="6" fill="#69747C"/><circle cx="14" cy="14" r="7" fill="none" stroke="white" stroke-width="2.8"/><circle cx="14" cy="14" r="4" fill="white" opacity="0.2"/><line x1="19.5" y1="19.5" x2="26" y2="26" stroke="white" stroke-width="3" stroke-linecap="round"/></svg>`,
  },

  // ── QApache — easter egg web server ───────────────────────────────────────
  qapache: {
    id: "qapache",
    title: "QApache — Internal Web Server",
    short: "QApache",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="28" height="28" rx="6" fill="#E94560"/><path d="M8 16 L12 20 L22 10" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  },

  // ── QTube — easter egg video platform ────────────────────────────────────
  qtube: {
    id: "qtube",
    title: "QTube — Video Platform",
    short: "QTube",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="28" height="28" rx="6" fill="#FF0000"/><polygon points="12,8 24,16 12,24" fill="white"/></svg>`,
  },

  // ── QOutlook — easter egg web mail ───────────────────────────────────────
  qoutlook: {
    id: "qoutlook",
    title: "QOutlook — Web Mail",
    short: "QOutlook",
    icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="28" height="28" rx="6" fill="#0078D4"/><path d="M6 10 L16 18 L26 10" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><rect x="6" y="10" width="20" height="14" rx="1" stroke="white" stroke-width="2" fill="none"/></svg>`,
  },
};

const STORAGE_KEY = "qaSimulatorDesktop";

const CAPSTONE_SESSION_KEY = "qa-capstone-session";
const PACKAGES_KEY = "qaModularPackages";

const state = {
  role: "junior",
  theme: "light",
  background: "default",
  brightness: 100,
  installedApps: Object.keys(APPS),
  packages: {},      // user-installed packages keyed by id
  fidelity: "win11",

  capstoneScenarioId: null,
  activeScenarioId: null,
  bugsFound: [],
  bugsLogged: [],
  activeBugs: [],

  // ── Capstone 2 orchestration state (Sprint G) ──────────────────────
  speed: 1,                 // Simulation speed: 1×, 2×, or 4×
  mode: 'guided',           // Training mode: 'guided' or 'free'
  capstone2Stage: 0,        // Current stage index (0-based, -1 = not active)
  capstone2InProg: false,   // Whether a C2 assessment is in progress
};

let shell,
  windowArea,
  startMenu,
  startButton,
  startSearchInput,
  startGrid,
  taskbarApps,
  roleLabel,
  taskbarRole,
  clockEl,
  roleSwitcher,
  notifyCenter,
  notifyList,
  quickPanel,
  taskviewOverlay,
  taskviewInner,
  lockScreen,
  lockTime,
  lockDate,
  notifyButton,
  quickButton,
  taskviewButton,
  themeLightBtn,
  themeDarkBtn,
  brightnessSlider,
  submitBtn,
  submitTile,
  pkgFileInput,
  pkgMgrOverlay,
  pkgMgrPanel,
  pkgMgrBody,
  pkgMgrList,
  pkgMgrEmpty,
  pkgMgrClose,
  pkgMgrInstallBtn,
  installPkgBtn,
  pkgManagerBtn;

let _clockInterval;
let _clockUpdateFn;
let _progressWidget;
let _speedBtn;
let _modePill;

document.addEventListener("DOMContentLoaded", init);

function init() {
  shell = document.getElementById("qa-shell");
  windowArea = document.getElementById("qa-window-area");
  startMenu = document.getElementById("qa-start-menu");
  startButton = document.getElementById("qa-start-button");
  startGrid = document.getElementById("qa-start-grid");
  startSearchInput = document.getElementById("qa-start-search-input");
  taskbarApps = document.getElementById("qa-taskbar-apps");
  roleLabel = document.getElementById("qa-role-label");
  taskbarRole = document.getElementById("qa-taskbar-role");
  clockEl = document.getElementById("qa-taskbar-clock");
  roleSwitcher = document.getElementById("qa-role-switcher");
  notifyCenter = document.getElementById("qa-notify-center");
  notifyList = document.getElementById("qa-notify-list");
  quickPanel = document.getElementById("qa-quick-panel");
  taskviewOverlay = document.getElementById("qa-taskview-overlay");
  taskviewInner = document.getElementById("qa-taskview-inner");
  lockScreen = document.getElementById("qa-lock-screen");
  lockTime = document.getElementById("qa-lock-time");
  lockDate = document.getElementById("qa-lock-date");
  notifyButton = document.getElementById("qa-notify-button");
  quickButton = document.getElementById("qa-quick-button");
  taskviewButton = document.getElementById("qa-taskview-button");
  themeLightBtn = document.getElementById("qa-theme-light");
  themeDarkBtn = document.getElementById("qa-theme-dark");
  brightnessSlider = document.getElementById("qa-brightness-slider");
  submitBtn = document.getElementById("qa-submit-btn");
  submitTile = document.getElementById("qa-submit-tile");
  pkgMgrOverlay = document.getElementById("qa-pkg-mgr-overlay");
  pkgMgrPanel = document.getElementById("qa-pkg-mgr-panel");
  pkgMgrBody = document.getElementById("qa-pkg-mgr-body");
  pkgMgrList = document.getElementById("qa-pkg-mgr-list");
  pkgMgrEmpty = document.getElementById("qa-pkg-mgr-empty");
  pkgMgrClose = document.getElementById("qa-pkg-mgr-close");
  pkgMgrInstallBtn = document.getElementById("qa-pkg-mgr-install-btn");
  pkgFileInput = document.getElementById("qa-package-file-input");
  installPkgBtn = document.getElementById("qa-install-package-btn");
  pkgManagerBtn = document.getElementById("qa-pkg-manager-btn");

  // ── INITIALISE ARCHITECTURE LAYERS ──────────────────────────
  var bus = window.QA_OS && window.QA_OS.EventBus;
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  var workspaces = window.QA_OS && window.QA_OS.Workspaces;

  if (compositor) compositor.init(windowArea);
  if (bus) bus.initAppMessaging();

  // ── BOOT SEQUENCE ─────────────────────────────────────────────────────
  var bootScreen = document.getElementById("qa-boot-screen");
  if (bootScreen) {
    setTimeout(function () {
      lockScreen.classList.remove("qa-lock-hidden");
      lockScreen.style.display = "";
      bootScreen.classList.add("qa-boot-hidden");
      setTimeout(function () {
        bootScreen.style.display = "none";
      }, 650);
    }, 2500);
  } else {
    lockScreen.classList.remove("qa-lock-hidden");
    lockScreen.style.display = "";
  }

  loadState();
  loadPackages();
  applyTheme();
  applyBackground();
  applyBrightness();
  applyFidelity();
  bindEvents();
  renderRole();
  renderAllWindows();
  renderTaskbar();
  renderStartMenu();
  startClock();
  setupPackageInstaller();
  startLockClock();

  // Auto-save via Workspaces when OS state changes
  if (workspaces) {
    setupAutoSave(workspaces);
  }

  setupNotifier();
  setupDesktopContextMenu();
  injectDesktopWidgets();
  updateProgressWidget();

  // Wire up EventBus to trigger toast notifier
  if (bus) {
    bus.on("notify", function (data) {
      showNotifier(data.text || data, data.type || "info");
    });
    // Legacy notify from app messages
    bus.on("app:NOTIFY", function (msg) {
      showNotifier(
        msg.text || msg.message || "Notification",
        msg.type || "info",
      );
    });
  }

  // F17: Listen for QOutlook unread count updates from the child app iframe
  window.addEventListener('message', function (event) {
    var msg = event.data;
    if (!msg || msg.type !== 'QOUTLOOK_UNREAD_COUNT') return;
    var badge = document.getElementById('qa-badge-qoutlook');
    if (badge) {
      var count = parseInt(msg.count, 10) || 0;
      if (count > 0) {
        badge.textContent = count > 99 ? '99+' : count;
        badge.style.display = '';
      } else {
        badge.style.display = 'none';
      }
    }
  });

  if (compositor && compositor.getWindows().length === 0) {
    openApp("dynamics");
    openApp("ac");
    // Maximize the work browser after a short delay so the window
    // has enough width for the Dynamics/ADO/AC form layouts
    setTimeout(function () {
      var wb = compositor.getWindows().find(function (w) {
        return w.appId === "browser" && w.isWorkBrowser === true;
      });
      if (wb) {
        compositor.setLayout(wb.id, "maximized");
        renderAllWindows();
        renderTaskbar();
      }
    }, 150);

    // Auto-launch enterprise apps (Teams, Outlook) after a short delay
    // to simulate a real Windows corporate desktop environment.
    setTimeout(function () {
      openApp("teams");
      openApp("qoutlook");
      // Launch browser minimized (simulates a user who has it running
      // but not actively in focus)
      openApp("browser");
      setTimeout(function () {
        // Minimize the browser after its window is created
        var browserWin = compositor.getWindows().find(function (w) {
          return w.appId === "browser" && !w.isWorkBrowser;
        });
        if (browserWin) {
          compositor.minimize(browserWin.id);
          renderAllWindows();
          renderTaskbar();
        }
      }, 200);
    }, 800);
  }

  // NOTE (2026-05-22): Removed dead cleanup wrapper code that was intended to
  // track event listeners for removal on unload. The wrapper was placed after
  // the bindEvents() call in init(), so it never tracked the actual listeners.
  // For this file:// desktop simulator running in an iframe, explicit listener
  // cleanup is not required because:
  // 1. The iframe is destroyed when navigating between pages
  // 2. Modern browsers garbage-collect listeners with detached DOM
  // 3. Training sessions are typically short-lived
  // If long-running sessions become a requirement, implement a proper
  // listener registry pattern here.

  var coreApi = {
    getRole: function () {
      return state.role;
    },
    getFidelity: function () {
      return state.fidelity;
    },
    setTheme: function (t) {
      setTheme(t);
    },
    setBackground: function (id) {
      setBackground(id);
    },
    setFidelity: function (mode) {
      setFidelity(mode);
    },
    notify: function (msg) {
      addNotification(msg);
    },
    notifyToast: function (text, type) {
      showNotifier(text, type);
    },
    openApp: function (id) {
      openApp(id);
    },
    installApp: function (id) {
      installApp(id);
    },
    uninstallApp: function (id) {
      uninstallApp(id);
    },
    isInstalled: function (id) {
      return isInstalled(id);
    },
    loadScenario: function (id) {
      return (window.SCENARIOS && window.SCENARIOS[id]) || null;
    },
    /**
     * getActiveScenarioId()
     * Returns the currently active scenario ID (if any), or null.
     * Used by apps (e.g. training) to proactively detect an active
     * capstone scenario without waiting for APP_BOOT.
     */
    getActiveScenarioId: function () {
      return state.activeScenarioId || null;
    },
    /**
     * setActiveScenarioId(id)
     * Lightweight scenario activation used by the Training app.
     * Sets state.activeScenarioId so any apps opened AFTER this call
     * receive the correct scenarioId in their APP_BOOT message.
     * Unlike startCapstoneScenario(), this does NOT reset bug tracking,
     * show the capstone overlay, or trigger scoring.
     * @param {string|null} id - e.g. "case-002", or null to clear.
     */
    setActiveScenarioId: function (id) {
      state.activeScenarioId = id || null;
      updateProgressWidget();
    },
    /**
     * closeApp(appId)
     * Closes all open windows for the given app ID.
     * Used by the Training app to reset the workspace when a new
     * scenario starts, so apps reopen with fresh scenario data.
     * @param {string} appId - e.g. "dynamics", "ado", "teams"
     */
    closeApp: function (appId) {
      var compositor = window.QA_OS && window.QA_OS.Compositor;
      if (!compositor) return;
      compositor.getWindows().forEach(function (win) {
        if (win.appId === appId) {
          closeWindow(win.id);
        }
      });
    },
    getAppHtml: function (appId) {
      return (typeof APP_HTML !== "undefined" && APP_HTML[appId]) || null;
    },
    completeTask: function (id) {
      addNotification("Task completed: " + id);
    },

    // Package API
    installPackage: function (jsonText) {
      return installPackageFromJson(jsonText);
    },
    removePackage: function (id) {
      uninstallPackage(id);
    },
    getPackages: function () {
      var p = {};
      for (var k in state.packages) {
        if (state.packages.hasOwnProperty(k)) p[k] = state.packages[k];
      }
      return p;
    },
    getAppInfo: function (id) {
      return getAppInfo(id);
    },

    // ── Capstone 2 Orchestration API (Sprint G) ────────────────────────────

    /**
     * getFiledBugs()
     * Returns all bugs the trainee has filed via ADO, mapped for the
     * Capstone 2 scoring engine. Each bug object includes the storyId
     * (derived from the AC Reference → SCENARIO_C2.bugs lookup), repro
     * steps, expected/actual results, severity, and title.
     *
     * Logs the return value with [C2] prefix for debugging.
     *
     * @returns {Array<Object>} Array of filed bug objects.
     */
    getFiledBugs: function () {
      console.log("[C2] getFiledBugs() called — state.bugsLogged has", state.bugsLogged.length, "entries");

      // Build acRef → storyId mapping from the scenario data
      var storyByAcRef = {};
      var scenario = (typeof SCENARIO_C2 !== "undefined") ? SCENARIO_C2 : null;
      if (scenario && scenario.bugs) {
        Object.keys(scenario.bugs).forEach(function (bugKey) {
          var bug = scenario.bugs[bugKey];
          if (bug.acRef && bug.storyId) {
            storyByAcRef[bug.acRef.toLowerCase()] = bug.storyId;
          }
        });
        console.log("[C2] getFiledBugs: built storyByAcRef map", JSON.stringify(storyByAcRef));
      } else {
        console.warn("[C2] getFiledBugs: SCENARIO_C2 not available — storyId mapping will be empty");
      }

      // Map each logged bug to the format Sprint G expects
      var mapped = (state.bugsLogged || []).map(function (b, idx) {
        var acRef = (b.acRef || "").trim();
        var storyId = storyByAcRef[acRef.toLowerCase()] || null;

        var mappedBug = {
          storyId:  storyId,
          title:    b.title   || "",
          severity: b.severity || "",
          repro:    b.repro   || "",
          expected: b.expected || "",
          actual:   b.actual  || "",
        };

        console.log("[C2] getFiledBugs: mapped bug #" + (idx + 1), JSON.stringify(mappedBug));
        return mappedBug;
      });

      console.log("[C2] getFiledBugs: returning", mapped.length, "bugs for scoring");
      return mapped;
    },

    /**
     * getScenario()
     * Returns the active scenario data (SCENARIO_C2) for the scoring engine.
     * Tries multiple access patterns to find it.
     *
     * Logs the result for debugging.
     *
     * @returns {Object|null} The SCENARIO_C2 object, or null.
     */
    getScenario: function () {
      // Try parent scope first (capstone-2.html loads capstone-scenario-2.js)
      try {
        if (window.parent && window.parent.SCENARIO_C2) {
          console.log("[C2] getScenario: found via window.parent.SCENARIO_C2");
          return window.parent.SCENARIO_C2;
        }
      } catch (e) {
        console.warn("[C2] getScenario: could not access window.parent", e);
      }

      // Then try own scope
      if (window.SCENARIO_C2) {
        console.log("[C2] getScenario: found via window.SCENARIO_C2");
        return window.SCENARIO_C2;
      }

      // Fallback: try QA_OS on parent
      try {
        if (window.parent && window.parent.QA_OS && window.parent.QA_OS.getScenario) {
          console.log("[C2] getScenario: found via window.parent.QA_OS.getScenario()");
          return window.parent.QA_OS.getScenario();
        }
      } catch (e) {}

      console.warn("[C2] getScenario: SCENARIO_C2 not found anywhere — scoring may be incomplete");
      return null;
    },

    /**
     * resetCapstone2(stage)
     * Resets the capstone 2 assessment to the given stage index.
     * Clears filed bugs, resets the stage counter, and persists to localStorage.
     * Called by capstone-2.html's retryCapstone2() when the trainee retries.
     *
     * Logs every step for debugging.
     *
     * @param {number} stage - Stage index to reset to (e.g. 3 = Day 1 Testing)
     */
    resetCapstone2: function (stage) {
      console.log("[C2] resetCapstone2(" + stage + ") called — resetting assessment state");

      // Log current state before reset
      console.log("[C2] resetCapstone2: pre-reset state", JSON.stringify({
        capstone2Stage: state.capstone2Stage,
        bugsLogged: state.bugsLogged.length,
        bugsFound: state.bugsFound.length,
        activeBugs: state.activeBugs.length,
      }));

      // Clear filed bugs
      state.bugsFound = [];
      state.bugsLogged = [];
      state.activeBugs = [];
      console.log("[C2] resetCapstone2: cleared bugsFound, bugsLogged, activeBugs");

      // Reset stage
      var targetStage = (typeof stage === "number" && stage >= 0) ? stage : 0;
      state.capstone2Stage = targetStage;
      state.capstone2InProg = true;

      // Persist to localStorage for the OS to pick up on reload
      try {
        var sessionRaw = localStorage.getItem(CAPSTONE_SESSION_KEY);
        if (sessionRaw) {
          var session = JSON.parse(sessionRaw);
          session.stage = targetStage;
          localStorage.setItem(CAPSTONE_SESSION_KEY, JSON.stringify(session));
          console.log("[C2] resetCapstone2: updated session stage to", targetStage);
        } else {
          console.warn("[C2] resetCapstone2: no capstone session found in localStorage");
        }
      } catch (e) {
        console.warn("[C2] resetCapstone2: could not persist reset to localStorage", e);
      }

      // Notify apps of the reset
      var bus = window.QA_OS && window.QA_OS.EventBus;
      if (bus && bus.postToAllApps) {
        bus.postToAllApps({
          type: "C2_RESET",
          stage: targetStage,
        });
        console.log("[C2] resetCapstone2: posted C2_RESET to all apps");
      }

      console.log("[C2] resetCapstone2: complete — stage=" + targetStage + ", ready for retry");
    },

    /**
     * getStage()
     * Returns the current capstone 2 stage (1-based, matching stage-1, stage-2, etc.).
     * Used by the Teams app to determine which stage messages to show.
     *
     * @returns {number} Current stage number (0 = not started, 1 = stage-1, etc.)
     */
    getStage: function () {
      return state.capstone2Stage || 0;
    },

    /**
     * advanceStage(unlockCondition)
     * Scans SCENARIO_C2.stages for a stage whose unlockCondition matches,
     * then advances state.capstone2Stage to that stage's 1-based index.
     * Persists the updated stage to localStorage so it survives iframe reload.
     *
     * Called by the Teams app when the trainee performs unlock actions:
     *   'CAPSTONE_2_LOADED'       → stage-1 (auto on boot)
     *   'STAGE_1_ACKNOWLEDGED'    → stage-2
     *   'ALL_STORIES_REVIEWED'    → stage-3
     *   'BUG_FILED_MINIMUM_ONE'   → stage-4
     *   'STANDUP_POSTED'          → stage-5
     *   'BUG_FILED_MINIMUM_TWO'   → stage-6
     *
     * @param {string} unlockCondition - The condition to look up in SCENARIO_C2.stages
     */
    advanceStage: function (unlockCondition) {
      console.log("[C2] advanceStage(" + unlockCondition + ") called — current stage=" + state.capstone2Stage);
      try {
        var scenario = (typeof SCENARIO_C2 !== "undefined") ? SCENARIO_C2 : null;
        if (!scenario || !scenario.stages) {
          console.warn("[C2] advanceStage: SCENARIO_C2 not available");
          return;
        }
        for (var i = 0; i < scenario.stages.length; i++) {
          var stage = scenario.stages[i];
          if (stage.unlockCondition === unlockCondition) {
            var newStage = i + 1; // 1-based
            if (newStage > state.capstone2Stage) {
              state.capstone2Stage = newStage;
              console.log("[C2] advanceStage: advanced to stage " + newStage + " (" + stage.name + ")");
              // Persist to localStorage
              try {
                var raw = localStorage.getItem(CAPSTONE_SESSION_KEY);
                if (raw) {
                  var session = JSON.parse(raw);
                  session.stage = newStage;
                  localStorage.setItem(CAPSTONE_SESSION_KEY, JSON.stringify(session));
                }
              } catch (e) {
                console.warn("[C2] advanceStage: could not persist stage", e);
              }
            } else {
              console.log("[C2] advanceStage: already at stage " + state.capstone2Stage + " — not regressing");
            }
            return;
          }
        }
        console.warn("[C2] advanceStage: no stage found with unlockCondition=" + unlockCondition);
      } catch (e) {
        console.warn("[C2] advanceStage error:", e);
      }
    },

    // Workspaces API
    saveWorkspace: function (name) {
      if (workspaces) return workspaces.save(name, getWorkspaceData());
    },
    restoreWorkspace: function (name) {
      if (workspaces)
        return workspaces.restore(name).then(function (data) {
          applyWorkspaceData(data);
        });
    },
    listWorkspaces: function () {
      return workspaces ? workspaces.list() : Promise.resolve([]);
    },

    saveAppState: function (appId, data) {
      try {
        localStorage.setItem("qa-app-" + appId, JSON.stringify(data));
      } catch (e) {}
    },
    loadAppState: function (appId) {
      try {
        var raw = localStorage.getItem("qa-app-" + appId);
        return raw ? JSON.parse(raw) : null;
      } catch (e) {
        return null;
      }
    },

    getMode: getMode,
    setMode: setMode,
    getSpeed: getSpeed,
    setSpeed: setSpeed,
    cycleSpeed: cycleSpeed,
    cycleMode: cycleMode,

    // Expose architecture layers for advanced use
    EventBus: bus,
    Compositor: compositor,
    Workspaces: workspaces,
  };

  window.QA_OS = coreApi;
  window.OS = coreApi;

  // Initialise keyboard shortcut registry (must run after DOM is ready)
  if (window.QA_SHORTCUTS) window.QA_SHORTCUTS.init();

  // Run boot-time health checks (after all modules are wired — toasts on failure)
  if (window.QA_HEALTH) window.QA_HEALTH.runBoot();
}

function bindEvents() {
  lockScreen.addEventListener("click", () => {
    if (!lockScreen.classList.contains("qa-lock-hidden")) unlock();
  });

  document.addEventListener("keydown", (e) => {
    // Close context menu on Escape
    if (e.key === "Escape") {
      var openMenu = document.querySelector(".qa-context-menu");
      if (openMenu) {
        openMenu.remove();
        return;
      }
    }

    if (!lockScreen.classList.contains("qa-lock-hidden")) unlock();
  });

  document.querySelectorAll(".qa-desktop-icon").forEach((icon) => {
    icon.addEventListener("dblclick", () => {
      const appId = icon.getAttribute("data-app");
      if (appId) openApp(appId);
    });
  });

  // ── FOLDER TOGGLE: double-click a data-folder element to expand/collapse ──
  document.querySelectorAll(".qa-desktop-folder").forEach((folder) => {
    folder.addEventListener("dblclick", function () {
      var folderId = this.getAttribute("data-folder");
      if (!folderId) return;
      var container = document.querySelector(
        '.qa-desktop-folder-children[data-folder="' + folderId + '"]'
      );
      if (!container) return;
      var isVisible = container.classList.contains("qa-folder-expanded");
      container.classList.toggle("qa-folder-expanded", !isVisible);
      this.classList.toggle("qa-folder-open", !isVisible);
    });
  });

  if (startSearchInput) {
    startSearchInput.addEventListener("input", function () {
      renderStartMenu(this.value.trim().toLowerCase());
    });
  }

  startButton.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleStartMenu();
    hideQuickPanel();
    hideNotifyCenter();
  });

  document.addEventListener("click", (e) => {
    // Dismiss any open context menu on any click outside it
    var openMenu = document.querySelector(".qa-context-menu");
    if (openMenu && !openMenu.contains(e.target)) {
      openMenu.remove();
    }

    if (!startMenu.contains(e.target) && !startButton.contains(e.target)) {
      hideStartMenu();
    }
    if (!quickPanel.contains(e.target) && !quickButton.contains(e.target)) {
      hideQuickPanel();
    }
    if (!notifyCenter.contains(e.target) && !notifyButton.contains(e.target)) {
      hideNotifyCenter();
    }
  });

  startMenu.addEventListener("click", (e) => {
    const btn = e.target.closest(".qa-start-item");
    if (!btn) return;

    if (btn.id === "qa-role-switcher") {
      toggleRole();
      hideStartMenu();
      return;
    }

    const appId = btn.getAttribute("data-app");
    if (appId) {
      openApp(appId);
      hideStartMenu();
    }
  });

  notifyButton.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleNotifyCenter();
    hideQuickPanel();
    hideStartMenu();
  });

  document
    .getElementById("qa-notify-clear")
    .addEventListener("click", clearNotifications);

  quickButton.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleQuickPanel();
    hideNotifyCenter();
    hideStartMenu();
  });

  themeLightBtn.addEventListener("click", () => setTheme("light"));
  themeDarkBtn.addEventListener("click", () => setTheme("dark"));

  if (brightnessSlider) {
    brightnessSlider.addEventListener("input", () => {
      state.brightness = Number(brightnessSlider.value) || 100;
      applyBrightness();
      saveState();
    });
  }

  taskviewButton.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleTaskview();
  });

  taskviewOverlay.addEventListener("click", (e) => {
    if (e.target === taskviewOverlay) hideTaskview();
  });

  if (submitBtn) {
    submitBtn.addEventListener("click", function () {
      runSubmit();
    });
  }

  if (submitTile) {
    submitTile.addEventListener("click", function () {
      runSubmit();
    });
  }

  // App message handling via EventBus
  var bus = window.QA_OS && window.QA_OS.EventBus;
  if (bus) {
                bus.onAppMessage("BUG_FOUND", function (msg) {
                    if (state.bugsFound.indexOf(msg.bugId) === -1) {
                        state.bugsFound.push(msg.bugId);
                        updateProgressWidget();
                    }
                    if (state.activeBugs.indexOf(msg.bugId) === -1) {
                        state.activeBugs.push(msg.bugId);
                    }
                    addNotification("🔍 System Alert: Defect detected in case data — " + msg.bugId + ". Check the AC Panel for details.");
                    console.log("[C2] BUG_FOUND: " + msg.bugId +
                        " (total found: " + state.bugsFound.length + ")");

                    // Immersion toast: Dynamics CRM-style notification
                    showNotifier("⚠️ Data validation issue: " + msg.bugId + " — review acceptance criteria", "warn");

                    // F6: Broadcast AC_VIOLATED to AC Panel when BUG_FOUND maps to an AC ref
                    var acRef = (msg.acRef) || null;
                    if (!acRef && state.activeScenarioId && window.SCENARIOS) {
                        var scenario = window.SCENARIOS[state.activeScenarioId];
                        if (scenario && scenario.acRefs && scenario.acRefs[msg.bugId]) {
                            acRef = scenario.acRefs[msg.bugId];
                        }
                    }
                    if (acRef) {
                        addNotification("📋 AC violated: " + acRef);
                        if (bus && bus.postToAllApps) {
                            bus.postToAllApps({
                                type: "AC_VIOLATED",
                                acRef: acRef,
                                bugId: msg.bugId,
                            });
                        }
                    }

                    // F11: Clip reacts to BUG_FOUND (not just BUG_LOGGED)
                    if (window.parent && window.parent.postMessage) {
                        window.parent.postMessage({
                            type: "BUG_FOUND",
                            bugId: msg.bugId,
                            acRef: acRef || null,
                        }, "*");
                    }
                });

    bus.onAppMessage("BUG_LOGGED", function (msg) {
      var bugData = msg.data || {};
      var bugKey =
        (bugData.acRef || "").trim().toLowerCase() + "|" +
        (bugData.title || "").trim().toLowerCase();
      var existingIndex = state.bugsLogged.findIndex(function (bug) {
        return (bug.acRef || "").trim().toLowerCase() + "|" +
          (bug.title || "").trim().toLowerCase() === bugKey;
      });
      if (existingIndex >= 0) {
        state.bugsLogged[existingIndex] = bugData;
      } else {
        state.bugsLogged.push(bugData);
      }
      addNotification(
        "📋 Bug report filed: " +
          (bugData.title ? bugData.title : "untitled"),
      );
      // Immersion toast: ADO-style notification
      showNotifier("✅ Bug submitted: " + (bugData.title ? bugData.title.substring(0, 60) : "untitled"), "info");
      console.log("[C2] BUG_LOGGED: title=" + (bugData.title || "(none)") +
        " severity=" + (bugData.severity || "(none)") +
        " acRef=" + (bugData.acRef || "(none)") +
        " repro=" + (typeof bugData.repro === "string" ? bugData.repro.substring(0, 30) + "..." : "(none)") +
        " expected=" + (bugData.expected ? "yes" : "no") +
        " actual=" + (bugData.actual ? "yes" : "no") +
        " (total logged: " + state.bugsLogged.length + ")");
    });

    bus.onAppMessage("BROWSER_STATE_CHANGED", function (msg) {
      var compositor = window.QA_OS && window.QA_OS.Compositor;
      if (compositor && typeof msg.winId === "number") {
        var win = compositor.getWindow(msg.winId);
        if (win) {
          win.browserState = msg.state || null;
          saveState();
        }
      }
    });
  }
}

// LOCK SCREEN

function unlock() {
  lockScreen.classList.add("qa-lock-hidden");
  // Notify the capstone wrapper page that the desktop is now accessible.
  // capstone-lab.html and capstone-2.html wait for this message before
  // starting the Clip guided intro — so Clip never fires during the lock screen.
  try { window.parent.postMessage({ type: "OS_UNLOCKED" }, "*"); } catch (e) {}
}

function startLockClock() {
  const update = () => {
    const now = new Date();
    const mm = String(now.getMinutes()).padStart(2, "0");

    let hours = now.getHours();
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12;
    hours = hours ? hours : 12;
    const hh = String(hours).padStart(2, "0");

    lockTime.textContent = `${hh}:${mm} ${ampm}`;
    lockDate.textContent = now.toLocaleDateString(undefined, {
      weekday: "long",
      month: "long",
      day: "numeric",
    });
  };
  update();
  setInterval(update, 30000);
}

// START MENU

function toggleStartMenu() {
  var isOpen = !startMenu.classList.contains("qa-start-menu-hidden");
  startMenu.classList.toggle("qa-start-menu-hidden");
  if (!isOpen) {
    // Menu was hidden — now it's open, focus the search input after a short delay
    // so the menu animation completes before the cursor appears.
    if (startSearchInput) {
      setTimeout(function () {
        startSearchInput.focus();
      }, 80);
    }
  }
}

function hideStartMenu() {
  startMenu.classList.add("qa-start-menu-hidden");
  if (startSearchInput) startSearchInput.value = "";
  renderStartMenu();
}

function renderStartMenu(filter) {
  if (!startGrid) return;
  startGrid.innerHTML = "";

  var apps = state.installedApps.filter(function (id) {
    if (!filter) return true;
    var app = getAppInfo(id);
    if (!app) return false;
    return (
      app.title.toLowerCase().indexOf(filter) !== -1 ||
      app.short.toLowerCase().indexOf(filter) !== -1 ||
      id.indexOf(filter) !== -1
    );
  });

  apps.forEach(function (id) {
    const app = getAppInfo(id);
    if (!app) return;
    const btn = document.createElement("button");
    btn.className = "qa-start-item";
    btn.setAttribute("data-app", id);
    btn.innerHTML = `
      <div class="qa-start-icon">${app.icon || "📦"}</div>
      <div class="qa-start-label">${app.short}</div>
    `;
    startGrid.appendChild(btn);
  });

  if (apps.length === 0) {
    var empty = document.createElement("div");
    empty.style.cssText =
      "grid-column:1/-1;text-align:center;padding:20px 0;color:var(--qa-muted-light);font-size:12px;";
    empty.textContent = "No results found";
    startGrid.appendChild(empty);
  }
}

// NOTIFICATIONS

function toggleNotifyCenter() {
  notifyCenter.classList.toggle("qa-notify-hidden");
}

function hideNotifyCenter() {
  notifyCenter.classList.add("qa-notify-hidden");
}

function addNotification(text) {
  const item = document.createElement("div");
  item.className = "qa-notify-item";
  item.textContent = text;
  notifyList.prepend(item);

  // Forward notification to parent page so Clip can announce it
  if (window.parent && window.parent !== window) {
    try {
      window.parent.postMessage({ type: "OS_NOTIFICATION", text: text }, "*");
    } catch (e) {}
  }
}

function clearNotifications() {
  notifyList.innerHTML = "";
}

// QUICK SETTINGS

function toggleQuickPanel() {
  quickPanel.classList.toggle("qa-quick-hidden");
}

function hideQuickPanel() {
  quickPanel.classList.add("qa-quick-hidden");
}

function setTheme(theme) {
  state.theme = theme === "dark" ? "dark" : "light";
  applyTheme();
  saveState();
}

function applyTheme() {
  shell.classList.toggle("qa-theme-dark", state.theme === "dark");
  shell.classList.toggle("qa-theme-light", state.theme !== "dark");
  if (themeLightBtn && themeDarkBtn) {
    themeLightBtn.classList.toggle("qa-quick-active", state.theme === "light");
    themeDarkBtn.classList.toggle("qa-quick-active", state.theme === "dark");
  }
}

function setBackground(id) {
  state.background = id || "default";
  applyBackground();
  saveState();
}

function applyBackground() {
  shell.dataset.bg = state.background || "default";
}

function applyBrightness() {
  const value = state.brightness || 100;
  document.documentElement.style.setProperty("--qa-brightness", value);
  if (brightnessSlider) brightnessSlider.value = value;
}

function setFidelity(mode) {
  const normalized = mode === "classic" ? "classic" : "win11";
  state.fidelity = normalized;
  applyFidelity();
  saveState();
  addNotification(
    normalized === "win11"
      ? "Visual mode: Windows 11 Mode"
      : "Visual mode: Classic Mode",
  );
}

function applyFidelity() {
  if (!shell) return;
  shell.dataset.fidelity = state.fidelity || "classic";
}

// TASK VIEW

function toggleTaskview() {
  if (taskviewOverlay.classList.contains("qa-taskview-hidden")) {
    renderTaskview();
    taskviewOverlay.classList.remove("qa-taskview-hidden");
  } else {
    hideTaskview();
  }
}

function hideTaskview() {
  taskviewOverlay.classList.add("qa-taskview-hidden");
}

function renderTaskview() {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  if (!compositor) return;

  // Brand colours for thumbnail preview blocks (extracted from app SVG icons)
  var BRAND_COLORS = {
    dynamics: "#0078D4",
    ado: "#5C2D91",
    ac: "#107C10",
    browser: "#0099BC",
    training: "#CA5010",
    teams: "#6264A7",
    settings: "#2B2B2B",
    word: "#185ABD",
    excel: "#107C10",
    powerpoint: "#C43E1C",
    reports: "#038387",
    inspector: "#69747C",
    qapache: "#E94560",
    qtube: "#FF0000",
    qoutlook: "#0078D4",
  };

  taskviewInner.innerHTML = "";
  var wins = compositor.getVisibleWindows();
  if (wins.length === 0) return;
  var activeId = compositor.getActiveId();

  wins.forEach(function (win) {
    var app = APPS[win.appId];
    var brandColor = (app && BRAND_COLORS[app.id]) || "#555";

    var thumb = document.createElement("div");
    thumb.className = "qa-taskview-thumb";
    if (win.id === activeId) {
      thumb.classList.add("qa-active");
    }

    // Colour preview block
    var preview = document.createElement("div");
    preview.className = "qa-taskview-thumb-preview";
    preview.style.backgroundColor = brandColor;
    thumb.appendChild(preview);

    const title = document.createElement("div");
    title.className = "qa-taskview-thumb-title";
    title.textContent = app ? app.title : `Window ${win.id}`;
    thumb.appendChild(title);

    thumb.addEventListener("click", (e) => {
      e.stopPropagation();
      focusWindow(win.id);
      hideTaskview();
    });

    taskviewInner.appendChild(thumb);
  });
}

// ROLE

function toggleRole() {
  state.role = state.role === "junior" ? "senior" : "junior";
  saveState();
  renderRole();
  renderAllWindows();
  addNotification(
    "Role switched to " +
      (state.role === "junior" ? "Junior Investigator" : "Senior Investigator"),
  );

  // Broadcast role change via EventBus
  var bus = window.QA_OS && window.QA_OS.EventBus;
  if (bus) {
    bus.postToAllApps({ type: "ROLE_CHANGE", role: state.role });
  }
}

function renderRole() {
  const label =
    state.role === "junior" ? "Junior Investigator" : "Senior Investigator";
  const short = state.role === "junior" ? "Junior" : "Senior";
  if (roleLabel) roleLabel.textContent = `Role: ${label}`;
  if (taskbarRole) taskbarRole.textContent = short;
}

// CAPSTONE / SCENARIO

function startCapstoneScenario(scenarioId) {
  state.capstoneScenarioId = scenarioId;
  state.activeScenarioId = scenarioId;
  state.bugsFound = [];
  state.bugsLogged = [];
  state.activeBugs = [];
  updateProgressWidget();

  const scenario = window.SCENARIOS && window.SCENARIOS[scenarioId];
  const brief = scenario ? scenario.brief : "Your assessment is ready.";

  const overlay = document.createElement("div");
  overlay.style.cssText = [
    "position:fixed",
    "inset:0",
    "z-index:50000",
    "background:rgba(0,0,0,0.72)",
    "display:flex",
    "align-items:center",
    "justify-content:center",
  ].join(";");

  const card = document.createElement("div");
  card.style.cssText = [
    "background:var(--qa-glass-dark)",
    "border-width:1px",
    "border-style:solid",
    "border-color:var(--qa-border-mid)",
    "border-radius:12px",
    "padding:32px 36px",
    "max-width:560px",
    "color:var(--qa-text-light)",
    "font-family:var(--qa-font)",
  ].join(";");

  card.innerHTML =
    '<div style="font-size:18px;font-weight:600;margin-bottom:16px;">Your Assignment</div>' +
    '<pre style="white-space:pre-wrap;font-family:inherit;font-size:13px;line-height:1.6;' +
    'margin-bottom:24px;color:var(--qa-text-light);">' +
    brief +
    "</pre>" +
    '<button id="qa-brief-start" style="background:var(--qa-accent);color:#000;' +
    "border:none;border-radius:6px;padding:10px 24px;font-size:13px;" +
    'font-weight:600;cursor:pointer;">Start Assessment</button>';

  overlay.appendChild(card);
  document.body.appendChild(overlay);

  var startBtn = document.getElementById("qa-brief-start");
  if (startBtn) {
    startBtn.addEventListener("click", function () {
      var compositor = window.QA_OS && window.QA_OS.Compositor;
      overlay.remove();

      openApp("dynamics");
      openApp("ac");

      setTimeout(function () {
        if (compositor) {
          var workBrowser = compositor.getWindows().find(function (w) {
            return w.appId === "browser" && w.isWorkBrowser === true;
          });
          if (workBrowser) {
            compositor.setLayout(workBrowser.id, "maximized");
          } else {
            var anyBrowser = compositor.getWindows().find(function (w) {
              return w.appId === "browser";
            });
            if (anyBrowser) compositor.setLayout(anyBrowser.id, "maximized");
          }
        }

        renderAllWindows();
        renderTaskbar();
      }, 100);
    });
  }

  renderTaskbar();
}

// WINDOW MANAGEMENT

function openApp(appId) {
  // Redirect Dynamics, ADO, and AC to the Work Browser instead of a standalone window
  if (appId === "dynamics" || appId === "ado" || appId === "ac") {
    openAppAsBrowserTab(appId);
    return;
  }

  if (!isInstalled(appId)) return;
  var app = APPS[appId];
  if (!app) return;

  var compositor = window.QA_OS && window.QA_OS.Compositor;
  if (!compositor) return;

  var win = compositor.createWindow(appId, {
    isWorkBrowser: state._openingWorkBrowser === true,
  });
  state._openingWorkBrowser = false;

  saveState();
  renderAllWindows();
  renderTaskbar();
  addNotification("Opened " + app.title);
}

function closeWindow(winId) {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  if (!compositor) return;
  var win = compositor.getWindow(winId);
  if (!win) return;
  var app = APPS[win.appId];

  var el = windowArea.querySelector('[data-win-id="' + winId + '"]');
  if (el) {
    el.classList.add("qa-closing");
    setTimeout(function () {
      actuallyCloseWindow(winId, app);
    }, 160);
  } else {
    actuallyCloseWindow(winId, app);
  }
}

function actuallyCloseWindow(winId, app) {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  if (!compositor) return;
  if (!compositor.destroyWindow(winId)) return;
  saveState();
  renderAllWindows();
  renderTaskbar();
  if (app) addNotification("Closed " + app.title);
}

function focusWindow(winId) {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  if (!compositor) return;
  var wasMinimized = compositor.focus(winId);
  if (!wasMinimized) {
    // Already visible — just update z-index and active class
    var wins = compositor.getWindows();
    for (var i = 0; i < wins.length; i++) {
      var w = wins[i];
      var el = windowArea.querySelector('[data-win-id="' + w.id + '"]');
      if (!el) continue;
      el.style.zIndex = w.z;
      el.classList.toggle("qa-active", w.id === winId);
      var overlay = el.querySelector(".qa-focus-overlay");
      if (overlay) overlay.style.display = w.id === winId ? "none" : "block";
    }
  } else {
    renderAllWindows();
  }
  saveState();
  renderTaskbar();
}

function toggleMaximize(winId) {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  if (!compositor) return;
  compositor.toggleMaximize(winId);
  saveState();
  renderAllWindows();
}

function minimizeWindow(winId) {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  if (!compositor) return;
  compositor.minimize(winId);
  saveState();
  renderAllWindows();
  renderTaskbar();
}

function applyLayoutClass(el, layout) {
  el.classList.remove("snap-left", "snap-right", "maximized");
  if (layout === "snap-left") el.classList.add("snap-left");
  if (layout === "snap-right") el.classList.add("snap-right");
  if (layout === "maximized") el.classList.add("maximized");
}

// RENDER WINDOWS

function renderAllWindows() {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  var bus = window.QA_OS && window.QA_OS.EventBus;
  if (!compositor) return;

  windowArea.innerHTML = "";
  var wins = compositor.getWindows();
  var activeId = compositor.getActiveId();

  wins
    .slice()
    .sort(function (a, b) {
      return a.z - b.z;
    })
    .forEach(function (win) {
      if (win.minimized) return;

      var app = APPS[win.appId];
      var el = document.createElement("div");
      el.className = "qa-window";
      if (win.id === activeId) el.classList.add("qa-active");
      el.style.zIndex = win.z;
      el.dataset.winId = win.id;

      applyLayoutClass(el, win.layout);

      if (win.layout === "normal") {
        if (typeof win.x === "number") el.style.left = win.x + "px";
        if (typeof win.y === "number") el.style.top = win.y + "px";
        if (typeof win.width === "number") el.style.width = win.width + "px";
        if (typeof win.height === "number") el.style.height = win.height + "px";
      }

      var header = document.createElement("div");
      header.className = "qa-window-header";
      header.innerHTML =
        '<div class="qa-window-title">' +
        (app ? app.title : "Window") +
        "</div>" +
        '<div class="qa-window-controls">' +
        '<button class="qa-window-btn minimize" title="Minimize"></button>' +
        '<button class="qa-window-btn maximize" title="Maximize"></button>' +
        '<button class="qa-window-btn close" title="Close"></button>' +
        "</div>";
      el.appendChild(header);

      // Resize handles (right, bottom, bottom-right corner)
      var rh = document.createElement("div");
      rh.className = "qa-resize-handles";
      rh.innerHTML =
        '<div class="qa-resize-h qa-resize-e" data-dir="e"></div>' +
        '<div class="qa-resize-h qa-resize-s" data-dir="s"></div>' +
        '<div class="qa-resize-h qa-resize-se" data-dir="se"></div>';
      el.appendChild(rh);

      // Snap layout flyout attached to header
      var flyout = document.createElement("div");
      flyout.className = "qa-snap-flyout";
      flyout.innerHTML =
        '<button class="qa-snap-cell qa-snap-max" data-layout="maximized" title="Maximize"></button>' +
        '<button class="qa-snap-cell qa-snap-tl" data-layout="snap-tl" title="Top-left"></button>' +
        '<button class="qa-snap-cell qa-snap-tr" data-layout="snap-tr" title="Top-right"></button>' +
        '<button class="qa-snap-cell qa-snap-bl" data-layout="snap-bl" title="Bottom-left"></button>' +
        '<button class="qa-snap-cell qa-snap-br" data-layout="snap-br" title="Bottom-right"></button>';
      header.appendChild(flyout);

      var body = document.createElement("div");
      body.className = "qa-window-body";

      if (win.appId === "ac") {
        var acIframe = document.createElement("iframe");
        acIframe.className = "qa-window-frame";
        acIframe.srcdoc = APP_HTML && APP_HTML["ac"] ? APP_HTML["ac"] : "";
        acIframe.addEventListener("load", function () {
          try {
            var bootMsg = {
              type: "APP_BOOT",
              appId: "ac",
              role: state.role,
              theme: state.theme,
              sessionId: win.id + "-" + Date.now().toString(36),
              scenarioId: state.activeScenarioId || null,
              activeBugs: state.activeBugs || [],
              // V1.5-4: enriched payload from shared db.js
              student: state.studentData
                ? { name: state.studentData.name, caseId: state.studentData.caseId }
                : null,
              progress: state.studentProgress || null,
            };
            // Derive scenario data from SCENARIOS if an active scenario is set
            if (state.activeScenarioId && window.SCENARIOS) {
              var scenario = window.SCENARIOS[state.activeScenarioId];
              if (scenario) {
                bootMsg.scenario = {
                  id: state.activeScenarioId,
                  crmState: scenario.crmState || null,
                  expectedBugs: scenario.expectedBugs || null,
                  acRefs: scenario.acRefs || null,
                };
              }
            }
            acIframe.contentWindow.postMessage(bootMsg, "*");
          } catch (e) {}
          if (bus) bus.registerAppWindow(win.id, acIframe);
        });
        body.appendChild(acIframe);
      } else if (APP_HTML && APP_HTML[win.appId]) {
        var iframe = document.createElement("iframe");
        iframe.className = "qa-window-frame";
        iframe.srcdoc = APP_HTML[win.appId];

        iframe.addEventListener("load", function () {
          if (bus) bus.registerAppWindow(win.id, iframe);
          try {
            var bootMsg = {
              type: "APP_BOOT",
              appId: win.appId,
              winId: win.id,
              role: state.role,
              theme: state.theme,
              sessionId: win.id + "-" + Date.now().toString(36),
              scenarioId: state.activeScenarioId || null,
              activeBugs: state.activeBugs || [],
              // V1.5-4: enriched payload from shared db.js
              student: state.studentData
                ? { name: state.studentData.name, caseId: state.studentData.caseId }
                : null,
              progress: state.studentProgress || null,
            };
            // Derive scenario data from SCENARIOS if an active scenario is set
            if (state.activeScenarioId && window.SCENARIOS) {
              var bootScenario = window.SCENARIOS[state.activeScenarioId];
              if (bootScenario) {
                bootMsg.scenario = {
                  id: state.activeScenarioId,
                  crmState: bootScenario.crmState || null,
                  expectedBugs: bootScenario.expectedBugs || null,
                  acRefs: bootScenario.acRefs || null,
                };
              }
            }
            if (win.appId === "browser") {
              if (win.browserState) bootMsg.browserState = win.browserState;
              if (state._browserTabRequest) {
                bootMsg.requestedTab = state._browserTabRequest;
                state._browserTabRequest = null;
              }
            }

            // Pass teamsThread data to the Teams app so it can render
            // scripted scenario messages (case assignments, stand-ups, etc.)
            if (win.appId === "teams" && state.activeScenarioId) {
              var scenarioData =
                window.SCENARIOS && window.SCENARIOS[state.activeScenarioId];
              if (scenarioData && scenarioData.teamsThread) {
                bootMsg.teamsThread = scenarioData.teamsThread;
              }
            }

            iframe.contentWindow.postMessage(bootMsg, "*");
            flushBrowserMessageQueue();
          } catch (e) {}
        });

        body.appendChild(iframe);
      } else {
        body.textContent = "App not configured.";
      }

      var focusOverlay = document.createElement("div");
      focusOverlay.className = "qa-focus-overlay";
      focusOverlay.style.display = win.id === activeId ? "none" : "block";
      focusOverlay.addEventListener("mousedown", function (e) {
        e.stopPropagation();
        focusWindow(win.id);
      });
      body.appendChild(focusOverlay);

      el.appendChild(body);
      windowArea.appendChild(el);

      header.addEventListener("mousedown", function (e) {
        startDrag(e, el, win.id);
      });

      header.addEventListener("contextmenu", function (e) {
        e.preventDefault();
        e.stopPropagation();
        showWindowContextMenu(win.id, e.clientX, e.clientY);
      });

      header.querySelector(".close").addEventListener("click", function (e) {
        e.stopPropagation();
        closeWindow(win.id);
      });

      header.addEventListener("dblclick", function () {
        toggleMaximize(win.id);
      });

      var maxBtn = header.querySelector(".maximize");
      maxBtn.addEventListener("click", function (e) {
        e.stopPropagation();
        toggleMaximize(win.id);
      });
      maxBtn.addEventListener("mouseenter", function () {
        flyout.classList.add("visible");
      });
      flyout.addEventListener("mouseleave", function () {
        flyout.classList.remove("visible");
      });
      flyout.querySelectorAll(".qa-snap-cell").forEach(function (cell) {
        cell.addEventListener("click", function (e) {
          e.stopPropagation();
          var layout = cell.getAttribute("data-layout");
          if (layout) {
            compositor.setLayout(win.id, layout);
            saveState();
            renderAllWindows();
          }
          flyout.classList.remove("visible");
        });
      });

      header.querySelector(".minimize").addEventListener("click", function (e) {
        e.stopPropagation();
        minimizeWindow(win.id);
      });

      // Resize handle events
      [].forEach.call(el.querySelectorAll(".qa-resize-h"), function (h) {
        h.addEventListener("mousedown", function (e) {
          e.stopPropagation();
          e.preventDefault();
          startResize(e, win.id, h.getAttribute("data-dir"));
        });
      });

      el.addEventListener("mousedown", function () {
        focusWindow(win.id);
      });
    });
}

// ── BROWSER TAB ROUTING ──────────────────────────────────────────────────
// Two types of browser windows:
// 1. Reference Browser (Home + QA Guidelines) — opened via Browser icon
// 2. Work Browser (Dynamics + ADO + AC tabs) — opened via Dynamics/ADO/AC icons

function openAppAsBrowserTab(appId) {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  if (!compositor) return;

  var workBrowser = compositor.getWindows().find(function (w) {
    return w.appId === "browser" && w.isWorkBrowser === true;
  });
  if (workBrowser) {
    focusWindow(workBrowser.id);
    postToBrowser({ type: "OPEN_APP_TAB", appId: appId }, workBrowser.id);
  } else {
    var anyBrowser = compositor.getWindows().find(function (w) {
      return w.appId === "browser";
    });
    if (anyBrowser && !anyBrowser.isWorkBrowser) {
      createWorkBrowser(appId);
    } else {
      state._browserTabRequest = appId;
      state._openingWorkBrowser = true;
      openApp("browser");
    }
  }
}

function createWorkBrowser(appId) {
  if (!isInstalled("browser")) return;
  var app = APPS["browser"];
  if (!app) return;

  var compositor = window.QA_OS && window.QA_OS.Compositor;
  if (!compositor) return;

  var win = compositor.createWindow("browser", { isWorkBrowser: true });
  state._browserTabRequest = appId;
  state._openingWorkBrowser = false;
  saveState();
  renderAllWindows();
  renderTaskbar();
  addNotification("Opened " + app.title);

  // Maximize work browser to ensure Dynamics/ADO layouts have enough room
  setTimeout(function () {
    compositor.setLayout(win.id, "maximized");
    renderAllWindows();
    renderTaskbar();
  }, 150);
}

function postToBrowser(msg, specificWinId) {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  var bus = window.QA_OS && window.QA_OS.EventBus;
  if (!compositor) return;

  var browserWin;
  if (specificWinId) {
    browserWin = compositor.getWindow(specificWinId);
  } else {
    browserWin = compositor.getWindows().find(function (w) {
      return w.appId === "browser";
    });
  }
  if (!browserWin) return;

  if (bus) {
    var sent = bus.postToApp(browserWin.id, msg);
    if (!sent) {
      bus.queueForApp(browserWin.id, msg);
    }
  }
}

function flushBrowserMessageQueue() {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  var bus = window.QA_OS && window.QA_OS.EventBus;
  if (!compositor || !bus) return;
  var browserWin = compositor.getWindows().find(function (w) {
    return w.appId === "browser";
  });
  if (!browserWin) return;
  bus.flushQueue(browserWin.id);
}

// DRAG + SNAP

function startDrag(e, el, winId) {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  if (!compositor) return;
  var win = compositor.getWindow(winId);
  if (!win) return;
  if (win.layout === "maximized") return;

  focusWindow(winId);

  var rect = el.getBoundingClientRect();
  var offsetX = e.clientX - rect.left;
  var offsetY = e.clientY - rect.top;
  var startX = e.clientX;
  var startY = e.clientY;

  var hasMoved = false;

  var shield = document.createElement("div");
  shield.style.cssText =
    "position:fixed;inset:0;z-index:2147483647;cursor:move;";

  function onMove(ev) {
    if (!hasMoved) {
      var dx = ev.clientX - startX;
      var dy = ev.clientY - startY;
      if (Math.abs(dx) < 5 && Math.abs(dy) < 5) return;
      hasMoved = true;
      e.preventDefault();
      document.body.appendChild(shield);
    }

    var x = ev.clientX - offsetX;
    var y = ev.clientY - offsetY;
    el.style.left = x + "px";
    el.style.top = y + "px";
    win.x = x;
    win.y = y;
  }

  function onUp(ev) {
    document.removeEventListener("mousemove", onMove);
    document.removeEventListener("mouseup", onUp);
    if (shield.parentNode) shield.remove();

    if (!hasMoved) return;

    var vw = windowArea.clientWidth;
    var sm = 24;
    var layout = "normal";

    if (ev.clientX < sm) layout = "snap-left";
    else if (ev.clientX > vw - sm) layout = "snap-right";
    else if (ev.clientY < sm) layout = "maximized";

    compositor.setLayout(winId, layout);
    saveState();
    renderAllWindows();
  }

  document.addEventListener("mousemove", onMove);
  document.addEventListener("mouseup", onUp);
}

// TASKBAR

function renderTaskbar() {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  if (!compositor) return;

  taskbarApps.innerHTML = "";

  var byApp = compositor.getWindowsGroupedByApp();
  var activeId = compositor.getActiveId();

  Object.keys(byApp).forEach(function (appId) {
    var app = APPS[appId];
    var wins = byApp[appId];
    var isActive = wins.some(function (w) {
      return w.id === activeId;
    });
    var hasVisible = wins.some(function (w) {
      return !w.minimized;
    });

    var btn = document.createElement("button");
    btn.className = "qa-taskbar-app-btn";
    if (isActive && hasVisible) btn.classList.add("qa-active");
    if (hasVisible) btn.classList.add("running");
    if (isActive && hasVisible) btn.classList.add("focused");
    btn.innerHTML =
      '<span class="qa-taskbar-app-icon">' +
      (app ? app.icon : "📦") +
      "</span>" +
      (appId === 'qoutlook' ? '<span class="qa-taskbar-badge" id="qa-badge-qoutlook" style="display:none;position:absolute;top:2px;right:2px;min-width:14px;height:14px;border-radius:7px;background:#e81123;color:#fff;font-size:9px;font-weight:700;line-height:14px;text-align:center;padding:0 4px;pointer-events:none;">0</span>' : '');
    btn.title = app ? app.title : appId;
    btn.dataset.label = app ? app.short : appId;
    btn.style.position = 'relative'; // for badge positioning

    btn.addEventListener("click", function () {
      var visible = wins.filter(function (w) {
        return !w.minimized;
      });
      if (visible.length === 0) {
        wins[0].minimized = false;
        compositor.focus(wins[0].id);
      } else {
        var topWin = visible.reduce(function (a, b) {
          return a.z > b.z ? a : b;
        });
        if (activeId === topWin.id) {
          visible.forEach(function (w) {
            w.minimized = true;
          });
          compositor.focus(null);
        } else {
          focusWindow(topWin.id);
          return;
        }
      }
      saveState();
      renderAllWindows();
      renderTaskbar();
    });

    btn.addEventListener("contextmenu", function (e) {
      e.preventDefault();
      wins.slice().forEach(function (w) {
        actuallyCloseWindow(w.id, app);
      });
    });

    taskbarApps.appendChild(btn);
  });

  if (submitBtn) {
    submitBtn.style.display = state.capstoneScenarioId ? "inline-flex" : "none";
  }
  if (submitTile) {
    submitTile.style.display = state.capstoneScenarioId
      ? "inline-flex"
      : "none";
  }
}

// CLOCK

function startClock() {
  const dateEl = document.getElementById("qa-taskbar-date");

  function updateClock() {
    const now = new Date();
    let hh = now.getHours();
    const mm = String(now.getMinutes()).padStart(2, "0");
    const ampm = hh >= 12 ? "PM" : "AM";
    hh = hh % 12 || 12;
    if (clockEl) clockEl.textContent = `${hh}:${mm} ${ampm}`;
    if (dateEl) {
      dateEl.textContent = now.toLocaleDateString(undefined, {
        weekday: "short",
        month: "numeric",
        day: "numeric",
      });
    }
  }
  _clockUpdateFn = updateClock;
  updateClock();
  scheduleClock();
}

function scheduleClock() {
  if (_clockInterval) clearInterval(_clockInterval);
  if (!_clockUpdateFn) return;
  var ms = Math.round(15000 / (state.speed || 1));
  _clockInterval = setInterval(_clockUpdateFn, ms);
}

// ── PROGRESS WIDGET ──────────────────────────────────────────────────────────

function injectDesktopWidgets() {
  var style = document.createElement('style');
  style.textContent = [
    '#qa-progress-widget {',
    '  position: fixed; top: 60px; right: 20px;',
    '  background: rgba(255,255,255,0.92);',
    '  border: 1px solid #d0d0d0;',
    '  border-radius: 8px;',
    '  padding: 8px 14px;',
    '  font-size: 12px;',
    '  font-family: "Segoe UI", system-ui, sans-serif;',
    '  color: #333;',
    '  box-shadow: 0 2px 12px rgba(0,0,0,0.1);',
    '  z-index: 500;',
    '  backdrop-filter: blur(4px);',
    '  display: none;',
    '  pointer-events: none;',
    '  user-select: none;',
    '}',
    '#qa-progress-widget.visible { display: flex; align-items: center; gap: 10px; }',
    '#qa-speed-btn {',
    '  background: rgba(255,255,255,0.08);',
    '  border-width: 1px; border-style: solid; border-color: var(--qa-border-mid);',
    '  border-radius: 10px;',
    '  padding: 2px 8px;',
    '  font-size: 10px;',
    '  font-family: var(--qa-font);',
    '  color: var(--qa-text-light);',
    '  cursor: pointer;',
    '  line-height: 1.6;',
    '  margin-right: 4px;',
    '}',
    '#qa-speed-btn:hover { background: var(--qa-hover-dark); }',
    '#qa-mode-pill {',
    '  border: none;',
    '  background: rgba(0,120,212,0.15);',
    '  color: #0078D4;',
    '  border-radius: 4px;',
    '  padding: 2px 8px;',
    '  font-size: 11px;',
    '  font-family: "Segoe UI", system-ui, sans-serif;',
    '  cursor: pointer;',
    '  pointer-events: auto;',
    '  line-height: 1.6;',
    '}',
    '#qa-mode-pill:hover { background: rgba(0,120,212,0.25); }',
  ].join('\n');
  document.head.appendChild(style);

  var widget = document.createElement('div');
  widget.id = 'qa-progress-widget';
  widget.innerHTML = '<span id="qa-progress-text"></span><button id="qa-mode-pill">🎓 Guided</button>';
  document.body.appendChild(widget);
  _progressWidget = widget;
  _modePill = document.getElementById('qa-mode-pill');
  _modePill.addEventListener('click', cycleMode);

  var taskbarRight = document.querySelector('.qa-taskbar-right');
  var clockWidget = document.querySelector('.qa-clock-widget');
  if (taskbarRight && clockWidget) {
    var btn = document.createElement('button');
    btn.id = 'qa-speed-btn';
    btn.textContent = '1\u00D7';
    btn.title = 'Simulation speed';
    btn.addEventListener('click', cycleSpeed);
    _speedBtn = btn;
    taskbarRight.insertBefore(btn, clockWidget);
  }
}

function updateProgressWidget() {
  if (!_progressWidget) return;
  if (state.activeScenarioId) {
    var scenario = window.SCENARIOS && window.SCENARIOS[state.activeScenarioId];
    var expected = (scenario && scenario.expectedBugs) ? scenario.expectedBugs.length : 0;
    var found = (state.bugsFound || []).length;
    var textEl = document.getElementById('qa-progress-text');
    if (textEl) textEl.textContent = '\uD83D\uDD0D Progress: ' + found + '/' + expected + ' bugs found';
    _modePill.textContent = state.mode === 'guided' ? '\uD83C\uDF93 Guided' : '\uD83D\uDD13 Free';
    _progressWidget.classList.add('visible');
  } else {
    _progressWidget.classList.remove('visible');
  }
}

function cycleSpeed() {
  var speeds = [1, 2, 4];
  var idx = speeds.indexOf(state.speed);
  state.speed = speeds[(idx + 1) % speeds.length];
  if (_speedBtn) _speedBtn.textContent = state.speed + '\u00D7';
  scheduleClock();
  var bus = window.QA_OS && window.QA_OS.EventBus;
  if (bus) bus.postToAllApps({ type: 'SPEED_CHANGE', speed: state.speed });
}

function cycleMode() {
  state.mode = state.mode === 'guided' ? 'free' : 'guided';
  updateProgressWidget();
  var bus = window.QA_OS && window.QA_OS.EventBus;
  if (bus) bus.postToAllApps({ type: 'MODE_CHANGE', mode: state.mode });
}

function getMode() { return state.mode; }
function setMode(m) { state.mode = m === 'free' ? 'free' : 'guided'; updateProgressWidget(); }
function getSpeed() { return state.speed; }
function setSpeed(s) { state.speed = [1, 2, 4].indexOf(s) >= 0 ? s : 1; if (_speedBtn) _speedBtn.textContent = state.speed + '\u00D7'; scheduleClock(); }

// APPS INSTALL/UNINSTALL

function isInstalled(id) {
  return state.installedApps.includes(id);
}

function installApp(id) {
  if (!APPS[id]) return;
  if (!isInstalled(id)) state.installedApps.push(id);
  saveState();
  renderStartMenu();
}

function uninstallApp(id) {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  state.installedApps = state.installedApps.filter(function (x) {
    return x !== id;
  });
  // Close all windows for this app via compositor
  if (compositor) {
    var wins = compositor.getWindowsByApp(id);
    wins.slice().forEach(function (w) {
      compositor.destroyWindow(w.id);
    });
  }
  saveState();
  renderAllWindows();
  renderTaskbar();
  renderStartMenu();
}

// ── PACKAGE / APP RESOLUTION ──────────────────────────────────────────────

function getAppInfo(id) {
  return APPS[id] || (state.packages && state.packages[id]) || null;
}

// ── PACKAGE PERSISTENCE ────────────────────────────────────────────────────

function savePackages() {
  try {
    localStorage.setItem(PACKAGES_KEY, JSON.stringify(state.packages || {}));
  } catch (e) {
    // storage full or disabled — fail silently
  }
}

function loadPackages() {
  try {
    var raw = localStorage.getItem(PACKAGES_KEY);
    if (raw) {
      var parsed = JSON.parse(raw);
      state.packages = {};
      for (var k in parsed) {
        if (parsed.hasOwnProperty(k)) state.packages[k] = parsed[k];
      }
    } else {
      state.packages = {};
    }
  } catch (e) {
    state.packages = {};
  }
}

// ── PACKAGE INSTALL / UNINSTALL ────────────────────────────────────────────

function validatePackage(pkg) {
  if (!pkg || typeof pkg !== "object")
    return "Package must be a JSON object.";
  if (!pkg.id || typeof pkg.id !== "string")
    return "Package must have a string 'id'.";
  if (!/^[a-zA-Z0-9_-]+$/.test(pkg.id))
    return "Package id must be alphanumeric (hyphens/underscores allowed).";
  if (!pkg.title || typeof pkg.title !== "string")
    return "Package must have a string 'title'.";
  if (!pkg.content || typeof pkg.content !== "string")
    return "Package must have a string 'content' (inline HTML).";
  if (!pkg.icon || typeof pkg.icon !== "string")
    return "Package must have a string 'icon' (emoji or text).";

  // Reserved built-in IDs that cannot be overridden
  var reserved = [
    "dynamics", "ado", "ac", "training", "settings",
    "browser", "teams", "word", "excel", "powerpoint",
    "reports", "inspector", "qapache", "qtube", "qoutlook",
  ];
  if (reserved.indexOf(pkg.id) !== -1)
    return 'Package id "' + pkg.id + '" is reserved.';

  return null; // valid
}

function installPackageFromJson(jsonText) {
  if (typeof jsonText !== "string") {
    jsonText = JSON.stringify(jsonText);
  }

  var pkg;
  try {
    pkg = JSON.parse(jsonText);
  } catch (e) {
    return { success: false, error: "Invalid JSON: " + e.message };
  }

  var err = validatePackage(pkg);
  if (err) {
    return { success: false, error: err };
  }

  // Already installed?
  if (state.packages[pkg.id]) {
    return {
      success: false,
      error: 'Package "' + pkg.id + '" is already installed.',
    };
  }

  // Register package
  state.packages[pkg.id] = pkg;

  // Auto-install (add to start menu)
  if (state.installedApps.indexOf(pkg.id) === -1) {
    state.installedApps.push(pkg.id);
  }

  savePackages();
  saveState();
  renderStartMenu();

  return { success: true };
}

function uninstallPackage(id) {
  if (!state.packages[id]) return;

  delete state.packages[id];

  state.installedApps = state.installedApps.filter(function (x) {
    return x !== id;
  });

  // Close any open windows for this package
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  if (compositor) {
    var wins = compositor.getWindowsByApp(id);
    wins.slice().forEach(function (w) {
      compositor.destroyWindow(w.id);
    });
  }

  savePackages();
  saveState();
  renderAllWindows();
  renderTaskbar();
  renderStartMenu();
  renderPackageList();
}

// ── PACKAGE MANAGER UI ─────────────────────────────────────────────────────

function showPackageManager() {
  if (!pkgMgrOverlay) return;
  renderPackageList();
  pkgMgrOverlay.classList.remove("qa-pkg-hidden");
  if (startMenu) startMenu.classList.add("qa-hidden");
}

function hidePackageManager() {
  if (!pkgMgrOverlay) return;
  pkgMgrOverlay.classList.add("qa-pkg-hidden");
}

function renderPackageList() {
  if (!pkgMgrList || !pkgMgrEmpty) return;
  var ids = Object.keys(state.packages || {});
  pkgMgrList.innerHTML = "";

  if (ids.length === 0) {
    pkgMgrEmpty.style.display = "";
    return;
  }
  pkgMgrEmpty.style.display = "none";

  ids.forEach(function (id) {
    var pkg = state.packages[id];
    if (!pkg) return;

    var row = document.createElement("div");
    row.className = "qa-pkg-row";

    var info = document.createElement("div");
    info.className = "qa-pkg-row-info";

    var iconSpan = document.createElement("span");
    iconSpan.className = "qa-pkg-row-icon";
    iconSpan.textContent = pkg.icon || "📦";

    var nameSpan = document.createElement("span");
    nameSpan.className = "qa-pkg-row-name";
    nameSpan.textContent = pkg.title;

    var idSpan = document.createElement("span");
    idSpan.className = "qa-pkg-row-id";
    idSpan.textContent = id;

    info.appendChild(iconSpan);
    info.appendChild(nameSpan);
    info.appendChild(idSpan);

    var btn = document.createElement("button");
    btn.className = "qa-pkg-row-uninstall";
    btn.textContent = "Uninstall";
    btn.addEventListener("click", function () {
      if (confirm('Are you sure you want to uninstall "' + pkg.title + '"?')) {
        uninstallPackage(id);
      }
    });

    row.appendChild(info);
    row.appendChild(btn);
    pkgMgrList.appendChild(row);
  });
}

function setupPackageInstaller() {
  if (!pkgFileInput) return;
  if (!installPkgBtn) installPkgBtn = document.getElementById("qa-install-package-btn");
  if (!pkgManagerBtn) pkgManagerBtn = document.getElementById("qa-pkg-manager-btn");

  // Start menu "Install Package" button
  if (installPkgBtn) {
    installPkgBtn.addEventListener("click", function () {
      if (startMenu) startMenu.classList.add("qa-hidden");
      pkgFileInput.click();
    });
  }

  // Add/Remove Programs button
  if (pkgManagerBtn) {
    pkgManagerBtn.addEventListener("click", function () {
      showPackageManager();
    });
  }

  // Close button
  if (pkgMgrClose) {
    pkgMgrClose.addEventListener("click", hidePackageManager);
  }

  // Click outside panel to close
  if (pkgMgrOverlay) {
    pkgMgrOverlay.addEventListener("click", function (e) {
      if (e.target === pkgMgrOverlay) hidePackageManager();
    });
  }

  // Install button in package manager panel
  if (pkgMgrInstallBtn) {
    pkgMgrInstallBtn.addEventListener("click", function () {
      pkgFileInput.click();
    });
  }

  // File input change handler
  pkgFileInput.addEventListener("change", function () {
    var file = pkgFileInput.files && pkgFileInput.files[0];
    if (!file) return;

    var reader = new FileReader();
    reader.onload = function (e) {
      var result = installPackageFromJson(e.target.result);
      if (!result.success) {
        alert("Install failed: " + result.error);
      } else {
        addNotification("Package installed successfully.");
      }
    };
    reader.onerror = function () {
      alert("Failed to read file.");
    };
    reader.readAsText(file);

    // Reset so re-selecting same file triggers change
    pkgFileInput.value = "";
  });
}

// STATE PERSISTENCE

function saveState() {
  try {
    var compositor = window.QA_OS && window.QA_OS.Compositor;
    var toSave = {
      role: state.role,
      theme: state.theme,
      background: state.background,
      brightness: state.brightness,
      installedApps: state.installedApps,
      fidelity: state.fidelity,
      compositorState: compositor
        ? {
            windows: compositor.serialize(),
            activeId: compositor.getActiveId(),
          }
        : null,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
  } catch (e) {}
}

function getWorkspaceData() {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  return {
    role: state.role,
    theme: state.theme,
    background: state.background,
    brightness: state.brightness,
    installedApps: state.installedApps,
    fidelity: state.fidelity,
    compositorState: compositor
      ? {
          windows: compositor.serialize(),
          activeId: compositor.getActiveId(),
        }
      : null,
  };
}

function applyWorkspaceData(data) {
  if (!data) return;
  var compositor = window.QA_OS && window.QA_OS.Compositor;

  if (data.role === "junior" || data.role === "senior") state.role = data.role;
  if (data.theme === "dark" || data.theme === "light") setTheme(data.theme);
  if (data.background) setBackground(data.background);
  if (typeof data.brightness === "number") {
    state.brightness = data.brightness;
    applyBrightness();
  }
  if (Array.isArray(data.installedApps)) {
    state.installedApps = data.installedApps;
    Object.keys(APPS).forEach(function (id) {
      if (state.installedApps.indexOf(id) === -1) state.installedApps.push(id);
    });
  }
  if (data.fidelity === "win11" || data.fidelity === "classic")
    setFidelity(data.fidelity);
  if (compositor && data.compositorState) {
    compositor.deserialize(data.compositorState.windows, {
      activeId: data.compositorState.activeId,
    });
  }
  renderRole();
  renderAllWindows();
  renderTaskbar();
  renderStartMenu();
}

function setupAutoSave(workspaces) {
  var autoSaveTimer = null;
  function scheduleAutoSave() {
    if (autoSaveTimer) clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(function () {
      workspaces.autoSave(getWorkspaceData()).catch(function () {});
    }, 5000);
  }

  // Subscribe to compositor events to trigger auto-save
  var bus = window.QA_OS && window.QA_OS.EventBus;
  if (bus) {
    bus.on("window-created", scheduleAutoSave);
    bus.on("window-destroyed", scheduleAutoSave);
    bus.on("window-focused", scheduleAutoSave);
    bus.on("window-minimized", scheduleAutoSave);
    bus.on("window-layout-changed", scheduleAutoSave);
  }
}

function loadState() {
  try {
    var compositor = window.QA_OS && window.QA_OS.Compositor;
    var raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    var parsed = JSON.parse(raw);

    if (parsed.role === "junior" || parsed.role === "senior")
      state.role = parsed.role;

    // Restore compositor state (windows, z-order, active window)
    if (compositor && parsed.compositorState) {
      compositor.deserialize(parsed.compositorState.windows || [], {
        activeId: parsed.compositorState.activeId || null,
      });
    } else if (Array.isArray(parsed.windows)) {
      // Legacy migration: old format had windows directly on state
      if (compositor) {
        compositor.deserialize(parsed.windows, {
          activeId: parsed.activeWindowId || null,
          nextId: parsed.nextWindowId || 1,
        });
      }
    }

    if (parsed.theme === "dark" || parsed.theme === "light")
      state.theme = parsed.theme;
    if (parsed.background) state.background = parsed.background;
    if (Array.isArray(parsed.installedApps)) {
      state.installedApps = parsed.installedApps;
      Object.keys(APPS).forEach(function (id) {
        if (state.installedApps.indexOf(id) === -1) {
          state.installedApps.push(id);
        }
      });
    }
    if (typeof parsed.brightness === "number")
      state.brightness = parsed.brightness;
    if (parsed.fidelity === "win11" || parsed.fidelity === "classic")
      state.fidelity = parsed.fidelity;
  } catch (e) {
    // ignore
  }

  // ── CAPSTONE SESSION BOOT ─────────────────────────────────────────────
  // When the OS is launched from capstone.html, a session object is written
  // to localStorage before the iframe is created. Read it here and use it
  // to load the student's configuration from IndexedDB synchronously.
  // If absent (standalone dist.html), skip gracefully.
  (function loadCapstoneSession() {
    try {
      var raw = localStorage.getItem(CAPSTONE_SESSION_KEY);
      if (!raw) return; // standalone mode — nothing to load
      var session = JSON.parse(raw);
      if (!session || !session.caseId) return;

      // Store caseId so other functions can use it (e.g. to write results)
      state.capstoneCaseId = session.caseId;
      state.role = session.role || state.role;
      state.activeScenarioId = session.scenarioId || "capstone-001";
      state.capstoneScenarioId = state.activeScenarioId;

      // Initialise Capstone 2 orchestration state
      // The session is always created by capstone-2.html with scenarioId "case-002",
      // so check both the canonical ID and the actual scenario ID written to the session.
      if (state.activeScenarioId === "capstone-2" || state.activeScenarioId === "case-002") {
        state.capstone2InProg = true;
        state.capstone2Stage = (typeof session.stage === "number") ? session.stage : 0;
        console.log("[C2] Capstone 2 session loaded — stage=" + state.capstone2Stage +
          ", role=" + state.role +
          ", bugToggles=" + Object.keys(session.bugToggles || {}).length + " toggles");

        // Auto-advance to stage 1 on fresh boot (CAPSTONE_2_LOADED).
        // If resuming from a persisted stage, only advance if no stage was saved.
        if (state.capstone2Stage === 0 && typeof window.QA_OS.advanceStage === "function") {
          window.QA_OS.advanceStage("CAPSTONE_2_LOADED");
        }
      }

      // activeBugs: convert the { bugId: true/false } toggle map to an
      // array of enabled bugId strings (what state.activeBugs expects).
      if (session.bugToggles && typeof session.bugToggles === "object") {
        state.activeBugs = Object.keys(session.bugToggles).filter(function (k) {
          return session.bugToggles[k] === true;
        });
        if (state.capstone2InProg) {
          console.log("[C2] Active bugs loaded:", JSON.stringify(state.activeBugs));
        }
      }
    } catch (e) {
      console.warn("os-core: could not load capstone session", e);
    }
  })();

  // ── V1.5-3A: SYNCHRONOUS STUDENT DATA (capstone-2.html bootstrap) ───
  // When the OS runs inside capstone-2.html's srcdoc iframe, the parent
  // page stores student info on window.__capstoneStudentInfo. Read it
  // synchronously here so APP_BOOT payloads include student name (needed
  // by Dynamics CRM to pre-fill the username field and validate login).
  // This runs BEFORE the async IndexedDB load (V1.5-3B) so even if the
  // IndexedDB read is slow, the first APP_BOOT already has student data.
  try {
    if (window.parent && window.parent.__capstoneStudentInfo) {
      state.studentData = window.parent.__capstoneStudentInfo;
      console.log("[os-core] Synchronous student data loaded from parent:",
        JSON.stringify(state.studentData));
    }
  } catch (e) {
    // Not in an iframe or cross-origin — skip
  }

  // ── V1.5-3B: ASYNC STUDENT DATA FROM IndexedDB (standalone OS) ──────
  // When the OS runs standalone (not in capstone-2.html), read student
  // session from sessionStorage and enrich APP_BOOT asynchronously.
  // Runs asynchronously and does NOT block boot.
  if (typeof initDB === "function" && !state.studentData) {
    var _readQaSession = function () {
      try {
        var raw = sessionStorage.getItem("qa_session");
        return raw ? JSON.parse(raw) : null;
      } catch (e) {
        return null;
      }
    };

    initDB().then(function () {
      var session = _readQaSession();
      if (!session || !session.caseId) return; // no active course session
      state.studentCaseId = session.caseId;
      return Promise.all([
        new Promise(function (resolve) {
          var s = getStudent(session.caseId);
          resolve(s);
        }),
        new Promise(function (resolve) {
          var p = getProgress(session.caseId);
          resolve(p);
        }),
        new Promise(function (resolve) {
          var t = getBugToggles(session.caseId);
          resolve(t);
        }),
      ]);
    }).then(function (results) {
      if (!results) return;
      state.studentData = results[0] || null;
      state.studentProgress = results[1] || null;
      if (results[2]) {
        var semanticKeys = results[2];
        // semanticKeys is an array of strings from getBugToggles() + BUG_MAP
        // Merge with existing activeBugs (capstone session may already have set some)
        var merged = {};
        (state.activeBugs || []).forEach(function (b) { merged[b] = true; });
        (semanticKeys || []).forEach(function (key) {
          merged[key] = true;
        });
        state.activeBugs = Object.keys(merged);
      }
    }).catch(function (err) {
      console.warn("[os-core] db.js init skipped (standalone mode):", err.message);
    });
  }

  // ── V1.5-5: ?mode=capstone QUERY PARAM HANDLING ────────────────────
  // When the new simplified capstone.html redirects here, we read the
  // query param instead of (or in addition to) the localStorage session.
  // This supports the direct-redirect flow (no capstone-lab.html iframe).
  (function handleCapstoneMode() {
    try {
      var params = new URLSearchParams(window.location.search);
      if (params.get("mode") !== "capstone") return;
      // Already loaded from localStorage session — skip (existing capstone-lab.html flow)
      if (state.capstoneScenarioId) return;
      // Set up capstone mode from the query param
      state.capstoneScenarioId = params.get("scenario") || "capstone-001";
      state.activeScenarioId = state.capstoneScenarioId;
      state.capstoneCaseId = state.studentCaseId || "unknown";
      console.log("[os-core] Capstone mode activated via ?mode=capstone: " + state.capstoneScenarioId);
      // Re-render taskbar to show the submit button now that capstoneScenarioId is set
      if (typeof renderTaskbar === "function") renderTaskbar();
    } catch (e) {
      console.warn("[os-core] Could not parse ?mode param:", e);
    }
  })();
}

// SUBMIT / SCORING

/**
 * scoreSubmission(scenarioId, bugsLogged)
 * Evaluates each BUG_LOGGED entry against the active scenario's expectedBugs.
 * Returns a structured result consumed by both the Teams review thread and the
 * existing result modal.
 */
function scoreSubmission(scenarioId, bugsLogged) {
  var scenario = window.SCENARIOS && window.SCENARIOS[scenarioId];
  var expected = (scenario && scenario.expectedBugs) || [];
  var acPattern = /^AC-(\d+\.\d+|[A-Z]+\d+-\d+-\d+)$/i;
  var sevPattern = /^\d\s*-\s*.+$/;
  var acRefs = (scenario && scenario.acRefs) || {};

  var scored = (bugsLogged || []).map(function (bug, idx) {
    var title = (bug.title || "").trim();
    var severity = (bug.severity || "").trim();
    var acRef = (bug.acRef || "").trim();
    var hasSteps = !!bug.hasSteps;

    var checks = {
      title:
        title.length > 10 && !/^(bug|issue|test|untitled|defect)$/i.test(title),
      severity: sevPattern.test(severity),
      acRef: acPattern.test(acRef),
      steps: hasSteps,
    };

    // Check if this report targets a real expected bug
    var matchedBugId = null;
    if (acRef) {
      for (var bugId in acRefs) {
        if (acRefs[bugId].toLowerCase() === acRef.toLowerCase()) {
          matchedBugId = bugId;
          break;
        }
      }
    }

    var passed =
      checks.title && checks.severity && checks.acRef && checks.steps;

    return {
      index: idx + 1,
      title: title || "(no title)",
      severity: severity || "(none)",
      acRef: acRef || "(none)",
      hasSteps: hasSteps,
      checks: checks,
      matched: matchedBugId !== null,
      matchedBugId: matchedBugId,
      passed: passed,
    };
  });

  var passCount = scored.filter(function (b) {
    return b.passed;
  }).length;
  var matchCount = scored.filter(function (b) {
    return b.matched;
  }).length;
  var total = scored.length;

  return {
    scored: scored,
    passCount: passCount,
    matchCount: matchCount,
    total: total,
    expectedTotal: expected.length,
  };
}

/**
 * persistCapstoneBugs()
 * Persists the current bugsLogged and bugsFound arrays to the capstone
 * session in localStorage so they survive an iframe reload or crash.
 * Called by runSubmit() before sending CAPSTONE_COMPLETE.
 */
function persistCapstoneBugs() {
  try {
    var raw = localStorage.getItem(CAPSTONE_SESSION_KEY);
    if (!raw) return;
    var session = JSON.parse(raw);
    session.bugsLogged = state.bugsLogged || [];
    session.bugsFound = state.bugsFound || [];
    localStorage.setItem(CAPSTONE_SESSION_KEY, JSON.stringify(session));
    console.log("[C2] persistCapstoneBugs: saved " +
      (state.bugsLogged || []).length + " logged bugs, " +
      (state.bugsFound || []).length + " found bugs");
  } catch (e) {
    console.warn("[C2] persistCapstoneBugs error:", e);
  }
}

function runSubmit() {
  // ── Guard against double-fire ──────────────────────────────────────
  if (state.submitInProgress) {
    console.warn("[C2] runSubmit: already in progress — ignoring duplicate call");
    return;
  }
  state.submitInProgress = true;

  // Safeguard: persist bugsLogged to localStorage before clearing anything
  // so the state survives if the iframe reloads during scoring.
  persistCapstoneBugs();

  // ── Detect Capstone 2 mode ──────────────────────────────────────────
  var isCapstone2 = state.capstone2InProg === true ||
                    state.capstoneScenarioId === "capstone-2" ||
                    state.activeScenarioId === "capstone-2" ||
                    state.capstoneScenarioId === "case-002" ||
                    state.activeScenarioId === "case-002";

  console.log("[C2] runSubmit() called — capstone2InProg=" + state.capstone2InProg +
    ", scenarioId=" + state.capstoneScenarioId +
    ", bugsFound=" + (state.bugsFound || []).length +
    ", bugsLogged=" + (state.bugsLogged || []).length);

  if (isCapstone2) {
    console.log("[C2] runSubmit: Capstone 2 mode — delegating scoring to capstone-2.html, " +
      "skipping OS-level result modal and legacy IndexedDB save");
  } else {
    // ── Legacy scoring path (capstone-1 and standalone OS) ──────────────
    if (!window.evaluateSubmission) {
      addNotification("Scoring engine not loaded.");
      // SECURITY FIX (2026-05-22): Reset guard so the user can retry after
      // the scoring engine loads. Previously this early-return left the flag
      // permanently true, bricking the submit button.
      state.submitInProgress = false;
      return;
    }

    const result = window.evaluateSubmission(
      state.capstoneScenarioId || "capstone-001",
      state.bugsFound,
      state.bugsLogged,
    );

    showResultModal(result);

    // Write results directly to Academy IndexedDB if we have a caseId.
    if (state.capstoneCaseId && typeof initDB === "function") {
      initDB()
        .then(function () {
          return saveQuizResults(state.capstoneCaseId, "capstone", {
            score: result.score,
            maxScore: result.maxScore,
            percentage: result.percentage,
            passed: result.passed,
            completedAt: new Date().toISOString(),
          });
        })
        .then(function () {
          if (result.passed) {
            return awardCertificate(state.capstoneCaseId);
          }
        })
        .catch(function (err) {
          console.warn(
            "os-core: failed to write capstone results to IndexedDB",
            err,
          );
        })
        .finally(function () {
          // SECURITY FIX (2026-05-22): Always reset the guard after the async
          // IndexedDB chain completes (or fails). Previously the flag was never
          // cleared, so subsequent submits were silently ignored.
          state.submitInProgress = false;
        });
    } else {
      // No async work pending — safe to reset immediately.
      state.submitInProgress = false;
    }
  }

  // ── Common path: SPRINT_REVIEW + CAPSTONE_COMPLETE — runs for both modes

  // POST SPRINT REVIEW TO TEAMS
  var reviewResult = scoreSubmission(
    state.capstoneScenarioId || "capstone-001",
    state.bugsLogged,
  );
  var bus = window.QA_OS && window.QA_OS.EventBus;
  if (bus && bus.postToAllApps) {
    bus.postToAllApps({
      type: "SPRINT_REVIEW",
      result: reviewResult,
    });
    console.log("[C2] runSubmit: posted SPRINT_REVIEW to all apps with", 
      (reviewResult.scored || []).length, "scored bugs");
  }

  if (window.parent && window.parent !== window) {
    try {
      window.parent.postMessage(
        {
          type: "CAPSTONE_COMPLETE",
          isCapstone2: isCapstone2,
          bugCount: (state.bugsLogged || []).length,
        },
        "*",
      );
      console.log("[C2] runSubmit: posted CAPSTONE_COMPLETE to parent (isCapstone2=" + isCapstone2 + ")");
    } catch (e) {
      console.warn("[C2] runSubmit: failed to post CAPSTONE_COMPLETE", e);
    }
  }
}

function showResultModal(result) {
  const overlay = document.createElement("div");
  overlay.style.cssText =
    "position:fixed;inset:0;z-index:50000;background:rgba(0,0,0,0.72);" +
    "display:flex;align-items:center;justify-content:center;";

  const icon = result.passed ? "🎉" : "📝";
  const heading = result.passed
    ? "Assessment Complete"
    : "Assessment Submitted";
  const subtext = result.passed
    ? "Congratulations! Your certificate is being prepared."
    : "Good attempt. Review the feedback below.";

  const card = document.createElement("div");
  card.style.cssText =
    "background:var(--qa-glass-dark);border-width:1px;border-style:solid;border-color:var(--qa-border-mid);" +
    "border-radius:12px;padding:32px 36px;max-width:480px;color:var(--qa-text-light);" +
    "font-family:var(--qa-font);text-align:center;";

  card.innerHTML =
    '<div style="font-size:36px;margin-bottom:12px;">' +
    icon +
    "</div>" +
    '<div style="font-size:18px;font-weight:600;margin-bottom:6px;">' +
    heading +
    "</div>" +
    '<div style="font-size:13px;color:var(--qa-muted-light);margin-bottom:20px;">' +
    subtext +
    "</div>" +
    '<pre style="text-align:left;white-space:pre-wrap;font-family:inherit;font-size:13px;' +
    "background:rgba(255,255,255,0.05);border-radius:6px;padding:12px 14px;" +
    'margin-bottom:20px;">' +
    (result.summary || "") +
    "</pre>" +
    '<button id="qa-result-close" ' +
    'style="background:var(--qa-accent-soft);color:var(--qa-accent);' +
    "border:1px solid rgba(96,205,255,0.3);border-radius:6px;" +
    'padding:8px 20px;font-size:13px;cursor:pointer;">Close</button>';

  overlay.appendChild(card);
  document.body.appendChild(overlay);

  const closeBtn = document.getElementById("qa-result-close");
  if (closeBtn) {
    closeBtn.addEventListener("click", function () {
      overlay.remove();
    });
  }
}

// ── RESIZE HANDLES ────────────────────────────────────────────────────────

function startResize(e, winId, dir) {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  if (!compositor) return;
  var win = compositor.getWindow(winId);
  if (!win || win.layout !== "normal") return;

  var el = document.querySelector('[data-win-id="' + winId + '"]');
  var rect = el ? el.getBoundingClientRect() : null;
  var startX = e.clientX;
  var startY = e.clientY;
  var startW =
    typeof win.width === "number" ? win.width : rect ? rect.width : 800;
  var startH =
    typeof win.height === "number" ? win.height : rect ? rect.height : 600;
  var startLeft = typeof win.x === "number" ? win.x : rect ? rect.left : 120;
  var startTop = typeof win.y === "number" ? win.y : rect ? rect.top : 60;

  var shield = document.createElement("div");
  shield.style.cssText =
    "position:fixed;inset:0;z-index:2147483647;cursor:" +
    (dir === "se" ? "nwse-resize" : dir === "e" ? "ew-resize" : "ns-resize") +
    ";";

  function onMove(ev) {
    var dx = ev.clientX - startX;
    var dy = ev.clientY - startY;
    var newW =
      dir === "e" || dir === "se" ? Math.max(280, startW + dx) : startW;
    var newH =
      dir === "s" || dir === "se" ? Math.max(200, startH + dy) : startH;
    compositor.resize(winId, startLeft, startTop, newW, newH);
    var el = document.querySelector('[data-win-id="' + winId + '"]');
    if (el) {
      el.style.width = newW + "px";
      el.style.height = newH + "px";
    }
  }

  function onUp() {
    document.removeEventListener("mousemove", onMove);
    document.removeEventListener("mouseup", onUp);
    if (shield.parentNode) shield.remove();
    saveState();
  }

  document.body.appendChild(shield);
  document.addEventListener("mousemove", onMove);
  document.addEventListener("mouseup", onUp);
}

// ── CONTEXT MENUS ─────────────────────────────────────────────────────────

function showWindowContextMenu(winId, x, y) {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  if (!compositor) return;
  var win = compositor.getWindow(winId);
  if (!win) return;

  var items = [];
  if (win.layout !== "normal") {
    items.push({
      label: "Restore",
      action: function () {
        compositor.setLayout(winId, "normal");
        saveState();
        renderAllWindows();
      },
    });
  }
  items.push(
    { label: "Move", action: function () {} },
    { label: "Size", action: function () {} },
  );
  items.push({ separator: true });
  items.push({
    label: "Minimize",
    action: function () {
      minimizeWindow(winId);
    },
  });
  if (win.layout !== "maximized") {
    items.push({
      label: "Maximize",
      action: function () {
        toggleMaximize(winId);
      },
    });
  }
  items.push({ separator: true });
  items.push({
    label: "Close",
    action: function () {
      closeWindow(winId);
    },
  });

  showContextMenu(items, x, y);
}

function showContextMenu(items, x, y) {
  var existing = document.querySelector(".qa-context-menu");
  if (existing) existing.remove();

  var menu = document.createElement("div");
  menu.className = "qa-context-menu";
  menu.style.left = x + "px";
  menu.style.top = y + "px";

  items.forEach(function (item) {
    if (item.separator) {
      var sep = document.createElement("div");
      sep.className = "qa-context-separator";
      menu.appendChild(sep);
      return;
    }
    var btn = document.createElement("button");
    btn.className = "qa-context-item";
    btn.textContent = item.label;
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      menu.remove();
      item.action();
    });
    menu.appendChild(btn);
  });

  document.body.appendChild(menu);

  setTimeout(function () {
    document.addEventListener("click", function closeMenu() {
      menu.remove();
      document.removeEventListener("click", closeMenu);
    });
  }, 0);
}

// ── WORKSPACES DIALOG UI ─────────────────────────────────────────────────

function showWorkspaceSaveDialog() {
  var overlay = showModalDialog(
    "Save Workspace",
    '<div style="margin-bottom:12px;font-size:12px;color:var(--qa-muted-light);">Name this session so you can restore it later.</div>' +
      '<input id="qa-ws-name" type="text" placeholder="e.g. Morning QA Session" ' +
      'style="width:100%;padding:8px 10px;background:rgba(255,255,255,0.06);border-width:1px;border-style:solid;border-color:var(--qa-border-mid);' +
      'border-radius:4px;color:var(--qa-text-light);font-size:13px;font-family:var(--qa-font);outline:none;" />',
    [
      { label: "Cancel", primary: false },
      {
        label: "Save",
        primary: true,
        action: function () {
          var name = document.getElementById("qa-ws-name");
          if (name && name.value.trim()) {
            var workspaces = window.QA_OS && window.QA_OS.Workspaces;
            if (workspaces) {
              workspaces
                .save(name.value.trim(), getWorkspaceData())
                .then(function () {
                  showNotifier(
                    "Workspace saved: " + name.value.trim(),
                    "success",
                  );
                })
                .catch(function (e) {
                  showNotifier("Failed to save workspace", "error");
                });
            }
          }
          overlay.remove();
        },
      },
    ],
  );
}

function showWorkspaceRestoreDialog() {
  var workspaces = window.QA_OS && window.QA_OS.Workspaces;
  if (!workspaces) return;

  workspaces
    .list()
    .then(function (list) {
      var itemsHtml =
        list.length === 0
          ? '<div style="padding:20px;text-align:center;color:var(--qa-muted-light);font-size:12px;">No saved workspaces.</div>'
          : list
              .map(function (item, idx) {
                var time = item.timestamp
                  ? new Date(item.timestamp).toLocaleString()
                  : "";
                return (
                  '<button class="qa-ws-item" data-idx="' +
                  idx +
                  '" ' +
                  'style="display:block;width:100%;padding:8px 12px;background:rgba(255,255,255,0.04);' +
                  "border:1px solid var(--qa-border-dark);border-radius:6px;color:var(--qa-text-light);" +
                  'font-size:12px;font-family:var(--qa-font);cursor:pointer;text-align:left;margin-bottom:4px;">' +
                  '<div style="font-weight:500;">' +
                  item.name +
                  "</div>" +
                  (time
                    ? '<div style="font-size:10px;color:var(--qa-muted-light);margin-top:2px;">' +
                      time +
                      "</div>"
                    : "") +
                  "</button>"
                );
              })
              .join("");

      var overlay = showModalDialog(
        "Restore Workspace",
        '<div style="margin-bottom:12px;font-size:12px;color:var(--qa-muted-light);">Select a previously saved workspace to restore.</div>' +
          "<div>" +
          itemsHtml +
          "</div>",
        list.length > 0
          ? [{ label: "Cancel", primary: false }]
          : [{ label: "Close", primary: true }],
      );

      if (list.length > 0) {
        [].forEach.call(
          overlay.querySelectorAll(".qa-ws-item"),
          function (btn) {
            btn.addEventListener("click", function () {
              var idx = parseInt(btn.getAttribute("data-idx"), 10);
              var item = list[idx];
              if (item && item.data) {
                applyWorkspaceData(item.data);
                showNotifier("Workspace restored: " + item.name, "success");
              }
              overlay.remove();
            });
          },
        );
      }
    })
    .catch(function () {
      showNotifier("Failed to load workspaces", "error");
    });
}

function showModalDialog(title, bodyHtml, buttons) {
  buttons = buttons || [{ label: "Close", primary: true }];

  var overlay = document.createElement("div");
  overlay.style.cssText =
    "position:fixed;inset:0;z-index:50000;background:rgba(0,0,0,0.65);display:flex;align-items:center;justify-content:center;";

  var card = document.createElement("div");
  card.style.cssText =
    "background:var(--qa-glass-dark);border:1px solid var(--qa-border-mid);border-radius:12px;padding:20px 24px;min-width:340px;max-width:420px;color:var(--qa-text-light);font-family:var(--qa-font);";

  var h = document.createElement("div");
  h.style.cssText = "font-size:14px;font-weight:600;margin-bottom:12px;";
  h.textContent = title;
  card.appendChild(h);

  var content = document.createElement("div");
  content.innerHTML = bodyHtml;
  card.appendChild(content);

  var btnRow = document.createElement("div");
  btnRow.style.cssText =
    "display:flex;justify-content:flex-end;gap:8px;margin-top:16px;";
  buttons.forEach(function (btn) {
    var b = document.createElement("button");
    b.textContent = btn.label;
    b.style.cssText = btn.primary
      ? "background:var(--qa-accent);color:#000;border:none;padding:7px 16px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;font-family:var(--qa-font);"
      : "background:transparent;color:var(--qa-text-light);border:1px solid var(--qa-border-mid);padding:7px 16px;border-radius:6px;font-size:12px;cursor:pointer;font-family:var(--qa-font);";
    b.addEventListener("click", function () {
      if (btn.action) btn.action();
      else overlay.remove();
    });
    btnRow.appendChild(b);
  });
  card.appendChild(btnRow);

  overlay.appendChild(card);
  document.body.appendChild(overlay);
  return overlay;
}

// ── DESKTOP CONTEXT MENU ─────────────────────────────────────────────────

function setupDesktopContextMenu() {
  var workspace = document.querySelector(".qa-workspace");
  if (!workspace) return;
  workspace.addEventListener("contextmenu", function (e) {
    if (
      e.target.closest(".qa-window") ||
      e.target.closest(".qa-taskbar") ||
      e.target.closest(".qa-desktop-icons")
    )
      return;
    e.preventDefault();
    showContextMenu(
      [
        { label: "View", action: function () {} },
        { label: "Sort by", action: function () {} },
        { label: "Refresh", action: function () {} },
        { separator: true },
        {
          label: "Save workspace",
          action: function () {
            showWorkspaceSaveDialog();
          },
        },
        {
          label: "Restore workspace",
          action: function () {
            showWorkspaceRestoreDialog();
          },
        },
        { separator: true },
        {
          label: "Display settings",
          action: function () {
            if (window.OS && window.OS.openApp) window.OS.openApp("settings");
          },
        },
        {
          label: "Personalize",
          action: function () {
            if (window.OS && window.OS.openApp) window.OS.openApp("settings");
          },
        },
      ],
      e.clientX,
      e.clientY,
    );
  });

  // Taskbar context menu
  var taskbar = document.querySelector(".qa-taskbar");
  if (taskbar) {
    taskbar.addEventListener("contextmenu", function (e) {
      var appBtn = e.target.closest(".qa-taskbar-app-btn");
      if (appBtn) {
        // App button context menu — close handled by existing listener
        return;
      }
      e.preventDefault();
      showContextMenu(
        [
          { label: "Task Manager", action: function () {} },
          { separator: true },
          {
            label: "Save workspace",
            action: function () {
              showWorkspaceSaveDialog();
            },
          },
          {
            label: "Restore workspace",
            action: function () {
              showWorkspaceRestoreDialog();
            },
          },
          { separator: true },
          {
            label: "Task view",
            action: function () {
              toggleTaskview();
            },
          },
        ],
        e.clientX,
        e.clientY,
      );
    });
  }
}

// ── NOTIFIER TOAST ────────────────────────────────────────────────────────

function setupNotifier() {
  var container = document.createElement("div");
  container.className = "qa-notifier";
  container.id = "qa-notifier";
  document.body.appendChild(container);
}

function showNotifier(text, type) {
  type = type || "info";
  var container = document.getElementById("qa-notifier");
  if (!container) return;

  var toast = document.createElement("div");
  toast.className = "qa-notifier-toast";
  toast.textContent = text;
  container.appendChild(toast);

  setTimeout(function () {
    toast.classList.add("out");
    setTimeout(function () {
      toast.remove();
    }, 200);
  }, 3500);
}
