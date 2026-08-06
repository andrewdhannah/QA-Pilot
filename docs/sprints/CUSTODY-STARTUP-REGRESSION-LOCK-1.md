# CUSTODY-STARTUP-REGRESSION-LOCK-1 — Custody Startup Regression Lock

**Status:** ✅ Sealed (ledger #30, Owner-approved 2026-07-06 per OD-CUSTODY-STARTUP-REGRESSION-LOCK-1-SEAL)
**Type:** Governance / regression lock
**Lane:** parallel_planning
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Input dependencies:** CUSTODY-SURFACE-STARTUP-INTEGRATION-1 (#29, sealed)

---

## Sprint Purpose

Lock the full #23–#29 custody startup chain with regression fixtures proving startup can report custody posture without gaining, implying, or exercising custody authority.

## Scope

**Allowed:**
- `docs/governance/CUSTODY-STARTUP-REGRESSION-LOCK.md`
- `scripts/validate-custody-startup-regression-lock.py`
- `scripts/test-custody-startup-regression-lock.sh`
- `docs/examples/custody-startup-regression-lock/` (11 fixtures)
- `docs/sprints/CUSTODY-STARTUP-REGRESSION-LOCK-1.md`
- `project-state/sprint-ledger.json` (add sprint #30 entry)
- `FEATURE-STATUS.md` (add sprint status)
- `SESSION-HANDOFF.md` (update handoff)

**Nothing else.** No changes to #23–#29 sealed contracts, no startup-contract.json changes, no generic harness changes, no Librarian files.

## Rules Covered (12 CRL rules)

| Rule | Assertion | Type |
|------|-----------|------|
| CRL-1 | Startup reports custody posture from #29 surface (read-only) | Positive |
| CRL-2 | Posture `available` when #29 surface is available | Positive |
| CRL-3 | Posture `degraded`/`unavailable` when surface missing/empty | Positive |
| CRL-4 | Report references sealed contracts #23–#29 | Positive |
| CRL-5 | No custody receipt creation during startup reporting | Negative |
| CRL-6 | No custody index mutation during startup reporting | Negative |
| CRL-7 | No summary surface mutation during startup reporting | Negative |
| CRL-8 | No approve/seal/execute/write controls in startup report | Negative |
| CRL-9 | `start qa-pilot` does not create sprint-start authorization | Positive |
| CRL-10 | Startup preserves Owner authorization boundary | Positive |
| CRL-11 | No cross-project (Librarian) authority created during startup | Negative |
| CRL-12 | Startup custody posture output is deterministically ordered | Positive |

## Fixtures

**4 positive fixtures (all pass CRL rules):**
- `posture-available.json` — normal operating state
- `posture-degraded-surface-missing.json` — surface unavailable
- `posture-empty-index.json` — empty index, zero counts
- `posture-sealed-refs.json` — all #23–#29 referenced with contract names

**7 negative fixtures (all correctly rejected):**
- `posture-claims-receipt-create.json` — CRL-5 violation
- `posture-claims-index-mutate.json` — CRL-6 violation
- `posture-claims-surface-mutate.json` — CRL-7 violation
- `posture-claims-approve-control.json` — CRL-8 violation
- `posture-claims-write-control.json` — CRL-8 violation
- `posture-claims-cross-project-auth.json` — CRL-11 violation
- `posture-claims-owner-decision-create.json` — CRL-10 violation

## Test Results

```
Test suite: 28/28 pass, 0 failed

Group 1 — Fixture validation:    11/11 pass (4 positive + 7 negative)
Group 2 — Live posture check:     7/7  pass (CRL-1,2,4,5,9,10,11 live)
Group 3 — External regression:   10/10 pass (AG-1 through AG-10)

External regression verified:
  #23 enforcement: 16/16  |  #24 live: 19/19
  #25 lifecycle: 24/24    |  #26 receipts: 36/36
  #27 index: 38/38        |  #28 surface: 32/32
  #29 integration: 23/23  |  Startup regression: 15/15
  Parity matrix: 13/13    |  Existing validators: 15/15
```

## Hard Boundaries Enforced

- No Librarian files modified
- No custody receipts mutated
- No #27 index or #28/#29 surface behavior altered
- No startup-contract.json or generic harness changes
- No approval/seal/execute/write authority created
- No cross-project authority created
- No sprint-start authority implied by startup

## Next

Owner direction. No sprint is authorized after #30.
