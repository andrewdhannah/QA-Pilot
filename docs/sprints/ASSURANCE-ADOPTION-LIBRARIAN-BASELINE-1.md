# ASSURANCE-ADOPTION-LIBRARIAN-BASELINE-1 — Librarian Adoption Baseline

**Type:** adoption / onboarding
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** assurance
**Boundary:** QA Pilot-local (reads Librarian state)
**Librarian impact:** integration_interface (read-only)
**Epic:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (Phase 1)
**Dependencies:** QA-PILOT-ASSURANCE-GOVERNANCE-MATURITY-1 (#206, sealed)

---

## Purpose

Validate that the assurance operating layer can onboard an additional project (The Librarian) while preserving a common assurance model and independent project authority.

## Key Questions

- Does the assurance language map naturally to another project's reality?
- Which concepts are truly universal versus QA Pilot-specific?
- Where does onboarding friction appear?
- Which evidence sources are easy to connect, and which require adapters?
- Does the Owner view remain useful when project structures differ?

## Scope

1. Map Librarian artifacts (governance files, receipts, lifecycle records, sprint data) into the common assurance model
2. Identify missing mappings and gaps
3. Measure onboarding effort and friction points
4. Produce an adoption baseline report

## Non-Scope

- Modifying Librarian files or governance
- Creating Librarian-specific assurance schema forks
- Full multi-project routing (Phase 2)
- Contract extraction or generalization (Phase 4)

## Acceptance Gates

| Gate | Validation Target |
|------|-------------------|
| AD-1 | Librarian artifacts mapped to assurance model |
| AD-2 | Missing mappings documented |
| AD-3 | Onboarding effort measured |
| AD-4 | Friction points identified |
| AD-5 | No Librarian files modified |
| AD-6 | Existing QA Pilot assurance unchanged |

---

**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Authorized by:** Andrew Hannah
**Epic:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (Phase 1)
**Ledger entry:** #207 (status: authorized)
