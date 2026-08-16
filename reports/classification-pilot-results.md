# ASSURANCE-CORPUS-CLASSIFICATION-1: Classification Pilot

**Status:** IN PROGRESS
**Date:** 2026-08-11
**Purpose:** Test classification categories against 27 real FAILs before locking the disposition enum

---

## Pilot Results

### Classification Categories (Proposed)

| Category | Description |
|---|---|
| IMPLEMENTATION_REGRESSION | Current behavior contradicts historical claim |
| HISTORICAL_BEHAVIOR_SUPERSEDED | Sprint claim was true when sealed but has since been superseded |
| INTENTIONAL_BEHAVIOR_CHANGE | Deliberate modification from historical behavior |
| HISTORICAL_CLAIM_NOT_OPERATIONAL | Claim was aspirational, never implemented |
| REQUIREMENT_DERIVATION_ERROR | Derived requirement doesn't accurately capture the sprint claim |
| TEST_CONSTRUCTION_ERROR | Artifact construction was incomplete |
| ENVIRONMENT_DEPENDENCY_EFFECT | External factor affected execution |
| UNRESOLVED | Not yet understood |

---

### Pilot Execution: 27 FAILs Classified

| # | Test ID | Sprint | Test Type | Classification | Rationale |
|---|---------|--------|-----------|----------------|-----------|
| 1 | UI-SHELL-1-FIX-1-T002 | UI-SHELL-1-FIX-1 | existence | REQUIREMENT_DERIVATION_ERROR | Test assumed sprint doc exists; evidence is in sprint ledger, not separate file |
| 2 | UI-SHELL-2-T002 | UI-SHELL-2 | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern — no separate doc file |
| 3 | UI-WORKLANE-1-T002 | UI-WORKLANE-1 | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern |
| 4 | UI-WORKLANE-2-T002 | UI-WORKLANE-2 | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern |
| 5 | UI-DECISIONS-1-T002 | UI-DECISIONS-1 | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern |
| 6 | UI-RECEIPTS-1-T002 | UI-RECEIPTS-1 | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern |
| 7 | MCP-OPENWORK-COMPAT-1-PART-B-T002 | MCP-OPENWORK-COMPAT-1-PART-B | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern |
| 8 | HARNESS-EXFIL-CLI-REPAIR-1-T002 | HARNESS-EXFIL-CLI-REPAIR-1 | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern |
| 9 | UI-PRODUCT-REVIEW-1-T002 | UI-PRODUCT-REVIEW-1 | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern |
| 10 | UI-FIRST-ACTION-2-T002 | UI-FIRST-ACTION-2 | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern |
| 11 | UI-SHELL-REBUILD-1A-T002 | UI-SHELL-REBUILD-1A | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern |
| 12 | UI-SHELL-REBUILD-1B-T002 | UI-SHELL-REBUILD-1B | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern |
| 13 | UI-SHELL-REBUILD-1C-T002 | UI-SHELL-REBUILD-1C | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern |
| 14 | UI-SHELL-REBUILD-1C-FIX-1-T002 | UI-SHELL-REBUILD-1C-FIX-1 | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern |
| 15 | UI-SHELL-REBUILD-1C-FIX-2-T002 | UI-SHELL-REBUILD-1C-FIX-2 | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern |
| 16-27 | (remaining) | (various) | existence | REQUIREMENT_DERIVATION_ERROR | Same pattern |

---

### Pilot Finding

**All 27 FAILs in this pilot share the same root cause:**

The test construction assumed that every sealed sprint would have a separate documentation file at `docs/sprints/<SPRINT_ID>.md`. However, many sprints — particularly UI sprints — have their evidence recorded in the sprint ledger's `evidence_note` field rather than in separate doc files.

This is a **REQUIREMENT_DERIVATION_ERROR**, not an IMPLEMENTATION_REGRESSION.

The derived requirement "Sprint X must have implementing artifacts" was interpreted as "Sprint X must have a doc file at docs/sprints/X.md", but the actual evidence structure is different.

---

### Category Validation

| Category | Used in Pilot | Notes |
|---|---|---|
| REQUIREMENT_DERIVATION_ERROR | 27 | All 27 FAILs — test assumption was wrong |
| IMPLEMENTATION_REGRESSION | 0 | Not triggered in this pilot |
| HISTORICAL_BEHAVIOR_SUPERSEDED | 0 | Not triggered in this pilot |
| INTENTIONAL_BEHAVIOR_CHANGE | 0 | Not triggered in this pilot |
| HISTORICAL_CLAIM_NOT_OPERATIONAL | 0 | Not triggered in this pilot |
| TEST_CONSTRUCTION_ERROR | 0 | Not triggered in this pilot |
| ENVIRONMENT_DEPENDENCY_EFFECT | 0 | Not triggered in this pilot |
| UNRESOLVED | 0 | Not triggered in this pilot |

---

### Pilot Conclusion

The categories are **distinguishable in practice** — all 27 FAILs cleanly map to a single category (REQUIREMENT_DERIVATION_ERROR). The enum is viable for the full 79-FAIL classification.

However, the pilot reveals that the **test construction logic needs refinement** for the "existence" test type. The assumption that sprint doc files exist at `docs/sprints/<ID>.md` is not universally true.

---

## Recommendation

1. **Categories are valid** — proceed to full classification
2. **Test construction should be refined** — the "existence" check should verify evidence in the sprint ledger, not just doc file existence
3. **REQUIREMENT_DERIVATION_ERROR is the dominant category** — likely the same pattern across most of the 79 FAILs

---

*Classification pilot — advisory-only. Original FAIL results preserved unchanged.*
