# Changelog
## QA Simulator Desktop — Modular OS v4

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### In Progress
- Capstone assessment integration (scoring engine + certificate flow)
- Scenario data layer: `capstone-001` with crmState, expectedBugs, acRefs
- Submit for Certification button in taskbar
- Role broadcast to all open app iframes on toggle

---

## [0.4.0] — 2026-05-13

### Added
- Modular OS v4 architecture — full rebuild from multi-file to single-file srcdoc model
- `build.js` build system — produces `os.bundle.js` (dev) and `dist.html` (distribution)
- `window.SCENARIOS` registry pattern for scenario data isolation
- `scenarios/scenarios-case-001.js` and `scenarios/scenarios-bug-001.js`
- Acceptance Criteria (AC) panel app
- Settings app with theme, wallpaper, fidelity mode, and role switcher
- Lock screen with live clock
- Task view overlay
- Notification centre
- Snap layout support (left / right / maximise)
- Junior / Senior role system — controls field visibility inside Dynamics

### Fixed
- `window.SCENARIOS` initialization guard added to `build.js` `readScenarios()`
  — scenario files previously crashed the runtime if the registry object was
  not initialized before the first property assignment
- Lock screen click and taskbar clock now initialize correctly after the above fix

### Changed
- App iframes now use `srcdoc` instead of `src` — eliminates file:// cross-origin
  restrictions, making the build fully portable
- `APP_BOOT` postMessage standardized across all app iframes

---

## [0.3.0] — 2026-05-01

### Added
- Multi-file OS architecture (pre-modular iteration)
- Dynamics CRM mock app with role-based field visibility
- Azure DevOps (ADO) mock app with bug report form
- postMessage communication layer between apps and OS shell

---

## [0.2.0] — 2026-04

### Added
- Single-file OS prototype
- Basic window management (drag, z-index)
- Taskbar with centred icons
- Win11-style start menu

---

## [0.1.0] — 2026-03

### Added
- Initial concept — Windows 11 desktop shell in HTML/CSS/JS
- Visual design based on Windows 11 Desktop Simulator (MIT)
