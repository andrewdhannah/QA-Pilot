# CUSTODY-SURFACE-STARTUP-INTEGRATION.md — Startup Custody Posture Integration

**Status:** 🔍 Pending (not sealed)
**Authority:** Read-only startup reporting integration over #28 summary surface. Does not mutate receipts, index, surface, custody behavior, or enforcement.
**Sprint:** CUSTODY-SURFACE-STARTUP-INTEGRATION-1

---

## 1. Purpose

Include the sealed CUSTODY-RECEIPT-SUMMARY-SURFACE-1 (#28) read-only custody summary surface in QA Pilot startup reporting so startup can report custody posture, degraded states, and review items without creating startup authority or mutation behavior.

## 2. Data Source

The startup integration reads **exclusively** from the #28 `custody-receipt-summary-surface.py` output. It does not read receipts directly. This ensures clean architectural layering:

```
Receipts (#26) → Index (#27) → Summary Surface (#28) → Startup Integration (this sprint)
```

| Layer | Component | Sprint |
|-------|-----------|--------|
| Receipt storage | `receipts/owner-decision-custody/` | #26 |
| Read-only index | `custody-receipt-index.py` | #27 |
| Summary surface | `custody-receipt-summary-surface.py` | #28 |
| Startup integration | `custody-surface-startup-integration.py` | **this** |

## 3. Modes

| Mode | Description |
|------|-------------|
| `report` | Generate the full custody posture report for startup (default) |
| `status` | Quick status check — surface status, receipt count, posture |
| `dry-run` | Validate inputs without full output |
| `validate` | Run acceptance gate validation against generated report |

Output can be `json` (default) or `markdown` (for STARTUP-STATE.md inclusion).

## 4. Startup Integration Flow

The `run-startup-checks.sh` script calls the integration at startup:

```
run-startup-checks.sh
  ├─ ... standard startup checks ...
  ├─ custody-surface-startup-integration.py report --format markdown
  └─ writes Custody Posture section to STARTUP-STATE.md
```

The integration is **optional** — if the script is missing or fails, STARTUP-STATE.md shows `**Custody surface:** unavailable` with no startup failure.

## 5. Report Output

```json
{
  "report_metadata": {
    "schema": "custody-surface-startup-integration-v1",
    "deterministic": true,
    "surface_status": "ok|missing|empty|unavailable",
    "report_type": "startup_custody_posture"
  },
  "custody_posture": {
    "available": true,
    "status": "available|degraded|unavailable",
    "detail": "12 custody receipts indexed",
    "total_receipts_in_index": 12
  },
  "summary": {
    "by_custody_source": {"write": 7, "live": 2, "lifecycle": 3},
    "by_decision_type": {"approvals": 10, "denied": 2, "warning": 0, "dry_run": 0},
    "by_violation_code": {"WRITE_SCOPE_VIOLATION": 2},
    "by_mutation_status": {"blocked": 2, "mutated": 10},
    "by_approval_provenance": {"owner_approval_present": 2, "owner_approval_absent": 10},
    "by_sprint": {...},
    "by_ledger_reference": {...},
    "by_sealed_contract": {...}
  },
  "sealed_contract_references": {
    "#23": {"receipts_referencing": 7, "tracked_in_surface": true},
    "#24": {"receipts_referencing": 3, "tracked_in_surface": true},
    "#25": {"receipts_referencing": 4, "tracked_in_surface": true},
    "#26": {"receipts_referencing": 0, "tracked_in_surface": true},
    "#27": {"receipts_referencing": 0, "tracked_in_surface": true},
    "#28": {"receipts_referencing": 0, "tracked_in_surface": true}
  },
  "review_items": [],
  "surface_controls": {
    "approve": false, "seal": false, "execute": false, "write": false
  }
}
```

## 6. Edge Cases

| Scenario | Behavior |
|----------|----------|
| Surface unavailable | `surface_status: "unavailable"`, posture `"unavailable"` |
| Receipts directory missing | Posture `"degraded"` with descriptive detail |
| Receipts directory empty | Posture `"degraded"`, zero counts |
| Integration script missing | STARTUP-STATE.md shows unavailable, no startup failure |
| Malformed/duplicate records | Listed in `review_items`, no auto-repair |
| Cross-project claim | Rejected with `CROSS_PROJECT_STARTUP_CLAIM_REJECTED` |
| Broad approval claim | Rejected with `BROAD_PROJECT_ROOT_APPROVAL_CLAIM` |
| Non-deterministic request | Rejected with error |

## 7. Non-Goals

- No receipt mutation, regeneration, or repair
- No custody behavior changes
- No index or surface behavior changes
- No new write/lifecycle/approval/seal/execution/startup authority
- No cross-project startup/surface/index authority
- No auto-approval, auto-seal, auto-promotion, or auto-execution
- No startup authority creation

## 8. Boundary Invariants

1. Startup integration reads from #28 summary surface output only
2. Integration does not mutate, regenerate, or repair receipts
3. Integration does not alter #27 index behavior or semantics
4. Integration does not alter #28 summary surface behavior or semantics
5. Missing/unavailable surface returns degraded status, not fabricated success
6. Empty index returns valid report with zero counts
7. Non-deterministic startup custody summary generation is rejected
8. Malformed/duplicate records are flagged as review items only
9. Dry-run receipts are not treated as approval evidence
10. Warning receipts are not treated as approval evidence
11. Startup report has no approve/seal/execute/write controls
12. Cross-project startup/surface/index claims are rejected
13. Broad project-root approval claims are rejected
14. All output is deterministically ordered
