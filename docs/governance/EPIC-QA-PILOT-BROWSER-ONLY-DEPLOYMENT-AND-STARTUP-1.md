# EPIC-QA-PILOT-BROWSER-ONLY-DEPLOYMENT-AND-STARTUP-1

**Status:** active
**Owner:** Andrew Hannah
**Authorization:** Owner explicit authorization 2026-07-08

## Purpose

Define the browser-only startup and deployment contract for QA Pilot before any implementation begins. QA Pilot must run from static hosting with no install, no backend, no server database, no required network after initial load.

## Sprint Sequence

| # | Sprint | Purpose |
|---|--------|---------|
| 1 | QA-PILOT-BROWSER-ONLY-STARTUP-AND-DEPLOYMENT-CONTRACT-1 | Define startup/deployment contract |
| 2 | QA-PILOT-BROWSER-SPLASH-AND-STARTUP-FLOW-1 | Splash screen and startup flow |
| 3 | QA-PILOT-ADMIN-TEAM-PACKAGE-BUILDER-1 | Admin team deployment JSON builder |
| 4 | QA-PILOT-LEARNER-LOCAL-IDENTITY-IMPORT-1 | Learner identity/import flow |
| 5 | QA-PILOT-BROWSER-COURSE-RUNTIME-1 | Course runtime delivery |
| 6 | QA-PILOT-LOCAL-PROGRESS-TRACKING-1 | Local progress tracking |
| 7 | QA-PILOT-LEARNER-RESULT-EXPORT-1 | Learner result JSON export |
| 8 | QA-PILOT-ADMIN-RESULT-IMPORT-1 | Admin result JSON import |
| 9 | QA-PILOT-BROWSER-ONLY-OPERATIONAL-BASELINE-1 | Operational baseline |

## Authority Boundaries

- No server authentication, backend database, installed software, cloud account dependency
- No cross-project write, Librarian mutation, authority expansion
- No autonomous publication
- Import/export JSON is the team handoff mechanism only
- Local user selection is not security authentication
