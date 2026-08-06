# ASSURANCE-CONTRACT-EVIDENCE-STATE-SEPARATION-1 — Evidence State Separation

**Type:** contract evolution (Phase 4)
**Status:** ✅ **SEALED — Owner-sealed 2026-07-21**
**Lane:** contract_extraction
**Boundary:** QA Pilot-local (reads all 4 consumer projects)
**Librarian impact:** contract_interface (produces schema recommendation)
**Epic:** EPIC-ASSURANCE-CONTRACT-EVOLUTION-1 (Phase 4)
**Dependencies:** ASSURANCE-ADOPTION-RUNTIME-NODE-BASELINE-1 (#210, sealed)

---

## Purpose

Define and validate whether the assurance model requires a first-class distinction between historical proof and current observed state.

## Primary Question

Does the assurance model require a first-class distinction between `assurance_record` (historical proof) and `assurance_snapshot` (current observed state)?

The adoption evidence strongly indicates yes.

---

## Proposed Contract Boundary

### `assurance_record`

**Represents:** What was established through a governed evidence event.

**Properties:**
- immutable
- timestamped
- attributable
- evidence-linked
- historical

**Examples:**
- qualification completed
- validation passed
- receipt issued
- artifact hash verified
- audit result captured

### `assurance_snapshot`

**Represents:** What is observed about the system at a particular point in time.

**Properties:**
- refreshable
- time-bound
- environment-dependent
- observational
- non-authoritative over history

**Examples:**
- runtime healthy
- service reachable
- process active
- model loaded
- current resource availability

---

## Core Constraint

> Do not begin by changing storage structures.

First establish:
1. Semantic model
2. Contract boundaries
3. Compatibility requirements
4. Migration implications

Only then decide whether implementation changes are required. The strongest outcome may be: new schema fields, a new projection contract, documentation changes, or a combination.

---

## Acceptance Gates

| Gate | Validation |
|------|-----------|
| ESS-1 | Existing assurance records map cleanly into `assurance_record` |
| ESS-2 | Runtime observations map into `assurance_snapshot` |
| ESS-3 | Snapshots cannot mutate historical records |
| ESS-4 | Records cannot imply current operational state |
| ESS-5 | Dashboard can distinguish historical proof from current observation |
| ESS-6 | Owner decisions reference the correct evidence class |
| ESS-7 | Existing QA Pilot behavior remains compatible |
| ESS-8 | Librarian/Agent Bridge/Runtime Node mappings remain valid |
| ESS-9 | Schema evolution impact documented |
| ESS-10 | Migration path defined if contract change is accepted |

---

## Scope

1. Define `assurance_record` semantic model
2. Define `assurance_snapshot` semantic model
3. Map all 4 consumer evidence types to the new distinction
4. Validate universality across shapes
5. Assess minimum schema change
6. Assess backward compatibility
7. Validate dashboard/projection improvement
8. Produce contract recommendation

## Non-Scope

- Storage structure changes (deferred — semantic model first)
- Compound identity promotion (deferred)
- Runtime-specific adapter construction (deferred)
- Broad core model overhaul

---

## Cross-Consumer Evidence Mapping

| Consumer | assurance_record candidates | assurance_snapshot candidates |
|----------|---------------------------|------------------------------|
| QA Pilot | Pipeline receipts, findings, test results | (none — lifecycle artifacts only) |
| Librarian | Receipts, sprint ledger entries, release gates | (none — governance artifacts only) |
| Agent Bridge | Intake receipts, custody artifacts, audit trails | Queue state, pairing state, status |
| Runtime Node | Qualification records, integration receipts, proof chain | Health checks, port state, process state, service status |

---

**Status:** ✅ **SEALED — Owner-sealed 2026-07-21**
**Sealed by:** Andrew Hannah
**Epic:** EPIC-ASSURANCE-CONTRACT-EVOLUTION-1 (Phase 4)
**Ledger entry:** #211 (status: sealed)

## Analysis Output

**Report:** `reports/ASSURANCE-CONTRACT-EVIDENCE-STATE-SEPARATION-1-ANALYSIS.md`
