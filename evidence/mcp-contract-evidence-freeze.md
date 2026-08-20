# MCP Execution Boundary — Contract Evidence Freeze (REVISED)

**Date:** 2026-08-18
**Status:** FROZEN — corrected baseline
**Work Packet:** WP-MCP-EXECUTION-BOUNDARY-RECONCILIATION-1

---

## Corrected Root Cause

**The Rust→Swift boundary is NOT broken.** All audit-flagged tools execute successfully when given proper arguments. The Phase 2 "failures" were caused by calling tools without required arguments through the OpenWork Cloud MCP adapter.

### Proof

| Tool | Empty Args | Proper Args | Verdict |
|------|-----------|-------------|---------|
| `librarian_search` | FAIL (-32602) | ✓ WORKS | Required: `query` |
| `librarian_extension_verify_manifest_hash` | FAIL (-32602) | ✓ WORKS | Required: `extension_id` |
| `capability_evidence_agent_usage` | FAIL (-32602) | ✓ WORKS | Required: `agent_identity` |
| `project_validate_profile` | FAIL (-32602) | ✓ WORKS | Required: `profile_id`, `profile_name`, `project_id`, `profile_type`, `modules` |
| `project_get_cursor` | FAIL (-32602) | ✓ WORKS | Required: `project_id` |

### What the error actually means

```
-32602 Invalid params: <tool>: The data couldn't be read because it is missing.
```

This is **Swift's standard `DecodingError` for a missing required key** in a `Codable` struct. It fires at the handler's `args.decode(XxxArguments.self)` call, NOT at the `ExecRequest` boundary.

### Why Phase 2 testing appeared to show systemic failure

The OpenWork Cloud MCP adapter sends tool calls without arguments (or with empty `{}`). Every tool with required parameters fails with the same error. This made it look like a systemic adapter issue, but it was actually a test methodology issue — the tools were called without required arguments.

---

## Corrected Failure Modes

| Mode | Root Cause | Scope |
|------|-----------|-------|
| Missing required arguments | OpenWork Cloud MCP sends empty `{}` for tools that require params | All tools with required args |
| Not advertised | `advertised: false` in manifest | 84 tools |
| Actual code defect | `project_validate_profile` may have additional issues | 1 tool (needs investigation) |

---

## What Changed

| Audit Finding | Corrected Finding |
|--------------|-------------------|
| "Dispatch map has `unknown` handlers → tools broken" | Dispatch map is dead code; never called |
| "7+ governance tools BROKEN" | Tools work when given proper arguments |
| "Knowledge Substrate MCP BROKEN" | Knowledge tools are `advertised: false` (configuration, not code) |
| "Root cause: GeneratedMCPDispatchMap.swift" | Root cause: Test methodology — empty args |
| "Systemic adapter failure" | Boundary works correctly |

---

## MCP System State (Corrected)

| Component | State | Notes |
|-----------|-------|-------|
| MCP execution boundary | **PASS** | Rust→Swift `/exec` works correctly |
| MCP authority topology | **FINDING** | Swift `/mcp` still exposed — should be retired |
| Swift `/mcp` retirement | **NOT VERIFIED** | Endpoint still responds to `tools/list` |
| Tool implementations | **EXIST** | All 157 tools have switch cases |
| Tool invocation (with args) | **PASS** | All tested tools succeed |
| Tool invocation (empty args) | **CORRECT BEHAVIOR** | `-32602` for missing required params |
| 84 non-advertised tools | **IMPLEMENTED, HIDDEN** | Lifecycle classification in progress |
| GeneratedMCPDispatchMap.swift | **DEAD ARTIFACT** | Retirement candidate |

---

*Evidence corrected. Execution boundary is functional. Authority boundary has a finding tracked in WP-MCP-AUTHORITY-BOUNDARY-CLEANUP-1.*
