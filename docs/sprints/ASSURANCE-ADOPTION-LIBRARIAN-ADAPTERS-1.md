# ASSURANCE-ADOPTION-LIBRARIAN-ADAPTERS-1 — Librarian Adapters

**Type:** adoption / integration
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** assurance
**Boundary:** QA Pilot-local (reads Librarian state)
**Librarian impact:** integration_interface (read-only)
**Epic:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (Phase 1)
**Dependencies:** ASSURANCE-ADOPTION-LIBRARIAN-BASELINE-1 (#207, sealed)

---

## Purpose

Create the minimum translation layer required for Librarian assurance projection without modifying the core assurance model.

## Scope

1. Map Librarian evidence sources (receipts, git history) into evidence freshness
2. Normalize path conventions for Librarian's file layout
3. Enable `dashboard --multi-project` to consume Librarian assurance state
4. Document adapter boundaries for future consumers

## Non-Scope

- Modifying the core assurance model
- Creating new project-specific assurance concepts
- Modifying Librarian files
- Agent Bridge or Runtime Node onboarding

## Acceptance Gates

| Gate | Validation Target |
|------|-------------------|
| AD-AD-1 | Adapter maps Librarian evidence sources |
| AD-AD-2 | Path conventions normalized |
| AD-AD-3 | Dashboard can consume Librarian assurance state |
| AD-AD-4 | QA Pilot behavior unchanged |
| AD-AD-5 | No new project-specific assurance concepts introduced |

---

**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Authorized by:** Andrew Hannah
**Epic:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (Phase 1)
**Ledger entry:** #208 (status: authorized)
