# Canonical Governance State Vocabulary

**Sprint:** LVC-001 — Lifecycle Vocabulary Consolidation
**Status:** Authoritative
**Instance Scope:** All governed system instances
**Date:** 2026-08-17

---

## Purpose

Define the five orthogonal dimensions of governance state for entities within a governed system instance. This vocabulary is instance-independent: the schema is reusable; the state is instance-specific.

A new instance inherits this governance model, never another instance's governance state.

---

## Dimensions

### 1. entity_type — What is this entity?

**Authority:** Entity classification authority (registration-time declaration)
**Inherited from other instances:** No
**Mutable:** Rarely — reclassification requires Owner decision

```
CAPABILITY            — does work on behalf of the system
SYSTEM_COMPONENT      — enables capabilities, provides substrate
EXTENSION             — optional add-on, may or may not be production
HISTORICAL_LINEAGE    — superseded implementation, retained for evidence
RUNTIME_PROVIDER      — model/tool provider
```

**Semantics:** Entity type is a structural classification. It determines which other dimensions are applicable. A SYSTEM_COMPONENT does not have a qualification_state of QUALIFIED — it has N/A. An EXTENSION has its own qualification lifecycle distinct from a CAPABILITY.

**Transitions:** Reclassification is an Owner decision. No automatic transitions.

### 2. lifecycle_state — Where is this entity in its lifecycle?

**Authority:** Existing canonical lifecycle model (cursor / governed transitions)
**Inherited from other instances:** No
**Mutable:** Yes — through governed lifecycle transitions

```
DISCOVERED     — identified, not yet classified
REGISTERED     — in registry, classification pending
INITIALIZED    — setup complete, not yet active
ACTIVE         — operating under governance
SUSPENDED      — temporarily halted
DEPRECATED     — marked for retirement
RETIRED        — no longer active
```

**Semantics:** Lifecycle state tracks the entity's position in its governed lifecycle. Transitions follow established lifecycle rules. No transition may be inferred from another dimension.

**Transitions:**
```
DISCOVERED → REGISTERED → INITIALIZED → ACTIVE
                                        ACTIVE → SUSPENDED
                                        ACTIVE → DEPRECATED → RETIRED
                                        SUSPENDED → ACTIVE
                                        SUSPENDED → DEPRECATED → RETIRED
```

**Projection notes:** Legacy `current_phase` values (`execution`, `init`) do not map 1:1 to this enum. The migration script documents explicit reconciliation rules per entity.

### 3. qualification_state — Has it satisfied qualification requirements?

**Authority:** Qualification engine / review surface
**Inherited from other instances:** No
**Mutable:** Yes — through qualification lifecycle

```
UNREVIEWED     — not yet evaluated
REVIEW_REQUIRED — evaluation pending
QUALIFIED      — has demonstrated evidence
DISQUALIFIED   — failed qualification
N/A            — not applicable (e.g., SYSTEM_COMPONENT)
```

**Semantics:** Qualification state is evidence-backed. It answers "has this entity demonstrated the evidence required for its type and role?" A QUALIFIED entity is not necessarily ACTIVE. An ACTIVE entity is not necessarily QUALIFIED.

**Applicability by entity_type:**
| entity_type | qualification_state applicable? |
|-------------|--------------------------------|
| CAPABILITY | Yes |
| SYSTEM_COMPONENT | N/A |
| EXTENSION | Yes |
| HISTORICAL_LINEAGE | N/A |
| RUNTIME_PROVIDER | Yes |

**Transitions:** Qualification follows the qualification lifecycle (discover → collect → validate → evaluate → lifecycle → review). No automatic transitions from other dimensions.

### 4. health_state — What is its current observed health?

**Authority:** Observed health / projection from evidence pipeline
**Inherited from other instances:** No
**Mutable:** Yes — re-observed continuously

```
HEALTHY        — observed state matches expected
DEGRADED       — partial failure or drift
STALE          — evidence exceeds freshness threshold
UNKNOWN        — insufficient observation data
```

**Semantics:** Health state is observational, not authoritative. It reflects what the evidence pipeline has observed, not what the entity declarations claim. A HEALTHY entity may be UNREVIEWED. A QUALIFIED entity may be STALE.

**Projection rules:** Health state is derived from evidence. It is the only dimension that is primarily projected rather than declared. However, the projection source (evidence pipeline) is authoritative for this dimension — health_state is not inferred from lifecycle_state or qualification_state.

**Transitions:** Re-observed on each evidence cycle. No governed transition rules — values reflect current observation.

### 5. execution_policy — What execution behavior is permitted?

**Authority:** Execution-permission policy / Owner decision
**Inherited from other instances:** No
**Mutable:** Yes — through governance policy changes

```
AUTO           — can start without approval
OWNER_APPROVAL — requires Owner decision
BLOCKED        — cannot start (dependency or policy)
N/A            — not executable (e.g., SYSTEM_COMPONENT)
```

**Semantics:** Execution policy is a permission gate. It answers "is this entity permitted to execute?" A BLOCKED entity may be HEALTHY and QUALIFIED — execution policy is independent. An AUTO entity may be DEGRADED.

**Applicability by entity_type:**
| entity_type | execution_policy applicable? |
|-------------|---------------------------|
| CAPABILITY | Yes |
| SYSTEM_COMPONENT | N/A |
| EXTENSION | Yes |
| HISTORICAL_LINEAGE | N/A |
| RUNTIME_PROVIDER | Yes |

**Transitions:** Policy changes require Owner decision or governance policy update. No automatic transitions.

---

## Orthogonality Invariant

No dimension may be used as a proxy for another. The following combinations are legal and non-contradictory:

| Example | entity_type | lifecycle_state | qualification_state | health_state | execution_policy |
|---------|------------|----------------|---------------------|--------------|------------------|
| Qualified but not running | CAPABILITY | INITIALIZED | QUALIFIED | HEALTHY | OWNER_APPROVAL |
| Running but unhealthy | CAPABILITY | ACTIVE | QUALIFIED | DEGRADED | AUTO |
| Healthy but not qualified | CAPABILITY | ACTIVE | UNREVIEWED | HEALTHY | BLOCKED |
| Degraded component | SYSTEM_COMPONENT | ACTIVE | N/A | DEGRADED | N/A |
| Suspended extension | EXTENSION | SUSPENDED | QUALIFIED | UNKNOWN | BLOCKED |
| Historical lineage | HISTORICAL_LINEAGE | RETIRED | N/A | UNKNOWN | N/A |

No dimension silently derives authority from another. An agent can answer three questions from three different fields:

| Question | Field |
|----------|-------|
| "Can this run?" | execution_policy |
| "Should this exist?" | lifecycle_state + qualification_state |
| "Is this healthy?" | health_state |

---

## Instance Boundary Rules

### What is inherited (canonical across instances)

- The five dimension definitions
- The legal enum values
- The orthogonality invariant
- The transition rules per dimension
- The applicability rules by entity_type
- The authority source per dimension

### What is instance-specific (never shared)

- Actual dimension values for entities
- Entity registrations
- Qualification evidence
- Health observations
- Execution policy decisions

### Prohibitions

1. **No state copying:** A new instance may not initialize its state from another instance's state as authoritative.
2. **No shared state:** Two instances may have entities with the same entity_id but different dimension values. They are independent.
3. **No cross-instance derivation:** No dimension value in instance A may be derived from a dimension value in instance B.

### Initialization rules for new instances

```
1. Apply canonical governance state schema
2. Initialize all five dimensions with default values:
   - entity_type: (declared at registration)
   - lifecycle_state: DISCOVERED
   - qualification_state: UNREVIEWED
   - health_state: UNKNOWN
   - execution_policy: BLOCKED
3. Register system entities
4. Begin qualification lifecycle
5. Begin health observation
6. Apply execution policy through governance
```

---

## Legacy Field Reconciliation

### Current registry fields (legacy)

| Legacy Field | Maps To | Reconciliation Notes |
|-------------|---------|---------------------|
| `current_phase` | lifecycle_state (projection) | Values `execution` → ACTIVE (approximate); `init` → INITIALIZED. Documented per-entity. |
| `current_phase_deprecated` | lifecycle_state (projection) | Duplicate of current_phase. Retained as provenance. |
| `lifecycle_stage` | (no direct mapping) | Numeric position indicator (1–8). Not a lifecycle state. Retained as provenance. |
| `lifecycle_label` | (no direct mapping) | Human-readable derivative of lifecycle_stage. Retained as provenance. |

### Migration boundary

Legacy fields are **not deleted** in LVC-001. They are:
1. Retained in the registry as provenance evidence
2. Marked as legacy/deprecated in the schema
3. Projected into canonical dimensions through deterministic migration
4. Subject to future removal in a separate governed operation

---

## Schema Reference

See `contracts/lifecycle-vocabulary.schema.json` for machine-checkable schema.

See `contracts/governance-state-schema.md` for the instance-independent governance contract.
