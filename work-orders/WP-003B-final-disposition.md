# WP-003B — Final Disposition (REVISED)

**Date:** 2026-08-16
**Status:** Classification complete — entity type axis established

---

## Architecture Context

These entities were part of the Add-on SDK expansion. The correct model:

```
                 Librarian Core
                      |
          Optional Capability Registry
                      |
        +-------------+-------------+
        |             |             |
     Add-on SDK    Extensions     Providers
        |
        +-- Claude/GPT Ingester
        +-- Knowledge Ingestion
        +-- Vault Integration
        +-- Bibliography / Research Tools
```

Key invariant: Librarian can operate without add-ons, but add-ons can register capabilities when present.

## Entity Type Axis

The registry was missing the distinction between things that do work and things that enable work. Before lifecycle states make sense, entity type must be declared.

| Entity | Type | Rationale |
|---|---|---|
| librarian | CAPABILITY | Core system, does work |
| agent-bridge | CAPABILITY | Platform extension, does work |
| librarian-workbench | CAPABILITY | Development tooling, does work |
| qa-pilot | CAPABILITY | Validation system, does work |
| knowledge-ingestion-addon | CAPABILITY | Ingestion capability (successor) |
| librarian-vault | SYSTEM_COMPONENT | Persistence substrate, enables capabilities |
| working-bibliography-extension | EXTENSION | SDK reference/extension, may or may not be production |
| claude-conversation-ingestion | HISTORICAL_LINEAGE | Superseded implementation, capability concept survived |

## Final Classifications

### librarian-vault → SYSTEM_COMPONENT

Not a capability. It provides substrate:

```
Knowledge ingestion
        ↓
Vault persistence layer
        ↓
Knowledge retrieval / MCP / RAG surfaces
```

**Do not initialize as capability.** Introduce entity classification:

```json
{
  "entity_type": "SYSTEM_COMPONENT",
  "lifecycle_state": "ACTIVE",
  "health_state": "...",
  "qualification_state": "N/A"
}
```

### working-bibliography-extension → EXTENSION

Part of the Add-on SDK exploration. The question is not "initialize or deprecate?" — it's "production extension or SDK reference artifact?"

The drift detector work makes it valuable, but value ≠ production capability.

**Classification:** EXTENSION
**Lifecycle question:** Is this a supported Librarian add-on, or a reference implementation proving the SDK works?

### claude-conversation-ingestion → HISTORICAL_LINEAGE

Not a broken capability. A superseded implementation:

```
Historical capability identity
        ↓
Superseded implementation
        ↓
Claude/GPT Ingester Add-on
        ↓
Vault ingestion pipeline
```

**Do not delete.** Retain for evidence chain continuity. The capability concept survived; only the implementation changed.

## Entity State After WP-003B

| Entity | Type | lifecycle_phase | Status |
|---|---|---|---|
| librarian | CAPABILITY | execution | Sealed |
| agent-bridge | CAPABILITY | execution | Sealed |
| librarian-workbench | CAPABILITY | execution | Sealed |
| qa-pilot | CAPABILITY | init | Sealed |
| knowledge-ingestion-addon | CAPABILITY | init | Sealed |
| librarian-vault | SYSTEM_COMPONENT | (empty) | Needs type-aware lifecycle |
| working-bibliography-extension | EXTENSION | (empty) | Needs extension lifecycle |
| claude-conversation-ingestion | HISTORICAL_LINEAGE | (empty) | ARCHIVED — no mutation needed |

## Registry Evolution Required

Before mutating the remaining two entities, the registry needs the entity_type axis.

Current registry fields:
```
project_id, display_name, current_phase, lifecycle_phase, startup_modes
```

Required additions:
```
entity_type: CAPABILITY | SYSTEM_COMPONENT | EXTENSION | HISTORICAL_LINEAGE | RUNTIME_PROVIDER
qualification_state: QUALIFIED | REVIEW_REQUIRED | UNREVIEWED | N/A
health_state: HEALTHY | DEGRADED | STALE | UNKNOWN
execution_policy: OWNER_APPROVAL | AUTO | BLOCKED | N/A
```

## WP-003B Closure

WP-003B has done its job:
1. Exposed the remaining ambiguity cases ✅
2. Revealed the registry needs entity_type before lifecycle ✅
3. Proved the add-on SDK work is the first example of why the ontology is needed ✅

**WP-003B is complete.** The two remaining cases (vault, bibliography) are not ordinary lifecycle transitions — they require the lifecycle vocabulary consolidation first.
