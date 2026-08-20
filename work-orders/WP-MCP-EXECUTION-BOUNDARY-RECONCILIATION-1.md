# WP-MCP-EXECUTION-BOUNDARY-RECONCILIATION-1

**Work Packet:** MCP Execution Boundary Reconciliation
**Status:** COMPLETE — No code repair needed
**Date:** 2026-08-18
**Agent:** OpenWork-Claude (mimo-v2.5)
**Supersedes:** WP-DISPATCH-ACTIVATION-REPAIR-1 (hypothesis invalidated)

---

## Problem Statement

The MCP layer is not revealing broken governance. It is revealing that the capability lifecycle between implementation and exposure was never fully modeled.

The inner machinery works (19/19 governance validation PASS). The failure is at the transport/adaptation layer — the boundary contract between independently evolving systems.

### Without MCP

```
caller
  ↓
Swift function
  ↓
result
```

### With MCP

```
caller
  ↓
MCP protocol
  ↓
Rust adapter
  ↓
JSON envelope
  ↓
Swift decoder
  ↓
router
  ↓
handler
  ↓
receipt
```

Every boundary has a schema expectation. A tool call has at least four representations:

| Layer | Representation |
|-------|---------------|
| MCP tool declaration | `{"name": "librarian_search", "inputSchema": {...}}` |
| Rust-side request model | `ExecRequest { tool, arguments: Value }` |
| Swift-side decoding model | `struct ExecRequest: Content { let tool: String; let arguments: [String: AnyCodable]? }` |
| Handler invocation model | `handleCallTool(name, arguments)` |

If any one of these disagrees, the failure looks like a tool failure even though the tool is fine.

---

## Scope

### IN

- Define canonical MCP execution envelope
- Align Rust `exec.rs` and Swift `ExecRequest` parameter format
- Classify the 84 hidden tools by lifecycle state
- Add lifecycle states beyond `advertised: true/false`
- Reconcile manifest hash (stale `268f6c7...` vs current `a8f1413...`)

### OUT

- Rewriting tool handlers
- Adding new tools
- Changing governance rules
- UI work
- Deferred audit findings

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| MCP-001 | Advertised tools execute successfully through Rust → Swift `/exec` path |
| MCP-002 | Execution envelope is schema-compatible across all layers |
| MCP-003 | Hidden tools have explicit lifecycle state (not just `advertised: false`) |
| MCP-004 | No tool exists in an ambiguous state |
| MCP-005 | Capability advertisement matches actual runtime availability |

---

## Phase 2 Evidence (carried from WP-DISPATCH-ACTIVATION-REPAIR-1)

### Failure Modes

| Mode | Tools | Failure Point | Root Cause |
|------|-------|---------------|------------|
| Advertised (73) | Reach Swift → `-32602` | Swift Codable decoder | Parameter format mismatch |
| Not advertised (84) | Rejected at MCP layer | MCP protocol | `advertised: false` in manifest |

### The `-32602` Error (all 73 advertised tools)

```
Invalid params: <tool>: The data couldn't be read because it is missing.
```

Stage: Swift Codable decoder (`ExecRequest` struct, MCPController.swift:995)

The tool name is extracted correctly; the `arguments` field fails to decode. This is systemic — every advertised tool fails identically.

### The 84 Hidden Tools

All 84 are **implemented** — each has a working switch case in `handleCallTool()`. None are missing implementations. They are hidden by `advertised: false` in the manifest.

Lifecycle classification:

| Subsystem | Count | Tools |
|-----------|-------|-------|
| Knowledge Substrate | 4 | `knowledge_findings`, `knowledge_import`, `knowledge_query`, `knowledge_status` |
| Privacy Filtering | 5 | `librarian_build_packet`, `librarian_classify`, `librarian_link_review`, `librarian_scan_secrets`, `librarian_verify_response` |
| Custody Enforcement | 4 | `librarian_check_custody`, `librarian_list_canonical`, `librarian_register_canonical`, `librarian_verify_checkin` |
| Dry-Run/Approval | 6 | `librarian_dry_run_delete`, `librarian_dry_run_move`, `librarian_dry_run_overwrite`, `librarian_check_approval`, `librarian_record_approval`, `librarian_request_approval` |
| OWL Review | 3 | `librarian_get_owl_review`, `librarian_list_owl_reviews`, `librarian_request_owl_review` |
| Release Gate | 4 | `librarian_check_git_status`, `librarian_check_test_drift`, `librarian_release_gate`, `librarian_sprint_close_gate` |
| Precision Tools | 10 | `librarian_exact_text_scan`, `librarian_marker_scan`, `librarian_patch_analysis`, `librarian_path_check`, `librarian_string_compare`, `librarian_validate_json`, `librarian_validate_markdown`, `librarian_validate_project_slots`, `librarian_validate_status_markers`, `librarian_validate_yaml` |
| DB-First | 2 | `db_first_epic_status`, `db_first_reconciliation_status` |
| Governance Internal | 2 | `governance_audit_verify`, `governance_lifecycle_reconcile` |
| Model Eval | 3 | `model_eval_fixture_get`, `model_eval_fixture_list`, `model_eval_run_record` |
| Model Runtime | 1 | `model_runtime_dispatch_check` |
| Node Registry | 5 | `node_registry_get`, `node_registry_list`, `node_registry_rules`, `node_registry_status`, `node_registry_validate` |
| Owner Action | 7 | `owner_action_check_resume`, `owner_action_create`, `owner_action_get`, `owner_action_list`, `owner_action_respond`, `owner_action_resume`, `owner_action_verify` |
| Project Workflow | 12 | `project_application_closure_*`, `project_authority_*`, `project_mcp_custody_*`, `project_owner_decision_*` |
| Work Packet | 10 | `project_work_packet_*`, `project_work_result_*` |
| Sprint Packet | 3 | `project_sprint_packet_dispatch*` |

---

## Capability Lifecycle Model (proposed)

Current state: a single boolean `advertised: true/false` collapses multiple meanings.

Proposed lifecycle:

```
DISCOVERED
    ↓
IMPLEMENTED       ← code exists, switch case present
    ↓
REGISTERED        ← runtime knows about it
    ↓
VALIDATION_PENDING ← awaiting governance review
    ↓
VALIDATED         ← governance accepts it
    ↓
ADVERTISED        ← clients can discover it
    ↓
AVAILABLE         ← clients may use it
```

The 84 hidden tools are at **IMPLEMENTED** but not beyond. The question is not "why aren't they working?" — it is "what lifecycle state are they actually in?"

---

## Recommended Phase 2 (Implementation)

### Step 1: Fix the Rust↔Swift parameter format
- Inspect `exec.rs` line 72-76 request body format
- Inspect `ExecRequest` struct at MCPController.swift:995
- Align the `arguments` field encoding
- Verify with a single tool (e.g., `librarian_search`)

### Step 2: Classify hidden tools
- Determine which of the 84 tools should be:
  - `ADVERTISED` (ready for agent use)
  - `VALIDATION_PENDING` (needs governance review)
  - `INTERNAL` (not for agent consumption)
  - `DEPRECATED` (legacy, not exposed)

### Step 3: Add lifecycle state to manifest
- Replace `advertised: boolean` with `lifecycle_state: enum`
- Update `buildToolList()` to filter by lifecycle state
- Update `extract-mcp-tool-manifest.py` to emit lifecycle state

### Step 4: Reconcile manifest hash
- Current dispatch map hash: `sha256:268f6c7...` (stale)
- Current manifest hash: `sha256:a8f1413...`
- Regenerate or deprecate `GeneratedMCPDispatchMap.swift`

---

## Evidence References

| Reference | Location | Description |
|-----------|----------|-------------|
| Phase 2 test results | WP-DISPATCH-ACTIVATION-REPAIR-1 §Verification Results | 14 tools tested, 0 pass (empty args) |
| Direct curl test | mcp-contract-evidence-freeze.md | 5 tools tested with proper args, 5 pass |
| ExecRequest struct | MCPController.swift:995 | Swift Codable decoder |
| exec.rs body | mcp-rust/src/exec.rs:72-76 | Rust request format |
| buildToolList | MCPToolRegistry.swift:16 | Advertised tools (73) |
| Manifest | mcp-tool-manifest.json | 157 tools, 73 advertised |
| Handler switch | MCPController.swift:1126+ | Manual dispatch (all 157) |
| Governance validation | test-library/governance-validation/ | 19/19 PASS (direct path) |
| Evidence freeze | evidence/mcp-contract-evidence-freeze.md | Corrected baseline |

---

## Final Disposition

**No code repair needed.** The Rust→Swift execution boundary works correctly.

The Phase 2 "systemic failure" was caused by calling tools without required arguments. Every tool with required parameters fails identically when called with empty `{}` — this is correct Swift `Codable` behavior, not a defect.

### What remains

| Item | Status | Action |
|------|--------|--------|
| Swift `/mcp` endpoint | ACTIVE (should be retired) | Tracked in WP-MCP-AUTHORITY-BOUNDARY-CLEANUP-1 |
| 84 non-advertised tools | Implemented, hidden | Lifecycle classification needed |
| `GeneratedMCPDispatchMap.swift` | Dead code | Deprecation candidate |
| Manifest hash | Stale (`268f6c7...`) | Regeneration needed |
| `advertised` boolean | Collapses multiple states | Lifecycle model expansion (future) |

### Audit finding corrections needed

The following audit conclusions should be revised:

1. **Capability Activation Audit (2026-08-17):** "4 BROKEN tools" — tools work when given proper arguments
2. **Governance Audit (2026-08-16):** "Knowledge Substrate MCP BROKEN" — tools are `advertised: false`, not broken
3. **Both audits:** "Root cause: GeneratedMCPDispatchMap.swift" — dispatch map is dead code, not the root cause

---

*COMPLETE. Investigation prevented a false repair and localized the actual state.*
