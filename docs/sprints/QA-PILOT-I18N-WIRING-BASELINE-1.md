# QA Pilot I18N Wiring Baseline

**Sprint:** QA-PILOT-I18N-WIRING-BASELINE-1 (Ledger #148)
**Lane:** i18n_wiring
**Epic:** EPIC-QA-PILOT-I18N-WIRING-1 (Sprint 1/5)
**Boundary:** qa_pilot_local
**Librarian impact:** none
**Status:** authorized — Owner-approved 2026-07-09
**Dependencies:** None

---

## Purpose

Inventory all hardcoded visible UI text across the 8 QA Pilot browser asset pages. Identify existing translation functions, dictionaries, language state, reload behavior, and gaps. Produce a page-by-page I18N wiring plan.

## Scope — Included

1. Inspect all 8 browser asset pages for hardcoded visible text
2. Map existing `__()` function, LANG dictionaries, language state, reload behavior
3. Classify text by category (shell, nav, labels, content, status, footer, alerts)
4. Document page-by-page I18N gaps with string counts
5. Evaluate risks to layout, accessibility, custody
6. Recommend Sprint 2 dictionary scope

## Scope — Excluded

- No broad rewrites or dictionary creation
- No backend/services
- No auth/install

---

## Completion Report

### Files Inspected (9)

| File | Lines | Type |
|------|-------|------|
| `js/i18n.js` | 315 | Translation engine |
| `i18n/lang-en.js` | 180 | English dictionary (96 keys) |
| `i18n/lang-fr.js` | 2630 | French dictionary (96 UI keys + course content) |
| `index.html` | 157 | Splash page |
| `admin.html` | 389 | Admin dashboard |
| `identity.html` | 127 | Learner identity |
| `catalog.html` | 163 | Training portal |
| `course-view.html` | 337 | Course runtime |
| `certificate.html` | 100 | Certificate |
| `export.html` | 102 | Result export |
| `import.html` | 106 | Admin import |

### Hardcoded Visible UI Text Found

All 8 pages have **zero `__()` calls** in HTML. Every visible text string is hardcoded.

| Page | Strings Found | Categories | Total Strings |
|------|---------------|------------|---------------|
| `index.html` | Title, h1, mode cards (3), identity note, footer | shell, nav, status | ~12 |
| `admin.html` | Title, headings (6), buttons (7), labels (4), placeholders (3), alerts, status text, footer | shell, nav, labels, status, footer | ~35 |
| `identity.html` | Title, h1, heading, confirm button, deployment info, identity note, footer | shell, nav, status, footer | ~10 |
| `catalog.html` | Title, h1, hero text, learner name, status text, footer | shell, nav, status, footer | ~10 |
| `course-view.html` | Title, welcome text, nav buttons (2), complete button, progress text, placeholder, sources, exercise area, footer | shell, nav, labels, status, footer | ~18 |
| `certificate.html` | Title, h1, completion text, learner info, details, advisory, print button, footer | shell, labels, status, footer | ~15 |
| `export.html` | Title, h1 (with "Academy" span), description, download button, note, footer | shell, labels, status, footer | ~8 |
| `import.html` | Title, h1 (with "Academy" span), description, upload label, advisory note, footer | shell, labels, status, footer | ~8 |
| **Total** | | | **~116** |

### Current `__()` and Dictionary Posture

| Component | Status |
|-----------|--------|
| `__()` function | ✅ Working — escapeHtml, interpolation, fallback, EN→FR dictionary switch |
| LANG_EN dictionary | ✅ Exists — 96 keys, but ~40 are legacy login strings from previous version |
| LANG_FR dictionary | ✅ Exists — 96 UI keys with French (Québec) translations |
| `initI18n()` | ✅ Called on page load — sets `LANG`, `currentLang`, `document.documentElement.lang`, tries `page_title_*` |
| `setLanguage()` | ✅ Switches dict, saves to localStorage, reloads page, updates `lang` attr |
| Page text using `__()` | ❌ **0 calls across all 8 pages** — all text hardcoded |
| Dictionary keys usable for current pages | ~56 of 96 keys are relevant to current browser-only pages |

### Page-by-Page I18N Gap List

| Page | Shell | Nav | Labels | Status | Footer | Existing `page_title_*` Key? |
|------|-------|-----|--------|--------|--------|------------------------------|
| `index.html` | h1, brand, mode cards | — | file input | identity note | 3 items | `page_title_index.html` → "Sign In" (wrong) |
| `admin.html` | 6 headings | 6 tabs | 4 labels + 3 placeholders | workspace indicator, alerts, identity note | 3 items | ❌ Missing |
| `identity.html` | h1, hero | back link | confirm button | deployment info, identity note | 3 items | ❌ Missing |
| `catalog.html` | h1, hero, learner name | home link | — | in-progress status, completed status | 3 items | `page_title_portal.html` (exists) |
| `course-view.html` | welcome, lesson title | prev/next, back | exercise placeholder | progress %, breadcrumb, sources | 3 items | `page_title_course-view.html` (exists) |
| `certificate.html` | h1, badge | back, print | — | completion details, advisory note | 3 items | ❌ Missing |
| `export.html` | h1 | back | — | item list, preview, note | 3 items | ❌ Missing |
| `import.html` | h1 | back | file upload | dashboard stats, advisory note | 3 items | ❌ Missing |

### Risks to Accessibility, Layout, and Custody

| Risk | Assessment |
|------|------------|
| **Layout breakage** | Low — `__()` replaces text in place; string length may vary (EN→FR) but existing dictionary fits current UI |
| **Accessibility regression** | Low — `__()` output goes into same elements; `aria-label`, `alt`, `title` attrs must also be wired |
| **Static-browser custody** | None — `__()` reads from static JS dictionary, no network calls |
| **Missing keys** | Medium — ~60 new keys needed; missing keys fall back to English or key name |
| **Existing legacy keys** | Low — ~40 login keys are unused but harmless; can be pruned in Sprint 2 |

### Recommended Sprint 2 Dictionary Scope

Recommended dictionary categories for `QA-PILOT-I18N-CORE-DICTIONARY-1`:

1. **Shell/Shared** — `app_name`, `app_brand`, `footer_source`, `footer_identity`, `footer_advisory`, `lang_en`, `lang_fr`, `skip_link`
2. **Navigation** — `back_link`, `home_link`, `admin_link`, `view_results`, `create_deployment`, `manage_members`
3. **Status/Labels** — `workspace_label`, `members_label`, `packages_label`, `no_workspace`, `no_results`, `identity_note`, `advisory_notice`
4. **Page-specific** — key per unique page heading/button string
5. **Admin** — tab labels (6), button labels (7), form labels (4), placeholders (3), empty states, bento heading labels
6. **Learner** — catalog headings, course nav, certificate text, export/import descriptions
7. **Titles** — add/update `page_title_*` for all 8 pages
8. **Legacy cleanup** — remove ~40 unused login keys

Estimated new keys needed: **~80–100** (across both EN and FR dictionaries).

### Validation Results

| Check | Result |
|-------|--------|
| All 8 pages inspected for hardcoded text | ✅ ~116 strings found |
| Translation function inspected | ✅ `__()` working, fallbacks, escapeHtml |
| Dictionary posture mapped | ✅ 96 keys, ~56 relevant, ~40 legacy |
| `page_title_*` dictionary keys | 3 of 8 page titles currently have keys |
| `__()` calls in HTML pages | ❌ **0 — epic gap confirmed** |
| Risks documented | ✅ All assessed (layout/a11y/custody — low/medium) |
| Sprint 2 recommendation provided | ✅ 8 categories, ~80-100 new keys |

### Unresolved Issues

| Issue | Impact | Sprint |
|-------|--------|--------|
| Existing `page_title_index.html` → "Sign In" (wrong — should be splash/startup) | Minor — title key exists but has incorrect label | Sprint 2 (dictionary) |
| ~40 legacy login keys exist in dictionary | None — unused but take up space | Sprint 2 (cleanup) |
| DE/FR/ES/other languages not present | Out of scope — EN/FR only | — |

### Owner Review Posture

| Aspect | Status |
|--------|--------|
| Sprint scope respected | ✅ Inventory only — no dictionary edits or text changes |
| No sealed epics mutated | ✅ Referenced by reference only |
| Sprint 2 not advanced | ✅ Not started — awaiting direction |
| Authority boundaries preserved | ✅ |

## Authorization Reference

- **Decision ID:** `OD-EPIC-QA-PILOT-I18N-WIRING-1-AUTHORIZATION`
- **Owner:** Andrew Hannah
- **Date:** 2026-07-09
