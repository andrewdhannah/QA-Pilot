# QA Pilot Frontend Operational Baseline

**Sprint:** QA-PILOT-FRONTEND-OPERATIONAL-BASELINE-1 (Sprint 9/9)
**Epic:** EPIC-QA-PILOT-ORIGINAL-FRONTEND-MIGRATION-1
**Status:** sealed — Owner-approved 2026-07-09 per OD-EPIC-QA-PILOT-ORIGINAL-FRONTEND-MIGRATION-1-BATCH-SEAL

## Purpose

Lock the migrated frontend with a design parity checklist, operational file inventory, browser-only constraints, and maintenance rules.

---

## 1. File Inventory

```
browser-assets/  (16 files, 8 pages + 8 support files)
├── index.html          — Splash/startup — 4 modes, EN/FR toggle
├── admin.html          — Admin workspace — workspace, members, packages, deploy, results
├── identity.html       — Learner identity selection from deployment roster
├── catalog.html        — Training catalog — course cards, progress, completed
├── course-view.html    — Course runtime — two-column, sidebar, quiz, progress
├── export.html         — Result JSON export
├── import.html         — Admin result import — dashboard with stats
├── certificate.html    — Completion certificate — print-to-PDF
├── css/main.css        — Original design system (933 lines, 29KB)
├── css/ado-mock.css    — Original ADO mock styling (278 lines)
├── css/dynamics-mock.css — Original Dynamics mock styling (353 lines)
├── js/i18n.js          — Original translation engine (315 lines)
├── i18n/lang-en.js     — English language pack (180 lines)
├── i18n/lang-fr.js     — French language pack (2,630 lines)
├── favicon.png         — Brand icon (3KB)
└── favicon.svg         — Brand vector (864 bytes)
```

All 8 pages are standalone static HTML. No build step, no server, no install.

## 2. Design Parity Checklist

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Uses original `main.css` design system | ✅ | All pages reference `css/main.css` |
| 2 | Uses original brand assets (`favicon.*`) | ✅ | All pages reference `favicon.svg` |
| 3 | "QA Pilot Academy" product naming | ✅ | All pages |
| 4 | Light theme (no greenfield dark) | ✅ | No `#0f1117`, `#1a1d28`, `#2a2d3a` in any file |
| 5 | Original topbar structure | ✅ | Frosted glass, SVG logo, brand name |
| 6 | Blue gradient hero sections | ✅ | Portal, admin, identity, catalog, certificate |
| 7 | original design tokens (`--color-primary`, `--space-*`, `--text-*`) | ✅ | Used throughout |
| 8 | Original admin layout (topbar + tabs + cards) | ✅ | `admin.html` |
| 9 | Original portal layout (topbar + hero + course grid) | ✅ | `catalog.html` |
| 10 | Original runtime layout (two-column sidebar + content) | ✅ | `course-view.html` |
| 11 | Original lesson navigation (prev/next + complete) | ✅ | `course-view.html` |
| 12 | Quiz/exercise rendering with feedback | ✅ | `course-view.html` |
| 13 | Certificate with print-to-PDF | ✅ | `certificate.html` |
| 14 | i18n EN/FR toggle on every page | ✅ | All pages load `i18n.js`, `lang-en.js`, `lang-fr.js` |
| 15 | No greenfield CSS inline replacement of main.css | ✅ | All pages use `main.css` + minimal page-specific overrides |

## 3. Browser-Only Constraint Checklist

| # | Constraint | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Static browser — no backend | ✅ | All files are standalone HTML |
| 2 | No server authentication | ✅ | No password fields, no login API |
| 3 | No installed software | ✅ | Open browser → open file |
| 4 | No cloud account dependency | ✅ | No API keys, no signup |
| 5 | localStorage for state | ✅ | `qapilot_state`, `qapilot_admin`, `qapilot_imported_results`, `qapilot_exercises`, `qapilot_training_content` |
| 6 | JSON import/export is custody boundary | ✅ | `deployment-v1` and `result-v1` schemas |
| 7 | Local identity ≠ authentication | ✅ | Identity note on every page |
| 8 | No cross-project write | ✅ | No Librarian file paths |
| 9 | No Librarian mutation | ✅ | No Librarian write operations |
| 10 | No autonomous publication | ✅ | All results advisory, Owner review required |

## 4. Workflow Verification

```
Admin (admin.html) → Create workspace → Add members → Assign packages → Generate deployment JSON
    ↓ (send JSON file)
Learner (index.html) → Import deployment → Select identity (identity.html)
    ↓
Learner (catalog.html) → View assigned packages
    ↓
Learner (course-view.html) → Complete sections → Submit exercises → Mark Complete
    ↓ (auto-redirect)
Learner (certificate.html) → View/print completion certificate
    ↓
Learner (export.html) → Export result JSON
    ↓ (send JSON file)
Admin (import.html) → Import result JSON → Dashboard shows completion
```

## 5. Allowed vs Forbidden Frontend Changes

### Allowed
- Adding new i18n translations to `lang-en.js` / `lang-fr.js`
- Adding new course packs to the training data
- Styling refinements using existing `main.css` tokens
- Bug fixes to existing JavaScript workflows
- Content updates to training material

### Forbidden
- **No greenfield frontend replacement** — any new page must first check original QA Pilot for reusable components
- **No backend introduction** — all state stays in localStorage
- **No authentication system** — local identity only
- **No rebuild of design system** — use existing `main.css` tokens
- **No inline CSS replacing main.css** — rely on design tokens, not hardcoded colors
- **No cross-project write** — Librarian stays read-only
- **No autonomous publication** — Owner/Trainer review required for deployment or result use

## 6. Maintenance Rules

1. **Adding a new page**: Copy existing page structure (topbar, hero, `main.css` ref, i18n scripts). Follow the established layout patterns.
2. **Adding i18n strings**: Add to both `lang-en.js` and `lang-fr.js`. Use `__('key')` for lookup.
3. **Data model changes**: All localStorage keys prefixed `qapilot_*`. Document new keys in this baseline.
4. **Schema changes**: Update `deployment-v1` or `result-v1` schemas. Maintain backward compatibility or document migration.
5. **Testing**: Open from `file://` in any modern browser. No build step required.
6. **Regression check**: Run design parity checklist (§2) and constraint checklist (§3) after any frontend change.

## 7. Completed Epic

```
EPIC-QA-PILOT-ORIGINAL-FRONTEND-MIGRATION-1 — Complete

[✓] QA-PILOT-ORIGINAL-ASSET-INVENTORY-1                 #126
[✓] QA-PILOT-ADMIN-CONSOLE-DESIGN-PORT-1                #127
[✓] QA-PILOT-LEARNER-PORTAL-DESIGN-PORT-1               #128
[✓] QA-PILOT-COURSE-RUNTIME-DESIGN-PORT-1               #129
[✓] QA-PILOT-QUIZ-FLOW-PORT-1                           #130
[✓] QA-PILOT-CERTIFICATE-PORT-1                         #131
[✓] QA-PILOT-I18N-PORT-1                                #132
[✓] QA-PILOT-WORKFLOW-INTEGRATION-1                     #133
[✓] QA-PILOT-FRONTEND-OPERATIONAL-BASELINE-1            #134 (sealed)
```
