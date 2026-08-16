# Ash/GPT Review — QA-Pilot Session (2026-08-11)

**Reviewers:** Ash (Claude), GPT
**Subject:** QA-Pilot Testing Node Qualification & Historical Assurance session
**Verdict:** Strong session. Architecture is sound, discipline held, one load-bearing task remains before anything gets frozen.

---

## 1. Architectural Assessment

### 1.1 The boundary held

The Testing Node Contract draws a clean line: QA-Pilot owns Capability Registry, Test Definition, Capability Resolution, Execution, Coverage Accounting, Result Contract, Evidence Production, and Governance Projection. It explicitly does not own Target Authority, Target Project State, Target Governance Decisions, Target Mutation, or Skill Authority.

This matters more than it might look on paper. It's the same pattern that governs everything else in the Librarian — no scalar authority, no auto-promotion, Runtime-proposes/Core-validates. QA-Pilot auditing the Librarian without being able to touch the Librarian's authority is what makes its findings usable as evidence rather than opinion. If that boundary had blurred even slightly — say, QA-Pilot able to auto-correct a finding it discovered — the whole audit's credibility would be compromised. It didn't blur. Good.

### 1.2 Reproducibility is earned, not asserted

100% structural/observational reproducibility across all 10 E2E runs, backed by a hashed provenance spine:

```
SOURCE MANIFEST → TEST PLANS → CONSTRUCTED ARTIFACTS → EXECUTION → RESULTS → EVIDENCE
```

Each transition is SHA-256 hashed and independently reconstructable. This is exactly what TESTING-COMPLETION-HONESTY-STANDARD.md exists to enforce, and the discipline is visibly holding — no completion claims outrunning evidence here.

### 1.3 The adapter pattern is the real deliverable

The Target Adapter Contract (target-adapter-v1.schema.json) plus three qualified adapters (mcp-jsonrpc, browser-playwright, cli) means QA-Pilot is not "a Librarian test harness" — it's a general-purpose auditor that happened to point at the Librarian first. That's the reusable asset. Pointing it at the next target should require zero rework of the node itself, only a new adapter if the target modality is genuinely novel.

### 1.4 Capability qualification is properly staged

SCRIPT_EXECUTION and SCHEMA_VALIDATION were pre-existing; MCP_API_INTERACTION and BROWSER_INTERACTION were validated through E2E-1/2 and E2E-3 respectively rather than assumed. That's the right order — capability claims earned by the runs that used them, not asserted up front.

---

## 2. Findings Against the Librarian

| ID | Severity | Description | Owner Decision | Ash's note |
|----|----------|-------------|----------------|------------|
| E2E-1-FIND-001 | violation | Pointer field name mismatch (project_id vs active_project_id) | Yes | Schema drift between two naming conventions. Needs standardization decision. |
| E2E-1-FIND-002 | violation | Validator path resolution coupled to validator's own location | No | Worth a second look — "No owner decision needed" should mean low-risk, not not yet triaged. |
| E2E-1-FIND-003 | violation | 3 registry entries with incomplete startup metadata | Yes | Data completeness gap. Straightforward once "complete" is defined. |
| E2E-2-FIND-001 | violation | /api/health endpoint returns 404 (Rust runtime) | Yes | Cheapest fix — low-effort, unblocks confident health-checking. |

---

## 3. The Load-Bearing Open Item: The 79 FAILs

The 79 failures are now the most valuable artifact. They could be:

1. **Implementation Regression** — genuine governance discrepancy
2. **Historical Behavior Superseded** — sprint claim was true when sealed but has since been superseded
3. **Intentional Behavior Change** — deliberate modification
4. **Historical Claim Not Operational** — claim was aspirational, never implemented
5. **Requirement Derivation Error** — derived requirement doesn't accurately capture the sprint claim
6. **Test Construction Error** — artifact construction was incomplete
7. **Environment/Dependency Effect** — external factor
8. **UNRESOLVED** — not yet understood (must be explicitly permitted)

**Critical invariant:** FAIL is an observation, not a governance verdict. The original FAIL remains forever. The governance layer adds `disposition = ...` without rewriting the execution result.

---

## 4. The Permanent Invariants

```
CLAIM ≠ REQUIREMENT ≠ TEST ≠ EXECUTION ≠ RESULT ≠ EVIDENCE ≠ GOVERNANCE DISPOSITION
```

And:

```
claimed capability ≠ qualified capability
constructed test ≠ executed test
observed result ≠ governance disposition
structural freeze ≠ semantic freeze
```

No stage may manufacture the authority of the next stage.

---

## 5. The Two-Stage Freeze

### Stage 1: Structural Freeze (NOW)

```
ASSURANCE CORPUS v1
├── STRUCTURAL FREEZE:       SEALED
├── GOVERNANCE CLASSIFICATION: PENDING
├── Requirements:            307
├── Artifacts:               307
├── Executions:              307
├── PASS:                    228
├── FAIL:                     79
├── ERROR:                     0
├── Reproducibility:         VERIFIED
└── Classification:          NOT YET PERFORMED
```

### Stage 2: Semantic Freeze (AFTER CLASSIFICATION)

```
ASSURANCE CORPUS v1
├── STRUCTURAL FREEZE:       SEALED
├── GOVERNANCE CLASSIFICATION: SEALED
├── FAILURES:                 79
├── CLASSIFIED:               63
└── UNRESOLVED:               16
```

---

## 6. Recommended Sequence

1. **Structural freeze** — Lock E2E-8/E8-R corpus as-is (reproducibility freeze, not truth claim)
2. **Classification pilot** — Test categories against 10-15 real FAILs before locking enum
3. **Full classification** — Classify all 79 under ASSURANCE-CORPUS-CLASSIFICATION-1
4. **Fix /api/health** — Independent, cheap, rerun E2E-2 for before/after
5. **Owner decisions** — FIND-001, FIND-003; re-examine FIND-002
6. **Semantic freeze** — Corpus v1 with both states recorded
7. **External target** — Point QA-Pilot at a non-Librarian system

---

## 7. The Strongest Conclusion

QA-Pilot can independently reconstruct, construct, execute, reproduce, and preserve evidence for assertions about another governed system without inheriting that system's authority.

That's the architectural property worth preserving.

```
GOVERNED TARGET
     │
     │ observation
     ▼
┌───────────────┐
│  QA-PILOT     │
│               │
│ Requirements  │
│      ↓        │
│ Capabilities  │
│      ↓        │
│ Test Plans    │
│      ↓        │
│ Test Artifact │
│      ↓        │
│ Adapter       │
│      ↓        │
│ Execution     │
│      ↓        │
│ Result        │
│      ↓        │
│ Evidence      │
└───────┬───────┘
        │
        ▼
  GOVERNANCE
  DISPOSITION
        │
        ▼
   OWNER AUTHORITY
```

QA-Pilot is not inside the authority loop. It supplies independently generated observations and evidence to that loop.

---

*Review saved as project artifact. Advisory-only.*
