# QA Pilot Browser-Only Team Workflow — Operational Baseline

**Epic:** EPIC-QA-PILOT-BROWSER-ONLY-DEPLOYMENT-AND-STARTUP-1
**Sprint:** QA-PILOT-BROWSER-ONLY-OPERATIONAL-BASELINE-1
**Status:** complete_pending_owner_review

## Completed System

| Sprint | Page | Purpose |
|--------|------|---------|
| 2 | `index.html` | Splash/startup — 4 modes (solo, returning, import, admin) |
| 3 | `admin.html` | Admin workspace — workspace, members, packages, deploy |
| 4 | `identity.html` | Learner identity selection from deployment roster |
| 5 | `catalog.html` | Training catalog — in-progress and completed packages |
| 5 | `course-view.html` | Course runtime — sections, progress, completion |
| 6 | `course-view.html` | (integrated) Progress tracking — auto-save, resume, completion |
| 7 | `export.html` | Learner result JSON export |
| 8 | `import.html` | Admin result JSON import with dashboard |

## All Files

| File | Size | Purpose |
|------|------|---------|
| `docs/schemas/browser-assets/index.html` | 10.8KB | Splash screen and startup mode selection |
| `docs/schemas/browser-assets/admin.html` | 10.2KB | Admin workspace and deployment generator |
| `docs/schemas/browser-assets/identity.html` | 3.8KB | Learner identity selection |
| `docs/schemas/browser-assets/catalog.html` | 4.2KB | Training catalog listing |
| `docs/schemas/browser-assets/course-view.html` | 7.5KB | Course runtime with progress tracking |
| `docs/schemas/browser-assets/export.html` | 4.5KB | Learner result export |
| `docs/schemas/browser-assets/import.html` | 4.8KB | Admin result import |

## Team Workflow

```
Admin creates workspace + members + assigns packages → deploys deployment JSON
        ↓
Learner opens index.html → imports deployment JSON → selects identity
        ↓
Learner views assigned packages in catalog → completes training in course-view
        ↓
Progress auto-saves to localStorage (resume-capable across sessions)
        ↓
Learner exports result JSON from export.html
        ↓
Admin imports result JSON into import.html → completion dashboard
        ↓
Trainer/Owner reviews results — no auto-approval
```

## Hard Boundaries

| Boundary | Enforced |
|----------|----------|
| Static browser only — no backend | ✅ All files standalone HTML |
| No server authentication | ✅ No password fields, no login API |
| No install required | ✅ Open in browser from static hosting |
| Browser storage only | ✅ All localStorage |
| JSON custody boundary | ✅ Deployment-v1 and result-v1 schemas |
| Local identity ≠ authentication | ✅ On every page |
| No autonomous publication | ✅ Results are advisory, not approval |
| No cross-project write | ✅ No Librarian paths referenced |
| No Librarian mutation | ✅ No Librarian file access |
| Advisory-only | ✅ All stored data has advisory context |

## JSON Schemas

### Deployment JSON (`deployment-v1`)
Created by admin, consumed by learner. Contains workspace name, member roster, and assigned training packages. Validated on import.

### Result JSON (`result-v1`)
Created by learner, consumed by admin. Contains learner ID, package results, completion timestamps. Validated on import.

## Maintenance Rules

- All pages are standalone — no build step, no dependencies
- Data model is `qapilot_state` (learner), `qapilot_admin` (admin), `qapilot_imported_results` (imported results), `qapilot_training_content` (loaded packages)
- Adding a new page requires: HTML file + link from relevant parent + localStorage read/write
- Schema changes require backward compatibility or data migration reset
- No package manager, no server, no build step
