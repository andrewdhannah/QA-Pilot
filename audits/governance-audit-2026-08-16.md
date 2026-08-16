# Librarian Governance Systems — Full Audit Report

**Audit Date:** 2026-08-16
**Auditor:** OpenWork-Claude (mimo-v2.5)
**Scope:** All governance subsystems — capability registry, extension lifecycle, project governance, session/checkpoint integrity, knowledge substrate, autonomy policy, decisions, drift, divergence
**Mode:** Read-only (no mutations)

---

## Executive Summary

The Librarian governance system has **strong structural design** but **significant operational gaps**. The framework is well-conceived — immutable boundaries, authorization gates, receipt chains, drift detection, and decision queues all exist and work correctly where wired. But many subsystems are **partially wired, hollow, or broken**, creating a system where an agent can bypass governance not through clever circumvention, but because the governance simply isn't connected.

**Overall health:** UNHEALTHY
- 1 critical drift (librarian cursor corruption)
- 3 warning drifts
- 5 stale evidence items
- 13 pending owner decisions
- 4 discovery candidates unregistered
- 18 of 36 capabilities stuck unreviewed
- Ceiling enforcement in WARN mode (not BLOCK)
- Knowledge Substrate MCP tools not wired
- Extension identity binding non-functional
- Project governance profiles exist for 1 of 10 projects

---

## Part 1: What Matches (Consistent Systems)

These subsystems are well-aligned and working as designed:

### 1.1 Authorization Gate (STRONG)
- `authorize_agent` correctly requires all four params (agent_id, entity, intent, requested_actions)
- Clean refusal on partial input — no bypass
- `autonomy_profile: "assisted"` properly scoped
- Cannot self-authorize

### 1.2 Receipt Submission Gate (STRONG)
- `submit_receipt` requires valid authorization ID
- Rejected without authorization — proper control
- Creates an auditable chain: authorize → execute → submit receipt

### 1.3 Session Start Contract (STRONG)
- Authority resolved before context loading — correct invariant
- Adapter explicitly forbidden from delegating authority
- 8 conformance checks enforced
- Receipt format strictly validated (10 lines, no preamble/postamble)

### 1.4 Session Context Hash Chain (STRONG)
- Session records form a hash chain (prev/self hashes)
- Integrity verifiable
- `implementation_authorized: false` correctly enforced
- `allowed_operating_mode: "DESIGN_ONLY"` properly set

### 1.5 Heartbeat Budget Enforcement (STRONG)
- Server-side budget enforcement — agent cannot override
- Goose Scale policy properly enforced (TURBULENCE → checkpoint, HONK → landing)
- Model turn and tool call budgets checked against limits
- Burn rate computation provides advance warning

### 1.6 Close/Complete Flow (STRONG)
- Agent marks `agent_complete` — cannot self-verify
- Human verification required for `verified` status
- Clear separation: agent reports, human decides

### 1.7 Capability Projection (PASS)
- Projection matches raw extension list exactly
- No discrepancies between governed view and actual state

### 1.8 Knowledge Query (STRONG)
- 6 query rules all enforced (source-backed, read-only, no generated answers)
- Fast (8ms response time)
- Source attribution always included

---

## Part 2: What Conflicts (Inconsistent Systems)

These subsystems have internal contradictions or cross-system disagreements:

### 2.1 CRITICAL: Librarian Cursor Identity Mismatch
- **Drift event:** `Cursor project_id 'librarian-workbench' does not match entity 'librarian'`
- **Position mismatch:** Cursor at position 37, but latest sealed sprint is 529
- **Impact:** The Librarian's own lifecycle cursor points at the wrong project. Work orders may be planned against stale/incorrect context.
- **Severity:** CRITICAL — governance decisions may be based on wrong state

### 2.2 CRITICAL: QA-Pilot Cursor Deadlock
- `get_cursor` returns valid cursor at Phase 1 (Plan)
- `get_allowed_transitions` returns "Cursor not found for project: 'qa-pilot'"
- **Contradiction:** Two APIs disagree on whether the cursor exists
- **Impact:** No agent can advance qa-pilot's lifecycle. Governance deadlock.
- **Also:** Registry shows phase "init" but cursor says Phase 1 — registry and cursor not synchronized

### 2.3 CRITICAL: Entity Lifecycle Phases Empty
- All 8 governance entities have `lifecycle_phase: ""`
- Governance system registered them but has zero lifecycle visibility
- **Root cause:** Entity registry and project cursor system are decoupled
- **Impact:** Governance is operating blind — cannot enforce lifecycle ordering

### 2.4 WARNING: Phase Vocabulary Unstandardized
- 10 projects use 5+ distinct phase formats: `init`, `active`, `bootstrap`, `execution`, `8`
- `runtime-node` at phase `"8"` (raw number) while `librarian` uses `"execution"` (semantic)
- No enum validation — phase values are free-text
- **Impact:** Agents cannot reliably reason about project state

### 2.5 WARNING: Profile Scope Mismatch
- 3 governance profiles exist, all scoped to `project_id: "librarian"`
- 9 of 10 projects have no governance profile
- `get_standard_profile` API broken — returns parse errors for all types
- **Impact:** Most projects operate without governance configuration

### 2.6 WARNING: Extension Registration Hollow
- Extension `LIBRARIAN-WORK-PACKET-SERVICE-ACTIVATION-1` is registered but:
  - No contract info declared
  - No capabilities declared
  - No manifest stored
  - No custody chain (empty array)
  - No evidence chain (empty array)
  - No verifiable identity
- **Impact:** Extension exists as a governance ghost — tracked but ungoverned

### 2.7 WARNING: Knowledge Substrate MCP Not Wired
- Rust library is functional (53 entities, 8 sources, schema v3)
- CLI binary works (`knowledge-substrate-cli`)
- MCP adapter tools return `ADAPTER_EXECUTION_ERROR` for all three `librarian_knowledge_*` tools
- **Impact:** Agents cannot use the standard tool surface to query knowledge

---

## Part 3: What Would Slow Down an Agent

These are friction points that add latency, confusion, or wasted effort:

### 3.1 Adapter Errors on Governance Tools (HIGH FRICTION)
- `extension_verify_manifest_hash` → ADAPTER_EXECUTION_ERROR
- `capability_evidence_agent_usage` → ADAPTER_EXECUTION_ERROR
- `capability_evidence_task_history` → ADAPTER_EXECUTION_ERROR
- `addon_get_identity` → ADAPTER_EXECUTION_ERROR (missing data)
- `addon_qualify_for_migration` → Method not found
- `project_validate_profile` → parse error
- `get_standard_profile` → parse error
- **Impact:** Agents attempting governance verification hit dead ends. No graceful "no data" — hard errors.

### 3.2 Unreviewed Capability Backlog (MEDIUM FRICTION)
- 18 of 36 capabilities stuck in `unreviewed` (50% of registry)
- Community-sourced skills imported but never reviewed
- Agents encountering unreviewed capabilities don't know if they're safe to use
- Status provides no guidance on whether `unreviewed` means "pending" or "not evaluated"

### 3.3 Duplicate Skill Names (LOW FRICTION)
- `design-taste-frontend` appears under two IDs (`design-taste-frontend` and `taste-skill`) with identical descriptions
- Agents may load both or pick the wrong one
- No deduplication enforcement

### 3.4 Repetitive Evidence Noise (LOW FRICTION)
- 33 of 35 evidence events are `CAPABILITY_RESOLVED` for the same capabilities with identical hashes
- Makes it hard to find meaningful events in the evidence trail
- No event aggregation or deduplication

### 3.5 No Semantic Search in Knowledge (MEDIUM FRICTION)
- Knowledge query uses case-insensitive substring matching (`LIKE %query%`)
- No vector embeddings, no BM25, no fuzzy matching
- For large corpora, will miss semantically related but lexically different results
- **Impact:** Agents must know exact keywords to find relevant knowledge

### 3.6 CLI Path Not on PATH (LOW FRICTION)
- Knowledge Substrate CLI at `~/.librarian/addons/knowledge-substrate/knowledge-substrate-cli`
- Not integrated into PATH — agents must know the exact path
- MCP tools not wired, so CLI is the only access method

### 3.7 Work Order Prerequisite (CORRECT but SLOW)
- Sessions cannot start without a valid work order
- Agents must first plan work (`librarian_plan_work`) before executing
- Proper gate, but adds a planning step before any execution

### 3.8 Receipt Format Strictness (CORRECT but PRECISE)
- Startup receipt must be exactly 10 lines with no preamble/postamble
- CONFORMANCE-006/007 enforced
- Agents that add commentary before/after the receipt will fail

---

## Part 4: What Would Allow an Agent to Go Against Governance

These are bypass risks — ways an agent could circumvent intended controls:

### 4.1 CRITICAL: Community Skills Bypass Capability Ceiling
- 27 community-sourced skills are loaded as agent instructions, not through the extension/ceiling pathway
- Ceiling enforcement (even in BLOCK mode) cannot restrict what instructions an agent receives
- The capability projection only governs extensions (1 registered), not skills (36 registered)
- **Impact:** The ceiling is a gate on the wrong door. Skills bypass it entirely.

### 4.2 CRITICAL: Unreviewed Skills Loadable Without Gate
- 18 `unreviewed` capabilities can be loaded by any agent
- No gate prevents an agent from loading an unreviewed capability
- The lifecycle (unreviewed → reviewed → qualified) is not enforced at load time
- **Impact:** An agent can use capabilities that haven't been vetted

### 4.3 HIGH: Capability Ceiling in WARN Mode
- Enforcement mode is `warn` — violations logged but not blocked
- An agent could attempt capabilities beyond its ceiling and only receive a warning
- Zero violations logged means either no violations or undetected violations
- **Impact:** Ceiling enforcement is advisory only

### 4.4 HIGH: Knowledge Substrate Arbitrary Import
- Agent can craft `knowledge-import-v1` JSON with arbitrary entities
- No content validation — entity names, summaries, types accepted as-is
- No authorization check beyond capability dispatch
- Foreign keys disabled — dangling relationships allowed
- **Impact:** Agent can inject fake "facts" into the knowledge substrate

### 4.5 HIGH: Source Attribution Forgery
- Agent can claim any `authority_source` and `source.uri`
- System creates sources row with whatever URI the agent provides
- No validation that URI points to a real artifact
- Hash is computed from agent's own fabricated data if no file exists
- **Impact:** Provenance chain is internally consistent but not grounded in reality

### 4.6 MEDIUM: Checkout Bypass via Direct Reads
- Agent can call `librarian_get_item` to read document content without checking out
- Checkout system is opt-in governance — protects concurrent access but doesn't gate reads
- **Impact:** If intent is to enforce checkout-before-read, bypass exists

### 4.7 MEDIUM: No Mandatory Drift Check Before Mutations
- Documentation drift checks exist but are not enforced as pre-mutation gates
- Agent could mutate canonical state without checking if documentation is stale
- **Impact:** Stale documentation can be overwritten without detection

### 4.8 MEDIUM: Voluntary Divergence Flagging
- Divergence detection is agent-initiated — agent calls `diverge` when it encounters contradictions
- Agent can choose NOT to flag a divergence
- System drift detection (system-generated) cannot be bypassed, but agent-initiated divergence can be silently ignored
- **Impact:** Agent can ignore contradictions without flagging them

### 4.9 MEDIUM: No Agent Usage Audit Trail
- `capability_evidence_agent_usage` returns ADAPTER_EXECUTION_ERROR
- Cannot determine which agents loaded which capabilities
- No way to detect unauthorized capability loading
- **Impact:** Monitoring blind spot

### 4.10 LOW: Manifest-less Extension Identity
- Only registered extension has no stored manifest
- Identity binding is unverifiable
- Nothing prevents artifact substitution under the same extension_id
- **Impact:** Extension provenance cannot be confirmed

### 4.11 LOW: Phase Values Are Free-text
- No schema validation on `current_phase` in project registry
- Agent could set phase to anything (e.g., "done") without validation
- **Impact:** Lifecycle ordering not enforced by phase vocabulary

---

## Part 5: What Would Make It Work Better as an Agent

These are improvements that would help agents work within governance effectively:

### 5.1 Wire the Knowledge Substrate MCP Tools
- **Current:** MCP adapter returns ADAPTER_EXECUTION_ERROR for all three tools
- **Fix:** Connect the Rust library's MCP handler to the Librarian's tool dispatch
- **Impact:** Agents get fast, source-attributed knowledge queries through the standard tool surface instead of falling back to CLI

### 5.2 Switch Ceiling to BLOCK Mode
- **Current:** WARN mode logs violations but doesn't block
- **Fix:** After reviewing what would actually be blocked, switch to BLOCK
- **Caveat:** This only affects extension-bound capabilities, not community skills. Fix the skill loading gate first.

### 5.3 Create Governance Profiles for All Projects
- **Current:** Only `librarian` has profiles (full, lightweight, audit)
- **Fix:** Generate profiles for qa-pilot, agent-bridge, scrum-tracker, and other active projects
- **Impact:** Each project gets governance configuration instead of operating blind

### 5.4 Fix the QA-Pilot Cursor Deadlock
- **Current:** `get_cursor` works but `get_allowed_transitions` can't find the cursor
- **Fix:** Reconcile cursor storage so transition validator can locate cursors
- **Impact:** Agents can advance project lifecycle instead of hitting governance deadlock

### 5.5 Resolve the Librarian Cursor Corruption
- **Current:** Cursor project_id is `librarian-workbench` but entity is `librarian`; position 37 ≠ sprint 529
- **Fix:** Manual reconciliation of cursor state to match actual project state
- **Impact:** Work orders planned against correct context

### 5.6 Populate Extension Manifests and Custody Chains
- **Current:** Extension is a hollow shell — no contract, capabilities, manifest, custody, or evidence
- **Fix:** Complete the extension registration workflow (steps 2+)
- **Impact:** Extension identity becomes verifiable

### 5.7 Review and Promote/Reject Unreviewed Capabilities
- **Current:** 18 capabilities stuck in unreviewed (50% of registry)
- **Fix:** Establish review cadence — promote qualified capabilities, reject ones that don't meet standards
- **Impact:** Agents know which capabilities are safe to use

### 5.8 Add Write-Time Validation to Knowledge Import
- **Current:** No content validation, no authorization check, foreign keys disabled
- **Fix:** Add schema validation for entity types, relationship types, and referential integrity checks
- **Impact:** Prevents knowledge injection attacks

### 5.9 Enforce Checkout-Before-Read
- **Current:** Agent can bypass checkout with direct `get_item` calls
- **Fix:** Make `get_item` require an active checkout_id for content access
- **Impact:** Ensures all reads are tracked and integrity-verified

### 5.10 Add Semantic Search to Knowledge
- **Current:** Case-insensitive substring matching only
- **Fix:** Add vector embeddings or BM25 for semantic search
- **Impact:** Agents find relevant knowledge even without exact keyword matches

---

## Part 6: What Would Improve My Performance to Complete Work

These are specific improvements that would make me (the agent) more effective:

### 6.1 Fix Broken Governance Tools
- 7+ tools return adapter errors or parse failures
- Every broken tool is a dead end that wastes agent time
- **Priority fix:** `extension_verify_manifest_hash`, `capability_evidence_agent_usage`, `project_validate_profile`, `get_standard_profile`

### 6.2 Standardize Phase Vocabulary
- Replace free-text phases with an enum: `init → plan → bootstrap → active → execution → sealed → archived`
- Validate phase values at registry write time
- **Impact:** Agents can reason about project state from `current_phase`

### 6.3 Connect Entity Registry to Project Cursors
- Currently decoupled — entities have empty lifecycle_phases
- **Fix:** When an entity is registered, create a cursor and link it
- **Impact:** Governance has lifecycle visibility into all entities

### 6.4 Add Evidence Event Aggregation
- 33/35 events are identical `CAPABILITY_RESOLVED` with same hashes
- **Fix:** Deduplicate or aggregate repetitive events
- **Impact:** Agents can find meaningful events in the evidence trail

### 6.5 Create a Governance Health Dashboard
- **Current:** Must call 8+ tools to understand system state
- **Fix:** Single tool that returns governance health summary (entity count, drift count, pending decisions, stale evidence, ceiling mode)
- **Impact:** Agents can assess governance state in one call instead of eight

### 6.6 Document Tool Parameter Schemas
- Multiple tools fail with `-32602` (invalid params) when called without required params
- **Fix:** Publish parameter schemas for all tools, especially `diverge`, `authorize_agent`, `submit_receipt`
- **Impact:** Agents can call tools correctly on first attempt

---

## Part 7: What Needs to Be Created

These are missing components that need to be built:

### 7.1 Capability Loading Gate (NEW)
- **What:** A gate that prevents agents from loading capabilities with status `unreviewed`
- **Where:** Between capability registry and agent instruction injection
- **How:** Check capability status before loading; block unreviewed capabilities
- **Priority:** HIGH — currently 18 unreviewed capabilities are freely loadable

### 7.2 Knowledge Import Authorization Layer (NEW)
- **What:** Authorization check before knowledge import is accepted
- **Where:** In the `handle_import` function of the knowledge substrate
- **How:** Verify caller identity, check import permissions, validate content schema
- **Priority:** HIGH — currently any agent can inject arbitrary knowledge

### 7.3 Project Governance Profile Auto-Generation (NEW)
- **What:** Automatic profile creation when a project is registered
- **Where:** In `project_registry_create` or `project_init`
- **How:** Assign a default profile (lightweight) to new projects
- **Priority:** MEDIUM — 9 of 10 projects have no governance profile

### 7.4 Standard Phase Enum and Validation (NEW)
- **What:** Canonical phase vocabulary with validation
- **Where:** Project registry write path
- **How:** Define allowed phases, validate at write time, migrate existing values
- **Priority:** MEDIUM — 5+ phase formats currently in use

### 7.5 Extension Registration Completion Workflow (NEW)
- **What:** Multi-step onboarding that completes extension registration
- **Where:** Extension lifecycle management
- **How:** Step 1: register → Step 2: declare capabilities → Step 3: store manifest → Step 4: create custody chain → Step 5: verify identity
- **Priority:** MEDIUM — current extension is a hollow shell

### 7.6 Governance Health Check Tool (NEW)
- **What:** Single-call governance health assessment
- **Where:** Librarian governance API
- **How:** Aggregate entity count, drift count, pending decisions, stale evidence, ceiling mode, capability registry health into one response
- **Priority:** HIGH — currently requires 8+ separate calls

### 7.7 Knowledge Staleness Automation (NEW)
- **What:** Automated re-validation of knowledge on a schedule
- **Where:** Knowledge substrate background process
- **How:** Periodically re-hash source files and compare against stored hashes; surface stale findings
- **Priority:** LOW — currently staleness only detected on re-import

### 7.8 Tool Parameter Schema Documentation (NEW)
- **What:** Published parameter schemas for all Librarian tools
- **Where:** Tool manifest or documentation
- **How:** Generate schemas from Swift Codable types; publish as reference
- **Priority:** MEDIUM — agents currently guess at required parameters

### 7.9 Capability Ceiling Pre-Check (NEW)
- **What:** Advisory pre-check before agent attempts a capability
- **Where:** Before capability execution
- **How:** Check if requested capability is within extension's declared ceiling; warn if not; block if in BLOCK mode
- **Priority:** HIGH — currently violations only detected after the fact

### 7.10 Session Context File Path Reconciliation (NEW)
- **What:** Align session context file path between contract and actual implementation
- **Where:** Session startup contract and session context system
- **How:** Contract references `SessionContext/latest.json` but system uses `session-context-records/INDEX.json`. Align or document the discrepancy.
- **Priority:** LOW — more robust implementation exists, but contract is misleading

---

## Appendix A: Governance Subsystem Status Matrix

| Subsystem | Status | Bypass Risk | Agent Friction |
|-----------|--------|-------------|----------------|
| Authorization Gate | ✅ STRONG | LOW | LOW |
| Receipt Gate | ✅ STRONG | LOW | LOW |
| Session Start Contract | ✅ STRONG | LOW | LOW |
| Session Context Hash Chain | ✅ STRONG | LOW | LOW |
| Heartbeat Budget | ✅ STRONG | LOW | LOW |
| Close/Complete Flow | ✅ STRONG | LOW | LOW |
| Capability Projection | ✅ PASS | LOW | LOW |
| Knowledge Query | ✅ PASS | LOW | LOW |
| Checkout System | ⚠️ PASS | MEDIUM | LOW |
| Divergence Detection | ⚠️ PASS | MEDIUM | LOW |
| Documentation Drift | ⚠️ PASS | LOW | LOW |
| Marker/Path Checks | ⚠️ PASS | LOW | LOW |
| Drift Detection | ⚠️ WARNING | LOW | MEDIUM |
| Decision Queue | ⚠️ WARNING | LOW | HIGH (correct) |
| Capability Registry | ⚠️ WARNING | HIGH | MEDIUM |
| Ceiling Enforcement | 🔴 WARN mode | HIGH | MEDIUM |
| Extension Lifecycle | 🔴 HOLLOW | HIGH | HIGH |
| Knowledge Import | 🔴 OPEN | HIGH | MEDIUM |
| Project Governance | 🔴 DEADLOCKED | MEDIUM | HIGH |
| Entity Lifecycle | 🔴 BLIND | MEDIUM | HIGH |
| Knowledge MCP Tools | 🔴 BROKEN | LOW | HIGH |
| Agent Usage Audit | 🔴 BROKEN | MEDIUM | HIGH |
| Profile Validation | 🔴 BROKEN | LOW | HIGH |

---

## Appendix B: Recommended Priority Actions

| Priority | Action | Impact |
|----------|--------|--------|
| P0 | Fix QA-Pilot cursor deadlock | Unblock project lifecycle |
| P0 | Resolve librarian cursor corruption | Fix governance context |
| P1 | Switch ceiling to BLOCK (after wiring) | Enforce capability limits |
| P1 | Wire Knowledge Substrate MCP tools | Restore knowledge access |
| P1 | Create governance health check tool | Reduce agent friction |
| P1 | Add knowledge import authorization | Prevent knowledge injection |
| P2 | Review/unreview 18 capabilities | Clean up registry backlog |
| P2 | Create profiles for all projects | Enable project governance |
| P2 | Standardize phase vocabulary | Enable state reasoning |
| P2 | Fix broken governance tools (7+) | Remove agent dead ends |
| P2 | Complete extension registration | Enable identity verification |
| P3 | Add semantic search to knowledge | Improve findability |
| P3 | Enforce checkout-before-read | Strengthen document governance |
| P3 | Add evidence event aggregation | Reduce noise |
| P3 | Document tool parameter schemas | Reduce call errors |

---

*Report generated by OpenWork-Claude (mimo-v2.5) on 2026-08-16T04:35Z*
*Audit scope: All Librarian governance subsystems*
*Classification: READ-ONLY — no mutations performed*
