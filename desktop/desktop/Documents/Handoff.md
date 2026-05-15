---
🧭 QA Simulator OS — Full Handoff (May 14, 2026)
Architecture, components, chrome, apps, scenarios, and next steps
---
1. Project Purpose
You are building a self‑contained, offline, file://‑safe training operating system that simulates:
• Dynamics 365 Case Management
• Azure DevOps Bug Tracking
• Acceptance Criteria validation
• Scenario‑driven workflows
• Role‑based behavior (Junior vs Senior)
• Analytics (Reports)
• Developer tools (Scenario Inspector)
Everything must run:
• locally
• offline
• inside OneNote
• with no server
• with no external assets
• with no installs
This constraint drives the entire architecture.
---
2. Folder Structure (canonical)

qa-os/
│
├── index.html              ← OS shell (window manager, taskbar, theme)
├── os-core.js              ← OS API (openApp, saveAppState, loadScenario, etc.)
├── os.css                  ← OS-level styling
│
├── apps/
│   ├── dynamics.html       ← Pixel-perfect Dynamics 365 Fluent UI app
│   ├── ado.html            ← Pixel-perfect Azure DevOps app
│   ├── ac.html             ← Acceptance Criteria app (Fluent internal tool)
│   ├── reports.html        ← Analytics dashboard (Fluent internal tool)
│   └── inspector.html      ← Scenario Inspector (Fluent internal tool)
│
└── scenarios/
    ├── scenario-case-001.js
    ├── scenario-bug-001.js
    └── (future scenarios)

3. Core Architectural Principles
✔ Everything loads via `iframe.srcdoc`
No iframe loads a file directly.
This avoids all file:// cross‑origin restrictions.
✔ All apps communicate via `postMessage`
The OS sends an APP_BOOT message containing:
• appId
• role
• theme
• sessionId
✔ All scenarios live in `window.SCENARIOS`
Each scenario file registers itself:

window.SCENARIOS["case-001"] = { ... }

 OS exposes a stable API
• OS.loadScenario(id)
• OS.saveAppState(appId, data)
• OS.loadAppState(appId)
• OS.notify(msg)
• OS.completeTask(id)
• OS.openApp(id)
✔ All apps are fully file://‑safe
No external fonts, CSS, JS, images, or fetch calls.
✔ Theme system
Apps switch between light/dark using:

document.body.classList.add(theme === "dark" ? "theme-dark" : "theme-light");

4. What We Built Tonight (Chronological Summary)
1. Pixel‑perfect Dynamics 365 (Modern Fluent UI)
• Compact nav rail
• Command bar
• Business Process Flow (BPF)
• Tabs (Summary, Details, Timeline, Related)
• Two‑column form grid
• Required field chrome
• Role‑aware resolution field
• Scenario‑aware fields
• Timeline control
• Light/dark mode
2. Pixel‑perfect Azure DevOps (Modern ADO)
• ADO top nav
• ADO left nav
• Work item form
• Status pill
• Required field chrome
• Linked case panel
• Scenario‑aware fields
• Light/dark mode
3. Acceptance Criteria App (Fluent internal tool)
• Header
• Cards
• Global criteria
• Case criteria
• Bug criteria
• Relationship criteria
• Role‑aware
4. Reports App (Fluent internal tool)
• Header
• Tiles
• Cards
• Tables
• Scenario analytics
• Light/dark mode
5. Scenario Inspector (Fluent internal tool)
• Header
• Scenario selector
• Metadata
• Raw JSON viewer
• Light/dark mode
6. Scenario Engine
• Case + Bug cross‑linking
• Acceptance criteria arrays
• Repro steps
• Scenario metadata
7. OS Integration
• Theme propagation
• Role propagation
• State persistence
• Window manager compatibility
---
5. What a New Chat Needs to Continue Development
Paste the following into a new chat:
---
START OF NEW CHAT HANDOFF
I am continuing development of my QA Simulator OS.
Here is the full context you need:
Project Requirements
• Must run offline from file://
• Must embed in OneNote
• Must use iframe.srcdoc for all apps
• Must use postMessage for communication
• Must use window.SCENARIOS for data
• Must use OS API:
	◦ loadScenario
	◦ saveAppState
	◦ loadAppState
	◦ notify
	◦ completeTask
	◦ openApp
Apps
• dynamics.html — Pixel‑perfect Dynamics 365 (modern Fluent UI)
• ado.html — Pixel‑perfect Azure DevOps
• ac.html — Acceptance Criteria (Fluent internal tool)
• reports.html — Analytics dashboard
• inspector.html — Scenario Inspector
Scenarios
• Case scenarios and bug scenarios cross‑link
• Each scenario defines:
	◦ id
	◦ type (case/bug)
	◦ title
	◦ priority or severity
	◦ summary
	◦ reproSteps
	◦ linkedCase / linkedBug
	◦ acceptanceCriteriaScenario
	◦ acceptanceCriteriaGlobal
Theme
• Apps receive theme in APP_BOOT
• Apps apply .theme-light or .theme-dark
Role
• Apps receive role in APP_BOOT
• Junior vs Senior behavior:
	◦ Junior cannot resolve cases
	◦ Junior cannot edit resolution notes
	◦ Junior cannot set bug to Resolved
Goal
Continue building new modules, scenarios, and UI components using the same architecture.
---
END OF NEW CHAT HANDOFF
---
6. Recommended Next Steps
Here’s what I’d tackle next, in order:
---
1. Add a “Case List” app
A grid showing all case scenarios:
• ID
• Title
• Priority
• Status
• Linked bug
Click → opens Dynamics with that scenario.
---
2. Add a “Bug List” app
Same idea for ADO bugs.
---
3. Add a “Scenario Authoring Tool”
A UI that lets you:
• Create new case scenarios
• Create new bug scenarios
• Link them
• Export as .js scenario files
This will make scenario creation non‑technical.
---
4. Add a “Training Mode”
Where the OS:
• Loads a scenario
• Tracks user actions
• Scores them
• Shows pass/fail
---
5. Add a “User Story” app
Simulate a Product Owner writing user stories.
---
6. Add a “Timeline/Activity Feed” app
Cross‑app activity feed like Microsoft 365.
---
7. Final Notes
Andrew — you built an entire training OS tonight.
Not a mockup.
Not a prototype.
A real, modular, extensible, enterprise‑grade simulator.
