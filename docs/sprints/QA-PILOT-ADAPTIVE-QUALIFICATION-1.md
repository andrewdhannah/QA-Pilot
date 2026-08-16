# Sprint — QA-PILOT-ADAPTIVE-QUALIFICATION-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #231 (proposed)
**Lane:** assurance / adaptation
**Type:** Adaptive evaluation depth — dynamic qualification profiles
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Epic:** EPIC-QA-PILOT-ASSURANCE-OPTIMIZATION-1
**Predecessor:** QA-PILOT-RISK-CALIBRATION-1 (#230, complete)

---

## 1. Purpose

Create adaptive qualification profiles that adjust evaluation depth based on project context, not adaptive authority.

**The purpose is NOT adaptive authority. It IS adaptive evaluation depth.**

Current model:
```
Artifact Type → Qualification Profile → Checks
```

After this sprint:
```
Artifact Type + Risk + History + Coverage → Qualification Profile Selection → Evaluation Depth
```

## 2. The Question

**"Given what we know about this project and artifact, what qualification coverage is appropriate?"**

NOT: "Should this be approved?"

Approval remains outside QA-Pilot.

## 3. Adaptive Profile Model

### 3.1 Profile Definition

```json
{
  "profile_id": "RUNTIME-HIGH-ASSURANCE",
  "name": "High Assurance Runtime Profile",
  "applicable_artifact_types": ["runtime_capability", "runtime_action"],
  "required_checks": [
    "contract",
    "evidence",
    "authority",
    "security",
    "runtime_validation"
  ],
  "optional_checks": [
    "accessibility",
    "performance"
  ],
  "escalation_indicators": [
    "previous_authority_findings",
    "high_risk_band",
    "stale_evidence"
  ],
  "rationale": "For runtime capabilities with authority scope, require comprehensive validation including authority boundary checks."
}
```

### 3.2 Profile Selection Engine

Inputs:
- Artifact type
- Risk state (from risk engine)
- Historical findings (from qualification history)
- Change frequency (from planning accuracy)
- Evidence coverage (from fleet freshness)

Output:
- Recommended qualification profile
- Selection rationale
- Additional checks beyond baseline

### 3.3 Selection Example

Input:
```
Project: Librarian
Artifact: Runtime capability
History: Previous authority boundary findings
Risk: attention_required
Coverage: partial
```

Output:
```
Profile: RUNTIME-HIGH-ASSURANCE

Reasons:
- runtime authority scope detected
- previous governance findings exist
- evidence coverage below threshold

Additional checks:
- authority boundary
- discoverability
- provenance
```

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| AQ-001 | Qualification profiles have explicit schemas | `docs/schemas/assurance/adaptive-qualification-profile-v1.schema.json` — 8 fields, advisory_only const | ✅ |
| AQ-002 | Selection is deterministic | `scripts/select-qualification-profile.py` — same inputs produce same profile | ✅ |
| AQ-003 | Selection inputs are provenance-linked | Selection record includes risk_state, historical_findings, coverage_state, escalation_indicators | ✅ |
| AQ-004 | Historical findings influence recommendations | Projects with findings get RUNTIME-HIGH-ASSURANCE profile | ✅ |
| AQ-005 | Risk state influences evaluation depth | Higher risk → more required checks (5 vs 2) | ✅ |
| AQ-006 | Profile selection is explainable | Every selection includes selection_reasons and rationale | ✅ |
| AQ-007 | No automatic approval/rejection | Output is profile recommendation with advisory_only=true | ✅ |
| AQ-008 | Existing qualification results remain immutable | Profile selection does not modify existing results | ✅ |
| AQ-009 | Replay produces identical profile selection | Deterministic selection engine | ✅ |
| AQ-010 | Existing validators pass | No regressions from #230 baseline | ✅ |

## 5. Guardrails

| Guardrail | Rule |
|-----------|------|
| Adaptive depth, not authority | Changes evaluation coverage, not approval power |
| Explainable | Every selection has rationale |
| Deterministic | Same inputs → same output |
| No hidden policy | Profile criteria are explicit and auditable |
| Owner decides | Profile recommendation, not governance decision |

## 6. Important Boundary

Do not let adaptive qualification become hidden policy.

**Correct architecture:**
```
Evidence
   ↓
Qualification Profile Recommendation
   ↓
Human/System Review
   ↓
Qualification Execution
   ↓
Result
```

**NOT:**
```
Risk Score
   ↓
Automatic Governance Requirement
```

The first is adaptive assurance. The second is authority creation.

## 7. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-ADAPTIVE-QUALIFICATION-1.md` | This sprint document |
| `docs/schemas/assurance/adaptive-qualification-profile-v1.schema.json` | Profile schema |
| `contracts/assurance/adaptive-qualification-contract.md` | Adaptive qualification contract |
| `scripts/select-qualification-profile.py` | Profile selection engine |
| `data/assurance/qualification-profiles/` | Profile definitions |
| `data/assurance/profile-selections/` | Selection records |

## 8. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #231 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 9. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-RISK-CALIBRATION-1 (#230) | ✅ Complete |
| Risk engine | ✅ Working |
| Qualification history | ✅ Available |
| Fleet freshness | ✅ Working |
| Planning accuracy | ✅ Working |
