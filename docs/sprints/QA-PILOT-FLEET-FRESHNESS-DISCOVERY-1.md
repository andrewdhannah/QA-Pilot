# Sprint — QA-PILOT-FLEET-FRESHNESS-DISCOVERY-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #224 (proposed)
**Lane:** assurance / discovery
**Type:** Advisory discovery layer — fleet freshness and coverage
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Predecessor:** QA-PILOT-RUNTIME-EVIDENCE-FEDERATION-1 (#223, complete)

---

## 1. Purpose

Establish an advisory discovery layer that identifies evidence freshness and coverage state across governed projects.

The remaining question is no longer "can QA-Pilot qualify?" It is:

**Can QA-Pilot determine where qualification attention is needed without requiring every project to be manually inspected?**

This sprint is NOT orchestration, remediation, or automated prioritization. It is observation and recommendation only.

## 2. Critical Distinction: Freshness ≠ Quality

| Fresh Evidence | Old Evidence |
|----------------|--------------|
| Fresh evidence can be bad | Old evidence can still be valid historical evidence |
| A fresh failing qualification = attention needed | A historical record = still valid proof |

**Example:**

| Scenario | Freshness | Quality | Meaning |
|----------|-----------|---------|---------|
| Project A: fresh failing qualification | current | failing | Attention needed NOW |
| Project B: old passing qualification | historical | passing | Still valid, but check recency |
| Project C: no recent evidence | unknown | unknown | Coverage gap |
| Project D: stale snapshot | stale | unknown | State may have changed |

## 3. Freshness Policy

### 3.1 Evidence Class Semantics

| Evidence Class | Freshness Model | Labels |
|----------------|-----------------|--------|
| `record` (immutable event) | Age does not invalidate. Old proof remains proof. | `current` < 60min, `historical` < 4hr, `archived` >= 4hr |
| `snapshot` (mutable state) | Age invalidates. Old observation may be stale. | `current` < 15min, `aging` 15-60min, `stale` > 60min |

### 3.2 Coverage Domains

Each project has evidence across domains:

| Domain | Evidence Types | Source |
|--------|---------------|--------|
| `runtime_action` | Action events | FlightPlan |
| `runtime_lifecycle` | Lifecycle events | FlightPlan |
| `runtime_resource` | Resource observations | FlightPlan |
| `qualification` | QR-* records | Qualification substrate |
| `security` | Security findings | Security scans |
| `accessibility` | A11y findings | Accessibility audits |

### 3.3 Coverage States

| State | Meaning |
|-------|---------|
| `full` | All expected domains have current evidence |
| `partial` | Some domains have evidence, others missing |
| `minimal` | Only essential domains have evidence |
| `none` | No evidence in any domain |
| `unknown` | Cannot determine coverage |

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| FRESH-001 | Freshness policy contract defined | `contracts/assurance/fleet-freshness-policy.md` — defines record/snapshot semantics, freshness windows, coverage domains, advisory boundary | ✅ |
| FRESH-002 | Coverage model implemented | `scripts/discover-fleet-freshness.py` — assesses per-project coverage across 6 domains. Produces coverage state (full/partial/minimal/none/unknown). | ✅ |
| FRESH-003 | Discovery projection created | `data/runtime-evidence/discovery-projection.json` — lightweight index with project_id, freshness_state, coverage_state, missing_domains, recommendations | ✅ |
| FRESH-004 | Advisory-only boundary preserved | Output is observation and recommendation only. No scheduling, dispatch, or mutation. Verified: output contains no action fields. | ✅ |
| FRESH-005 | Multi-project validation passes | QA-Pilot (current, minimal), Librarian (current, minimal). No cross-project contamination. Independent assessments. | ✅ |
| FRESH-006 | LINK readiness contract defined | `contracts/assurance/link-readiness-contract.md` — defines `get_project_assurance_state()` and `get_fleet_assurance_state()` interfaces | ✅ |
| FRESH-007 | CAG validation passes | Capability activated through: implemented + validated + evidence-backed + registered + projected + discoverable + authority-bounded = operational | ✅ |
| FRESH-008 | Existing validators pass | No regressions from #223 baseline | ✅ |

## 5. Guardrails

| Guardrail | Rule |
|-----------|------|
| Advisory discovery only | Not orchestration, not remediation, not prioritization |
| Freshness ≠ Quality | Never conflate evidence age with evidence correctness |
| No automated action | System recommends; Owner decides |
| No LINK integration | Define interface only. LINK consumes later. |
| No fleet orchestration | Per-project assessment, not cross-project coordination |
| Authority boundary | Discovery observes; it does not schedule or dispatch |

## 6. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-FLEET-FRESHNESS-DISCOVERY-1.md` | This sprint document |
| `contracts/assurance/fleet-freshness-policy.md` | Freshness policy contract |
| `contracts/assurance/link-readiness-contract.md` | LINK readiness interface contract |
| `scripts/discover-fleet-freshness.py` | Discovery engine |
| `data/runtime-evidence/discovery-projection.json` | Discovery projection index |

## 7. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #224 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 8. Sequencing After This Sprint

```
#221 Capture          ✅
#222 Qualification    ✅
#223 Federation       ✅
#224 Freshness        ← THIS SPRINT
#225 Risk Prioritization  future
#226 LINK Integration     future
#227 Planning Feedback    future
```

## 9. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-RUNTIME-EVIDENCE-FEDERATION-1 (#223) | ✅ Complete |
| Federation engine (`scripts/federate-runtime-evidence.py`) | ✅ Working |
| Qualification engine (`scripts/qualify-runtime-evidence.py`) | ✅ Working |
| Per-project evidence stores | ✅ 2 projects |
| Discovery metadata | ✅ `discovery.json` |
