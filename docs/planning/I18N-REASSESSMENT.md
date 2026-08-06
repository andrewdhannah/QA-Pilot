# I18N-REASSESSMENT.md

**Track B of QA-PILOT-POST-CANONICAL-SURFACE-REASSESSMENT-1**
**Date:** 2026-07-20
**Status:** Assessment complete — completion plan produced

---

## Coverage Findings

### Key Inventory

| Language | UI Keys | Course Content Keys | Total |
|----------|---------|-------------------|-------|
| English (lang-en.js) | 103 | 0 | 103 |
| French (lang-fr.js) | 103 | 351 | 454 |

**Key parity:** All 103 EN UI keys have FR equivalents. Zero missing translations for defined keys.

### Translation Module

| Component | Status | Notes |
|-----------|--------|-------|
| `i18n.js` | ✅ Functional | `__()` function, language toggle, localStorage persistence |
| `lang-en.js` | ✅ Complete | 103 UI keys |
| `lang-fr.js` | ✅ Complete | 103 UI keys + 351 course content keys |
| Language toggle | ✅ Wired | `renderLangToggle()` in 3 pages |
| `setLanguage()` | ✅ Functional | Sets language, fires event, reloads page |
| `initI18n()` | ✅ Functional | Reads localStorage, sets active language |

### Key Organization

| Prefix | Count | Pages |
|--------|-------|-------|
| `login_*` | 12 | index.html |
| `portal_*` | 25 | portal.html |
| `course_*` | 18 | course-view.html |
| `admin_*` | 15 | admin/*.html |
| `app_*` | 8 | apps/*.html |
| `global_*` | 10 | Shared |
| `lang_*` | 2 | Toggle labels |

---

## Runtime Validation

### Pages With i18n Integration

| Page | i18n Script | Language Toggle | `__()` Usage | Hardcoded Strings |
|------|-------------|-----------------|--------------|-------------------|
| `index.html` | ✅ Loaded | ✅ Present | ⚠️ Partial | ~10 hardcoded |
| `portal.html` | ✅ Loaded | ✅ Present | ⚠️ Partial | ~15 hardcoded |
| `course-view.html` | ✅ Loaded | ✅ Present | ✅ Full | 0 hardcoded |
| `admin/dashboard.html` | ⚠️ Not loaded | ❌ Absent | ⚠️ Partial | ~10 hardcoded |
| `admin/assign.html` | ⚠️ Not loaded | ❌ Absent | ⚠️ Partial | ~5 hardcoded |
| `admin/bugs.html` | ⚠️ Not loaded | ❌ Absent | ❌ None | ~5 hardcoded |
| `apps/*.html` | ⚠️ Mixed | ❌ Absent | ⚠️ Mixed | Variable |

### app.js Translation Usage

| Function | Count | Notes |
|----------|-------|-------|
| `t()` calls | 16 | Uses translation function in login flow |
| Direct i18n references | 0 | No direct `i18n.js` function calls |
| `isDemoAccount()` | 1 | Uses `t()` for demo account detection |

**Finding:** `app.js` uses a `t()` function (16 calls) but doesn't directly reference `i18n.js`. The `t()` function may be a wrapper or separate translation mechanism. This should be investigated during implementation.

---

## Missing Seams

### SEAM-I1: Hardcoded English in Core Pages

**Classification:** OBSERVATION

**index.html hardcoded strings:**
- Hero tagline: "Professional QA training that bridges the gap..."
- Feature labels: "Industry-Relevant", "Hands-On Labs", "Credentials", "Career Ready"
- Form labels: "Sign In", "Email address", "Password"
- Info section: "About QA Pilot Academy", "Professional Certificates"

**portal.html hardcoded strings:**
- Sidebar: "Quick Links", "Certificates", "Resources"
- Sections: "My Learning", "Available Courses"
- Stats: "Enrolled", "Completed"
- Buttons: "Sign Out", "Download Student Data"

**admin/dashboard.html hardcoded strings:**
- Onboarding: "Students", "Settings", "Assign Lessons"
- Stats: "Total Students"
- Navigation: "Administrator", "Sign Out"

### SEAM-I2: Admin Pages Without i18n

**Classification:** KNOWN LIMITATION

Admin pages (`dashboard.html`, `assign.html`, `bugs.html`, `editor.html`) do not load `i18n.js` and have no language toggle. All UI text is hardcoded English.

### SEAM-I3: Language Toggle Coverage

**Classification:** KNOWN LIMITATION

Only 3 of 43 pages have the language toggle. The toggle is functional where present but doesn't reach most of the application.

### SEAM-I4: Course Content Translation Scope

**Classification:** OBSERVATION

`lang-fr.js` contains 351 course content keys (vs 103 UI keys). This suggests course content was translated but the UI layer was not fully wired. The course content translations exist but may not be rendered if the HTML doesn't use `__('key')`.

---

## Recommended Completion Plan

### Phase 1: Core Page I18N Completion (High Priority)

**Scope:** Wire remaining hardcoded strings in `index.html`, `portal.html` to `__('key')` function.
**Estimated effort:** ~25 strings, 2 pages
**Output:** All core page text translatable

**Steps:**
1. Audit `index.html` for all hardcoded English strings
2. Add missing keys to `lang-en.js` and `lang-fr.js`
3. Replace hardcoded strings with `__('key')` calls
4. Verify language toggle affects all text
5. Repeat for `portal.html`

### Phase 2: Admin Page i18n (Medium Priority)

**Scope:** Add `i18n.js` to admin pages. Wire hardcoded strings. Add language toggle.
**Estimated effort:** ~20 strings, 4 pages
**Dependency:** Phase 1

**Steps:**
1. Add `i18n.js`, `lang-en.js`, `lang-fr.js` script tags to admin pages
2. Add `initI18n()` call to admin page scripts
3. Add language toggle to admin topbar
4. Wire hardcoded strings to `__('key')`
5. Add missing keys to language files

### Phase 3: App Module i18n (Low Priority)

**Scope:** Add i18n support to active app modules. Determine which modules need translation.
**Estimated effort:** Variable — depends on module count
**Dependency:** Phase 2

### Phase 4: Translation Validation (High Priority — after Phases 1-3)

**Scope:** Validate all translations render correctly. Check for encoding issues, placeholder substitution, RTL support.
**Estimated effort:** Validation only
**Dependency:** Phases 1-3

---

## Orphan Key Analysis

### Keys in lang-fr.js but Not Used in HTML

The course content keys (351 keys with `content_*` prefix) exist in `lang-fr.js` but may not be rendered in HTML if the course content doesn't use `__('key')`. This should be validated during implementation.

### Key Usage Pattern

| Pattern | Status |
|---------|--------|
| `__('key')` in HTML | ✅ Used in core pages |
| `t()` in app.js | ⚠️ Separate mechanism — investigate |
| Direct `LANG[key]` access | ⚠️ Possible in some modules |

---

**Produced by:** QA-PILOT-POST-CANONICAL-SURFACE-REASSESSMENT-1 (ledger #169)
**Classification:** Advisory planning evidence — does not authorize implementation.
