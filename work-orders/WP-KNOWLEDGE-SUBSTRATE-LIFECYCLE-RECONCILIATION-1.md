# WP-KNOWLEDGE-SUBSTRATE-LIFECYCLE-RECONCILIATION-1

**Work Packet:** Knowledge Substrate Lifecycle Reconciliation
**Phase:** 1 — Characterization
**Status:** COMPLETE
**Date:** 2026-08-18
**Agent:** OpenWork-Claude (mimo-v2.5)
**Precedes:** WP-KNOWLEDGE-SUBSTRATE-INTEGRATION-1

---

## Problem Statement

Knowledge custody extensions have independently implemented capability layers, but the extension lifecycle, registration, handshake, and governed composition contracts have only been proven in the Working Bibliography reference implementation. The system does not lack capability — it lacks promotion from local capability to governed capability.

---

## Extension Taxonomy

### Type A — Knowledge Producer Extension

Responsibilities:
```
source → parse → normalize → produce artifact → emit provenance → submit custody request
```

| Extension | Status | Classification |
|-----------|--------|---------------|
| Working Bibliography | ACTIVE | Producer (reference) |
| Knowledge Ingestion Addon | REGISTERED (stuck) | Producer |
| Claude Conversation Ingestion | REMOVED (foundation) | Producer |

### Type B — Knowledge Custody Extension

Responsibilities:
```
receive artifact → verify provenance → store → index → retrieve → assemble context
```

| Extension | Status | Classification |
|-----------|--------|---------------|
| Librarian Vault | REGISTERED (stuck) | Custody (infrastructure) |

**The Vault is infrastructure, not merely another producer package.** Different lifecycle authority applies.

### Type C — Transport Extension

Responsibilities:
```
intent transport → identity → authorization → audit
```

| Extension | Status | Classification |
|-----------|--------|---------------|
| Agent Bridge | Separate concern | Transport |

---

## Required Lifecycle Contract (Extracted from WB Reference)

### Minimum Files for a Governed Extension

| File | Purpose | WB Has | KIA Has | Vault Has |
|------|---------|--------|---------|-----------|
| `.librarian/extension.json` | Identity declaration | ✅ | ⚠️ stale path | ⚠️ stale path |
| `mcp/capabilities.json` | Capability manifest | ✅ | ✅ | ✅ |
| `docs/contracts/<contract>.json` | Formal contract | ✅ | ❌ | ❌ |
| `src/handshake/identity.py` | Identity announcement | ✅ | ❌ | ❌ |
| `src/handshake/validator.py` | Contract validation | ✅ | ❌ | ❌ |
| `src/handshake/lifecycle.py` | 6-state state machine | ✅ | ❌ | ❌ |
| `src/handshake/orchestrator.py` | Handshake sequence | ✅ | ❌ | ❌ |
| `src/handshake/receipts.py` | Handshake receipts | ✅ | ❌ | ❌ |
| `src/validation/` | Validation evidence | ✅ | ❌ | ❌ |

### Lifecycle State Machine

```
REGISTERED → CONTRACT_VERIFIED → OWNER_APPROVED → ACTIVE
                                                   → SUSPENDED → REVOKED
```

Authority policy (from WB reference):

| Transition | Authority |
|------------|-----------|
| REGISTERED → CONTRACT_VERIFIED | automated |
| CONTRACT_VERIFIED → OWNER_APPROVED | owner |
| OWNER_APPROVED → ACTIVE | automated |
| ACTIVE → SUSPENDED | automated (drift) |
| ACTIVE → REVOKED | owner (violation) |
| SUSPENDED → ACTIVE | owner (clear drift) |
| SUSPENDED → REVOKED | owner (terminate) |

### Current Lifecycle States

| Extension | State | Next Required |
|-----------|-------|---------------|
| WB | ACTIVE | None (reference) |
| KIA | REGISTERED (stuck) | CONTRACT_VERIFIED |
| Vault | REGISTERED (stuck) | CONTRACT_VERIFIED |
| CCI | REMOVED | Re-registration if needed |

---

## Provider Registry Requirements

Current `package-registry.json` contents:

| Package | State | Notes |
|---------|-------|-------|
| working-bibliography-extension | ACTIVE | Reference |
| claude-conversation-ingestion | REMOVED | Was installed, then removed |
| knowledge-ingestion-addon | **MISSING** | Not registered |
| librarian-vault | **MISSING** | Not registered |

**KIA and Vault are invisible to the governance kernel.** They cannot be discovered, authorized, or composed without registry entries.

---

## Composition Boundary Definition

### Current (Ungoverned)

```
KIA → (manual) → Vault
```

No authority chain. No receipts. No lifecycle gate.

### Target (Governed)

```
KIA (Producer)
    ↓
IngestionResult + Provenance + Evidence
    ↓
Extension Lifecycle Boundary
    ↓
Librarian SDK/Core Authority
    ↓
Vault (Custody)
    ↓
Knowledge Substrate
    ↓
Agent Access (with citations)
```

### Composition Contract (Proposed)

The transition between Producer and Custody extensions should have:

| Property | Requirement |
|----------|-------------|
| Authority | Owner-authorized or SDK-governed |
| Receipt | Every transition emits a receipt |
| Provenance | IngestionResult carries source provenance |
| Validation | Vault validates before accepting |
| Dedup | Vault checks for existing artifacts |
| Audit trail | Both producer and custody record the handoff |

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| LRC-001 | Extension taxonomy finalized (Producer/Custody/Transport) |
| LRC-002 | Required lifecycle contract documented |
| LRC-003 | KIA classified as Producer |
| LRC-004 | Vault classified as Custody |
| LRC-005 | Provider registry requirements defined |
| LRC-006 | Composition boundary defined |

---

## Implementation Order (After Characterization)

1. **Register Vault as custody extension** in provider registry
2. **Register KIA as producer extension** in provider registry
3. **Copy WB handshake** to both extensions
4. **Implement validation evidence** for both
5. **Wire KIA → Vault governed transition** with receipt
6. **Prove end-to-end:** PDF → KIA → Vault → Librarian → Agent context

---

## Critical Observation

The substrate is closer to completion than expected. The missing work is governance composition, not foundational capability. The WB extension proves the pattern works. The task is to generalize it across the extension ecosystem.

---

*Phase 1 complete. Read-only characterization — no mutations performed.*
*This work packet precedes WP-KNOWLEDGE-SUBSTRATE-INTEGRATION-1.*
