# VAULT-MCP-TOPOLOGY-RECONCILIATION-1

**Work Packet:** Vault MCP Topology Reconciliation
**Phase:** 1 — Characterization
**Status:** IN PROGRESS
**Date:** 2026-08-18
**Agent:** OpenWork-Claude (mimo-v2.5)

---

## Hypothesis

Librarian MCP is the single governed connection fabric. Vault, KIA, WB, CCI, and Nodes are components behind it rather than peer MCP authorities.

---

## Current State

### Vault MCP (port 9002) — 6 tools

| Tool | Operation | Authority |
|------|-----------|-----------|
| `vault_ingest` | Receive IngestionResult | Custody |
| `vault_search` | Search indexed knowledge | Custody |
| `vault_retrieve` | Retrieve context with citations | Custody |
| `vault_verify` | Verify provenance | Custody |
| `vault_status` | Vault statistics | Custody |
| `vault_artifacts` | List indexed artifacts | Custody |

### Librarian MCP (port 3457) — 73 advertised tools

Already has knowledge tools:

| Tool | Operation | Source |
|------|-----------|--------|
| `knowledge_query` | Query Knowledge Substrate | Rust SDK add-on |
| `knowledge_import` | Import to Knowledge Substrate | Rust SDK add-on |
| `knowledge_status` | Knowledge Substrate health | Rust SDK add-on |
| `knowledge_findings` | Knowledge findings | Rust SDK add-on |
| `librarian_search` | Document search (FTS5/vector) | Librarian Core |

### KIA MCP (port 9001) — 6 tools

| Tool | Operation | Source |
|------|-----------|--------|
| `ki_ingest_pdf` | Ingest PDF | KIA |
| `ki_list_ingested` | List ingested docs | KIA |
| `ki_query_document` | Query document | KIA |
| `ki_ingest_attempts` | List attempts | KIA |
| `ki_registry_stats` | Registry stats | KIA |
| `ki_registry_integrity` | Registry health | KIA |

---

## Characterization Questions

### Q1: What does Vault own?

Vault owns:
- Storage (SQLite database)
- Chunking (page/paragraph/sentence strategies)
- Embedding (TF-IDF)
- Hybrid search (vector + fulltext)
- Provenance verification
- Context assembly with citations

Vault does NOT own:
- Knowledge creation (KIA/WB/CCI own this)
- Governance decisions (Librarian Core owns this)
- Agent authorization (Librarian MCP owns this)

### Q2: Does Vault have independent authority?

No. Vault is a custody infrastructure. It:
- Receives artifacts from producers
- Stores and indexes them
- Retrieves them on demand
- Verifies provenance

It does NOT:
- Decide what gets ingested (producers decide)
- Authorize access (Librarian Core decides)
- Make governance decisions (Owner decides)

### Q3: Can Vault tools be exposed through Librarian MCP?

Yes. The Vault's 6 tools are all custody operations that could be represented as Librarian MCP capabilities:
- `knowledge.ingest` (replaces `vault_ingest`)
- `knowledge.search` (extends `knowledge_query`)
- `knowledge.retrieve` (new — context with citations)
- `knowledge.verify` (new — provenance check)
- `knowledge.status` (extends `knowledge_status`)
- `knowledge.artifacts` (new — list indexed artifacts)

### Q4: What is the correct topology?

```
Agents
  ↓
Librarian MCP :3457
  ↓
governed tools
  ↓
┌───────────────┴───────────────┐
│                               │
Knowledge Substrate        Vault (custody)
(Rust SDK add-on)          (internal service)
│                               │
├── knowledge_query             ├── ingest
├── knowledge_import            ├── search
├── knowledge_status            ├── retrieve
└── knowledge_findings          ├── verify
                                ├── status
                                └── artifacts
```

### Q5: Does any add-on bypass Librarian governance?

Current state:
- KIA MCP (port 9001) — separate MCP authority ⚠️
- Vault MCP (port 9002) — separate MCP authority ⚠️
- WB MCP (port 8765) — separate MCP authority ⚠️

These are all peer MCP authorities that bypass Librarian's governed connection fabric.

### Q6: How do remote Nodes reach knowledge capabilities?

Through Librarian MCP over HTTPS. The current architecture already supports this:
- Rust MCP Protocol Plane (:3457) serves MCP over HTTP
- Remote Nodes connect via HTTPS
- Librarian MCP is the sole MCP authority

---

## Proposed Target Topology

```
                    AGENTS / NODES
                         │
                         ▼
                  Librarian MCP
                  :3457 /mcp
                         │
           ┌─────────────┼─────────────┐
           │             │             │
    governed tools  knowledge    custody ops
           │         substrate    (internal)
           │             │             │
           ▼             ▼             ▼
      Librarian    KIA/WB/CCI     Vault
        Core      (producers)   (custody)
```

**Add-ons become internal components, not peer MCP authorities.**

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| TOPO-001 | Vault operations identified and classified |
| TOPO-002 | Vault authority boundary defined |
| TOPO-003 | KIA → Vault communication path defined |
| TOPO-004 | Librarian MCP can represent Vault capabilities |
| TOPO-005 | No add-on bypasses Librarian governance |
| TOPO-006 | Remote Nodes can reach knowledge via Librarian MCP |
| TOPO-007 | Final authority/topology diagram produced |

---

*Characterization in progress. No implementation — design/reconciliation only.*
