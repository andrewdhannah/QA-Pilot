# Ash Handoff — Post-Sprint Verification
## For: New Cowork session with Andrew (Andrew calls Claude "Ash")
## Last updated: May 2026 — includes C4, C5, G3, G4, G5 sprints + 6 UI/UX phases + architecture refactor

---

## What This Is

The **QA Pilot** platform is a Windows 11-style desktop simulator built for QA onboarding training.
It has two integrated halves:

- **QA Pilot Academy** — HTML/CSS/JS lesson platform (index.html → lessons → capstone → certificate)
- **QA Pilot Desktop** — OS simulator (dist.html, embedded in capstone.html as srcdoc iframe)

**Repo:** https://github.com/andrewdhannah/QA-Pilot  
**Local:** `/Users/andrew/Documents/Claude/Projects/QA Pilot/`  
**Build:** `./build.sh` from project root → runs `node desktop/build.js`  
**Stack:** Pure HTML/CSS/JS. No frameworks, no CDN at runtime. file:// safe.  
**CSS tokens:** `css/main.css` — read before touching any CSS.  
**Data layer:** IndexedDB via `js/db.js`.  

---

## Pre-Sprint Fixes Applied (verify these are still intact)

These bugs were fixed before the sprints ran. Confirm they haven't been regressed:

### js/db.js
- `getBugToggles()` uses key `'activeBugs'` (NOT `'bugToggles'`) and correctly unwraps the IDB record value
- `awardCertificate()` dual-writes both `progress.certificateAwarded = true` AND `progress.certificateEarned = true`

### desktop/src/os-core.js
- `loadState()` merges new APPS keys into loaded `installedApps` array (so newly added apps aren't blocked by old localStorage)
- `loadState()` reads `localStorage['qa-capstone-activeBugs']` and applies it to `state.activeBugs`
- `renderForm()` in dynamics.html has null guards on `resolutionEl` and `resolutionDateEl` (applyRole removes them before renderForm runs)

### capstone.html
- `isCapstoneUnlocked()` handles both standard path (lesson-4) AND accelerated survey paths (checks all assigned lessons except 'capstone' are complete)
- `progress.placementSurvey` has null guard with fallback to full standard path

### desktop/apps/browser.html
- `br-frame` has explicit `srcdoc="<!doctype html><html><body></body></html>"` to prevent file:// unsafe load warning

### desktop/build.js
- Capstone sync uses `indexOf` (not regex) to find `/* BUILD:OS_START */` and `/* BUILD:OS_END */` markers — no false "markers not found" warnings

---

## Sprint C4 — IndexedDB OS Bridge
**Files touched:** `desktop/build.js`, `desktop/src/os-core.js`, `capstone.html`  
**Do NOT touch:** `js/db.js`, `js/app.js`

### What it should have done
1. `js/db.js` bundled as the **first JS block** in `desktop/os.bundle.js` and `desktop/dist.html`
2. `CAPSTONE_SESSION_KEY = "qa-capstone-session"` constant added in os-core.js after `STORAGE_KEY`
3. `loadCapstoneSession()` IIFE in `loadState()` — reads localStorage session object, sets `state.capstoneCaseId`, `state.role`, `state.activeScenarioId`, converts `bugToggles` map to `state.activeBugs` array
4. On submit, OS writes score to IndexedDB via `saveQuizResults()` and `awardCertificate()` if `state.capstoneCaseId` is set
5. `capstone.html` writes full session object `{ caseId, role, scenarioId, bugToggles }` to `localStorage['qa-capstone-session']` before launching OS
6. Lesson completion gate in capstone.html — redirects to course.html with error toast if prerequisites not complete
7. `handleOSMessage()` simplified — just removes session key and redirects to certificate.html after 2000ms

### Verify
- [ ] `node desktop/build.js` completes with no errors
- [ ] `db.js` is the first JS block in `desktop/os.bundle.js` (check top of file)
- [ ] Open capstone from a completed-lessons account — browser DevTools console logs correct caseId on OS boot
- [ ] Bug toggles set in admin Bug Lab reach `state.activeBugs` in the OS
- [ ] After OS submit, IndexedDB (DevTools → Application → IndexedDB → QAPilotDB) shows score data
- [ ] Navigate directly to capstone.html without completing lessons — should redirect to course.html with toast
- [ ] Open `desktop/dist.html` directly (no capstone session) — should boot normally with no errors

---

## Sprint C5 — OS Visual Polish
**Files touched:** `desktop/src/os-core.js`, `desktop/apps/browser.html`, `desktop/apps/settings.html`, `desktop/index.html`, `desktop/os.css`

### What it should have done
1. **Boot screen** — appears on first load, shows 72px blue rounded-rect logo with checkmark SVG, tagline "Test Smarter. Ship Better.", 5-dot bounce spinner animation, fades out after ~2.5s to reveal lock screen
2. **Browser app** — `.br-titlebar` div removed (was redundant with OS window title bar), tabs are 30px tall, active tab has `box-shadow: inset 0 2px 0 0 var(--br-blue)` accent, close X always visible, app title shortened to "QA Browser"
3. **Settings app** — full Win11 rebuild: 200px left sidebar nav (System, Personalization, Apps, About sections, each with SVG icon), About section shows product name/version/credits, dark mode CSS tokens, all existing functionality preserved
4. **Taskbar running indicators** — open apps show a 4px dot via `::after` pseudo-element with class `running`, focused app shows a 16px wider bar with class `focused`
5. **Lock screen** — radial gradient overlay added for visual depth

### Verify
- [ ] Load `desktop/dist.html` (or via `index.html`) — boot screen appears, animates, fades
- [ ] After boot, lock screen shows with gradient overlay
- [ ] Open Browser app — no double title bar, tabs are visible and pronounced, active tab has blue top accent
- [ ] Open Settings — left sidebar nav is visible, clicking each section shows correct content, About section shows product info
- [ ] Open any app, check taskbar — open app icon shows small dot indicator below it
- [ ] Click another window to focus — focused app dot is wider/different from non-focused running apps
- [ ] Run `./build.sh` — no errors, dist.html updated

---

## Sprint G3 — Academy Visual Refresh
**Files touched:** `css/main.css`, `course.html`, `lesson-1.html`, `lesson-2.html`, `lesson-3.html`, `lesson-4.html`  
**Do NOT touch:** `js/db.js`, `js/app.js`, `data/`, `admin/`, `desktop/`, `certificate.html`

### What it should have done
1. **4 lesson accent colour sets** added to `:root` in `css/main.css` (after status color block):
   - `--lesson-1-color: #2563eb` (Blue — Testing 101) + light + border
   - `--lesson-2-color: #ea580c` (Orange — Bug Reporting) + light + border
   - `--lesson-3-color: #0891b2` (Teal — CRM Tools) + light + border
   - `--lesson-4-color: #7c3aed` (Purple — QA Process) + light + border
2. **New CSS component blocks** appended to end of `css/main.css`: `.topbar-progress-indicator`, `.topbar-progress-pip`, `.chapter-hero`, `.callout`, `.quiz-option`, `.lesson-card` (with all variants)
3. **course.html** — `showLessonList()` uses new `.lesson-card` design with `LESSON_META` map, inline SVG icons, progress bars, status badges
4. **lesson-1 through lesson-4** — each has `CHAPTER_HEROES` map with title/sub/bg/color/border/icon for every chapter, `renderChapterHero()` function injects hero at top of `.chapter-main`, topbar has `#topbar-pips` populated with pip dots

### Verify
- [ ] Open `course.html` — lesson cards show coloured left border, icon, title, progress bar, and status badge
- [ ] Each lesson card uses correct accent colour (1=blue, 2=orange, 3=teal, 4=purple)
- [ ] Open lesson-1.html, navigate to any chapter — chapter hero section shows at top with correct colour and icon
- [ ] Topbar pips update as chapters are navigated (done=green, active=blue, future=grey)
- [ ] Quiz options highlight correctly on selection (selected=blue border, correct=green, incorrect=red)
- [ ] Progress saving still works — complete a chapter, refresh, confirm progress is retained
- [ ] No CDN links or external image references added (check `<head>` of modified files)

---

## Sprint G4 — Certificate Redesign
**Files touched:** `certificate.html`  
**Do NOT touch:** anything else

### What it should have done
1. Full certificate document layout — student name, score, date, course title
2. **Score ring** — SVG circle with `stroke-dashoffset` animation on load (ring fills to score percentage)
3. **Watermark + seal** — decorative SVG background watermark, circular seal graphic
4. **Score breakdown card** — per-lesson or per-section score breakdown
5. **What's Next panel** — next steps after completing the course (links back to course, etc.)
6. **Print styles** — `@media print` removes nav, shows clean document

### Verify
- [ ] Navigate to `certificate.html` from a completed account — certificate renders with student name and score
- [ ] Score ring animates on page load (stroke-dashoffset transition)
- [ ] Watermark / seal visible in background
- [ ] Score breakdown shows per-lesson data
- [ ] What's Next panel links are correct
- [ ] `Ctrl+P` or print — shows clean certificate layout, no nav chrome

---

## Sprint G5 — Admin Dashboard Polish
**Files touched:** `admin/dashboard.html`  
**Do NOT touch:** `js/db.js`, `js/app.js`, `data/`

### What it should have done
1. **Bug Lab tab** — each bug toggle row has a `.bug-status-chip` element showing "Active" (amber pill) or "Off" (grey pill), updates after Save is clicked
2. **Bug Lab summary banner** — `#bug-lab-summary` div at top of tab showing "X bugs currently active", updates on save
3. **Save key verified** — save button calls `saveSetting('activeBugs', JSON.stringify(checked))` (NOT `'bugToggles'`)
4. **Students tab** — expandable student rows show: overall progress % pill, per-lesson quiz score badges (≥70% green, <70% orange, not attempted grey), certificate status (green check or grey dash)
5. **Admin topbar** — matches student-facing topbar style with `.topbar` / `.topbar-brand` / `.topbar-right` structure

### Verify
- [ ] Open `admin/dashboard.html` → Bug Lab tab — toggle some bugs, click Save, chips update to Active/Off
- [ ] Bug count banner at top of Bug Lab tab shows correct count and updates after save
- [ ] Check browser DevTools → Application → IndexedDB — saved key is `activeBugs` (not `bugToggles`)
- [ ] Students tab — expand a student row, verify progress %, per-lesson quiz badges, certificate status all show
- [ ] Student with ≥70% quiz score shows green badge; <70% shows orange; not attempted shows grey
- [ ] Student who earned certificate shows green check (uses `certificateAwarded || certificateEarned`)
- [ ] All 5 tabs (Students, Settings, Assign Lessons, Content Editor, Bug Lab) still load and save correctly
- [ ] Admin topbar looks visually consistent with course.html / lesson page topbars

---

## Full End-to-End Flow Test

Run through this complete path to confirm everything integrates:

1. Open `index.html` → create or log in as a student
2. Complete at least one lesson chapter and quiz
3. Open `admin/dashboard.html` → Students tab → verify that student's progress shows
4. Admin → Bug Lab → toggle 2-3 bugs on → Save → confirm chips show Active
5. Back to student session → complete all lessons
6. Navigate to `capstone.html` → confirm OS launches with correct role
7. In OS → verify bug toggles are active (bugs should affect CRM/ADO behaviour)
8. Submit capstone → OS score modal appears → redirected to `certificate.html`
9. Certificate renders with student name, score ring animates
10. Back to admin → Students tab → student shows 100% progress + certificate earned

---

---

## Architecture Refactor — New src/ Layers

Three new source files were added to `desktop/src/`. They are bundled in dependency order by `desktop/build.js`:

```
db.js → event-bus.js → compositor.js → workspaces.js → APP_HTML → scenarios → os-core.js
```

**Verify build order is correct** — if compositor.js loads before event-bus.js, or os-core.js loads before compositor.js, runtime errors will occur on first window open.

### src/event-bus.js
Pub/sub for internal shell events. Replaces direct `window.addEventListener("message")` and `iframe.contentWindow.postMessage()` calls.
- `EventBus.on(event, handler)` / `EventBus.off()` / `EventBus.emit()`
- `EventBus.postToApp(winId, msg)` / `EventBus.postToAllApps(msg)`
- `EventBus.onAppMessage(handler)` — single message listener for all app iframes
- `EventBus.registerAppWindow(winId, iframe)` — queues messages until iframe is ready, then flushes
- Exposed on `window.EventBus`

### src/compositor.js
Window state management extracted from os-core.js. `state.windows`, `state.nextWindowId`, `state.nextZ`, `state.activeWindowId` all removed from os-core.js and delegated here.
- `Compositor.createWindow(config)` / `Compositor.destroyWindow(id)`
- `Compositor.focusWindow(id)` / `Compositor.minimizeWindow(id)`
- `Compositor.setLayout(id, layout)` — layouts: `normal`, `maximized`, `snap-left`, `snap-right`, `snap-tl`, `snap-tr`, `snap-bl`, `snap-br`
- `Compositor.serialize()` / `Compositor.deserialize(data)` — includes legacy null width/height migration
- Emits lifecycle events: `window-created`, `window-destroyed`, `window-focused`
- Width/height defaults: 800×600 fallback if container too small

### src/workspaces.js
IndexedDB-backed workspace persistence. Uses its own database (`qa-workspaces`, separate from `QAPilotDB`).
- `Workspaces.save(name)` — named save
- `Workspaces.restore(name)` — restores window layout by name
- `Workspaces.list()` — returns all saved workspaces
- `Workspaces.delete(name)`
- Auto-save snapshots on every window change (debounced, max 10 kept)
- Used by OS for auto-saving workspace state

---

## UI/UX Phases — What Was Built

### Phase 1 — Resize Handles
- **compositor.js:** `resize()` method, quadrant snap layouts (`snap-tl`, `snap-tr`, `snap-bl`, `snap-br`), width/height defaults (800×600 fallback)
- **os-core.js:** `startResize()` drag handler for right-edge, bottom-edge, bottom-right-corner handles. Uses `getBoundingClientRect()` for robust sizing.

**Verify:**
- [ ] Drag right edge of a window → resizes horizontally
- [ ] Drag bottom edge → resizes vertically
- [ ] Drag bottom-right corner → resizes both axes
- [ ] Snap layout `snap-tl` places window in top-left quadrant at correct size

### Phase 2 — Snap Layout Flyout
- Hover the maximize button (□) → flyout appears with 5 options: Full, TL, TR, BL, BR
- Flyout uses `backdrop-filter: blur()` glass effect with smooth fade-in animation
- Clicking a cell calls `compositor.setLayout()` and re-renders

**Verify:**
- [ ] Hover maximize button → flyout appears within ~200ms
- [ ] Flyout has glass/blur appearance
- [ ] Clicking TL snaps window to top-left quadrant
- [ ] Clicking Full maximizes window
- [ ] Moving mouse away from button dismisses flyout

### Phase 3 — Fluent Context Menus
- Window header right-click: Restore, Minimize, Maximize, Close (with separators)
- Desktop right-click: View, Refresh, Save/Restore workspace, Display settings, Personalize
- Taskbar right-click: Task Manager, Save/Restore workspace, Task View
- Generic `showContextMenu()` with glass styling and scale-in animation

**Verify:**
- [ ] Right-click a window title bar → context menu appears with correct items
- [ ] Right-click desktop (not on an icon) → desktop context menu appears
- [ ] Right-click taskbar → taskbar context menu appears
- [ ] Clicking outside any context menu dismisses it
- [ ] Context menus have glass/blur styling and scale-in animation

### Phase 4 — Animations + Acrylic Texture
- `.qa-opening` animation (scale in) on new windows
- Taskbar running indicator gets accent color and wider hover glow
- Acrylic noise texture: SVG fractal noise via `::before` pseudo-element at 1.5% opacity, `mix-blend-mode: overlay`; dark theme = 2.5%; disabled in classic fidelity mode

**Verify:**
- [ ] Open a new app → window scales in with opening animation
- [ ] Acrylic texture is visible (subtle noise) on window chrome in light mode
- [ ] Dark mode acrylic texture is slightly more pronounced
- [ ] Switch to Classic fidelity (Settings) → acrylic texture disappears
- [ ] Running app dot in taskbar shows accent color

### Phase 5 — EventBus Notifier
- `setupNotifier()` creates toast container at bottom-right
- `showNotifier(text, type)` slides toasts in from right, auto-dismiss after 3.5s
- `EventBus "notify"` and `"app:NOTIFY"` events are wired to show toasts
- Exposed as `QA_OS.notifyToast()`

**Verify:**
- [ ] Trigger a save action → toast slides in from right
- [ ] Toast auto-dismisses after ~3.5s
- [ ] Multiple toasts stack without overlapping
- [ ] `QA_OS.notifyToast("Test message")` works from browser console
- [ ] An app iframe calling `window.parent.QA_OS.notifyToast("msg")` shows toast

### Phase 6 — Workspaces UI
- `showWorkspaceSaveDialog()` — modal with name input, saves via Workspaces API
- `showWorkspaceRestoreDialog()` — lists saved workspaces from IndexedDB, click to restore
- `showModalDialog()` — generic helper for future dialogs

**Verify:**
- [ ] Desktop right-click → "Save workspace" → modal appears with name input
- [ ] Enter a name, save → toast confirms save
- [ ] Desktop right-click → "Restore workspace" → list of saved workspaces appears
- [ ] Click a saved workspace → windows restore to saved positions/sizes
- [ ] Auto-save: open several windows, close browser tab, reopen → windows restore automatically

---

## Browser App — Per-Window State Fix

### Problem that was fixed
Browser tab state was stored in a single shared `localStorage` key (`qa-app-browser`). When `renderAllWindows()` was called (on drag, focus change, maximize, etc.) all iframes were destroyed and recreated — causing all browser windows to reload from the same shared key, mixing up or resetting tabs.

### Solution
Browser tab state is now stored on the window object in `compositor`/`state.windows[n].browserState`. Persists in memory across `renderAllWindows()` and persists to IndexedDB via `saveState()`.

**Changes:**
- `os-core.js`: Sends `winId` and `browserState` in `APP_BOOT` message; handles `BROWSER_STATE_CHANGED` message to update `win.browserState` and call `saveState()`
- `apps/browser.html`: Removed shared `OS.loadAppState("browser")` / `OS.saveAppState("browser")`; tracks `_winId`; boots from `msg.browserState` if present; `persist()` sends `BROWSER_STATE_CHANGED` to parent with full tab state

### Dual Browser Windows
- **Work Browser** — opens with Dynamics, ADO, AC Panel tabs pre-loaded
- **Reference Browser** — opens with Home and Guidelines tabs
- Capstone scenario now maximizes Work Browser (not a non-existent window)

**Verify:**
- [ ] Open two Browser windows → each maintains its own tabs independently
- [ ] Drag a browser window (triggers renderAllWindows) → tabs don't reset
- [ ] Close and reopen browser → tabs restore from saved state
- [ ] Work Browser opens with Dynamics/ADO/AC tabs; Reference Browser opens with Home/Guidelines
- [ ] Capstone launch → Work Browser maximizes correctly

---

## QApache / QTube Easter Eggs

Internal pages are registered in `INTERNAL_PAGES` in `apps/browser.html` (around line 307):

```javascript
var INTERNAL_PAGES = {
    "qapache": function() { return QAPACHE_PAGE; },  // Apache "It Works!" spoof
    "qtube":   function() { return QTUBE_PAGE; },    // YouTube spoof with AI video titles
};
```

Type any key in the browser address bar and hit Enter to load the page. Adding more fake sites:
```javascript
var INTERNAL_PAGES = {
    "qapache":  function() { return QAPACHE_SERVER_PAGE; },
    "qtube":    function() { return QTUBE_PAGE; },
    "qmail":    function() { return QMAIL_PAGE; },    // future: fake Gmail
    "qsearch":  function() { return QSEARCH_PAGE; },  // future: fake Google
    "qamazon":  function() { return QAMAZON_PAGE; },  // future: fake Amazon
};
```

**QApache** — Apache-style server splash: feather logo 🪶, "QApache v2.4.59", "0 vulnerabilities" humour, server info table.  
**QTube** — Dark YouTube-style UI with red accents, 8 fake AI-generated video titles, glitch effects, scanning gradient animations, "Secret unlocked" banner.

### QTube Video Implementation — Sprite Strip Animation
QTube "videos" are implemented in pure JS/CSS — no actual video files, no codecs, no ffmpeg required. Works from `file://` with zero dependencies.

**Format:** Each video is a **72×1024px vertical sprite strip** containing 8 frames stacked top-to-bottom (128px per frame: 1024 ÷ 8 = 128px).

**Playback:** CSS `background-position-y` is stepped through the strip using `setInterval` or `requestAnimationFrame` — advancing by 128px each frame — to simulate video playback on the thumbnail or player.

**Adding new "videos":** Create a 72×1024px strip image (8 frames × 128px tall each), add it to the `INTERNAL_PAGES` / QTube registry, reference it in the video card config. The JS player handles the animation automatically.

This was chosen over the original ffmpeg `.webm` approach because sprite strips are self-contained, base64-encodable, and fully file:// safe.

**Verify:**
- [ ] Open Browser app → type `qapache` in address bar → QApache page loads
- [ ] Type `qtube` → QTube loads with video grid and glitch effects
- [ ] Hover a video card → glitch effect triggers
- [ ] Typing an unknown address doesn't crash — falls through to normal (blank or error) behaviour

---

## Key Gotchas (don't re-learn these)

- **`</script>` in app HTML** breaks dist.html. `build.js` escapes it automatically — never "fix" it in source.
- **`db.js` functions unwrap IDB records** — `getSetting(key)` returns `.value` already. Don't double-unwrap.
- **`awardCertificate()` must write both** `certificateAwarded` and `certificateEarned` — admin reads the latter.
- **`activeBugs` is the canonical key** — anything referencing `bugToggles` as a settings key is a bug.
- **Build after every OS source change** — `dist.html` and capstone.html only update when `./build.sh` is run.
- **file:// + srcdoc**: apps load as srcdoc iframes. External CSS/JS is blocked. Everything must be inlined by build.js.
- **applyRole() removes DOM nodes** — any function running after it must null-check removed elements.
- **installedApps merge** — loadState() must merge APPS keys into loaded array, not overwrite it.
