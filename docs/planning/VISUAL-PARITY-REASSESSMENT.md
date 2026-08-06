# VISUAL-PARITY-REASSESSMENT.md

**Track A of QA-PILOT-POST-CANONICAL-SURFACE-REASSESSMENT-1**
**Date:** 2026-07-20
**Status:** Assessment complete — implementation recommendations produced

---

## Current State

### Design System

| Component | Status | Notes |
|-----------|--------|-------|
| CSS Design Tokens | ✅ Present | `main.css` `:root` defines 25+ color tokens, status colors, lesson colors |
| Consistent Typography | ✅ Present | Font stack, sizes, weights defined in main.css |
| Component Classes | ✅ Present | `.btn`, `.card`, `.form-control`, `.topbar`, `.login-*`, `.portal-*` |
| Status Badges | ✅ Present | `.status-open`, `.status-in-progress`, `.status-pending`, `.status-resolved`, `.status-closed` |
| Mock CSS | ✅ Present | `ado-mock.css`, `dynamics-mock.css` for simulated app environments |

### Page Inventory

| Category | Pages | main.css | Language Toggle | Consistent Navigation |
|----------|-------|----------|-----------------|----------------------|
| Core (login/portal/course) | 3 | ✅ All | ✅ All | ✅ Yes |
| Admin | 4 | ✅ All | ❌ None | ✅ Topbar |
| Apps (content modules) | 16 | ✅ All | ❌ None | ⚠️ Varies |
| Legacy/Lab | 14 | ⚠️ 6 missing | ❌ None | ❌ Inconsistent |
| Desktop/Debug | 3 | ⚠️ Mixed | ❌ None | ❌ Inconsistent |
| **Total** | **43** | **35 linked** | **3 toggle** | **~20 consistent** |

### Core Application Pages

| Page | Design Consistency | i18n Integration | Navigation |
|------|-------------------|------------------|------------|
| `index.html` (Sign In) | ✅ Consistent | ⚠️ Partial (hardcoded strings) | ✅ Login layout |
| `portal.html` (Training Portal) | ✅ Consistent | ⚠️ Partial (hardcoded strings) | ✅ Sidebar + topbar |
| `course-view.html` (Course Viewer) | ✅ Consistent | ✅ Wired | ✅ Consistent |
| `admin/dashboard.html` | ✅ Consistent | ⚠️ Partial | ✅ Topbar |
| `admin/assign.html` | ✅ Consistent | ⚠️ Partial | ✅ Topbar |
| `admin/bugs.html` | ✅ Consistent | ⚠️ Partial | ✅ Topbar |
| `admin/editor.html` | ✅ Consistent | ⚠️ Partial | ✅ Topbar |

---

## Gap Inventory

### GAP-V1: Hardcoded English in Core Pages

**Severity:** OBSERVATION
**Impact:** Language toggle exists but doesn't affect all visible text

**Affected pages:**
- `index.html`: 10+ hardcoded strings (tagline, hero features, form labels, info section)
- `portal.html`: 15+ hardcoded strings (sidebar titles, section headers, button labels)
- `admin/dashboard.html`: 10+ hardcoded strings (onboarding sections, stats labels)

**Example (index.html):**
```html
<!-- Hardcoded — not using __('key') -->
<p class="login-hero-tagline">Professional QA training that bridges the gap...</p>
<div class="hero-feature-text"><strong>Industry-Relevant</strong> – Real-world testing scenarios</div>
<h1 class="login-title">Sign In</h1>
```

**Recommendation:** Wire remaining hardcoded strings to `__('key')` function. Estimated ~35 strings across 3 core pages.

### GAP-V2: Legacy Pages Without Design System

**Severity:** OBSERVATION
**Impact:** 8 pages don't link `main.css` — inconsistent visual appearance

**Affected pages:**
- `QA-Pilot-Session.html`, `QASimulator.html`, `START_Me_Up.html`
- `ado-lab.html`, `capstone-lab.html`, `crm-lab.html`
- `confirm.html`, `mock.html`, `simple-login.html`
- `guide-facilitator.html`, `guide-student.html`

**Recommendation:** Determine if these pages are:
1. **Active** — need main.css integration
2. **Legacy/reference** — can be excluded from parity scope

### GAP-V3: Language Toggle Coverage

**Severity:** OBSERVATION
**Impact:** Only 3 of 43 pages have language toggle

**Pages with toggle:** `index.html`, `portal.html`, `course-view.html`
**Pages without toggle:** 40 pages

**Recommendation:** Add language toggle to admin pages and active app modules. Legacy pages may not need toggle if they're reference-only.

### GAP-V4: App Module Design Consistency

**Severity:** OBSERVATION
**Impact:** 16 content modules in `apps/` have varying design approaches

**Modules with consistent design:** `training.html`, `settings.html`, `reports.html`, `browser.html`
**Modules with custom design:** `dynamics.html`, `teams.html`, `qoutlook.html`

**Recommendation:** Audit app modules for design token usage. Modules that simulate real apps (dynamics, teams, outlook) may intentionally use custom styling.

---

## Impact Classification

| Gap | Classification | Action |
|-----|---------------|--------|
| GAP-V1: Hardcoded English | OBSERVATION | Re-plan — wire to i18n |
| GAP-V2: Legacy pages | OBSERVATION | Determine active vs legacy |
| GAP-V3: Toggle coverage | KNOWN LIMITATION | Add toggle to active pages |
| GAP-V4: App module consistency | OBSERVATION | Audit intent of custom styling |

---

## Recommended Implementation Scope

### Phase 1: Core Page I18N Wiring (High Priority)

**Scope:** Wire hardcoded strings in `index.html`, `portal.html`, `admin/dashboard.html` to `__('key')` function.
**Estimated effort:** ~35 strings, 3 pages
**Dependency:** None — can proceed immediately

### Phase 2: Admin Page I18N (Medium Priority)

**Scope:** Add language toggle to admin pages. Wire remaining hardcoded strings.
**Estimated effort:** ~15 strings, 4 pages
**Dependency:** Phase 1

### Phase 3: Legacy Page Assessment (Low Priority)

**Scope:** Determine which legacy pages are active. Add main.css and language toggle to active pages.
**Estimated effort:** Variable — depends on active page count
**Dependency:** Owner decision on legacy page status

### Phase 4: App Module Audit (Low Priority)

**Scope:** Audit app modules for design consistency. Determine which modules need parity vs. intentional custom styling.
**Estimated effort:** Audit only — implementation varies
**Dependency:** Phase 3

---

## Proposed Future Sprint Breakdown

| Sprint | Scope | Priority |
|--------|-------|----------|
| QA-PILOT-CORE-I18N-WIRING-1 | Wire hardcoded strings in 3 core pages | High |
| QA-PILOT-ADMIN-I18N-WIRING-1 | Add toggle + wire strings in admin pages | Medium |
| QA-PILOT-LEGACY-PAGE-ASSESSMENT-1 | Determine active legacy pages | Low |
| QA-PILOT-APP-MODULE-AUDIT-1 | Audit app module design consistency | Low |

---

**Produced by:** QA-PILOT-POST-CANONICAL-SURFACE-REASSESSMENT-1 (ledger #169)
**Classification:** Advisory planning evidence — does not authorize implementation.
