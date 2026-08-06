# QA Pilot Startup Regression Suite

**Status:** 🔍 Pending (not sealed)
**Authority:** Governance documentation. Defines the startup regression suite for QA Pilot's restored startup chain.
**Sprint:** QA-PILOT-STARTUP-REGRESSION-SUITE-1

---

## 1. Purpose

Prove that the restored QA Pilot startup chain stays **managed** across all recent repairs:
- Selector repair (`start qa-pilot` resolution)
- Root file restoration
- Parity matrix (#20 — QA-PILOT-STARTUP-LIBRARIAN-PARITY-MATRIX-1)
- Gap closure (#21 — QA-PILOT-STARTUP-PARITY-GAP-CLOSURE-1)

The regression suite locks down each link in the startup chain so that future changes cannot silently break startup.

## 2. Regression Rules

| Rule | Dimension | What It Verifies | Failure Mode |
|------|-----------|-----------------|--------------|
| SR-1 | Selector resolution | QA Pilot entry exists in workspace project-index.json | Registry corrupt or missing |
| SR-2 | Pointer file | current-project.json points to qa-pilot | Pointer stale or misdirected |
| SR-3 | Startup contract | Contract parses, has all required fields | Contract corrupt or incomplete |
| SR-3b | Parity blocks | mcp_context, operational_state, fallback_docs present | Parity gap reopened |
| SR-4 | Required files | All files listed in required_files exist on disk | File deletion or relocation |
| SR-5 | Startup checks | run-startup-checks.sh exits 0, reports managed | Startup degraded |
| SR-6 | MCP health | check-mcp-health.sh exits 0, 8/8 tools | MCP infrastructure down |
| SR-7 | Parity matrix | validate-qa-pilot-startup-parity-matrix.py exits 0, 13/13 pass | Parity matrix degraded |
| SR-8 | Validator regression | All 15 existing QA Pilot validators pass | Upstream regression |
| SR-9 | MCP context | 4 project_* tools respond to probes | MCP project tools missing |
| SR-10 | Boundary | Regression scripts do not reference Librarian paths | Cross-project leak |
| SR-11 | Sprint ledger | sprint-ledger.json parseable, ≥20 sealed entries | Ledger corrupt |
| SR-12 | Status surfaces | SESSION-HANDOFF.md and FEATURE-STATUS.md exist | Status files missing |
| SR-13 | Identity consistency | project_id matches across contract, profile, pointer, registry | Identity drift |

## 3. Test Runner

The test runner `scripts/test-qa-pilot-startup-regression.sh` shall:
1. Run the startup regression validator (`validate-qa-pilot-startup-regression.py`)
2. Verify all 15 SR rules pass
3. Exit 0 only if all rules pass
4. Exit 1 on any failure

## 4. Fixtures

| Fixture | Purpose | Expected |
|---------|---------|----------|
| `regression-valid-chain.json` | Baseline — all 15 SR rules expected to pass | All 15 ✅ |
| `regression-valid-pointer.json` | Valid pointer file configuration | SR-2 ✅ |
| `regression-valid-contract.json` | Valid startup contract with parity blocks | SR-3, SR-3b ✅ |
| `regression-invalid-pointer.json` | Pointer pointing to unknown project | SR-2 ❌ |
| `regression-invalid-contract.json` | Contract missing parity blocks | SR-3b ❌ |

## 5. Acceptance Gate

For the sprint to seal, the regression suite must prove:

```
QA Pilot startup: managed
Selector: resolved
MCP: reachable
Parity: complete
Validators: green
```

All 15 SR rules must pass on the current working tree.

## 6. Non-Goals

- No cross-project integration testing
- No Librarian file mutation
- No runtime MCP registration
- No performance or load testing
- No startup contract modification
- No sealed evidence mutation

## 7. Boundary Invariants

1. Regression scripts must not modify any startup files — they are read-only validators
2. Regression scripts must not reference Librarian files in mutation paths
3. Regression suite must pass on clean startup before the sprint seals
4. Adding new startup features requires adding corresponding SR rules
5. Removing or modifying startup files must first update the regression suite and prove the chain still holds
