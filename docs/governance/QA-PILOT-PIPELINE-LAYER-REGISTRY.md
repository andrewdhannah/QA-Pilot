# QA-PILOT-PIPELINE-LAYER-REGISTRY.md — QA Pilot Pipeline Layer Registry

**Status:** ✅ Sealed (sprint #48)
**Authority:** Advisory-only. No approval, seal, execution, write, or sprint-start authority conferred.
**Custody:** QA Pilot-local only. No Librarian mutation permitted.

---

## 1. Purpose

Define a governed, explicit pipeline layer registry that replaces hardcoded `EXPECTED_LAYERS` in the pipeline health validator (PH-12). The registry lists all sealed QA Pilot pipeline layers with their slot, sprint ID, layer type, custody, and authority posture. It distinguishes expected sealed layers from genuinely unexpected extra layers, fixing the pre-existing PH-12 expected-layer drift that incorrectly flagged #38–#47 as "extra."

This sprint closes the PH-12 drift by making the pipeline health validator registry-aware.

---

## 2. Definitions

| Term | Definition |
|------|-----------|
| **Pipeline Layer** | A sealed QA Pilot sprint that contributes to the advisory pipeline. Each layer has a slot (ledger number), sprint ID, and layer type. |
| **Layer Registry** | A governed data file (`data/pipeline-layer-registry/registry.json`) listing all pipeline layers with their validated properties. |
| **PLR-* Rule** | Pipeline Layer Registry business rule enforced by the layer registry validator. |
| **Expected Layer** | A sealed sprint registered in the layer registry. These layers are recognized and expected — not drift. |
| **Unexpected Extra Layer** | A sealed sprint that is NOT in the layer registry AND NOT a pre-pipeline sprint. Truly unknown extra layers are flagged as drift. |
| **Missing Layer** | A slot number gap in the layer registry — a sealed sprint that should exist but is absent from the registry. |

---

## 3. Schema

The layer registry schema is defined at `docs/schemas/qa-pilot-pipeline-layer-registry.schema.json` (Draft 2020-12).

### 3.1 Required Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `registry_id` | string (pattern `^PLR-[A-Z0-9-]+$`) | Unique registry identifier |
| `title` | string (min 1) | Human-readable title |
| `description` | string (min 10) | Context for this registry |
| `layers` | array (min 1) | Ordered list of sealed pipeline layers |
| `advisory_only` | boolean (`true`) | Always advisory |
| `custody` | string (`qa-pilot-local`) | Local custody only |
| `librarian_impact` | string (`none`) | No Librarian mutation |
| `not_seal_authority` | string (min 20 chars) | Seal-authority disclaimer |
| `not_librarian_mutation_authority` | string (min 20 chars) | Librarian-mutation disclaimer |
| `created_at` | string (date-time) | ISO 8601 creation timestamp |

### 3.2 Layer Entry Fields

| Field | Type | Description |
|-------|------|-------------|
| `slot` | integer (>= 1) | Ledger sealed number |
| `sprint_id` | string (pattern) | Authorized sprint ID |
| `sprint_title` | string (optional) | Human-readable sprint title |
| `layer_type` | enum | `pipeline`, `governance`, `implementation`, `validation`, `planning`, `enforcement`, `simulation`, `production`, `architecture`, `bridge`, `defect` |
| `status` | string (`sealed`) | Must be sealed |
| `advisory` | boolean (`true`) | Must be advisory-only |
| `custody` | string (`qa-pilot-local`) | Must be qa-pilot-local |
| `librarian_mutation` | boolean (`false`) | Must be false |

---

## 4. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| PLR-1 | Registry conforms to qa-pilot-pipeline-layer-registry.schema.json | Schema |
| PLR-2 | advisory_only must be true | Schema const |
| PLR-3 | custody must be qa-pilot-local | Schema pattern |
| PLR-4 | librarian_impact must be none | Schema const |
| PLR-5 | not_seal_authority must be present and >= 20 chars | Schema |
| PLR-6 | not_librarian_mutation_authority must be present and >= 20 chars | Schema |
| PLR-7 | At least one layer entry required | Schema minItems |
| PLR-8 | All entries must have status=sealed | Schema const |
| PLR-9 | All entries must have advisory=true | Schema const |
| PLR-10 | All entries must have custody=qa-pilot-local | Schema pattern |
| PLR-11 | All entries must have librarian_mutation=false | Schema const |
| PLR-12 | Slot numbers must be strictly increasing (no duplicates, no gaps that skip sealed sprints) | Validator |
| PLR-13 | Each sprint_id must resolve to a sealed entry in the sprint ledger | Validator |
| PLR-14 | No authority claims in descriptions or detail fields | Validator |
| PLR-15 | No Librarian mutation authority referenced | Validator |
| PLR-16 | Registry must include slots #33 through latest sealed pipeline head | Validator |

---

## 5. Registry Location

The canonical layer registry lives at `data/pipeline-layer-registry/registry.json`. It is a governed data file — advisory-only, QA Pilot-local. It is consumed by:
- `validate-qa-pilot-pipeline-layer-registry.py` — validates registry integrity
- `validate-qa-pilot-pipeline-health-regression.py` — loads `EXPECTED_LAYERS` from registry (PH-12 fix)

---

## 6. Authority

- **Advisory-only.** The layer registry is an advisory governance artifact. It does not approve, seal, execute, write, or authorize sprint starts.
- **QA Pilot-local custody.** All registry data resides within QA Pilot-local paths only.
- **No Librarian mutation.** Registry validation rejects any reference to Librarian mutation authority.
- **No execution or remediation.** The registry reports status only — it does not modify the pipeline, seal sprints, or change layer behavior.
- **No sealing automation.** The registry does not trigger or automate sealing.
- **Existing boundaries preserved.** All #33-#47 advisory-only custody boundaries are unchanged.

---

## 7. Invariants

| # | Invariant | Enforcement |
|---|-----------|-------------|
| I-1 | All valid registry entries must pass schema validation | Schema + validator |
| I-2 | All invalid fixtures must fail validation | Validator |
| I-3 | advisory_only=true invariant is unchangeable | Schema const |
| I-4 | custody=qa-pilot-local invariant is unchangeable | Schema pattern |
| I-5 | librarian_impact=none invariant is unchangeable | Schema const |
| I-6 | PLR-* ID pattern is required | Schema pattern |
| I-7 | Slot numbers must be strictly increasing | Validator |
| I-8 | Each sprint_id must resolve to sealed ledger entry | Validator |
| I-9 | No registry may claim approval/seal/execute/write authority | Validator |
| I-10 | All existing #33-#47 validators and test runners remain green | Regression |
| I-11 | PH-12 must no longer flag registry layers as unexpected extra layers | Integration |
