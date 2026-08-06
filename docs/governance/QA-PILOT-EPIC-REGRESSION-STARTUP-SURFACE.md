# QA Pilot Pipeline Startup Surface — Governance

**Status:** Agent work complete — pending Owner review
**Sprint:** QA-PILOT-EPIC-REGRESSION-STARTUP-SURFACE-1
**Boundary:** QA Pilot-local startup/status surfaces only
**Librarian impact:** none
**Authority:** advisory-only

## Purpose

Expose the completed four-layer QA Pilot advisory pipeline in startup/status surfaces so a new session can immediately report sealed head, active sprint, pipeline posture, and custody boundary.

## Reported Fields

| Field | Description |
|-------|-------------|
| Sealed head | Highest sealed sprint ID and number |
| Active sprint | Currently active (non-sealed) sprint |
| Next authorized sprint | Always "none (awaiting Owner direction)" |
| Pipeline posture | advisory-only |
| Custody | qa-pilot-local |
| Librarian mutation | NONE |
| Pipeline layers | EP / TC / QR / ERS with descriptions |
| Packet counts | Evidence, test cases, result packets, Epic suites |

## Pipeline Layers

| # | Sprint | Prefix | Description | Advisory |
|---|--------|--------|-------------|----------|
| 33 | QA-PILOT-MCP-EVIDENCE-INTAKE-1 | EP- | Bounded evidence packet ingest | ✅ |
| 34 | QA-PILOT-TEST-COMPOSITION-1 | TC- | Evidence → test cases | ✅ |
| 35 | QA-PILOT-RESULT-PACKET-EXPORT-1 | QR- | Evidence + tests → results | ✅ |
| 36 | QA-PILOT-EPIC-REGRESSION-BUILDER-1 | ERS- | EP+TC+QR → Epic suites | ✅ |

## SS Rules

| Rule | Description |
|------|-------------|
| SS-1 | Reports sealed QA Pilot head correctly |
| SS-2 | Reports active sprint correctly |
| SS-3 | Reports next authorized sprint accurately |
| SS-4 | Exposes EP/TC/QR/ERS chain without packet contents |
| SS-5 | Labels all layers advisory-only |
| SS-6 | Reports zero Librarian mutation authority |
| SS-7 | Rejects stale sealed-head claims |
| SS-8 | Rejects active-sprint/ledger mismatches |
| SS-9 | Rejects seal/promotion/canonical-truth authority claims |

## Forbidden

- Reconstructing full packet contents in startup report
- Claiming seal, promotion, canonical-truth, or Librarian-ingest authority
- Reporting Librarian mutation authority as present
