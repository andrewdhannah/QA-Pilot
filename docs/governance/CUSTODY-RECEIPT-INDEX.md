# CUSTODY-RECEIPT-INDEX.md — Custody Receipt Index

**Status:** 🔍 Pending (not sealed)
**Authority:** Read-only index over unified custody receipts from #26. Does not mutate receipts, custody behavior, or enforcement.
**Sprint:** CUSTODY-RECEIPT-INDEX-1

---

## 1. Purpose

Build a read-only query/index layer over unified custody receipts from OWNER-DECISION-CUSTODY-RECEIPTS-1 (#26), so Owner review can query custody decisions by source, decision type, sprint, ledger reference, violation code, mutation status, approval provenance, and sealed-contract reference.

## 2. Modes

| Mode | Description |
|------|-------------|
| `index` | Build and output the full index with summary counts |
| `query` | Filter receipts by criteria (source, type, violation, sprint, etc.) |
| `status` | Directory health, total/malformed/duplicate counts |
| `dry-run` | Validate index is buildable without full output |

## 3. Query Filters

| Filter | CLI Flag | Description |
|--------|----------|-------------|
| Custody source | `--custody-source` | write, live, lifecycle |
| Decision type | `--decision-type` | approved, denied, warning, dry_run |
| Violation code | `--violation-code` | e.g. WRITE_SCOPE_VIOLATION |
| Mutation status | `--mutation-status` | mutated, blocked, dry_run_no_mutation |
| Approval present | `--approval-present` | Only receipts with Owner approval |
| Approval absent | `--approval-absent` | Only receipts without Owner approval |
| Sprint ID | `--sprint` | Substring match on sprint ID |
| Ledger reference | `--ledger` | Numeric ledger number |
| Contract reference | `--contract` | #23, #24, #25, #26 |

## 4. Index Output

```json
{
  "index_metadata": {
    "schema": "custody-receipt-index-v1",
    "deterministic": true,
    "directory_status": "ok|missing|empty",
    "total_receipts": 12,
    "total_malformed": 0,
    "total_duplicate_ids": 0
  },
  "summary": {
    "by_custody_source": {"write": 7, "live": 2, "lifecycle": 3},
    "by_decision_type": {"approved": 10, "denied": 2},
    "by_violation_code": {"WRITE_SCOPE_VIOLATION": 2},
    "by_mutation_status": {"mutated": 10, "blocked": 2},
    "by_approval_provenance": {"present": 2, "absent": 10},
    "by_sprint": {"AG-1": 1, ...},
    "by_ledger": {"#23": 7, "#24": 2, "#25": 3},
    "by_sealed_contract": {"#23": 7, "#24": 2, "#25": 3}
  },
  "malformed": [],
  "duplicates": [],
  "receipts": [...]
}
```

## 5. Edge Cases

| Scenario | Behavior |
|----------|----------|
| Receipts directory missing | `directory_status: "missing"`, no fabricated success |
| Receipts directory empty | `directory_status: "empty"`, valid index with zero counts |
| Malformed JSON files | Listed in `malformed` array, not in index |
| Duplicate receipt IDs | Listed in `duplicates` array |
| Non-deterministic request | Rejected with error |

## 6. Non-Goals

- No receipt mutation
- No custody behavior changes
- No new write/lifecycle/approval authority
- No cross-project index authority
- No auto-approval, auto-seal, auto-promotion, or auto-execution

## 7. Boundary Invariants

1. Index is read-only — never mutates receipts
2. Missing directory returns degraded status, not fabricated success
3. Empty directory returns valid empty index
4. Non-deterministic generation is rejected
5. Malformed receipts are detected without repair
6. Duplicate receipt IDs are detected
7. All output is deterministically ordered
