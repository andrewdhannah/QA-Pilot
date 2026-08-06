# QA-PILOT-SNAPSHOT-UPDATE-GATE.md — QA Pilot Snapshot Update Gate

**Status:** 🔍 Active (sprint #57)
**Authority:** Advisory-only. No approval, seal, execution, or sprint-start authority conferred.
**Custody:** QA Pilot-local only. No Librarian mutation permitted.

---

## 1. Purpose

Define governed rules for when the frozen startup surface regression snapshot (SRS-BASELINE-001) may be updated after legitimate surface changes, preventing the snapshot from becoming stale or being casually overwritten.

---

## 2. Update Classes

| Class | Description |
|-------|-------------|
| `legitimate_surface_change` | A planned, documented change to the startup surface (e.g. new section, new rule set). |
| `registry_layer_count_change` | Registry layer count changed due to sealed sprint adding/deprecating a layer. |
| `rcr_receipt_count_change` | RCR receipt count changed due to new backfill or new sealed sprint. |
| `rcg_coverage_change` | RCG coverage gap changed due to new sealed sprint without matching RCR. |
| `no_snapshot_update_required` | No snapshot update is needed (baseline still matches live state). |

---

## 3. Business Rules

| Rule | Description |
|------|-------------|
| SUG-1 | Gate conforms to qa-pilot-snapshot-update-gate.schema.json |
| SUG-2 | advisory_only must be true |
| SUG-3 | custody = qa-pilot-local |
| SUG-4 | librarian_impact = none |
| SUG-5 | not_seal_authority >= 20 chars |
| SUG-6 | not_librarian_mutation_authority >= 20 chars |
| SUG-7 | update_class must be valid enum |
| SUG-8 | previous_snapshot_id must reference existing snapshot |
| SUG-9 | rationale must be >= 20 chars |
| SUG-10 | If proposed_layer_pg_count < previous, must explain in rationale |
| SUG-11 | Update must not classify degraded/blocked as improvement without evidence |
| SUG-12 | No authority claims in descriptions or rationale |
| SUG-13 | No Librarian mutation authority referenced |

---

## 4. Authority

Advisory-only. No approval, seal, execution, or sprint-start authority conferred. No automatic baseline rewrite.

---

## 5. Invariants

| # | Invariant | Enforcement |
|---|-----------|-------------|
| I-1 | All valid gates must pass schema | Schema + validator |
| I-2 | All invalid fixtures must fail | Validator |
| I-3 | SUG-* ID pattern required | Schema |
| I-4 | No gate may claim seal/approve authority | Validator |
| I-5 | All existing validators remain green | Regression |
