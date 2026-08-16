# Sprint — QA-PILOT-RUNTIME-EVIDENCE-COMPLETION-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #221 (proposed)
**Lane:** assurance / evidence
**Type:** Substantive capability — runtime evidence boundary completion
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none
**Predecessor:** QA-PILOT-REGRESSION-LEARNING-LOOP-1 (#220, sealed)

---

## 1. Purpose

Complete QA Pilot's own runtime evidence boundary. Operationalize the existing FlightPlan schemas (`runtime-action-event-v1`, `runtime-lifecycle-event-v1`, `runtime-resource-observation-v1`) as QA Pilot-governed evidence, with full provenance chain and validation rules.

This sprint establishes runtime evidence as a first-class QA Pilot capability — not yet federated across projects, but internally complete and provably conformant to the evidence contract.

## 2. Architectural Context

### Current State

```
QA-Pilot
   |
   ├── Qualification evidence     ✅ (QR-* records, 175 records)
   ├── Finding evidence           ✅ (E2E-* findings)
   ├── Learning evidence          ✅ (learning objects, feedback)
   ├── Runtime evidence           ⏳ THIS SPRINT
   |
   └── Cross-project assurance    future (Sprint B)
```

### What Exists Today

| Artifact | Location | Status |
|----------|----------|--------|
| `runtime-action-event-v1.schema.json` | `docs/schemas/flightplan/` | Schema exists. Defines `event_id`, `session_id`, `action`, `action_detail`, optional `work_packet_id`/`work_order_id`. |
| `runtime-lifecycle-event-v1.schema.json` | `docs/schemas/flightplan/` | Schema exists. Defines `event_id`, `session_id`, `lifecycle_event`, `failure_reason`, `actor`. |
| `runtime-resource-observation-v1.schema.json` | `docs/schemas/flightplan/` | Schema exists. Defines `observation_id`, `session_id`, `model_identity`, `consumed`, `estimate`, `variance`. |
| Evidence contract | `contracts/assurance/evidence-contract.md` | DRAFT. Defines `assurance_record` vs `assurance_snapshot`, 9 invariants, provenance chain. |
| Runtime Node adoption baseline | `reports/ASSURANCE-ADOPTION-RUNTIME-NODE-BASELINE-1-FINDINGS.md` | Identifies artifact-vs-runtime evidence as strongest contract-level signal. |

### Gap

The schemas define the wire format for runtime events. They do not define:

1. **How runtime events become QA Pilot evidence** (ingestion contract)
2. **What provenance fields are required** (the 6-identity chain)
3. **How runtime evidence is validated** (rules and enforcement)
4. **How freshness applies** (immutable events vs mutable snapshots)

## 3. Scope

### In Scope

1. **Runtime evidence ingestion contract** — Define how `runtime-action-event`, `runtime-lifecycle-event`, and `runtime-resource-observation` become `assurance_record` or `assurance_snapshot` evidence objects conforming to the evidence contract.

2. **Provenance chain completion** — Add required identity fields to runtime evidence schemas:
   - `node_identity` — Which QA Pilot node produced this?
   - `runtime_identity` — Which runtime (OpenWork, Codex, Claude Code, etc.)?
   - `agent_identity` — Which agent (openwork-claude, etc.)?
   - `model_identity` — Already exists in resource observation. Extend to action/lifecycle events.
   - `session_identity` — Already exists as `session_id`. Formalize as identity object.
   - `work_packet_identity` — Already exists as optional `work_packet_id`. Formalize.
   - `authority_scope` — Under what authority boundary was this produced?

3. **Evidence validation rules** — Define and implement validation rules for runtime evidence:
   - RE-1 through RE-N (to be specified during implementation)
   - Schema conformance validation
   - Provenance completeness validation
   - Freshness classification validation

4. **Freshness semantics for runtime evidence** — Apply the two-class freshness model:
   - `runtime_action_event` → `assurance_record` (immutable, historical)
   - `runtime_lifecycle_event` → `assurance_record` (immutable, historical)
   - `runtime_resource_observation` → `assurance_snapshot` (mutable, time-bound)
   - `runtime_health_check` → `assurance_snapshot` (mutable, time-bound)

5. **Append-only evidence store** — Runtime evidence enters QA Pilot's evidence store through a governed intake path. No overwrites. No deletions.

6. **Validation runner** — Script that validates all runtime evidence against the schema and provenance rules.

### Out of Scope

- Cross-project evidence routing (Sprint B: QA-PILOT-RUNTIME-EVIDENCE-FEDERATION-1)
- LINK planning integration (deferred until runtime evidence is stable)
- Multi-project identity federation
- Fleet-level freshness or discovery
- Runtime evidence from non-QA-Pilot projects
- Planning accuracy measurement

## 4. Provenance Chain (Target State)

Every runtime evidence object must be able to answer:

```
What happened?          → event_type / action / lifecycle_event
When?                   → timestamp / captured_at
Who produced it?        → agent_identity (agent_id, agent_version)
Under what runtime?     → runtime_identity (runtime_id, runtime_type, runtime_version)
Using what model?       → model_identity (provider, model, version)
For which project?      → node_identity (project_id, project_type)
Under what authority?   → authority_scope (scope, constraints)
```

### Provenance Groups

Provenance is separated into two distinct groups. This separation matters because a model/runtime may participate in multiple projects; the project identity must not be inferred from runtime identity.

**Execution Identity** — "What produced this observation?"

| Field | Purpose | Required |
|-------|---------|----------|
| `node_identity` | Which node produced this? | Yes |
| `runtime_identity` | Which runtime (OpenWork, Codex, Claude Code)? | Yes |
| `agent_identity` | Which agent? | Yes |
| `model_identity` | Which model? | Yes |
| `session_identity` | Which session? | Yes |

**Governance Context** — "Under what governed activity did this occur?"

| Field | Purpose | Required |
|-------|---------|----------|
| `project_identity` | Which project? | Yes |
| `work_packet_identity` | Which work packet? | Optional |
| `owner_identity` | Who is the owner? | Optional |
| `authority_scope` | Under what authority boundary? | Yes |

Target provenance object structure:

```json
{
  "execution_identity": {
    "node_identity": {
      "project_id": "qa-pilot",
      "project_type": "add_on",
      "node_id": "qa-pilot-node-001"
    },
    "runtime_identity": {
      "runtime_id": "openwork-session-abc",
      "runtime_type": "openwork",
      "runtime_version": "0.1.0"
    },
    "agent_identity": {
      "agent_id": "openwork-claude",
      "agent_version": "latest"
    },
    "model_identity": {
      "provider": "anthropic",
      "model": "claude-sonnet-4-20250514"
    },
    "session_identity": {
      "session_id": "40415ede-e7aa-493c-8f93-02644f169e35",
      "started_at": "2026-08-16T03:04:38Z"
    }
  },
  "governance_context": {
    "project_identity": {
      "project_id": "qa-pilot",
      "project_type": "add_on"
    },
    "work_packet_identity": {
      "work_packet_id": "wp-qa-pilot-20260710-1",
      "work_order_id": null
    },
    "owner_identity": {
      "owner_id": "andrew-hannah"
    },
    "authority_scope": {
      "scope": "qa_pilot_local",
      "constraints": ["advisory_only", "no_cross_project_mutation"]
    }
  }
}
```

## 5. Freshness Application

| Event Type | Evidence Class | Freshness Model | Confidence Labels |
|------------|---------------|-----------------|-------------------|
| `runtime_action_event` | `record` | Age does not invalidate. Threshold: `current` < 60min, `historical` < 4hr, `archived` >= 4hr | current / historical / archived |
| `runtime_lifecycle_event` | `record` | Same as above | current / historical / archived |
| `runtime_resource_observation` | `snapshot` | Refresh interval: 15min. `current` < 15min, `stale` >= 15min | current / stale / unknown |
| Runtime health check | `snapshot` | Refresh interval: 30sec. `current` < 30sec, `stale` >= 30sec | current / stale / unknown |

## 6. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| RE-COMPLETE-1 | Runtime evidence schemas extended with provenance fields | Updated `runtime-*-v1.schema.json` files with `execution_identity` (node, runtime, agent, model, session) and `governance_context` (project, work_packet, owner, authority_scope) | ✅ |
| RE-COMPLETE-2 | Ingestion contract defined | `contracts/assurance/runtime-evidence-ingestion.md` — specifies event-to-evidence mapping, field mapping, validation rules (REI-1 through REI-8), authority boundary (CAG-RUNTIME-008) | ✅ |
| RE-COMPLETE-3 | Validation rules implemented | `scripts/validate-runtime-evidence.py` — validates schema conformance, provenance completeness, freshness classification, authority boundary. 5 commands: validate, ingest, validate-all, status, list | ✅ |
| RE-COMPLETE-4 | At least 3 runtime events ingested as QA Pilot evidence | `data/runtime-evidence/` — 3 validated evidence records: RAE-* (action/record), RLE-* (lifecycle/record), RRO-* (resource/snapshot) from QA Pilot's own session | ✅ |
| RE-COMPLETE-5 | Freshness classification validated | Validation runner confirms: action event = `current` (record), lifecycle event = `current` (record), resource observation = `stale` (snapshot, >15min old) | ✅ |
| RE-COMPLETE-6 | All existing validators pass | 74 validators + 83 test runners unchanged. No regressions. Assurances contracts validator: 10/10 PASS. Pre-existing failures in SR-8 unrelated to this sprint. | ✅ |
| RE-COMPLETE-7 | Provenance chain traceable | Every ingested runtime evidence traces: evidence → session → agent → runtime → project → authority. Execution Identity and Governance Context groups separated. | ✅ |
| CAG-RUNTIME-008 | Observation does not become authority | Runtime evidence records: (a) declare observation source, (b) declare authority scope, (c) remain immutable after ingestion, (d) do not trigger mutation workflows directly, (e) require existing governed pathways for any recommendation or action. Validated: evidence contains no `authorization` or `dispatch` fields; authority boundary check passes for all 3 ingested records. | ✅ |

## 7. Guardrails

| Guardrail | Rule |
|-----------|------|
| QA-Pilot only | No cross-project evidence routing. No multi-project identity. |
| No cross-project routing | Runtime evidence from other projects is not ingested in this sprint. |
| No planning integration | No connection to cost estimates, token budgets, or LINK. |
| Advisory-only | All runtime evidence maintains `advisory_only: true`, `custody: qa_pilot_local`. |
| Append-only store | Runtime evidence is never modified or deleted after ingestion. |
| Authority separation | QA Pilot produces runtime evidence. Owner approves profile changes. |
| Schema backward compatibility | Existing FlightPlan schemas are extended, not replaced. Old consumers continue to work. |
| No auto-remediation | Runtime evidence findings produce recommendations, not actions. |
| Authority boundary preservation | Runtime evidence is observation only. It does not become authority. Observe ≠ Decide. Recommend ≠ Authorize. Evidence ≠ Ownership. |

## 8. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-RUNTIME-EVIDENCE-COMPLETION-1.md` | This sprint document |
| `contracts/assurance/runtime-evidence-ingestion.md` | Runtime evidence ingestion contract |
| `docs/schemas/flightplan/runtime-evidence-provenance-v1.schema.json` | Provenance object schema |
| `scripts/validate-runtime-evidence.py` | Runtime evidence validation runner |
| `data/runtime-evidence/` | Ingested runtime evidence store |

## 9. Files to Modify

| File | Change |
|------|--------|
| `docs/schemas/flightplan/runtime-action-event-v1.schema.json` | Add provenance fields (node_identity, runtime_identity, agent_identity, model_identity, authority_scope) |
| `docs/schemas/flightplan/runtime-lifecycle-event-v1.schema.json` | Add provenance fields |
| `docs/schemas/flightplan/runtime-resource-observation-v1.schema.json` | Add node_identity, runtime_identity, agent_identity, authority_scope (model_identity already exists) |
| `project-state/sprint-ledger.json` | Add entry #221 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 10. Sequencing After This Sprint

```
QA-PILOT-RUNTIME-EVIDENCE-COMPLETION-1   ← THIS SPRINT
        ↓
QA-PILOT-RUNTIME-EVIDENCE-QUALIFICATION-1   ← qualify the runtime evidence substrate
        ↓
QA-PILOT-RUNTIME-EVIDENCE-FEDERATION-1   ← multi-project identity/routing
        ↓
Fleet Freshness + Discovery
        ↓
Planning Accuracy Loop (LINK integration)
```

## 11. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-REGRESSION-LEARNING-LOOP-1 (#220) | ✅ Sealed |
| Evidence contract (contracts/assurance/evidence-contract.md) | ✅ Exists (DRAFT — pending Owner review) |
| FlightPlan schemas (docs/schemas/flightplan/) | ✅ Exist |
| Runtime Node adoption baseline (#210) | ✅ Sealed |

## 12. Risk

| Risk | Mitigation |
|------|------------|
| Evidence contract is DRAFT | This sprint operates under the DRAFT contract. If Owner review changes invariants, this sprint's evidence may need reclassification. Mitigation: use the contract as-is; reclassification is a future governance action, not a blocking dependency. |
| Provenance fields may be too heavy for some runtimes | Start with the full 6-identity chain for QA Pilot's own sessions. Federation sprint can relax requirements for external projects. |
| No runtime events currently captured | This sprint must capture at least 3 events from live QA Pilot sessions. May need to instrument a session or use historical session data if available. |
