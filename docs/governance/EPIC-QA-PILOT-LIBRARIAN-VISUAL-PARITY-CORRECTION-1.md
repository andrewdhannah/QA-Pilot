# EPIC-QA-PILOT-LIBRARIAN-VISUAL-PARITY-CORRECTION-1 — Visual Parity Correction

**Status:** Authorized — Owner-approved 2026-07-09
**Decision ID:** `OD-EPIC-QA-PILOT-LIBRARIAN-VISUAL-PARITY-CORRECTION-1-AUTHORIZATION`
**Design reference:** Current CarbideFrame Librarian frontend (active/librarian/Public/)
**I18N epic paused:** EPIC-QA-PILOT-I18N-WIRING-1 (#148-#152) — deferred until parity correction complete

## Sprint Sequence

| # | Sprint | Purpose |
|---|--------|---------|
| 1 | QA-PILOT-LIBRARIAN-VISUAL-PARITY-REFERENCE-AUDIT-1 | Reference audit, mismatch matrix |
| 2 | QA-PILOT-LANDING-SHELL-PARITY-REMEDIATION-1 | Landing page shell redesign |
| 3 | QA-PILOT-ADMIN-LEARNER-PARITY-REMEDIATION-1 | Admin + learner pages redesign |
| 4 | QA-PILOT-EXPORT-IMPORT-CERTIFICATE-PARITY-REMEDIATION-1 | Export/import/cert pages redesign |
| 5 | QA-PILOT-LIBRARIAN-VISUAL-PARITY-VALIDATION-1 | Final validation + seal recommendation |

## Authority Boundaries
- No Librarian file mutation
- No backend, auth, telemetry, external dependencies
- No fake-live status
- Prior design claims must be verified against current Librarian source
