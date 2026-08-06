# QA-PILOT-RCR-CLOSEOUT-GATE.md — QA Pilot RCR Closeout Gate

**Status:** 🔍 Active (sprint #53)
**Authority:** Advisory-only. No approval, seal, execution, or sprint-start authority conferred.
**Custody:** QA Pilot-local only. No Librarian mutation permitted.

---

## 1. Purpose

Define a governed closeout gate requiring every completed QA Pilot sprint to explicitly declare its registry impact and, when applicable, provide a valid RCR receipt before it can be considered seal-ready. The gate validates that:

1. Every sprint has a declared registry impact classification.
2. If the sprint affects the registry (adds_layer/updates_layer/deprecates_layer), a valid RCR receipt exists.
3. If the sprint does not affect the registry (no_registry_impact), a valid rationale exists.
4. Registry layer counts are consistent before and after.

This closes the lifecycle gap after #51 (RCR lifecycle) and #52 (RCR surface) by adding closeout enforcement.

---

## 2. Definitions

| Term | Definition |
|------|-----------|
| **Closeout Gate** | A governed gate packet (`RCG-*`) declaring a sprint's registry impact and validating seal-readiness. |
| **RCG-* Rule** | RCR Closeout Gate business rule enforced by the validator. |
| **Seal-ready** | A sprint is seal-ready when its closeout gate passes all checks (status=ready). |

---

## 3. Schema

The RCR closeout gate schema is defined at `docs/schemas/qa-pilot-rcr-closeout-gate.schema.json` (Draft 2020-12).

### 3.1 Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `gate_id` | string (pattern `^RCG-`) | Unique closeout gate identifier |
| `sprint_id` | string | Sprint being closed out |
| `ledger_number` | integer | Ledger number |
| `registry_impact` | enum | adds_layer/updates_layer/no_registry_impact/deprecates_layer |
| `rcr_receipt_id` | string (conditional) | RCR receipt ID (required for adds_layer/updates_layer/deprecates_layer) |
| `registry_before_summary` | string (min 10) | Registry state before |
| `registry_after_summary` | string (min 10) | Registry state after |
| `no_impact_rationale` | string (conditional, min 20) | Rationale for no_registry_impact |
| `closeout_status` | enum | ready/blocked/degraded |
| `advisory_only` | boolean (true) | Always advisory |

---

## 4. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| RCG-1 | Gate conforms to qa-pilot-rcr-closeout-gate.schema.json | Schema |
| RCG-2 | advisory_only must be true | Schema |
| RCG-3 | custody must be qa-pilot-local | Schema |
| RCG-4 | librarian_impact must be none | Schema |
| RCG-5 | not_seal_authority >= 20 chars | Schema |
| RCG-6 | not_librarian_mutation_authority >= 20 chars | Schema |
| RCG-7 | sprint_id must resolve to a sealed ledger entry | Validator |
| RCG-8 | registry_impact must be valid enum | Schema |
| RCG-9 | If adds_layer/updates_layer/deprecates_layer: RCR receipt must exist and be valid | Validator |
| RCG-10 | If no_registry_impact: rationale must be >= 20 chars | Schema |
| RCG-11 | Registry layer counts must be internally consistent | Validator |
| RCG-12 | No authority claims in descriptions or rationale | Validator |
| RCG-13 | No Librarian mutation authority referenced | Validator |

---

## 5. Closeout Gate Flow

```
Sprint complete
  → Agent creates RCG packet declaring registry impact
  → Validator checks:
      - Sprint exists and is sealed
      - Registry impact valid
      - If adds_layer/updates_layer/deprecates_layer: RCR receipt exists
      - If no_registry_impact: rationale >= 20 chars
      - Layer counts consistent
  → Result: ready / blocked / degraded
  → Only ready sprints should proceed to seal
```

---

## 6. Authority

- **Advisory-only.** Closeout gates are advisory governance artifacts. They do not approve, seal, execute, or authorize sprint starts.
- **QA Pilot-local custody.** All gate data within QA Pilot-local paths only.
- **No Librarian mutation.** No Librarian files modified.
- **No automatic sealing.** Gates validate seal-readiness but do not seal.
- **No automatic registry mutation.** Gates do not create, modify, or delete registry entries.

---

## 7. Invariants

| # | Invariant | Enforcement |
|---|-----------|-------------|
| I-1 | All valid gates must pass schema validation | Schema + validator |
| I-2 | All invalid fixtures must fail validation | Validator |
| I-3 | advisory_only=true is unchangeable | Schema const |
| I-4 | RCG-* ID pattern is required | Schema pattern |
| I-5 | Every adds_layer sprint must have a valid RCR receipt | Validator |
| I-6 | Every no_registry_impact sprint must have rationale >= 20 chars | Schema + validator |
| I-7 | No gate may claim approval/seal/execute/write authority | Validator |
| I-8 | All #33-#53 validators remain green | Regression |
