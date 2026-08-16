# Sprint — QA-PILOT-CONTINUOUS-QUALIFICATION-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #226 (proposed)
**Lane:** assurance / continuous
**Type:** Controlled requalification lifecycle — event-driven assessment refresh
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Predecessor:** QA-PILOT-RISK-PRIORITIZATION-1 (#225, complete)

---

## 1. Purpose

Establish controlled requalification lifecycle when assurance-relevant state changes.

The system now knows:
- What exists? (#223 federation)
- Is the evidence trustworthy? (#222 qualification)
- Where is evidence missing or aging? (#224 freshness)
- Where should attention go? (#225 risk prioritization)

What it does NOT yet know:
- **When should this assessment be refreshed?**

Continuous Qualification closes that lifecycle.

## 2. The Model

```
Evidence Change
       │
       △
Qualification Trigger
       │
       △
Qualification Execution
       │
       △
QR-* New Record (append-only)
       │
       △
Risk Recalculation
       │
       △
Updated Advisory State
```

**Critical invariant:** Nothing gets overwritten. Every qualification run creates a new immutable record.

## 3. Trigger Classes

| Trigger | Example | Response |
|---------|---------|----------|
| `evidence_change` | New runtime event ingested | Requalify affected profile |
| `capability_change` | Capability declaration updated | Requalify capability profile |
| `finding_change` | New finding pattern detected | Recalculate risk |
| `freshness_expiry` | Evidence window exceeded | Flag for requalification |
| `policy_change` | Qualification baseline updated | Requalify all affected |

**Explicitly excluded:**
- Automatic remediation
- Automatic work creation
- Automatic approval
- Automatic dispatch

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| CQ-001 | Append-only history | `data/runtime-evidence/qualification-history.json` — runs appended, never modified. History command shows immutable chain. | ✅ |
| CQ-002 | Deterministic replay | Same evidence produces same qualification result. Verified by running qualification twice with same inputs. | ✅ |
| CQ-003 | Trigger provenance | Every run includes trigger_type, source_ref, triggered_at, profile, input_refs, result. | ✅ |
| CQ-004 | Risk integration | Evidence → Qualification → Finding Pattern → Risk chain works. Risk state updates from new qualification results. | ✅ |
| CQ-005 | No authority escalation | Engine cannot create work packets, assign owners, close findings, or approve remediation. Only produces observation, recommendation, evidence. | ✅ |
| CQ-006 | Failure isolation | One failed qualification does not disable engine. Other qualifications continue. | ✅ |
| CQ-007 | Multi-project validation | Continuous qualification works across projects (QA-Pilot + Librarian). No cross-project contamination. | ✅ |
| CQ-008 | CAG activation | Capability activated through: implemented + validated + evidence-backed + registered + projected + discoverable + authority-bounded | ✅ |
| CQ-009 | LINK readiness surface | `get_assurance_state()`, `get_latest_qualification()`, `get_risk_state()` interfaces defined in contract. No planning mutation. | ✅ |
| CQ-010 | Existing validators pass | No regressions from #225 baseline | ✅ |

## 5. Guardrails

| Guardrail | Rule |
|-----------|------|
| Append-only history | New QR-* records only. Never modify existing. |
| Deterministic | Same inputs → same outputs, always |
| Trigger provenance | Every run traces its cause |
| No authority escalation | Engine recommends; Owner decides |
| Failure isolation | One failure does not cascade |
| Advisory only | All outputs are observation and recommendation |

## 6. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-CONTINUOUS-QUALIFICATION-1.md` | This sprint document |
| `contracts/assurance/continuous-qualification-contract.md` | Trigger contract and invariants |
| `contracts/assurance/continuous-qualification-link-readiness.md` | LINK readiness interface |
| `scripts/continuous-qualification.py` | Trigger engine |
| `data/runtime-evidence/qualification-history.json` | Append-only qualification history |

## 7. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #226 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 8. Sequencing After This Sprint

```
#221 Capture          ✅
#222 Qualification    ✅
#223 Federation       ✅
#224 Freshness        ✅
#225 Risk Priority    ✅
#226 Continuous Qual  ← THIS SPRINT
#227 LINK Integration future
```

After #226, LINK integration becomes the correct next boundary because LINK can consume a mature assurance surface:

```
Agent Planning Context
      +
Assurance State
      +
Risk Context
      +
Evidence Provenance
```

## 9. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-RISK-PRIORITIZATION-1 (#225) | ✅ Complete |
| Qualification engine (`scripts/qualify-runtime-evidence.py`) | ✅ Working |
| Risk engine (`scripts/prioritize-risk.py`) | ✅ Working |
| Fleet freshness discovery (`scripts/discover-fleet-freshness.py`) | ✅ Working |
| Discovery projection | ✅ Exists |
