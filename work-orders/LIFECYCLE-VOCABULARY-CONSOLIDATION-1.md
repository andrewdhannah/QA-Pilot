# LIFECYCLE-VOCABULARY-CONSOLIDATION-1

**Epic ID:** LVC-001
**Date:** 2026-08-16
**Status:** PLANNED — depends on WP-003B closure

---

## Objective

Separate entity type from entity lifecycle. The registry currently conflates "what is this?" with "where is it in its lifecycle?" The add-on SDK work exposed this gap: the registry cannot distinguish capabilities from system components from extensions from historical lineage.

## Problem Statement

Current registry fields carry multiple independent concepts:

| Field | Question It Answers |
|---|---|
| lifecycle_phase | Where in lifecycle? |
| current_phase | Same question, different vocabulary |
| startup_modes | How to enter execution? |
| qualification_status | Is it justified? |
| health_state | What does evidence indicate? |

These are independent dimensions, but the registry treats them as a single lifecycle phase.

## Required Separation

### Dimension 1: Entity Type (what is this?)

```
CAPABILITY            — does work on behalf of the system
SYSTEM_COMPONENT      — enables capabilities, provides substrate
EXTENSION             — optional add-on, may or may not be production
HISTORICAL_LINEAGE    — superseded implementation, retained for evidence
RUNTIME_PROVIDER      — model/tool provider
```

### Dimension 2: Lifecycle State (where does it exist?)

```
DISCOVERED     — identified, not yet classified
REGISTERED     — in registry, classification pending
INITIALIZED    — setup complete, not yet active
ACTIVE         — operating under governance
SUSPENDED      — temporarily halted
DEPRECATED     — marked for retirement
RETIRED        — no longer active
```

### Dimension 3: Qualification State (is it justified?)

```
UNREVIEWED     — not yet evaluated
REVIEW_REQUIRED — evaluation pending
QUALIFIED      — has demonstrated evidence
DISQUALIFIED   — failed qualification
N/A            — not applicable (e.g., SYSTEM_COMPONENT)
```

### Dimension 4: Health State (what does evidence indicate?)

```
HEALTHY        — observed state matches expected
DEGRADED       — partial failure or drift
STALE          — evidence exceeds freshness threshold
UNKNOWN        — insufficient observation data
```

### Dimension 5: Execution Policy (how may it start?)

```
AUTO           — can start without approval
OWNER_APPROVAL — requires Owner decision
BLOCKED        — cannot start (dependency or policy)
N/A            — not executable (e.g., SYSTEM_COMPONENT)
```

## Why This Matters

A clean agent should be able to answer three questions from three different fields:

| Question | Field |
|---|---|
| "Can this run?" | execution_policy |
| "Should this exist?" | lifecycle_state + qualification_state |
| "Is this healthy?" | health_state |

No contradiction exists in independent dimensions:

```
qa-pilot:
  lifecycle_state: INITIALIZED
  qualification_state: QUALIFIED
  health_state: HEALTHY
  execution_policy: OWNER_APPROVAL_REQUIRED

knowledge-ingestion-addon:
  lifecycle_state: INITIALIZED
  qualification_state: REVIEW_REQUIRED
  health_state: DEGRADED (MCP tools broken)
  execution_policy: BLOCKED_PENDING_WIRING

librarian-vault:
  entity_type: SYSTEM_COMPONENT
  lifecycle_state: ACTIVE
  qualification_state: N/A
  health_state: HEALTHY
  execution_policy: N/A
```

## Scope

### Included
- Define canonical state dimensions
- Map existing fields to new dimensions
- Identify deprecated fields
- Add migration rules
- Update schemas/contracts
- Add validation preventing future conflation
- Populate entity_type for all 8 entities
- Populate all dimensions for sealed entities

### Excluded
- Runtime qualification engine (WP-003 already handles gate)
- Capability ceiling enforcement (separate concern)
- Knowledge substrate wiring (separate concern)

## Acceptance Gates

### G1 — Dimension Separation

Every entity has independent values for:
- entity_type
- lifecycle_state
- qualification_state
- health_state
- execution_policy

### G2 — No Contradictions

No entity has:
- lifecycle_state: ACTIVE with entity_type: HISTORICAL_LINEAGE
- lifecycle_state: RETIRED with execution_policy: AUTO
- qualification_state: N/A with entity_type: CAPABILITY

### G3 — Migration Complete

All existing lifecycle_phase values are mapped to the new dimensions.

### G4 — Validation Active

Future mutations cannot set lifecycle_state without entity_type being declared.

### G5 — Agent Verifiable

An agent can answer "Can this run?", "Should this exist?", and "Is this healthy?" from three different fields for every entity.

## Dependency Chain

```
WP-001 Cursor Integrity          ✅
WP-002 Lifecycle Reconciliation  ✅
WP-003A Operational Reconciliation ✅
WP-003B Classification           ✅ (exposed the need)
        |
        v
LVC-001 Vocabulary Consolidation  ← YOU ARE HERE
        |
        v
WP-003B completion (vault + bibliography)
        |
        v
GPI-001 Runtime Qualification
```

## Evidence From Prior Work

The add-on SDK work is the first example of why this consolidation is needed:

| Entity | Was Treated As | Actually Is |
|---|---|---|
| librarian-vault | Capability | System Component |
| working-bibliography-extension | Capability | Extension |
| claude-conversation-ingestion | Capability | Historical Lineage |

The registry was missing the distinction between things that do work and things that enable work.
