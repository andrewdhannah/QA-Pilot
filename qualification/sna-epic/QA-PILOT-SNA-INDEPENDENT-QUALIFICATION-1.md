# QA-PILOT-SNA-INDEPENDENT-QUALIFICATION-1 — Sprint Receipt

**Sprint ID:** QA-PILOT-SNA-INDEPENDENT-QUALIFICATION-1
**Project:** QA Pilot
**Date:** 2026-08-15
**Status:** 🔍 Pending Owner review
**Authority:** advisory-only, QA Pilot-local

---

## Purpose

Independent qualification of the EPIC-SPRINT-NUMBER-ALLOCATION-GOVERNANCE-1 epic.
QA-Pilot derives tests from the **epic contract**, not from the SNA implementation.

This sprint does NOT re-run SNA-1 through SNA-9 tests. It independently verifies
the customer invariant from outside the implementation's own test architecture.

## Contract Under Test

**Epic Invariant:**
> Given any supported Librarian workflow capable of creating, importing, restoring,
> cloning, recovering, building, or sealing a sprint, the system mechanically
> prevents that workflow from producing a live sprint whose number was not
> atomically reserved and bound to that sprint.

**6 Contract Invariants:**
1. A sprint number must be atomically reserved before a sprint becomes buildable
2. No production path may assign a sprint number through an alternate mechanism
3. Reservation must bind to specific sprint identity
4. Seal requires valid reservation, commit binding, and evidence gates
5. Persistence layer enforces uniqueness independently of application routing
6. Import/restore distinguishes historical preservation from new allocation

## Qualification Structure

| Layer | Question | Tests | Passed | Failed |
|-------|----------|-------|--------|--------|
| 1. Contract | Does the invariant have unambiguous acceptance criteria? | 9 | 9 | 0 |
| 2. Workflow | Can every supported lifecycle path be exercised? | 6 | 6 | 0 |
| 3. Negative | Can any forbidden state be produced? | 8 | 8 | 0 |
| 4. Concurrency | Can races defeat reservation/binding? | 3 | 3 | 0 |
| 5. Persistence | Can restart/mutation/recovery bypass controls? | 5 | 4 | 1 |
| 6. Interface | Can MCP/API/CLI paths bypass the allocator? | 5 | 5 | 0 |
| 7. Exceptional | Can import/restore/clone/recovery create a violation? | 6 | 6 | 0 |
| 8. Evidence | Can QA-Pilot independently prove the observed result? | 10 | 10 | 0 |
| 9. Regression | Does the entire existing test suite remain clean? | 6 | 6 | 0 |
| Critical Adversarial | Fabricate violation without allocator | 6 | 6 | 0 |
| Positive Workflow | Legitimate paths still work | 4 | 4 | 0 |
| **TOTAL** | | **68** | **67** | **1** |

## Finding: P-003 — Corrupt JSON Crash

**Severity:** medium
**Layer:** persistence
**Test:** P-003 — Corrupt JSON: allocator crashes on corrupt store

**Description:**
The `NumberReservationStore._atomic_update()` method reads raw bytes from the
store file and calls `json.loads()` without error handling. If the store file
becomes corrupted (disk error, partial write, etc.), the allocator crashes with
`JSONDecodeError` instead of recovering gracefully.

The `_load()` method (used by non-atomic reads) correctly catches `JSONDecodeError`
and returns empty state. The `_atomic_update()` method (used by all mutations)
does not have this protection.

**Impact:** Storage corruption causes allocator failure. This is a robustness issue,
not an invariant violation. The customer invariant remains enforced — the allocator
rejects invalid states; it just doesn't survive file corruption gracefully.

**Classification:** Robustness finding, not an invariant violation.

**Recommendation:** Add `try/except (json.JSONDecodeError, OSError)` around the
`json.loads(raw)` call in `_atomic_update()` to match the resilience of `_load()`.

## Critical Adversarial Results

| Scenario | Result | Detail |
|----------|--------|--------|
| CRIT-001: Fabricated number → build | REJECTED | can_build correctly rejects unreserved number |
| CRIT-002: Injected reservation → seal | CORRECT | Seal gate validates state; security boundary = file access control |
| CRIT-003: Gate bypass attempt | NO BYPASS | create_sprint always calls reserve internally |
| CRIT-004: Tampered sprint_id | DETECTED | Binding verifier detects mismatch |
| CRIT-005: Mismatched commit binding | REJECTED | Seal gate rejects binding mismatch |
| CRIT-006: Two gates, same number | ONE WINNER | Allocator enforces uniqueness under contention |

**Conclusion:** There is no supported path through which a fabricated identity
becomes a live governed sprint. The security boundary is file-level access control
to the reservation store.

## Positive Workflow Results

| Scenario | Result |
|----------|--------|
| POS-001: Full lifecycle (reserve → bind → build → commit → seal) | PASS |
| POS-002: Historical restore preserves identity | PASS |
| POS-003: Clone-as-new creates new reservation | PASS |
| POS-004: Multiple sprints coexist | PASS |

**Conclusion:** The invariant enforcement does not break legitimate workflows.

## Cross-System Evidence Summary

```
SNA internal qualification:
  SNA-1 through SNA-8: all sealed
  SNA-9: surface re-audit complete
  0 production bypasses remaining

SNA-8 adversarial qualification:
  36/36 adversarial tests pass
  0 invariant violations under attack

QA-Pilot independent qualification:
  67/68 tests pass
  1 medium finding (corrupt JSON robustness — not invariant violation)
  0 invariant violations
  0 bypass paths discovered

Cross-system conclusion:
  PASS — customer invariant enforced
  The single finding (P-003) is a robustness issue, not an invariant violation.
  The system mechanically prevents producing a live sprint whose number was not
  atomically reserved and bound to that sprint.
```

## Disposition

**Recommendation:** Owner review. The single finding (P-003) is a robustness
improvement, not a blocker for the epic seal. The customer invariant is
independently corroborated by QA-Pilot from outside the SNA test architecture.

## Files

- **Test suite:** `qualification/sna-epic/qa-pilot-sna-independent-qualification.py`
- **Evidence artifact:** `qualification/sna-epic/evidence/QA-PILOT-SNA-INDEPENDENT-QUALIFICATION-1-evidence.json`
- **This receipt:** `qualification/sna-epic/QA-PILOT-SNA-INDEPENDENT-QUALIFICATION-1.md`
