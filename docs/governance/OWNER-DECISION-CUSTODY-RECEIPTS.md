# OWNER-DECISION-CUSTODY-RECEIPTS.md — Custody Receipt Normalization

**Status:** 🔍 Pending (not sealed)
**Authority:** Unifies custody receipts from #23, #24, #25 into a single Owner-reviewable decision trail.
**Sprint:** OWNER-DECISION-CUSTODY-RECEIPTS-1

---

## 1. Purpose

Unify custody receipts from PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT-1 (#23), LIVE-CUSTODY-INTEGRATION-1 (#24), and LIFECYCLE-CUSTODY-EXTENSION-1 (#25) into a single Owner-reviewable decision trail. This is a receipt/evidence normalization sprint only. It does not add or change any authority.

## 2. Receipt Schema

All unified receipts conform to `owner-decision-custody-receipt-v1`:

| Field | Description |
|-------|-------------|
| `receipt_id` | Deterministic hash from content |
| `custody_source` | `write` / `live` / `lifecycle` |
| `source_contract` | `#23` / `#24` / `#25` / `direct` |
| `decision_type` | `approved` / `denied` / `warning` / `dry_run` |
| `immutable` | Always `true` — receipts cannot be overwritten |
| `deterministic` | Always `true` — non-deterministic generation rejected |
| `request` | project_id, sprint_id, file_path, transition, reason |
| `enforcement` | decision, blocker_code, violation_code, triggered_rules |
| `provenance` | owner_approval_present, owner_approval_ref, approval_is_broad |
| `mutation_status` | `mutated` / `blocked` / `dry_run_no_mutation` |
| `linked_references` | sprint_id, ledger_numbers, source_receipt_id |
| `sealed_contracts_referenced` | References to #23, #24, #25 |

## 3. Validation Rules

| Rule | Description |
|------|-------------|
| Cross-project receipt claims rejected | `project_id` must be `qa-pilot` |
| Broad approval rejected | `owner_approval_is_broad` causes denial |
| Dry-run not approval | Dry-run receipts cannot serve as approval evidence |
| Warning not approval | Warning receipts cannot serve as approval evidence |
| Deterministic only | `deterministic` must be true; non-deterministic rejected |
| Immutable after write | Existing receipts cannot be overwritten |

## 4. Modes

| Mode | Behavior |
|------|----------|
| `live` | Normalize input, persist receipt to `receipts/owner-decision-custody/` |
| `dry-run` | Normalize input, return receipt without persisting |
| `scan` | Scan existing audit directories (`data/custody-audit/`, `data/lifecycle-custody-audit/`) and produce unified receipts |

## 5. Storage

Normalized receipts are stored at:
```
receipts/owner-decision-custody/<receipt_id>.json
```

Source audit receipts remain at their original locations:
- `data/custody-audit/` (#24 live custody)
- `data/lifecycle-custody-audit/` (#25 lifecycle custody)

## 6. Non-Goals

- No new write authority
- No new lifecycle authority
- No cross-project receipt authority
- No auto-approval, auto-seal, auto-promotion, or auto-execution
- No alteration of #23, #24, or #25 contracts

## 7. Boundary Invariants

1. Cross-project receipt claims rejected with clear error
2. Broad approvals rejected with clear error
3. Dry-run receipts never count as approval evidence
4. Warning receipts never count as approval evidence
5. Non-deterministic generation always rejected
6. Receipts are immutable after write (no overwrite)
7. Receipts cannot bypass #23 write custody
8. Receipts cannot alter #24 live behavior
9. Receipts cannot alter #25 lifecycle behavior
