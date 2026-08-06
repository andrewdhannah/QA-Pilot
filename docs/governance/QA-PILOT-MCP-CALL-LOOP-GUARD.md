# QA-PILOT-MCP-CALL-LOOP-GUARD.md — QA Pilot MCP Call Loop Guard

**Status:** ✅ Sealed (sprint #47)
**Authority:** Advisory-only. No approval, seal, execution, write, or sprint-start authority conferred.
**Custody:** QA Pilot-local only. No Librarian mutation permitted.

---

## 1. Purpose

Define an enforceable, Owner-reviewable guard against MCP doom-loop patterns in QA Pilot agent sessions. The guard captures an agent session's MCP tool-call trace and validates that:

1. No repeated identical MCP calls occur (same tool, same params, after a definitive result).
2. No repeated health checks occur after a successful or expected terminal result.
3. No cross-lane Librarian MCP calls from QA Pilot context without explicit authorization.
4. Bounded max-call count is respected.
5. A stop reason is present for each sequence of calls.
6. Owner-visible diagnostic packet is produced when guard conditions are violated.
7. No automatic retry loops — calls stop after definitive results (e.g. `-32602` expected for add-on projects).
8. No Librarian mutation authority is claimed or exercised.

This guard closes defect `QA-PILOT-OPEN-WORK-MCP-DOOM-LOOP-DEFECT-1`.

---

## 2. Definitions

| Term | Definition |
|------|-----------|
| **MCP Call** | A single invocation of an MCP tool (e.g. `project_get_profile`, `project_get_cursor`) from the agent to the MCP server. |
| **Identical Call** | The same MCP tool called with the same parameters as a previous call. |
| **Doom Loop** | Repeated, unbounded MCP calls where the agent does not stop after a definitive or expected terminal result. |
| **Cross-Lane Call** | An MCP call to a Librarian governance tool from a QA Pilot (add-on) agent session without explicit authorization. |
| **Stop Reason** | A documented justification for why the agent stopped calling MCP tools at that point (e.g. protocol rule, expected error, explicit Owner direction). |
| **Guard Packet** | A QA Pilot-local diagnostic packet (`MG-*`) containing the MCP call trace and aggregate guard evaluation. |
| **Terminal Result** | A result that definitively ends a call sequence: `success`, `not_found` (`-32602`), or `unreachable`. |

---

## 3. Schema

The MCP call loop guard schema is defined at `docs/schemas/qa-pilot-mcp-call-loop-guard.schema.json` (Draft 2020-12).

### 3.1 Required Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `guard_id` | string (pattern `^MG-[A-Z0-9-]+$`) | Unique guard diagnostic identifier |
| `session_id` | string (min 1) | The agent session ID being evaluated |
| `title` | string (min 1) | Human-readable title |
| `description` | string (min 10) | Context for this guard evaluation |
| `mcp_calls` | array (min 1) | Chronological trace of MCP tool calls |
| `aggregate` | object | Guard evaluation results |
| `advisory_only` | boolean (`true`) | Always advisory |
| `custody` | string (`qa-pilot-local`) | Local custody only |
| `librarian_impact` | string (`none`) | No Librarian mutation |
| `not_seal_authority` | string (min 20 chars) | Seal-authority disclaimer |
| `not_librarian_mutation_authority` | string (min 20 chars) | Librarian-mutation disclaimer |
| `created_at` | string (date-time) | ISO 8601 creation timestamp |

### 3.2 MCP Call Entry Fields

| Field | Type | Description |
|-------|------|-------------|
| `call_number` | integer (>= 1) | Sequential call number |
| `tool` | string | MCP tool name |
| `params_summary` | string (optional) | Summary of parameters |
| `result` | enum | `success`, `not_found`, `unreachable`, `other_error` |
| `result_detail` | string (optional) | Full result or error message |
| `phase` | enum | `startup`, `implementation`, `verification`, `diagnostic`, `seal` |
| `retry` | boolean | Whether this was a retry after definitive result |
| `stop_reason` | string (optional) | Why the agent stopped after this result |

### 3.3 Aggregate Fields

| Field | Type | Description |
|-------|------|-------------|
| `total_calls` | integer | Total MCP calls in session |
| `unique_tools` | integer | Distinct tools called |
| `repeated_identical_calls` | integer | Count of repeated identical calls |
| `repeated_health_checks` | integer | Count of repeated health checks after success |
| `stop_reason_present` | boolean | Whether a stop reason was documented |
| `cross_lane_detected` | boolean | Whether cross-lane calls were found |
| `bounded` | boolean | Whether total calls were within bounds |
| `no_auto_retry_loop` | boolean | Whether no auto-retry loop was detected |
| `terminal_result_recognized` | boolean | Whether terminal results were recognized |

---

## 4. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| MG-1 | Guard packet must conform to qa-pilot-mcp-call-loop-guard.schema.json | Schema |
| MG-2 | advisory_only must be true | Schema const |
| MG-3 | custody must be qa-pilot-local | Schema pattern |
| MG-4 | librarian_impact must be none | Schema const |
| MG-5 | not_seal_authority must be present and >= 20 chars | Schema |
| MG-6 | not_librarian_mutation_authority must be present and >= 20 chars | Schema |
| MG-7 | At least one MCP call recorded | Schema minItems |
| MG-8 | No repeated identical MCP calls after definitive result | Validator |
| MG-9 | No repeated health checks after success | Validator |
| MG-10 | No cross-lane Librarian MCP calls without authorization | Validator |
| MG-11 | Bounded max-call count enforced (max 10 distinct MCP calls) | Validator |
| MG-12 | Stop reason must be present for each tool sequence | Validator |
| MG-13 | No auto-retry loop: calls stop after terminal result | Validator |
| MG-14 | No authority claims in descriptions or detail fields | Validator |
| MG-15 | No Librarian mutation authority referenced | Validator |

---

## 5. Pipeline References

The MCP call loop guard evaluates sessions that interact with these sealed sprint layers:

| # | Layer | Sprint |
|---|-------|--------|
| 33 | Evidence Intake | QA-PILOT-MCP-EVIDENCE-INTAKE-1 |
| 34 | Test Composition | QA-PILOT-TEST-COMPOSITION-1 |
| 35 | Result Export | QA-PILOT-RESULT-PACKET-EXPORT-1 |
| 36 | Epic Regression | QA-PILOT-EPIC-REGRESSION-BUILDER-1 |
| 37 | Startup Surface | QA-PILOT-EPIC-REGRESSION-STARTUP-SURFACE-1 |
| 38 | Health Regression | QA-PILOT-PIPELINE-HEALTH-REGRESSION-1 |
| 39 | Drift Detection | QA-PILOT-PIPELINE-DRIFT-DETECTION-1 |
| 40 | Recovery Diagnostics | QA-PILOT-PIPELINE-RECOVERY-DIAGNOSTICS-1 |
| 41 | Owner Review Packet | QA-PILOT-PIPELINE-OWNER-REVIEW-PACKET-1 |
| 42 | ODR | QA-PILOT-OWNER-REVIEW-DECISION-RECEIPT-1 |
| 43 | ODR Startup Surface | QA-PILOT-OWNER-DECISION-RECEIPT-STARTUP-SURFACE-1 |
| 44 | Evidence Checklist | QA-PILOT-EVIDENCE-CHECKLIST-1 |
| 45 | Checklist Review Packet | QA-PILOT-CHECKLIST-REVIEW-PACKET-1 |
| 46 | Evidence Linker | QA-PILOT-CHECKLIST-EVIDENCE-LINKER-1 |

---

## 6. Authority

- **Advisory-only.** Guard packets are advisory diagnostic artifacts. They do not approve, seal, execute, write, or authorize sprint starts.
- **QA Pilot-local custody.** All guard data resides within QA Pilot-local paths only.
- **No Librarian mutation.** Guard validation rejects any reference to Librarian mutation authority.
- **No execution or remediation.** Guard packets report status only — they do not block, throttle, or modify MCP calls.
- **No sealing automation.** Guard packets do not trigger or automate sealing.
- **Existing boundaries preserved.** The #33-#46 advisory-only custody boundaries are unchanged.

---

## 7. Invariants

| # | Invariant | Enforcement |
|---|-----------|-------------|
| I-1 | All valid guard packets must pass schema validation | Schema + validator |
| I-2 | All invalid fixtures must fail validation | Validator |
| I-3 | advisory_only=true invariant is unchangeable | Schema const |
| I-4 | custody=qa-pilot-local invariant is unchangeable | Schema pattern |
| I-5 | librarian_impact=none invariant is unchangeable | Schema const |
| I-6 | MG-* ID pattern is required | Schema pattern |
| I-7 | MCP calls array must have at least 1 entry | Schema minItems |
| I-8 | Aggregate counts must be internally consistent | Validator |
| I-9 | No guard may claim approval/seal/execute/write authority | Validator |
| I-10 | All existing #33-#46 validators and test runners remain green | Regression |
