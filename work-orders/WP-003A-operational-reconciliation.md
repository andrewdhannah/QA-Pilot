# WP-003A — Operational Registry Reconciliation

**Work Packet:** WP-003A of GOVERNANCE-IDENTITY-CONSISTENCY-1
**Date:** 2026-08-16
**Status:** READY — awaiting Owner decision receipts

---

## Objective

Reconcile two active operational entities to their correct lifecycle state in the canonical registry.

## Scope

| Entity | Current Phase | Proposed Phase | Canonical State |
|---|---|---|---|
| librarian | (not set) | execution | Operational |
| agent-bridge | (not set) | execution | Operational |

## Evidence Basis

### librarian

| Evidence Source | Value |
|---|---|
| Cursor phase | 8 (Operational) |
| Cursor position | 529 |
| Sealed transitions | 471 |
| Total work items | 478 |
| Registry (project-state) | "execution" |
| Classification confidence | HIGH |

### agent-bridge

| Evidence Source | Value |
|---|---|
| Cursor phase | 8 (Operational) |
| Cursor position | 14 |
| Transition history | 18 entries spanning all 8 phases |
| Profile | platform_extension |
| Registry (project-state) | "active" |
| Drift | 2 warnings (stale 31 days, not corruption) |
| Classification confidence | HIGH |

## Acceptance Gates

### G1 — Owner Decision Receipts

Two decision receipts required:
- `ODR-WP003A-LIBRARIAN-001`
- `ODR-WP003A-AGENT-BRIDGE-001`

### G2 — Lifecycle Reconciliation

Each entity processed through `governance_lifecycle_reconcile`:
- Validated against canonical Rust enum
- Authorization basis provided
- Evidence basis documented

### G3 — Reconciliation Receipts

Two receipts:
- `LCR-WP003A-LIBRARIAN-001`
- `LCR-WP003A-AGENT-BRIDGE-001`

### G4 — Registry Verification

After mutation, `librarian_governance_get_entities` returns:
- librarian: `lifecycle_phase: "execution"`
- agent-bridge: `lifecycle_phase: "execution"`

## Stop Conditions

- If entity cannot be classified without invention → route to Owner Decision Queue
- If cursor state contradicts registry state → investigate before mutating

---

## Owner Decision Receipts

### ODR-WP003A-LIBRARIAN-001

```json
{
  "receipt_type": "OWNER_DECISION_RECEIPT",
  "receipt_id": "ODR-WP003A-LIBRARIAN-001",
  "entity_id": "librarian",
  "transition": {
    "from": "(not set)",
    "to": "execution",
    "canonical_state": "Operational"
  },
  "evidence": {
    "cursor_phase": 8,
    "cursor_position": 529,
    "sealed_transitions": 471,
    "total_work_items": 478,
    "classification_confidence": "HIGH"
  },
  "authorization_scope": "Permit lifecycle registry mutation only"
}
```

### ODR-WP003A-AGENT-BRIDGE-001

```json
{
  "receipt_type": "OWNER_DECISION_RECEIPT",
  "receipt_id": "ODR-WP003A-AGENT-BRIDGE-001",
  "entity_id": "agent-bridge",
  "transition": {
    "from": "(not set)",
    "to": "execution",
    "canonical_state": "Operational"
  },
  "evidence": {
    "cursor_phase": 8,
    "cursor_position": 14,
    "transition_history_entries": 18,
    "phases_covered": [0, 1, 2, 3, 4, 5, 6, 7, 8],
    "profile": "platform_extension",
    "classification_confidence": "HIGH"
  },
  "authorization_scope": "Permit lifecycle registry mutation only"
}
```
