# Sprint — QA-PILOT-RUNTIME-EVIDENCE-QUALIFICATION-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #222 (proposed)
**Lane:** assurance / qualification
**Type:** Trust calibration — runtime evidence qualification
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none
**Predecessor:** QA-PILOT-RUNTIME-EVIDENCE-COMPLETION-1 (#221, complete)

---

## 1. Purpose

Demonstrate that runtime evidence records are sufficient, consistent, and useful for independent qualification decisions. This is a trust calibration sprint — not a federation sprint.

Sprint #221 proved runtime evidence can be captured correctly.
Sprint #222 proves runtime evidence can be evaluated correctly.

This is the first consumer of the Qualification Compiler against a non-sprint artifact, validating the broader thesis: QA-Pilot does not only qualify project changes — it can qualify operational evidence streams.

## 2. Qualification Questions

### Q1: Provenance Completeness

Can every runtime evidence record answer all 6 provenance questions?

| Question | Field | Required |
|----------|-------|----------|
| What happened? | `observation.observed_state` | Yes |
| Who produced it? | `provenance.execution_identity.agent_identity` | Yes |
| Under what runtime? | `provenance.execution_identity.runtime_identity` | Yes |
| Using what model? | `provenance.execution_identity.model_identity` | Yes |
| For which project? | `provenance.governance_context.project_identity` | Yes |
| Under what authority? | `provenance.governance_context.authority_scope` | Yes |

**Failure:** Runtime event exists but any provenance field is missing.
**Disposition:** FINDING.

### Q2: Evidence Integrity

Verify:
- Append-only behavior (no overwrites)
- Immutability after ingestion (no modifications)
- Duplicate handling (same event_id rejected)
- Timestamp consistency (captured_at <= now)
- Schema version tracking (schema_version present)

**Test:** Attempt to modify an existing runtime evidence record. Expected: rejected by validation.

### Q3: Evidence Usability

Can QA-Pilot make a qualification determination from evidence alone?

**Input:** runtime-action-event + lifecycle-event + resource-observation
**Output:** Qualification Result: PASS / FINDING / NOT_APPLICABLE

This tests the full pipeline: Capture → Validate → Qualify.

### Q4: Freshness Semantics

Prove the two-class freshness model works correctly:

| Evidence Class | Age Behavior | Example |
|----------------|-------------|---------|
| `record` (immutable event) | Old event ≠ stale evidence | Created 2026-08-15 → `historical` record (still valid as proof) |
| `snapshot` (mutable state) | Old snapshot = potentially stale state | Created 15min ago → `stale` snapshot |

The system must not confuse:
- `old event ≠ stale evidence` (records age into historical/archived, not stale)
- `old snapshot = potentially stale state` (snapshots age into stale)

### Q5: Authority Boundary Regression

Carry forward CAG-RUNTIME-008. The qualification engine must not accidentally elevate evidence.

**Expected:**
- Evidence: "Agent performed deployment"
- Qualification: "Deployment observed"
- NOT: "Deployment approved"

## 3. Qualification Profile

First consumer of the Qualification Compiler against a non-sprint artifact.

```json
{
  "profile": "runtime_evidence_assurance_v1",
  "applies_to": [
    "runtime-action-event",
    "runtime-lifecycle-event",
    "runtime-resource-observation"
  ],
  "checks": [
    "provenance-completeness",
    "immutability",
    "freshness-classification",
    "authority-boundary",
    "schema-conformance"
  ]
}
```

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| RE-QUAL-1 | Provenance completeness check implemented | `scripts/qualify-runtime-evidence.py` — validates all 16 required provenance fields (6 identity questions × 2-3 fields each) | ✅ |
| RE-QUAL-2 | Evidence integrity check implemented | Validates evidence_id, schema_version, evidence_class, timestamps, custody origin | ✅ |
| RE-QUAL-3 | Evidence usability proven | `data/runtime-evidence/qualification-results.json` — 3 records qualify, all produce PASS disposition | ✅ |
| RE-QUAL-4 | Freshness semantics validated | Records correctly get current/historical/archived labels. Snapshots correctly get current/stale labels. Records never get "stale". | ✅ |
| RE-QUAL-5 | Authority boundary regression passes | CAG-RUNTIME-008 carried forward. No authorization/dispatch/executed/sealed/approved/owner_decision fields found in any record. | ✅ |
| RE-QUAL-6 | Qualification profile IR created | `qualification/compiler/ir/runtime-evidence-qualification-ir.json` — 5 invariants, 3 gates, 2 authority constraints, 9 layer derivations, 2 adversarial rules | ✅ |
| RE-QUAL-7 | All 5 qualification checks pass against ingested evidence | 3/3 records PASS. 0 findings. Disposition: PASS. | ✅ |
| RE-QUAL-8 | All existing validators pass | No regressions from #221 baseline. | ✅ |

## 5. Guardrails

| Guardrail | Rule |
|-----------|------|
| QA-Pilot only | No cross-project evidence qualification |
| No federation | No multi-project identity or routing |
| No planning integration | No connection to cost estimates or LINK |
| Advisory-only | All qualification results maintain advisory_only=true |
| No auto-remediation | Qualification findings produce recommendations, not actions |
| Authority boundary | Qualification engine observes evidence; it does not authorize action |
| First non-sprint artifact | This validates QA-Pilot can qualify operational evidence, not just project changes |

## 6. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-RUNTIME-EVIDENCE-QUALIFICATION-1.md` | This sprint document |
| `qualification/compiler/ir/runtime-evidence-qualification-ir.json` | Qualification profile IR for runtime evidence |
| `scripts/qualify-runtime-evidence.py` | Qualification engine for runtime evidence |
| `data/runtime-evidence/qualification-results.json` | Qualification results from running against ingested evidence |

## 7. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #222 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 8. Sequencing After This Sprint

```
QA-PILOT-RUNTIME-EVIDENCE-COMPLETION-1   (#221) ✅
        ↓
QA-PILOT-RUNTIME-EVIDENCE-QUALIFICATION-1 (#222) ← THIS SPRINT
        ↓
QA-PILOT-RUNTIME-EVIDENCE-FEDERATION-1   (future)
        ↓
Fleet Freshness + Discovery
        ↓
Planning Accuracy Loop (LINK integration)
```

## 9. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-RUNTIME-EVIDENCE-COMPLETION-1 (#221) | ✅ Complete |
| Qualification Compiler (`qualification/compiler/`) | ✅ Exists |
| Qualification IR schema (`qualification/compiler/ir/qualification-ir.schema.json`) | ✅ Exists |
| Runtime evidence store (`data/runtime-evidence/`) | ✅ 3 records ingested |

## 10. Architectural Significance

This sprint validates a critical thesis: **QA-Pilot can qualify operational evidence streams, not just project changes.**

Previous qualification targets:
- Sprint #216: QR-* qualification records (sprint artifacts)
- Sprint #217: Evidence pipeline (evidence packets)
- Sprint #218: Evaluation engine (qualification results)
- Sprint #219: Review surface (human decisions)

New qualification target:
- Sprint #222: Runtime evidence (operational observations)

If this works, the qualification substrate is proven general-purpose — not locked to sprint lifecycle artifacts.
