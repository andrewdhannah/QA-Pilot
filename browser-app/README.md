# QA Pilot

A fully offline QA onboarding training platform — bilingual (EN/FR), multi-course, and zero-dependency. Trainees log in, work through structured courses, and then practise inside a realistic Windows 11-style desktop simulator. No server, no install, no internet required. Open `index.html` from `file://` and go.

---

## Why

Traditional QA training relies on live sandbox environments that require setup, credentials, and connectivity. This doesn't work for:

- **Remote / offline learners** — no stable internet, no access to corporate VPN
- **OneNote / SharePoint distribution** — materials need to be self-contained
- **Bilingual teams** — content must work in both English and Québec French
- **Quick onboarding** — trainers need zero setup time
- **Realistic practice** — trainees need to feel like they're using the real tools

QA Pilot solves this by running entirely in the browser from local files. Trainees log in, complete lessons with quizzes, and then work inside a simulated desktop with realistic versions of Dynamics 365, Azure DevOps, Teams, and other tools — all driven by scripted scenarios with intentional bugs to find.

---

## What's inside

```
QA Pilot/
├── index.html                  Student login (entry point)
├── portal.html                 Course catalog — My Learning + Available Courses
├── course-view.html            Multi-course lesson viewer (sidebar, quizzes, progress)
├── course.html                 Legacy QA Onboarding course page (still active)
├── capstone.html               Capstone assessment (redirects to QASimulator.html?mode=capstone)
├── capstone-2.html             Advanced capstone
├── certificate.html            Certificate of completion
├── QASimulator.html            Desktop OS simulator (main build output)
│
├── admin/
│   ├── index.html              Admin login
│   ├── dashboard.html          Student management and progress overview
│   ├── bugs.html               Bug Lab — toggle intentional defects for training
│   ├── editor.html             Global content editor (role names, email templates)
│   └── assign.html             Manual path assignment per student
│
├── css/
│   ├── main.css                Design tokens, base layout, shared components
│   ├── dynamics-mock.css       Dynamics 365 UI chrome
│   └── ado-mock.css            Azure DevOps UI chrome
│
├── js/
│   ├── db.js                   IndexedDB gateway — only file that touches the DB
│   ├── app.js                  Global utilities and session guards
│   ├── i18n.js                 Bilingual engine — __() translation function
│   ├── lang-en.js              English string dictionary
│   └── lang-fr.js              French string dictionary (Québec French)
│
├── data/
│   ├── content.js              Single source of truth — all course definitions,
│   │                           lesson content, and quiz questions
│   └── bug-keys.js             Centralized bug key constants
│
├── QA Pilot Docs/              Documentation (moved from docs/ in V1.5)
│   ├── PULSE/                  Programmatic Update & Logic Status Engine
│   │   └── feature-status.md   Verified feature states
│   ├── Session Handoffs/       Structured Project Information & Navigation Engine
│   │   ├── SESSION-HANDOFF.md  Session summary and planning
│   │   └── SESSION-HEARTBEAT.json  Machine-readable session state
│   ├── CORTEX/                 Comprehensive Object Registry for Technical Execution
│   ├── VITAL/                  Verified Integrated Traceability & Alignment Layer
│   └── Design/                 Design documents and sprint plans
│
├── chrome-extension/           FlightPlan prompt helper for AI-assisted development
│
└── desktop/                    QA Pilot Desktop OS (development templates)
    ├── index.html              Dev entry point (loads os.bundle.js)
    ├── os.css                  All OS styles — Win11 tokens, window chrome, taskbar
    ├── build.js                Build tool → os.bundle.js + QASimulator.html
    ├── src/
    │   ├── os-core.js          OS engine — state, window manager, drag/snap, roles
    │   ├── compositor.js       Rendering and layout compositor
    │   ├── workspaces.js       Virtual desktop / workspace manager
    │   ├── event-bus.js        Cross-module event system
    │   ├── keyboard-shortcuts.js  Win key, Alt+Tab, and other shortcuts
    │   ├── health-checks.js    OS self-diagnostics
    │   └── scoring.js          Scenario scoring engine
    ├── apps/
    │   ├── dynamics.html       Dynamics 365 CRM case simulator
    │   ├── ado.html            Azure DevOps bug report simulator
    │   ├── teams.html          Microsoft Teams channel simulator
    │   ├── browser.html        Training browser with documentation
    │   ├── qoutlook.html       Outlook email simulator
    │   ├── qtube.html          QTube — training video player
    │   ├── qapache.html        QApache — internal portal simulator
    │   ├── reports.html        Analytics and results dashboard
    │   ├── inspector.html      QA Inspector tool
    │   ├── ac.html             Acceptance Criteria reference panel
    │   ├── training.html       Task list and scenario launcher
    │   └── settings.html       Theme, wallpaper, fidelity, role switcher
    └── scenarios/              Scenario data (case state, expected bugs, AC refs)
```

---

## How it works

### Three layers

| Layer | What it does |
|-------|-------------|
| **Academy** | `index.html` → `portal.html` → `course-view.html`. Login, multi-course enrollment, sequential module/quiz flow, progress tracking, certificate. Backed by IndexedDB. |
| **Desktop OS** | A Windows 11-style desktop embedded in the capstone. Boot screen, lock screen, taskbar, start menu, draggable/snappable windows. Junior/Senior role system controls field-level access. |
| **Apps** | Simulated work tools loaded as `srcdoc` iframes inside the OS. Communicate with the OS engine via `window.parent.QA_OS`. |

### Multi-course architecture

Courses are defined in `data/content.js` under `COURSE_DEFINITIONS`. Each course has modules, sub-modules, and per-module quiz questions — all in one file. Adding a new course means adding entries to that object; no new pages required.

Current courses:
- **QA Onboarding** — 6 modules, testing fundamentals through capstone
- **Agile & Scrum for Developers** — 9 modules, 35 sub-modules, 96 quiz questions
- **QA Onboarding — Advanced** — 3 modules, 9 sub-modules, 2 quizzes, 1 capstone
- **Capstone 2** — 1 module, Advanced Capstone Assessment exercise

### Bilingual support (EN/FR)

A language toggle appears in the topbar of every course page. The `__('key')` function pulls strings from `js/lang-en.js` or `js/lang-fr.js` based on the saved preference. Course content has a separate French content layer in `data/content.js`. Switching language reloads the page — clean, no DOM patching.

### Data flow

- **Student accounts, progress, quiz results, and settings** are stored in IndexedDB via `js/db.js` — the only file that opens the database
- **Passwords** are hashed with PBKDF2 (SHA-256, 100K iterations, random salt) via the Web Crypto API — never stored as plaintext
- **OS state** (open windows, positions, theme) persisted to `localStorage`
- **Scenario data** defines CRM state, expected bugs, and AC references that drive each capstone exercise

---

## Quick start

### Prerequisites
- A modern browser (Chrome or Edge recommended; Firefox and Safari 15+ supported)
- [Node.js](https://nodejs.org/) 16+ — only needed if rebuilding the desktop OS

### Run the Academy

```bash
# No build step needed
open index.html
```

Default admin password: `QAAdmin2026` — change it in the Admin dashboard after first login.

### Run the Desktop OS standalone

```bash
open QASimulator.html
```

### Rebuild the Desktop OS

```bash
node build.js
```

Produces:
- `os.bundle.js` — dev bundle (loaded by `desktop/index.html`)
- `QASimulator.html` — fully self-contained single-file build, no external references

---

## Security notes

- **Passwords are PBKDF2-hashed** at rest (SHA-256, 100K iterations, 16-byte random salt). Plaintext is never stored or logged.
- **No network requests** — the platform is fully offline. No data ever leaves the browser.
- **IndexedDB** is scoped per-origin. When running from `file://`, data is local to the file path.
- **Admin access** is gated by a hashed password in IndexedDB settings.

---

## Built with

- [Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API) — PBKDF2 password hashing
- [IndexedDB](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API) — student records, progress, settings
- Vanilla JavaScript, HTML, CSS — no frameworks, no build dependencies for the Academy
- Visual design inspired by [Windows 11 Desktop Simulator](https://github.com/username/windows-11-desktop-simulator) (MIT licence)
- Includes QASimulator.ico for application icon (generated from favicon.svg)

---

## License

MIT — see [LICENSE](./LICENSE).
