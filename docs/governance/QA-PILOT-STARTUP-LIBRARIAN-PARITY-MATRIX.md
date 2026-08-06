# QA Pilot ↔ Librarian Startup Parity Matrix

**Status:** 🔍 Pending (not sealed)
**Authority:** Governance documentation. Parity reference for startup contract alignment.
**Sprint:** QA-PILOT-STARTUP-LIBRARIAN-PARITY-MATRIX-1

---

## 1. Purpose

This document provides a structured comparison of QA Pilot's and The Librarian's startup capabilities, contracts, and governance surfaces. It serves as a reference for:

- Ensuring QA Pilot startup parity with The Librarian as the reference implementation
- Identifying gaps where QA Pilot lacks a capability The Librarian has
- Documenting intentional divergences (by design, not gaps)
- Planning future parity sprints

**Status key:**

| Symbol | Meaning |
|--------|---------|
| ✅ | Full parity — identical capability |
| ⚠️ | Divergent — different but correct by design |
| ❌ | Missing — QA Pilot lacks capability Librarian has (gap) |
| 🔍 | Unknown — needs investigation |

---

## 2. Startup Contract

Comparing `startup-contract.json` fields between both projects.

| # | Dimension | Librarian | QA Pilot | Parity | Notes |
|---|-----------|-----------|----------|--------|-------|
| SC-1 | contract_schema | `startup-contract-v1` | `startup-contract-v1` | ✅ Same | Schema is shared across workspace |
| SC-2 | identity_source | `PROJECT-STARTUP.md` | `PROJECT-IDENTITY.md` | ⚠️ Different | Librarian uses one doc; QA Pilot splits identity into IDENTITY.md + PROFILE.json |
| SC-3 | startup_state_file | `STARTUP-STATE.md` | `STARTUP-STATE.md` | ✅ Same | Both write generated state to same filename at project root |
| SC-4 | startup_checks_script | `scripts/run-startup-checks.sh` | `scripts/run-startup-checks.sh` | ✅ Same | Both have project-local startup check script |
| SC-5 | is_web_app | `true` | `false` | ⚠️ Different | By design — Librarian is a Swift web app; QA Pilot is Python/script |
| SC-6 | verification_surfaces | Swift build + Python validators + shell tests + JSON fixtures + model runtime validators | Python validators + shell tests + JSON fixtures + example fixtures | ⚠️ Different | QA Pilot lacks Swift build surfaces and model runtime validators (by design — not a Swift project) |
| SC-7 | required_files | `Public/index.html`, `Public/app.js`, `Public/styles.css`, `Public/theme.css`, `PROJECT-STARTUP.md`, `SESSION-HANDOFF.md`, `FEATURE-STATUS.md` | `PROJECT-IDENTITY.md`, `PROJECT-PROFILE.json`, `project-state/sprint-ledger.json`, `SESSION-HANDOFF.md`, `FEATURE-STATUS.md` | ⚠️ Different | QA Pilot requires profile + ledger (not web assets); both require SESSION-HANDOFF and FEATURE-STATUS |
| SC-8 | forbidden_terms | Librarian-specific: `sprint-3`, `540`, `.tests-baseline.json`, `Sources/App/`, `run-validation-harness.sh` | QA Pilot-specific: `Public/index.html`, `Public/app.js`, `Public/styles.css`, `Public/theme.css`, `active/librarian/...` | ⚠️ Different | Each project guards its own boundary terms |
| SC-9 | historical_root | `/Users/andrew/Desktop/OpenWork` | `/Users/andrew/Desktop/CarbideFrame` | ⚠️ Different | Different historical anchors per project origin |
| SC-10 | context_sources | `PROJECT-STARTUP.md` (required), `SESSION-HANDOFF.md`, `FEATURE-STATUS.md`, `sprint-ledger.json` (optional) | `PROJECT-IDENTITY.md` (required), `PROJECT-PROFILE.json` (required), `SESSION-HANDOFF.md` (required), `FEATURE-STATUS.md`, `sprint-ledger.json` (optional) | ⚠️ Different | QA Pilot has more required context sources (3 vs 1) |
| SC-11 | mcp_context | Required — profile_tool, cursor_tool, transitions_tool, context_tool declared | Not declared in contract | ❌ Gap | QA Pilot startup contract does not declare mcp_context block; relies on generic protocol fallback |
| SC-12 | operational_state transitional_source | `project-state/sprint-ledger.json` | Not declared | ❌ Gap | QA Pilot startup contract does not declare operational_state block |
| SC-13 | fallback_docs | `PROJECT-STARTUP.md`, `STARTUP-DEGRADED-MODE.md`, `STARTUP-REFERENCE.md` | Not declared | ❌ Gap | QA Pilot startup contract does not declare fallback_docs |
| SC-14 | project_name | `The Librarian` | `QA Pilot` | ⚠️ Different | Different names (expected) |

---

## 3. Governance Profile

Comparing governance profiles (`project_get_profile` output for both projects).

| # | Module | Librarian (librarian-full-governance) | QA Pilot (qa-pilot-full-governance) | Parity | Notes |
|---|--------|--------------------------------------|--------------------------------------|--------|-------|
| GP-1 | activity_receipts | `required` | `required` | ✅ Same | Core module |
| GP-2 | continuation_gate | `strict` | `strict` | ✅ Same | |
| GP-3 | design_direction | `enabled` | `enabled` | ✅ Same | |
| GP-4 | document_custody | `required` | `required` | ✅ Same | Core module |
| GP-5 | lifecycle_cursor | `strict` | `strict` | ✅ Same | |
| GP-6 | model_qualification_routing | `enabled` | `enabled` | ✅ Same | |
| GP-7 | multi_agent_coordination | `enabled` | `enabled` | ✅ Same | |
| GP-8 | owner_review_seal | `strict` | `strict` | ✅ Same | |
| GP-9 | planning_harness | `enabled` | `enabled` | ✅ Same | |
| GP-10 | provenance | `required` | `required` | ✅ Same | Core module |
| GP-11 | recall_packets | `enabled` | `enabled` | ✅ Same | |
| GP-12 | source_tracking | `required` | `required` | ✅ Same | Core module |
| GP-13 | sprint_work_packets | `strict` | `strict` | ✅ Same | |
| GP-14 | tracker_dashboard | `enabled` | `enabled` | ✅ Same | |
| GP-15 | validation_gates | `strict` | `strict` | ✅ Same | |
| GP-16 | work_lanes | `enabled` | `enabled` | ✅ Same | |
| GP-17 | profile_type | `full` | `full` | ✅ Same | |
| GP-18 | profile_version | `1.0.0` | `1.0.0` | ✅ Same | |

**Full parity on governance profile modules.** Both projects operate under identical governance profile configurations.

---

## 4. Lifecycle Cursor

| # | Dimension | Librarian | QA Pilot | Parity | Notes |
|---|-----------|-----------|----------|--------|-------|
| LC-1 | Current phase | Execution (phase 3+) | Plan (phase 1) | ⚠️ Different | Different maturity levels |
| LC-2 | Allowed transitions | Phase-dependent | 1 → 2 (planning complete) | ⚠️ Different | Different phase position |
| LC-3 | Cycle | N/A | 1 | ⚠️ Different | QA Pilot is in first cycle |
| LC-4 | Entered from | Unknown | `project_init` | 🔍 Unknown | Both have standard lifecycle |

Both projects use the same lifecycle cursor module (`lifecycle_cursor: strict`). Differences are expected due to different maturity levels.

---

## 5. MCP Context Acquisition

| # | Dimension | Librarian | QA Pilot | Parity | Notes |
|---|-----------|-----------|----------|--------|-------|
| MC-1 | profile_tool | `project_get_profile(librarian-full-governance)` | `project_get_profile(qa-pilot-full-governance)` | ✅ Same | Same tool, different profile ID |
| MC-2 | cursor_tool | `project_get_cursor(librarian)` | `project_get_cursor(qa-pilot)` | ✅ Same | Same tool, different project ID |
| MC-3 | transitions_tool | `project_get_allowed_transitions(librarian)` | `project_get_allowed_transitions(qa-pilot)` | ✅ Same | Same tool, different project ID |
| MC-4 | context_tool | `project_assemble_context(librarian, ...)` | `project_assemble_context(qa-pilot, ...)` | ✅ Same | Same tool, different project data |
| MC-5 | Generic protocol fallback | Via STARTUP-PROTOCOL.md §3.2 | Via STARTUP-PROTOCOL.md §3.2 | ✅ Same | Both share the generic protocol path |

**Full parity on MCP context acquisition.** Both projects use identical MCP tools through the generic protocol.

---

## 6. Project Startup Doc

Comparing `PROJECT-STARTUP.md` structure.

| # | Dimension | Librarian | QA Pilot | Parity | Notes |
|---|-----------|-----------|----------|--------|-------|
| PD-1 | Project identity | Inline table in PROJECT-STARTUP.md | Separate PROJECT-IDENTITY.md + PROFILE.json | ⚠️ Different | QA Pilot separates into dedicated identity/profile files |
| PD-2 | Startup protocol reference | References STARTUP-PROTOCOL.md | References AGENT-START.md §13 | ⚠️ Different | Same protocol, different reference style |
| PD-3 | MCP context acquisition | Explicit step-by-step with tool calls | References generic protocol | ⚠️ Different | QA Pilot relies on generic protocol; Librarian documents it explicitly |
| PD-4 | Path rules | Read/write + read-only + no-edit | Read/write + read-only + no-edit | ✅ Same | Same path structure |
| PD-5 | Allowed mutation paths | Not in PROJECT-STARTUP | Explicit table in PROJECT-STARTUP | ⚠️ Different | QA Pilot documents mutation paths; Librarian does not duplicate |
| PD-6 | Agent authority | `bounded` | `advisory-only` | ⚠️ Different | QA Pilot is advisory-only (add-on project) |
| PD-7 | Work identity binding | Explicit `start <WORK-ID>` rules | Not documented | ❌ Gap | QA Pilot PROJECT-STARTUP.md lacks work identity binding rules |

---

## 7. Startup Checks

| # | Dimension | Librarian | QA Pilot | Parity | Notes |
|---|-----------|-----------|----------|--------|-------|
| CH-1 | Startup checks script | `scripts/run-startup-checks.sh` | `scripts/run-startup-checks.sh` | ✅ Same | Same filename |
| CH-2 | MCP health check | `scripts/check-mcp-health.sh` | Fallback to Librarian's check | ❌ Gap | QA Pilot has no dedicated MCP health check script |
| CH-3 | Working tree check | ✅ Git status check | ✅ Git status check | ✅ Same | |
| CH-4 | Required files check | ✅ | ✅ | ✅ Same | |
| CH-5 | Validator count | ✅ | ✅ | ✅ Same | |
| CH-6 | Test runner count | ✅ | ✅ | ✅ Same | |
| CH-7 | STARTUP-STATE.md generation | ✅ | ✅ | ✅ Same | Same filename, same format |
| CH-8 | Git branch detection | ✅ | ✅ | ✅ Same | |
| CH-9 | Last commit detection | ✅ | ✅ | ✅ Same | |

**Nearly full parity on startup checks.** Only gap: CH-2 — QA Pilot lacks its own `scripts/check-mcp-health.sh` script and falls back to the Librarian's.

---

## 8. Output Mode & Report Format

| # | Dimension | Librarian | QA Pilot | Parity | Notes |
|---|-----------|-----------|----------|--------|-------|
| OR-1 | Output contract | STARTUP-OUTPUT-CONTRACT.md | STARTUP-OUTPUT-CONTRACT.md | ✅ Same | Shared contract |
| OR-2 | Strict mode | 10-line fenced report | 10-line fenced report | ✅ Same | Shared format |
| OR-3 | Verbose mode | Step narration + report + ≤4-line summary | Step narration + report + ≤4-line summary | ✅ Same | Shared format |
| OR-4 | Debug mode | Diagnostics + report | Diagnostics + report | ✅ Same | Shared format |
| OR-5 | Repair mode | Diagnostics + report + blocker guidance | Diagnostics + report + blocker guidance | ✅ Same | Shared format |
| OR-6 | Validation script | `scripts/validate-startup-report.py` | `scripts/validate-startup-report.py` | ✅ Same | Shared validator |

**Full parity.** Both projects use the same shared STARTUP-OUTPUT-CONTRACT.md.

---

## 9. Session Identity Derivation

| # | Dimension | Librarian | QA Pilot | Parity | Notes |
|---|-----------|-----------|----------|--------|-------|
| SI-1 | Start with work ID | Renames session to sprint ID | Same via generic protocol | ✅ Same | |
| SI-2 | Start with project only | Renames to `project-name (idle)` | Same via generic protocol | ✅ Same | |
| SI-3 | No project selected | `startup — no project` | `startup — no project` | ✅ Same | |
| SI-4 | Degraded mode | `project-name (degraded)` | `project-name (degraded)` | ✅ Same | |

**Full parity.** Both use the same SESSION-IDENTITY-DERIVATION.md rules.

---

## 10. Degraded Mode & Fallback

| # | Dimension | Librarian | QA Pilot | Parity | Notes |
|---|-----------|-----------|----------|--------|-------|
| DM-1 | Degraded mode doc | STARTUP-DEGRADED-MODE.md | STARTUP-DEGRADED-MODE.md | ✅ Same | Shared doc |
| DM-2 | Fallback docs in contract | 3 docs declared | Not declared | ❌ Gap | QA Pilot contract lacks fallback_docs field |
| DM-3 | MCP unreachable fallback | Via STARTUP-DEGRADED-MODE.md | Via STARTUP-DEGRADED-MODE.md | ✅ Same | Shared protocol |

---

## 11. Cross-Project Boundaries

| # | Dimension | Librarian | QA Pilot | Parity | Notes |
|---|-----------|-----------|----------|--------|-------|
| XB-1 | Forbidden cross-project paths | N/A (root project) | 10 forbidden path patterns | ⚠️ Different | QA Pilot has explicit cross-project constraints; Librarian is the root project |
| XB-2 | Allowed mutation paths | All (root project) | 9 path patterns + 4 file overrides | ⚠️ Different | QA Pilot is constrained; Librarian has full access |
| XB-3 | Sandbox boundary | N/A | `harness_governed` | ⚠️ Different | QA Pilot is explicitly sandboxed |

---

## 12. Gap Summary

| # | Gap | Description | Priority | Action |
|----|------|-------------|----------|--------|
| G-1 | SC-11: mcp_context | QA Pilot startup contract does not declare mcp_context block | Medium | Add mcp_context block to QA Pilot startup-contract.json |
| G-2 | SC-12: operational_state | QA Pilot contract lacks operational_state transitional source declaration | Medium | Add operational_state block to QA Pilot startup-contract.json |
| G-3 | SC-13: fallback_docs | QA Pilot contract lacks fallback_docs field | Low | Add fallback_docs to QA Pilot startup-contract.json |
| G-4 | PD-7: work identity binding | QA Pilot PROJECT-STARTUP.md lacks `start <WORK-ID>` binding rules | Medium | Add work identity binding section to QA Pilot PROJECT-STARTUP.md |
| G-5 | CH-2: MCP health check | QA Pilot lacks own `scripts/check-mcp-health.sh` | Low | Create QA Pilot-local MCP health check script |
| G-6 | DM-2: fallback docs in contract | QA Pilot contract lacks fallback_docs | Low | Resolved by G-3 |

---

## 13. Intentional Divergences

These differences are by design and do not represent gaps:

| # | Dimension | Rationale |
|---|-----------|-----------|
| D-1 | SC-5: is_web_app = false | QA Pilot is a Python/script project, not a Swift web app |
| D-2 | SC-6: No Swift build surfaces | QA Pilot has no Swift code |
| D-3 | SC-2: split identity sources | QA Pilot deliberately separates identity (IDENTITY.md) from profile (PROFILE.json) for modularity |
| D-4 | GP: same profile modules | Both projects correctly share the same governance profile type (`full`) — this is expected |
| D-5 | XB-1/2/3: sandbox constraints | QA Pilot as add-on project is intentionally constrained; Librarian as root project is not |
| D-6 | PD-6: advisory-only authority | QA Pilot as add-on has restricted authority; Librarian has bounded authority |
| D-7 | SC-7: different required files | Each project requires its own specific file set |
| D-8 | LC-1/2: different phase | Different maturity levels — QA Pilot is in Plan phase (1), Librarian is further along |

---

## 14. Invariants

- PM-1: Every startup parity dimension must have a status marker (✅, ⚠️, ❌, 🔍).
- PM-2: Every gap (❌) must have a priority and proposed action.
- PM-3: Every divergence (⚠️) must have a documented rationale.
- PM-4: Parity matrix must be re-evaluated when either project's startup contract changes.
- PM-5: Gaps are tracked as separate sprints — this matrix does not implement gap fixes.
