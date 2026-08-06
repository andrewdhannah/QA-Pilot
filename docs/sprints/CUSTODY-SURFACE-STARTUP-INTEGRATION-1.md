# CUSTODY-SURFACE-STARTUP-INTEGRATION-1 — Startup Custody Posture Integration

**Status:** 🔍 Pending (not sealed)
**Type:** Governance / startup reporting integration
**Lane:** parallel_planning
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Input dependencies:** CUSTODY-RECEIPT-SUMMARY-SURFACE-1 (#28, sealed)

---

## Sprint Purpose

Include the sealed CUSTODY-RECEIPT-SUMMARY-SURFACE-1 (#28) read-only custody summary surface in QA Pilot startup reporting. Startup can now report custody posture, degraded states, and review items without creating startup authority or mutation behavior.

This sprint is **startup reporting integration only**. It does not:
- Mutate, regenerate, or repair receipts
- Alter #27 index behavior or #28 surface semantics
- Create startup, approval, seal, write, lifecycle, receipt, index, or execution authority
- Create cross-project startup authority

## Scope

**Allowed:**
- `scripts/custody-surface-startup-integration.py`
- `scripts/run-startup-checks.sh` (add Custody Posture section)
- `scripts/test-custody-surface-startup-integration.sh`
- `docs/governance/CUSTODY-SURFACE-STARTUP-INTEGRATION.md`
- `docs/examples/custody-surface-startup-integration/`
- `docs/sprints/CUSTODY-SURFACE-STARTUP-INTEGRATION-1.md`
- `project-state/sprint-ledger.json` (add sprint #29 entry)
- `FEATURE-STATUS.md` (add sprint status)
- `SESSION-HANDOFF.md` (update handoff)

**Read-only inputs:**
- `receipts/` (via #28 surface only)
- `scripts/custody-receipt-index.py` (#27, via #28)
- `scripts/custody-receipt-summary-surface.py` (#28, consumed as data source)

## Acceptance Gates

34 acceptance gates defined. See test runner for full details.

## Implementation Summary

**Integration script:** `scripts/custody-surface-startup-integration.py`
- Modes: `report`, `status`, `dry-run`, `validate`
- Output formats: `json` (default), `markdown` (for STARTUP-STATE.md)
- Reads from #28 summary surface output only (subprocess call)
- Builds custody posture report with source counts, decision types, violations, mutation status, approval provenance, sealed-contract references #23–#28
- Preserves degraded/missing/empty/unavailable surface status
- Flags malformed/duplicate receipts as review items (no auto-repair)
- Rejects cross-project claims with `CROSS_PROJECT_STARTUP_CLAIM_REJECTED`
- Rejects broad-approval claims with `BROAD_PROJECT_ROOT_APPROVAL_CLAIM`
- Rejects non-deterministic generation
- Provides no approve/seal/execute/write controls

**Startup checks integration:** `scripts/run-startup-checks.sh`
- Calls integration script at startup
- Includes Custody Posture section in STARTUP-STATE.md
- Graceful failure: if script missing, shows unavailable with no startup halt

**Test runner:** `scripts/test-custody-surface-startup-integration.sh`
- 23 integration acceptance gates (AG-1 through AG-23)
- 11 external regression gates (AG-24 through AG-34)

**Governance doc:** `docs/governance/CUSTODY-SURFACE-STARTUP-INTEGRATION.md`
- 8 sections covering purpose, data source, modes, flow, output, edge cases, non-goals, invariants

**Example fixtures:** `docs/examples/custody-surface-startup-integration/`
- `valid-integration-report.json` — normal operating state
- `degraded-surface-report.json` — surface unavailable scenario
- `report-with-review-items.json` — report with malformed/duplicate records

## Files Changed

| File | Action |
|------|--------|
| `scripts/custody-surface-startup-integration.py` | Created |
| `scripts/run-startup-checks.sh` | Modified (add Custody Posture section) |
| `scripts/test-custody-surface-startup-integration.sh` | Created |
| `docs/governance/CUSTODY-SURFACE-STARTUP-INTEGRATION.md` | Created |
| `docs/examples/custody-surface-startup-integration/valid-integration-report.json` | Created |
| `docs/examples/custody-surface-startup-integration/degraded-surface-report.json` | Created |
| `docs/examples/custody-surface-startup-integration/report-with-review-items.json` | Created |
| `docs/sprints/CUSTODY-SURFACE-STARTUP-INTEGRATION-1.md` | Created |
| `FEATURE-STATUS.md` | Modified |
| `SESSION-HANDOFF.md` | Modified |
| `project-state/sprint-ledger.json` | Modified |

## Validation Results

```
Integration validation: 23/23 acceptance gates pass
  AG-1 through AG-23: all pass
Startup checks: managed mode, custody posture included

External regression:
  #23 enforcement: 16/16 pass
  #24 live integration: 19/19 pass
  #25 lifecycle: 24/24 pass
  #26 receipts: 36/36 pass
  #27 index: 38/38 pass
  #28 surface: 22/22 pass
  Startup regression: pass
  Parity matrix: pass
  Existing validators: pass
```

## Hard Boundaries Enforced

- No Librarian files modified
- No custody receipts mutated
- No index behavior altered (#27)
- No surface behavior altered (#28)
- No startup authority created
- No write/lifecycle/approval/seal/execution authority created
- No cross-project startup/surface/index authority created
- No auto-approval, auto-seal, auto-promotion, or auto-execution added
- No unrelated QA Pilot files modified

## Next Authorized Sprint

Owner direction.
