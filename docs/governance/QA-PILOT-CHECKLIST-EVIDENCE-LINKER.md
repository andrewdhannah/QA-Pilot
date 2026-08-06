# QA-PILOT-CHECKLIST-EVIDENCE-LINKER.md — QA Pilot Checklist Evidence Linker

**Status:** 🔍 Active (sprint #46)
**Authority:** Advisory-only. No approval, seal, execution, write, or sprint-start authority conferred.
**Custody:** QA Pilot-local only. No Librarian mutation permitted.

---

## 1. Purpose

Add a deterministic linking layer between evidence checklists (#44) and the actual pipeline evidence stores (#33-#45). Validates that evidence refs inside each checklist item point to real, existing pipeline artifacts — evidence packets, test cases, result packets, epic suites, owner decision receipts, and other stored records.

---

## 2. Definitions

| Term | Definition |
|------|-----------|
| **Evidence Linker** | A QA Pilot-local packet (`EL-*`) that resolves evidence refs from a checklist against real pipeline stores. |
| **Link Check** | A single resolution attempt: given a checklist item's pipeline_layer and ref, does the referenced artifact exist? |
| **Link Status** | `found` — artifact exists at expected location; `missing` — artifact not found; `stale` — artifact exists but is outdated (e.g. superseded by newer version). |
| **Aggregate Status** | `all_found` — every ref resolved; `missing_refs` — list of unfound refs; `stale_refs` — list of stale refs. |

---

## 3. Schema

The evidence linker schema is defined at `docs/schemas/qa-pilot-checklist-evidence-linker.schema.json` (Draft 2020-12).

### 3.1 Required Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `linker_id` | string (pattern `^EL-[A-Z0-9-]+$`) | Unique linker identifier |
| `source_checklist_id` | string (pattern `^EC-[A-Z0-9-]+$`) | The evidence checklist whose refs are validated |
| `title` | string | Human-readable title |
| `description` | string (min 10 chars) | Stores scanned and context |
| `links` | array (min 1) | Individual link checks |
| `aggregate` | object | total_links, found, missing, stale, all_found |
| `advisory_only` | boolean (`true`) | Always advisory |
| `custody` | string (`qa-pilot-local`) | Local custody only |
| `librarian_impact` | string (`none`) | No Librarian mutation |
| `not_seal_authority` | string (min 20 chars) | Seal-authority disclaimer |
| `not_librarian_mutation_authority` | string (min 20 chars) | Librarian-mutation disclaimer |
| `created_at` | string (date-time) | ISO 8601 creation timestamp |

### 3.2 Link Check Fields

| Field | Type | Description |
|-------|------|-------------|
| `item_id` | string (pattern `^ECI-`) | Checklist item being checked |
| `pipeline_layer` | enum | Which layer should contain this evidence |
| `ref` | string | The specific reference being resolved |
| `status` | enum (`found`, `missing`, `stale`) | Resolution outcome |
| `detail` | string (optional) | Why missing/stale or additional context |
| `expected_path` | string (optional) | Expected filesystem or store path |

### 3.3 Aggregate Fields

| Field | Type | Description |
|-------|------|-------------|
| `total_links` | integer | Total links checked |
| `found` | integer | Links resolved successfully |
| `missing` | integer | Links not found |
| `stale` | integer | Links found but outdated |
| `all_found` | boolean | True only if missing=0 and stale=0 |

---

## 4. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| EL-1 | Linker must conform to qa-pilot-checklist-evidence-linker.schema.json | Schema |
| EL-2 | advisory_only must be true | Schema const |
| EL-3 | custody must be qa-pilot-local | Schema pattern |
| EL-4 | librarian_impact must be none | Schema const |
| EL-5 | not_seal_authority must be present and >= 20 chars | Schema |
| EL-6 | not_librarian_mutation_authority must be present and >= 20 chars | Schema |
| EL-7 | source_checklist_id must reference an EC-* pattern | Schema pattern |
| EL-8 | At least one link check required | Schema minItems |
| EL-9 | Aggregate counts must match link array: total_links == len(links), found + missing + stale == total_links | Validator |
| EL-10 | If missing > 0, aggregate.missing_refs must be non-empty | Schema conditional |
| EL-11 | If stale > 0, aggregate.stale_refs must be non-empty | Schema conditional |
| EL-12 | all_found must be true only when missing=0 and stale=0 | Schema conditional |
| EL-13 | No authority claims in descriptions or detail fields | Validator |
| EL-14 | No Librarian mutation authority referenced | Validator |

---

## 5. Pipeline References

Evidence linkers scan the sealed pipeline stores:

| # | Layer | Store Path |
|---|-------|------------|
| 33 | Evidence Intake | `data/evidence/evidence-index.json` |
| 34 | Test Composition | `data/test-cases/test-case-index.json` |
| 35 | Result Export | `data/result-packets/result-packet-index.json` |
| 36 | Epic Regression | `data/epic-regression/epic-regression-index.json` |
| 42 | Owner Decision Receipt | `data/owner-decisions/` |
| 44 | Evidence Checklist | `docs/examples/qa-pilot-evidence-checklist/` |
| 45 | Checklist Review Packet | `docs/examples/qa-pilot-checklist-review-packet/` |

---

## 6. Authority

- **Advisory-only.** Linkers are advisory artifacts. They do not approve, seal, execute, write, or authorize sprint starts.
- **QA Pilot-local custody.** All linker data resides within QA Pilot-local paths only.
- **No Librarian mutation.** Linker validation rejects any reference to Librarian mutation authority.
- **No execution or remediation.** Linkers report status only — they do not create, repair, or modify evidence.
- **No sealing automation.** Linkers do not trigger or automate sealing.
- **Existing boundaries preserved.** The #33-#45 advisory-only custody boundaries are unchanged.

---

## 7. Invariants

| # | Invariant | Enforcement |
|---|-----------|-------------|
| I-1 | All valid linker packets must pass schema validation | Schema + validator |
| I-2 | All invalid fixtures must fail validation | Validator |
| I-3 | advisory_only=true invariant is unchangeable | Schema const |
| I-4 | custody=qa-pilot-local invariant is unchangeable | Schema pattern |
| I-5 | librarian_impact=none invariant is unchangeable | Schema const |
| I-6 | EL-* ID pattern is required | Schema pattern |
| I-7 | EC-* source checklist reference is required | Schema pattern |
| I-8 | Aggregate counts must be internally consistent | Validator |
| I-9 | No linker may claim approval/seal/execute/write authority | Validator |
| I-10 | All existing #33-#45 validators and test runners remain green | Regression |
