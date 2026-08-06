# QA-PILOT-POST-CANONICAL-SURFACE-REASSESSMENT-1 — Post-Canonical Surface Reassessment

**Type:** planning / reassessment
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** planning
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Dependencies:** DWR-004 sealed (validation environment trustworthy); DWR-005 sealed (identity aligned)

---

## Purpose

Reassess Visual Parity and I18N against the Owner-approved canonical QA Pilot state. This is not an implementation sprint. It produces planning evidence.

**Why now:** The canonical state is established, identity metadata is aligned, and the validation environment is trustworthy. The foundation is suitable for generating reliable reassessment evidence.

---

## Scope

### Track A — Visual Parity Reassessment (DWR-001)

| # | Area | Action |
|---|------|--------|
| 1 | Current UI state | Evaluate against intended parity target |
| 2 | Paused work | Reconcile assumptions from Sprints #153–#155 |
| 3 | Missing surfaces | Identify incomplete or absent UI components |
| 4 | Component alignment | Document gaps between current and intended state |

**Output:** `VISUAL-PARITY-REASSESSMENT.md`

Containing:
- Current state
- Gap inventory
- Impact classification
- Recommended implementation scope
- Proposed future sprint breakdown

### Track B — I18N Revalidation (DWR-002)

| # | Area | Action |
|---|------|--------|
| 1 | Key coverage | Evaluate existing language key coverage |
| 2 | Runtime usage | Validate keys are actually used in application |
| 3 | Missing translations | Identify untranslated strings |
| 4 | Orphan keys | Find keys defined but not used |
| 5 | Integration | Verify alignment with canonical application state |

**Output:** `I18N-REASSESSMENT.md`

Containing:
- Coverage findings
- Runtime validation
- Missing seams
- Recommended completion plan

### Explicit Non-Scope

This sprint must not:

- Implement visual corrections
- Add translations
- Redesign UI components
- Modify governance validators
- Modify canonical identity
- Consume DWR-003 (Librarian QA packet export)

**The output is a decision-quality plan, not execution.**

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| SR-1 | Canonical baseline reference confirmed |
| SR-2 | Visual parity current state documented |
| SR-3 | I18N runtime state documented |
| SR-4 | Previous paused work reconciled |
| SR-5 | Implementation recommendations produced |
| SR-6 | Evidence package produced |
| SR-7 | No feature changes made |

---

## Evidence Contract

This sprint produces exactly:

```
docs/sprints/QA-PILOT-POST-CANONICAL-SURFACE-REASSESSMENT-1-EVIDENCE.md
```

Containing:
- Track A findings (Visual Parity)
- Track B findings (I18N)
- Gap inventories
- Implementation recommendations
- Scope compliance confirmation

Plus two track-specific outputs:
- `docs/planning/VISUAL-PARITY-REASSESSMENT.md`
- `docs/planning/I18N-REASSESSMENT.md`

---

## Sprint Boundary

| Constraint | Value |
|------------|-------|
| Project boundary | QA Pilot-local |
| Librarian mutation | none |
| Cross-project mutation | none |
| File scope | `browser-app/` (read-only inspection), `docs/planning/` (new outputs) |
| Write scope | Reassessment documents, evidence document |
| Read-only scope | Application UI, language files, governance metadata |

---

## Resulting State

| Track | Before | After |
|-------|--------|-------|
| DWR-001 (Visual Parity) | Paused, old assumptions | Re-plan available |
| DWR-002 (I18N) | Paused, old assumptions | Re-validation complete |
| Future implementation | Not ready | Ready for authorization |

---

## Decision Point After Completion

The Owner decides:
- Authorize Visual Parity implementation
- Authorize I18N completion
- Defer or reject based on findings

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Authorized by:** Andrew Hannah
**Ledger entry:** #169 (authorized)
