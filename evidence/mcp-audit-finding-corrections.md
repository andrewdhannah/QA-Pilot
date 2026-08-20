# MCP Investigation — Audit Finding Corrections

**Date:** 2026-08-18
**Source:** WP-DISPATCH-ACTIVATION-REPAIR-1 → WP-MCP-EXECUTION-BOUNDARY-RECONCILIATION-1
**Status:** CORRECTED

---

## Corrected Findings

### Capability Activation Audit (2026-08-17) — Corrections

| Original Finding | Corrected Finding | Evidence |
|-----------------|-------------------|----------|
| "4 BROKEN tools due to dispatch map `handlerFunction: unknown`" | Tools execute correctly when given required arguments. Dispatch map is dead code — never called. | Direct curl test: 5/5 tools pass with proper args |
| "Root cause: GeneratedMCPDispatchMap.swift has `unknown` for every tool" | Dispatch map (`lookupDispatch()`) is never invoked. `/exec` routes through manual `switch` in `handleCallTool()`. | `lookupDispatch()` has zero call sites in codebase |
| "Knowledge Substrate MCP BROKEN" | Knowledge tools are `advertised: false` in manifest, not broken. They execute when the advertisement gate is bypassed. | `knowledge_query` rejected at advertisement layer, not execution layer |
| "7+ governance tools return adapter errors" | Tools return `-32602` when called without required arguments. This is correct Swift `Codable` behavior. | All tested tools pass with proper arguments |

### Governance Audit (2026-08-16) — Corrections

| Original Finding | Corrected Finding | Evidence |
|-----------------|-------------------|----------|
| "Knowledge Substrate MCP tools not wired" | Knowledge tools are implemented and routed correctly. They are intentionally not advertised (`advertised: false`). | Switch case exists in `handleCallTool()`; advertisement gate rejects them |
| "Extension identity binding non-functional" | Separate from MCP execution. Extension lifecycle is a governance concern, not a routing defect. | N/A — outside MCP investigation scope |
| "Profile validation broken" | `project_validate_profile` executes correctly with all required arguments. | Direct test: `{"profile_id":"full","profile_name":"Full","project_id":"qa-pilot","profile_type":"full","modules":{}}` returns validation result |

---

## Corrected System State

| Component | State | Notes |
|-----------|-------|-------|
| MCP execution boundary | **PASS** | Rust→Swift `/exec` works correctly |
| Tool implementations | **EXIST** | All 157 tools have switch cases in `handleCallTool()` |
| Tool invocation (with args) | **PASS** | All tested tools succeed with proper arguments |
| Tool invocation (empty args) | **CORRECT BEHAVIOR** | `-32602` for missing required params is standard |
| OpenWork Cloud adapter | **LIMITATION** | Sends `{}` for some calls, causing apparent failures |
| Governance validation suite | **VALID** | Tests direct Swift imports, not MCP path — different scope |
| 84 non-advertised tools | **IMPLEMENTED, HIDDEN** | Need lifecycle classification |
| GeneratedMCPDispatchMap.swift | **DEAD ARTIFACT** | Never invoked; retirement candidate |

---

*Corrections applied. Canonical audit record updated.*
