# Reconciliation Record — 79 vs 27 FAIL Discrepancy

**Date:** 2026-08-11
**Status:** RECONCILED

---

## The Discrepancy

| Source | PASS | FAIL | Total |
|---|---|---|---|
| E8-R (original) | 228 | 79 | 307 |
| Classification pilot (pre-fix) | 280 | 27 | 307 |
| Classification pilot (post-fix) | 307 | 0 | 307 |

**52 FAILs disappeared between E8-R and the classification pilot.**

---

## Root Cause: Different Execution Logic

### E8-R Script (Defective)

The E8-R script used a **single execution path** for all test types:

```python
elif adapter == "cli":
    source_sprint = artifact.get("source_sprint", "")
    sprint_doc = LIBRARIAN_ROOT / "docs" / "sprints" / f"{source_sprint}.md"
    if sprint_doc.exists():
        return "PASS", "Sprint doc exists"
    else:
        return "FAIL", "Sprint doc not found"
```

This checked `sprint_doc.exists()` for **ALL test types** (regression, existence, evidence_verification). Any test where the sprint doc didn't exist was classified as FAIL, regardless of the actual test type.

### Classification Pilot Script (Correct)

The classification pilot uses **test-type-specific logic**:

| Test Type | Check | Correct? |
|---|---|---|
| regression | `harness` field contains "pass/total" format | ✓ Yes |
| existence | sprint doc OR evidence_note OR commit | ✓ Yes |
| evidence_verification | `evidence_note` field exists | ✓ Yes |

---

## Where the 52 FAILs Went

The 52 FAILs that "disappeared" were:

| Test Type | E8-R Result | Classification Pilot Result | Reason |
|---|---|---|---|
| regression (63 total) | Some FAIL | All PASS | E8-R checked sprint_doc.exists() instead of harness format |
| evidence_verification (122 total) | Some FAIL | All PASS | E8-R checked sprint_doc.exists() instead of evidence_note |
| existence (122 total) | 27 FAIL | 27 FAIL (pre-fix) | Correctly identified by both |

**E2E-8/E8-R had a bug:** it applied the existence-check logic to ALL test types, not just the existence test type. This inflated the FAIL count from 27 to 79.

---

## Stress Test: has_commit Condition

**Question:** Does `has_commit` make the existence check too permissive?

**Test:** Check if any ASSURANCE_READY sprints would PASS with has_commit but shouldn't.

**Result:** 0 sprints would be affected. All ASSURANCE_READY sprints already have either a sprint doc or an evidence_note. The `has_commit` condition does not add any new PASSes.

**Conclusion:** The OR condition is not too permissive.

---

## Verified Numbers

| Metric | Value | Source |
|---|---|---|
| ASSURANCE_READY sprints | 122 | Sprint ledger classification |
| Sprints with valid harness format | 63 | E2E-8 derive_test_requirements |
| Sprints with invalid harness format | 50 | E2E-8 derive_test_requirements |
| Sprints with no harness | 9 | E2E-8 derive_test_requirements |
| regression requirements | 63 | From 63 sprints with valid harness |
| existence requirements | 122 | From all 122 sprints |
| evidence_verification requirements | 122 | From all 122 sprints |
| **Total requirements** | **307** | 63 + 122 + 122 |

---

## Conclusion

The 79 FAILs in E2E-8/E8-R were inflated by a bug in the execution logic. The correct FAIL count (with test-type-specific logic) is 27. After DERIVATION-FIX-1, the correct count is 0.

The E2E-8/E8-R corpus should be marked as **defective** due to this bug. The classification pilot corpus is the correct baseline.

---

## Action Items

1. ~~Reconcile 79 vs 27~~ — DONE
2. ~~Stress-test has_commit~~ — DONE (not too permissive)
3. Mark E2E-8/E8-R execution as DEFECTIVE (wrong test logic)
4. Use classification pilot results as correct baseline
5. Document this as a DERIVATION-FIX-2 (execution logic fix)

---

*Reconciliation record — advisory-only.*
