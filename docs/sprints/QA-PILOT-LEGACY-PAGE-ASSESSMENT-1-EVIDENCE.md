# QA-PILOT-LEGACY-PAGE-ASSESSMENT-1-EVIDENCE.md

**Produced by:** QA-PILOT-LEGACY-PAGE-ASSESSMENT-1 (ledger #172)
**Date:** 2026-07-20
**Classification:** Advisory assessment evidence — does not authorize implementation

---

## Acceptance Gate Results

| Gate | Result | Assessment |
|------|--------|------------|
| LA-1 | PASS | All 14 legacy pages assessed |
| LA-2 | PASS | Usage status determined for each page |
| LA-3 | PASS | i18n state documented for each page |
| LA-4 | PASS | Recommendation produced for each page |
| LA-5 | PASS | No pages modified |
| LA-6 | PASS | Evidence produced (this document) |

**6 PASS, 0 FAIL**

---

## Per-Page Assessment

| # | Page | Purpose | Size | Lines | i18n State | Links to Core | Recommendation |
|---|------|---------|------|-------|------------|---------------|---------------|
| 1 | QA-Pilot-Session.html | Session launcher | 7.8KB | 270 | Absent | 1 | RETAIN (low effort, low impact — static page, no i18n needed) |
| 2 | QASimulator.html | QA Desktop simulator | 813KB | 7,597 | Partial | 2 | MIGRATE (active simulation surface, but large effort) |
| 3 | START_Me_Up.html | Loading splash | 1.8KB | 46 | Absent | 1 | RETIRE (splash page, can be removed) |
| 4 | ado-lab.html | Azure DevOps lab | 46KB | 1,316 | Partial | 0 | RETAIN (active lab, already has partial i18n) |
| 5 | capstone-lab.html | Capstone assessment | 30KB | 803 | Partial | 1 | RETAIN (active assessment, already has partial i18n) |
| 6 | capstone-2.html | Advanced capstone | 914KB | 8,956 | Partial | 4 | MIGRATE (active capstone, wired to core, large effort) |
| 7 | crm-lab.html | Dynamics CRM lab | 50KB | 1,268 | Partial | 0 | RETAIN (active lab, already has partial i18n) |
| 8 | confirm.html | Confirmation page | 5.9KB | 199 | Partial | 0 | RETAIN (already has functional i18n, minimal effort) |
| 9 | mock.html | Design mock | 41KB | 1,040 | Partial | 0 | RETAIN (design reference, low impact) |
| 10 | simple-login.html | Team login | 19KB | 546 | Partial | 2 | MIGRATE (active login surface, wired to db.js/app.js) |
| 11 | guide-facilitator.html | Facilitator guide | 16KB | 462 | Partial | 1 | RETAIN (static guide, already has partial i18n) |
| 12 | guide-student.html | Student quick start | 16KB | 460 | Partial | 1 | RETAIN (static guide, already has partial i18n) |
| 13 | chrome-extension/popup.html | Browser extension | 22KB | 600 | Partial | 0 | OWNER_DECISION_REQUIRED (extension has separate lifecycle) |
| 14 | desktop/dist.html | Desktop distribution | 814KB | 7,597 | Partial | 2 | OWNER_DECISION_REQUIRED (desktop app, separate packaging) |

---

## Detailed Assessment

### Pages Recommended for RETAIN (n=7)

These pages have partial or absent i18n but are either static enough that translation is low-value, or already functional with their current architecture.

| Page | Rationale |
|------|-----------|
| QA-Pilot-Session.html | Static session launcher. Single text node. Low user impact. |
| ado-lab.html | Active simulation lab with inline styles. Already has partial `t()` calls. |
| capstone-lab.html | Active capstone assessment with inline styles. Already has partial `t()` calls. |
| crm-lab.html | Active CRM simulation lab. Already has partial `t()` calls. |
| confirm.html | Minimal confirmation page (199 lines). Already has functional i18n. |
| mock.html | Design reference mock. Low user impact for i18n. |
| guide-facilitator.html | Static guide document. Already has partial i18n. |
| guide-student.html | Static guide document. Already has partial i18n. |

### Pages Recommended for MIGRATE (n=3)

These pages are actively used, visible to users, and would benefit from full i18n wiring.

| Page | Rationale | Estimated Effort |
|------|-----------|-----------------|
| QASimulator.html | Active simulation surface. 813KB, 7,597 lines. Large but user-facing. | **High** (~1 sprint) |
| capstone-2.html | Active advanced capstone. 914KB, 8,956 lines. Already has main.css + core deps. | **High** (~1 sprint) |
| simple-login.html | Active team login page. 19KB, 546 lines. Has db.js + app.js dependencies. | **Medium** (~1/2 sprint) |

### Pages Recommended for RETIRE (n=1)

| Page | Rationale |
|------|-----------|
| START_Me_Up.html | Loading splash page (46 lines, 1.8KB). No user-facing content of value. Likely an early prototype artifact. |

### Pages Requiring Owner Decision (n=2)

| Page | Question | Context |
|------|----------|---------|
| chrome-extension/popup.html | Should the Chrome extension remain part of the QA Pilot surface? | Extension has separate packaging and deployment lifecycle. May belong in a separate project. |
| desktop/dist.html | Should the desktop distribution remain part of the QA Pilot surface? | 814KB packaged desktop app. May have separate build/release pipeline. |

---

## Recommendation Summary

| Category | Count | Action |
|----------|-------|--------|
| RETAIN | 8 | No i18n work required |
| MIGRATE | 3 | Implementation sprint(s) needed |
| RETIRE | 1 | Decommission candidate |
| OWNER_DECISION_REQUIRED | 2 | Owner direction needed |

### Aggregate Migration Effort (if approved)

| Priority | Page | Effort |
|----------|------|--------|
| High | simple-login.html | ~1/2 sprint |
| Medium | QASimulator.html | ~1 sprint |
| Medium | capstone-2.html | ~1 sprint |
| **Total** | **3 pages** | **~2.5 sprints** |

---

## App Module Audit Dependency

Based on this assessment, the App Module Audit (deferred) should proceed as follows:

- If MIGRATE candidates are approved → audit app modules after migration to avoid double work
- If MIGRATE candidates are deferred → audit app modules against current surface

---

## Scope Compliance

| Check | Result |
|-------|--------|
| Translation keys added | None |
| Pages modified | None |
| Language toggles added | None |
| Templates refactored | None |
| App modules touched | None |

**Scope classification:** Assessment only. No implementation changes.

---

## Key Risk Note

The `QASimulator.html` and `desktop/dist.html` pages appear to be very similar (same file size, same line count). They may be duplicates or one may be a build artifact of the other. This should be verified before any migration work begins.

---

**Produced by:** QA-PILOT-LEGACY-PAGE-ASSESSMENT-1 (ledger #172)
**Classification:** Advisory assessment evidence — does not authorize implementation.
