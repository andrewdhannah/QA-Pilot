# Sprint — QA-PILOT-LINK-ASSURANCE-INTEGRATION-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #227 (proposed)
**Lane:** assurance / integration
**Type:** Planning context integration — LINK consumes assurance state
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Predecessor:** QA-PILOT-CONTINUOUS-QUALIFICATION-1 (#226, complete)

---

## 1. Purpose

Expose governed assurance state to planning workflows without granting planning systems authority over qualification or remediation.

**Critical separation:**
- QA-Pilot determines assurance state
- LINK consumes assurance state for planning context
- Owner decides action

LINK answers: **"What assurance context should influence planning?"**
LINK does NOT answer: **"What should the project do?"**

## 2. Architecture

```
QA-Pilot Assurance Engine
        │
        △
Advisory State
        │
        △
Assurance Projection API    ← THIS SPRINT
        │
        △
LINK Planning Context
        │
        △
Human/Agent Planning
        │
        △
Owner Decides
```

## 3. Planning Context

### Before LINK Integration

```
Agent: "Create authentication sprint"
```

### After LINK Integration

```
Agent: "Create authentication sprint"

Context:
- Existing security qualification coverage: partial
- Previous security findings: 2
- Risk band: monitor
- Recommendation: include security qualification gate
```

The agent is better informed. It is not commanded.

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| LINK-001 | Read-only consumption | `scripts/link-assurance-query.py` — no write operations. Interface returns data only. authority_boundary field explicitly set. | ✅ |
| LINK-002 | Provenance preservation | Every assurance item includes provenance chain: risk_assessment_id, qualification_run_id, freshness_assessment_source. | ✅ |
| LINK-003 | Staleness visibility | Freshness label always included in output. Stale/aging state never hidden. | ✅ |
| LINK-004 | Recommendation boundary | Output is advisory context, not commands. Explicitly states: "This is advisory context, not a command." | ✅ |
| LINK-005 | Multi-project isolation | Planning context is per-project. No cross-project context leakage. | ✅ |
| LINK-006 | CAG activation | Integration activated through: implemented + validated + evidence-backed + registered + projected + discoverable + authority-bounded | ✅ |
| LINK-007 | Existing validators pass | No regressions from #226 baseline | ✅ |

## 5. Guardrails

| Guardrail | Rule |
|-----------|------|
| Read-only consumption | LINK has no write operations to QA-Pilot state |
| Provenance traces to source | Every assurance item traces back to evidence |
| Freshness always visible | Stale/aging labels never hidden |
| Advisory, not authoritative | Recommendations, not commands |
| Project isolation | No cross-project context leakage |
| Owner decides | LINK informs; Owner authorizes |

## 6. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-LINK-ASSURANCE-INTEGRATION-1.md` | This sprint document |
| `contracts/assurance/assurance-projection-contract.md` | Projection API contract |
| `scripts/link-assurance-query.py` | LINK query surface |
| `data/runtime-evidence/link-projection.json` | LINK-consumable projection |

## 7. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #227 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 8. Sequencing After This Sprint

```
#226 Continuous Qual  ✅
#227 LINK Integration ← THIS SPRINT
#228 Round-Trip Validation  future
```

After #227, the next milestone should be proving the entire cross-system loop:

```
Plan
  ↓
Build
  ↓
Qualify
  ↓
Evidence
  ↓
Risk
  ↓
LINK Context
  ↓
Better Plan
```

A round-trip validation sprint proves the full lifecycle before adding optimization.

## 9. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-CONTINUOUS-QUALIFICATION-1 (#226) | ✅ Complete |
| Risk engine (`scripts/prioritize-risk.py`) | ✅ Working |
| Continuous qualification engine | ✅ Working |
| Fleet freshness discovery | ✅ Working |
| Discovery projection | ✅ Exists |
