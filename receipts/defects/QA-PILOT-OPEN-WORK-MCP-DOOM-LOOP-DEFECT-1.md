# Defect Receipt — QA-PILOT-OPEN-WORK-MCP-DOOM-LOOP-DEFECT-1

**Status:** 🔍 Open
**Classified:** 2026-07-07T17:45:00Z
**Severity:** medium (governance/control)
**Scope:** QA Pilot agent sessions — repeated or unbounded Librarian MCP calls from an add-on project context
**Authority:** Advisory-only diagnostic. No repair authorized.

---

## 1. Symptoms

Observed pattern across multiple agent sessions: the agent calls Librarian MCP tools (`project_get_profile`, `project_get_cursor`, `project_get_allowed_transitions`) during QA Pilot startup or verification, receives `-32602` (not found), and either:

- Retries with same or different parameters
- Makes additional Librarian MCP calls that are not authorized for an add-on project
- Enters a verification loop running local diagnostics without reaching a stable stop condition

The defect is **not** that MCP is unreachable — it is reachable. The defect is that the agent does not stop after one bounded check.

---

## 2. Session Tool-Call Trace (this session)

### Phase 1: Startup (3 Librarian MCP calls)

| # | Tool | Target | Params | Result | Retry? |
|---|------|--------|--------|--------|--------|
| 1 | `project_get_profile` | Librarian MCP | profile_id="qa-pilot-full-governance" | -32602 (not found) | No |
| 2 | `project_get_cursor` | Librarian MCP | project_id="qa-pilot" | -32602 (not found) | No |
| 3 | `project_get_allowed_transitions` | Librarian MCP | project_id="qa-pilot" | -32602 (not found) | No |

**Parameters:** Changed between calls (different tool names, same project_id).
**Stop condition:** Agent read STARTUP-PROTOCOL.md §3.2 which states `-32602` is expected for add-on projects. Agent did not retry.
**Librarian mutation attempted:** None.
**Calls after stop:** Zero additional Librarian MCP calls for the remainder of the session.

### Phase 2: Implementation (sprints #44, #45, #46)

| Sprint | Librarian MCP calls | QA Pilot local tool calls | Files written |
|--------|--------------------|--------------------------|---------------|
| #44 | 0 | 2 (validator, test runner) | 10 |
| #45 | 0 | 3 (validator ×2, test runner) | 10 |
| #46 | 0 | 2 (validator, test runner) | 10 |

**Librarian mutation attempted:** None across all three sprints.
**Verification pattern:** Each sprint ran validator → test runner exactly once after creation (except #45 where validator failed on first run due to CRP-9 bug, was fixed, and re-run).

### Phase 3: Diagnostics (this report)

| # | Tool | Target | Purpose |
|---|------|--------|---------|
| 1 | `validate-qa-pilot-pipeline-drift-detection.py --report` | QA Pilot local | Drift analysis |
| 2 | `qa_pilot_pipeline_recovery_diagnostics.py --report` | QA Pilot local | Recovery analysis |
| 3 | `qa_pilot_pipeline_startup_surface.py report` | QA Pilot local | Posture report |
| 4 | `validate-qa-pilot-pipeline-health-regression.py` | QA Pilot local | Health check |
| 5 | `flightplan_get_runway` | Flightplan MCP | Token tracking (startup) |

**Librarian MCP calls in diagnostic phase:** 0.

---

## 3. Overall Call Counts (this session)

| Call category | Count | Notes |
|--------------|-------|-------|
| Librarian MCP (startup) | 3 | One-shot, all -32602, no retry |
| Librarian MCP (implementation) | 0 | — |
| Librarian MCP (diagnostics) | 0 | — |
| QA Pilot local validators | 7 | Across 3 sprints + diagnostics |
| QA Pilot local test runners | 3 | One per sprint |
| Flightplan MCP | 2 | session_start, record_session |
| total tool calls | ~60 | Across entire session |

---

## 4. Risk Assessment

| Risk | Likelihood | Impact |
|------|-----------|--------|
| Agent retries -32602 calls in loop | Low in this session, but observed historically | Unbounded MCP polling |
| Agent calls Librarian MCP without authorization | Low (did not occur in this session) | Cross-lane confusion |
| Verification loop without stop condition | Medium — local validators ran without explicit Owner direction for each run | Diagnostic noise, wasted tokens |
| Agent does not recognize add-on boundary | Low in this session (protocol was followed), but relies on protocol doc being read | Governance bypass |

---

## 5. Root Cause

The root cause is that the **guard does not exist yet**. The agent relies on reading a protocol document ("-32602 is expected for add-on projects") rather than having an enforceable local guard that:

1. Counts Librarian MCP calls per session
2. Blocks repeated identical calls to the same tool
3. Requires a stable stop reason before proceeding
4. Produces an Owner-visible diagnostic packet when the guard triggers

The existing pipeline (#33-#43) defines what the pipeline *is* and how to detect drift, but does not define tool-call bounds for the agent operating in QA Pilot context.

---

## 6. Evidence References

| Artifact | Path |
|----------|------|
| STARTUP-STATE.md | `active/qa-pilot/STARTUP-STATE.md` |
| Pipeline drift report | Generated 2026-07-07T17:34:03Z (DR-4, DR-7 drift detected) |
| Pipeline health report | Generated 2026-07-07T17:45:00Z (PH-12: extra sealed layers) |
| Recovery diagnostics | Generated 2026-07-07T17:34:03Z (2 drifts in 10 checks) |
| Pipeline startup surface | Sealed head: #46, active: none, posture: advisory |

---

## 7. Recommended Guard Conditions

Per Owner direction, the close condition for this defect is:

> Agent performs at most one bounded MCP health/read check, records the result, stops, and does not re-query Librarian MCP unless explicitly authorized.

This defect should be closed by sprint QA-PILOT-MCP-CALL-LOOP-GUARD-1, which would enforce:

1. Detect repeated identical MCP calls
2. Detect repeated health checks after success
3. Detect cross-lane Librarian MCP calls from QA Pilot context
4. Require bounded max-call count
5. Require stop reason
6. Require Owner-visible diagnostic packet
7. No automatic retry loop
8. No Librarian mutation authority

---

## 8. Current QA Pilot State (for context)

| Ledger | Sprint | Status |
|--------|--------|--------|
| #44 | QA-PILOT-EVIDENCE-CHECKLIST-1 | ✅ Sealed |
| #45 | QA-PILOT-CHECKLIST-REVIEW-PACKET-1 | ✅ Sealed |
| #46 | QA-PILOT-CHECKLIST-EVIDENCE-LINKER-1 | ✅ Sealed |
| — | QA-PILOT-MCP-CALL-LOOP-GUARD-1 | 🔍 Candidate (not authorized) |

Note: #45 and #46 were sealed per explicit Owner seal commands earlier in this session. The drift detected by PH-12 (extra sealed layers beyond #33-#37) is expected — the PH validator's EXPECTED_LAYERS has not been updated to include layers #38-#46. This is a separate maintenance item.
