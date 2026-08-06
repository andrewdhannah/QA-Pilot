# QA-PILOT-POST-ASSESSMENT-DECISION-PACKAGE-1 — Post-Assessment Decision Package

**Artifact class:** decision package (post-assessment planning artifact)
**Status:** ✅ **DECISIONS RECORDED — Owner-authorized 2026-07-20**
**Prepared:** 2026-07-20
**Location:** `docs/planning/`

---

## Phase Summary

### Assessment Chain

| # | Sprint | Outcome | Evidence |
|---|--------|---------|----------|
| #172 | Legacy Page Assessment | 8 RETAIN, 3 MIGRATE candidates, 1 RETIRE, 2 OWNER DECISION | Assessed 14 pages |
| #174 | Surface Reconciliation | QASimulator/desktop confirmed duplicates; capstone-2 distinct | 3 surfaces compared |
| #175 | App Module Audit | All 16 modules shared between QASimulator AND capstone-2 | 16 modules inventoried |

### Completed Governance Chain

| Area | Status |
|------|--------|
| Canonical transition | COMPLETE |
| Identity correction | SEALED (#167) |
| Validator repair | SEALED (#168) |
| Core I18N | SEALED (#170) |
| Admin I18N | SEALED (#171) |
| Legacy assessment | SEALED (#172) |
| Login migration | SEALED (#173) |
| Surface reconciliation | SEALED (#174) |
| App module audit | SEALED (#175) |

---

## Section 1 — Implementation Candidates

### Candidate A: capstone-2 I18N Migration

**Source:** #174 (Surface Reconciliation) — classified MIGRATE
**Evidence:** Distinct active assessment surface, 914KB, 8,956 lines, deeply integrated (12+ refs from course-view, portal, 6 app modules)
**Constraint:** All 16 `apps/` modules are shared between capstone-2 AND QASimulator. Module-level changes affect both surfaces.

**Recommended action:** Migration planning package, not immediate coding.

### Candidate B: START_Me_Up Retirement

**Source:** #172 (Legacy Page Assessment) — classified RETIRE
**Evidence:** 46-line loading splash page, 1.8KB, no functional content, likely early prototype artifact
**Recommended action:** Remove or archive.

### Candidate C: desktop/dist.html Consolidation

**Source:** #174 (Surface Reconciliation) — classified CONSOLIDATE
**Evidence:** Byte-level duplicate of QASimulator.html with single path difference (`js/db.js` vs `../js/db.js`)
**Recommended action:** Retire duplicate or replace with symlink.

---

## Section 2 — Owner Decisions Required

### Decision 1: Desktop Distribution Pathway

| Decision | Detail |
|----------|--------|
| Outcome | CONSOLIDATE — retire desktop/dist.html duplicate |
| Rationale | Confirmed duplicate of QASimulator.html with single path difference. Maintain single canonical surface. |

### Decision 2: Chrome Extension

| Decision | Detail |
|----------|--------|
| Outcome | RETAIN in current project |
| Rationale | Keep within QA Pilot project for now; separate lifecycle decision deferred. |

### Decision 3: QASimulator I18N Direction

| Decision | Detail |
|----------|--------|
| Outcome | MIGRATE — include in combined surface migration |
| Rationale | Shared module constraint requires coordinated migration with capstone-2. |

### Decision 4: START_Me_Up Lifecycle

| Decision | Detail |
|----------|--------|
| Outcome | RETIRE — remove loading splash page |
| Rationale | 46-line page with no functional content. No runtime references identified. |

---

## Section 3 — Decision-Action Map

```
Owner Decision              Implementation
────────────────────────────────────────────────
capstone-2 migration  ──>  Migration sprint(s)
                              (coordinated with QASimulator)

Desktop distribution  ──>  CONSOLIDATE or RETIRE path

Chrome extension      ──>  SEPARATE or RETAIN path

QASimulator i18n      ──>  MIGRATE or DEFER path
                              (coordinated with capstone-2)

START_Me_Up           ──>  RETIRE or RETAIN path
```

### Coordination Requirement

Because all 16 `apps/` modules are shared between capstone-2 and QASimulator:

- Modules cannot be migrated independently
- A joint migration plan covering both surfaces is required
- Module-related acceptance gates must specify dual-surface validation

---

## Section 4 — Artifact Binding

```
Prepared By:
Agent (QA Pilot governance harness)

Assessment Basis:
#172 Legacy Page Assessment
#174 QASimulator/Capstone Surface Reconciliation
#175 App Module Audit

Implementation Authorization:
Pending — Owner decisions required first
```

---

**End of QA-PILOT-POST-ASSESSMENT-DECISION-PACKAGE-1 (Preliminary)**
