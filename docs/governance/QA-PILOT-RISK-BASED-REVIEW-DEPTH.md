# QA Pilot Risk-Based Review Depth — Governance Document

## 1. Purpose

Define how QA Pilot assigns risk-based review depth to result packets so that review effort scales with actual change risk, evidence quality, and authority impact. This governance document covers the review depth model, risk input matrix, escalation rules, output contracts, and authority boundaries.

## 2. Review Depth Modes

| Level | Definition | Typical Use Case |
|-------|-----------|-----------------|
| **none** | No QA Pilot review artifact generated | Zero-risk, fully passing, non-authority, non-production, internal-only changes in lightweight lanes |
| **light** | 1-page summary card produced | Low-risk changes where all RC/E4 checks pass and no authority/production/registry impact |
| **standard** | Full structured review packet produced | Moderate-risk changes with some non-critical failures, routine changes, or partial-completion results |
| **heavy** | Full evidence trace packet produced | High-risk changes with authority impact, production-path mutation, ledger/registry changes, or cross-node involvement |

## 3. Risk Input Matrix

### 3.1 Input Definitions

| Input | Type | Weight | Description |
|-------|------|--------|-------------|
| authority_change | boolean | 10 | Whether the result involves authority boundary changes |
| production_path_impact | boolean | 7 | Whether the result affects production code or data paths |
| ledger_registry_change | boolean | 8 | Whether the result modifies ledger, index, or registry records |
| cross_node_involvement | boolean | 5 | Whether the result spans multiple agent nodes |
| partial_completion | boolean | 5 | Whether the result has partial completion status |
| incomplete_requirements | integer | 0/3/6 | Number of incomplete requirements (0=none, 1-2=some+3, 3+=many+6) |
| rc_failure_count | integer | 0/3/6 | Number of failed RC consistency checks (0=none, <50%=+3, >=50%=+6) |
| rc_total_count | integer | — | Total RC consistency checks (for rate calculation) |
| e4_failure_count | integer | 0/3/6 | Number of failed E4 evidence checks |
| e4_total_count | integer | — | Total E4 evidence checks (for rate calculation) |
| lightweight_lane | boolean | -3 | Whether the result is in a lightweight lane (reduces risk score) |

### 3.2 Composite Score Ranges

| Score Range | Base Depth |
|-------------|-----------|
| 0–3 | none |
| 4–10 | light |
| 11–20 | standard |
| 21+ | heavy |

## 4. Escalation Rules (ER-1 through ER-10)

| Rule | Condition | Effect |
|------|-----------|--------|
| ER-1 | `authority_change == true` | Floor = **heavy**. QA Pilot review mandatory. |
| ER-2 | `ledger_registry_change == true` | Floor = **standard**. |
| ER-3 | `production_path_impact == true` | Floor = **standard**. |
| ER-4 | `cross_node_involvement == true` | Floor = **standard**. |
| ER-5 | `partial_completion == true` | Floor = **standard**. |
| ER-6 | `incomplete_requirements > 0` | Floor = **standard**. |
| ER-7 | `rc_failure_count > 0` | Escalate one level above base depth. |
| ER-8 | `e4_failure_count > 0` | Escalate one level above base depth. |
| ER-9 | lightweight_lane AND all RC/E4 pass AND no authority/production/registry change | Floor = **none**. QA Pilot may be skipped. |
| ER-10 | Multiple escalation rules fire simultaneously | Final depth = highest triggered level (not additive). |

**Escalation ordering:** Escalation rules are evaluated independently. Each rule sets a floor or escalation. ER-10 ensures the highest depth wins when multiple rules fire.

## 5. Output Contracts

### 5.1 Light Review Card
Produced for `light` depth. 1-page summary containing:
- Source evaluation ID and risk score
- RC/E4 pass/fail counts and rates
- Clearance status (`cleared` or `needs_attention`)
- Authority disclaimer

### 5.2 Standard QA Review Packet
Produced for `standard` depth. Structured review containing:
- Evidence bundle review (E4 summary)
- Per-finding commentary
- Consistency guard evaluation (RC summary)
- Risk input breakdown
- Recommendation summary
- Authority disclaimer

### 5.3 Heavy Evidence Review Packet
Produced for `heavy` depth. Full evidence trace containing:
- Standard packet content (evidence review, findings, guard eval, risk breakdown)
- Cross-node involvement trace
- Authority boundary assessment
- Registry/ledger impact analysis
- Partial-completion gap evaluation
- Escalation chain documentation (all 10 ER rules with triggered/not-triggered status)
- Full evidence trace
- Recommendation summary
- Authority disclaimer

## 6. Validator Rules

### RD Rules (Depth Evaluations)

| Rule | Description |
|------|-------------|
| RD-1 | assigned_depth must be one of none/light/standard/heavy |
| RD-2 | composite_risk_score must be non-negative integer |
| RD-3 | advisory_only must be True |
| RD-4 | custody must be qa-pilot-local |
| RD-5 | librarian_impact must be 'none' |
| RD-6 | authority_disclaimer must match exact text |
| RD-7 | No forbidden authority fields present |
| RD-8 | Text fields must not claim authority |
| RD-9 | evaluation_id must start with RD-EVAL- |
| RD-10 | escalation_chain must contain valid ER- rule IDs |
| RD-11 | Depth escalation correctness (ER-1, ER-2, ER-5 enforcement) |
| RD-12 | ER-9 present when lightweight+allPass conditions met |
| RD-13 | escalation_chain length ≤ 10 |
| RD-14 | No duplicate rule IDs in escalation_chain |
| RD-15 | assigned_depth is in valid depth order |

### C Rules (Review Cards)

| Rule | Description |
|------|-------------|
| C-1 | assigned_depth must be 'light' |
| C-2 | clearance_status must be 'cleared' or 'needs_attention' |
| C-3 | No forbidden authority fields |

### P Rules (Review Packets)

| Rule | Description |
|------|-------------|
| P-1 | assigned_depth must be 'standard' or 'heavy' |
| P-2 | No forbidden authority fields |

### H Rules (Heavy Packets)

| Rule | Description |
|------|-------------|
| H-1 | assigned_depth must be 'heavy' |
| H-2 | No forbidden authority fields |

## 7. Authority Boundary

| Operation | Allowed |
|-----------|---------|
| Read evidence depth posture | ✅ Advisory |
| Assign review depth (none/light/standard/heavy) | ✅ Advisory |
| Generate review output artifacts | ✅ Advisory |
| Approve intake | ❌ Denied |
| Verify evidence | ❌ Denied |
| Close workbench items | ❌ Denied |
| Seal results | ❌ Denied |
| Execute work | ❌ Denied |
| Mutate source records or evidence chain | ❌ Denied |
| Replace Owner decision authority | ❌ Denied |

## 8. Integration Points

| Surface | Integration |
|---------|------------|
| RC-01–11 | Depth evaluation consumes RC pass/fail counts from consistency guard framework |
| EB-01–10 | Depth evaluation consumes E4 pass/fail counts from evidence bundle framework |
| TD threshold (#88) | Depth evaluation supersedes the simpler threshold state with risk-based depth |
| DP decision packet (#90) | Depth evaluation feeds recommendation to decision packet layer |
| Lightweight lane | Lane classification determines ER-9 eligibility (lightweight skip) |
| Session handoff | Depth status surfaces can be added to startup report |

## 9. Sealed Sprint Preservation

This sprint does not modify, extend, or supersede:
- QA-PILOT-REVIEW-DEPTH-THRESHOLDS-1 (#88) — preserved as-is
- QA-PILOT-REVIEW-DEPTH-THRESHOLDS-STARTUP-SURFACE-1 (#89) — preserved as-is
- QA-PILOT-REVIEW-DEPTH-THRESHOLDS-DECISION-PACKET-1 (#90) — preserved as-is

All existing QA Pilot validators and review behavior remain unaffected.

## 10. Completion Packet

### 10.1 Files Created/Modified

| File | Type | Purpose |
|------|------|---------|
| `docs/schemas/qa-pilot-risk-based-review-depth.schema.json` | Created | Evaluation schema |
| `docs/schemas/qa-pilot-risk-based-review-card.schema.json` | Created | Light review card schema |
| `docs/schemas/qa-pilot-risk-based-review-packet.schema.json` | Created | Standard review packet schema |
| `docs/schemas/qa-pilot-risk-based-heavy-packet.schema.json` | Created | Heavy evidence review packet schema |
| `scripts/qa_pilot_risk_based_review_depth.py` | Created | CLI (8 commands) |
| `scripts/validate-qa-pilot-risk-based-review-depth.py` | Created | RD/C/P/H validator rules |
| `scripts/test-qa-pilot-risk-based-review-depth.sh` | Created | Test runner |
| `docs/examples/qa-pilot-risk-based-review-depth/*.json` | Created | 9 fixtures (6 valid + 3 invalid) |
| `docs/governance/QA-PILOT-RISK-BASED-REVIEW-DEPTH.md` | Created | Governance document |
| `docs/sprints/QA-PILOT-RISK-BASED-REVIEW-DEPTH-1.md` | Created | Sprint receipt |
| `data/risk-based-review-depths/` | Created | Data store directory |

### 10.2 Review Depth Model Summary

4 review depth levels (none/light/standard/heavy), 9 risk inputs with weighted scoring, composite score ranges, escalation floors, and 3 output contract types.

### 10.3 Risk Input Mapping

9 risk inputs mapped to source signals: authority change, production-path, ledger/registry, cross-node, partial-completion, incomplete requirements (from result packet), RC failures (from consistency guard), E4 failures (from evidence bundle), lightweight lane (from lane classification).

### 10.4 Escalation Rule Summary

10 escalation rules (ER-1 through ER-10) covering authority-sensitive triggers, production/registry impacts, completion status, evidence quality signals, lane classification, and conflict resolution (ER-10: highest depth wins).

### 10.5 Output Contract Examples

- `valid-low-risk-lightweight.json` → RD-EVAL assigned `none` depth
- `valid-standard-packet-example.json` → RP- standard review packet
- `valid-heavy-packet-example.json` → HP- heavy evidence review packet with full escalation chain

### 10.6 Validator/Fixture Results

```
Results: 19/19 pass, 0 fail, 0 skip
```

All 6 validation scenarios pass:
1. Low-risk lightweight → none/light ✅
2. Authority-sensitive → heavy ✅
3. Incomplete-plan → standard ✅
4. Failed RC/E4 → escalated to standard ✅
5. Authority boundary enforced (advisory-only) ✅
6. Existing validators unaffected ✅

### 10.7 Regression Impact Assessment

- Sealed #88, #89, #90: unchanged — new sprint creates independent surfaces
- Existing TD-1–TD-8 validators: unaffected — validator scripts unchanged
- Existing DP-1–DP-8 validators: unaffected — validator scripts unchanged
- Existing RC/EB framework references: unaffected — consumed as inputs only
- Existing QA Pilot pipeline validators: all remain green
- Windows Router: remains deferred_not_wired

### 10.8 Seal Recommendation

Scope satisfied: all 10 acceptance gates met, 19/19 tests pass, 9 fixtures cover valid/invalid cases, authority boundaries enforced, sealed predecessors preserved. Recommend Owner seal.

---

## 11. Windows Router Deferred

Windows Router remains **deferred_not_wired**. No cross-node routing, Windows project initialization, or WIN-EVIDENCE-PACKET-EXPORT-1 work was performed or is required for this sprint.
