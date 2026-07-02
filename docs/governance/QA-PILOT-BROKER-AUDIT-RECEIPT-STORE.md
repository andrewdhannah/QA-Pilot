# QA Pilot Broker Audit Receipt Store — Governance

**Sprint:** QA-PILOT-BROKER-AUDIT-RECEIPT-STORE-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** QA Pilot-local broker audit receipt store. Advisory-only. No Librarian mutation.

---

## 1. Purpose

Define, validate, and govern the QA Pilot broker audit receipt store schema. Broker audit receipts are generated for every broker call (accepted or rejected) and must prove custody, tool routing, advisory-only output, and rollback/audit traceability without granting approval, seal, merge, or production-readiness authority.

## 2. Audit Receipt Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `audit_id` | string | Yes | Unique audit receipt identifier |
| `receipt_type` | string | Yes | Must be `"broker_audit"` |
| `active_project_id` | string | Yes | Must be `"qa-pilot"` |
| `target_project_id` | string | Yes | Must be `"qa-pilot"` |
| `requested_tool` | string | Yes | Tool name from sealed surface |
| `custody_record_id` | string | Yes | Custody record identifier |
| `handler_path` | string | Yes | QA Pilot project-local handler path |
| `authority_level` | string | Yes | `"R0"` (read-only) or `"R1"` (advisory) |
| `advisory_only` | boolean | Yes | Must be `true` |
| `output_effects` | array | Yes | Effects of the output — must not include approval/seal/merge/production_readiness/runtime_mutation |
| `audit_timestamp` | string | Yes | ISO 8601 timestamp |
| `rollback_reference` | string | Yes | Reference to rollback plan or policy |
| `validation_result` | string | Yes | One of `"pass"`, `"fail"`, `"blocked"`, `"advisory_only"` |

## 3. Validation Rules (BA-1 through BA-12)

| Rule | Condition |
|------|-----------|
| BA-1 | receipt_type must be `"broker_audit"` |
| BA-2 | active_project_id must be `"qa-pilot"` |
| BA-3 | target_project_id must be `"qa-pilot"` |
| BA-4 | requested_tool must belong to sealed QA Pilot MCP/advisory broker surface |
| BA-5 | handler_path must be QA Pilot project-local (`active/qa-pilot/`) |
| BA-6 | authority_level must be `"R0"` (read-only) or `"R1"` (advisory) |
| BA-7 | advisory_only must be `true` |
| BA-8 | output_effects must not include `approval`, `seal`, `merge`, `production_readiness`, or `runtime_mutation` |
| BA-9 | custody_record_id must be present and non-empty |
| BA-10 | rollback_reference must be present and non-empty |
| BA-11 | validation_result must be `"pass"`, `"fail"`, `"blocked"`, or `"advisory_only"` |
| BA-12 | No Librarian runtime/MCPController path may appear as an implementation target |

## 4. Storage

Broker audit receipts are stored at `data/audit/broker/<audit_id>.json`. This sprint does not modify the storage mechanism — it defines and validates the schema.

## 5. Boundaries

- All changes remain inside `active/qa-pilot/`
- No Librarian repo mutation
- No MCPController/native registration
- No cross-project runtime integration
- No approval, seal, merge, or production-readiness authority
- No external QA Pilot production repo modification

## 6. Non-Goals

- No runtime implementation
- No storage mechanism changes
- No native MCP registration
- No cross-project integration
- No authority expansion
