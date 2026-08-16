# ASSURANCE CORPUS v1 — State Record

**Date:** 2026-08-11
**Status:** STRUCTURAL FREEZE SEALED / GOVERNANCE CLASSIFICATION COMPLETE

---

## Corpus States

### State 0: E8-R (Original — DEFECTIVE)

```
ASSURANCE CORPUS v1 — E8-R (DEFECTIVE)
├── STRUCTURAL FREEZE:       SEALED
├── GOVERNANCE CLASSIFICATION: N/A
├── Requirements:            307
├── Artifacts:               307
├── Executions:              307
├── PASS:                    228
├── FAIL:                     79
├── ERROR:                     0
├── Reproducibility:         VERIFIED
├── Execution Logic:         DEFECTIVE (wrong dispatch per test type)
└── Status:                  SUPERSDED by DERIVATION-FIX-2
```

### State 1: Post DERIVATION-FIX-2 (Dispatch Corrected)

```
ASSURANCE CORPUS v1 — POST-FIX-2
├── STRUCTURAL FREEZE:       SEALED
├── GOVERNANCE CLASSIFICATION: COMPLETE
├── Requirements:            307
├── Artifacts:               307
├── Executions:              307
├── PASS:                    280
├── FAIL:                     27
├── ERROR:                     0
├── Reproducibility:         VERIFIED
├── Classification:          ALL 27 = REQUIREMENT_DERIVATION_ERROR
└── Fix Applied:             DERIVATION-FIX-2
```

### State 2: Post DERIVATION-FIX-1 (Existence Check Corrected)

```
ASSURANCE CORPUS v1 — SEALED
├── STRUCTURAL FREEZE:       SEALED
├── GOVERNANCE CLASSIFICATION: COMPLETE
├── Requirements:            307
├── Artifacts:               307
├── Executions:              307
├── PASS:                    307
├── FAIL:                       0
├── ERROR:                       0
├── Reproducibility:         VERIFIED
├── Classification:          N/A (no FAILs)
├── Fix Applied:             DERIVATION-FIX-1 + DERIVATION-FIX-2
└── Note:                    100% structurally expected (see below)
```

---

## Before/After Comparison

| Metric | E8-R (DEFECTIVE) | Post FIX-2 | Post FIX-1 | Delta |
|---|---|---|---|---|
| PASS | 228 | 280 | 307 | +79 |
| FAIL | 79 | 27 | 0 | -79 |

---

## Fix Changelog

### DERIVATION-FIX-2: Per-Type Dispatch Correction

**Scope:** Test execution dispatch now uses test-type-specific logic
**Root cause:** E8-R applied `sprint_doc.exists()` to ALL test types
**Effect:** 79→27 FAILs (52 regression/evidence_verification FAILs removed)

| Test Type | Before (DEFECTIVE) | After (CORRECTED) |
|---|---|---|
| regression | sprint_doc.exists() | harness format check |
| existence | sprint_doc.exists() | sprint doc OR evidence_note OR commit |
| evidence_verification | sprint_doc.exists() | evidence_note exists |

### DERIVATION-FIX-1: Existence Check Recognition

**Scope:** Existence check recognizes evidence_note and commit as valid evidence
**Root cause:** Existence check only recognized docs/sprints/<ID>.md
**Effect:** 27→0 FAILs (all REQUIREMENT_DERIVATION_ERROR resolved)

| Evidence Location | Before | After |
|---|---|---|
| docs/sprints/<ID>.md | ✓ | ✓ |
| evidence_note | ✗ | ✓ |
| commit | ✗ | ✓ |

---

## Why 100% Is Structurally Expected

The 307 requirements were drawn from sprints classified ASSURANCE_READY during historical triage. Part of what made a sprint ASSURANCE_READY was having reconstructable evidence. Once the existence/evidence_verification checks are correctly implemented, they are close to tautologically guaranteed to pass for this corpus — the checks re-confirm the selection criterion rather than independently testing something that could plausibly have gone either way.

**regression** (harness field format) is the one check doing real discriminating work against content rather than presence.

**Honest framing:** "100% pass rate on a corpus pre-filtered for evidence availability, with regression as the substantive check."

---

## Classification Summary

### Pre-Fix Classification (27 FAILs)

| Category | Count | Notes |
|---|---|---|
| REQUIREMENT_DERIVATION_ERROR | 27 | All 27 — existence check too narrow |
| IMPLEMENTATION_REGRESSION | 0 | |
| HISTORICAL_BEHAVIOR_SUPERSEDED | 0 | |
| INTENTIONAL_BEHAVIOR_CHANGE | 0 | |
| HISTORICAL_CLAIM_NOT_OPERATIONAL | 0 | |
| TEST_CONSTRUCTION_ERROR | 0 | |
| ENVIRONMENT_DEPENDENCY_EFFECT | 0 | |
| UNRESOLVED | 0 | |

### Post-Fix Classification (0 FAILs)

No FAILs to classify. All 307 requirements pass with corrected derivation logic.

---

## Provenance

```
E8-R ORIGINAL (DEFECTIVE — wrong dispatch logic)
       ↓
RECONCILIATION (79 vs 27 discrepancy identified)
       ↓
DERIVATION-FIX-2 (per-type dispatch corrected)
       ↓
CLASSIFICATION PILOT (27 FAILs examined)
       ↓
REQUIREMENT_DERIVATION_ERROR identified
       ↓
DERIVATION-FIX-1 (existence check corrected)
       ↓
POST-FIX VERIFICATION (0 FAILs)
       ↓
ASSURANCE CORPUS v1 — SEALED
```

---

## Key Findings

1. **E8-R had a dispatch bug:** applied existence-check to all test types, inflating FAILs from 27 to 79
2. **27 FAILs were REQUIREMENT_DERIVATION_ERROR:** derivation logic predated evidence_note convention
3. **Both bugs fixed, 0 FAILs remain:** corpus is correct
4. **100% is structurally expected:** corpus pre-filtered for evidence availability

---

## Permanent Invariants Preserved

```
FAIL ≠ governance verdict
constructed test ≠ executed test
observed result ≠ governance disposition
structural freeze ≠ semantic freeze
```

Original FAIL results preserved unchanged. Dispositions added as additive layer.

---

## E8-R Disposition

E8-R is marked **DEFECTIVE** (not deleted or superseded). It preserves the pre-fix execution results as evidence of the dispatch bug. This follows the principle: don't overwrite defective results, add corrected layers.

---

*Corpus state record — advisory-only.*
