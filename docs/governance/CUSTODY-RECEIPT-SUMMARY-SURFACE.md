# CUSTODY-RECEIPT-SUMMARY-SURFACE.md — Custody Receipt Summary Surface

**Status:** 🔍 Pending (not sealed)
**Authority:** Read-only Owner-review summary surface over #27 custody receipt index. Does not mutate receipts, index, custody behavior, or enforcement.
**Sprint:** CUSTODY-RECEIPT-SUMMARY-SURFACE-1

---

## 1. Purpose

Expose the sealed CUSTODY-RECEIPT-INDEX-1 (#27) read-only custody receipt index as an Owner-review summary surface. This surface provides summary counts, violation analysis, provenance tracking, and review-item detection — all from the #27 index output without touching receipts directly.

## 2. Data Source

The summary surface reads **exclusively** from the #27 `custody-receipt-index.py` output. It does not read receipts directly. This ensures clean architectural layering:

```
Receipts (#26) → Index (#27) → Summary Surface (this sprint)
```

| Layer | Component | Sprint |
|-------|-----------|--------|
| Receipt storage | `receipts/owner-decision-custody/` | #26 |
| Read-only index | `custody-receipt-index.py` | #27 |
| Summary surface | `custody-receipt-summary-surface.py` | **this** |

## 3. Modes

| Mode | Description |
|------|-------------|
| `surface` | Generate the full Owner-review summary surface (default) |
| `status` | Quick status check — directory status, receipt count, malformed/duplicate counts |
| `dry-run` | Validate index is buildable without surface output |
| `validate` | Run acceptance gate validation against generated or provided surface output |

## 4. Surface Output Structure

```json
{
  "surface_metadata": {
    "schema": "custody-receipt-summary-surface-v1",
    "deterministic": true,
    "index_status": "ok|missing|empty|unavailable",
    "total_receipts_in_index": 12,
    "index_schema": "custody-receipt-index-v1"
  },
  "summary": {
    "by_custody_source": {"write": 7, "live": 2, "lifecycle": 3},
    "by_decision_type": {
      "approvals": 10, "denied": 2, "warning": 0, "dry_run": 0
    },
    "by_decision_type_raw": {"approved": 10, "denied": 2},
    "by_violation_code": {"WRITE_SCOPE_VIOLATION": 2},
    "by_mutation_status": {"mutated": 10, "blocked": 2},
    "by_approval_provenance": {
      "owner_approval_present": 2, "owner_approval_absent": 10
    },
    "by_sprint": {"SPRINT-1": 3, ...},
    "by_ledger_reference": {"#23": 7, "#24": 2, "#25": 3},
    "by_sealed_contract": {"#23": 7, "#24": 3, "#25": 4}
  },
  "sealed_contract_references": {
    "#23": {"receipts_referencing": 7, "known_contract": true},
    "#24": {"receipts_referencing": 3, "known_contract": true},
    "#25": {"receipts_referencing": 4, "known_contract": true},
    "#26": {"receipts_referencing": 0, "known_contract": true},
    "#27": {"receipts_referencing": 0, "known_contract": true}
  },
  "review_items": [
    {"type": "malformed_receipt", "filename": "...", "detail": "...",
     "action": "review", "auto_repair": false}
  ],
  "surface_controls": {
    "approve": false, "seal": false, "execute": false, "write": false
  }
}
```

## 5. Decision Type Classification

The summary surface classifies decision types into four categories:

| Category | Included Decision Types | Example |
|----------|------------------------|---------|
| `approvals` | `approved` | Approved write, allowed transition |
| `denied` | `denied` | WRITE_SCOPE_VIOLATION, sealed evidence |
| `warning` | `warning` | REQUIRES_OWNER_APPROVAL |
| `dry_run` | `dry_run` | Dry-run evaluation results |

The raw breakdown (`by_decision_type_raw`) preserves the original index counts for full transparency.

## 6. Edge Cases

| Scenario | Behavior |
|----------|----------|
| Index missing/unavailable | `index_status: "unavailable"`, empty summary, no review items |
| Receipts directory missing | `index_status: "missing"` propagated from index |
| Receipts directory empty | `index_status: "empty"`, all counts zero |
| Malformed receipts | Listed in `review_items` as `malformed_receipt`, no auto-repair |
| Duplicate receipt IDs | Listed in `review_items` as `duplicate_receipt_id`, no auto-repair |
| Cross-project claim | Rejected with `CROSS_PROJECT_SURFACE_CLAIM_REJECTED` |
| Broad approval claim | Rejected with `BROAD_PROJECT_ROOT_APPROVAL_CLAIM_REJECTED` |
| Non-deterministic request | Rejected with error |

## 7. Non-Goals

- No receipt mutation, regeneration, or repair
- No custody behavior changes
- No index behavior changes
- No new write/lifecycle/approval/seal/execution authority
- No cross-project surface/index authority
- No auto-approval, auto-seal, auto-promotion, or auto-execution
- No approve/seal/execute/write controls

## 8. Boundary Invariants

1. Summary surface reads from #27 index output only — never reads receipts directly
2. Surface does not mutate, regenerate, or repair receipts
3. Surface does not alter #27 index behavior or semantics
4. Missing/unavailable index returns degraded status, not fabricated success
5. Empty index returns valid empty surface with zero counts
6. Non-deterministic summary generation is rejected
7. Malformed/duplicate records are flagged as review items, not repaired
8. Dry-run receipts are not treated as approval evidence
9. Warning receipts are not treated as approval evidence
10. Surface has no approve/seal/execute/write controls
11. Cross-project surface/index claims are rejected
12. Broad project-root approval claims are rejected
13. All output is deterministically ordered
