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

};

const STORAGE_KEY = "qaSimulatorDesktop";

const CAPSTONE_SESSION_KEY = "qa-capstone-session";

const state = {
  role: "junior",
  theme: "light",
  background: "default",
  brightness: 100,
  installedApps: Object.keys(APPS),
  fidelity: "win11",

  capstoneScenarioId: null,
  activeScenarioId: null,
  bugsFound: [],
  bugsLogged: [],
  activeBugs: [],
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
  submitTile;

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

  // ── INITIALISE ARCHITECTURE LAYERS ──────────────────────────
  var bus = window.QA_OS && window.QA_OS.EventBus;
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  var workspaces = window.QA_OS && window.QA_OS.Workspaces;

  if (compositor) compositor.init(windowArea);
  if (bus) bus.initAppMessaging();

  // ── BOOT SEQUENCE ─────────────────────────────────────────────────────
  var bootScreen = document.getElementById('qa-boot-screen');
  if (bootScreen) {
    setTimeout(function() {
      lockScreen.classList.remove('qa-lock-hidden');
      lockScreen.style.display = '';
      bootScreen.classList.add('qa-boot-hidden');
      setTimeout(function() {
        bootScreen.style.display = 'none';
      }, 650);
    }, 2500);
  } else {
    lockScreen.classList.remove('qa-lock-hidden');
    lockScreen.style.display = '';
  }

  loadState();
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
  startLockClock();

  // Auto-save via Workspaces when OS state changes
  if (workspaces) {
    setupAutoSave(workspaces);
  }

  setupNotifier();
  setupDesktopContextMenu();

  // Wire up EventBus to trigger toast notifier
  if (bus) {
    bus.on("notify", function (data) {
      showNotifier(data.text || data, data.type || "info");
    });
    // Legacy notify from app messages
    bus.on("app:NOTIFY", function (msg) {
      showNotifier(msg.text || msg.message || "Notification", msg.type || "info");
    });
  }

  if (compositor && compositor.getWindows().length === 0) {
    openApp("dynamics");
    openApp("ac");
  }

  var coreApi = {
    getRole: function () { return state.role; },
    getFidelity: function () { return state.fidelity; },
    setTheme: function (t) { setTheme(t); },
    setBackground: function (id) { setBackground(id); },
    setFidelity: function (mode) { setFidelity(mode); },
    notify: function (msg) { addNotification(msg); },
    notifyToast: function (text, type) { showNotifier(text, type); },
    openApp: function (id) { openApp(id); },
    installApp: function (id) { installApp(id); },
    uninstallApp: function (id) { uninstallApp(id); },
    loadScenario: function (id) { return (window.SCENARIOS && window.SCENARIOS[id]) || null; },
    getAppHtml: function (appId) { return (typeof APP_HTML !== 'undefined' && APP_HTML[appId]) || null; },
    completeTask: function (id) { addNotification("Task completed: " + id); },

    // Workspaces API
    saveWorkspace: function (name) {
      if (workspaces) return workspaces.save(name, getWorkspaceData());
    },
    restoreWorkspace: function (name) {
      if (workspaces) return workspaces.restore(name).then(function (data) { applyWorkspaceData(data); });
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
      } catch (e) { return null; }
    },

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
       if (openMenu) { openMenu.remove(); return; }
     }

     if (!lockScreen.classList.contains("qa-lock-hidden")) unlock();
   });

  document.querySelectorAll(".qa-desktop-icon").forEach((icon) => {
    icon.addEventListener("dblclick", () => {
      const appId = icon.getAttribute("data-app");
      if (appId) openApp(appId);
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
      }
      if (state.activeBugs.indexOf(msg.bugId) === -1) {
        state.activeBugs.push(msg.bugId);
      }
      addNotification("🔍 Defect encountered: " + msg.bugId);
    });

    bus.onAppMessage("BUG_LOGGED", function (msg) {
      state.bugsLogged.push(msg.data || {});
      addNotification(
        "📋 Bug report filed: " +
          (msg.data && msg.data.title ? msg.data.title : "untitled"),
      );
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
      setTimeout(function() { startSearchInput.focus(); }, 80);
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
    var app = APPS[id];
    if (!app) return false;
    return app.title.toLowerCase().indexOf(filter) !== -1 ||
           app.short.toLowerCase().indexOf(filter) !== -1 ||
           id.indexOf(filter) !== -1;
  });

  apps.forEach(function (id) {
    const app = APPS[id];
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
    empty.style.cssText = "grid-column:1/-1;text-align:center;padding:20px 0;color:var(--qa-muted-light);font-size:12px;";
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

  taskviewInner.innerHTML = "";
  var wins = compositor.getVisibleWindows();
  if (wins.length === 0) return;
  var activeId = compositor.getActiveId();

  wins.forEach(function (win) {
    var app = APPS[win.appId];
    var thumb = document.createElement("div");
    thumb.className = "qa-taskview-thumb";
    if (win.id === activeId) {
      thumb.classList.add("qa-active");
    }

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
    "border:1px solid var(--qa-border-mid)",
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
            var anyBrowser = compositor.getWindows().find(function (w) { return w.appId === "browser"; });
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
  if (appId === "training") {
    startCapstoneScenario("capstone-001");
    return;
  }

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
    .sort(function (a, b) { return a.z - b.z; })
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
        '<div class="qa-window-title">' + (app ? app.title : "Window") + '</div>' +
        '<div class="qa-window-controls">' +
          '<button class="qa-window-btn minimize" title="Minimize"></button>' +
          '<button class="qa-window-btn maximize" title="Maximize"></button>' +
          '<button class="qa-window-btn close" title="Close"></button>' +
        '</div>';
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
            acIframe.contentWindow.postMessage(
              { type: "APP_BOOT", appId: "ac", role: state.role, theme: state.theme,
                sessionId: win.id + "-" + Date.now().toString(36),
                scenarioId: state.activeScenarioId || null,
                activeBugs: state.activeBugs || [] }, "*");
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
            };
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
              var scenarioData = window.SCENARIOS && window.SCENARIOS[state.activeScenarioId];
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

      header.addEventListener("mousedown", function (e) { startDrag(e, el, win.id); });

      header.addEventListener("contextmenu", function (e) {
        e.preventDefault();
        e.stopPropagation();
        showWindowContextMenu(win.id, e.clientX, e.clientY);
      });

      header.querySelector(".close").addEventListener("click", function (e) {
        e.stopPropagation();
        closeWindow(win.id);
      });

      header.addEventListener("dblclick", function () { toggleMaximize(win.id); });

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

      el.addEventListener("mousedown", function () { focusWindow(win.id); });
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
    var anyBrowser = compositor.getWindows().find(function (w) { return w.appId === "browser"; });
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
}

function postToBrowser(msg, specificWinId) {
  var compositor = window.QA_OS && window.QA_OS.Compositor;
  var bus = window.QA_OS && window.QA_OS.EventBus;
  if (!compositor) return;

  var browserWin;
  if (specificWinId) {
    browserWin = compositor.getWindow(specificWinId);
  } else {
    browserWin = compositor.getWindows().find(function (w) { return w.appId === "browser"; });
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
  var browserWin = compositor.getWindows().find(function (w) { return w.appId === "browser"; });
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
  shield.style.cssText = "position:fixed;inset:0;z-index:2147483647;cursor:move;";

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
    var isActive = wins.some(function (w) { return w.id === activeId; });
    var hasVisible = wins.some(function (w) { return !w.minimized; });

    var btn = document.createElement("button");
    btn.className = "qa-taskbar-app-btn";
    if (isActive && hasVisible) btn.classList.add("qa-active");
    if (hasVisible) btn.classList.add("running");
    if (isActive && hasVisible) btn.classList.add("focused");
    btn.innerHTML = '<span class="qa-taskbar-app-icon">' + (app ? app.icon : "📦") + "</span>";
    btn.title = app ? app.title : appId;
    btn.dataset.label = app ? app.short : appId;

    btn.addEventListener("click", function () {
      var visible = wins.filter(function (w) { return !w.minimized; });
      if (visible.length === 0) {
        wins[0].minimized = false;
        compositor.focus(wins[0].id);
      } else {
        var topWin = visible.reduce(function (a, b) { return a.z > b.z ? a : b; });
        if (activeId === topWin.id) {
          visible.forEach(function (w) { w.minimized = true; });
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
      wins.slice().forEach(function (w) { actuallyCloseWindow(w.id, app); });
    });

    taskbarApps.appendChild(btn);
  });

  if (submitBtn) {
    submitBtn.style.display = state.capstoneScenarioId ? "inline-flex" : "none";
  }
  if (submitTile) {
    submitTile.style.display = state.capstoneScenarioId ? "inline-flex" : "none";
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
  updateClock();
  setInterval(updateClock, 15000);
}

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
  state.installedApps = state.installedApps.filter(function (x) { return x !== id; });
  // Close all windows for this app via compositor
  if (compositor) {
    var wins = compositor.getWindowsByApp(id);
    wins.slice().forEach(function (w) { compositor.destroyWindow(w.id); });
  }
  saveState();
  renderAllWindows();
  renderTaskbar();
  renderStartMenu();
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
      compositorState: compositor ? {
        windows: compositor.serialize(),
        activeId: compositor.getActiveId(),
      } : null,
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
    compositorState: compositor ? {
      windows: compositor.serialize(),
      activeId: compositor.getActiveId(),
    } : null,
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
  if (data.fidelity === "win11" || data.fidelity === "classic") setFidelity(data.fidelity);
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
      if (!raw) return;   // standalone mode — nothing to load
      var session = JSON.parse(raw);
      if (!session || !session.caseId) return;

      // Store caseId so other functions can use it (e.g. to write results)
      state.capstoneCaseId   = session.caseId;
      state.role             = session.role || state.role;
      state.activeScenarioId = session.scenarioId || "capstone-001";
      state.capstoneScenarioId = state.activeScenarioId;

      // activeBugs: convert the { bugId: true/false } toggle map to an
      // array of enabled bugId strings (what state.activeBugs expects).
      if (session.bugToggles && typeof session.bugToggles === 'object') {
        state.activeBugs = Object.keys(session.bugToggles).filter(function(k) {
          return session.bugToggles[k] === true;
        });
      }
    } catch (e) {
      console.warn("os-core: could not load capstone session", e);
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
  var scenario     = window.SCENARIOS && window.SCENARIOS[scenarioId];
  var expected     = (scenario && scenario.expectedBugs) || [];
  var acPattern    = /^AC-\d+(\.\d+)?$/i;
  var sevPattern   = /^\d\s*-\s*.+$/;
  var acRefs       = (scenario && scenario.acRefs) || {};

  var scored = (bugsLogged || []).map(function(bug, idx) {
    var title    = (bug.title    || "").trim();
    var severity = (bug.severity || "").trim();
    var acRef    = (bug.acRef    || "").trim();
    var hasSteps = !!bug.hasSteps;

    var checks = {
      title:    title.length > 10 && !/^(bug|issue|test|untitled|defect)$/i.test(title),
      severity: sevPattern.test(severity),
      acRef:    acPattern.test(acRef),
      steps:    hasSteps,
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

    var passed = checks.title && checks.severity && checks.acRef && checks.steps;

    return {
      index:    idx + 1,
      title:    title || "(no title)",
      severity: severity || "(none)",
      acRef:    acRef || "(none)",
      hasSteps: hasSteps,
      checks:   checks,
      matched:  matchedBugId !== null,
      matchedBugId: matchedBugId,
      passed:   passed,
    };
  });

  var passCount  = scored.filter(function(b) { return b.passed; }).length;
  var matchCount = scored.filter(function(b) { return b.matched; }).length;
  var total      = scored.length;

  return {
    scored:     scored,
    passCount:  passCount,
    matchCount: matchCount,
    total:      total,
    expectedTotal: expected.length,
  };
}

function runSubmit() {
  if (!window.evaluateSubmission) {
    addNotification("Scoring engine not loaded.");
    return;
  }

  const result = window.evaluateSubmission(
    state.capstoneScenarioId || "capstone-001",
    state.bugsFound,
    state.bugsLogged,
  );

  showResultModal(result);

  // Write results directly to Academy IndexedDB if we have a caseId.
  // This means capstone.html only needs to listen for the signal to redirect
  // — it no longer needs to call saveQuizResults() or awardCertificate().
  if (state.capstoneCaseId && typeof initDB === 'function') {
    initDB()
      .then(function() {
        return saveQuizResults(state.capstoneCaseId, 'capstone', {
          score:       result.score,
          maxScore:    result.maxScore,
          percentage:  result.percentage,
          passed:      result.passed,
          completedAt: new Date().toISOString()
        });
      })
      .then(function() {
        return awardCertificate(state.capstoneCaseId);
      })
      .catch(function(err) {
        console.warn("os-core: failed to write capstone results to IndexedDB", err);
      });
  }

  // POST SPRINT REVIEW TO TEAMS
  var reviewResult = scoreSubmission(
    state.capstoneScenarioId || "capstone-001",
    state.bugsLogged
  );
  var bus = window.QA_OS && window.QA_OS.EventBus;
  if (bus && bus.postToAllApps) {
    bus.postToAllApps({
      type:   "SPRINT_REVIEW",
      result: reviewResult,
    });
  }

  if (window.parent && window.parent !== window) {
    try {
      window.parent.postMessage(
        {
          type: "CAPSTONE_COMPLETE",
          result: result,
        },
        "*",
      );
    } catch (e) {
      // ignore
    }
  }
}

function showResultModal(result) {
  const overlay = document.createElement("div");
  overlay.style.cssText =
    "position:fixed;inset:0;z-index:50000;background:rgba(0,0,0,0.72);" +
    "display:flex;align-items:center;justify-content:center;";

  const icon = result.passed ? "🎉" : "📝";
  const heading = result.passed ? "Assessment Complete" : "Assessment Submitted";
  const subtext = result.passed
    ? "Congratulations! Your certificate is being prepared."
    : "Good attempt. Review the feedback below.";

  const card = document.createElement("div");
  card.style.cssText =
    "background:var(--qa-glass-dark);border:1px solid var(--qa-border-mid);" +
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
  var startW = typeof win.width === "number" ? win.width : (rect ? rect.width : 800);
  var startH = typeof win.height === "number" ? win.height : (rect ? rect.height : 600);
  var startLeft = typeof win.x === "number" ? win.x : (rect ? rect.left : 120);
  var startTop = typeof win.y === "number" ? win.y : (rect ? rect.top : 60);

  var shield = document.createElement("div");
  shield.style.cssText = "position:fixed;inset:0;z-index:2147483647;cursor:" + (dir === "se" ? "nwse-resize" : dir === "e" ? "ew-resize" : "ns-resize") + ";";

  function onMove(ev) {
    var dx = ev.clientX - startX;
    var dy = ev.clientY - startY;
    var newW = (dir === "e" || dir === "se") ? Math.max(280, startW + dx) : startW;
    var newH = (dir === "s" || dir === "se") ? Math.max(200, startH + dy) : startH;
    compositor.resize(winId, startLeft, startTop, newW, newH);
    var el = document.querySelector('[data-win-id="' + winId + '"]');
    if (el) { el.style.width = newW + "px"; el.style.height = newH + "px"; }
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
    items.push({ label: "Restore", action: function () {
      compositor.setLayout(winId, "normal");
      saveState(); renderAllWindows();
    }});
  }
  items.push(
    { label: "Move", action: function () {} },
    { label: "Size", action: function () {} }
  );
  items.push({ separator: true });
  items.push({ label: "Minimize", action: function () { minimizeWindow(winId); } });
  if (win.layout !== "maximized") {
    items.push({ label: "Maximize", action: function () { toggleMaximize(winId); } });
  }
  items.push({ separator: true });
  items.push({ label: "Close", action: function () { closeWindow(winId); } });

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
  var overlay = showModalDialog("Save Workspace",
    '<div style="margin-bottom:12px;font-size:12px;color:var(--qa-muted-light);">Name this session so you can restore it later.</div>' +
    '<input id="qa-ws-name" type="text" placeholder="e.g. Morning QA Session" ' +
    'style="width:100%;padding:8px 10px;background:rgba(255,255,255,0.06);border:1px solid var(--qa-border-mid);' +
    'border-radius:4px;color:var(--qa-text-light);font-size:13px;font-family:var(--qa-font);outline:none;" />',
    [
      { label: "Cancel", primary: false },
      { label: "Save", primary: true, action: function () {
        var name = document.getElementById("qa-ws-name");
        if (name && name.value.trim()) {
          var workspaces = window.QA_OS && window.QA_OS.Workspaces;
          if (workspaces) {
            workspaces.save(name.value.trim(), getWorkspaceData()).then(function () {
              showNotifier("Workspace saved: " + name.value.trim(), "success");
            }).catch(function (e) {
              showNotifier("Failed to save workspace", "error");
            });
          }
        }
        overlay.remove();
      }}
    ]
  );
}

function showWorkspaceRestoreDialog() {
  var workspaces = window.QA_OS && window.QA_OS.Workspaces;
  if (!workspaces) return;

  workspaces.list().then(function (list) {
    var itemsHtml = list.length === 0
      ? '<div style="padding:20px;text-align:center;color:var(--qa-muted-light);font-size:12px;">No saved workspaces.</div>'
      : list.map(function (item, idx) {
          var time = item.timestamp ? new Date(item.timestamp).toLocaleString() : "";
          return '<button class="qa-ws-item" data-idx="' + idx + '" ' +
            'style="display:block;width:100%;padding:8px 12px;background:rgba(255,255,255,0.04);' +
            'border:1px solid var(--qa-border-dark);border-radius:6px;color:var(--qa-text-light);' +
            'font-size:12px;font-family:var(--qa-font);cursor:pointer;text-align:left;margin-bottom:4px;">' +
            '<div style="font-weight:500;">' + item.name + '</div>' +
            (time ? '<div style="font-size:10px;color:var(--qa-muted-light);margin-top:2px;">' + time + '</div>' : '') +
            '</button>';
        }).join("");

    var overlay = showModalDialog("Restore Workspace",
      '<div style="margin-bottom:12px;font-size:12px;color:var(--qa-muted-light);">Select a previously saved workspace to restore.</div>' +
      '<div>' + itemsHtml + '</div>',
      list.length > 0
        ? [{ label: "Cancel", primary: false }]
        : [{ label: "Close", primary: true }]
    );

    if (list.length > 0) {
      [].forEach.call(overlay.querySelectorAll(".qa-ws-item"), function (btn) {
        btn.addEventListener("click", function () {
          var idx = parseInt(btn.getAttribute("data-idx"), 10);
          var item = list[idx];
          if (item && item.data) {
            applyWorkspaceData(item.data);
            showNotifier("Workspace restored: " + item.name, "success");
          }
          overlay.remove();
        });
      });
    }
  }).catch(function () {
    showNotifier("Failed to load workspaces", "error");
  });
}

function showModalDialog(title, bodyHtml, buttons) {
  buttons = buttons || [{ label: "Close", primary: true }];

  var overlay = document.createElement("div");
  overlay.style.cssText = "position:fixed;inset:0;z-index:50000;background:rgba(0,0,0,0.65);display:flex;align-items:center;justify-content:center;";

  var card = document.createElement("div");
  card.style.cssText = "background:var(--qa-glass-dark);border:1px solid var(--qa-border-mid);border-radius:12px;padding:20px 24px;min-width:340px;max-width:420px;color:var(--qa-text-light);font-family:var(--qa-font);";

  var h = document.createElement("div");
  h.style.cssText = "font-size:14px;font-weight:600;margin-bottom:12px;";
  h.textContent = title;
  card.appendChild(h);

  var content = document.createElement("div");
  content.innerHTML = bodyHtml;
  card.appendChild(content);

  var btnRow = document.createElement("div");
  btnRow.style.cssText = "display:flex;justify-content:flex-end;gap:8px;margin-top:16px;";
  buttons.forEach(function (btn) {
    var b = document.createElement("button");
    b.textContent = btn.label;
    b.style.cssText = (btn.primary
      ? "background:var(--qa-accent);color:#000;border:none;padding:7px 16px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;font-family:var(--qa-font);"
      : "background:transparent;color:var(--qa-text-light);border:1px solid var(--qa-border-mid);padding:7px 16px;border-radius:6px;font-size:12px;cursor:pointer;font-family:var(--qa-font);");
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
    if (e.target.closest(".qa-window") || e.target.closest(".qa-taskbar") || e.target.closest(".qa-desktop-icons")) return;
    e.preventDefault();
    showContextMenu([
      { label: "View", action: function () {} },
      { label: "Sort by", action: function () {} },
      { label: "Refresh", action: function () {} },
      { separator: true },
      { label: "Save workspace", action: function () { showWorkspaceSaveDialog(); } },
      { label: "Restore workspace", action: function () { showWorkspaceRestoreDialog(); } },
      { separator: true },
      { label: "Display settings", action: function () {
        if (window.OS && window.OS.openApp) window.OS.openApp("settings");
      }},
      { label: "Personalize", action: function () {
        if (window.OS && window.OS.openApp) window.OS.openApp("settings");
      }},
    ], e.clientX, e.clientY);
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
      showContextMenu([
        { label: "Task Manager", action: function () {} },
        { separator: true },
        { label: "Save workspace", action: function () { showWorkspaceSaveDialog(); } },
        { label: "Restore workspace", action: function () { showWorkspaceRestoreDialog(); } },
        { separator: true },
        { label: "Task view", action: function () { toggleTaskview(); } },
      ], e.clientX, e.clientY);
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
    setTimeout(function () { toast.remove(); }, 200);
  }, 3500);
}
