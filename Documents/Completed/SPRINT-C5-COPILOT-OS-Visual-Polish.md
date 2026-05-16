# Sprint C5 — OS Visual Polish (Boot Screen, Browser, Settings, Taskbar)
## Copilot Prompt — GitHub repo: andrewdhannah/QA-Pilot

You are working in the QA Pilot repository, specifically the desktop simulator.
All changes are in `desktop/` unless noted otherwise.
No CDN links, no external imports, no fetch(). File:// safe architecture.
Run `node desktop/build.js` after all changes are complete.

Read `desktop/src/os-core.js` and `desktop/os.css` before writing any code.
Read each app HTML file before editing it.

---

## Context

The OS desktop is a Windows 11-inspired simulator built in pure HTML/CSS/JS.
It already has: a lock screen, taskbar, start menu, notification center,
window management, and app iframes.

This sprint adds polish to five areas:
1. Boot screen — Win11-style logo + animated spinner before the lock screen
2. Browser app — remove duplicate title bar, more pronounced tabs
3. Settings app — Win11-style sidebar nav + About page
4. Taskbar — running-app indicator dots under active apps
5. Lock screen — subtle background depth

No changes to: `js/db.js`, `js/app.js`, `data/`, Academy HTML pages.
Do NOT add CDN links or external fonts.
Run `node build.js` at the end.

---

## Deliverable 1: Boot Screen

### 1a. Add boot screen HTML to index.html

Add a new `#qa-boot-screen` div as the FIRST child inside `#qa-shell`,
before `#qa-lock-screen`:

```html
<!-- ── BOOT SCREEN ──────────────────────────────────────────────────── -->
<!-- Shown for ~2.5s on first load, then fades out to the lock screen.   -->
<div id="qa-boot-screen" class="qa-boot-screen">
  <div class="qa-boot-center">

    <!-- QA Pilot logo mark -->
    <div class="qa-boot-logo">
      <svg width="72" height="72" viewBox="0 0 72 72" fill="none"
           xmlns="http://www.w3.org/2000/svg">
        <rect width="72" height="72" rx="16" fill="#2563eb"/>
        <path d="M20 36 L30 46 L52 24"
              stroke="white" stroke-width="6"
              stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="36" cy="36" r="14" stroke="white" stroke-width="2"
                fill="none" opacity="0.25"/>
      </svg>
    </div>

    <div class="qa-boot-product">QA Pilot</div>
    <div class="qa-boot-slogan">Test Smarter. Ship Better.</div>

    <!-- Win11-style dot spinner -->
    <div class="qa-boot-spinner" aria-label="Loading">
      <div class="qa-boot-dot"></div>
      <div class="qa-boot-dot"></div>
      <div class="qa-boot-dot"></div>
      <div class="qa-boot-dot"></div>
      <div class="qa-boot-dot"></div>
    </div>

  </div>
</div>
```

### 1b. Add boot screen CSS to os.css

```css
/* ── BOOT SCREEN ──────────────────────────────────────────────────────── */

.qa-boot-screen {
  position: fixed;
  inset: 0;
  background: #050a14;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  transition: opacity 0.6s ease;
}

.qa-boot-screen.qa-boot-hidden {
  opacity: 0;
  pointer-events: none;
}

.qa-boot-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.qa-boot-logo {
  animation: qa-boot-logo-in 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

@keyframes qa-boot-logo-in {
  from { opacity: 0; transform: scale(0.7); }
  to   { opacity: 1; transform: scale(1); }
}

.qa-boot-product {
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.01em;
  animation: qa-boot-fade-up 0.5s 0.2s ease both;
}

.qa-boot-slogan {
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  font-size: 13px;
  color: rgba(255,255,255,0.45);
  letter-spacing: 0.02em;
  animation: qa-boot-fade-up 0.5s 0.35s ease both;
}

@keyframes qa-boot-fade-up {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Win11-style bouncing dot spinner */
.qa-boot-spinner {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 32px;
  animation: qa-boot-fade-up 0.5s 0.5s ease both;
}

.qa-boot-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(255,255,255,0.85);
  animation: qa-boot-bounce 1.4s ease-in-out infinite both;
}

.qa-boot-dot:nth-child(1) { animation-delay: 0.0s; }
.qa-boot-dot:nth-child(2) { animation-delay: 0.16s; }
.qa-boot-dot:nth-child(3) { animation-delay: 0.32s; }
.qa-boot-dot:nth-child(4) { animation-delay: 0.48s; }
.qa-boot-dot:nth-child(5) { animation-delay: 0.64s; }

@keyframes qa-boot-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.3; }
  40%            { transform: scale(1.0); opacity: 1.0; }
}
```

### 1c. Add boot logic to os-core.js

In the `init()` function, find where `loadState()` is called and add a
boot sequence that shows the boot screen for 2.5s then fades it out:

```javascript
// ── BOOT SEQUENCE ─────────────────────────────────────────────────────
// Show boot screen for 2.5s (simulating OS startup), then fade out.
// The lock screen sits beneath it and becomes visible after the fade.
var bootScreen = document.getElementById('qa-boot-screen');
if (bootScreen) {
  // Delay everything until after boot screen fades (matches CSS transition)
  setTimeout(function() {
    bootScreen.classList.add('qa-boot-hidden');
    // Remove from DOM after transition completes so it doesn't block clicks
    setTimeout(function() {
      bootScreen.style.display = 'none';
    }, 650);
  }, 2500);
}
```

Add `bootScreen` to the variable declarations at the top of `init()` alongside
`lockScreen`, `clockEl`, etc.

---

## Deliverable 2: Browser App — Remove Duplicate Title Bar + Better Tabs

File: `desktop/apps/browser.html`

### 2a. Remove the `.br-titlebar` block entirely

Delete these lines (the entire titlebar div, approximately lines 247–252):
```html
<div class="br-titlebar">
  <div class="br-titlebar-icon">e</div>
  <div class="br-titlebar-title">Edge — Training Browser</div>
</div>
```

The OS window already shows "QA Browser — Tabbed Workspace" in its own
title bar. This inner titlebar is a duplicate bar.

Also delete the corresponding CSS rules:
```css
.br-titlebar { … }
.br-titlebar-icon { … }
.br-titlebar-title { … }
```

### 2b. Replace tab CSS with more pronounced styling

Replace the existing `.br-tab`, `.br-tab-active`, `.br-tab-title`,
`.br-tab-close` CSS with:

```css
.br-tabs-row {
  height: 36px;
  display: flex;
  align-items: flex-end;
  padding: 0 4px;
  box-sizing: border-box;
  background: var(--br-bg-alt);
  border-bottom: 1px solid var(--br-border-subtle);
  gap: 2px;
}

.br-tab {
  min-width: 130px;
  max-width: 220px;
  height: 30px;
  border-radius: 6px 6px 0 0;
  background: rgba(0,0,0,0.04);
  border: 1px solid transparent;
  border-bottom: none;
  display: flex;
  align-items: center;
  padding: 0 10px;
  box-sizing: border-box;
  font-size: 12px;
  color: var(--br-text-subtle);
  cursor: pointer;
  gap: 6px;
  transition: background 0.12s;
  position: relative;
}

body.theme-dark .br-tab {
  background: rgba(255,255,255,0.04);
}

.br-tab:hover:not(.br-tab-active) {
  background: rgba(0,0,0,0.07);
}

body.theme-dark .br-tab:hover:not(.br-tab-active) {
  background: rgba(255,255,255,0.08);
}

.br-tab-active {
  background: var(--br-tab-bg-active) !important;
  border-color: var(--br-border-subtle);
  color: var(--br-text);
  font-weight: 500;
  /* Accent line at top of active tab */
  box-shadow: inset 0 2px 0 0 var(--br-blue);
}

.br-tab-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 12px;
}

.br-tab-close {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  line-height: 1;
  color: var(--br-text-subtle);
  opacity: 0.5;
  flex-shrink: 0;
  transition: opacity 0.1s, background 0.1s;
}

.br-tab:hover .br-tab-close,
.br-tab-active .br-tab-close {
  opacity: 1;
}

.br-tab-close:hover {
  background: rgba(0,0,0,0.1);
  opacity: 1;
}

body.theme-dark .br-tab-close:hover {
  background: rgba(255,255,255,0.15);
}

.br-tab-new {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--br-text-subtle);
  font-size: 18px;
  line-height: 1;
  flex-shrink: 0;
  transition: background 0.12s;
}

.br-tab-new:hover {
  background: rgba(0,0,0,0.07);
  color: var(--br-text);
}

body.theme-dark .br-tab-new:hover {
  background: rgba(255,255,255,0.1);
}
```

### 2c. Update the OS window title for browser

In `desktop/src/os-core.js`, find the APPS registry `browser` entry and
update the title to be shorter (the tabbed workspace label was redundant
with the in-app tab row):

```javascript
browser: {
  id:    "browser",
  title: "QA Browser",
  short: "Browser",
  icon:  `...` // keep existing SVG
},
```

---

## Deliverable 3: Settings App — Win11 Sidebar Layout + About Page

File: `desktop/apps/settings.html`

Replace the entire file with a two-column Win11-style layout.
Keep ALL existing functionality (brightness, theme, background, fidelity,
app toggles). Add a new "About" section. Add dark mode support.

### Layout structure

```html
<!doctype html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>Settings</title>
  <style>
    /* ... see CSS below ... */
  </style>
</head>
<body class="theme-light">
  <div class="st-root">

    <!-- Left sidebar nav -->
    <nav class="st-nav">
      <div class="st-nav-header">Settings</div>

      <div class="st-nav-item active" data-section="system">
        <svg class="st-nav-icon" viewBox="0 0 20 20" fill="currentColor">
          <path d="M10 2a8 8 0 100 16A8 8 0 0010 2zm0 2a6 6 0 110 12A6 6 0 0110 4zm0 3a3 3 0 100 6 3 3 0 000-6z"/>
        </svg>
        System
      </div>

      <div class="st-nav-item" data-section="personalization">
        <svg class="st-nav-icon" viewBox="0 0 20 20" fill="currentColor">
          <path d="M4 5a2 2 0 012-2h8a2 2 0 012 2v10a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm2 0v10h8V5H6zm1 2h6v2H7V7zm0 4h4v2H7v-2z"/>
        </svg>
        Personalization
      </div>

      <div class="st-nav-item" data-section="apps">
        <svg class="st-nav-icon" viewBox="0 0 20 20" fill="currentColor">
          <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zm0 8a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zm6-8a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2h-2zm0 8a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2h-2z"/>
        </svg>
        Apps
      </div>

      <div class="st-nav-item" data-section="about">
        <svg class="st-nav-icon" viewBox="0 0 20 20" fill="currentColor">
          <path d="M18 10A8 8 0 102 10a8 8 0 0016 0zm-8-3a1 1 0 110 2 1 1 0 010-2zm-1 4h2v4H9v-4z"/>
        </svg>
        About
      </div>
    </nav>

    <!-- Main content area — sections toggled by nav -->
    <main class="st-main">

      <!-- SYSTEM -->
      <section class="st-section" id="st-section-system">
        <h2 class="st-section-title">System</h2>

        <div class="st-group">
          <div class="st-group-label">Display</div>
          <div class="st-row">
            <div class="st-row-info">
              <span class="st-row-label">Brightness</span>
              <span class="st-row-sub">Adjust screen brightness</span>
            </div>
            <input id="settings-brightness" type="range" class="st-slider"
                   min="50" max="120" value="100"/>
          </div>
        </div>

        <div class="st-group">
          <div class="st-group-label">Colour theme</div>
          <div class="st-row">
            <div class="st-row-info">
              <span class="st-row-label">App theme</span>
              <span class="st-row-sub">Choose light or dark mode</span>
            </div>
            <div class="st-pill-row">
              <button id="settings-theme-light" class="st-pill active">Light</button>
              <button id="settings-theme-dark"  class="st-pill">Dark</button>
            </div>
          </div>
        </div>

        <div class="st-group">
          <div class="st-group-label">Visual fidelity</div>
          <div class="st-row">
            <div class="st-row-info">
              <span class="st-row-label">Window style</span>
              <span class="st-row-sub">Windows 11 mode uses frosted glass effects</span>
            </div>
            <div class="st-pill-row">
              <button id="settings-fidelity-win11"    class="st-pill active">Windows 11</button>
              <button id="settings-fidelity-classic"  class="st-pill">Classic</button>
            </div>
          </div>
        </div>
      </section>

      <!-- PERSONALIZATION -->
      <section class="st-section" id="st-section-personalization" style="display:none">
        <h2 class="st-section-title">Personalization</h2>

        <div class="st-group">
          <div class="st-group-label">Desktop background</div>
          <div class="st-bg-grid" id="st-bg-grid">
            <button class="st-bg-swatch active" data-bg="default">
              <div class="st-bg-preview st-bg-default"></div>
              <span>Default</span>
            </button>
            <button class="st-bg-swatch" data-bg="sunrise">
              <div class="st-bg-preview st-bg-sunrise"></div>
              <span>Sunrise</span>
            </button>
            <button class="st-bg-swatch" data-bg="glow">
              <div class="st-bg-preview st-bg-glow"></div>
              <span>Glow</span>
            </button>
          </div>
        </div>
      </section>

      <!-- APPS -->
      <section class="st-section" id="st-section-apps" style="display:none">
        <h2 class="st-section-title">Apps</h2>
        <div class="st-group">
          <div class="st-group-label">Installed applications</div>
          <div id="settings-app-list"></div>
        </div>
      </section>

      <!-- ABOUT -->
      <section class="st-section" id="st-section-about" style="display:none">
        <h2 class="st-section-title">About</h2>

        <div class="st-about-hero">
          <svg width="52" height="52" viewBox="0 0 52 52" fill="none"
               xmlns="http://www.w3.org/2000/svg">
            <rect width="52" height="52" rx="12" fill="#2563eb"/>
            <path d="M14 26 L22 34 L38 18"
                  stroke="white" stroke-width="4.5"
                  stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <div>
            <div class="st-about-name">QA Pilot Desktop</div>
            <div class="st-about-version">Version 1.0 · Sprint 5</div>
          </div>
        </div>

        <div class="st-group">
          <div class="st-group-label">Platform</div>
          <div class="st-row st-row-static">
            <span class="st-row-label">Built on</span>
            <span class="st-row-value">Modular OS v4</span>
          </div>
          <div class="st-row st-row-static">
            <span class="st-row-label">Architecture</span>
            <span class="st-row-value">Pure HTML/CSS/JS · file:// safe</span>
          </div>
          <div class="st-row st-row-static">
            <span class="st-row-label">Data layer</span>
            <span class="st-row-value">IndexedDB (QA Pilot Academy)</span>
          </div>
        </div>

        <div class="st-group">
          <div class="st-group-label">Credits</div>
          <div class="st-row st-row-static">
            <span class="st-row-label">Product owner</span>
            <span class="st-row-value">Andrew Hannah</span>
          </div>
          <div class="st-row st-row-static">
            <span class="st-row-label">Built with</span>
            <span class="st-row-value">GitHub Copilot + Claude (Anthropic)</span>
          </div>
          <div class="st-row st-row-static">
            <span class="st-row-label">Design language</span>
            <span class="st-row-value">Microsoft Fluent / Windows 11</span>
          </div>
        </div>

        <div class="st-group">
          <div class="st-group-label">Description</div>
          <p class="st-about-desc">
            QA Pilot Desktop is a Windows 11-inspired simulator used to train
            junior QA professionals. Students investigate realistic bug scenarios
            using mock versions of Dynamics 365, Azure DevOps, and an AC Panel —
            all running offline in the browser with no external dependencies.
          </p>
        </div>
      </section>

    </main>
  </div>

  <script>
    /* ... all existing settings logic, updated for new IDs + new about section ... */
    /* Nav switching, brightness, theme, background, fidelity, app list — all kept */
    /* Add nav item click → show/hide sections logic */
  </script>
</body>
</html>
```

### Settings CSS

Write complete CSS for the settings app. Key rules:

```css
:root {
  --st-bg:       #f3f2f1;
  --st-surface:  #ffffff;
  --st-nav-bg:   #f3f2f1;
  --st-border:   #e5e3e0;
  --st-text:     #1a1a1a;
  --st-sub:      #6b7280;
  --st-blue:     #2563eb;
  --st-active:   rgba(37,99,235,0.1);
  --st-radius:   8px;
}

body.theme-dark {
  --st-bg:      #202020;
  --st-surface: #2d2d2d;
  --st-nav-bg:  #1c1c1c;
  --st-border:  #3a3a3a;
  --st-text:    #f3f2f1;
  --st-sub:     #9ca3af;
  --st-active:  rgba(37,99,235,0.2);
}

body { margin: 0; font-family: system-ui,-apple-system,"Segoe UI",sans-serif;
       background: var(--st-bg); color: var(--st-text); }

.st-root { display: flex; height: 100vh; overflow: hidden; }

/* Nav */
.st-nav { width: 200px; background: var(--st-nav-bg); padding: 12px 8px;
           box-sizing: border-box; flex-shrink: 0; border-right: 1px solid var(--st-border); }
.st-nav-header { font-size: 20px; font-weight: 700; padding: 8px 10px 16px;
                  color: var(--st-text); }
.st-nav-item { display: flex; align-items: center; gap: 10px; padding: 9px 10px;
               border-radius: var(--st-radius); cursor: pointer; font-size: 13px;
               color: var(--st-sub); transition: background 0.1s, color 0.1s; }
.st-nav-item:hover { background: rgba(0,0,0,0.05); color: var(--st-text); }
body.theme-dark .st-nav-item:hover { background: rgba(255,255,255,0.06); }
.st-nav-item.active { background: var(--st-active); color: var(--st-blue);
                       font-weight: 600; }
.st-nav-icon { width: 16px; height: 16px; flex-shrink: 0; }

/* Main */
.st-main { flex: 1; overflow-y: auto; padding: 20px 28px; }
.st-section-title { font-size: 22px; font-weight: 700; margin: 0 0 20px;
                     color: var(--st-text); }

/* Groups + rows */
.st-group { margin-bottom: 20px; }
.st-group-label { font-size: 11px; font-weight: 700; text-transform: uppercase;
                   letter-spacing: 0.07em; color: var(--st-sub); margin-bottom: 6px; }
.st-row { display: flex; align-items: center; justify-content: space-between;
          padding: 12px 14px; background: var(--st-surface); border: 1px solid var(--st-border);
          border-radius: var(--st-radius); margin-bottom: 2px; gap: 16px; }
.st-row-info { display: flex; flex-direction: column; gap: 2px; }
.st-row-label { font-size: 13px; font-weight: 500; }
.st-row-sub   { font-size: 11px; color: var(--st-sub); }
.st-row-value { font-size: 12px; color: var(--st-sub); }
.st-row-static { cursor: default; }

/* Slider */
.st-slider { flex-shrink: 0; width: 140px; accent-color: var(--st-blue); }

/* Pills */
.st-pill-row { display: flex; gap: 4px; }
.st-pill { padding: 5px 12px; border-radius: 999px; border: 1px solid var(--st-border);
           background: var(--st-bg); font-size: 12px; cursor: pointer;
           color: var(--st-sub); transition: all 0.12s; }
.st-pill:hover { border-color: var(--st-blue); color: var(--st-blue); }
.st-pill.active { background: var(--st-active); border-color: var(--st-blue);
                  color: var(--st-blue); font-weight: 600; }

/* Background swatches */
.st-bg-grid { display: flex; gap: 10px; flex-wrap: wrap; }
.st-bg-swatch { display: flex; flex-direction: column; align-items: center;
                gap: 6px; border: 2px solid transparent; border-radius: 10px;
                padding: 6px; cursor: pointer; background: transparent;
                transition: border-color 0.15s; font-size: 11px; color: var(--st-sub); }
.st-bg-swatch.active { border-color: var(--st-blue); color: var(--st-blue); }
.st-bg-preview { width: 80px; height: 50px; border-radius: 6px;
                  border: 1px solid var(--st-border); }
.st-bg-default { background: linear-gradient(135deg, #1a1f36 0%, #2d3561 100%); }
.st-bg-sunrise { background: linear-gradient(135deg, #f97316 0%, #f43f5e 50%, #6366f1 100%); }
.st-bg-glow    { background: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 50%, #ec4899 100%); }

/* About section */
.st-about-hero { display: flex; align-items: center; gap: 14px; padding: 16px 14px;
                  background: var(--st-surface); border: 1px solid var(--st-border);
                  border-radius: var(--st-radius); margin-bottom: 20px; }
.st-about-name    { font-size: 16px; font-weight: 700; }
.st-about-version { font-size: 12px; color: var(--st-sub); margin-top: 2px; }
.st-about-desc    { font-size: 13px; line-height: 1.65; color: var(--st-sub);
                     margin: 0; padding: 12px 14px; background: var(--st-surface);
                     border: 1px solid var(--st-border); border-radius: var(--st-radius); }

/* App list rows (inside Apps section) */
.st-app-row { display: flex; align-items: center; justify-content: space-between;
              padding: 10px 14px; background: var(--st-surface);
              border: 1px solid var(--st-border); border-radius: var(--st-radius);
              margin-bottom: 2px; font-size: 13px; }
.st-app-toggle { padding: 4px 12px; border-radius: 999px; border: 1px solid var(--st-border);
                  background: transparent; cursor: pointer; font-size: 11px;
                  color: var(--st-sub); transition: all 0.12s; }
.st-app-toggle:hover { border-color: var(--st-blue); color: var(--st-blue); }
```

### Nav switching JS (add to script block)

```javascript
// Section navigation
document.querySelectorAll('.st-nav-item').forEach(function(item) {
  item.addEventListener('click', function() {
    var sectionId = item.getAttribute('data-section');
    document.querySelectorAll('.st-nav-item').forEach(function(n) {
      n.classList.toggle('active', n === item);
    });
    document.querySelectorAll('.st-section').forEach(function(s) {
      s.style.display = s.id === 'st-section-' + sectionId ? '' : 'none';
    });
  });
});

// APP_BOOT: apply theme
window.addEventListener('message', function(event) {
  var msg = event.data;
  if (!msg || msg.type !== 'APP_BOOT' || msg.appId !== 'settings') return;
  if (msg.theme === 'dark') document.body.classList.add('theme-dark');
  else document.body.classList.remove('theme-dark');
});
```

Keep all existing functionality (brightness, theme, background, fidelity,
app list). Update element IDs to match the new markup (`settings-brightness`,
`settings-theme-light`, `settings-theme-dark`, `settings-fidelity-win11`,
`settings-fidelity-classic` remain the same so os-core.js wiring is unchanged).

---

## Deliverable 4: Taskbar — Running-App Indicator

### CSS (add to os.css)

```css
/* Win11-style running indicator — small centred line under active app */
.qa-taskbar-app-btn {
  position: relative;
}

.qa-taskbar-app-btn::after {
  content: '';
  position: absolute;
  bottom: 3px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  border-radius: 2px;
  background: currentColor;
  opacity: 0;
  transition: width 0.15s, opacity 0.15s;
}

/* Any open app shows a subtle dot */
.qa-taskbar-app-btn.running::after {
  opacity: 0.55;
  width: 4px;
}

/* The focused/active window's app shows a wider, fully opaque line */
.qa-taskbar-app-btn.running.focused::after {
  opacity: 1;
  width: 16px;
}
```

In `os-core.js`, update `renderTaskbar()` to add `running` and `focused`
classes to taskbar buttons:
- `running` → any app that has at least one open window
- `focused` → the app whose window is currently `state.activeWindowId`

---

## Deliverable 5: Lock Screen — Subtle Background Depth

In `os.css`, find the `.qa-lock-screen` rule and add a subtle noise pattern
via a CSS gradient overlay so it feels less flat:

```css
.qa-lock-screen {
  /* Keep existing background rules, ADD: */
  background-image:
    radial-gradient(ellipse at 30% 60%, rgba(37,99,235,0.18) 0%, transparent 60%),
    radial-gradient(ellipse at 75% 25%, rgba(139,92,246,0.12) 0%, transparent 55%);
}
```

---

## Definition of Done

- [ ] Boot screen appears for ~2.5s on first load then fades to lock screen
- [ ] QA Pilot logo and "Test Smarter. Ship Better." are visible on boot screen
- [ ] Dot spinner animates correctly with staggered delay
- [ ] Browser app has no inner title bar (only the OS window bar remains)
- [ ] Browser tabs are taller, active tab has blue top accent, all tabs have visible close X
- [ ] Browser window title is "QA Browser" (not "QA Browser — Tabbed Workspace")
- [ ] Settings has a left sidebar with 4 sections: System, Personalization, Apps, About
- [ ] About section shows product info, platform, credits, and description
- [ ] All existing settings (brightness, theme, background, fidelity, app list) still work
- [ ] Taskbar shows running dot under open apps, wider dot under the focused app
- [ ] Lock screen has the gradient overlay depth effect
- [ ] `node build.js` completes with all 3 outputs ✓ including capstone.html sync
- [ ] No CDN links or external assets added anywhere
