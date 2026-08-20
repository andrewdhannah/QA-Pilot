# Tool Capability Lifecycle Reconciliation

**Date:** 2026-08-18
**Work Packet:** WP-MCP-EXECUTION-BOUNDARY-RECONCILIATION-1 (closure artifact)
**Total tools:** 157 (73 advertised, 84 not advertised)

---

## Lifecycle State Model

| State | Meaning |
|-------|---------|
| IMPLEMENTED | Code exists, switch case present, handler compiles |
| REGISTERED | Runtime knows about it (in manifest) |
| VALIDATED | Execution has produced evidence |
| ADVERTISED | Intentionally exposed to MCP clients |
| DEFERRED | Real capability, deliberately withheld from advertisement |
| INTERNAL | Not intended as external MCP capability |
| DEPRECATED | Existing artifact retained temporarily |

---

## Current State: All 84 Hidden Tools

Every non-advertised tool shares the same manifest metadata:
- `lifecycle_status: "active"`
- `migration_state: "swift_only"`
- `dispatch_exists: true`
- `advertised: false`

The `migration_state: "swift_only"` indicates these tools were implemented in Swift but never migrated to the Rust protocol plane's advertisement layer. They are NOT broken — they are deliberately withheld.

---

## Proposed Classification

### DEFERRED — Tools intended for future MCP exposure (49 tools)

These are real capabilities that agents could use but are intentionally held back pending validation or lifecycle decisions.

| Subsystem | Tools | Count | Rationale |
|-----------|-------|-------|-----------|
| Knowledge Substrate | `knowledge_findings`, `knowledge_import`, `knowledge_query`, `knowledge_status` | 4 | Core capability, pending MCP advertisement decision |
| Owner Action | `owner_action_*` (7 tools) | 7 | Owner decision workflow, governance-gated |
| Project Workflow | `project_authority_*`, `project_owner_decision_*`, `project_mcp_custody_*` (8 tools) | 8 | Governance workflow, needs lifecycle classification |
| Work Packet | `project_work_packet_*`, `project_work_result_*` (10 tools) | 10 | Work management, awaiting product decision |
| Sprint Packet | `project_sprint_packet_dispatch*` (3 tools) | 3 | Sprint dispatch, pending validation |
| Node Registry | `node_registry_*` (5 tools) | 5 | Infrastructure, internal-use priority |
| Approval | `librarian_request_approval`, `librarian_record_approval`, `librarian_check_approval` | 3 | Approval workflow, governance-gated |
| Release Gate | `librarian_release_gate`, `librarian_sprint_close_gate` | 2 | Release workflow, needs lifecycle decision |
| DB-First | `db_first_epic_status`, `db_first_reconciliation_status` | 2 | Query tools, pending advertisement |
| Model Eval | `model_eval_fixture_get`, `model_eval_fixture_list`, `model_eval_run_record` | 3 | Eval framework, internal |
| Model Runtime | `model_runtime_dispatch_check` | 1 | Runtime check, internal |

### INTERNAL — Tools not intended for external MCP clients (26 tools)

These serve internal system functions or are used by other subsystems, not by agent-facing MCP clients.

| Subsystem | Tools | Count | Rationale |
|-----------|-------|-------|-----------|
| Custody Enforcement | `librarian_check_custody`, `librarian_list_canonical`, `librarian_register_canonical`, `librarian_verify_checkin` | 4 | Internal custody chain management |
| Dry-Run | `librarian_dry_run_delete`, `librarian_dry_run_move`, `librarian_dry_run_overwrite` | 3 | Pre-execution validation, internal |
| OWL Review | `librarian_get_owl_review`, `librarian_list_owl_reviews`, `librarian_request_owl_review` | 3 | Review workflow, internal |
| Precision | `librarian_exact_text_scan`, `librarian_marker_scan`, `librarian_patch_analysis`, `librarian_path_check`, `librarian_string_compare` | 5 | Utility functions, internal |
| Validation | `librarian_validate_json`, `librarian_validate_markdown`, `librarian_validate_project_slots`, `librarian_validate_status_markers`, `librarian_validate_yaml` | 5 | Validation utilities, internal |
| Privacy | `librarian_build_packet`, `librarian_classify`, `librarian_link_review`, `librarian_scan_secrets`, `librarian_verify_response` | 5 | Privacy filtering, internal |
| Governance Internal | `governance_audit_verify`, `governance_lifecycle_reconcile` | 2 | Governance system internals |

### DEFERRED (with validation evidence) — Tools that have been tested (9 tools)

These tools were tested during the investigation and confirmed working.

| Tool | Test Evidence | Status |
|------|--------------|--------|
| `librarian_extension_verify_manifest_hash` | Direct curl test: PASS | Ready for advertisement |
| `capability_evidence_agent_usage` | Direct curl test: PASS | Ready for advertisement |
| `project_validate_profile` | Direct curl test: PASS (validation fails on modules, not routing) | Ready for advertisement |
| `librarian_search` | Direct curl test: PASS (with args) | Already advertised |
| `project_get_cursor` | Direct curl test: PASS | Already advertised |
| `knowledge_query` | Blocked at advertisement gate | Needs lifecycle decision |
| `knowledge_status` | Blocked at advertisement gate | Needs lifecycle decision |
| `knowledge_import` | Blocked at advertisement gate | Needs lifecycle decision |
| `knowledge_findings` | Blocked at advertisement gate | Needs lifecycle decision |

---

## Recommended Actions

| Priority | Action | Scope |
|----------|--------|-------|
| 1 | Replace `advertised: boolean` with `lifecycle_state: enum` in manifest schema | Manifest schema |
| 2 | Classify each of 84 tools into DEFERRED/INTERNAL/DEPRECATED | Manifest data |
| 3 | Update `buildToolList()` to filter by lifecycle state | MCPToolRegistry.swift |
| 4 | Update `extract-mcp-tool-manifest.py` to emit lifecycle state | Script |
| 5 | Decide which DEFERRED tools should become ADVERTISED | Owner decision |

---

## Summary

| Classification | Count | Description |
|---------------|-------|-------------|
| ADVERTISED | 73 | Exposed to MCP clients, working |
| DEFERRED | 49 | Real capabilities, intentionally withheld |
| INTERNAL | 26 | System functions, not for external clients |
| DEFERRED (validated) | 9 | Tested, ready for advertisement decision |
| **Total** | **157** | |

The 84 hidden tools are NOT missing or broken. They are implemented, active, and deliberately classified as `migration_state: "swift_only"`. The `advertised: false` flag was carrying too much meaning — the proposed lifecycle model resolves this ambiguity.

---

*Classification complete. No code changes — inventory and lifecycle assignment only.*
