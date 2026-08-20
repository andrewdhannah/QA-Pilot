# LVC-001 — Lifecycle Vocabulary Consolidation

**Sprint ID:** LVC-001
**Project:** qa-pilot
**Phase:** Phase 7 — Adoption & Empirical Validation (P7.1 Cross-Project Trial)
**Status:** PLANNED — awaiting Owner authorization
**Date:** 2026-08-17
**Authority Scope:** restricted

---

## Objective

Consolidate the five-dimensional governance state vocabulary into a canonical, instance-independent model that can be applied consistently to existing and newly created governed system instances.

Resolve vocabulary/state-model ambiguity that obstructs clean cross-project validation.

**This is not architecture expansion.** It resolves a known ambiguity using the existing architecture. The five dimensions already exist as concepts in receipts and work orders — they are not yet persisted independently in the registry.

## Critical Rule

**These dimensions are orthogonal. No dimension may be used as a proxy for another.**

```
entity_type ≠ lifecycle_state ≠ qualification_state ≠ health_state ≠ execution_policy
```

- A healthy entity is not necessarily qualified.
- A qualified entity is not necessarily operational.
- An operational entity is not necessarily permitted to execute a particular operation.

That separation is exactly what Phase 7 needs to validate empirically.

## Canonical Ownership

Each dimension has exactly one authority source. No dimension derives authority from another.

| Dimension | Authority Source | Answers |
|-----------|-----------------|---------|
| `entity_type` | Entity classification authority | What is this entity? |
| `lifecycle_state` | Existing canonical lifecycle model | Where is this entity in its lifecycle? |
| `qualification_state` | Qualification authority | Has it satisfied qualification requirements? |
| `health_state` | Observed health / projection | What is its current observed health? |
| `execution_policy` | Execution-permission policy | What execution behavior is permitted? |

**For `lifecycle_state` in particular:** Do not derive a new enum from the current registry vocabulary. Reuse the already-established canonical lifecycle model. `current_phase`, `current_phase_deprecated`, and numeric `lifecycle_stage` are legacy/projection inputs requiring reconciliation, not competing authorities.

## Instance Independence

The five-dimensional state model describes an instance of the governed system, not just the current QA Pilot registry.

```
                 CANONICAL VOCABULARY
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      Librarian       QA Pilot      New Instance
          │              │              │
     own state       own state       own state
          │              │              │
          └──────────────┴──────────────┘
                   same model
```

A new instance inherits the governance model, not the governance state. The schema is reusable while the state is instance-specific.

### Canonical Bootstrap Contract

```
Create System Instance
        ↓
Apply Canonical Governance Schema
        ↓
Initialize five state dimensions
        ↓
Register system entities
        ↓
Qualify entities
        ↓
Observe health
        ↓
Apply execution policy
```

A new instance does not inherit "Librarian is Operational" or "QA Pilot is Qualified." It inherits the governance model, not the governance state.

---

## Migration Boundary

### Current State

```
Receipts
    └── know the dimensions

Registry
    ├── current_phase
    ├── lifecycle_stage
    └── current_phase_deprecated
```

### Target State

```
Canonical Registry
├── entity_type
├── lifecycle_state
├── qualification_state
├── health_state
└── execution_policy

Legacy fields
├── current_phase
├── lifecycle_stage
└── current_phase_deprecated
       │
       └── reconciliation / migration evidence
```

**Do not silently delete legacy fields in the same operation.** Legacy fields are retained as reconciliation inputs. Their values are projected into canonical dimensions through deterministic migration. The legacy fields themselves become provenance evidence, not competing authorities.

---

## Audit Evidence (Current State)

### Registry Fields (project-index.json)

Current registry carries these fields per entity:

```
project_id, display_name, current_phase, lifecycle_stage, lifecycle_label,
startup_capable, tags, deprecated
```

### What Exists vs. What's Needed

| Dimension | Concept Exists? | In Receipts? | In Registry? | Conflation Found |
|-----------|----------------|-------------|-------------|-----------------|
| entity_type | Yes (WP-003B) | Yes | **No** | Not stored |
| lifecycle_state | Yes (WP-002) | Partial | **No** | `current_phase` used as proxy (values: `execution`, `init` — not canonical enum) |
| qualification_state | Yes (Capability Gate) | Partial | **No** | Not stored |
| health_state | Yes (Health Endpoint) | No | **No** | Not stored |
| execution_policy | Yes (WP-003) | No | **No** | Not stored |

### Conflation Map

| Current Field | Being Used As | Problem |
|---------------|--------------|---------|
| `current_phase` | lifecycle_state proxy | Values (`execution`, `init`) don't match canonical lifecycle enum (`ACTIVE`, `INITIALIZED`, etc.) |
| `current_phase_deprecated` | Duplicate of current_phase | Two fields, same concept, different vocabulary |
| `lifecycle_stage` | Numeric lifecycle position | Unrelated to lifecycle state enum (1=Foundation, 8=Next Cycle) |
| `lifecycle_label` | Human-readable lifecycle | Derivative of lifecycle_stage, not an independent dimension |

---

## Canonical Model

### Legal Enum Values

#### entity_type
```
CAPABILITY            — does work on behalf of the system
SYSTEM_COMPONENT      — enables capabilities, provides substrate
EXTENSION             — optional add-on, may or may not be production
HISTORICAL_LINEAGE    — superseded implementation, retained for evidence
RUNTIME_PROVIDER      — model/tool provider
```

#### lifecycle_state
```
DISCOVERED     — identified, not yet classified
REGISTERED     — in registry, classification pending
INITIALIZED    — setup complete, not yet active
ACTIVE         — operating under governance
SUSPENDED      — temporarily halted
DEPRECATED     — marked for retirement
RETIRED        — no longer active
```

#### qualification_state
```
UNREVIEWED     — not yet evaluated
REVIEW_REQUIRED — evaluation pending
QUALIFIED      — has demonstrated evidence
DISQUALIFIED   — failed qualification
N/A            — not applicable (e.g., SYSTEM_COMPONENT)
```

#### health_state
```
HEALTHY        — observed state matches expected
DEGRADED       — partial failure or drift
STALE          — evidence exceeds freshness threshold
UNKNOWN        — insufficient observation data
```

#### execution_policy
```
AUTO           — can start without approval
OWNER_APPROVAL — requires Owner decision
BLOCKED        — cannot start (dependency or policy)
N/A            — not executable (e.g., SYSTEM_COMPONENT)
```

### Per-Instance Value Examples

| Dimension | Librarian | QA Pilot | New Instance |
|-----------|-----------|----------|-------------|
| entity_type | instance-specific entities | instance-specific entities | instance-specific entities |
| lifecycle_state | current state | current state | independently initialized |
| qualification_state | evidence for Librarian | evidence for QA Pilot | starts according to qualification process |
| health_state | observed | observed | observed |
| execution_policy | applicable policy | applicable policy | applicable policy |

---

## Scope

### In Scope

1. Define the canonical vocabulary for all five dimensions
2. Identify the authoritative enum/source for each dimension
3. Define legal values and semantics
4. Define transitions where transitions actually belong
5. Define projection rules where a value is derived rather than authoritative
6. Populate `entity_type` for all 8 registry entities
7. Complete WP-003B for: Vault, Bibliography, the remaining unclassified entity
8. Add deterministic validation preventing dimension conflation
9. Produce migration/reconciliation evidence for existing registry records
10. Verify that existing Phase 7 workflows consume the canonical dimensions correctly
11. Establish canonical governance state schema as instance-independent contract
12. Define initialization rules for new governed system instances

### Out of Scope

- New lifecycle states
- New assurance primitives
- New governance authority
- Runtime qualification implementation itself (GPI-001)
- Routing changes
- New execution policy mechanisms
- Reworking Phase 7 architecture merely for consistency
- Automatically advancing entities because their fields are now populated

---

## Work Packets

### WP-LVC-001 — Canonical Vocabulary Definition + Governance State Schema

**Purpose:** Define the five dimensions with formal enums, semantics, and transition rules. Establish canonical governance state schema as instance-independent contract.

**Deliverables:**
- `contracts/lifecycle-vocabulary.md` — canonical vocabulary document
- `contracts/lifecycle-vocabulary.schema.json` — machine-checkable schema
- `contracts/governance-state-schema.md` — instance-independent governance contract
- Enum definitions for all 5 dimensions
- Transition rules per dimension
- Projection rules (where derived vs. authoritative)
- Instance boundary rules (what is inherited vs. instance-specific)
- Initialization rules for new governed system instances
- Prohibition on copying another instance's state as authoritative state
- Instance identity as part of state/provenance boundary

**Acceptance Gates:**
- LVC-001-A: Canonical vocabulary exists
- LVC-001-B: Each dimension has one authoritative definition
- LVC-001-P: Canonical vocabulary is instance-independent and reusable across governed system instances

### WP-LVC-002 — Registry Extension

**Purpose:** Add the five dimension fields to the project-index.json registry schema. Preserve legacy fields as provenance.

**Deliverables:**
- Updated `project-index-v2.schema.json` with 5 new fields
- Legacy fields retained (not deleted) with deprecation markers
- Migration script: legacy fields → canonical dimensions
- Before/after state snapshots
- Reconciliation evidence per entity

**Acceptance Gates:**
- LVC-001-C: Dimensions are independently persisted/projected
- LVC-001-K: Reconciliation is evidence-backed

### WP-LVC-003 — Entity Population

**Purpose:** Populate all 5 dimensions for all 8 entities.

**Deliverables:**
- Populated registry records for all 8 entities
- Classification evidence per entity
- WP-003B completion for vault + bibliography + remaining

**Acceptance Gates:**
- LVC-001-G: All 8 registry entities have entity_type
- LVC-001-H: WP-003B remaining entities reconciled

### WP-LVC-004 — Conflation Detection

**Purpose:** Add validation preventing dimension conflation.

**Critical invariant:** Detection of conflation may produce a Finding; it must not automatically repair or mutate the affected state. This preserves the established boundary:

```
Evidence → Finding → Disposition → Owner Decision → Mutation → Receipt
```

**Deliverables:**
- Validator script: `scripts/validate-lifecycle-vocabulary.py`
- Rules detecting:
  - lifecycle_state used as qualification_state
  - health_state implying qualification
  - qualification_state implying execution permission
- Test fixtures (valid + invalid)
- All findings routed to disposition pipeline, never auto-repaired

**Acceptance Gates:**
- LVC-001-D: No lifecycle state is being used as qualification state
- LVC-001-E: No health state implies qualification
- LVC-001-F: No qualification state implies execution permission
- LVC-001-J: Invalid/conflated combinations are detected

### WP-LVC-005 — Consumer Verification

**Purpose:** Verify existing Phase 7 workflows consume canonical dimensions correctly.

**Deliverables:**
- Audit of existing consumers (capability gate, health endpoint, lifecycle cursor)
- Evidence that consumers read from canonical fields
- Regression test: existing behavior unchanged

**Acceptance Gates:**
- LVC-001-I: Existing consumers use canonical dimensions
- LVC-001-L: Existing Phase 7 behavior remains intact

### WP-LVC-006 — Architecture Freeze Guard

**Purpose:** Ensure LVC-001 does not introduce new assurance primitives or unauthorized mutations.

**Deliverables:**
- Architecture freeze compliance check
- Mutation audit: no unauthorized lifecycle mutations
- Replay test: same classification from same inputs

**Acceptance Gates:**
- LVC-001-M: No new assurance primitive introduced
- LVC-001-N: No unauthorized lifecycle mutation occurs
- LVC-001-O: Replay produces the same classification

---

## Acceptance Gates (Summary)

| Gate | Question | Work Packet |
|------|----------|-------------|
| LVC-001-A | Canonical vocabulary exists | WP-LVC-001 |
| LVC-001-B | Each dimension has one authoritative definition | WP-LVC-001 |
| LVC-001-C | Dimensions are independently persisted/projected | WP-LVC-002 |
| LVC-001-D | No lifecycle state is being used as qualification state | WP-LVC-004 |
| LVC-001-E | No health state implies qualification | WP-LVC-004 |
| LVC-001-F | No qualification state implies execution permission | WP-LVC-004 |
| LVC-001-G | All 8 registry entities have entity_type | WP-LVC-003 |
| LVC-001-H | WP-003B remaining entities reconciled | WP-LVC-003 |
| LVC-001-I | Existing consumers use canonical dimensions | WP-LVC-005 |
| LVC-001-J | Invalid/conflated combinations are detected | WP-LVC-004 |
| LVC-001-K | Reconciliation is evidence-backed | WP-LVC-002 |
| LVC-001-L | Existing Phase 7 behavior remains intact | WP-LVC-005 |
| LVC-001-M | No new assurance primitive introduced | WP-LVC-006 |
| LVC-001-N | No unauthorized lifecycle mutation occurs | WP-LVC-006 |
| LVC-001-O | Replay produces the same classification | WP-LVC-006 |
| LVC-001-P | Canonical vocabulary is instance-independent and reusable across governed system instances | WP-LVC-001 |

**16 gates total.** Strongest gates: C/D/E/F (dimension independence), G/H (classification gap closure), I (consumer integration), K (evidence-backed migration), M/N (freeze + authority protection), O (replayability), P (instance independence).

---

## Completion Criterion

**Not merely:** "All eight entities now have five fields."

**Instead:** The system can represent and reason about the five dimensions independently, existing governed workflows no longer require vocabulary conflation to operate, and the canonical model can be applied to a new governed system instance without inheriting another instance's state.

This makes LVC-001 meaningful to P7.1 rather than administrative cleanup. It becomes the governance-state bootstrap contract for future Librarian/QA-Pilot-class systems, without introducing a new assurance primitive.

---

## Dependency Chain

```
GIR-001 (complete) ✅
        ↓
LVC-001 (this sprint) ← YOU ARE HERE
        ↓
WP-003B completion (vault + bibliography)
        ↓
GPI-001 Runtime Qualification
```

GPI-001 stays behind LVC-001 + WP-003B. Runtime qualification is precisely the sort of mechanism that becomes ambiguous if the underlying lifecycle/qualification vocabulary is still unstable.

---

## Architecture Freeze Compliance

Because QA Pilot is already in Phase 7 empirical validation:

**LVC-001 should prove that the existing architecture can express the required distinction, not create another layer to express it.**

That is the right interpretation of the "no new assurance primitives until Phase 7 demonstrates unmet requirements" freeze.

### Freeze Guard Checks

| Check | Status |
|-------|--------|
| New assurance primitives? | No — vocabulary consolidation only |
| New governance authority? | No — existing authority model preserved |
| New lifecycle states? | No — canonicalizing existing concepts |
| Routing changes? | No — data model only |
| Execution policy mechanisms? | No — field definition only |
| Instance state inheritance? | No — new instances start independently |

---

## Evidence Required

- [ ] Before snapshot: current registry state (8 entities, existing fields)
- [ ] Canonical vocabulary document
- [ ] Governance state schema (instance-independent)
- [ ] Schema definition
- [ ] Migration script + evidence
- [ ] Populated registry (after)
- [ ] Validator script + test results
- [ ] Consumer audit results
- [ ] Architecture freeze compliance check
- [ ] Replay test results
- [ ] Instance independence verification

---

## Stop Conditions

Stop immediately if:
- LVC-001 requires new assurance primitives
- Migration requires guessing authority state
- Existing Phase 7 behavior regresses
- Canonical model requires reworking Phase 7 architecture
- Instance independence cannot be achieved without new authority

---

## Authorization Posture

```
LVC-001
Status: READY FOR AUTHORIZATION

WP-LVC-001  Canonical Vocabulary + Governance State Schema
WP-LVC-002  Registry Extension
WP-LVC-003  Entity Population
WP-LVC-004  Conflation Detection
WP-LVC-005  Consumer Verification
WP-LVC-006  Architecture Freeze Guard

Acceptance Gates: A–P (16 gates)
New Authority: NONE
New Assurance Primitives: NONE
Runtime Qualification: NOT IN SCOPE
Routing: NOT IN SCOPE
Instance Independence: IN SCOPE (schema-level only)
```
