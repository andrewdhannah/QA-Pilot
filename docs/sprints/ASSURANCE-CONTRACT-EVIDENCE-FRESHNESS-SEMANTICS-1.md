# ASSURANCE-CONTRACT-EVIDENCE-FRESHNESS-SEMANTICS-1 — Evidence Freshness Semantics

**Type:** contract evolution (Phase 4)
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-21**
**Lane:** contract_extraction
**Boundary:** QA Pilot-local
**Librarian impact:** contract_interface
**Epic:** EPIC-ASSURANCE-CONTRACT-EVOLUTION-1 (Phase 4)
**Dependencies:** ASSURANCE-CONTRACT-PROJECTION-CLASSIFICATION-UPDATE-1 (#212, sealed)

---

## Purpose

Define freshness semantics that preserve the difference between historical evidence validity and current operational observation age.

## Rationale

Classification (#211/#212) answers: *"What kind of evidence is this?"*

Freshness answers: *"How much confidence should we place in this evidence now?"*

These are different questions with different answers depending on evidence class:

```
assurance_record:
    Qualification passed  → Is this record still relevant?
    Receipt issued        → Historical confidence
    Evidence captured     → Evidence age

assurance_snapshot:
    Runtime observed      → Is this observation still current?
    Health measured       → Refresh interval
    State captured        → Current confidence
```

A single stale-time rule would be incorrect. Old evidence ≠ invalid evidence.

---

## Acceptance Gates

| Gate | Validation |
|------|-----------|
| EFS-1 | Record freshness semantics defined |
| EFS-2 | Snapshot freshness semantics defined |
| EFS-3 | Staleness cannot invalidate historical proof incorrectly |
| EFS-4 | Old snapshots cannot appear current |
| EFS-5 | Dashboard freshness indicators use evidence class |
| EFS-6 | Existing 4-consumer mappings remain valid |
| EFS-7 | No storage migration unless evidence requires |
| EFS-8 | Agent dispatch implications documented |

---

## Expected Outcome

```
assurance_record:
    evidence age
    validation context
    historical confidence

assurance_snapshot:
    observation age
    refresh interval
    current confidence
```

---

**Status:** ✅ **SEALED — Owner-sealed 2026-07-21**
**Authorized by:** Andrew Hannah
**Epic:** EPIC-ASSURANCE-CONTRACT-EVOLUTION-1 (Phase 4)
**Ledger entry:** #213 (status: sealed)

## Implementation Summary

### Semantic Contract
- **`reports/ASSURANCE-CONTRACT-EVIDENCE-FRESHNESS-SEMANTICS-1-ANALYSIS.md`** — Full contract analysis

### Dashboard Script (v1.1 → v1.2 implicitly)
- `scripts/qa_pilot_owner_dashboard.py`:
  - Classification map extended with freshness config (threshold_minutes for records, refresh_interval_seconds for snapshots)
  - `compute_freshness_label()` — class-aware freshness: `current`/`historical`/`archived` for records, `current`/`stale` for snapshots
  - `get_evidence_freshness()` — split output by `records` and `snapshots` with class-aware labels
  - `build_evidence_classification()` — includes freshness_label and age_minutes per item
  - Text renderer updated with classification section showing both freshness band summaries

### Validator
- `scripts/validate-qa-pilot-owner-dashboard.py` — Added EFS-1 through EFS-10

### Verification
- ✅ All 27 checks pass (OD + EPC + EFS)
- ✅ All 13 existing test runner tests pass
- ✅ All 22 classification + freshness unit tests pass
- ✅ Zero storage changes

### Key Invariant
> **age ≠ invalidity** — Records become `historical` (not invalid); snapshots become `stale` (not current).
