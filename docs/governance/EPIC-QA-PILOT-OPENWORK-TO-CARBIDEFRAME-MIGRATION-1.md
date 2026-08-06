# EPIC-QA-PILOT-OPENWORK-TO-CARBIDEFRAME-MIGRATION-1

**Type:** migration (5 sprints)
**Lane:** migration
**Boundary:** QA Pilot-local, browser-app only. No Librarian mutation.
**Librarian impact:** none
**Owner authorization:** `apt_bb2995d2` recorded 2026-07-10T18:53:52Z. Approval basis: *"Approve Option A from `QA-PILOT-SOURCE-OF-TRUTH-RECONCILIATION-1`"*.
**Decision ID:** `OD-qa-pilot-20260710-260710-1`
**Work packet:** `wp-qa-pilot-20260710-1` (authorized, dispatched)
**Approval token expiry:** 2026-07-11T18:53:52Z
**Reconciliation source:** `reports/QA-PILOT-SOURCE-OF-TRUTH-RECONCILIATION-1.md`

---

## 1. Purpose

Migrate the complete QA Pilot application from `/Users/andrew/Desktop/OpenWork/QA Pilot` into `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/browser-app/` while preserving the CarbideFrame QA Pilot governance framework. No further visual parity, styling, or I18N work may continue until the complete application is migrated and validated.

## 2. Target Location

`/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/browser-app/`

Rationale: keep the migrated browser application separate from CarbideFrame governance directories such as `scripts/`, `docs/`, `project-state/`, `receipts/`, `data/`, `config/`, validators, schemas, fixtures, and sprint records.

## 3. Explicit Authorizations (Owner, 2026-07-10)

1. Authorize copying the complete OpenWork QA Pilot application files into `active/qa-pilot/browser-app/`.
2. Preserve all CarbideFrame governance framework files.
3. Preserve current `docs/schemas/browser-assets/` as archived/reference design assets. Do not delete them.
4. Re-scope `EPIC-QA-PILOT-LIBRARIAN-VISUAL-PARITY-CORRECTION-1`; pause remaining visual parity sprints until after migration validation.
5. Re-scope any I18N wiring work; it must be revalidated against the migrated complete application before seal.
6. Leave `/Users/andrew/Desktop/OpenWork/QA Pilot` in place for now as the source-of-truth reference until the migrated CarbideFrame copy is validated and Owner-approved as canonical.

## 4. Required Corrections Before Work

- Correct the reconciliation report/status surfaces if they overstate:
  - visual parity epic progress as Sprint 3/5 when only Sprint 2/5 is verified
  - I18N epic status as complete if repo evidence does not support it
- Both corrections landed in `FEATURE-STATUS.md` and `SESSION-HANDOFF.md` during Sprint 1.

## 5. Bounded Sprint Sequence

| # | Sprint | Status | Purpose |
|---|--------|--------|---------|
| 1 | `QA-PILOT-MIGRATION-PREP-AND-SNAPSHOT-1` | 🔍 in progress | Snapshot CarbideFrame state, archive browser-assets, verify no-overwrite, produce copy manifest |
| 2 | `QA-PILOT-OPENWORK-APP-COPY-1` | ⏳ pending | Copy the complete OpenWork QA Pilot application per the manifest |
| 3 | `QA-PILOT-MIGRATED-APP-SMOKE-VALIDATION-1` | ⏳ pending | Verify file:// open + login/session/portal/course/certificate/admin/sim/QA module/debug panel |
| 4 | `QA-PILOT-CARBIDEFRAME-GOVERNANCE-INTEGRATION-1` | ⏳ pending | Startup surfaces learn browser-app location; governance `data/` stays separate |
| 5 | `QA-PILOT-MIGRATION-ROUNDTRIP-VALIDATION-1` | ⏳ pending | Full roundtrip; final report; recommend canonical status |

## 6. Hard Boundaries

- Do not overwrite CarbideFrame governance files.
- Do not mutate CarbideFrame Librarian files.
- Do not mutate OpenWork QA Pilot source.
- Do not continue visual redesign or I18N wiring during migration.
- Do not add backend, auth service, telemetry, external dependencies, or fake-live behavior.
- Do not mark OpenWork QA Pilot archived or superseded until Owner explicitly approves after validation.
- Do not seal the epic without explicit Owner decision.

## 7. Source Authority

| Class | Authority |
|-------|-----------|
| Owner authorization | `apt_bb2995d2` (this sprint) |
| Reconciliation | `reports/QA-PILOT-SOURCE-OF-TRUTH-RECONCILIATION-1.md` (Option A) |
| CarbideFrame governance framework | `scripts/`, `docs/governance/`, `docs/schemas/`, `fixtures/`, `project-state/sprint-ledger.json` |
| Source of complete application | `/Users/andrew/Desktop/OpenWork/QA Pilot` (read-only during migration) |
| Copy plan | `reports/qa-pilot-migration-copy-manifest-1.json` (Sprint 1 artifact) |
| Overwrite protection | `reports/qa-pilot-migration-overwrite-protection-1.json` (Sprint 1 artifact) |
| Browser-assets archive | `receipts/browser-assets-snapshot.tar.gz` (Sprint 1 artifact) |
| Snapshot receipt | `receipts/migration-prep-snapshot-1.json` (Sprint 1 artifact) |
| Work packet | `wp-qa-pilot-20260710-1` |
| Dispatch | `spd-qa-pilot-20260710-1` |

## 8. Re-scope Posture During Migration

- `EPIC-QA-PILOT-LIBRARIAN-VISUAL-PARITY-CORRECTION-1` — re-scoped to paused. Sprints 1-2 verified (`#153`, `#154`); Sprint 3 (`#155`) re-scoped (incomplete shell); Sprints 4-5 paused. See `reports/QA-PILOT-SOURCE-OF-TRUTH-RECONCILIATION-1.md`.
- `EPIC-QA-PILOT-I18N-WIRING-1` — paused 2026-07-09. 5 sprints run, none sealed. Must be revalidated against the migrated complete application before any seal.
- `EPIC-QA-PILOT-DESIGN-QUALITY-REGRESSION-1` — sealed 2026-07-09 (`#143`–`#147`). No re-scope.
- `EPIC-QA-PILOT-DESIGN-LANGUAGE-REFRESH-1` — sealed 2026-07-09 (`#136`–`#142`). No re-scope.

## 9. Seal Authority

This epic may only be sealed by explicit Owner decision after Sprint 5 produces a final report recommending canonical status. The agent never auto-seals.

## 10. Out of Scope

- Replacing the OpenWork source with the CarbideFrame copy.
- Archiving or superseding OpenWork QA Pilot.
- Re-applying Librarian visual design to the migrated app (handled in a follow-up epic).
- Sealing the I18N epic.
- Sealing any further visual-parity sprint.
- Any change to the CarbideFrame Librarian.
