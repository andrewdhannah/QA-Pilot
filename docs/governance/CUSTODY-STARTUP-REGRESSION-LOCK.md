# CUSTODY-STARTUP-REGRESSION-LOCK.md — Custody Startup Regression Lock

**Status:** 🔍 Active (sprint #30)
**Authority:** Read-only regression lock over #23–#29 custody startup chain. Proves startup reports custody posture without gaining, implying, or exercising custody authority.
**Sprint:** CUSTODY-STARTUP-REGRESSION-LOCK-1

---

## 1. Purpose

Lock the full #23–#29 custody startup chain with regression fixtures proving startup can report custody posture across the sealed chain without gaining, implying, or exercising custody authority.

## 2. Coverage

The regression lock covers the complete #23–#29 chain:

| Sprint | Component | Sealed |
|--------|-----------|--------|
| #23 | Write custody enforcement | ✅ |
| #24 | Live custody integration | ✅ |
| #25 | Lifecycle custody extension | ✅ |
| #26 | Owner-decision custody receipts | ✅ |
| #27 | Custody receipt index | ✅ |
| #28 | Custody receipt summary surface | ✅ |
| #29 | Custody surface startup integration | ✅ |

## 3. Locked Invariants

| Rule | Assertion | Type |
|------|-----------|------|
| CRL-1 | Startup must report custody posture from #29 surface (read-only) | Positive |
| CRL-2 | Startup posture is `available` when #29 surface is available | Positive |
| CRL-3 | Startup posture is `degraded`/`unavailable` when #29 surface is missing/empty/failing | Positive |
| CRL-4 | Startup report references sealed contracts #23–#29 by contract ID | Positive |
| CRL-5 | Startup must not create custody receipts in `receipts/owner-decision-custody/` | Negative |
| CRL-6 | Startup must not mutate custody receipt index (`custody-receipt-index.py` persistent state) | Negative |
| CRL-7 | Startup must not mutate summary surface persistent state | Negative |
| CRL-8 | Startup report must have no approve/seal/execute/write controls | Negative |
| CRL-9 | Startup (`start qa-pilot`) must not treat project startup as sprint-start authorization | Positive |
| CRL-10 | Startup must preserve the Owner authorization boundary from GLOBAL-STARTUP-INTENT-AUTHORIZATION-CONTRACT-1 | Positive |
| CRL-11 | Startup must not create cross-project authority (no Librarian paths created/modified) | Negative |
| CRL-12 | Startup custody posture report must be deterministically ordered | Positive |

## 4. Positive Fixtures

| Fixture | Rule | Description |
|---------|------|-------------|
| `posture-available.json` | CRL-1, CRL-2 | Normal operating state: #29 surface ok, report shows available posture with counts |
| `posture-degraded-surface-missing.json` | CRL-3 | #28/#29 surface unavailable, report shows degraded |
| `posture-empty-index.json` | CRL-3 | #27 index empty, report returns zero counts without error |
| `posture-sealed-refs.json` | CRL-4 | Report references all of #23–#29 with correct sealed-contract IDs |
| `posture-no-sprint-auth.json` | CRL-9 | After `start qa-pilot`, pointer file unchanged, no sprint-start receipt created |

## 5. Negative Fixtures

| Fixture | Rule | Description |
|---------|------|-------------|
| `posture-claims-receipt-create.json` | CRL-5 | Startup report claims to have created a custody receipt → rejected |
| `posture-claims-index-mutate.json` | CRL-6 | Startup report claims to have mutated custody index → rejected |
| `posture-claims-surface-mutate.json` | CRL-7 | Startup report claims to have mutated summary surface → rejected |
| `posture-claims-approve-control.json` | CRL-8 | Startup report claims approve=true or seal=true → rejected |
| `posture-claims-write-control.json` | CRL-8 | Startup report claims write=true or execute=true → rejected |
| `posture-claims-cross-project-auth.json` | CRL-11 | Startup report references Librarian runtime paths as authority → rejected |
| `posture-claims-owner-decision-create.json` | CRL-10 | Startup report claims to have created/modified an Owner decision receipt → rejected |

## 6. Testing Strategy

The test runner validates three layers:

1. **Fixture validation**: Each pass/fail fixture is validated against the CRL rules
2. **Live posture check**: `custody-surface-startup-integration.py report` output is checked for read-only posture
3. **External regression**: All sealed #23–#28 runners still pass after lock

## 7. Non-Goals

- No new startup authority of any kind
- No changes to #29 integration script behavior
- No changes to #27 index, #28 surface, or any prior sealed contract
- No changes to startup-contract.json, run-startup-checks.sh, or the generic harness
- No Librarian file modification

## 8. Boundary Invariants

1. Regression lock operates on fixture data + live startup output only
2. Lock does not mutate any receipt, index, surface, or enforcement artifact
3. All CRL rules are deterministically evaluated
4. Invalid fixtures are rejected with clear rule violations
5. All existing SR, PM, and suite validators continue to pass
6. No Librarian files are touched by any lock artifact
