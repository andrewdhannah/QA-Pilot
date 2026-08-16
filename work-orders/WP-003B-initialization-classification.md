# WP-003B — Capability Initialization Classification (REVISED)

**Work Packet:** WP-003B of GOVERNANCE-IDENTITY-CONSISTENCY-1
**Date:** 2026-08-16
**Status:** INVESTIGATION REQUIRED — revised classification set

---

## Objective

Classify five registered entities that lack lifecycle state. Determine lifecycle intent for each based on evidence, not assumption.

## Revised Classification Set

The previous Initialize-only classification is insufficient. A registry entry should not imply capability maturity.

| Classification | Meaning | Lifecycle State |
|---|---|---|
| `ACTIVE_CAPABILITY` | Real capability, ready for operational lifecycle | Operational or Initialize |
| `REGISTERED` | Registry entry exists, capability substance unclear | Needs investigation |
| `INITIALIZATION_REQUIRED` | Real capability, not yet started | Initialize |
| `DEPRECATED_CANDIDATE` | Superseded or no longer active | Deprecation path |
| `ARCHIVED` | Historical identity, retained for evidence chain | Archived |

## Entity Classifications

### 1. qa-pilot

| Question | Answer |
|---|---|
| Capability declaration exists? | Yes — active project |
| Provider exists? | Yes — Owner |
| Evidence of ownership? | Yes — WP-001, WP-002, GIR-001 work items |
| Projection exists? | Yes — governance entities |
| Agent can discover boundary? | Yes |
| Can enter lifecycle state? | Yes — cursor at Phase 1 |

**Classification:** `ACTIVE_CAPABILITY`
**Proposed lifecycle state:** Initialize (Phase 1, no work completed)
**Evidence basis:** cursor phase 1, governance activity (WP-001/002/003), project registry entry
**Confidence:** HIGH

### 2. working-bibliography-extension

| Question | Answer |
|---|---|
| Capability declaration exists? | Yes — registry entry |
| Provider exists? | Unknown |
| Evidence of ownership? | None — no work items, no cursor |
| Projection exists? | In governance entities |
| Agent can discover boundary? | Unknown |
| Can enter lifecycle state? | Unclear — no cursor to advance |

**Classification:** `REGISTERED`
**Proposed lifecycle state:** Needs investigation — is this an active extension or a placeholder?
**Evidence basis:** registry entry only, no work evidence
**Confidence:** LOW

**Decision required:** Is this an active extension that needs initialization, or a placeholder that should be deprecated?

### 3. claude-conversation-ingestion

| Question | Answer |
|---|---|
| Capability declaration exists? | Yes — registry entry |
| Provider exists? | No — superseded |
| Evidence of ownership? | None — no work items, no cursor |
| Projection exists? | In governance entities |
| Agent can discover boundary? | No — startup_modes is empty |
| Can enter lifecycle state? | No — cannot be activated |
| Replacement exists? | Yes — Claude/GPT Ingester Add-on → Vault → Knowledge Substrate |

**Classification:** `DEPRECATED_CANDIDATE`
**Proposed lifecycle state:** ARCHIVED (retain historical identity, do not initialize)
**Evidence basis:** superseded by Claude/GPT Ingester Add-on, empty startup_modes, no activation path
**Confidence:** HIGH

**Lineage:**
```
Old: claude-conversation-ingestion
        ↓
    (single-purpose ingestion component)

New: Claude/GPT Ingester Add-on
        ↓
    Vault
        ↓
    Knowledge Substrate
```

**Governance action:** Retain registry identity for evidence chain continuity. Do not delete. Mark as archived/superseded. The capability lineage changed; the registry records that.

**Future signal:** `CAPABILITY_SUPERSEDED` or `LEGACY_REGISTRATION` — a registry contains a capability identity that the runtime ecosystem no longer contains as an active capability.

### 4. librarian-vault

| Question | Answer |
|---|---|
| Capability declaration exists? | Yes — registry entry |
| Provider exists? | Unknown |
| Evidence of ownership? | None — no work items, no cursor |
| Projection exists? | In governance entities |
| Agent can discover boundary? | Unknown |
| Can enter lifecycle state? | Unclear |

**Classification:** `REGISTERED`
**Proposed lifecycle state:** Needs investigation — is this a capability or an infrastructure component?
**Evidence basis:** registry entry only, knowledge substrate exists separately
**Confidence:** LOW

**Decision required:** Is librarian-vault a user-facing capability, or infrastructure that the knowledge substrate runs on?

### 5. knowledge-ingestion-addon

| Question | Answer |
|---|---|
| Capability declaration exists? | Yes — registry entry |
| Provider exists? | Yes — knowledge substrate team |
| Evidence of ownership? | Yes — functional Rust library (53 entities, 8 sources, schema v3) |
| Projection exists? | In governance entities |
| Agent can discover boundary? | No — MCP tools not wired (ADAPTER_EXECUTION_ERROR) |
| Can enter lifecycle state? | Partially — substance exists but MCP surface broken |

**Classification:** `ACTIVE_CAPABILITY` (substance exists)
**Proposed lifecycle state:** Initialize — has substance but needs MCP wiring
**Evidence basis:** functional knowledge substrate, 53 entities, 8 sources, schema v3
**Confidence:** MEDIUM — MCP adapter broken is a blocking issue

**Note:** This is the current ingestion capability (replacing claude-conversation-ingestion). Its MCP tools being broken is a known issue (from GIR-001 audit). The lifecycle state should reflect its actual readiness.

## Summary

| Entity | Classification | Lifecycle State | Confidence |
|---|---|---|---|
| qa-pilot | ACTIVE_CAPABILITY | Initialize | HIGH |
| working-bibliography-extension | REGISTERED | Needs investigation | LOW |
| claude-conversation-ingestion | DEPRECATED_CANDIDATE | ARCHIVED | HIGH |
| librarian-vault | REGISTERED | Needs investigation | LOW |
| knowledge-ingestion-addon | ACTIVE_CAPABILITY | Initialize | MEDIUM |

## Acceptance Gates

### G1 — No False Operational State

No entity moves to Operational without cursor evidence, work item evidence, and provider declaration.

### G2 — Deprecated Entity Preserved

claude-conversation-ingestion retains registry identity. Evidence chain preserved. Not deleted.

### G3 — Classification Evidence Documented

Each entity's classification is backed by specific evidence (or lack thereof).

### G4 — Owner Decision Receipts

One receipt per entity:
- `ODR-WP003B-QA-PILOT-001`
- `ODR-WP003B-WORKING-BIBLIOGRAPHY-001`
- `ODR-WP003B-CLAUDE-CONVERSATION-001`
- `ODR-WP003B-LIBRARIAN-VAULT-001`
- `ODR-WP003B-KNOWLEDGE-INGESTION-001`

### G5 — Registry Update Only After Classification

No mutation before classification is approved. Each classification requires Owner decision receipt.

## Stop Conditions

- If entity has no capability declaration and no provider → recommend deprecation
- If entity has substance but wrong classification → investigate before mutating
- If entity startup_modes is empty → requires explicit Owner decision on activation capability
- If entity is superseded → archive, do not initialize
