# QA-PILOT-MIGRATION-ROUNDTRIP-VALIDATION-1

**Sprint:** 5/5 of `EPIC-QA-PILOT-OPENWORK-TO-CARBIDEFRAME-MIGRATION-1`
**Type:** validation (roundtrip)
**Lane:** migration
**Boundary:** QA Pilot-local, read-only comparison. No Librarian mutation.
**Librarian impact:** none
**Status:** ✅ Sealed (ledger #160, 2026-07-13)
**Approval token:** `apt_95de2494`

---

## 1. Sprint Goal

Full roundtrip validation: compare the migrated CarbideFrame copy against the OpenWork source. Validate completeness of the migration. Produce a canonical-source recommendation.

## 2. Roundtrip Comparison Results

### 2a. File Inventory

| Metric | Count |
|--------|-------|
| OpenWork source files (excluding .git, .DS_Store) | ~123 |
| Manifest files (Sprint 1 copy plan) | 123 |
| CarbideFrame browser-app/ files | 124 (123 manifest + .gitkeep) |

**Result:** 123/123 manifest files present in browser-app/. Zero missing. One extra (`.gitkeep`, intentional from Sprint 1).

### 2b. Byte-Level SHA Verification

| Metric | Count |
|--------|-------|
| Files compared | 123 |
| Byte-identical matches | **120** |
| Intentional deviations | **3** |

The 3 deviations are the **Sprint 3 path fixes** — documented, Owner-authorized, and required for the app to function:

| File | Fix | Reason |
|------|-----|--------|
| `certificate.html` | `course.html` → `course-view.html` | Reference to non-existent page |
| `desktop/index.html` | `href="os.css"` → `href="../os.css"` | Wrong relative path depth |
| `desktop/dist.html` | `src="data/bug-keys.js"` → `src="../data/bug-keys.js"` | Wrong relative path depth |

**Verification:** OpenWork source SHA matches the manifest SHA for all 3 files (OpenWork untouched). CarbideFrame SHA differs because the fix was applied. This is the correct, expected behavior.

### 2c. Functional Flow Completeness

| Flow | Files Checked | All Exist | Status |
|------|---------------|-----------|--------|
| Login/session | 4 (index.html, simple-login.html, js/db.js, js/app.js) | ✅ | PASS |
| Portal/catalog | 3 (portal.html, js/db.js, data/content.js) | ✅ | PASS |
| Course-view/lesson | 4 (course-view.html, js/db.js, data/content.js, css/main.css) | ✅ | PASS |
| Certificate | 2 (certificate.html, js/pdf-lib.js) | ✅ | PASS |
| Admin suite | 6 (all admin pages) | ✅ | PASS |
| Simulator | 4 (QASimulator.html, src/os-core.js, os.css, os.bundle.js) | ✅ | PASS |
| QA module | 4 (qa-db.js, qa-export-json.js, qa-export-md.js, qa-import-json.js) | ✅ | PASS |
| Debug panel | 2 (debug/index.html, debug/debug-panel.js) | ✅ | PASS |

**Result:** 8/8 functional flows complete. All critical paths resolve.

### 2d. Path Risk Residual

**Zero** non-blocking broken references remaining (all fixed in Sprint 3).

### 2e. Governance Integration

| Check | Result |
|-------|--------|
| `is_web_app = true` | ✅ |
| `web_app_root` set | ✅ |
| `browser-app/` in `allowed_mutation_paths` | ✅ |
| `QA-PILOT-BROWSER-APP-SEPARATION.md` exists | ✅ |

## 3. Canonical-Source Recommendation

**PROMOTE_TO_CANONICAL_WITH_NOTES** (HIGH confidence)

120/123 files byte-identical to OpenWork source. 3 intentional, documented path fixes improve the app. All 8 functional flows complete. Zero broken refs. Governance integration complete.

The CarbideFrame `browser-app/` is functionally equivalent to and structurally improved over the OpenWork source. It can replace the OpenWork source as canonical after explicit Owner decision.

**Owner decision required:** Promote CarbideFrame `browser-app/` to canonical. This is a governance decision, not an automated action.

## 4. Sprint 5 Acceptance Gates

| Gate | Result |
|------|--------|
| All 123 manifest files present | ✅ |
| SHA verification (120 identical, 3 intentional) | ✅ |
| All 8 functional flows complete | ✅ |
| Zero blocking path defects | ✅ |
| Governance integration verified | ✅ |
| Recommendation produced | ✅ |

## 5. Epic Closure

| Sprint | Ledger | Status |
|--------|--------|--------|
| QA-PILOT-MIGRATION-PREP-AND-SNAPSHOT-1 | #156 | ✅ Sealed |
| QA-PILOT-OPENWORK-APP-COPY-1 | #157 | ✅ Sealed |
| QA-PILOT-MIGRATED-APP-SMOKE-VALIDATION-1 | #158 | ✅ Sealed |
| QA-PILOT-CARBIDEFRAME-GOVERNANCE-INTEGRATION-1 | #159 | ✅ Sealed |
| QA-PILOT-MIGRATION-ROUNDTRIP-VALIDATION-1 | #160 | ✅ Sealed |

**Epic status:** ✅ Fully sealed. All 5 sprints complete.

## 6. Next Steps (Owner Decision Required)

1. **Promote to canonical:** Owner decides whether CarbideFrame `browser-app/` replaces OpenWork source as the single source of truth.
2. **Archive OpenWork:** After promotion, OpenWork QA Pilot can be archived or marked superseded.
3. **Follow-up epics (optional):** Librarian visual design reapplication, I18N revalidation against the complete app.
