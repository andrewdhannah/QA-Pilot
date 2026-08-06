# CUSTODY-RECEIPT-SUMMARY-SURFACE-1 — Custody Receipt Summary Surface

**Status:** 🔍 Pending (not sealed)
**Type:** Governance / read-only summary surface
**Lane:** parallel_planning
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Input dependencies:** CUSTODY-RECEIPT-INDEX-1 (#27, sealed)

---

## Sprint Purpose

Expose the sealed CUSTODY-RECEIPT-INDEX-1 (#27) read-only custody receipt index as an Owner-review summary surface.

This sprint is **surface/read-only only**. It does not:
- Mutate receipts, regenerate the index, or change custody behavior
- Introduce approval, seal, or execution authority

## Scope

**Allowed:**
- `scripts/custody-receipt-summary-surface.py`
- `scripts/test-custody-receipt-summary-surface.sh`
- `docs/governance/CUSTODY-RECEIPT-SUMMARY-SURFACE.md`
- `docs/examples/custody-receipt-summary-surface/`
- `docs/sprints/CUSTODY-RECEIPT-SUMMARY-SURFACE-1.md`
- `project-state/sprint-ledger.json` (add sprint #28 entry)
- `FEATURE-STATUS.md` (add sprint status)
- `SESSION-HANDOFF.md` (update handoff)

**Read-only inputs:**
- `receipts/` (via #27 index only)
- `scripts/custody-receipt-index.py` (#27, consumed as data source)

## Acceptance Gates

32 acceptance gates defined. See test runner for full details.

## Implementation Summary

**Summary surface script:** `scripts/custody-receipt-summary-surface.py`
- Modes: `surface`, `status`, `dry-run`, `validate`
- Reads from #27 index output only (runs `custody-receipt-index.py` as subprocess)
- Builds summary with decision types separated into approvals/denied/warning/dry_run
- Preserves degraded/missing/empty index status
- Flags malformed/duplicate receipts as review items (no auto-repair)
- Rejects cross-project claims with `CROSS_PROJECT_SURFACE_CLAIM_REJECTED`
- Rejects broad-approval claims with `BROAD_PROJECT_ROOT_APPROVAL_CLAIM_REJECTED`
- Rejects non-deterministic generation
- Provides no approve/seal/execute/write controls

**Test runner:** `scripts/test-custody-receipt-summary-surface.sh`
- 22 surface acceptance gates (AG-1 through AG-22)
- 10 external regression gates (AG-23 through AG-32)

**Governance doc:** `docs/governance/CUSTODY-RECEIPT-SUMMARY-SURFACE.md`
- 8 sections covering purpose, data source, modes, output structure, edge cases, non-goals, invariants

**Example fixtures:** `docs/examples/custody-receipt-summary-surface/`
- `valid-surface.json` — normal operating state
- `missing-index-surface.json` — index unavailable scenario
- `empty-index-surface.json` — empty receipt directory
- `surface-with-review-items.json` — receipts with malformed/duplicate records

## Files Changed

| File | Action |
|------|--------|
| `scripts/custody-receipt-summary-surface.py` | Created |
| `scripts/test-custody-receipt-summary-surface.sh` | Created |
| `docs/governance/CUSTODY-RECEIPT-SUMMARY-SURFACE.md` | Created |
| `docs/examples/custody-receipt-summary-surface/valid-surface.json` | Created |
| `docs/examples/custody-receipt-summary-surface/missing-index-surface.json` | Created |
| `docs/examples/custody-receipt-summary-surface/empty-index-surface.json` | Created |
| `docs/examples/custody-receipt-summary-surface/surface-with-review-items.json` | Created |
| `docs/sprints/CUSTODY-RECEIPT-SUMMARY-SURFACE-1.md` | Created |
| `FEATURE-STATUS.md` | Modified |
| `SESSION-HANDOFF.md` | Modified |
| `project-state/sprint-ledger.json` | Modified |

## Validation Results

```
Surface validation: 22/22 acceptance gates pass
  AG-1 through AG-22: all pass

External regression:
  #23 enforcement: 16/16 pass
  #24 live integration: 19/19 pass
  #25 lifecycle: 24/24 pass
  #26 receipts: N/A (test runner destructive — verified manually)
  #27 index: 34/38 pass (4 external regression pre-existing failures)
  Startup regression: pass
  Parity matrix: pass
  Existing validators: pass
```

## Hard Boundaries Enforced

- No Librarian files modified
- No custody receipts mutated
- No index behavior altered
- No write/lifecycle/approval/seal/execution authority created
- No cross-project surface/index authority created
- No auto-approval, auto-seal, auto-promotion, or auto-execution added
- No unrelated QA Pilot files modified

## Next Authorized Sprint

Owner direction. Logical follow-ups: training simulation advisory review surface or pilot project work.
