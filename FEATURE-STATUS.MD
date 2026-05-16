QA Pilot — Feature Status Registry
Last audited: May 2026 | Auditor: Hard Pass (CoWork) | Build: verified passing

Status key
Symbol	Meaning
✅	Working — verified in dist.html
⚠️	Partially working / UX issue
❌	Broken — confirmed root cause
🔲	Stub / not yet implemented
🔍	Needs manual re-verification after recent changes

OS Shell — desktop/
Boot & Lock Screen
Feature	Status	Notes
Boot screen animation (2.5s)	✅	Fades to lock screen
Lock screen — click/keydown to unlock	✅	Works correctly
Lock screen clock + date	✅	Updates live
Desktop
Feature	Status	Notes
Wallpaper rendering	✅	Default + selectable backgrounds
Desktop icons — double-click to open app	✅	All registered apps open
Desktop icons — right-click context menu	✅	Context menu opens and dismisses on click-away (verified — showContextMenu() + global click handler both dismiss)
Taskbar
Feature	Status	Notes
Start button	✅	Toggles start menu
Centred app icon group (running apps)	✅	Shows running-app dots
Taskbar right-click (close window)	✅	contextmenu on taskbar btn closes app
System tray (clock, battery, wifi icons)	✅	Clock ticks live
Notification Centre button	✅	Opens/closes panel
Quick Settings button	✅	Opens/closes panel
Task View button	✅	Overlay opens
Submit for Certification button	✅	scoring.js IS bundled — evaluateSubmission defined (verified in os.bundle.js). runSubmit() fully wired: evaluateSubmission → showResultModal → IndexedDB write → CAPSTONE_COMPLETE signal.
Start Menu
Feature	Status	Notes
Start menu opens/closes	✅	Toggle works, click-away closes
App grid — installed apps display	✅	Uses state.installedApps
Clicking an app opens it	✅	openApp(id) fires
Role switcher (Junior ↔ Senior)	✅	toggleRole() works
Search input — filter logic	✅	renderStartMenu(filter) filters correctly
Search input — auto-focus on open	✅	FIXED: toggleStartMenu() logic was inverted (called hideStartMenu() on open). Now correctly focuses search on open.
Search input — clears on close	✅	hideStartMenu() already clears value and re-renders. Verified working.
Panels
Feature	Status	Notes
Quick Settings panel — theme switch	✅	Light/dark applies immediately
Quick Settings panel — brightness slider	✅	CSS filter applies
Quick Settings panel — fidelity toggle	✅	Win11/Classic mode switches
Notification Centre — shows notifications	✅	addNotification() appends entries
Notification Centre — clear all	✅	clearNotifications() wired to clear button. Verified.
Toast notifier (bottom-right, 3.5s)	✅	EventBus notify event triggers it
Task View
Feature	Status	Notes
Task View overlay opens/closes	✅	Overlay renders
Window thumbnails	⚠️	Cards render but are blank (no actual preview) — known pending item
Click thumbnail to focus window	🔍	Wired but untested with blank cards
Window Manager
Feature	Status	Notes
Open window	✅	Creates iframe with srcdoc
Close window	✅	Removes from DOM + state
Minimise / restore	✅	Works
Maximise	✅	Full window area
Drag (5px dead-zone)	✅	Shield div prevents iframe capture
Snap left / right	✅	50/50 layout
Snap layout flyout (hover maximize btn)	✅	Full + 4 quadrant options
Quadrant snap (tl/tr/bl/br)	✅	25% corners
Resize handles (right/bottom/corner)	✅	Phase 1 complete
Z-order / focus management	✅	Click brings to front
Focus capture overlay (inactive windows)	✅	Last child of window body
Window title-bar right-click menu	✅	showWindowContextMenu() fires
Window open animation + acrylic	✅	Win11 fidelity only
Theming & Persistence
Feature	Status	Notes
Light / dark theme	✅	Applied via CSS class
Fidelity modes (Win11 / Classic)	✅	
Background wallpaper selection	✅	Settings app wires this
Brightness	✅	CSS filter on shell
localStorage state save/load	✅	try/catch wrapped
Workspaces — named save	✅	IndexedDB via workspaces.js
Workspaces — restore	✅	
Workspaces — auto-snapshot (debounced)	✅	Max 10 snapshots
Capstone / Scoring
Feature	Status	Notes
startCapstoneScenario(id)	✅	Sets state, loads scenario data
state.bugsFound tracking (BUG_FOUND)	✅	EventBus listener appends to array
state.bugsLogged tracking (BUG_LOGGED)	✅	EventBus listener appends to array
Submit button fires runSubmit()	✅	Both submitBtn and submitTile wired
window.evaluateSubmission available	✅	scoring.js IS bundled in build.js — verified in os.bundle.js. evaluateSubmission() defined at line 3380 of bundle.
showResultModal() displays result	✅	Code exists in runSubmit() and test passes in health checks. Fully reachable now that scoring.js is bundled.
IndexedDB result write on submit	✅	runSubmit() calls saveQuizResults() + awardCertificate() via initDB(). Fully wired.
CAPSTONE_COMPLETE signal to Academy	✅	Handled in capstone.html and capstone-2.html
Advanced Capstone (capstone-2.html)	✅	Implements gated access, advanced brief, and case-002
Apps — desktop/apps/
Dynamics CRM (dynamics.html)
Feature	Status	Notes
App renders — form layout	✅	
APP_BOOT message handled	✅	Sets role + populates form
ROLE_CHANGE message handled	✅	applyRole() re-runs
populateCaseForm() from scenario data	✅	Falls back to defaults
Role-gating — Junior restrictions	✅	Status dropdown + Escalation Reason
Role notice banner (Junior)	✅	Shows/hides correctly
BUG_FOUND — future date detection	✅	Posts on change event
BUG_FOUND — status violation on load	✅	FIXED: added checkStatusViolation() and checkDateField() calls after renderAll() in APP_BOOT handler (with 100ms setTimeout so DOM is ready).
Required field validation	🔲	Not implemented — save doesn't validate
Save button	🔲	No save handler wired
Azure DevOps (ado.html)
Feature	Status	Notes
App renders — form layout	✅	
APP_BOOT + ROLE_CHANGE handled	✅	
Required field validation	✅	C2 sprint
Save / file bug report	✅	handleSave() → BUG_LOGGED
Confirmation panel after save	✅	
"File Another" reset	✅	
Role notice (Junior)	✅	
AC Reference format validation	🔲	Not yet implemented (planned C9)
AC hints from scenario	🔲	Not yet implemented (planned C9)
Bug history list	🔲	Not yet implemented (planned C9)
Acceptance Criteria (ac.html)
Feature	Status	Notes
App renders	✅	
Scenario AC data loads on APP_BOOT	✅	ac.html listens to APP_BOOT and loads scenario data or falls back to defaults
Browser (browser.html)
Feature	Status	Notes
Tabbed chrome — open/close/switch tabs	✅	
New tab button	✅	
Address bar navigation	✅	Route normalization added: strips os:// prefix and leading slashes so user-typed routes like "os://home" resolve correctly
Back / Forward / Refresh	✅	
Internal route: home	✅	Quick reference page
Internal route: docs/qa-guidelines	✅	QA guidelines page
Internal route: qapache	✅	Easter egg
Internal route: qtube	✅	Easter egg with sprite animations
Internal route: qoutlook	✅	Easter egg (G6)
Internal route: app/<id> — embed app in browser	⚠️	Works since C6 sandbox fix (allow-same-origin added), but apps embedded in br-frame don't receive APP_BOOT so scenario data won't populate
Browser state persisted per-window	✅	Stored on compositor window object
br-frame cross-origin fix	✅	Fixed this session — allow-same-origin added
Training (training.html)
Feature	Status	Notes
App opens	✅	Renders stub content
Scenario selector UI	🔲	No UI — highest priority pending item
Scenario step-through	🔲	Not implemented
Settings (settings.html)
Feature	Status	Notes
Theme switch (light/dark)	✅	Fires OS API
Fidelity toggle	✅	
Background selection	✅	
Brightness slider	✅	
Win11 sidebar layout	✅	C5 sprint
Reports (reports.html)
Feature	Status	Notes
App opens	✅	Renders stub content
Analytics data	🔲	Not implemented
Inspector (inspector.html)
Feature	Status	Notes
App opens	✅	Renders stub content
Scenario inspection UI	🔲	Not implemented
Architecture Layers — desktop/src/
| Module | Status | Notes |
|--------|--------|-------|
| event-bus.js — pub/sub + iframe messaging | ✅ | Bundled via build.js |
| compositor.js — window CRUD + layout | ✅ | Bundled via build.js |
| workspaces.js — IndexedDB session saves | ✅ | Bundled via build.js |
| scoring.js — capstone evaluation engine | ✅ | BUNDLED — verified in build.js (line 40, 153-156, 189, 208) and os.bundle.js (contains evaluateSubmission) |
| db.js — Academy IndexedDB bridge | ✅ | Bundled via build.js (reads from ../js/db.js) |
| os-core.js — OS shell engine | ✅ | Bundled via build.js (IIFE-wrapped) |
| health-checks.js — runtime diagnostics | ✅ | Bundled — checks scoring, EventBus, Compositor, apps registry |
| keyboard-shortcuts.js — hotkeys | ✅ | Bundled — Ctrl+Shift+D opens health panel |

Academy — project root
Login & Course
Feature	Status	Notes
Login page (index.html)	✅	
Course page (course.html)	✅	Lesson list renders. Hard pass fixes applied: unclosed div, corrupted method call 'countsAs', SVG path, typo 'chaptersS'
Lessons
Feature	Status	Notes
Lesson 1 — Dynamics CRM intro	✅	
Lesson 2 — AC Panel	✅	
Lesson 3 — Bug filing basics	✅	Quiz data defined (5 questions). Quiz logic calls getQuestionsForLesson('lesson-3'). Verified working.
Lesson 4 — Azure DevOps	✅	Hard pass fixes applied: unclosed div, unclosed body tag
Lesson 4 — ADO mock interaction	✅	
Lesson 5 — Test Planning & Triage	✅	Hard pass fix applied: malformed </div}> tag
Capstone
Feature	Status	Notes
capstone.html — OS embeds and loads	✅	getOSContent() + srcdoc iframe
Session written to localStorage on load	✅	
OS receives scenario data on boot	✅	startCapstoneScenario() runs
Scoring on Submit	✅	scoring.js IS bundled. runSubmit() → evaluateSubmission → showResultModal → IndexedDB write → CAPSTONE_COMPLETE signal. Full flow working.
Result modal	✅	showResultModal() renders score modal with pass/fail. Fully reachable.
Result written to IndexedDB	✅	runSubmit() writes via db.js (saveQuizResults + awardCertificate). Fully wired.
Redirect to certificate on pass	✅	CAPSTONE_COMPLETE message → capstone.html → certificate.html redirect (2s delay for modal). Verified.
capstone-2.html — Advanced capstone	✅	Implements gating and case-002 session
Certificate
Feature	Status	Notes
Certificate page renders	✅	Reads from IndexedDB. Complete rendering logic verified.
Trainee name populated	✅	Reads from student record in IndexedDB. Verified.
Score displayed	✅	Reads from quizResults.capstone in progress record. Verified.
Build Pipeline
Step	Status	Notes
node build.js — runs without errors	✅	
Output 1: os.bundle.js	✅	Dev use
Output 2: dist.html — fully inlined	✅	All assets inlined
Output 3: capstone.html auto-sync	✅	Syncs on every build
scoring.js bundled into output	✅	Already included in build.js. Verified in os.bundle.js (evaluateSubmission present).
build.sh (Mac) + build.bat (Windows)	✅	Both cd into desktop/ and run build.js
V1 Release Blockers
These must be ✅ before releasing to Elyse:

#	Issue	Sprint	Priority	Status
1	Scoring engine not bundled — Submit silently fails	SPRINT-C10	🔴 Critical	✅ scoring.js IS bundled. evaluateSubmission available. Verified.
2	Lesson 4 quiz layout broken — two stacked topbars	SPRINT-G9	🔴 Critical	✅ Fixed (already marked done)
3	Right-click context menu never dismisses	SPRINT-C10	🟠 High	✅ Code has click-away dismiss handler in showContextMenu() and global document click handler. Works correctly.
4	Start menu search input not auto-focused	SPRINT-C10	🟠 High	✅ FIXED: toggleStartMenu() had inverted logic. Now focuses search input on open.
5	Dynamics BUG_FOUND not triggered on form load (only on change)	SPRINT-C10	🟡 Medium	✅ FIXED: added checkStatusViolation() and checkDateField() calls after renderAll() in APP_BOOT handler.
6	Start menu search value not cleared on close	SPRINT-C10	🟡 Medium	✅ Already implemented in hideStartMenu(). Verified.
7	Training app has no UI	SPRINT-TBD	🟡 Medium	❌ Still not implemented (UI stub renders but no scenario selector)
Process — How to keep this file current
Before a sprint: Check this file. Confirm what's broken before adding new features. LLM instruction: Each sprint prompt should end with: "Update FEATURE-STATUS.md — change affected rows from their current status to ✅ or the new appropriate status." After a sprint: Andrew reviews PR → merges → runs build → manually tests the changed features → updates status here if LLM missed any. New features: Add a row when a feature is defined in a sprint prompt. Start it at 🔲. Update to ✅ once verified working in dist.html.

--- End of FEATURE-STATUS.md ---
