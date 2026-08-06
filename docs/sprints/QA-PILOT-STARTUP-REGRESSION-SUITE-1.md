# QA-PILOT-STARTUP-REGRESSION-SUITE-1 — Sprint Receipt

**Sprint ID:** QA-PILOT-STARTUP-REGRESSION-SUITE-1
**Type:** Validation / regression suite
**Lane:** parallel_planning
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Input dependencies:** QA-PILOT-STARTUP-PARITY-GAP-CLOSURE-1 (ledger #21), QA-PILOT-STARTUP-LIBRARIAN-PARITY-MATRIX-1 (ledger #20)

## Scope Satisfied

Created a startup regression suite that proves the restored QA Pilot startup chain stays managed across all recent repairs.

### Regression Validator (15 rules)

| Rule | Dimension | Status |
|------|-----------|--------|
| SR-1 | Selector resolution — QA Pilot in project-index | ✅ |
| SR-2 | Pointer file points to qa-pilot | ✅ |
| SR-3 | Startup contract parses with required fields | ✅ |
| SR-3b | Parity blocks present (mcp_context, operational_state, fallback_docs) | ✅ |
| SR-4 | All required files exist on disk | ✅ |
| SR-5 | Startup checks report managed mode | ✅ |
| SR-6 | MCP health check exits 0, 8/8 tools | ✅ |
| SR-7 | Parity matrix validator passes 13/13 | ✅ |
| SR-8 | All 15 existing validators pass (zero regression) | ✅ |
| SR-9 | MCP context tools responsive (4 project_* tools) | ✅ |
| SR-10 | No Librarian file references in regression scripts | ✅ |
| SR-11 | Sprint ledger parseable, ≥20 sealed entries | ✅ |
| SR-12 | Status surfaces exist | ✅ |
| SR-13 | project_id consistent across all identity sources | ✅ |

### Artifacts Created

| File | Purpose |
|------|---------|
| `docs/governance/QA-PILOT-STARTUP-REGRESSION.md` | Governance doc (7 sections, 5 invariants) |
| `scripts/validate-qa-pilot-startup-regression.py` | Regression validator (15 rules SR-1 through SR-13) |
| `scripts/test-qa-pilot-startup-regression.sh` | Test runner (orchestrates validator) |
| `docs/examples/qa-pilot-startup-regression/regression-valid-chain.json` | Baseline fixture — all rules expected to pass |
| `docs/sprints/QA-PILOT-STARTUP-REGRESSION-SUITE-1.md` | Sprint receipt |

### Validation Results

| Suite | Rules | Result |
|-------|-------|--------|
| Startup regression | 15 SR | 15/15 pass ✅ |
| Parity matrix | 13 PM | 13/13 pass ✅ |
| Existing validators | 14 | 14/14 pass ✅ |
| **Total** | **42** | **42/42 pass** ✅ |

## Hard Boundaries Enforced

- ❌ No Librarian file mutation
- ❌ No cross-project writes
- ❌ No modification to sealed sprint ledger entries
- ❌ No startup contract modification
- ❌ No sealed evidence mutation

## Acceptance Gate Met

```
QA Pilot startup: managed ✅
Selector: resolved ✅
MCP: reachable ✅
Parity: complete ✅
Validators: green ✅
```

## Next

Owner review and seal. After seal, the alternative next sprint in the queue is `PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT-1` or Owner direction.
