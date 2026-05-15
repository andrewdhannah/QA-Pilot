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
    title: "QA Browser — Tabbed Workspace",
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

const state = {
  role: "junior",
  windows: [],
  activeWindowId: null,
  nextWindowId: 1,
  nextZ: 1,
  theme: "light",
  background: "default",
  brightness: 100,
  installedApps: Object.keys(APPS),
  fidelity: "win11", // "win11" or "classic"

  // Capstone / scenario session state (not persisted)
  capstoneScenarioId: null, // 'capstone-001' when active
  activeScenarioId: null,
  bugsFound: [],   // bugId strings from BUG_FOUND
  bugsLogged: [],  // { title, severity, acRef, hasSteps } from BUG_LOGGED
  activeBugs: [],  // bugIds currently active in the scenario
};

let shell,
  windowArea,
  startMenu,
  startButton,
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

  if (state.windows.length === 0) {
    openApp("dynamics");
    openApp("ac");
  }

  const coreApi = {
    getRole: () => state.role,
    getFidelity: () => state.fidelity,
    setTheme: (theme) => setTheme(theme),
    setBackground: (id) => setBackground(id),
    setFidelity: (mode) => setFidelity(mode),
    notify: (msg) => addNotification(msg),
    openApp: (id) => openApp(id),
    installApp: (id) => installApp(id),
    uninstallApp: (id) => uninstallApp(id),
    loadScenario: (id) => (window.SCENARIOS && window.SCENARIOS[id]) || null,
    completeTask: (id) => addNotification(`Task completed: ${id}`),

    // Global per-app persistence
    saveAppState: (appId, data) => {
      try {
        const key = `qa-app-${appId}`;
        localStorage.setItem(key, JSON.stringify(data));
      } catch (e) {
        // ignore
      }
    },
    loadAppState: (appId) => {
      try {
        const key = `qa-app-${appId}`;
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : null;
      } catch (e) {
        return null;
      }
    },
  };

  window.QA_OS = coreApi;
  window.OS = coreApi;
}

function bindEvents() {
  lockScreen.addEventListener("click", () => {
    if (!lockScreen.classList.contains("qa-lock-hidden")) unlock();
  });

  document.addEventListener("keydown", () => {
    if (!lockScreen.classList.contains("qa-lock-hidden")) unlock();
  });

  document.querySelectorAll(".qa-desktop-icon").forEach((icon) => {
    icon.addEventListener("dblclick", () => {
      const appId = icon.getAttribute("data-app");
      if (appId) openApp(appId);
    });
  });

  startButton.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleStartMenu();
    hideQuickPanel();
    hideNotifyCenter();
  });

  document.addEventListener("click", (e) => {
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

  // Listen for messages from apps running inside iframes
  window.addEventListener("message", function (event) {
    var msg = event.data;
    if (!msg || !msg.type) return;

    if (msg.type === "BUG_FOUND") {
      if (state.bugsFound.indexOf(msg.bugId) === -1) {
        state.bugsFound.push(msg.bugId);
      }
      if (state.activeBugs.indexOf(msg.bugId) === -1) {
        state.activeBugs.push(msg.bugId);
      }
      addNotification("🔍 Defect encountered: " + msg.bugId);
    }

    if (msg.type === "BUG_LOGGED") {
      state.bugsLogged.push(msg.data || {});
      addNotification(
        "📋 Bug report filed: " +
          (msg.data && msg.data.title ? msg.data.title : "untitled"),
      );
    }
  });
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
  startMenu.classList.toggle("qa-start-menu-hidden");
}

function hideStartMenu() {
  startMenu.classList.add("qa-start-menu-hidden");
}

function renderStartMenu() {
  if (!startGrid) return;
  startGrid.innerHTML = "";

  state.installedApps.forEach((id) => {
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
  taskviewInner.innerHTML = "";
  const wins = state.windows.filter((w) => !w.minimized);
  if (wins.length === 0) return;

  wins.forEach((win) => {
    const app = APPS[win.appId];
    const thumb = document.createElement("div");
    thumb.className = "qa-taskview-thumb";
    if (win.id === state.activeWindowId) {
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
    `Role switched to ${
      state.role === "junior" ? "Junior Investigator" : "Senior Investigator"
    }`,
  );

  // Broadcast role change to all open app iframes
  state.windows.forEach(function (win) {
    const el = windowArea.querySelector('[data-win-id="' + win.id + '"]');
    if (!el) return;
    const iframe = el.querySelector("iframe");
    if (!iframe || !iframe.contentWindow) return;
    try {
      iframe.contentWindow.postMessage(
        {
          type: "ROLE_CHANGE",
          role: state.role,
        },
        "*",
      );
    } catch (e) {
      // ignore
    }
  });
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

  const startBtn = document.getElementById("qa-brief-start");
  if (startBtn) {
    startBtn.addEventListener("click", function () {
      overlay.remove();

      openApp("dynamics");
      openApp("ac");

      setTimeout(function () {
        const dynWin = state.windows.find((w) => w.appId === "dynamics");
        const acWin = state.windows.find((w) => w.appId === "ac");
        if (dynWin) dynWin.layout = "snap-left";
        if (acWin) acWin.layout = "snap-right";

        renderAllWindows();
        renderTaskbar();
      }, 100);
    });
  }

  renderTaskbar();
}

// WINDOW MANAGEMENT

function openApp(appId) {
  // Training app starts the capstone scenario instead of opening a window
  if (appId === "training") {
    startCapstoneScenario("capstone-001");
    return;
  }

  if (!isInstalled(appId)) return;
  const app = APPS[appId];
  if (!app) return;

  const winId = state.nextWindowId++;
  const z = state.nextZ++;

  // Use the number of currently OPEN windows (not the ever-growing winId)
  // to calculate the cascade offset. This way, once windows are closed,
  // new ones reset back toward the centre of the screen.
  const openCount = state.windows.length;   // windows already open before this one
  const CASCADE_STEP_X = 28;
  const CASCADE_STEP_Y = 22;
  const MAX_CASCADE    = 6;   // reset cascade after this many steps
  const step  = openCount % MAX_CASCADE;
  const baseX = 160 + step * CASCADE_STEP_X;
  const baseY = 80  + step * CASCADE_STEP_Y;

  state.windows.push({
    id: winId,
    appId,
    z,
    layout: "normal",
    minimized: false,
    x: baseX,
    y: baseY,
  });
  state.activeWindowId = winId;
  saveState();
  renderAllWindows();
  renderTaskbar();
  addNotification(`Opened ${app.title}`);
}

function closeWindow(winId) {
  const idx = state.windows.findIndex((w) => w.id === winId);
  if (idx === -1) return;
  const app = APPS[state.windows[idx].appId];

  const el = windowArea.querySelector(`[data-win-id="${winId}"]`);
  if (el) {
    el.classList.add("qa-closing");
    setTimeout(() => {
      actuallyCloseWindow(winId, app);
    }, 160);
  } else {
    actuallyCloseWindow(winId, app);
  }
}

function actuallyCloseWindow(winId, app) {
  const idx = state.windows.findIndex((w) => w.id === winId);
  if (idx === -1) return;
  state.windows.splice(idx, 1);
  if (state.activeWindowId === winId) {
    state.activeWindowId = state.windows.length
      ? state.windows[state.windows.length - 1].id
      : null;
  }
  saveState();
  renderAllWindows();
  renderTaskbar();
  if (app) addNotification(`Closed ${app.title}`);
}

function focusWindow(winId) {
  const win = state.windows.find((w) => w.id === winId);
  if (!win) return;

  const needsUnminimize = win.minimized;
  win.z = state.nextZ++;
  win.minimized = false;
  state.activeWindowId = winId;
  saveState();

  if (needsUnminimize) {
    renderAllWindows();
  } else {
    state.windows.forEach((w) => {
      const el = windowArea.querySelector(`[data-win-id="${w.id}"]`);
      if (!el) return;
      el.style.zIndex = w.z;
      el.classList.toggle("qa-active", w.id === winId);

      const overlay = el.querySelector(".qa-focus-overlay");
      if (overlay) overlay.style.display = w.id === winId ? "none" : "block";
    });
  }
  renderTaskbar();
}

function toggleMaximize(winId) {
  const win = state.windows.find((w) => w.id === winId);
  if (!win) return;
  if (win.layout === "maximized") {
    win.layout = "normal";
  } else {
    win.layout = "maximized";
    win.minimized = false;
  }
  saveState();
  renderAllWindows();
}

function minimizeWindow(winId) {
  const win = state.windows.find((w) => w.id === winId);
  if (!win) return;
  win.minimized = true;
  if (state.activeWindowId === winId) {
    state.activeWindowId = null;
  }
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
  windowArea.innerHTML = "";
  state.windows
    .slice()
    .sort((a, b) => a.z - b.z)
    .forEach((win) => {
      if (win.minimized) return;

      const app = APPS[win.appId];
      const el = document.createElement("div");
      el.className = "qa-window";
      if (win.id === state.activeWindowId) el.classList.add("qa-active");
      el.style.zIndex = win.z;
      el.dataset.winId = win.id;

      applyLayoutClass(el, win.layout);

      if (win.layout === "normal") {
        if (typeof win.x === "number") el.style.left = `${win.x}px`;
        if (typeof win.y === "number") el.style.top = `${win.y}px`;
      }

      const header = document.createElement("div");
      header.className = "qa-window-header";
      header.innerHTML = `
        <div class="qa-window-title">${app ? app.title : "Window"}</div>
        <div class="qa-window-controls">
          <button class="qa-window-btn minimize" title="Minimize"></button>
          <button class="qa-window-btn maximize" title="Maximize"></button>
          <button class="qa-window-btn close" title="Close"></button>
        </div>
      `;
      el.appendChild(header);

      const body = document.createElement("div");
      body.className = "qa-window-body";

      if (win.appId === "ac") {
        const iframe = document.createElement("iframe");
        iframe.className = "qa-window-frame";
        iframe.srcdoc = APP_HTML && APP_HTML["ac"] ? APP_HTML["ac"] : "";
        iframe.addEventListener("load", () => {
          try {
            iframe.contentWindow.postMessage(
              {
                type: "APP_BOOT",
                appId: "ac",
                role: state.role,
                theme: state.theme,
                sessionId: `${win.id}-${Date.now().toString(36)}`,
                scenarioId: state.activeScenarioId || null,
                activeBugs: state.activeBugs || [],
              },
              "*",
            );
          } catch (e) {}
        });
        body.appendChild(iframe);
      } else if (APP_HTML && APP_HTML[win.appId]) {
        const iframe = document.createElement("iframe");
        iframe.className = "qa-window-frame";
        iframe.srcdoc = APP_HTML[win.appId];

        iframe.addEventListener("load", () => {
          try {
            iframe.contentWindow.postMessage(
              {
                type: "APP_BOOT",
                appId: win.appId,
                role: state.role,
                theme: state.theme,
                sessionId: `${win.id}-${Date.now().toString(36)}`,
                scenarioId: state.activeScenarioId || null,
                activeBugs: state.activeBugs || [],
              },
              "*",
            );
          } catch (e) {
            // ignore
          }
        });

        body.appendChild(iframe);
      } else {
        body.textContent = "App not configured.";
      }

      const focusOverlay = document.createElement("div");
      focusOverlay.className = "qa-focus-overlay";
      focusOverlay.style.display =
        win.id === state.activeWindowId ? "none" : "block";
      focusOverlay.addEventListener("mousedown", (e) => {
        e.stopPropagation();
        focusWindow(win.id);
      });
      body.appendChild(focusOverlay);

      el.appendChild(body);
      windowArea.appendChild(el);

      header.addEventListener("mousedown", (e) => startDrag(e, el, win.id));

      header.querySelector(".close").addEventListener("click", (e) => {
        e.stopPropagation();
        closeWindow(win.id);
      });

      header.addEventListener("dblclick", () => toggleMaximize(win.id));

      header.querySelector(".maximize").addEventListener("click", (e) => {
        e.stopPropagation();
        toggleMaximize(win.id);
      });

      header.querySelector(".minimize").addEventListener("click", (e) => {
        e.stopPropagation();
        minimizeWindow(win.id);
      });

      el.addEventListener("mousedown", () => focusWindow(win.id));
    });
}

// DRAG + SNAP

function startDrag(e, el, winId) {
  const win = state.windows.find((w) => w.id === winId);
  if (!win) return;
  if (win.layout === "maximized") return;

  focusWindow(winId);

  const rect = el.getBoundingClientRect();
  const offsetX = e.clientX - rect.left;
  const offsetY = e.clientY - rect.top;
  const startX = e.clientX;
  const startY = e.clientY;

  let hasMoved = false;

  const shield = document.createElement("div");
  shield.style.cssText =
    "position:fixed;inset:0;z-index:2147483647;cursor:move;";

  function onMove(ev) {
    if (!hasMoved) {
      const dx = ev.clientX - startX;
      const dy = ev.clientY - startY;
      if (Math.abs(dx) < 5 && Math.abs(dy) < 5) return;
      hasMoved = true;
      e.preventDefault();
      document.body.appendChild(shield);
    }

    const x = ev.clientX - offsetX;
    const y = ev.clientY - offsetY;
    el.style.left = `${x}px`;
    el.style.top = `${y}px`;
    win.x = x;
    win.y = y;
  }

  function onUp(ev) {
    document.removeEventListener("mousemove", onMove);
    document.removeEventListener("mouseup", onUp);
    if (shield.parentNode) shield.remove();

    if (!hasMoved) return;

    const vw = windowArea.clientWidth;
    const sm = 24;

    if (ev.clientX < sm) win.layout = "snap-left";
    else if (ev.clientX > vw - sm) win.layout = "snap-right";
    else if (ev.clientY < sm) win.layout = "maximized";
    else win.layout = "normal";

    saveState();
    renderAllWindows();
  }

  document.addEventListener("mousemove", onMove);
  document.addEventListener("mouseup", onUp);
}

// TASKBAR

function renderTaskbar() {
  taskbarApps.innerHTML = "";

  const byApp = {};
  state.windows.forEach((w) => {
    if (!byApp[w.appId]) byApp[w.appId] = [];
    byApp[w.appId].push(w);
  });

  Object.keys(byApp).forEach((appId) => {
    const app = APPS[appId];
    const wins = byApp[appId];
    const isActive = wins.some((w) => w.id === state.activeWindowId);
    const hasVisible = wins.some((w) => !w.minimized);

    const btn = document.createElement("button");
    btn.className = "qa-taskbar-app-btn";
    if (isActive && hasVisible) btn.classList.add("qa-active");
    if (hasVisible && !isActive) btn.classList.add("qa-running");
    btn.innerHTML = `<span class="qa-taskbar-app-icon">${app ? app.icon : "📦"}</span>`;
    btn.title = app ? app.title : appId;
    btn.dataset.label = app ? app.short : appId;

    btn.addEventListener("click", () => {
      const visible = wins.filter((w) => !w.minimized);
      if (visible.length === 0) {
        wins[0].minimized = false;
        state.activeWindowId = wins[0].id;
      } else {
        const topWin = visible.reduce((a, b) => (a.z > b.z ? a : b));
        if (state.activeWindowId === topWin.id) {
          visible.forEach((w) => (w.minimized = true));
          state.activeWindowId = null;
        } else {
          focusWindow(topWin.id);
          return;
        }
      }
      saveState();
      renderAllWindows();
      renderTaskbar();
    });

    btn.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      wins.slice().forEach((w) => actuallyCloseWindow(w.id, app));
    });

    taskbarApps.appendChild(btn);
  });

  // Submit button / tile only visible during capstone
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
  state.installedApps = state.installedApps.filter((x) => x !== id);
  state.windows = state.windows.filter((w) => w.appId !== id);
  saveState();
  renderAllWindows();
  renderTaskbar();
  renderStartMenu();
}

// STATE PERSISTENCE

function saveState() {
  try {
    const toSave = {
      role: state.role,
      windows: state.windows,
      activeWindowId: state.activeWindowId,
      nextWindowId: state.nextWindowId,
      nextZ: state.nextZ,
      theme: state.theme,
      background: state.background,
      brightness: state.brightness,
      installedApps: state.installedApps,
      fidelity: state.fidelity,
      // capstone/session fields intentionally NOT persisted
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
  } catch (e) {
    // ignore
  }
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const parsed = JSON.parse(raw);
    if (parsed.role === "junior" || parsed.role === "senior")
      state.role = parsed.role;
    if (Array.isArray(parsed.windows)) state.windows = parsed.windows;
    if (
      typeof parsed.activeWindowId === "number" ||
      parsed.activeWindowId === null
    )
      state.activeWindowId = parsed.activeWindowId;
    if (typeof parsed.nextWindowId === "number")
      state.nextWindowId = parsed.nextWindowId;
    if (typeof parsed.nextZ === "number") state.nextZ = parsed.nextZ;
    if (parsed.theme === "dark" || parsed.theme === "light")
      state.theme = parsed.theme;
    if (parsed.background) state.background = parsed.background;
    if (Array.isArray(parsed.installedApps)) {
      state.installedApps = parsed.installedApps;
      // Merge in any apps added to APPS after the last save.
      // Without this, a newly-added app (e.g. "browser") won't appear
      // because the old saved list doesn't know about it yet.
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

  // Read active bug configuration injected by capstone.html before launching
  // the OS. capstone.html writes an array of enabled bugId strings to
  // 'qa-capstone-activeBugs' in localStorage so the OS can read them here.
  // This is the cleanest cross-frame communication path since both share the
  // same file:// origin when the OS runs as a srcdoc with allow-same-origin.
  try {
    var capstoneBugs = localStorage.getItem("qa-capstone-activeBugs");
    if (capstoneBugs) {
      var bugList = JSON.parse(capstoneBugs);
      if (Array.isArray(bugList)) {
        state.activeBugs = bugList;
      }
    }
  } catch (e) {
    // ignore — activeBugs stays as [] which means no bugs active (safe default)
  }
}

// SUBMIT / SCORING

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
