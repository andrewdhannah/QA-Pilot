# Start Packet — QA-PILOT-RISK-BASED-REVIEW-DEPTH-1

**Type:** Implementation — risk-based review depth
**Status:** 🔍 Start packet prepared — awaiting Owner confirmation to begin implementation
**Predecessor:** QA-PILOT-REVIEW-DEPTH-THRESHOLDS-DECISION-PACKET-1 (sealed #90)
**QA Pilot ledger head:** #90
**Authorization:** Owner-authorized 2026-07-08 per explicit instruction

---

## 1. Objective

Implement risk-based QA Pilot review depth so that review effort scales with the actual risk, evidence quality, and authority impact of a change. The sealed evidence pipeline already produces result packet consistency guards (RC-01–11) and E4 evidence bundles (EB-01–10). This sprint consumes those signals to determine how much review is appropriate, instead of applying a fixed review burden to every result.

## 2. Motivation

The sealed evidence pipeline now provides layered signals:

```
Result Packet
    ↓
Consistency Guard (RC-01–11)
    ↓
E4 Evidence Bundle (EB-01–10)
    ↓
Owner Review
```

The pipeline proves that result packets are consistent and evidence bundles are valid. But there is no mechanism to ask: **how much review does this specific result need?** A low-risk, fully passing, non-authority change can waste Owner time with heavy review. A high-risk, partially failing, authority-sensitive change can slip through light review. This sprint implements the risk-based review depth selector that sits between the evidence pipeline and the Owner review surface.

## 3. Input Dependencies

| Dependency | Status | Role |
|---|---|---|
| QA-PILOT-REVIEW-DEPTH-THRESHOLDS-1 (#88) | ✅ Sealed | Threshold schema, TD-1–TD-8 rules, basic state classification |
| QA-PILOT-REVIEW-DEPTH-THRESHOLDS-DECISION-PACKET-1 (#90) | ✅ Sealed | Decision packet schema, DP-1–DP-8 rules, Owner-facing packet states |
| RC-01–11 (Consistency Guard framework) | ✅ Existing | Result packet consistency check references |
| EB-01–10 (E4 Evidence Bundle framework) | ✅ Existing | Evidence bundle evaluation references |
| Lightweight lane infrastructure | ✅ Existing | Lane classification eligibility rules |
| Startup handoff enforcement | ✅ Existing | Session handoff posture |

## 4. Scope

### 4.1 Review Depth Modes

Define **four review depth levels** that QA Pilot can assign to a result packet:

| Level | When Applied | Output |
|-------|-------------|--------|
| **none** | Zero-risk, fully passing, internal-only changes | No review artifact generated. Result passes through. |
| **light** | Low-risk, all RC/EB checks pass, no authority change | Light review card — 1-page summary |
| **standard** | Moderate risk, some non-critical check failures, routine changes | Standard QA review packet — structured findings |
| **heavy** | High risk, authority-sensitive, production-path impact, partial completion, cross-node | Heavy evidence review packet — full evidence trace |

### 4.2 Risk Input Matrix

Review depth is determined by evaluating **risk inputs**, each contributing to a composite risk score:

| Risk Input | Source | Weight |
|---|---|---|
| Authority change flag | Sprint metadata / lane classification | High |
| Production-path impact | File scope classification (config vs source vs data) | High |
| Ledger/index/registry change | Sprint metadata, RC-08–RC-11 | High |
| Cross-node involvement | Lane classification | Medium |
| Partial-completion status | Result packet completion state | Medium |
| Incomplete requirements | Result packet requirement status | Medium |
| RC consistency failure count | Consistency guard RC-01–11 pass rate | Medium |
| E4 evidence status | Evidence bundle EB-01–10 pass rate | Medium |
| Lightweight lane classification | Lane eligibility check | Low |

### 4.3 Escalation Rules

Depth escalates automatically when risk input thresholds are exceeded:

| Rule | Trigger | Escalation |
|---|---|---|
| ER-1 | Authority change detected | Minimum depth = **heavy** (mandatory QA Pilot review) |
| ER-2 | Ledger/index/registry change detected | Minimum depth = **standard** |
| ER-3 | Production-path file mutation | Minimum depth = **standard** |
| ER-4 | Cross-node involvement | Minimum depth = **standard** |
| ER-5 | Partial completion (`outcome: incomplete` or `outcome: partial`) | Minimum depth = **standard** |
| ER-6 | Incomplete requirements (any requirement not `pass`) | Minimum depth = **standard** |
| ER-7 | RC pass rate < 100% (any consistency guard failure) | Escalate one level above default |
| ER-8 | E4 evidence pass rate < 100% (any EB check failure) | Escalate one level above default |
| ER-9 | Lightweight lane + all RC/EB pass + no authority/production/registry change | Minimum depth = **none** (QA Pilot may be skipped) |
| ER-10 | Multiple escalation rules fire simultaneously | Depth = highest triggered level (not additive) |

### 4.4 QA Pilot Review Mandatory / Optional

| Condition | QA Pilot Review |
|---|---|
| Heavy depth | ✅ Mandatory |
| Standard depth | ✅ Mandatory |
| Light depth | ✅ Performed (light card) |
| None depth | ⏭️ May be skipped |

### 4.5 Review Output Contracts

**Light Review Card** (`review-card`):
- Result packet ID, review depth, risk summary
- RC/EB pass/fail counts
- Whether change is cleared or needs attention
- Authority disclaimer
- 1-page structured output

**Standard QA Review Packet** (`review-packet`):
- Full evidence bundle review
- Per-finding commentary
- Consistency guard evaluation
- Risk input breakdown
- Recommendation summary
- Authority disclaimer

**Heavy Evidence Review Packet** (`review-packet-heavy`):
- Full standard packet content
- Cross-node involvement trace
- Authority boundary assessment
- Registry/ledger impact analysis
- Partial-completion gap evaluation
- Escalation chain documentation
- Full evidence trace

### 4.6 Will Do

1. **Review depth schema** — JSON schema for review depth selection, including:
   - Risk input evaluation record
   - Composite risk score
   - Assigned review depth
   - Escalation justification chain
   - Source references (RC-*, EB-*, threshold ID, packet ID)
2. **Review output schemas** — Three schemas for light/standard/heavy output contracts
3. **CLI commands:**
   - `depth-evaluate` — Evaluate a result packet and assign review depth
   - `depth-read <id>` — Read stored depth evaluation
   - `depth-list` — List all depth evaluations
   - `depth-validate [id]` — Validate against schema + RD rules
   - `depth-status` — Show aggregate depth state
   - `card-create <depth-id>` — Generate light review card
   - `packet-create <depth-id>` — Generate standard review packet
   - `packet-heavy-create <depth-id>` — Generate heavy evidence review packet
4. **Storage:** `data/risk-based-review-depths/`
5. **Validator rules** (RD-1 through RD-N) enforcing:
   - Valid risk input values
   - Correct depth assignment per escalation rules
   - Correct output contract format per depth level
   - Rejection of auto-accept/auto-reject/execution/seal/approval/verification
   - Authority boundary enforcement
   - Reference traceability (RC-*, EB-*, thresholds)
6. **Integration with existing pipelines:**
   - Consume RC pass/fail counts from result packet consistency framework
   - Consume EB pass/fail counts from E4 evidence bundle framework
   - Consume threshold evaluations from #88
   - Feed recommendation to decision packet layer (#90)
   - Surface depth selection rationale for Owner transparency

### 4.7 Will Not Do

- ❌ No execution authority introduced
- ❌ No auto-acceptance or auto-rejection of results
- ❌ No approval or seal authority
- ❌ No verification closure
- ❌ No mutation of source records or evidence chain
- ❌ No modification to sealed #88, #89, or #90 artifacts
- ❌ No changes to Librarian startup protocol or infrastructure
- ❌ No changes to QA Pilot's advisory-only posture

## 5. Authority Boundary

| Rule | Value |
|------|-------|
| Authority mode | advisory-only |
| Execution authority | explicitly denied |
| Auto-accept/reject authority | explicitly denied |
| Seal or approval authority | explicitly denied |
| Source mutation | explicitly denied |
| Production mutation | explicitly denied |
| Can override Owner decision | explicitly denied |
| Can block/non-block Owner review | advisory recommendation only |

## 6. Acceptance Gates

- [ ] RD-1: Review depth schema defines none/light/standard/heavy with correct fields
- [ ] RD-2: Risk input matrix produces composite risk score from all 9 inputs
- [ ] RD-3: All 10 escalation rules (ER-1–ER-10) implemented and tested
- [ ] RD-4: 3 review output schemas (light card, standard packet, heavy packet) defined
- [ ] RD-5: CLI commands implemented (8 commands)
- [ ] RD-6: Validator rules reject authority claims, enforce depth correctness
- [ ] RD-7: Positive fixtures (low risk → none/light, authority change → heavy) pass
- [ ] RD-8: Negative fixtures (depth too low for risk, authority claims) fail
- [ ] RD-9: Existing TD and DP validators remain unaffected (regression check)
- [ ] RD-10: Existing RC and EB framework references resolve correctly

## 7. Validation Scenarios (Required)

| # | Scenario | Expected Depth | Validates |
|---|----------|---------------|-----------|
| 1 | Low-risk lightweight change, all RC/EB pass, no authority/production/registry change | none or light | ER-9 |
| 2 | Authority-sensitive change (authority flag set) | heavy | ER-1 |
| 3 | Incomplete-plan result (partial completion + incomplete requirements) | standard or heavy | ER-5, ER-6 |
| 4 | Failed RC checks + failed EB checks on otherwise low-risk change | standard (escalated from none/light) | ER-7, ER-8 |
| 5 | QA Pilot authority boundary enforcement — advisory-only rules enforced | all levels | RD-6 violation rejection |
| 6 | Existing RC and EB validators unaffected by new sprint | no regression | RD-9 |

## 8. Completion Packet Requirements (8 Deliverables)

| # | Deliverable | Description |
|---|---|---|
| 1 | **Review-depth matrix** | Document defining the 4 levels, risk inputs, weights, and mapping rules |
| 2 | **Escalation rules** | Document defining ER-1 through ER-10 with triggers, conditions, and edge cases |
| 3 | **Validator rules** | Script `scripts/validate-qa-pilot-risk-based-review-depth.py` with RD-1–RD-N rules |
| 4 | **Fixtures** | 6+ fixtures covering valid/invalid depth assignments for all 4 levels |
| 5 | **Test results** | Test runner `scripts/test-qa-pilot-risk-based-review-depth.sh` — all tests pass |
| 6 | **Examples of each review mode** | One example each for light card, standard packet, heavy packet |
| 7 | **Regression impact assessment** | Verification that existing TD, DP, RC, EB, and pipeline validators remain unaffected |
| 8 | **Seal recommendation** | Summary of scope satisfaction, authority boundaries preserved, and evidence |

## 9. Pre-requisites

- [x] QA-PILOT-REVIEW-DEPTH-THRESHOLDS-1 sealed (#88)
- [x] QA-PILOT-REVIEW-DEPTH-THRESHOLDS-STARTUP-SURFACE-1 sealed (#89)
- [x] QA-PILOT-REVIEW-DEPTH-THRESHOLDS-DECISION-PACKET-1 sealed (#90)
- [x] RC-01–11 consistency guard framework exists
- [x] EB-01–10 evidence bundle framework exists
- [x] Lightweight lane infrastructure exists
- [x] QA Pilot ledger at #90

## 10. Start Packet Metadata

```
packet_id: START-PACKET-QA-RISK-DEPTH-001
prepared_at: 2026-07-08T07:20:00Z
prepared_by: OpenWork agent
status: awaiting_owner_confirmation
authority_mode: advisory-only
qa_pilot_ledger_head: 90
predecessor: QA-PILOT-REVIEW-DEPTH-THRESHOLDS-DECISION-PACKET-1
sprint_id: QA-PILOT-RISK-BASED-REVIEW-DEPTH-1
```
