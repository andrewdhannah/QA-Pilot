# QA Pilot OS — Sprint Implementation Roadmap

Based on:
- Technical Architecture Hardening Plan v1
- Product Roadmap v1 → v5
- UI/UX Enhancement Roadmap

**Core Constraint:** Everything must work from `file://` — no server, no external CDNs, no dependencies.

---

# Phase 1 — Architecture Hardening (Foundational)

## Sprint A1 — Event Bus

**Goal:** Create a centralized event orchestration layer that wraps the existing `postMessage` system without breaking any app logic.

**Why First:** Event bus enables:
- Action logging
- Replay debugging
- Cross-app coordination
- Analytics later

### Deliverables

| File | Description |
|---|---|
| `src/event-bus.js` | Standalone event bus module |

### API Surface

```js
OS.bus.emit(type, payload)     // emit event
OS.bus.on(type, handler)       // subscribe
OS.bus.off(type, handler)      // unsubscribe
OS.bus.once(type, handler)     // one-time subscription
OS.bus.getHistory()             // for debugging/replay
```

### Integration Pattern

```text
Apps (iframe)
    ↓
postMessage (existing)
    ↓
Event Bus Wrapper (NEW)
    ↓
OS handlers (existing)
```

**No breaking changes** — event bus becomes a wrapper around the existing system.

### Sprint Tasks

1. Create `src/event-bus.js` with typed events
2. Define standard event types:
   - `window.open`, `window.close`, `window.focus`
   - `tab.create`, `tab.close`, `tab.focus`
   - `app.launch`, `app.minimize`, `app.maximize`
   - `role.change`
   - `theme.change`
   - `bug.found`, `bug.logged`
   - `scenario.start`, `scenario.complete`
3. Wrap existing `postMessage` listeners in os-core.js
4. Ensure all existing app code continues working without modification

---

## Sprint A2 — Compositor Abstraction

**Goal:** Create a surface registry and rendering coordinator that wraps the existing window manager.

**Why Next:** Compositor enables:
- Snap layouts
- Smooth animations
- GPU-friendly rendering
- Virtual desktops later
- Proper z-index management

### Deliverables

| File | Description |
|---|---|
| `src/compositor.js` | Compositor layer |

### API Surface

```js
// Surface Registry
Compositor.registerSurface(winId, element)
Compositor.unregisterSurface(winId)
Compositor.getSurface(winId)
Compositor.getAllSurfaces()

// Layer Manager
Compositor.setZ(winId, z)
Compositor.raiseToTop(winId)
Compositor.sendToBack(winId)

// Focus Manager
Compositor.setFocus(winId)
Compositor.getFocusedWindow()
Compositor.clearFocus()

// Snap Engine
Compositor.getSnapZones()
Compositor.snapTo(winId, zoneId)  // "snap-left", "snap-right", "maximized"
Compositor.getSnapLayout(winId)

// Animation Scheduler
Compositor.animate(winId, property, from, to, duration)
Compositor.scheduleFrame(callback)
Compositor.flush()

// Render Coordinator
Compositor.markDirty(winId)
Compositor.render()
```

### Integration Pattern

**DO NOT replace the existing window manager.** Instead:

```text
Existing Window Management (os-core.js)
    ↓
Calls into Compositor (NEW)
    ↓
Compositor manipulates DOM
    ↓
Visual result (same as before, but now centralized)
```

### Sprint Tasks

1. Create surface registry interface (winId → element mapping)
2. Move z-index logic into compositor
3. Move focus management into compositor
4. Move snap behavior into compositor
5. Add animation scheduling hooks (for later use)
6. Ensure all existing window operations work through compositor
7. No visual changes yet — this is just abstraction

---

## Sprint A3 — Design Token System

**Goal:** Centralize all visual design values to ensure consistency across apps.

**Why Now:** Easier to do before adding more UI features.

### Deliverables

| File | Description |
|---|---|
| `tokens.css` | CSS Custom Properties for all design values |

### Token Categories

```css
/* Surface Tokens */
--surface-primary
--surface-secondary
--surface-elevated
--surface-accent
--surface-danger
--surface-success

/* Border Tokens */
--border-subtle
--border-mid
--border-strong
--border-accent
--radius-sm
--radius-md
--radius-lg
--radius-window

/* Text Tokens */
--text-primary
--text-secondary
--text-muted
--text-on-accent
--text-danger
--text-success

/* Shadow Tokens */
--shadow-subtle
--shadow-window
--shadow-focus
--shadow-menu

/* Spacing Tokens */
--spacing-xxs
--spacing-xs
--spacing-sm
--spacing-md
--spacing-lg
--spacing-xl

/* Motion Tokens */
--motion-fast
--motion-standard
--motion-slow
--motion-bounce

/* Theme-specific overrides */
html.theme-dark {
  --surface-primary: ...
}
```

### Sprint Tasks

1. Audit existing CSS for all hardcoded values
2. Create tokens.css with organized categories
3. Map old CSS values to new tokens (gradual migration)
4. Import tokens globally
5. No visual changes — values should be identical, just centralized

---

## Sprint A4 — Persistent Workspace Manager

**Goal:** Save and restore complete desktop sessions using IndexedDB (already in the project).

**Why:** Largest perceived quality upgrade for users.

**Uses existing:** IndexedDB layer from `db.js` is already bundled.

### Deliverables

| File | Description |
|---|---|
| `src/workspace-manager.js` | Workspace save/load/management |

### API Surface

```js
// Save current state
Workspace.save(name)  // saves to IndexedDB
Workspace.autoSave()  // called on state changes

// Load
Workspace.load(name)
Workspace.list()        // returns saved workspaces
Workspace.get(name)     // get full workspace data

// Delete
Workspace.delete(name)

// Import/Export
Workspace.export(name)  // returns JSON
Workspace.import(json)  // imports from JSON
```

### What a Workspace Contains

```js
{
  id: "default",
  name: "Default Workspace",
  createdAt: timestamp,
  modifiedAt: timestamp,
  
  state: {
    windows: [...],         // full window state
    activeWindowId: 3,
    nextWindowId: 10,
    nextZ: 15,
    
    role: "junior",
    theme: "light",
    background: "default",
    brightness: 100,
    fidelity: "win11",
    installedApps: [...],
    
    // Capstone/training state if active
    activeScenarioId: null,
    capstoneScenarioId: null,
    bugsFound: [],
    bugsLogged: [],
    activeBugs: [],
  }
}
```

### Integration Pattern

```text
Boot Sequence:
1. Load capstone session (existing)
2. Check for saved workspace
3. If exists and no active session → restore
4. If no workspace → boot normally

State Changes:
- Existing saveState() triggers Workspace.autoSave()
- Throttled (e.g., 500ms) to avoid IndexedDB spam
```

### Sprint Tasks

1. Create workspace data structure
2. Implement save to IndexedDB
3. Implement load from IndexedDB
4. Integrate with existing `saveState()` / `loadState()`
5. Add throttled auto-save
6. Add workspace list/delete API
7. Add JSON import/export (for debugging/backup)

---

## Sprint A5 — Action Logging (Deterministic)

**Goal:** Log all user actions for debugging, replay, and future AI evaluation.

**Why:** Unlocks:
- Training replay
- Certification evidence
- Analytics
- AI evaluation layer later

### Deliverables

| File | Description |
|---|---|
| `src/action-log.js` | Action logging system |

### Log Entry Structure

```js
{
  id: "uuid-or-sequence",
  timestamp: number,
  actor: "user",           // "user", "system", "ai"
  action: "window.open",    // verb
  target: "dynamics",       // what was affected
  previousState: {...},     // state before action
  newState: {...},          // state after action
  metadata: {...}           // additional context
}
```

### Standard Action Types

```
window: open, close, focus, minimize, maximize, move, resize, snap
tab: create, close, focus, navigate
app: launch, terminate
role: change
theme: change
bug: found, logged
scenario: start, pause, resume, complete
workspace: save, load
```

### API Surface

```js
ActionLog.log(actor, action, target, prevState, newState, meta)
ActionLog.get(sinceTime)
ActionLog.getByAction(actionType)
ActionLog.getByTarget(targetId)
ActionLog.export()
ActionLog.clear()
```

### Integration Pattern

**Initially:** Logging only, no behavior changes.

```text
Event Bus receives event
    ↓
ActionLog records entry
    ↓
Existing handler continues
```

### Sprint Tasks

1. Create action type registry
2. Create log entry structure
3. Create log storage (in memory + IndexedDB)
4. Hook into event bus (or directly into key handlers)
5. Implement query APIs
6. Implement export

---

# Phase 2 — UI & Window Manager Enhancements

## Sprint B1 — Window Resize Handles

**Goal:** Allow resizing windows by dragging edges and corners.

### What to Implement

```
┌─────────────────────◄─────────┐
│                              │
│                              ▲
│                              │
│                              │
│                              ▼
│                              │
└─────────────────────►─────────┘

     8 total resize zones:
     N, NE, E, SE, S, SW, W, NW
```

### Cursor Map

| Zone | Cursor |
|---|---|
| N/S | `ns-resize` |
| E/W | `ew-resize` |
| NE/SW | `nesw-resize` |
| NW/SE | `nwse-resize` |

### Integration

- Build on top of **Compositor** (Phase 1)
- Use existing drag code pattern from `startDrag()` in os-core.js
- Store `minWidth`, `minHeight`, `maxWidth`, `maxHeight` per window

### Sprint Tasks

1. Add resize zone detection (hit testing)
2. Add cursor styling per zone
3. Implement drag-based resize (N/S/E/W/NE/NW/SE/SW)
4. Add min/max constraints
5. Store dimensions in window state
6. Ensure compositor tracks dimensions

---

## Sprint B2 — Snap Layout Flyout (Windows 11 Style)

**Goal:** Hover over maximize button → show snap layout selector.

### Layout Options

```
Layout 1        Layout 2        Layout 3        Layout 4

┌──────┬──────┐  ┌─────────────┐  ┌──────┬──────┐  ┌──────┬─────────┐
│      │      │  │             │  │      │      │  │      │         │
│ 50%  │ 50%  │  │    100%     │  │ 33%  │ 66%  │  │ 33%  │   66%   │
│      │      │  │             │  │      │      │  │      │         │
└──────┴──────┘  └─────────────┘  └──────┴──────┘  └──────┴─────────┘

Layout 5 (Grid)

┌─────────┬─────────┐
│         │         │
│   50%   │   50%   │
│         │         │
├─────────┼─────────┤
│         │         │
│   50%   │   50%   │
│         │         │
└─────────┴─────────┘
```

### Visual Design

- Windows 11 style: pill-shaped buttons with previews inside
- Hover states
- Click to snap window to that layout zone
- Hover preview (ghost of window shows where it would go)

### Sprint Tasks

1. Design layout components in HTML/CSS
2. Add hover detection on maximize button
3. Show flyout with configurable delay
4. Implement layout previews
5. Implement snap-to-layout on click
6. Add ghost preview while hovering options
7. Integrate with Compositor.snapEngine

---

## Sprint B3 — Fluent Context Menus

**Goal:** Right-click support across the shell.

### Context Menu Locations

| Location | Menu Items |
|---|---|
| Desktop | View, Sort by, Refresh, Personalize |
| Taskbar | Toolbars, Taskbar settings, Task Manager |
| Taskbar App | Close window, Close all windows |
| Window Titlebar | Restore, Move, Size, Minimize, Maximize, Close |

### Design

- Windows 11 style: rounded corners, acrylic effect (simulated), separators
- Keyboard navigation (up/down arrows)
- Click outside to dismiss
- Disabled items for unsupported options

### Sprint Tasks

1. Create context menu component (HTML/CSS/JS)
2. Add right-click handler to desktop
3. Add right-click handler to taskbar
4. Add right-click handler to taskbar app buttons
5. Add right-click handler to window titlebars
6. Add keyboard navigation
7. Add click-outside dismissal

---

## Sprint B4 — Taskbar Animations

**Goal:** Smooth, tasteful animations for taskbar interactions.

### Animation Types

| Trigger | Animation |
|---|---|
| App launch | Icon scales up slightly, then settles |
| Hover | Background fades in, subtle elevation |
| Click | Quick scale down then up (button press feel) |
| Window open/running | Indicator dot animates in |
| Focus change | Indicator animates from one icon to next |

### Integration

- Use **Compositor.animate()** from Phase 1
- All animations CSS-based where possible
- JS orchestration for state transitions

### Sprint Tasks

1. Design CSS keyframes
2. Add hover animations
3. Add click animations
4. Add app launch animations
5. Add running indicator entry/exit animations
6. Add focus transition animations

---

## Sprint B5 — Acrylic Noise Texture

**Goal:** Add subtle noise texture to Mica/Acrylic surfaces for more authentic Fluent look.

### Approach

Since we can't load external image assets from `file://` easily:

1. **CSS noise via data URL** — generate noise canvas and convert to data URL
2. **SVG filter noise** — use SVG filters with turbulence
3. **Canvas overlay** — tiny canvas with generated noise

Recommended: **CSS repeating-linear-gradient** pattern or **SVG turbulence filter** embedded directly in CSS.

### Affected Surfaces

- Start menu
- Taskbar
- Quick settings panel
- Notification center
- Window glass effects (future)

### Sprint Tasks

1. Create noise texture generation
2. Add as CSS overlay to acrylic surfaces
3. Ensure opacity is subtle (3-8% opacity)
4. Works in dark and light themes

---

# Phase 3 — App Ecosystem Expansion

## Sprint C1 — File Explorer (Simulated)

**Goal:** Add a simulated file explorer with virtual filesystem.

### Features

- Tree-style navigation (Desktop, Documents, Downloads, Pictures)
- List view / icon view toggle
- File/folder selection
- Right-click context menus
- "Open" → launches appropriate app (or shows "not associated" message)
- Properties panel

### Virtual Filesystem Structure

```
Desktop/
  ├── Dynamics Case.lnk        // shortcut to Dynamics
  ├── Azure DevOps.lnk         // shortcut to ADO
  ├── AC Panel.lnk             // shortcut to AC
  └── Browser.lnk              // shortcut to Browser

Documents/
  ├── Case Notes/
  │   ├── Case-001.txt
  │   └── Case-002.txt
  └── Reports/
      └── QA-Analytics.pdf

Downloads/
  └── (empty initially)

Pictures/
  └── Screenshots/
      └── (empty initially)
```

### Integration

- Filesystem stored in localStorage / IndexedDB
- Shortcuts (.lnk files) call `OS.openApp()`
- Content not editable initially — this is just navigation and launch

### Sprint Tasks

1. Create `apps/file-explorer.html`
2. Design explorer UI (sidebar + main pane)
3. Implement virtual filesystem in memory
4. Implement list view
5. Implement icon view toggle
6. Add double-click to open
7. Add right-click menus
8. Register in APPS registry

---

## Sprint C2 — Outlook Mail (Simulated)

**Goal:** Add a simulated email client for training scenarios.

### Features

- Inbox with fake training emails
- Read-only initially
- Email list + preview pane
- Folder navigation (Inbox, Sent Items, Drafts)
- Search bar (non-functional or limited)
- "Reply" button shows "Feature not available in simulator"

### Fake Email Content

For QA training:

```
From: Pete, Senior Investigator
Subject: Re: Case 001 - High Priority
Date: 5 minutes ago

Andrew,

I just reviewed your bug report. The severity should be 2, not 1.
Please check AC-2.1 again.

Also, make sure the repro steps are numbered correctly.

- Pete
```

```
From: System
Subject: Case 001 Assigned
Date: 2 hours ago

You have been assigned Case 001.
Customer: Contoso Retail
Priority: High

Please investigate and update Dynamics CRM.
```

### Sprint Tasks

1. Create `apps/outlook.html`
2. Design Outlook-style UI (folder list + email list + preview)
3. Add sample training emails
4. Implement email selection
5. Implement preview pane
6. Add search UI
7. Add "Reply" / "Forward" buttons with simulator messages
8. Register in APPS registry

---

## Sprint C3 — Teams Chat (Simulated)

**Goal:** Add simulated Teams/Slack-style chat for training scenarios.

### Features

- Chat threads with supervisor / team members
- Scenario-driven messages
- "Send message" shows "Messages sent to supervisor will be reviewed"
- Message timestamps
- Read receipts / "Typing..." indicators (fake)
- User avatars (initials-based)

### Chat Participants

| User | Role |
|---|---|
| Pete | Senior Investigator (supervisor) |
| Sarah | Product Owner |
| Mike | Dev Lead |
| Alex | Junior Investigator (peer) |

### Training Scenario Messages

```
[9:42 AM] Pete: Hey Andrew, just wanted to check in on Case 001.
[9:43 AM] Pete: Found anything interesting yet?
[9:45 AM] Andrew: [user message here]
[9:46 AM] Pete is typing...
[9:47 AM] Pete: Good catch on the date field. Make sure to check AC-3.2.
```

### Sprint Tasks

1. Create `apps/teams.html`
2. Design Teams-style UI (chat list + main chat pane + message input)
3. Add fake participants
4. Add sample chat threads
5. Implement "Send" button with appropriate feedback
6. Add fake typing indicator
7. Add avatars
8. Register in APPS registry

---

## Sprint C4 — Training Content Browser (QTube+)

**Goal:** Expand QTube into a real training content browser.

### Current State

- `qapache` — Apache-style server info page
- `qtube` — YouTube clone with fake AI videos

### Expansion

- Add actual training content (static pages)
- Add lesson navigation
- Add search of documentation
- Make QTube thumbnails actually link somewhere

### New Routes

| Route | Content |
|---|---|
| `qapache` | Server info page (done) |
| `qtube` | Video browsing (done) |
| `docs/*` | Existing: qa-guidelines, etc. |
| `lessons/*` | Guided lesson content |
| `reference/*` | Reference documentation |
| `search?q=...` | Search results page |

### Sprint Tasks

1. Add lesson content placeholders
2. Add reference documentation placeholders
3. Add search UI
4. Make QTube thumbnails navigable
5. Add back/forward navigation history improvements
6. Add breadcrumbs for docs/lessons

---

# Phase 4 — Scenario Engine 2.0

## Sprint D1 — Scenario State Machines

**Goal:** Formalize scenarios as state graphs with transitions and validations.

### Current State

Scenarios are JS objects with `brief`, acceptance criteria, and bug definitions.

### New Structure

```js
{
  id: "capstone-001",
  name: "Capstone Assessment",
  
  states: [
    { id: "start", name: "Scenario Started", onEnter: "showBrief" },
    { id: "investigating", name: "Investigating Case" },
    { id: "found_bug", name: "Bug Identified" },
    { id: "logged_bug", name: "Bug Reported in ADO" },
    { id: "complete", name: "Complete" },
  ],
  
  transitions: [
    { from: "start", to: "investigating", trigger: "brief.closed" },
    { from: "investigating", to: "found_bug", trigger: "bug.found" },
    { from: "found_bug", to: "logged_bug", trigger: "bug.logged" },
    { from: "logged_bug", to: "complete", trigger: "submit.clicked", condition: "allBugsLogged" },
  ],
  
  validations: [
    { state: "logged_bug", check: "bugReport.hasSeverity", fail: "notify.missingSeverity" },
    { state: "logged_bug", check: "bugReport.hasSteps", fail: "notify.missingSteps" },
    { state: "logged_bug", check: "bugReport.hasAcRef", fail: "notify.missingAcRef" },
  ],
  
  completionRules: [
    "allRequiredBugsFound",
    "allFoundBugsLogged",
    "bugReportsMeetQualityBar",
  ],
}
```

### Integration

**Existing scenarios continue working.** State machine support is optional.

```text
Simple Scenario (old style)
    ↓
Works without modification
    ↓
No state tracking, just simple bug_found / bug_logged

State Machine Scenario (new style)
    ↓
Engine tracks state graph
    ↓
Validations run on transitions
    ↓
Guided remediation on validation failure
```

### Sprint Tasks

1. Design state machine data structure
2. Create state machine engine
3. Implement trigger matching
4. Implement condition evaluation
5. Implement validations
6. Implement completion rules
7. Ensure backward compatibility with simple scenarios
8. Update capstone scenario to use state machine (optional migration)

---

## Sprint D2 — Multi-Step Branching Scenarios

**Goal:** Support scenarios with branching logic, timed events, and conditional outcomes.

### Features

- **Conditional transitions:** "If severity=1 AND role=junior → showHint()"
- **Timed events:** "30 seconds in → sendSupervisorEmail()"
- **Multiple paths:** "If user finds bug X first vs bug Y first → different guidance"
- **Endings:** Good, Excellent, Needs Improvement based on actions

### Example Branching Logic

```js
{
  on: "bug.found",
  if: {
    "bugId === 'date-field' && role === 'junior'": {
      action: "sendNotification",
      payload: { text: "Pete: Good catch! Check the AC-3.2 requirement again." }
    },
    "bugId === 'date-field' && role === 'senior'": {
      action: "sendNotification",
      payload: { text: "Pete: Nice, you caught that. Let me know if you find anything else." }
    }
  }
}
```

### Sprint Tasks

1. Add conditional expression evaluator
2. Add timed event scheduler
3. Add notification action system
4. Add multiple path tracking
5. Add scoring based on path taken
6. Add multiple ending support

---

## Sprint D3 — Scenario Editor UI

**Goal:** Allow non-technical users to create/edit scenarios.

**Note:** Low priority until actual users request this. But architect for it.

### Features

- Visual workflow builder (state machine graph)
- Field editor (for Dynamics fields)
- Bug definition editor
- Acceptance criteria editor
- Export to JSON
- Import from JSON

### Sprint Tasks

1. Create `apps/scenario-editor.html`
2. Design UI with panels (flow, fields, bugs, AC)
3. Implement JSON import/export
4. Implement field editor
5. Implement bug editor
6. Implement AC editor
7. (Later) Visual flow builder

---

# Phase 5 — AI-Assisted Runtime (v4 Vision)

## Sprint E1 — Local AI Assistant Interface

**Goal:** Create interface for local-first AI assistance.

**Constraints:** No external API calls unless explicitly configured. Design for:
- Local models (Ollama, llama.cpp)
- RAG on local documentation
- Offline vector search

### API Design (for future)

```js
AI.ask(question)           // returns answer from local model/RAG
AI.searchDocs(query)       // vector search of docs/lessons/AC
AI.explain(bugId)          // explain a bug
AI.coach(action)           // coach on workflow
AI.evaluate(bugReport)     // evaluate bug report quality
```

### Current Implementation

Since we don't have actual local inference yet:

1. **Create the interface** — chat UI similar to Copilot
2. **Pre-packaged responses** — based on current scenario
3. **Design for future** — interface ready for actual model integration

### Sprint Tasks

1. Create `apps/ai-assistant.html`
2. Design chat UI
3. Implement pre-packaged scenario-aware responses
4. Create stub API layer ready for future integration
5. Register in APPS registry

---

## Sprint E2 — RAG / Librarian Layer

**Goal:** Create searchable documentation layer.

### Features

- Index all: docs, lessons, acceptance criteria, scenario briefs
- Simple keyword search initially
- Design for future vector embeddings
- Show results with context

### Structure

```
Search Index:
├── Documents
│   ├── QA Guidelines
│   ├── Process docs
│   └── Role guides
│
├── Lessons
│   ├── Lesson 001: Bug report basics
│   └── ...
│
└── Scenario-Specific
    ├── AC-2.1: Status field restrictions
    ├── AC-3.2: Date field validation
    └── ...
```

### Sprint Tasks

1. Create search index data structure
2. Implement keyword search
3. Implement result ranking
4. Integrate with browser search bar
5. Add search results page
6. Design for future embedding integration

---

# Phase 6 — v5: BMAD Agile Operating Environment

## Long-Term Vision (No Immediate Sprints)

These require significant investment and should only be planned after v1-v4 are solid.

### Multi-Agent Coordination

```
Agents:
├── PM Agent        — Creates user stories, prioritizes
├── QA Agent        — Finds bugs, writes reports
├── Librarian Agent — Answers questions, searches docs
├── Sprint Planner  — Token-aware planning (Flightplan)
└── Documentation Assistant
```

### Enterprise Workspace Runtime

- Shared workspaces (networked, if allowed)
- Team orchestration
- Role-based access control within simulator
- Encrypted workspace storage

### Portable AI Workspace

- Local inference bundled
- Portable embeddings
- Zero-config AI assistance

---

# Implementation Principles

## Non-Negotiable Constraints

1. **`file://` compatible** — No server, no external requests
2. **Zero dependencies** — No npm, no imports, pure JS/CSS/HTML
3. **Offline-first** — Everything works without network
4. **Backward compatible** — Don't break existing scenarios/apps
5. **Privacy-first** — No telemetry, no data leaves the page

## Additive Only

> Add systems around the working runtime rather than replacing the working runtime.

| Pattern | Description |
|---|---|
| **Wrap, don't rewrite** | Event bus wraps postMessage, doesn't replace it |
| **Abstract, don't eliminate** | Compositor wraps window management, doesn't replace it |
| **Layer on top** | New features as additional layers, not rewrites |
| **Fallback gracefully** | New code has fallbacks for old data |

## Sprint Ordering Rationale

```
Architecture (Phase 1)
    ↓
Foundation for everything else
    ↓
UI/Window Manager (Phase 2)
    ↓
Builds on compositor/event bus
    ↓
App Ecosystem (Phase 3)
    ↓
Builds on all previous layers
    ↓
Scenario Engine (Phase 4)
    ↓
Builds on event bus, action log
    ↓
AI Features (Phase 5)
    ↓
Builds on RAG/librarian layer
```

---

# Quick Reference: Sprint Summary

| Sprint | Name | Files | Depends On |
|---|---|---|---|
| A1 | Event Bus | `src/event-bus.js` | None |
| A2 | Compositor | `src/compositor.js` | A1 (optional) |
| A3 | Design Tokens | `tokens.css` | None |
| A4 | Workspace Manager | `src/workspace-manager.js` | None |
| A5 | Action Log | `src/action-log.js` | A1 |
| B1 | Resize Handles | os-core.js changes | A2 |
| B2 | Snap Layout Flyout | New component + os-core.js | A2 |
| B3 | Context Menus | New component + os-core.js | A1 (events) |
| B4 | Taskbar Animations | CSS + os-core.js | A2 |
| B5 | Acrylic Noise | CSS | None |
| C1 | File Explorer | `apps/file-explorer.html` | A1 (events), B3 (menus) |
| C2 | Outlook | `apps/outlook.html` | A1 (events) |
| C3 | Teams Chat | `apps/teams.html` | A1 (events) |
| C4 | Training Content Browser | browser.html updates | None |
| D1 | Scenario State Machines | scenarios + engine | A1 (events), A5 (log) |
| D2 | Branching Scenarios | scenario engine updates | D1 |
| D3 | Scenario Editor | `apps/scenario-editor.html` | D1 |
| E1 | AI Assistant Interface | `apps/ai-assistant.html` | E2 (RAG) later |
| E2 | RAG/Librarian | search index + engine | None |

---

*Last Updated: May 2026*
