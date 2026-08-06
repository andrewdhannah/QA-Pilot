# ASSURANCE-ADOPTION-AGENT-BRIDGE-BASELINE-1 — Agent Bridge Adoption Baseline

**Type:** adoption / onboarding (Phase 2)
**Status:** ✅ **SEALED — Owner-sealed 2026-07-21**
**Lane:** assurance
**Boundary:** QA Pilot-local (reads Agent Bridge state)
**Librarian impact:** none
**Epic:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (Phase 2)
**Dependencies:** ASSURANCE-ADOPTION-LIBRARIAN-ADAPTERS-1 (#208, sealed)

---

## Purpose

Validate that the assurance model remains meaningful around runtime/integration behavior — does assurance transfer from governance-shaped evidence to execution-shaped evidence?

## Primary Question

Can Agent Bridge express its operational state through the existing assurance model without introducing Agent Bridge-specific assurance semantics?

## Key Success Signal

Not "everything maps." A good outcome may be:
- **Direct mapping** for governance and receipts
- **Adapters** for runtime evidence
- **Explicit gaps** for capabilities Agent Bridge does not possess

Absence of a capability is valid assurance information.

---

## Recommended Mapping Areas

| Assurance concept | Agent Bridge candidate source |
|---|---|
| Project identity | Agent Bridge registry/project metadata |
| Evidence lineage | Execution receipts, integration records, validation outputs |
| Ownership | Agent authority boundaries |
| Governance records | Decision receipts and lifecycle events |
| Operational state | Bridge health, contracts, validation outcomes |
| Risk signals | Failed validations, unresolved integration conditions |

---

## Acceptance Gates

| Gate | Validation |
|------|-----------|
| AB-AD-1 | Agent Bridge identity mapped |
| AB-AD-2 | Runtime/integration evidence sources identified |
| AB-AD-3 | Existing receipts map into evidence lineage |
| AB-AD-4 | Ownership boundaries preserved |
| AB-AD-5 | Missing assurance capabilities remain visible |
| AB-AD-6 | No Agent Bridge concepts promoted into core model prematurely |
| AB-AD-7 | Adoption friction measured |
| AB-AD-8 | Adapter requirements classified |

---

## Scope

1. Map Agent Bridge project structure to assurance model
2. Assess whether MCP/integration evidence sources fit existing concepts
3. Identify new friction points not surfaced by Librarian adoption
4. Measure whether adapter requirements differ in kind (not just degree)
5. Classify each gap as: direct mapping, adapter needed, or explicit absence

## Non-Scope

- Core model modification
- Adapter construction (deferred to Phase 2b or Phase 3)
- Runtime Node onboarding (Phase 3)
- Contract extraction (Phase 4)
- Any Agent Bridge-specific assurance concept promotion

---

## Status

**Status:** ✅ **SEALED — Owner-sealed 2026-07-21**
**Sealed by:** Andrew Hannah
**Epic:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (Phase 2)
**Ledger entry:** #209 (status: sealed)
