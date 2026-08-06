# QA Pilot Epic Scenario Suite — QA-PILOT-EPIC-SCENARIO-SUITES

**Sprint:** QA-PILOT-EPIC-SCENARIO-SUITES
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** Advisory only. Read-only. No cross-project mutation.

---

## 1. Purpose

Transform QA-Pilot from a governed evidence consumer into a system-level composition verifier. Create reusable epic validation scenarios that prove collections of completed work orders compose into functioning capabilities.

This is NOT a test runner. It is a **composition verifier** that compares expected vs observed evidence states and produces structured training/testing/learning artifacts.

## 2. Architecture

```
SDK (EvidenceProvider)
    │
    ├── getEvidenceSnapshot()
    ├── getFindings()
    ├── getCompositionGraph()
    ├── getProvenanceChain()
    └── getValidationArtifacts()
    │
    ▼
Epic Scenario Suite
    │
    ├── Scenario Definition
    │   ├── input evidence package
    │   ├── expected composition
    │   ├── expected findings
    │   ├── pass/fail criteria
    │   └── learning context
    │
    ├── Evaluation Engine
    │   ├── compare expected vs observed
    │   ├── classify gaps
    │   └── generate learning artifact
    │
    └── Validation Result
        ├── check-level pass/fail
        ├── observed state capture
        └── teachable moment narrative
```

## 3. Scenario Types

| Type | Purpose | First Scenario |
|------|---------|----------------|
| `complete_epic` | Verify all OE layers compose correctly | EP-EP-001 |
| `missing_artifact` | Detect and classify absent evidence | EP-MISS-001 |
| `conflicting_sources` | Validate authority resolution | EP-CONF-001 |
| `broken_provenance` | Identify broken lineage links | EP-PROV-001 |
| `mutation_boundary` | Confirm boundary enforcement | EP-BOUND-001 |

## 4. First Validation Target: Evidence Plane Epic

The smallest complete system where QA-Pilot proves its purpose:

```
OE-001 → OE-002 → OE-003 → OE-004 → OE-005 → OE-006 → Epic Validation Contract
```

Each layer exercises a distinct SDK capability:
- OE-001: Evidence snapshot
- OE-002: Diagnostic findings
- OE-003: Composition graph
- OE-004: Authority resolution (conflict detection)
- OE-005/OE-006: Provenance chain

## 5. Scope (In scope)

1. 5 scenario definitions targeting the Evidence Plane epic
2. Evaluation engine consuming SDK data
3. Learning artifact generation (teachable moments)
4. Reusable scenario pattern for future epics

## 6. Scope (Out of scope / Non-goals)

- ❌ No mutation APIs — QA-Pilot does not modify evidence
- ❌ No authority arbitration — QA-Pilot does not resolve conflicts
- ❌ No substitute receipts — validation results are advisory
- ❌ No Librarian state modification

## 7. Reusable Pattern

Each epic validation scenario produces:

```
Epic Validation Scenario
    ├── Input evidence package       (from SDK queries)
    ├── Expected composition         (scenario definition)
    ├── Expected findings            (scenario definition)
    ├── Expected pass/fail criteria  (scenario definition)
    └── Validation artifact          (structured result + learning)

That becomes the template for future epics:
provider lifecycle, MCP, CI, platform releases
```

## 8. Authority Boundaries

- **Librarian** owns evidence, provenance, and governance state
- **SDK** provides governed read-only access
- **QA-Pilot** validates composition, generates learning artifacts
- **QA-Pilot does not**: resolve findings, rewrite evidence, change authority records, modify Librarian state, create substitute receipts

## 9. Scenario Lifecycle

```
Expected Definition                    SDK Data
      │                                   │
      └───────┬───────────────────────────┘
              │
              ▼
      Comparison Engine
              │
              ├── PASS  →  Learning artifact: "this works correctly"
              └── REVIEW → Learning artifact: "these gaps need attention"
              │
              ▼
         Validation Result
         (advisory, read-only)
```

## 10. Files

| File | Description |
|------|-------------|
| `scripts/qa_pilot_epic_scenario_suite.py` | Scenario engine — evaluate, run, format |
| `scripts/validate-qa-pilot-epic-scenario-suite.py` | Validator for scenario fixtures |
| `scripts/test-qa-pilot-epic-scenario-suite.sh` | Test runner |
| `docs/schemas/qa-pilot-epic-scenario-suite.schema.json` | Schema for scenario results |
| `docs/examples/qa-pilot-epic-scenario-suite/` | Valid and invalid fixtures |
| `docs/governance/QA-PILOT-EPIC-SCENARIO-SUITES.md` | This governance document |

## 11. Dependencies

- **Requires:** QA-PILOT-SDK-INTEGRATION-1 (EvidenceProvider SDK)
- **Requires:** OA-001 through OE-006 evidence plane outputs
- **Consumes:** 5 SDK query methods
- **Provides:** Reusable epic validation pattern + first 5 scenarios
