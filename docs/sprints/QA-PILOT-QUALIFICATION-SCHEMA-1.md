# Sprint Receipt — QA-PILOT-QUALIFICATION-SCHEMA-1

**Ledger:** Pending — awaiting seal
**Lane:** implementation / qualification
**Type:** Substantive capability — qualification substrate
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none
**Authorization:** Owner-authorized 2026-07-16 per "Proceeding with QA-PILOT-QUALIFICATION-SCHEMA-1 is the correct next implementation step"
**Predecessor:** QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1 (planning sprint)

---

## Goal

Deploy the canonical qualification record model: QR- schema, validator, fixtures, and qualification store. Establish the substrate that every later qualification capability depends on.

## Proof of Completion

| Acceptance Criterion | Evidence | Status |
|---------------------|----------|--------|
| QR schema implemented | `docs/schemas/qa-pilot-qualification-record.schema.json` | ✅ |
| Schema validation implemented | `scripts/validate-qa-pilot-qualification.py` (4 modes, 25 QR rules) | ✅ |
| Valid fixtures pass | 7/7 valid fixtures pass (all levels + types + exempt) | ✅ |
| Invalid fixtures rejected | 8/8 invalid fixtures rejected (QR-2 through QR-25 violations) | ✅ |
| Qualification store created | `data/qualification-records/` with `qualification-index.json` | ✅ |
| Receipt inheritance validated | Evidence lineage test: QR → evidence_ref → source file chain verified | ✅ |
| Sprint receipt sealed | This document | ✅ |

## Deliverables

### Schema
- `docs/schemas/qa-pilot-qualification-record.schema.json` — Draft 2020-12, 25+ properties, 11 required, conditional required per qualification_type

### Validator
- `scripts/validate-qa-pilot-qualification.py` — 4 modes (fixture, live, validate, chain), 25 business rules (QR-1 through QR-25)

### Fixtures (15 total)

**Valid (7):**
| Fixture | Qualification Type | Level | Tests |
|---------|-------------------|-------|-------|
| `valid/artifact-spot-checked.json` | artifact | spot_checked | QR-1–QR-25 pass |
| `valid/artifact-peer-reviewed.json` | artifact | peer_reviewed | QR-1–QR-25 pass |
| `valid/artifact-audited.json` | artifact | audited | QR-1–QR-25 pass |
| `valid/process-peer-reviewed.json` | process | peer_reviewed | QR-1–QR-25 pass |
| `valid/reviewer-audited.json` | reviewer | audited | QR-1–QR-25 pass |
| `valid/exempt-by-policy.json` | artifact | exempt | QR-1–QR-25 pass |
| `valid/unqualified-no-evidence.json` | artifact | unqualified | QR-1–QR-25 pass |

**Invalid (8):**
| Fixture | Violation | Rule |
|---------|-----------|------|
| `invalid/missing-required-field.json` | Missing required fields | QR-2 |
| `invalid/authority-claiming.json` | `sealed_by` field present | QR-9 |
| `invalid/bad-custody.json` | `custody: librarian-managed` | QR-7 |
| `invalid/stale-evidence.json` | Evidence >90d old | QR-14 |
| `invalid/bad-level-for-score.json` | audited with 0.62 score | QR-17 |
| `invalid/audited-insufficient-evidence.json` | audited with 1 evidence_ref | QR-18 |
| `invalid/expired-qualification.json` | Past expiry date | QR-19 |
| `invalid/reviewer-no-decision-evidence.json` | reviewer type without owner_decision | QR-25 |

### Qualification Store
- `data/qualification-records/qualification-index.json` — Index file
- `data/qualification-records/` — Record storage directory

### Test Runners
- `scripts/test-qa-pilot-qualification.sh` — 32 acceptance gates (17 main + 15 sub-checks)
- `scripts/test-qualification-receipt-inheritance.sh` — 6 evidence lineage gates

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| **DD-1**: QR- record_id pattern `QR-[A-Z0-9]{4,12}-[0001-9999]` | Flexible middle segment allows type codes (ART, PRO, REV) and padded sequences |
| **DD-2**: 5 qualification levels (unqualified, spot_checked, peer_reviewed, audited, exempt) | Covers the full spectrum from no-evidence to formal-audit, plus policy-based exemption |
| **DD-3**: 25 QR validation rules with severity (error vs warning) | Error rules block processing; warning rules flag but don't block — matches established QA Pilot pattern |
| **DD-4**: Store is file-backed with JSON index | Matches existing QA Pilot data stores (evidence, receipts, custody). No DB dependency. |
| **DD-5**: conditionalRequired for qualification_type | Artifact requires scores, process requires lifecycle+provenance, reviewer requires provenance+evidence |
| **DD-6**: advisory_only=true is a const (immutable) | Prevents any QR- record from being used to authorize work |

## Authority Boundary Enforcement

- All records enforce `advisory_only: true`, `custody: qa-pilot-local`, `librarian_impact: none`
- QR-9 rejects any record containing authority-claiming fields (sealed, approved, executed, etc.)
- QR-6 makes `advisory_only: true` immutable (const in schema)
- No auto-seal, no ledger mutation, no Librarian mutation
- QR- records qualify artifacts — they do not authorize action

## Validation

| Suite | Result |
|-------|--------|
| Fixture validation (7 valid fixtures) | ✅ 7/7 pass |
| Fixture validation (8 invalid fixtures) | ✅ 8/8 rejected |
| Full test runner (32 gates) | ✅ 32/32 pass |
| Receipt inheritance (6 gates) | ✅ 6/6 pass |
| Validator chain self-test | ✅ PASS |

## Files Created

| File | Purpose |
|------|---------|
| `docs/schemas/qa-pilot-qualification-record.schema.json` | QR- schema (Draft 2020-12) |
| `scripts/validate-qa-pilot-qualification.py` | 4-mode validator, 25 QR rules |
| `docs/examples/qa-pilot-qualification/valid/artifact-spot-checked.json` | Valid fixture |
| `docs/examples/qa-pilot-qualification/valid/artifact-peer-reviewed.json` | Valid fixture |
| `docs/examples/qa-pilot-qualification/valid/artifact-audited.json` | Valid fixture |
| `docs/examples/qa-pilot-qualification/valid/process-peer-reviewed.json` | Valid fixture |
| `docs/examples/qa-pilot-qualification/valid/reviewer-audited.json` | Valid fixture |
| `docs/examples/qa-pilot-qualification/valid/exempt-by-policy.json` | Valid fixture |
| `docs/examples/qa-pilot-qualification/valid/unqualified-no-evidence.json` | Valid fixture |
| `docs/examples/qa-pilot-qualification/invalid/missing-required-field.json` | Invalid fixture |
| `docs/examples/qa-pilot-qualification/invalid/authority-claiming.json` | Invalid fixture |
| `docs/examples/qa-pilot-qualification/invalid/bad-custody.json` | Invalid fixture |
| `docs/examples/qa-pilot-qualification/invalid/stale-evidence.json` | Invalid fixture |
| `docs/examples/qa-pilot-qualification/invalid/bad-level-for-score.json` | Invalid fixture |
| `docs/examples/qa-pilot-qualification/invalid/audited-insufficient-evidence.json` | Invalid fixture |
| `docs/examples/qa-pilot-qualification/invalid/expired-qualification.json` | Invalid fixture |
| `docs/examples/qa-pilot-qualification/invalid/reviewer-no-decision-evidence.json` | Invalid fixture |
| `data/qualification-records/qualification-index.json` | Qualification store index |
| `scripts/test-qa-pilot-qualification.sh` | 32-gate acceptance test runner |
| `scripts/test-qualification-receipt-inheritance.sh` | Evidence lineage validation |
| `docs/sprints/QA-PILOT-QUALIFICATION-SCHEMA-1.md` | This sprint receipt |

## Files Modified

None. All files are new — no existing governance files were modified.

## Next

Awaiting Owner seal decision. Next authorized sprint: **QA-PILOT-QUALIFICATION-EVIDENCE-PIPELINE-1**.
