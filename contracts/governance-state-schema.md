# Canonical Governance State Schema

**Sprint:** LVC-001 — Lifecycle Vocabulary Consolidation
**Status:** Authoritative
**Instance Scope:** All governed system instances
**Date:** 2026-08-17

---

## Purpose

Define the instance-independent governance state contract. This schema is reusable across governed system instances (Librarian, QA Pilot, future instances). The schema is shared; the state is instance-specific.

---

## Contract

### What this schema governs

An instance of a governed system contains entities. Each entity has five orthogonal state dimensions. This schema defines:

1. The five dimensions and their legal values
2. The authority source for each dimension
3. The applicability rules by entity type
4. The instance boundary (what is shared vs. instance-specific)
5. The initialization rules for new instances
6. The prohibition on state copying

### What this schema does not govern

- Instance-specific entity registrations
- Instance-specific dimension values
- Cross-instance state synchronization
- Lifecycle transitions (governed by lifecycle model)
- Qualification evaluation (governed by qualification engine)

---

## Global Vocabulary (shared across instances)

### Dimension Definitions

| Dimension | Type | Authority Source | Applicable To |
|-----------|------|-----------------|---------------|
| entity_type | enum (5 values) | Entity classification authority | All entities |
| lifecycle_state | enum (7 values) | Canonical lifecycle model | All entities |
| qualification_state | enum (5 values) | Qualification engine | CAPABILITY, EXTENSION, RUNTIME_PROVIDER |
| health_state | enum (4 values) | Evidence pipeline | All entities |
| execution_policy | enum (4 values) | Governance policy | CAPABILITY, EXTENSION, RUNTIME_PROVIDER |

### Legal Values

See `lifecycle-vocabulary.md` §Legal Enum Values for complete definitions.

### Transition Rules

See `lifecycle-vocabulary.md` §Transitions per dimension.

---

## Instance-Specific State (never shared)

Each governed system instance maintains its own:

```
Instance Registry
├── entity registrations (entity_id → entity_type)
├── lifecycle states (entity_id → lifecycle_state)
├── qualification states (entity_id → qualification_state)
├── health states (entity_id → health_state)
└── execution policies (entity_id → execution_policy)
```

### Instance Identity Boundary

Every state record is bound to its instance:

```
{
  "instance_id": "<canonical-instance-identifier>",
  "entity_id": "<entity-identifier>",
  "entity_type": "<type>",
  "lifecycle_state": "<state>",
  "qualification_state": "<state>",
  "health_state": "<state>",
  "execution_policy": "<policy>",
  "provenance": {
    "source": "<authority-source>",
    "timestamp": "<ISO-8601>",
    "receipt_id": "<receipt-identifier>"
  }
}
```

The `instance_id` is part of the state/provenance boundary. Two instances may have entities with the same `entity_id` but different dimension values — they are independent.

---

## Instance Boundary Rules

### Inherited (canonical across instances)

- Five dimension definitions
- Legal enum values
- Orthogonality invariant
- Transition rules per dimension
- Applicability rules by entity_type
- Authority source per dimension
- Schema validation rules

### Instance-Specific (never shared)

- Actual dimension values
- Entity registrations
- Qualification evidence
- Health observations
- Execution policy decisions
- Provenance records

### Prohibitions

| # | Prohibition | Rationale |
|---|------------|-----------|
| 1 | No state copying from another instance | New instances start independently |
| 2 | No shared state between instances | Independence of governed systems |
| 3 | No cross-instance derivation | No dimension in A derived from B |
| 4 | No silent authority inheritance | Governance state is not inherited |

---

## Initialization Contract

### New Instance Bootstrap

```
1. Apply canonical governance state schema
2. Initialize entity registry (empty)
3. For each entity registered:
   a. Declare entity_type (required at registration)
   b. Set lifecycle_state = DISCOVERED
   c. Set qualification_state = UNREVIEWED (or N/A per entity_type)
   d. Set health_state = UNKNOWN
   e. Set execution_policy = BLOCKED (or N/A per entity_type)
4. Begin lifecycle transitions through governed process
5. Begin qualification lifecycle
6. Begin health observation
7. Apply execution policy through governance
```

### Migration of Existing Instances

For instances with pre-existing state (e.g., current QA Pilot):

```
1. Apply canonical governance state schema
2. For each entity:
   a. Reconcile legacy fields → canonical dimensions
   b. Document migration evidence per entity
   c. Retain legacy fields as provenance
3. Validate: all five dimensions populated for all entities
4. Validate: no conflation violations
5. Validate: orthogonality invariant holds
```

---

## Validation Rules

### Schema Validation

Every entity state record must validate against `lifecycle-vocabulary.schema.json`.

### Conflation Detection

| Rule | Check | Severity |
|------|-------|----------|
| LCV-001 | lifecycle_state not used as qualification_state | error |
| LCV-002 | health_state does not imply qualification | error |
| LCV-003 | qualification_state does not imply execution permission | error |
| LCV-004 | SYSTEM_COMPONENT/HISTORICAL_LINEAGE → qualification_state = N/A | error |
| LCV-005 | SYSTEM_COMPONENT/HISTORICAL_LINEAGE → execution_policy = N/A | error |

### Orthogonality Validation

No two dimensions may have a derivation relationship. Specifically:

- lifecycle_state ≠ qualification_state
- qualification_state ≠ health_state
- health_state ≠ execution_policy
- health_state ≠ qualification_state
- qualification_state ≠ execution_policy

Any detected conflation produces a Finding routed to the disposition pipeline. It must not automatically repair or mutate state.

---

## Receipt Requirements

Every state mutation produces a receipt:

```
{
  "receipt_type": "governance-state-mutation",
  "instance_id": "<instance>",
  "entity_id": "<entity>",
  "dimension": "<dimension>",
  "before": "<previous-value>",
  "after": "<new-value>",
  "authority": "<authority-source>",
  "timestamp": "<ISO-8601>",
  "mutation_type": " governed | migration | observation "
}
```

Migration receipts use `mutation_type: "migration"`. Governed transitions use `mutation_type: "governed"`. Health observations use `mutation_type: "observation"`.

---

## Compliance

This schema is compliant with:

- QA Pilot Phase 7 architecture freeze (no new assurance primitives)
- QA Pilot authority model (evaluator ≠ recorder ≠ teacher ≠ authority holder)
- Instance independence requirement (schema reusable, state instance-specific)
- Migration provenance requirement (legacy fields retained)
