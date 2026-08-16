# DERIVATION-FIX-2: Per-Type Dispatch Correction

**Date:** 2026-08-11
**Status:** APPLIED
**Change Type:** Bug fix in test execution dispatch logic

---

## Change

The test execution dispatch was corrected to use test-type-specific logic instead of applying the existence-check to all test types.

### Before (Defective)

```python
# E8-R: Same check for ALL test types
elif adapter == "cli":
    source_sprint = artifact.get("source_sprint", "")
    sprint_doc = LIBRARIAN_ROOT / "docs" / "sprints" / f"{source_sprint}.md"
    if sprint_doc.exists():
        return "PASS", "Sprint doc exists"
    else:
        return "FAIL", "Sprint doc not found"
```

### After (Corrected)

```python
# Classification pilot: test-type-specific logic
elif adapter == "cli":
    if test_type == "regression":
        # Check harness field format
        harness = sprint_data.get("harness", "")
        if harness and "/" in harness:
            parts = harness.split("/")
            total = int(parts[1].split()[0])
            if total > 0:
                return "PASS", f"Harness claims {total} tests"
        return "FAIL", "No valid harness format"

    elif test_type == "existence":
        # Check multiple evidence locations
        if has_sprint_doc or has_evidence_note or has_commit:
            return "PASS", "Authoritative evidence exists"
        else:
            return "FAIL", "No authoritative evidence"

    elif test_type == "evidence_verification":
        # Check evidence_note field
        if has_evidence_note:
            return "PASS", "Evidence note exists"
        else:
            return "FAIL", "No evidence note"
```

---

## Reason

The E8-R script applied `sprint_doc.exists()` to ALL test types (regression, existence, evidence_verification). This caused:

- **regression tests** to FAIL when sprint docs didn't exist (even though regression checks harness format, not doc existence)
- **evidence_verification tests** to FAIL when sprint docs didn't exist (even though evidence_verification checks evidence_note, not doc existence)

Only **existence tests** should check for sprint doc/evidence_note/commit.

---

## Effect

| Metric | Before (E8-R) | After (Classification Pilot) | Delta |
|---|---|---|---|
| PASS | 228 | 280 | +52 |
| FAIL | 79 | 27 | -52 |

The 52 FAILs that "disappeared" were regression and evidence_verification tests that were incorrectly classified as FAIL due to wrong dispatch logic.

---

## Relationship to DERIVATION-FIX-1

| Fix | Scope | Effect |
|---|---|---|
| DERIVATION-FIX-1 | Existence check recognizes evidence_note and commit | 27→0 FAILs |
| DERIVATION-FIX-2 | Per-type dispatch uses correct check per test type | 79→27 FAILs |

These are **separate bugs** with separate root causes:
- FIX-1: Existence check was too narrow (only checked doc file)
- FIX-2: Dispatch logic applied wrong check to wrong test types

---

## Changelog Entry

```
DERIVATION-FIX-2
Change: test execution dispatch now uses test-type-specific logic
        (regression→harness format, existence→evidence locations,
        evidence_verification→evidence_note)
Reason: E8-R applied sprint_doc.exists() to ALL test types,
        causing 52 regression/evidence_verification FAILs
Effect: 79 FAILs reduced to 27 (only existence test type remains)
Date:   2026-08-11
```

---

*Fix applied as governed change. E8-R corpus preserved as pre-fix evidence.*
