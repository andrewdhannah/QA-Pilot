# QA Pilot Broker Audit Store Implementation — Governance

**Sprint:** QA-PILOT-BROKER-AUDIT-STORE-IMPLEMENTATION-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** QA Pilot-local broker audit store. Advisory-only. No Librarian mutation.

---

## 1. Purpose

Implement QA Pilot-owned broker audit storage mechanics using the sealed broker audit receipt schema. The audit store provides register, get, list, and status operations for broker audit receipts with schema validation, advisory-only enforcement, and bounded listing.

## 2. Store Operations

| Operation | Authority | Description |
|-----------|-----------|-------------|
| register | R1 (advisory mutation) | Validate and persist a broker audit receipt |
| get | R0 (read-only) | Retrieve an audit receipt by audit_id |
| list | R0 (read-only) | List audit receipts with bounded limit 1-100 |
| status | R0 (read-only) | Audit store status summary |

## 3. Validation Rules

The store validates every incoming receipt against the sealed schema and enforces:
- No approval/seal/merge/production_readiness in output_effects
- No Librarian runtime/MCPController paths in handler_path
- advisory_only must be true
- All 13 required fields present

## 4. Storage Paths

| Path | Purpose |
|------|---------|
| `data/audit/broker/` | Individual audit receipt files |
| `data/audit/broker-index.json` | Audit receipt index |
| `data/audit/broker-status.json` | Audit store status |

## 5. Boundaries

- All changes inside `active/qa-pilot/`
- No Librarian repo mutation
- No MCPController/native registration
- No cross-project runtime integration
- No approval, seal, merge, or production-readiness authority
- No external QA Pilot production repo modification

## 6. Non-Goals

- No Librarian runtime integration
- No native MCP registration
- No cross-project execution
- No authority expansion
