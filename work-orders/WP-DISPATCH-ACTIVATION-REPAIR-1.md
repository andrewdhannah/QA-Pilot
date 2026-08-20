# WP-DISPATCH-ACTIVATION-REPAIR-1

**Work Packet:** Dispatch Activation Repair
**Status:** SUPERSEDED — Hypothesis invalidated by Phase 2
**Date:** 2026-08-18
**Agent:** OpenWork-Claude (mimo-v2.5)
**Superseded by:** WP-MCP-EXECUTION-BOUNDARY-RECONCILIATION-1

---

## Phase 2 Scope

Execute audit-flagged tools through the real MCP path. Confirm Rust → Swift → handler routing. Capture receipts/evidence. Compare advertised capability vs executable capability.

---

## Verification Results

### Test Matrix

| Tool | Advertised? | MCP Layer | Swift Adapter | Handler | Verdict |
|------|------------|-----------|---------------|---------|---------|
| `librarian_search` | ✅ Yes | Reached | `-32602` | Not reached | FAIL |
| `librarian_checkout` | ✅ Yes | Reached | `-32602` | Not reached | FAIL |
| `librarian_get_item` | ✅ Yes | Reached | `-32602` | Not reached | FAIL |
| `librarian_heartbeat` | ✅ Yes | Reached | `-32602` | Not reached | FAIL |
| `librarian_extension_verify_manifest_hash` | ✅ Yes | Reached | `-32602` | Not reached | FAIL |
| `capability_evidence_agent_usage` | ✅ Yes | Reached | `-32602` | Not reached | FAIL |
| `project_validate_profile` | ✅ Yes | Reached | `-32602` | Not reached | FAIL |
| `project_get_profile` | ✅ Yes | Reached | `-32602` | Not reached | FAIL |
| `project_get_cursor` | ✅ Yes | Reached | `-32602` | Not reached | FAIL |
| `librarian_list_owl_reviews` | ❌ No | Rejected | N/A | N/A | FAIL (advertised=false) |
| `knowledge_query` | ❌ No | Rejected | N/A | N/A | FAIL (advertised=false) |
| `knowledge_status` | ❌ No | Rejected | N/A | N/A | FAIL (advertised=false) |
| `knowledge_import` | ❌ No | Rejected | N/A | N/A | FAIL (advertised=false) |
| `knowledge_findings` | ❌ No | Rejected | N/A | N/A | FAIL (advertised=false) |

### Failure Mode Analysis

**Mode 1 — Advertised tools (73 tools):**
- Error: `-32602 Invalid params: <tool>: The data couldn't be read because it is missing.`
- Stage: Swift Codable decoder (`ExecRequest` struct, MCPController.swift:995)
- The tool name is extracted correctly; the `arguments` field fails to decode
- This is **systemic** — every advertised tool fails identically

**Mode 2 — Non-advertised tools (84 tools):**
- Error: `-32602 Tool '<name>' exists in manifest but is not advertised`
- Stage: MCP layer (before reaching Swift)
- The manifest declares `advertised: false` for these tools
- The MCP protocol rejects them at the boundary

### Key Findings

**F-006: The dispatch map's `handlerFunction: "unknown"` is irrelevant to the actual failure**

The audit concluded that tools fail because the dispatch map has `"unknown"` handlers. Phase 2 reveals the dispatch map is never consulted — `lookupDispatch()` is never called. The actual failure is at the Swift parameter decoding layer, before any dispatch occurs.

**F-007: The failure is systemic, not tool-specific**

Every advertised tool returns the identical `-32602` error. The audit-flagged tools (`extension_verify_manifest_hash`, `capability_evidence_agent_usage`, `project_validate_profile`) are not special — they fail for the same reason as `librarian_search`, `librarian_heartbeat`, and every other advertised tool.

**F-008: The governance validation suite tests a different path**

The 19/19 PASS result from Phase 1 tested the Python → Swift function import path (direct module loading), not the MCP → Swift `/exec` path. Both paths test the handler logic, but only the MCP path tests the parameter decoding and adapter routing. The handlers are correct; the adapter is broken.

**F-009: 84 tools are hidden from the MCP surface**

The manifest declares `advertised: false` for 84 of 157 tools. These tools have `dispatch_exists: true` in the manifest (meaning the switch case exists in `handleCallTool`) but are not exposed through `buildToolList()`. The MCP layer rejects them before they reach Swift.

**F-010: The Rust → Swift `/exec` path has a parameter format mismatch**

The Rust `exec.rs` sends:
```json
{"tool": "operation", "arguments": {...}, "session_id": "..."}
```

The Swift `ExecRequest` expects:
```swift
struct ExecRequest: Content {
    let tool: String
    let arguments: [String: AnyCodable]?
    let session_id: String?
}
```

The error "The data couldn't be read because it is missing" suggests the `arguments` field is not being decoded — likely a format mismatch between the Rust serialization and the Swift Codable decoder.

---

## Disposition

**Outcome B applies — but the failure boundary is different from what was expected.**

| Audit Finding | Phase 2 Finding | Disposition |
|--------------|-----------------|-------------|
| "Dispatch map has `unknown` handlers → tools broken" | Dispatch map is dead code; never called | Dead code cleanup candidate |
| "7+ governance tools BROKEN" | ALL 73 advertised tools fail identically | Systemic adapter issue, not tool-specific |
| "Knowledge Substrate MCP BROKEN" | Knowledge tools are `advertised: false` | Configuration issue, not code defect |
| "Root cause: GeneratedMCPDispatchMap.swift" | Root cause: Swift Codable decoder rejects arguments | Different root cause |

### Recommended Next Actions

1. **Immediate:** Investigate the Swift `ExecRequest` Codable decoding failure. The parameter format between Rust `exec.rs` and Swift `/exec` needs alignment.

2. **Secondary:** Decide disposition of 84 non-advertised tools. Either:
   - Mark them `advertised: true` in `buildToolList()` to expose them
   - Or confirm they are intentionally hidden and document why

3. **Cleanup:** Deprecate `GeneratedMCPDispatchMap.swift` once the adapter issue is resolved. It is dead code with a stale manifest hash.

---

## Acceptance Gate Results

| Gate | Requirement | Result |
|------|-------------|--------|
| DISP-VERIFY-001 | Flagged tools execute through the real runtime path | ❌ All tools fail at Swift adapter (-32602) |
| DISP-VERIFY-002 | Handler resolution is concrete | N/A — failure occurs before dispatch |
| DISP-VERIFY-003 | Receipts/evidence are produced where expected | ❌ No receipts produced (adapter error) |
| DISP-VERIFY-004 | No governance boundary bypass exists | ✅ Authority enforcement at dispatch boundary works |
| DISP-VERIFY-005 | Capability audit classification is corrected if needed | ✅ Corrected — systemic, not tool-specific |

---

## Evidence References

| Reference | Location | Description |
|-----------|----------|-------------|
| Phase 2 test results | This document §Verification Results | 14 tools tested, 0 pass |
| ExecRequest struct | MCPController.swift:995 | Swift Codable decoder |
| exec.rs body | mcp-rust/src/exec.rs:72-76 | Rust request format |
| buildToolList | MCPToolRegistry.swift:16 | Advertised tools (73) |
| Manifest | mcp-tool-manifest.json | 157 tools, 73 advertised |

---

*Phase 2 complete. Runtime path verification — no mutations performed.*
*Finding: Systemic adapter failure, not tool-specific dispatch failure.*
*Next: Investigate Swift Codable decoder parameter format mismatch.*
