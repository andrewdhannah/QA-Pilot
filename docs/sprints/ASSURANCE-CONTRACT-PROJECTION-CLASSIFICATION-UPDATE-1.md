# ASSURANCE-CONTRACT-PROJECTION-CLASSIFICATION-UPDATE-1 — Projection Classification Update

**Type:** contract implementation (Phase 4)
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-21**
**Lane:** contract_extraction
**Boundary:** QA Pilot-local
**Librarian impact:** contract_interface
**Epic:** EPIC-ASSURANCE-CONTRACT-EVOLUTION-1 (Phase 4)
**Dependencies:** ASSURANCE-CONTRACT-EVIDENCE-STATE-SEPARATION-1 (#211, sealed)

---

## Purpose

Operationalize the #211 evidence state separation contract by updating assurance projections so evidence state classification is explicit, preventing historical records from being interpreted as current operational state.

---

## Scope

### Included
- Add `evidence_classification` to `qa-pilot-owner-dashboard.schema.json`
- Update dashboard projection/rendering paths
- Add validator coverage for classification mappings
- Verify existing records remain compatible
- Confirm runtime snapshots and historical records render distinctly

### Excluded
- Storage changes
- Database migration
- Core evidence model rewrite
- Consumer-specific assurance concepts
- Agent dispatch behavior changes

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| EPC-1 | Projection schema accepts evidence classification |
| EPC-2 | Existing records remain valid |
| EPC-3 | Historical records cannot render as operational without explicit classification |
| EPC-4 | Runtime snapshots render separately from historical records |
| EPC-5 | Dashboard labels accurately represent evidence state |
| EPC-6 | Existing consumers remain compatible |
| EPC-7 | No persistence changes required |

---

## Preserved Invariant

```
assurance_record
    ≠
assurance_snapshot
```

The projection layer may combine them for Owner visibility, but it must preserve their meaning.

---

**Status:** ✅ **SEALED — Owner-sealed 2026-07-21**
**Authorized by:** Andrew Hannah
**Epic:** EPIC-ASSURANCE-CONTRACT-EVOLUTION-1 (Phase 4)
**Ledger entry:** #212 (status: sealed)

## Implementation Summary

### Schema Update
- **`docs/schemas/qa-pilot-owner-dashboard.schema.json`** — v1.1
  - Added required `evidence_classification` block with `summary`, `classifications` array, and `invariant`
  - Each item: `source`, `evidence_class` (enum: `assurance_record` | `assurance_snapshot`), `display_label`, `temporal_note`, `source_type`
  - Exit invariant: "No historical record is rendered as current operational state without explicit classification"

### Dashboard Script
- **`scripts/qa_pilot_owner_dashboard.py`** — v1.1
  - Added `EVIDENCE_CLASSIFICATION_MAP` covering all 4 consumers (QA Pilot, Librarian, Agent Bridge, Runtime Node)
  - Added `classify_evidence()` — prefix-based classification with heuristic fallback
  - Added `build_evidence_classification()` — assemblies classification block
  - Classification included in both JSON and text output

### Validator
- **`scripts/validate-qa-pilot-owner-dashboard.py`** — Added EPC-1 through EPC-7

### Verification
- ✅ All 17 checks pass (OD-1..10 + EPC-1..7)
- ✅ All 13 existing test runner tests pass
- ✅ All 19 cross-consumer classification unit tests pass
- ✅ Zero storage changes
- ✅ Zero evidence ingestion changes
