# WP-MCP-AUTHORITY-BOUNDARY-CLEANUP-1

**Work Packet:** MCP Authority Boundary Cleanup
**Phase:** 3 — Verification
**Status:** COMPLETE
**Date:** 2026-08-18
**Agent:** OpenWork-Claude (mimo-v2.5)

---

## Finding

Retired Swift MCP authority surface (`POST /mcp`) remains exposed on the same process that serves the authorized execution adapter (`POST /exec`).

### Severity

Medium — architectural boundary drift

### Impact

Potential dual MCP authority. Future clients may bypass the Rust protocol plane and call Swift `/mcp` directly, creating an ungoverned execution path.

---

## Current Topology

```
Client
  |
  +--> Rust MCP :3457       ← sole MCP authority (per MCP-RETIRE-019, #564)
  |
  +--> Swift MCP :3456/mcp  ← RETIRED but still active ❌
  |
  +--> Swift /exec :3456    ← intended execution adapter ✅
```

## Required Topology

```
Client
  |
  v
Rust MCP :3457
  |
  v
Swift /exec :3456
```

---

## Scope

### IN

- Confirm current `/mcp` exposure on Swift :3456
- Confirm Rust remains sole MCP authority
- Remove/disable Swift `/mcp` route registration
- Preserve `/exec` endpoint
- Verify Rust MCP path still functions after change

### OUT

- Tool lifecycle redesign
- MCP contract changes
- Dispatch work
- Capability changes
- 84 hidden tool classification
- Dispatch map retirement

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| AUTH-001 | Swift `/mcp` endpoint no longer responds |
| AUTH-002 | Swift `/exec` endpoint still functions |
| AUTH-003 | Rust MCP authority unaffected |
| AUTH-004 | No client code references Swift `/mcp` directly |
| AUTH-005 | Bridge script topology comments match actual state |

---

## Evidence

| Evidence | Source |
|----------|--------|
| Swift `/mcp` responds to `tools/list` | Direct curl test: `curl -s http://127.0.0.1:3456/mcp -X POST ...` |
| Swift `/exec` responds correctly | Direct curl test: verified in WP-MCP-EXECUTION-BOUNDARY-RECONCILIATION-1 |
| Bridge script declares `/mcp` retired | `mcp-start-and-bridge.sh` line 7: "Swift : execution adapter only (UI + /exec; /mcp endpoint retired)" |
| `registerMCPRoutes` registers both routes | MCPController.swift:929 — `GET /mcp` and `POST /mcp` still active |

---

## Phase 1 Characterization Findings

### F-001: Swift registers three MCP routes

| Route | Method | Purpose | Status |
|-------|--------|---------|--------|
| `GET /mcp` | GET | SSE transport endpoint | **SHOULD BE RETIRED** |
| `POST /mcp` | POST | JSON-RPC message handling | **SHOULD BE RETIRED** |
| `POST /exec` | POST | Execution adapter endpoint | **KEEP** |

All three are registered in `registerMCPRoutes()` (MCPController.swift:929), called from `AppEntry.swift:325`.

### F-002: Two MCP authorities exist simultaneously

| Authority | Port | Tools advertised | Status |
|-----------|------|-----------------|--------|
| Rust MCP Protocol Plane | :3457 | 73 | Intended sole authority |
| Swift MCP | :3456 | 73 | Retired but active |

Both return identical `tools/list` responses. Both accept `tools/call`. This is the dual-authority problem.

### F-003: No production startup path depends on Swift MCP authority

| Path | Depends on Swift `/mcp`? | Notes |
|------|-------------------------|-------|
| `AppEntry.swift:325` | Calls `registerMCPRoutes()` | Registers all three routes — the source of the issue |
| `mcp-start-and-bridge.sh` | No | Bridge talks to Rust :3457, not Swift :3456/mcp |
| Rust `main.rs` | No | Rust connects to Swift `/exec` only |
| OpenWork config | No | `opencode.jsonc` points to bridge script, not Swift directly |
| GUI app (`ContentView.swift`) | No | Loads `http://127.0.0.1:3456` (web UI, not MCP) |

### F-004: Two scripts reference Swift MCP directly

| Script | Reference | Impact |
|--------|-----------|--------|
| `check-wqi-008-invariant.py` | `LIBRARIAN_MCP_ENDPOINT` defaults to `http://127.0.0.1:3456/mcp` | Would break if Swift `/mcp` removed — needs update to `:3457/mcp` |
| `benchmark-mcp-performance.py` | `SWIFT_URL` defaults to `http://localhost:3456/mcp` | Compares Swift vs Rust — intentional, but outdated |

### F-005: /exec dependency graph is clean

| Dependency | Direction | Notes |
|------------|-----------|-------|
| Rust `exec.rs` → Swift `/exec` | Inbound | Only external caller |
| Swift `/exec` → `handleCallTool()` | Internal | Same handler as `/mcp` |
| `handleCallTool()` → handler functions | Internal | 157 tool handlers |
| No internal Swift code calls `/exec` | — | Confirmed: zero matches |

### F-006: Rust health endpoint confirms intended topology

```json
{
  "adapter": {
    "kind": "swift",
    "reachable": true,
    "url": "http://localhost:3456 (exec)"
  },
  "protocol": {
    "implementation": "rust_protocol_plane",
    "name": "mcp-rust-protocol-plane"
  }
}
```

Rust identifies itself as the protocol authority and Swift as the execution adapter. This matches the intended architecture.

---

## Phase 2 Implementation (COMPLETE — requires Swift server restart)

### Changes Made

| File | Change | Lines |
|------|--------|-------|
| `MCPController.swift:927-980` | Removed `GET /mcp` and `POST /mcp` route registrations | ~50 lines removed |
| `check-wqi-008-invariant.py:25` | Default endpoint `:3456/mcp` → `:3457/mcp` | 1 line |
| `benchmark-mcp-performance.py:20` | `SWIFT_URL` `:3456/mcp` → `:3456/exec` | 1 line |

### Pre-Change Verification (current running instance)

| Check | Result |
|-------|--------|
| Rust MCP available | ✅ 73 tools, healthy |
| Swift `/exec` works | ✅ Tool execution OK |
| Swift `/mcp` responds | ⚠️ 73 tools (pre-change — retired after restart) |
| Governance validation | ✅ 19/19 PASS |

### Required: Swift Server Restart

The code changes are in the source tree but the Swift server is running the old binary. A restart is required for the `/mcp` routes to be removed.

Restart command:
```bash
# Stop current Swift server
kill $(lsof -tiTCP:3456 -sTCP:LISTEN) 2>/dev/null

# Restart via bridge script (starts both Rust and Swift)
/Users/andrew/Desktop/CarbideFrame/active/librarian/scripts/mcp-start-and-bridge.sh
```

### Post-Restart Verification (to be run after restart)

| Gate | Requirement | Command |
|------|-------------|---------|
| MCP-BOUNDARY-001 | Rust `/mcp` available | `curl -s http://127.0.0.1:3457/mcp -X POST ...` |
| MCP-BOUNDARY-002 | Swift `/mcp` unavailable | `curl -s http://127.0.0.1:3456/mcp -X POST ...` → connection refused |
| MCP-BOUNDARY-003 | Swift `/exec` works | `curl -s http://127.0.0.1:3456/exec -X POST ...` |
| MCP-BOUNDARY-004 | Tool behavior unchanged | `librarian_search` returns results |
| MCP-BOUNDARY-005 | Governance validation green | `python3 run-governance-validation.py` |
| MCP-BOUNDARY-006 | No second authority | Swift `/mcp` returns connection refused |

---

## Acceptance Gate Results

| Gate | Requirement | Result |
|------|-------------|--------|
| MCP-BOUNDARY-001 | Rust `/mcp` available | ✅ 73 tools |
| MCP-BOUNDARY-002 | Swift `/mcp` unavailable | ✅ Returns `Not Found` |
| MCP-BOUNDARY-003 | Swift `/exec` works | ✅ Tool execution OK |
| MCP-BOUNDARY-004 | Tool behavior unchanged | ✅ `librarian_search` returns results |
| MCP-BOUNDARY-005 | Governance validation green | ✅ 19/19 PASS |
| MCP-BOUNDARY-006 | No second authority surface | ✅ Swift `/mcp` returns `Not Found` |

---

## Post-Repair Topology

```
MCP Client
    ↓
Rust MCP :3457 /mcp        ✅ sole authority
    ↓
Swift :3456 /exec           ✅ execution adapter
    ↓
Librarian Core
```

**Swift `/mcp` retired. Authority boundary restored.**

---

*COMPLETE. All gates pass. Authority topology matches intended architecture.*
