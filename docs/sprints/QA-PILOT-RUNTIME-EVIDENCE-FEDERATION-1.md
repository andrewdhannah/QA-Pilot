# Sprint — QA-PILOT-RUNTIME-EVIDENCE-FEDERATION-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #223 (proposed)
**Lane:** assurance / federation
**Type:** Identity and boundary sprint — multi-project evidence federation
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Predecessor:** QA-PILOT-RUNTIME-EVIDENCE-QUALIFICATION-1 (#222, complete)

---

## 1. Purpose

Establish a governed multi-project runtime evidence boundary without creating a centralized authority layer.

This sprint allows QA-Pilot to consume runtime evidence from multiple governed projects while preserving source ownership, evidence provenance, authority separation, and project isolation.

**This is an identity and boundary sprint, not a data aggregation sprint.**
The goal is not "collect everything." The goal is "prove multiple governed sources can participate without collapsing ownership boundaries."

## 2. Architectural Context

### The Boundary Crossed

Before #222, QA-Pilot qualified project artifacts, sprint outcomes, and implementation evidence.
After #222, QA-Pilot qualifies operational evidence streams.
After #223, QA-Pilot qualifies operational evidence streams from **multiple projects**.

This is the first sprint where the system leaves the single-project trust boundary.

### Current State

```
QA-Pilot
   ├── Qualification evidence     ✅
   ├── Finding evidence           ✅
   ├── Learning evidence          ✅
   ├── Runtime evidence (local)   ✅ (#221, #222)
   └── Cross-project runtime      ⏳ THIS SPRINT
```

### The Evidence Flow (Target State)

```
Project Runtime
       │
       ▼
Runtime Evidence Adapter (project-owned)
       │
       △
QA-Pilot Evidence Intake
       │
       △
Qualification (QA-Pilot-owned)
       │
       △
Qualification Result (advisory-only)
```

**Critical invariant:** QA-Pilot evaluates evidence. It does not become the evidence authority.

## 3. New Problems Introduced

### 3.1 Project Identity

Federation requires canonical project identity. QA-Pilot must never infer project identity from runtime identity.

**Current provenance has:**
```json
{
  "governance_context": {
    "project_identity": {
      "project_id": "qa-pilot",
      "project_type": "add_on"
    }
  }
}
```

**Federation requires:**
```json
{
  "project_identity": {
    "project_id": "librarian",
    "project_instance": "librarian-prod-node-001",
    "identity_source": "librarian-registry"
  }
}
```

### 3.2 Evidence Ownership

Federation should preserve:
```
Project Runtime
       │
       ▼
Evidence Produced (project-owned)
       │
       △
QA-Pilot Qualification (evaluator)
       │
       △
Qualification Result (advisory-only)
```

NOT:
```
Project Runtime
       │
       △
QA-Pilot owns evidence (wrong)
```

### 3.3 Adapter Boundary

```
Project
   │
   △
Runtime Evidence Adapter (project-owned)
   │
   △
QA-Pilot Evidence Intake (validation boundary)
   │
   △
Qualification
```

The adapter owns: extraction, translation, project-specific mapping.
QA-Pilot owns: validation, qualification, evidence result.

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| FED-001 | Project identity resolution | 2 projects (QA-Pilot + Librarian) ingested with canonical project_identity. Evidence stored in separate directories. Identity validated against adapter assertion. | ✅ |
| FED-002 | Provenance preservation | Evidence retains origin project, runtime, agent, model, session, authority scope. Verified by comparing source event with ingested evidence. | ✅ |
| FED-003 | Isolation | Evidence directories per-project. Cross-project index is read-only. Qualification runs per-project. | ✅ |
| FED-004 | Adapter contract | Librarian adapter ingests Librarian runtime events without changing QA-Pilot core. Adapter interface defined in federation contract. | ✅ |
| FED-005 | Cross-project qualification | Qualification runs per-project. Results independent. No ownership merging. | ✅ |
| FED-006 | CAG preservation | No dispatch, mutation, or approval authority created. Federation adds ingestion, not authority. | ✅ |
| FED-007 | Discovery readiness | `discovery.json` shows project coverage metadata. Supports future "What projects have runtime assurance coverage?" query. | ✅ |
| FED-008 | Existing validators pass | No regressions from #222 baseline. | ✅ |

## 5. Guardrails

| Guardrail | Rule |
|-----------|------|
| Identity and boundary sprint | Not a data aggregation sprint. Prove the boundary works, don't collect everything. |
| Source ownership preserved | Projects own their evidence. QA-Pilot evaluates, it does not own. |
| No centralized authority | Federation does not create a central evidence authority. |
| No fleet freshness | Deferred to #224. Freshness after federation is substantially more complex. |
| Advisory-only | All qualification results maintain advisory_only=true. |
| No auto-remediation | Qualification findings produce recommendations, not actions. |
| No LINK integration | Discovery readiness only. No planning or cost estimation. |
| Project isolation | Evidence from one project cannot affect another project's qualification. |

## 6. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-RUNTIME-EVIDENCE-FEDERATION-1.md` | This sprint document |
| `contracts/assurance/runtime-evidence-federation.md` | Federation contract (adapter boundary, identity rules, isolation) |
| `docs/schemas/flightplan/project-identity-v1.schema.json` | Canonical project identity schema |
| `scripts/federate-runtime-evidence.py` | Federation engine (adapter registry, multi-project ingestion, isolation) |
| `data/runtime-evidence/projects/` | Per-project evidence directories |

## 7. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #223 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 8. Sequencing After This Sprint

```
QA-PILOT-RUNTIME-EVIDENCE-COMPLETION-1    (#221) ✅
        ↓
QA-PILOT-RUNTIME-EVIDENCE-QUALIFICATION-1 (#222) ✅
        ↓
QA-PILOT-RUNTIME-EVIDENCE-FEDERATION-1    (#223) ← THIS SPRINT
        ↓
Fleet Freshness + Discovery                (#224) future
        ↓
Planning Accuracy Loop                     (#225) future
```

## 9. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-RUNTIME-EVIDENCE-QUALIFICATION-1 (#222) | ✅ Complete |
| Runtime evidence store (`data/runtime-evidence/`) | ✅ 3 records |
| Qualification engine (`scripts/qualify-runtime-evidence.py`) | ✅ Working |
| Provenance schema (`runtime-evidence-provenance-v1.schema.json`) | ✅ Exists |

## 10. What This Sprint Does NOT Do

- Does not collect evidence from all projects
- Does not create a fleet-level freshness model
- Does not implement LINK integration
- Does not create a central evidence authority
- Does not merge ownership boundaries
- Does not implement planning accuracy measurement
- Does not create cross-project regression guards
