# Owner Decision Receipt — OD-QA-PILOT-QUALIFICATION-EVIDENCE-PIPELINE-1-AUTHORIZATION

**Sprint:** QA-PILOT-QUALIFICATION-EVIDENCE-PIPELINE-1
**Type:** Implementation — evidence ingestion
**Decision:** ✅ Authorized
**Decision date:** 2026-07-16
**Owner:** Andrew Hannah
**Authorization basis:** "Then authorize: QA-PILOT-QUALIFICATION-EVIDENCE-PIPELINE-1"

---

## Authorized Scope

| Area | Deliverable |
|------|-------------|
| Evidence source adapters | Read interfaces for each QA Pilot layer that produces qualification-relevant data |
| Layer discovery | Auto-detection of existing QA Pilot layers that can serve as evidence sources |
| Evidence normalization | Convert layer-specific formats into governed evidence records |
| QR population | Create QR- records from normalized evidence |
| Provenance linking | Chain each QR back to its source artifact via evidence_refs |
| Qualification store ingestion | Write QR- records into `data/qualification-records/` with index updates |
| Evidence collection receipts | Produce collection receipts documenting what was ingested, from where, and when |
| Pipeline validation fixtures | Fixtures proving the ingestion pipeline processes evidence correctly |

## Guardrails

- ❌ No new qualification rules (QR-1 through QR-25 are final)
- ❌ No QR schema modification unless evidence gap exposed (must prove the need)
- ❌ No qualification decisions — evaluation engine belongs to execution sprint
- ✅ Advisory-only posture maintained throughout

## Dependencies

| Dependency | Relationship |
|-----------|-------------|
| QA-PILOT-QUALIFICATION-SCHEMA-1 (#161) | ✅ Sealed — provides QR- schema, validator, store |
| QA Pilot sealed layers (#1–#160) | Evidence sources — read-only access |
| Qualification Landscape Catalog | Layer classification for adapter targeting |

## Authority Boundary

| Dimension | Allowed | Prohibited |
|-----------|---------|------------|
| QR- schema | Read and validate against | ❌ Modify unless gap proven |
| Existing QA Pilot layers | Read evidence from | ❌ Modify any existing file |
| Qualification store | Write QR- records | ❌ Modify existing QR- records retroactively |
| docs/planning/* | Create new planning docs | — |
| Librarian governance contracts | Read-only reference | ❌ Implementation files |
| Cross-project | — | ❌ No cross-project writes |
| Seal | — | ❌ No seal authority |
