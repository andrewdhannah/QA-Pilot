# QA-Pilot Testing Node Contract

**Extracted from:** E2E-1 Librarian Runtime Audit (first qualified implementation case)
**Status:** DRAFT — 🔍 Pending Owner review
**Evidence source:** E2E-1-EXEC-001, E2E-1-RUN3-EXEC-001

---

## 1. Purpose

Define the Testing Node boundary for QA-Pilot. This contract establishes what QA-Pilot owns, what it does not own, and how it interacts with target systems — derived from the E2E-1 implementation evidence, not from speculation.

## 2. The Critical Property

QA-Pilot does not inherit a target system's assertion that the substrate works. It interrogates the target through its own qualified capabilities and records what actually happens.

```
TARGET SYSTEM (e.g. Librarian)
    │
    │ governed substrate
    ▼
┌─────────────────────────────────────────┐
│              QA-PILOT                   │
│                                         │
│  capability registry                    │
│       ↓                                 │
│  test definition                        │
│       ↓                                 │
│  capability resolution                  │
│       ↓                                 │
│  execution                              │
│       ↓                                 │
│  result contract                        │
│       ↓                                 │
│  evidence production                    │
│       ↓                                 │
│  governance projection                  │
└─────────────────────────────────────────┘
    │
    ▼
  governance report (advisory-only)
```

## 3. What QA-Pilot OWNS

| Domain | Ownership | Evidence |
|--------|-----------|----------|
| **Capability Registry** | QA-Pilot defines, qualifies, and maintains its own testing capabilities | `capability-registry/capability-registry.json` |
| **Test Definition** | QA-Pilot defines what to test, in what order, with what pass criteria | `test-library/`, `scripts/e2e-1-*.py` |
| **Capability Resolution** | QA-Pilot resolves which capabilities are needed and whether they are available | `capability-registry/capability-assessment.json` |
| **Execution** | QA-Pilot executes tests through its own qualified capabilities | `scripts/mcp-capability.py`, `scripts/e2e-1-*.py` |
| **Coverage Accounting** | QA-Pilot tracks what was discovered, executable, executed, and reported | `reports/E2E-1-*.json` |
| **Result Contract** | QA-Pilot produces deterministic results (PASS/FAIL/CAPABILITY_MISSING) | `reports/E2E-1-*.json` |
| **Evidence Production** | QA-Pilot produces immutable evidence records following the evidence contract | `evidence/E2E-1/` |
| **Governance Projection** | QA-Pilot produces advisory-only governance reports | `reports/E2E-1-*-governance-report.md` |

## 4. What QA-Pilot does NOT OWN

| Domain | Boundary | Consequence |
|--------|----------|-------------|
| **Target Authority** | QA-Pilot does not have authority over the target system | Cannot fix, modify, or authorize changes to the target |
| **Target Project State** | QA-Pilot does not own the target's project state | Observes state; does not mutate it |
| **Target Governance Decisions** | QA-Pilot does not make governance decisions for the target | Reports findings; Owner decides |
| **Target Mutation** | QA-Pilot does not modify the target system | Read-only by default; write requires explicit authorization |
| **Skill Authority** | QA-Pilot does not own the skills used by the target | Uses its own qualified capabilities, not the target's |

## 5. Capability Resolution Model

Every test requirement flows through capability resolution:

```
Requirement
    ↓
Required capability (e.g. MCP_API_INTERACTION)
    ↓
Qualified capability available?
    ├── no  → CAPABILITY_MISSING
    │         (no conclusion about target permitted)
    └── yes
          ↓
       Execute test
          ↓
       PASS / FAIL / ERROR
```

### 5.1 Error Taxonomy

MCP failures are distinguishable from test failures:

| Error Class | Meaning | Test Result |
|-------------|---------|-------------|
| MCP_INFRA_UNREACHABLE | Service not reachable | CAPABILITY_MISSING or ERROR |
| MCP_INFRA_MALFORMED_RESPONSE | Response parsing failed | ERROR |
| MCP_INFRA_TIMEOUT | Request timed out | ERROR |
| MCP_INFRA_AUTH_FAILURE | Authentication failed | CAPABILITY_MISSING |
| MCP_PROTO_TOOL_NOT_FOUND | Tool does not exist | FAIL (defect in target) |
| MCP_PROTO_INVALID_ARGUMENTS | Invalid arguments | FAIL (defect in test) |
| MCP_APP_TOOL_ERROR | Tool executed but returned error | FAIL (defect in target) |
| MCP_NONE | No error | PASS |

### 5.2 Provenance

Every MCP interaction captures:
- Timestamp
- Tool name and arguments
- Response hash (SHA-256)
- Error class
- Duration
- Target endpoint

## 6. Evidence Contract

### 6.1 Execution Record

Every test execution produces an execution record:

```
AssuranceEvidence {
    evidence_class: "record",
    identity: {
        evidence_id: "E2E-1-EXEC-NNN",
        timestamp: ISO8601,
        source: "qa-pilot"
    },
    observation: {
        observed_state: string,
        artifact_refs: string[],
        measurements: object
    },
    context: {
        environment: string,
        consumer_shape: string,
        execution_context: object
    },
    custody: {
        origin: string,
        chain: string[],
        verification_state: "verified"
    },
    freshness: {
        captured_at: ISO8601,
        confidence_label: "historical"
    }
}
```

### 6.2 Finding Record

When a test fails, a finding record is produced:

```
AssuranceFinding {
    finding_id: string,
    source: string,
    severity: "info" | "advisory" | "violation",
    evidence_refs: string[],
    contract_ref: string,
    classification: "pass" | "advisory" | "fail",
    derived_at: ISO8601,
    derivation_chain: [{ step, evidence }],
    finding: {
        title: string,
        description: string,
        affected_components: string[],
        invariant_violated: string,
        impact: string
    },
    recommendation: {
        description: string,
        proposed_action: string,
        owner_decision_required: boolean
    },
    advisory_only: true,
    no_seal_authority: true
}
```

### 6.3 Capability Gap Record

When a capability is missing, a capability gap record is produced:

```
AssuranceEvidence {
    evidence_class: "record",
    identity: {
        evidence_id: "E2E-1-CAPGAP-NNN",
        ...
    },
    observation: {
        observed_state: "CAPABILITY_MISSING: ...",
        measurements: {
            capability_required: string,
            capability_status: "NOT_AVAILABLE",
            test_result: "CAPABILITY_MISSING"
        }
    },
    ...
}
```

## 7. Governance Projection

QA-Pilot produces advisory-only governance reports. These reports:
- Do not confer authority
- Do not seal or approve
- Are 🔍 Pending Owner review
- QA Pilot ≠ Authority

## 8. Scalability

The testing node model is target-agnostic. Future audits can express:

```
Requirement
    ↓
Required capability
    ↓
Qualified capability available?
    ├── no  → CAPABILITY_MISSING
    └── yes → execute → PASS / FAIL / ERROR
```

This works for:
- Librarian (demonstrated by E2E-1)
- Future testing nodes
- Runtime nodes
- Project services
- MCP servers
- API surfaces
- Distributed/platform implementations

Without embedding knowledge of each target into QA-Pilot's execution engine.

## 9. First Qualified Implementation Case: E2E-1

### 9.1 What E2E-1 Proved

| Metric | Run 1 | Run 3 | Final |
|--------|-------|-------|-------|
| Requirements | 10 | — | 10 |
| Discovered | 10 | — | 10 |
| Executable | 8 | 10 | 10 |
| Executed | 8 | 10 | 10 |
| Reported | 8 | 10 | 10 |
| PASS | 5 | 4 | 7 |
| FAIL | 3 | 0 | 3 |
| CAPABILITY_MISSING | 2 | 0 | 0 |
| Coverage | 50% | — | 100% |
| Status | INCOMPLETE | — | COMPLETE |

### 9.2 What E2E-1 Demonstrated

1. **Independent verification:** QA-Pilot tested the Librarian without inheriting its assertions
2. **Capability resolution:** CAPABILITY_MISSING correctly reported when capabilities were absent
3. **Capability build:** MCP/API capability built, qualified, and used to close the gap
4. **Deterministic results:** All 10 requirements executed and reported deterministically
5. **Evidence production:** Immutable evidence records with SHA-256 integrity
6. **Governance projection:** Advisory-only reports with explicit finding/defect separation

### 9.3 The Three Librarian Defects

These are findings against the Librarian, not incompleteness in QA-Pilot:

| Finding | Defect | Owner Decision |
|---------|--------|----------------|
| E2E-1-FIND-001 | Pointer field name mismatch | Yes |
| E2E-1-FIND-002 | Validator path resolution | No |
| E2E-1-FIND-003 | Incomplete startup metadata | Yes |

## 10. Contract Invariants

| Invariant | Rule | Enforcement |
|-----------|------|-------------|
| TN-1 | QA-Pilot does not inherit target assertions | Architecture |
| TN-2 | Every test flows through capability resolution | Execution |
| TN-3 | CAPABILITY_MISSING produces no conclusion about target | Contract |
| TN-4 | Every execution produces an evidence record | Evidence |
| TN-5 | Every failure produces a finding record | Evidence |
| TN-6 | Governance reports are advisory-only | Contract |
| TN-7 | QA-Pilot does not mutate target systems | Boundary |
| TN-8 | Findings require Owner decision | Governance |

---

## SHA-256 Integrity

```
e229799ad393577c0ea48f9cb4a9f63ced5598cc7a2dd6eee0c0d7cdfba87568
```

---

## Advisory Notice

This contract is advisory-only. It does not confer authority, seal, or approval.
All findings are 🔍 Pending Owner review.
QA Pilot ≠ Authority.
