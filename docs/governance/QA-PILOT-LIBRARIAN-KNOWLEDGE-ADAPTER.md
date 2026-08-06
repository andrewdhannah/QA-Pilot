# QA Pilot Librarian Knowledge Adapter

**Sprint:** QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER-1
**Epic:** EPIC-QA-PILOT-TRAINING-SYSTEM-1 (Sprint 3/11)
**Status:** complete_pending_owner_review

## Purpose

Create the governed read-only bridge that allows QA Pilot to consume Librarian canonical knowledge for training generation. This is the first implementation sprint in the training system epic — it establishes the knowledge retrieval layer that all subsequent training generation sprints depend on.

## Architecture

```
Librarian Canonical Artifact
          ↓
Knowledge Adapter (read-only)
          ↓
  Source Reference / Provenance Record
          ↓
QA Pilot Training Layer (Sprints 4+)
          ↓
Training Artifact with Source Lineage
```

## Operations

| Command | Purpose | Output |
|---------|---------|--------|
| `scan` | Discover all available Librarian sources | Counts by type, full source list |
| `query` | Search sources by path pattern, type, or keyword | Matching source references |
| `reference` | Create structured source reference for a file | Source reference with path, revision, hash |
| `provenance` | Create provenance record linking multiple sources | Record with source_hash, advisory flags |
| `verify` | Verify source accessibility and hash integrity | Per-source accessible + hash_match status |
| `status` | Show adapter configuration and state | Librarian accessibility, source counts |

## Source Types

| Type | Librarian Path | Content |
|------|---------------|---------|
| `governance` | `docs/governance/` | Governance documents, operating models |
| `schema` | `docs/schemas/` | JSON schemas for all governed artifacts |
| `rule` | `docs/rules/` | Operating rules and protocols |
| `ledger` | `project-state/sprint-ledger.json` | Canonical sprint ledger |
| `receipt` | `receipts/decision-resolutions/` | Owner decision receipts |

## Rules

| Rule | Description |
|------|-------------|
| KA-1 | Adapter version must be `knowledge-adapter-v1` |
| KA-2 | Operation must be one of scan/query/reference/provenance/verify/status |
| KA-3 | `generated_at` must be valid ISO 8601 UTC |
| KA-4 | Source references require path, revision, source_type, accessible |
| KA-5 | Provenance records require provenance_id, sources, source_hash |
| KA-6 | Provenance `source_hash` must be valid SHA-256 hex (64 chars) |
| KA-7 | Provenance `advisory` must be true |
| KA-8 | Provenance `no_authority_promotion` must be true |
| KA-9 | Verify operation status matches accessibility + hash results |
| KA-10 | No Librarian mutation paths in adapter output |
| KA-11 | Scan returns sources grouped by type with correct counts |
| KA-12 | Query results respect type/keyword filters |
| KA-13 | Reference returns accessible status per path |
| KA-14 | Status reports advisory-only authority |

## Hard Boundaries

- **No write access** to Librarian filesystem or MCP tools
- **No cross-project write capability**
- **No authority promotion** through knowledge references
- **No training generation** — this sprint only establishes the retrieval layer
- **Advisory-only** — all adapter output is advisory, never authoritative

## Artifacts

| Artifact | Path |
|----------|------|
| Schema | `docs/schemas/qa-pilot-knowledge-adapter.schema.json` |
| CLI | `scripts/qa_pilot_knowledge_adapter.py` (6 commands) |
| Validator | `scripts/validate-qa-pilot-knowledge-adapter.py` (14 rules KA-1 to KA-14) |
| Test runner | `scripts/test-qa-pilot-knowledge-adapter.sh` |
| Fixtures | `docs/examples/qa-pilot-knowledge-adapter/` (3 valid + 3 invalid) |
| Governance doc | `docs/governance/QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER.md` |
| Sprint doc | `docs/sprints/QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER-1.md` |
