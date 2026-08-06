# QA-PILOT-CANONICAL-IDENTITY-METADATA-CORRECTION-1 — Canonical Identity Metadata Correction

**Type:** governance / metadata correction
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** governance
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Dependencies:** Canonical transition complete (ODR-PROMOTE-TO-CANONICAL-0001); DWR-005

---

## Purpose

Update canonical identity metadata to match the Owner-approved canonical state. This is identity reconciliation, not feature work.

**Why this is first:** The canonical state now exists. Future evidence must reference that canonical identity. Leaving stale identity metadata in place would allow future artifacts to generate avoidable ambiguity.

---

## Scope

### Included

| # | Area | Action |
|---|------|--------|
| 1 | PROJECT-IDENTITY.md `canonical_repo` | Update from old CarbideFrame path to Owner-approved canonical path |
| 2 | Historical references | Preserve — do not remove migration source references, historical OpenWork references, migration evidence paths |
| 3 | Identity consumers | Validate startup/readiness surfaces, project selectors, evidence references, documentation links, generated metadata |
| 4 | Reconciliation evidence | Produce evidence document with changed field, previous value, new value, reason, validation performed |

### Explicit Non-Scope

This sprint must not:

- Repair governance validators (DWR-004)
- Modify Visual Parity work (DWR-001)
- Modify I18N work (DWR-002)
- Alter migration history
- Rewrite old evidence
- Change canonical decision records (ODR-PROMOTE-TO-CANONICAL-0001 is immutable)

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| ID-1 | Canonical identity metadata points to Owner-approved canonical path |
| ID-2 | Historical migration references preserved |
| ID-3 | No evidence references resolve to invalid identity |
| ID-4 | Startup/project metadata remains consistent |
| ID-5 | Change evidence produced |
| ID-6 | No unrelated files modified |

---

## Evidence Contract

This sprint produces exactly:

```
QA-PILOT-CANONICAL-IDENTITY-METADATA-CORRECTION-1-EVIDENCE.md
```

The evidence document contains:

| # | Section | Purpose |
|---|---------|---------|
| 1 | Changed field | What was modified |
| 2 | Previous value | What it was before |
| 3 | New value | What it is now |
| 4 | Reason | Why the change was made |
| 5 | Validation performed | What was checked to confirm the change is correct |

---

## Deliverables

| Artifact | Location | Purpose |
|----------|----------|---------|
| Sprint record | `docs/sprints/QA-PILOT-CANONICAL-IDENTITY-METADATA-CORRECTION-1.md` (this document) | Sprint trace |
| Change evidence | `docs/sprints/QA-PILOT-CANONICAL-IDENTITY-METADATA-CORRECTION-1-EVIDENCE.md` | Reconciliation evidence |

---

## Resulting State

| State | Before | After |
|-------|--------|-------|
| Canonical state | Established | Established |
| Identity metadata | Drift present | Aligned |
| Future evidence chain | At risk of ambiguity | Stable |

---

## Sprint Boundary

| Constraint | Value |
|------------|-------|
| Project boundary | QA Pilot-local |
| Librarian mutation | none |
| Cross-project mutation | none |
| File scope | `PROJECT-IDENTITY.md`, identity consumers (read-only verification) |
| Write scope | `PROJECT-IDENTITY.md` (canonical_repo field), evidence document |
| Read-only scope | All governance metadata, startup surfaces, evidence references |

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Authorized by:** Andrew Hannah
**Ledger entry:** #167 (authorized)
