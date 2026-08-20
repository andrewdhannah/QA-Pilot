# WP-KNOWLEDGE-SUBSTRATE-INTEGRATION-1

**Work Packet:** Knowledge Substrate Integration
**Phase:** 1 — Characterization
**Status:** COMPLETE
**Date:** 2026-08-18
**Agent:** OpenWork-Claude (mimo-v2.5)
**Parallel to:** WO-4+ Dashboard Consolidation (independent streams)

---

## Problem Statement

The knowledge custody add-ons have individual capabilities but lack governed composition. The gap is not broken functionality — it is missing lifecycle activation and transition authority.

---

## Extension Lifecycle State Inventory

| Extension | Location | Phase | Lifecycle | MCP Server | Handshake | Vault Connect |
|-----------|----------|-------|-----------|------------|-----------|---------------|
| WB Extension | `working-bibliography-extension/` | Milestone 4 | ACTIVE (proven) | ✅ Working (port 8765) | ✅ Complete | NO (own store) |
| Librarian Vault | `active/librarian-vault/` | init | REGISTERED | ✅ Working (port 9002) | ❌ Stub | IS the vault |
| Knowledge Ingestion | `active/knowledge-ingestion-addon/` | init | REGISTERED | ⚠️ Stubbed (port 9001) | ❌ Stub | NO (own SQLite) |
| Claude Conversation | `Claude-Conversation-Ingestion/` | foundation | REMOVED from registry | ❌ No server | ❌ Missing | NO |

**Key finding:** 3 of 4 extensions are stuck at `init`/`REGISTERED`. Only WB has progressed through the lifecycle.

---

## SDK Boundary Map

```
Rust SDK (librarian-sdk)
├── manifest      — AddonManifest identity + capabilities
├── capability    — Registration and discovery
├── execution     — Handler execution context
├── governance    — Custody, evidence, receipts
├── storage       — Private SQLite per add-on
├── lifecycle     — State machine (Installed → Initializing → Ready → Degraded → Disabled → Removed)
├── qualification — Admission pipeline
└── runtime       — SdkRuntime orchestrates register/qualify/activate/execute
```

The SDK provides the **governed execution boundary**. Add-on handlers provide domain logic. The SDK handles all governance automatically (custody → residency → execute → evidence → receipt → release).

**Python extensions do not use the Rust SDK.** They have parallel but separate MCP server implementations. The SDK boundary is not wired to the Python extensions.

---

## Ownership Models

### Ingestion Addon Ownership

| Concern | Owner | Evidence |
|---------|-------|----------|
| Document parsing | Ingestion Addon | `src/parsers/pdf.py` — PyMuPDF |
| Validation bridge | Ingestion Addon | `src/contract/validation.py` — deterministic |
| Evidence package | Ingestion Addon | `src/contract/evidence.py` — receipt generation |
| Registry (dedup, integrity) | Ingestion Addon | `src/registry/registry.py` — SQLite |
| IngestionResult production | Ingestion Addon | Contract output |

### Vault Ownership

| Concern | Owner | Evidence |
|---------|-------|----------|
| Ingestion reception | Vault | `src/vault/ingestion.py` — accepts IngestionResult |
| Chunking | Vault | `src/vault/chunking.py` — page/paragraph/sentence |
| Embedding | Vault | `src/vault/embedding.py` — TF-IDF |
| Hybrid search | Vault | `src/vault/search.py` — vector + fulltext |
| Provenance verification | Vault | `src/vault/provenance.py` |
| Context assembly | Vault | `src/vault/context.py` — citations |

### Missing: Transition Authority

| Concern | Current Owner | Required Owner |
|---------|---------------|----------------|
| IngestionResult → Vault handoff | Nobody | Extension lifecycle boundary |
| Lifecycle state advancement | Nobody | SDK/Core authority |
| Capability activation | Nobody | Owner approval gate |
| Cross-extension data flow | Nobody | Governed transition |

---

## Handshake Gap Analysis

### Reference Implementation (WB Extension)

The WB extension has a complete 6-state handshake:

```
REGISTERED → CONTRACT_VERIFIED → OWNER_APPROVED → ACTIVE
                                                   → SUSPENDED → REVOKED
```

With authority policy:
- `REGISTERED → CONTRACT_VERIFIED`: automated (contract validation)
- `CONTRACT_VERIFIED → OWNER_APPROVED`: owner (explicit authorization)
- `OWNER_APPROVED → ACTIVE`: automated (activation signal)
- `ACTIVE → SUSPENDED`: automated (drift detection)
- `ACTIVE → REVOKED`: owner (contract violation)
- `SUSPENDED → ACTIVE`: owner (clear drift)
- `SUSPENDED → REVOKED`: owner (terminate)

### Gap in Vault and KIA

Both have `src/handshake/README.md` with only: "Copy from working-bibliography-extension reference."

No implementation files exist. The 7 files needed:

| File | Purpose | Status |
|------|---------|--------|
| `identity.py` | Extension identity announcement | ❌ Missing |
| `validator.py` | Contract + capability manifest validation | ❌ Missing |
| `lifecycle.py` | 6-state state machine with authority policy | ❌ Missing |
| `orchestrator.py` | Handshake sequence (announce → validate → await → activate) | ❌ Missing |
| `receipts.py` | Handshake receipts | ❌ Missing |
| `__init__.py` | Module exports | ❌ Missing |
| `README.md` | Instructions | ⚠️ Placeholder only |

---

## Validation Evidence Requirements

The Librarian architecture requires validation artifacts for lifecycle advancement:

```
Exists ≠ Qualified ≠ Activated ≠ Available
```

Without validation, extensions cannot progress beyond `REGISTERED`. The validation needs:

| Evidence Type | Purpose | Current |
|---------------|---------|---------|
| Contract validation | Proves extension conforms to declared contract | ❌ Missing |
| Capability manifest validation | Proves declared capabilities match implementation | ❌ Missing |
| Boundary test evidence | Proves extension respects governance boundaries | ❌ Missing |
| Integration test evidence | Proves extension works with Librarian core | ❌ Missing |

---

## Transition Authority Definition (Proposed)

```
Current:

Ingestion Addon                    Vault
    owns parsing                     owns indexing
    produces IngestionResult         accepts vault_ingest
         ↓                               ↑
    (manual handoff — no authority)


Target:

Ingestion Addon
    ↓
validated IngestionResult
    ↓
Extension lifecycle boundary ← WHO OWNS THIS?
    ↓
Librarian SDK/Core authority
    ↓
Vault ingestion boundary
    ↓
Knowledge substrate availability
```

**The transition authority between ingestion and vault is the missing governance layer.** It should not be:
- Direct Python→Python (bypasses governance)
- Manual handoff (no authority chain)
- Agent-mediated (adds latency, no receipts)

It should be:
- SDK-governed transition with receipt
- Owner-authorized activation
- Evidence-backed handoff

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| KSI-001 | All 4 extensions have explicit lifecycle state |
| KSI-002 | Handshake contract defined for vault and KIA |
| KSI-003 | Transition authority ownership assigned |
| KSI-004 | Validation evidence requirements specified |
| KSI-005 | Ingestion → Vault data flow has governance receipt |

---

## Recommended Phase 2 (Implementation — NOT AUTHORIZED YET)

1. Copy WB handshake implementation to vault and KIA
2. Wire KIA MCP server to actual tool implementations
3. Define IngestionResult → vault_ingest transition authority
4. Implement validation evidence for both extensions
5. Prove end-to-end: PDF → ingestion → vault → librarian → agent

---

*Phase 1 complete. Read-only characterization — no mutations performed.*
*Parallel to WO-4+ Dashboard Consolidation.*
