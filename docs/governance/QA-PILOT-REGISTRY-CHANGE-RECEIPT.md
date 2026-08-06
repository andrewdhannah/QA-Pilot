# QA-PILOT-REGISTRY-CHANGE-RECEIPT.md — QA Pilot Registry Change Receipt

**Status:** 🔍 Active (sprint #51)
**Authority:** Advisory-only. No approval, seal, execution, write, or sprint-start authority conferred.
**Custody:** QA Pilot-local only. No Librarian mutation permitted.

---

## 1. Purpose

Define a governed receipt layer for any future sprint that changes, adds to, or intentionally does not affect the QA Pilot layer registry. Every sprint that may affect the pipeline layer registry must produce a receipt declaring its registry impact class, preventing the registry from becoming a new manual-maintenance surface after #48–#50.

---

## 2. Definitions

| Term | Definition |
|------|-----------|
| **Registry Change Receipt** | A QA Pilot-local advisory receipt (`RCR-*`) declaring how a sprint affects the layer registry. |
| **adds_layer** | The sprint adds a new layer to the registry (e.g. a new sealed sprint becomes part of the pipeline). |
| **updates_layer** | The sprint updates the metadata of an existing registry layer (e.g. title, description). |
| **no_registry_impact** | The sprint intentionally does not affect the registry. Requires a rationale >= 20 chars. |
| **deprecates_layer** | The sprint deprecates or removes a layer from the registry. |

---

## 3. Schema

The registry change receipt schema is defined at `docs/schemas/qa-pilot-registry-change-receipt.schema.json` (Draft 2020-12).

### 3.1 Required Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `receipt_id` | string (pattern `^RCR-[A-Z0-9-]+$`) | Unique receipt identifier |
| `sprint_id` | string (min 1) | Sprint ID that produced this change |
| `ledger_number` | integer (>= 1) | Ledger number of the sprint |
| `registry_impact` | enum | `adds_layer`, `updates_layer`, `no_registry_impact`, `deprecates_layer` |
| `registry_before_summary` | string (min 10) | Registry state before the change |
| `registry_after_summary` | string (min 10) | Registry state after the change |
| `rationale` | string (min 20 for no_registry_impact) | Rationale for the classification |
| `advisory_only` | boolean (`true`) | Always advisory |
| `custody` | string (`qa-pilot-local`) | Local custody only |
| `librarian_impact` | string (`none`) | No Librarian mutation |
| `not_seal_authority` | string (min 20 chars) | Seal-authority disclaimer |
| `not_librarian_mutation_authority` | string (min 20 chars) | Librarian-mutation disclaimer |
| `created_at` | string (date-time) | ISO 8601 creation timestamp |

### 3.2 Conditional Fields

| Field | Condition | Description |
|-------|-----------|-------------|
| `layer_slot_added` | registry_impact=adds_layer | Slot number of the added layer |
| `layer_slot_deprecated` | registry_impact=deprecates_layer | Slot number of the deprecated layer |

---

## 4. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| RCR-1 | Receipt conforms to qa-pilot-registry-change-receipt.schema.json | Schema |
| RCR-2 | advisory_only must be true | Schema const |
| RCR-3 | custody must be qa-pilot-local | Schema pattern |
| RCR-4 | librarian_impact must be none | Schema const |
| RCR-5 | not_seal_authority must be present and >= 20 chars | Schema |
| RCR-6 | not_librarian_mutation_authority must be present and >= 20 chars | Schema |
| RCR-7 | registry_impact must be a valid enum value | Schema enum |
| RCR-8 | If adds_layer, layer_slot_added must be present and >= 1 | Schema conditional |
| RCR-9 | If deprecates_layer, layer_slot_deprecated must be present and >= 1 | Schema conditional |
| RCR-10 | If no_registry_impact, rationale >= 20 chars | Schema conditional |
| RCR-11 | registry_before_summary must be present and >= 10 chars | Validator |
| RCR-12 | registry_after_summary must be present and >= 10 chars | Validator |
| RCR-13 | When adds_layer, registry_after layer count must be registry_before count + 1 | Validator |
| RCR-14 | No authority claims in descriptions or rationale | Validator |
| RCR-15 | No Librarian mutation authority referenced | Validator |

---

## 5. Receipt Location

Registry change receipts are stored alongside other QA Pilot receipt types. The receipt must be produced during the sprint that affects the registry, before sealing.

---

## 6. Authority

- **Advisory-only.** Registry change receipts are advisory governance artifacts. They do not approve, seal, execute, write, or authorize sprint starts.
- **QA Pilot-local custody.** All receipt data resides within QA Pilot-local paths only.
- **No Librarian mutation.** Receipt validation rejects any reference to Librarian mutation authority.
- **No automatic registry mutation.** The receipt declares but does not perform registry changes.
- **No sealing automation.** Receipts do not trigger or automate sealing.
- **Existing boundaries preserved.** All #33-#50 advisory-only custody boundaries are unchanged.

---

## 7. Invariants

| # | Invariant | Enforcement |
|---|-----------|-------------|
| I-1 | All valid receipts must pass schema validation | Schema + validator |
| I-2 | All invalid fixtures must fail validation | Validator |
| I-3 | advisory_only=true invariant is unchangeable | Schema const |
| I-4 | custody=qa-pilot-local invariant is unchangeable | Schema pattern |
| I-5 | librarian_impact=none invariant is unchangeable | Schema const |
| I-6 | RCR-* ID pattern is required | Schema pattern |
| I-7 | registry_impact must be a declared enum value | Schema enum |
| I-8 | layer counts must be consistent when adds_layer | Validator |
| I-9 | No receipt may claim approval/seal/execute/write authority | Validator |
| I-10 | All #33-#50 validators and test runners remain green | Regression |
