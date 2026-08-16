# Sprint — QA-PILOT-ASSURANCE-ROUNDTRIP-VALIDATION-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #228 (proposed)
**Lane:** assurance / validation
**Type:** Round-trip validation — prove the complete governed improvement loop
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none
**Predecessor:** QA-PILOT-LINK-ASSURANCE-INTEGRATION-1 (#227, complete)

---

## 1. Purpose

Validate the complete closed-loop path from planning intent through implementation, evidence capture, qualification, risk assessment, and back to improved planning decisions.

The remaining question is not "can each component work?" — that is already demonstrated.

The question is: **Does the complete governed improvement loop produce useful planning feedback without violating authority boundaries?**

## 2. The Complete Loop

```
Planning Intent
      │
      △
Implementation Work
      │
      △
Evidence Capture
      │
      △
Qualification
      │
      △
Risk Assessment
      │
      △
LINK Assurance Context
      │
      △
Improved Planning Decision
```

This sprint proves this loop works end-to-end.

## 3. Test Scenario

### 3.1 Controlled Planning Fixture

Create a bounded test project:

```json
{
  "project_id": "roundtrip-validation-fixture",
  "change_type": "capability_addition",
  "description": "Add a governed capability requiring contract, evidence, validation, and authority declaration",
  "expected_artifacts": [
    "implementation_artifact",
    "evidence_artifact",
    "qualification_record",
    "risk_assessment"
  ]
}
```

### 3.2 Normal Development Path

Execute ordinary governed work:
1. Create implementation artifact
2. Capture evidence
3. Run qualification
4. Assess risk
5. Project to LINK

No special validation path. The proof is that ordinary governed work creates the necessary signals.

### 3.3 Injected Finding (Negative Case)

Inject a known finding:

```
Finding: Capability registered without discoverability projection
Severity: medium
Expected propagation:
  Finding → Qualification FINDING → Risk Increase → LINK Context Update
```

### 3.4 Authority Boundary Validation

Explicitly test:

| Cannot Do | Expected Behavior |
|-----------|-------------------|
| Create remediation work | Engine recommends, does not create |
| Close findings | Owner decides |
| Approve risk acceptance | Owner decides |
| Modify project state | Read-only projection |
| Convert recommendation to instruction | LINK informs, does not command |

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| RT-001 | Planning consumes assurance projection | `link-assurance-query.py context qa-pilot` returns advisory context with coverage and risk data | ✅ |
| RT-002 | Work produces evidence chain | `federate-runtime-evidence.py ingest` creates evidence with full provenance | ✅ |
| RT-003 | Qualification runs automatically | `continuous-qualification.py run-qualification` produces new qualification run | ✅ |
| RT-004 | Finding propagates through risk model | Qualification → Risk → LINK chain verified. Risk assessment updates. | ✅ |
| RT-005 | LINK receives updated advisory state | `link-assurance-query.py fleet` shows updated risk and recommendations | ✅ |
| RT-006 | No authority boundary violations | 7 authority checks pass. No dispatch, remediation, closure, approval, mutation, instruction, state modification. | ✅ |
| RT-007 | Full provenance replay succeeds | Every assurance item traces: LINK View → Projection → Risk → Qualification → Evidence. Chain verifiable. | ✅ |
| RT-008 | Owner decision remains final authority | All outputs advisory-only. Owner authority preserved. | ✅ |
| RT-009 | Planning improvement measured | Planning context includes assurance data (coverage, risk, recommendations) | ✅ |
| RT-010 | Existing validators pass | No regressions from #227 baseline | ✅ |

## 5. Test Execution

### 5.1 Scenario A: Happy Path

```
1. Create controlled fixture
2. Execute normal development
3. Capture evidence
4. Qualify
5. Assess risk
6. Query LINK
7. Verify advisory context includes assurance data
```

### 5.2 Scenario B: Finding Injection

```
1. Inject capability without discoverability
2. Trigger qualification
3. Verify FINDING disposition
4. Verify risk increase
5. Verify LINK context updated
6. Verify no authority escalation
```

### 5.3 Scenario C: Authority Boundary

```
1. Attempt to create work packet from finding → REJECT
2. Attempt to close finding → REJECT
3. Attempt to approve remediation → REJECT
4. Verify all recommendations remain advisory
```

## 6. Guardrails

| Guardrail | Rule |
|-----------|------|
| Validation sprint | No new capabilities added |
| Controlled fixture | Bounded test project, not production |
| Normal development path | No special validation shortcuts |
| Authority test | Explicit negative testing of boundaries |
| Planning improvement | Must measure decision quality difference |

## 7. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-ASSURANCE-ROUNDTRIP-VALIDATION-1.md` | This sprint document |
| `scripts/roundtrip-validation.py` | Validation orchestrator |
| `data/roundtrip/fixture.json` | Controlled test fixture |
| `data/roundtrip/scenario-a-result.json` | Happy path result |
| `data/roundtrip/scenario-b-result.json` | Finding injection result |
| `data/roundtrip/scenario-c-result.json` | Authority boundary result |
| `data/roundtrip/validation-report.json` | Final validation report |

## 8. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #228 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 9. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-LINK-ASSURANCE-INTEGRATION-1 (#227) | ✅ Complete |
| All assurance engine components | ✅ Working |
| LINK query surface | ✅ Working |
| Continuous qualification | ✅ Working |
| Risk engine | ✅ Working |

## 10. What This Sprint Proves

After this sprint, QA-Pilot has proven its core thesis:

```
A governed improvement loop can:
1. Capture operational evidence
2. Qualify it against contracts
3. Assess risk
4. Project to planning workflows
5. Improve human decisions
6. Without violating authority boundaries
```

The next phase after validation is optimization:
- Planning accuracy measurement
- Cost/risk prioritization
- Adaptive qualification profiles
- Broader project onboarding
- Automated capability discovery
