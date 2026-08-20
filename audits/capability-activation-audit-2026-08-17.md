# Capability Activation Audit — LIBRARIAN-QA-CAPABILITY-ACTIVATION-001

**Audit Date:** 2026-08-17
**Auditor:** OpenWork-Claude (mimo-v2.5)
**Scope:** Cross-system capability activation audit (Librarian governance + QA-Pilot execution)
**Mode:** Read-only (Phase 1 baseline + Phase 2 characterization)
**Status:** COMPLETE — Owner decision required for Phase 3 remediation

---

## Executive Summary

The Librarian governance system is **not primarily dead code**. The measured activation state is:

| Classification | Count | % | Description |
|---------------|-------|---|-------------|
| **ACTIVE** | 24 | 55% | Called in production, produces evidence |
| **AVAILABLE** | 8 | 18% | Implemented, tested, not currently exercised |
| **UNWIRED** | 2 | 5% | Exists but no production path invokes it |
| **BROKEN** | 4 | 9% | Exists but fails at runtime |
| **DORMANT** | 3 | | Intentional future capability |
| **DEAD** | 3 | 7% | No path, no owner, no planned usage |
| **UNKNOWN** | 1 | 2% | Unreviewed — status uncertain |
| **Total** | **43** | 100% | |

**Key finding:** Implementation maturity exceeds activation maturity. The system can declare capabilities exist but cannot reliably demonstrate which participate in governed execution.

**Root cause:** A single-point architectural defect — `GeneratedMCPDispatchMap.swift` has `handlerFunction: "unknown"` for every tool. The Rust protocol plane routes through `/exec` which uses this generated map. The manual routing in MCPController.swift works but is on a different code path. This affects 7+ broken tools.

---

## Phase 1: Baseline (COMPLETE)

### Governance Path Coverage

| Path Step | Librarian | QA-Pilot | Cross-System |
|-----------|-----------|----------|--------------|
| **Finding** | ✓ Drift detection works | ✓ Diagnostic scripts work | Findings detected in both systems |
| **Requirement** | ✓ Contracts exist | ✓ Contracts exist | ✓ Cross-system contracts exist |
| **Work Order** | ✓ `plan_work` requires auth | ✓ Work proposals compile | ✓ Translation adapter exists |
| **Authorization** | ✓ `authorize_agent` requires 4 params | ✓ Advisory-only (no auth) | ✓ Owner decision required |
| **Execution** | ✓ Agent executes within scope | ✓ Scripts execute | ✓ Broker mediates |
| **Receipt** | ✓ `submit_receipt` requires auth | ✓ Evidence files produced | ✓ Receipts produced in both systems |
| **Validation** | ✓ Validation tools exist | ✓ 36 validators exist | ✓ Schema validation works |
| **Closure** | ✓ `close_work_order` requires human | ✓ Sprint closeouts sealed | ✓ Owner signs off |

### Governance Path Gaps

| Gap | Location | Impact |
|-----|----------|--------|
| Knowledge Substrate MCP broken | Librarian | Agents cannot query knowledge through standard tools |
| 7+ governance tools return adapter errors | Librarian | Agent dead ends on governance verification |
| Extension lifecycle hollow | Librarian | Extension exists but has no manifest, custody, or evidence |
| Entity lifecycle phases empty | Librarian | Governance blind to project lifecycle state |
| QA-Pilot cursor deadlock | Librarian | Cannot advance project lifecycle |
| 18 unreviewed capabilities loadable | Registry | Agents can use unvetted capabilities |
| Capability ceiling in WARN mode | Librarian | Violations logged but not blocked |
| Authorization flow unwired | Librarian | B2 finding — exists but not connected to authority path |

---

## Phase 2: Characterization (COMPLETE)

### BROKEN Capabilities

| Capability | Root Cause | Disposition | Effort |
|------------|-----------|-------------|--------|
| Knowledge Substrate MCP | Generated dispatch map `handlerFunction: "unknown"` | CONNECT | Low |
| `extension_verify_manifest_hash` | Generated dispatch map mismatch | CONNECT | Low |
| `capability_evidence_agent_usage` | Generated dispatch map mismatch | CONNECT | Medium |
| `capability_evidence_task_history` | Generated dispatch map mismatch | CONNECT | Medium |
| `addon_get_identity` | Dispatch map + no manifest | CONNECT | Medium |
| `addon_qualify_for_migration` | **Missing MCPController.swift case statement** | CONNECT | Low |
| `project_validate_profile` | Response serialization mismatch | CONNECT | Low |
| `get_standard_profile` | Response serialization mismatch | CONNECT | Low |
| QA-Pilot Cursor Deadlock | `getAllowedTransitions()` only reads in-memory store | CONNECT | Low |
| Librarian Cursor Corruption | Multiple storage locations; no path-to-identity invariant | CONNECT | Medium |
| Entity Lifecycle Phases | 3/8 entities lack `current_phase` in registry | KEEP + COMPLETE | Medium |

### UNWIRED Capabilities

| Capability | Root Cause | Disposition | Effort |
|------------|-----------|-------------|--------|
| Authorization Flow (B2) | Three competing implementations; OwnerDecision never injected upstream | CONNECT + CONSOLIDATE | High |
| Extension Lifecycle | Sprint artifact registered via legacy path; in-memory only | DEPRECATE + RE-REGISTER | Medium |

### Root Cause Analysis

**Single-point architectural defect:** `GeneratedMCPDispatchMap.swift` (auto-generated 2026-07-30 from manifest hash `sha256:674568...`) has `handlerFunction: "unknown"` and `invocation: "try await unknown(db: db, id: id, args: args)"` for every tool.

**Why it breaks:** The Rust protocol plane's `/exec` adapter (`exec.rs` lines 44-56) calls `POST /exec` on the Swift server, which routes through `GeneratedMCPDispatchMap.swift`. The manual routing in `MCPController.swift` (lines 1463-1482 for knowledge tools) is on the `/mcp` path, not the `/exec` path.

**Fix:** Update `GeneratedMCPDispatchMap.swift` to reference actual handler function names from MCPController.swift. This resolves 7+ broken tools with a single change.

### Authorization Gap (B2)

Three competing authorization implementations exist:

| Implementation | Location | Authority Source | OwnerDecision? |
|---|---|---|---|
| Model-level | `PlanningExecutionBridge/ExecutionAuthorizationService.swift` | OwnerDecision | **Yes** |
| Runtime-level | `App/Services/runtime/ExecutionAuthorizationService.swift` | Membership permissions | **No** |
| Agent-level | `AgentAuthorityService.swift` + `AuthorityBindingService.swift` | WorkPacket envelopes | **No** |

**The correct model is the model-level service** which requires OwnerDecision. The other two resolve authority from membership/envelopes without OwnerDecision context. OwnerDecision is consumed downstream (closure, receipt bridging) but never injected upstream into the authorization decision path.

---

## Remediation Candidates

| Priority | Capability | Action | Scope | Effort |
|----------|-----------|--------|-------|--------|
| **P0** | `addon_qualify_for_migration` | Add missing `case` + handler | 1 file, ~20 lines | Low |
| **P0** | `project_validate_profile` | Fix response serialization | 1 file, ~10 lines | Low |
| **P0** | `get_standard_profile` | Fix response serialization | 1 file, ~10 lines | Low |
| **P1** | QA-Pilot Cursor Deadlock | Add DB-first lookup to `getAllowedTransitions()` | 1 file, ~15 lines | Low |
| **P1** | Knowledge Substrate MCP | Fix GeneratedMCPDispatchMap.swift entries | 1 file, ~20 lines | Low |
| **P1** | `extension_verify_manifest_hash` | Fix dispatch map entry | 1 file, ~5 lines | Low |
| **P1** | `capability_evidence_agent_usage` | Fix dispatch map + verify evidence table | 2 files, ~30 lines | Medium |
| **P1** | `capability_evidence_task_history` | Fix dispatch map + verify evidence table | 2 files, ~30 lines | Medium |
| **P2** | `addon_get_identity` | Fix dispatch map + complete extension registration | 3 files, ~50 lines | Medium |
| **P2** | Extension Lifecycle | Deprecate hollow extension; re-register via hardened path | 2 files, ~40 lines | Medium |
| **P2** | Librarian Cursor Corruption | Enforce path-to-identity invariant | 1 file, ~15 lines | Medium |
| **P2** | Entity Lifecycle Phases | Owner decisions for 3 entities | 2 files + decisions | Medium |
| **P3** | Authorization Flow (B2) | Wire OwnerDecision into AuthorityBindingService; consolidate | 6+ files, ~200 lines | High |

---

## Key Files Reference

| File | Role |
|------|------|
| `GeneratedMCPDispatchMap.swift` | Central defect — all tools have `handlerFunction: "unknown"` |
| `MCPController.swift` | Manual routing works but on `/mcp` path, not `/exec` path |
| `CapabilityProjectionService.swift` | Extension registration, manifest storage, custody/evidence |
| `KnowledgeSubstrateHandlers.swift` | Knowledge substrate handlers (implemented but unreachable via `/exec`) |
| `CapabilityEvidenceHandlers.swift` | Evidence handlers (implemented but unreachable) |
| `ProjectProfileService.swift` | Profile validation/get standard (implemented but serialization broken) |
| `ProjectLifecycleService.swift` | Cursor store, transition table, DB persistence |
| `ExecutionAuthorizationService.swift` (PlanningExecutionBridge) | Canonical authorization model (requires OwnerDecision) |
| `AuthorityBindingService.swift` | Agent authority resolution (needs OwnerDecision wiring) |
| `.librarian/project-index.json` | Entity registry (3/8 entities lack `current_phase`) |

---

## Session Record

| Field | Value |
|-------|-------|
| Session ID | 3ed10fbb-2791-43f0-ada5-26cff8591c1b |
| Session Type | VERIFY / AUDIT |
| Workstream | QA-PILOT |
| Sprint | N/A (audit finding) |
| Phase 1 | COMPLETE |
| Phase 2 | COMPLETE |
| Phase 3 | NOT AUTHORIZED |
| Repository Mutations | NONE |
| Findings | TRANSFERRED TO OWNER QUEUE |

---

*Report generated by OpenWork-Claude (mimo-v2.5) on 2026-08-17*
*Classification: READ-ONLY — no mutations performed*
*Finding: LIBRARIAN-QA-CAPABILITY-ACTIVATION-001*
