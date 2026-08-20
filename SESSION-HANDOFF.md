# Session Handoff — Active Direction

## Current Epic: EPIC-ASSURANCE-CONTRACT-EVOLUTION-1

**Status:** ✅ **DIRECTED — Owner-directed 2026-07-21**
**Phase:** Phase 4 — Contract extraction
**Objective:** Convert adoption evidence into stable assurance contracts without prematurely generalizing implementation-specific concepts. Complete the adoption discipline: Observe → Measure → Classify → Generalize.

## Previous Epic: EPIC-ASSURANCE-OPERATIONS-ADOPTION-1

**Status:** ✅ **COMPLETE — All 4 phases sealed**
**Milestone completed:** Adoption epic complete — model survived all 4 consumer shapes.
**Phase transition:** Adoption → Contract extraction

| Phase | Consumer | Shape | Key Finding | Sprint |
|-------|----------|-------|-------------|--------|
| Phase 1 | Librarian | Governance/documentation | Semantic portability — model generalizes beyond origin | #207 |
| Phase 1b | Librarian adapters | Projection adaptation | Adapter pattern confirmed | #208 |
| Phase 2 | Agent Bridge | Runtime/integration | Operational portability — compound identity gap | #209 |
| Phase 3 | Runtime Node | Hardware/operational | Evidence model boundary — artifact vs runtime evidence | #210 |

## Epic: EPIC-ASSURANCE-CONTRACT-EVOLUTION-1

**Status:** ✅ **PHASE 4 COMPLETE — All 4 phases sealed 2026-07-27**
**Type:** contract extraction
**Lane:** assurance
**Boundary:** QA Pilot-local (reads all 3 consumer projects)
**Librarian impact:** contract_interface (Phase 4 scope)
**Dependencies:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (complete)

**Purpose:** Convert adoption evidence into stable assurance contracts without prematurely generalizing implementation-specific concepts.

**Contract extraction:** Complete. All 9 identified surfaces evaluated against evidence corpus.

### Phase 4 Extraction Outcome

| Category | Surface | Disposition |
|----------|---------|-------------|
| **Promoted to contract** | Evidence state | `contracts/assurance/evidence-contract.md` |
| | Finding derivation | `contracts/assurance/finding-contract.md` |
| | Remediation lifecycle | `contracts/assurance/remediation-contract.md` |
| | Owner decision boundary | `contracts/assurance/owner-decision-contract.md` |
| | Regression lifecycle | `contracts/assurance/regression-contract.md` |
| **Evaluated — covered** | Custody invariants | Existing #215 contracts sufficient |
| **Evaluated — local behavior** | Finding lifecycle states | QA Pilot-local implementation, not universal |
| **Deferred** | Verification sufficiency | No completed remediation evidence |
| | Learning → regression | No verified fixes exist |

### Disposition Record — Visual Parity Epic (#153–#155)

| Sprint | Disposition | Reason |
|--------|------------|--------|
| #153 Reference audit | ✅ Sealed | One-time analysis — mismatch matrix (M1-M10) is durable reference evidence |
| #154 Landing shell remediation | ✅ Closed (superseded) | Implementation applied to pre-migration surface, overwritten by migration (#157), not restored |
| #155 Admin/learner remediation | ✅ Closed (superseded) | Implementation applied to pre-migration surface, overwritten by migration, not restored. Execution against incomplete browser shell noted but secondary to surface replacement |

**Note:** Visual parity intent remains unfulfilled at the canonical surface level. The current `browser-app/` retains original design language (blue hero, emoji, uniform cards, no source-chips). If Librarian visual parity is desired, it requires a new implementation pass against the canonical surface.

### Disposition Record — Post-Canonical Reassessment

| Sprint | Disposition | Reason |
|--------|------------|--------|
| QA-PILOT-POST-CANONICAL-SURFACE-REASSESSMENT-1 | ✅ Closed (absorbed) | Original purpose fulfilled by subsequent sealed validation: frontend roundtrip validation (#135), post-migration I18N (#170-#177), canonical surface governance rule. Reassessment is now a repeatable assurance operation.

### Disposition Record — I18N Epic (#148–#152)

| Sprint | Disposition | Reason |
|--------|------------|--------|
| #148 I18N baseline | ✅ Sealed | Historical baseline evidence — analysis that informed later work |
| #149 Core dictionary | ✅ Closed (superseded) | Implementation replaced by #170/#171/#173 |
| #150 Page wiring | ✅ Closed (superseded) | Wiring replaced by post-migration #170/#171 |
| #151 Rerender/state | ✅ Closed (superseded) | Behavior re-established by later implementation |
| #152 Roundtrip validation | ✅ Closed (superseded) | Validation target replaced; current validation at #135 |

**Governance rule derived:** `docs/governance/CANONICAL-SURFACE-VALIDATION-RULE.md` — A completed work item may only be sealed as a current implementation artifact if the validated surface remains the canonical target.

### Architecture Boundary Established

```
Universal Assurance Layer
├── Evidence contract
├── Finding derivation contract
├── Remediation contract
├── Owner decision contract
└── Regression contract

Consumer Operational Layers (NOT universal)
├── QA Pilot finding lifecycle (local)
├── Librarian execution lifecycle (local)
├── Agent Bridge artifact lifecycle (local)
└── Runtime Node lifecycle (local)
```

The invariant is not "every consumer has the same workflow." The invariant is: "every consumer participates in the same governed evidence and authority boundaries."

### Remaining Gap

The assurance model is complete enough for operational use. The remaining blocker is **execution activation** — not assurance definition. The deferred surfaces (verification, learning→regression) require an operational loop: Finding → Owner Decision → Work Proposal → Work Packet → Execution → Verification Evidence → Regression Learning.

**Extraction pipeline:**
```
Evidence Corpus
    |
    v
Repeated Observation
    |
    v
Cross-Consumer Comparison
    |
    v
Invariant Candidate
    |
    v
Contract Candidate
    |
    v
Formal Assurance Contract
```

**The invariant test:** Single consumer observation ≠ contract candidate. Multiple consumer shapes + stable behavior independent of implementation = contract candidate.

**Classification buckets for each pattern found:**
| Classification | Meaning | Action |
|---------------|---------|--------|
| Local behavior | Specific to one consumer or implementation | Retain as evidence only |
| Repeated practice | Appears multiple times but lacks universal boundary | Continue observing |
| Stable invariant | Survives across shapes and contexts | Promote into contract |

**Extraction ordering (evidence-driven — revised 2026-07-27):**

| Surface | Status | Reason |
|---------|--------|--------|
| Evidence state | ✅ Complete | #215 |
| Finding derivation | ✅ Complete | #215 |
| Remediation lifecycle | ✅ Complete | #215 |
| Owner decision boundary | ✅ Complete | #215 |
| Regression lifecycle model | ✅ Complete | #215 |
| Custody invariants | ✅ Evaluated | Covered by existing contracts — no new contract |
| Verification sufficiency | ⏸ Deferred | No completed remediation evidence in corpus |
| Learning → regression | ⏸ Deferred | No verified fixes exist; requires P1 first |
| Finding lifecycle states | 🔍 Candidate | Corpus: 17 OPEN, 0 transitions. Expected outcome: no invariant unless non-state lifecycle behavior survives cross-consumer test |

**Note on test ownership (governance rule — not a contract):**
- A test belongs in QA Pilot when its failure means "the governed system violated an assurance contract."
- A test belongs in the implementation repo when its failure means "this component does not function correctly."
- This prevents QA Pilot from becoming a second copy of every project's test suite while preserving it as the assurance verification plane.

**Constraint:** A contract should only exist because the evidence corpus demonstrates a stable invariant, not because the system would benefit from having one.

**Phase 4 extraction categories:**
| Category | Status |
|----------|--------|
| Proven from evidence → Formal contracts | #215 (5 contracts) |
| Not yet proven → Deferred | Verification sufficiency, finding lifecycle, learning→regression |
| Ready for extraction | Custody invariants |

Librarian work packet service (P1) is a separate parallel track — no dependency inversion required. QA Pilot Phase 4 asks "what must be true?"; Librarian asks "how is authorized work executed?"

**Key decisions:**

| Decision | Priority | Status | Source |
|----------|----------|--------|--------|
| `assurance_record` vs `assurance_snapshot` | HIGH — evidence-backed | ✅ Extracted as contract | Runtime Node (#210) |
| Evidence freshness semantics | HIGH | ✅ Extracted as contract | Cross-cutting |
| QA Pilot → Librarian work proposals | HIGH | ✅ Interface defined (#214), blocked by P1 | #214 |
| Compound identity | MEDIUM | Observation — not promoted to contract | Agent Bridge (#209) |
| Runtime-specific adapters | LOW | Covered by adapter boundary pattern | Cross-cutting |

**Adoption discipline:** Observe → Measure → Classify → Generalize

## Previous Epic: EPIC-ASSURANCE-OPERATIONS-ADOPTION-1

**Status:** ✅ **COMPLETE — All 6 sprints sealed (#201–#206)**
**Milestone completed:** QA-PILOT-ASSURANCE-OPERATING-LAYER-1 (#166–#200)
**Current phase:** Pre-sprint (baseline reconciliation ready — entry gate)
**Awaiting:** `authorize sprint QA-PILOT-CANONICAL-ASSURANCE-BASELINE-RECONCILIATION-1` to begin Sprint 201

---

## Epic Summary

**Type:** assurance operations integration (5 sprints planned)
**Lane:** assurance
**Boundary:** QA Pilot-local
**Librarian impact:** none (integration_interface for Phase 2)

**Purpose:** Demonstrate that the QA Pilot assurance operating layer functions continuously across projects, surfaces, evidence sources, and Owner decisions. Transition from building assurance primitives to proving the assurance loop operates at scale.

**Entry condition:** Milestone QA-PILOT-ASSURANCE-OPERATING-LAYER-1 recorded as COMPLETE (scope #166–#200).

### Authorized Sprint Sequence

| Sprint | Purpose | Status |
|--------|---------|--------|
| QA-PILOT-CANONICAL-ASSURANCE-BASELINE-RECONCILIATION-1 | Freeze post-#200 baseline, verify lifecycle chain integrity, establish metrics | ✅ SEALED (#201) |
| QA-PILOT-ASSURANCE-LAYER-REGISTRY-RECONCILIATION-1 | Pre-dashboard data reconciliation — registry extended through slot 201, health baselines regenerated | ✅ SEALED (#202) |
| QA-PILOT-OWNER-DASHBOARD-INTEGRATION-1 | Expose assurance state through Owner-facing governance surface | ✅ SEALED (#203) |
| QA-PILOT-PROJECT-ASSURANCE-ROUTING-1 | Multi-project assurance routing | ✅ SEALED (#204) |
| QA-PILOT-ASSURANCE-CALIBRATION-1 | Operational calibration — measure false positives, stale state, decision queue, evidence freshness, projection accuracy | ✅ SEALED (#205) |
| QA-PILOT-ASSURANCE-GOVERNANCE-MATURITY-1 | Institutionalize operating model — policies, maturity criteria, cadence, lifecycle ownership, drift detection | ✅ SEALED (#206) |
| QA-PILOT-PROJECT-ASSURANCE-ROUTING-1 | Multi-project assurance routing | ✅ SEALED (#204) |
| QA-PILOT-ASSURANCE-CALIBRATION-1 | Operational calibration over sustained activity | Planned (Phase 3) |
| QA-PILOT-ASSURANCE-GOVERNANCE-MATURITY-1 | SLAs, trends, scorecards, release gates | Planned (Phase 4) |

### Sprint Resolutions

| Previous Sprint | Resolution |
|----------------|-----------|
| QA-PILOT-CANONICAL-BASELINE-AUDIT-1 | 🔄 Reclassified → QA-PILOT-CANONICAL-ASSURANCE-BASELINE-RECONCILIATION-1 (entry gate for new epic) |
| QA-PILOT-POST-CANONICAL-SURFACE-REASSESSMENT-1 | ⏸️ Deferred into EPIC-QA-PILOT-ASSURANCE-OPERATIONS-INTEGRATION-1 Phase 2 |

---

## Milestone: QA-PILOT-ASSURANCE-OPERATING-LAYER-1

**Status:** ✅ **COMPLETE — Recorded 2026-07-20**
**Scope:** #166–#200
**Classification:** Capability milestone
**Location:** `reports/QA-PILOT-ASSURANCE-OPERATING-LAYER-1-MILESTONE.md`

**Outcome:** QA Pilot now contains an operational assurance layer capable of transforming findings into governed lifecycle decisions through evidence-backed validation, risk prioritization, Owner decision control, and continuous assurance management.

**Notable sprints in scope:**
- #178–#184: Testing, regression, UAT, a11y, performance, security capabilities
- #185–#194: Assurance profiles, continuous assurance loop, evidence lineage, risk prioritization, history recorder
- #195–#198: Automation refinement, release governance, enterprise packs, model-assisted
- #199–#200: Finding lifecycle architecture and implementation (capstone)

---

## Previous Epics (Sealed — Historical)

### EPIC-QA-PILOT-OPENWORK-TO-CARBIDEFRAME-MIGRATION-1 — Sealed (#156–#160)

**Type:** migration (5 sprints)
**Status:** ✅ Sealed — all 5 sprints sealed. Migration work complete.
**Note:** Migration-source canonical promotion decision superseded by assurance operations integration direction.

### EPIC-QA-PILOT-DESIGN-QUALITY-REGRESSION-1 — Sealed (#143–#147)

**Type:** design / accessibility remediation
**Status:** ✅ Sealed — Owner-approved 2026-07-09.
**Scope:** Keyboard nav, focus, semantics, landmarks, form labels, contrast, i18n toggle, responsive media queries across all 8 pages.

### EPIC-QA-PILOT-DESIGN-LANGUAGE-REFRESH-1 — Sealed (#136–#142)

**Type:** design language convergence (7 sprints)
**Status:** ✅ Sealed.

### EPIC-QA-PILOT-TRAINING-SYSTEM-1 — Sealed (#106–#116)

**Type:** training system (11 sprints)
**Status:** ✅ Sealed.
**Scope:** Training data browser, pipeline, execution, report builder, admin dashboard, review surface, simulator.

### EPIC-QA-PILOT-BROWSER-ONLY-DEPLOYMENT-AND-STARTUP-1 — Sealed (#92–#100)

**Type:** deployment and startup surface (9 sprints)
**Status:** ✅ Sealed.

### EPIC-QA-PILOT-BROWSER-ONLY-REAL-WORLD-PILOT-1 — Sealed (#87–#91)

**Type:** browser-only real-world pilot (5 sprints)
**Status:** ✅ Sealed.
**Scope:** Risk-based review depth, decision packet, startup surface.

### EPIC-QA-PILOT-ORIGINAL-FRONTEND-MIGRATION-1 — Sealed (#125–#134)

**Type:** frontend migration (10 sprints)
**Status:** ✅ Sealed.

### EPIC-QA-PILOT-APP-SURFACE-MIGRATION-1 — Merged into ORIGINAL-FRONTEND

**Note:** Single sprint (#117) absorbed into the frontend migration epic.

---

## Re-scoped / Paused Epics (Historical)

**EPIC-QA-PILOT-LIBRARIAN-VISUAL-PARITY-CORRECTION-1** — 🚫 Re-scoped 2026-07-10.
**EPIC-QA-PILOT-I18N-WIRING-1** — ⏸️ Deferred by Owner 2026-07-09.

---

## Active Project State

**Ledger updated:** 2026-08-17
**Latest sealed sprint:** #220 QA-PILOT-REGRESSION-LEARNING-LOOP-1
**Latest completed sprint:** P7.1-TEST-001 Cross-Layer Governance Validation (19/19 PASS)
**Active epic:** Phase 7 — Adoption & Empirical Validation (P7.1 Cross-Project Trial)
**Qualification substrate:** COMPLETE — all 5 sprints sealed (#216–#219 + #165 roundtrip)
**Learning loop:** COMPLETE — end-to-end improvement loop proven (#220)
**Governance vocabulary:** COMPLETE — canonical five-dimensional model established (LVC-001)
**Runtime qualification:** COMPLETE — qualification operates against canonical state (GPI-001)
**Controlled validation:** COMPLETE — governance/qualification composition verified (P7.1-TEST-001)
**End-to-end loop dependency:** SATISFIED — Librarian work packet service discovered as existing sprint #546; capability projection activated. Tier 2 gates WQI-005/WQI-006 unblocked.
**Authorized sprints:** LVC-001 + GPI-001 + P7.1-TEST-001 COMPLETE. P7.1-OPS-001 RECORDED (finding, not yet authorized for execution).
**Deferred sprints:** Framework Validation, I18N reassessment, visual parity reassessment, post-canonical surface reassessment

## P7.1 Operational Findings

**P7.1-OPS-001 — Project Session Availability**

During this session, the agent attempted to close the Librarian session and received "session tools unavailable." The agent fell back to direct file editing. This is the first real P7.1 operational finding.

The gap is a project registration → session binding → MCP/tool exposure path, not a governance architecture primitive. The project needs a Librarian session interface, not a local Librarian implementation.

Absence of the session interface must not cause silent fallback to unmanaged direct operation when the work is declared governed.

Recorded at `work-orders/P7.1-OPS-001-project-session-availability.md`. Awaiting Owner direction.

**LIBRARIAN-QA-CAPABILITY-ACTIVATION-001 — Capability Activation Audit**

Cross-system capability activation audit. Phase 1 baseline + Phase 2 characterization complete.

Key finding: The system is not primarily dead code. Implementation maturity exceeds activation maturity. 55% ACTIVE, 18% AVAILABLE, 9% BROKEN, 5% UNWIRED.

Root cause: `GeneratedMCPDispatchMap.swift` single-point defect — all tools have `handlerFunction: "unknown"`. Affects 7+ broken MCP tools.

Authorization flow (B2) unwired — three competing implementations, OwnerDecision never injected upstream.

Remediation candidates P0–P3 established. Awaiting Owner decision.

Recorded at `audits/capability-activation-audit-2026-08-17.md` and `work-orders/CAPABILITY-ACTIVATION-AUDIT-001.md`.

## Sealed Sprint: ASSURANCE-CONTRACT-EVIDENCE-STATE-CONTRACT-FORMALIZATION-1 (#215)

**Status:** ✅ **SEALED — Owner-sealed 2026-07-27**
**Epic:** EPIC-ASSURANCE-CONTRACT-EVOLUTION-1 Phase 4 (Contract extraction)
**Purpose:** Convert the four sealed adoption baselines (#207–#210) from evidence collections into canonical assurance contracts. Extract the invariants that survived across all 4 consumer shapes.
**Deliverables:** 5 contract artifacts under `contracts/assurance/`:
- `evidence-contract.md` — Canonical evidence object (2-class record/snapshot model)
- `finding-contract.md` — Finding derivation (3-layer evidence/finding/recommendation separation)
- `remediation-contract.md` — Remediation lifecycle (7-state model with provenance)
- `owner-decision-contract.md` — QA Pilot ≠ Authority (9 MUST NOT rules, mechanically testable)
- `regression-contract.md` — Regression guard lifecycle
- `assurance-contracts.schema.json` — Machine-checkable schema with authority enforcement
- `CROSS-CONSUMER-VOCABULARY-MATRIX.md` — Proves 10 universal invariants
**Acceptance gates:** 10/10 PASS (CF-1 through CF-10)
**Architectural milestone:** QA Pilot transitioned from evidence-producing subsystem to contract-governed assurance subsystem. Assurance behavior is now represented as enforceable contracts rather than accumulated observations.

## Sealed Sprint: QA-PILOT-LIBRARIAN-WORK-QUEUE-INTEGRATION-1 (#214)

**Status:** ✅ **SEALED — Owner-sealed 2026-07-24**
**Purpose:** Create governed bridge from QA-Pilot diagnostic findings to Librarian-compatible work proposals. Proposal artifact, not work packet. QA-Pilot-local execution. Tier 1/Tier 2 acceptance split.
**Key invariant:** QA-Pilot detects and proposes. It does not call Librarian work packet MCP tools. It does not create work packets. It does not authorize, dispatch, or execute anything.
**Tier 1 gates (QA-Pilot-owned):** WQI-001, WQI-002, WQI-003, WQI-004, WQI-007, WQI-008 — all PASS
**Tier 2 gates (blocked):** WQI-005, WQI-006 — blocked pending LIBRARIAN-WORK-PACKET-SERVICE-ACTIVATION-1 (not yet created)
**Test results:** 19/19 tests pass, validator passes all Tier 1 gates including WQI-008 (fail-closed regression gate)
**MCP diagnostic trail:** Librarian work packet bridge probed during authorization — `work_packet_service_available: false`, `bridge_status: degraded`. MCP tool surface is routable but backing service is not operational. This is the contract-first approach: interface exists ahead of capability. The diagnostic trail itself is QA-Pilot evidence of the missing Librarian operational layer. WQI-008 captures this as a regression asset.
**Seal note:** Tier 2 gates remain blocked by LIBRARIAN-WORK-PACKET-SERVICE-ACTIVATION-1. Blocking condition is external dependency, not implementation failure.

## Sprint Sequencing (End-to-End Loop)

| Order | Sprint | Side | Status |
|-------|--------|------|--------|
| 1 | ASSURANCE-CONTRACT-EVIDENCE-STATE-CONTRACT-FORMALIZATION-1 | QA-Pilot | ✅ Sealed (#215) |
| 2 | QA-PILOT-LIBRARIAN-WORK-QUEUE-INTEGRATION-1 | QA-Pilot | ✅ Sealed (#214) |
| 3 | LIBRARIAN-WORK-PACKET-SERVICE-ACTIVATION-1 | Librarian | ✅ Discovered — existing sprint #546, capability projection activated |
| 4 | QA-PILOT-REGRESSION-LEARNING-LOOP-1 | QA Pilot | ✅ Sealed (#220) — **Architectural milestone: governed improvement loop proven** |

**Correction (2026-08-15):** Sprint #3 was not missing. Sprint #546 already existed in the Librarian ledger. The apparent blocker was a capability projection discoverability gap, not an implementation gap. The work packet service is now discoverable via MCP capability projection. Tier 2 gates WQI-005/WQI-006 are unblocked.

**Governance lesson:** Sealed history is immutable. New evidence extends understanding; it does not rewrite history. Sprint vs. Extension distinction — a sprint creates evidence history; a capability projection creates discoverability. They are related but not interchangeable.

**Architectural milestone (2026-08-15):** Sprint #220 proves the governed improvement loop. The system can discover, qualify, teach, authorize, and improve from problems while preserving independent authority boundaries. The thesis is no longer theoretical. Next phase: generalization and operational scaling.

## Qualification Substrate Sequence (COMPLETE)

| Order | Sprint | Contract | Status |
|-------|--------|----------|--------|
| 1 | QUALIFICATION-SCHEMA-1 | Qualification Run Record | ✅ Sealed (#216) |
| 2 | QUALIFICATION-EVIDENCE-PIPELINE-1 | Evidence Boundary | ✅ Sealed (#217) |
| 3 | QUALIFICATION-EXECUTION-1 | Runtime Boundary | ✅ Sealed (#218) |
| 4 | QUALIFICATION-REVIEW-SURFACE-1 | Human Authority Boundary | ✅ Sealed (#219) |
| 5 | QUALIFICATION-ROUNDTRIP-VALIDATION-1 | Complete Loop Proof | ✅ Sealed (#165) |

**Complete.** All 5 qualification substrate sprints sealed. The qualification architecture is a closed, repeatable loop: discover → collect → validate → evaluate → lifecycle → review → status → startup → decision → lineage. Advisory-only boundaries confirmed at every layer.

## Deferred Items

| Item | Reason | Future Process |
|------|--------|----------------|
| Framework Validation | Defer until work packet service + qualification substrate complete | Prove "the governed improvement loop works" not just "capabilities exist" — NOW PROVEN by #220 |
| I18N Reassessment (#148–#152) | Paused — needs revalidation post-migration | Historical UI work → Applicability determination → Qualification → PASS/FINDING/NOT APPLICABLE |
| Visual Parity Reassessment | Re-scoped — paused pending migration validation | Same process as I18N |
| Post-Canonical Surface Reassessment | Deferred to Phase 2 | Same process as I18N |

## Phase Transition

**Architecture discovery: COMPLETE** (sprint #220)
**Next phase: Generalization and operational scaling**

The system has crossed from "build missing primitives" into "system integration and operationalization." The governed improvement loop is proven. The next phase makes it scalable, discoverable, and economically selective.

### Authority Model (Preserved)

| Function | Owner |
|----------|-------|
| Build | Agents/projects |
| Evaluate | QA-Pilot |
| Record truth | Librarian |
| Teach | Training system |
| Accept risk | Owner |

The loop works because the evaluator, recorder, teacher, and authority holder are separated. Do not collapse them together.

### Next Maturity Questions (Sequenced)

The system has crossed from "build missing primitives" into "system integration and operationalization." The governed improvement loop is proven. The next phase makes it scalable, discoverable, and economically selective.

**Sequencing principle:** Complete the assurance engine internally, then generalize it externally. Do not build the ecosystem before the boundary contracts are stable.

| Order | Sprint | Purpose | Status |
|-------|--------|---------|--------|
| 1 | QA-PILOT-RUNTIME-EVIDENCE-COMPLETION-1 | Complete QA Pilot's own runtime evidence boundary. Operationalize FlightPlan schemas. 6-identity provenance chain (Execution Identity + Governance Context). | ✅ Complete (#221, all 8 gates PASS) |
| 2 | QA-PILOT-RUNTIME-EVIDENCE-QUALIFICATION-1 | Trust calibration — prove runtime evidence can be evaluated correctly. 5 qualification checks. Qualification profile IR. First non-sprint artifact. | ✅ Complete (#222, all 8 gates PASS) |
| 3 | QA-PILOT-RUNTIME-EVIDENCE-FEDERATION-1 | Identity and boundary sprint — multi-project evidence federation. Canonical project identity. Adapter contract. Per-project isolation. Discovery metadata. | ✅ Complete (#223, all 8 gates PASS) |
| 4 | Fleet Freshness + Discovery | Advisory discovery layer — freshness policy, coverage model, discovery projection, LINK readiness interface. | ✅ Complete (#224, all 8 gates PASS) |
| 5 | Planning Accuracy Loop | Connect runtime evidence to LINK planning. Estimate → Execution → Evidence → Actual Cost → Accuracy → Improved Estimate. | ⏸ Deferred |

**Key insight:** You cannot measure planning accuracy without reliable execution evidence. Runtime evidence must be stable before LINK integration.

### Scaling Architecture (Target State)

```
Runtime Observation
        ↓
Qualification Context
        ↓
Risk Signal
        ↓
Planning Decision
```

Without runtime evidence, LINK and FlightPlan only know declared state.
With runtime evidence, they can reason about observed behavior.

### Current Phase State

```
PHASE 7 — ADOPTION & EMPIRICAL VALIDATION

P7.1 Cross-Project Trial                    IN PROGRESS
  └── LVC-001 Vocabulary Consolidation      ✅ Complete (16/16 gates PASS)
  └── WP-003B Completion                    ✅ Complete (vault + bibliography)
  └── GPI-001 Runtime Qualification         ✅ Complete (15/15 gates PASS)
  └── P7.1-TEST-001 Validation Suite        ✅ Complete (19/19 tests PASS)
  └── P7.1:      CONTINUES — awaiting operational evidence
```

### Phase 6 Complete — Architecture Freeze

**Phase 6 is COMPLETE.** No more architecture-building sprints until Phase 7 adoption/validation demonstrates concrete unmet requirements.

**The governed improvement lifecycle is now mechanically demonstrable:**

```
Problem Discovery
       ↓
Assurance
       ↓
Recommendation
       ↓
Owner Decision
       ↓
Governed Change
       ↓
Evidence
       ↓
Outcome Measurement
       ↓
Learning Signal
       ↓
Improved Future Decisions
```

**No arrow from Learning directly into Authority.** That is the architectural property preserved.

### Phase 7 — Adoption & Empirical Validation

**Objective:** Determine whether the completed QA-Pilot lifecycle produces reliable, useful, and repeatable decision support when applied to real governed work across multiple projects.

**The test is no longer:** "Can QA-Pilot do this?"
**The test is:** "Does doing this improve governed engineering decisions enough to justify continued operation?"

### Architecture Freeze Governance Rule

During Phase 7:

**No new QA-Pilot assurance primitive may be introduced solely because a theoretically desirable capability has been identified.**

A proposed architectural change requires:

```
Observed operational deficiency
        ↓
Evidence
        ↓
Existing capability assessed
        ↓
Concrete unmet requirement established
        ↓
Owner review
        ↓
Architecture change permitted
```

### Phase 7 Validation Stages

| Stage | Question | Primary Evidence |
|-------|----------|------------------|
| P7.1 | Does the lifecycle operate across projects? | Complete lifecycle traces |
| P7.2 | Does it work with actual evidence? | Runtime/work/evidence records |
| P7.3 | Do recommendations produce useful outcomes? | Recommendation → outcome history |
| P7.4 | Do signals improve decisions? | Decision comparisons / owner outcomes |
| P7.5 | Does accumulated evidence produce meaningful learning? | Cross-project learning signals |
| P7.6 | Is the system ready for sustained use? | Readiness assessment |

### Phase 7 Success Condition

```
QA-Pilot Phase 7
        │
        ├── Real work demonstrated
        ├── Cross-project operation demonstrated
        ├── Evidence provenance demonstrated
        ├── Recommendation effectiveness measured
        ├── Decision utility measured
        ├── Learning validity demonstrated
        ├── Operational economics understood
        └── Authority boundaries preserved
                    │
                    ▼
          ADOPTION READINESS DECISION
```

**Possible outcomes:**
- READY
- READY WITH CONSTRAINTS
- EXTEND VALIDATION
- ARCHITECTURE GAP IDENTIFIED
- NOT READY

### Phase 7 Status

| Stage | Status |
|-------|--------|
| P7.1 Cross-Project Trial | ✅ IN PROGRESS |
| P7.2 Real-Work Evidence | Ready |
| P7.3 Recommendation Effectiveness | Ready |
| P7.4 Decision Utility | Ready |
| P7.5 Fleet Learning | Ready |
| P7.6 Adoption Review | Ready |

**Phase 7 Authorization:** ✅ Owner-authorized 2026-08-17
**Current Stage:** P7.1 Cross-Project Trial — IN PROGRESS

### Architecture Complete

```
Observation
    ↓
Qualification
    ↓
Assessment
    ↓
Prediction
    ↓
Recommendation
    ↓
Human Decision
```

**Each step reduces uncertainty. No step increases authority.**

### Architecture Complete

```
State
   ↓
Trajectory
   ↓
Risk
   ↓
Value of Attention
   ↓
Human Decision
```

**The complete decision-support stack is now operational.**

### Architecture Milestone

```
                  Governance Substrate
                         │
                         ▼
                 QA-Pilot Assurance
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
  Qualification       Learning        Discovery
       │                 │                 │
       └─────────────────┼─────────────────┘
                         △
                    LINK Context
                         △
                  Better Planning
                         △
                  Better Systems
```

**QA-Pilot has proven its core thesis.**

### Architecture Milestone

```
GOVERNANCE SUBSTRATE
         │
         ▼
ASSURANCE ENGINE
         │
 ┌───────┼───────┐
 ▼       ▼       ▼
Evidence Qualify Risk
 │       │       │
 └───────┼───────┘
         ▼
  LINK Planning Context
         │
         ▼
 Better Human Decisions
         │
         ▼
  Learning Feedback Loop
```

**QA-Pilot has proven its core thesis.**

### What NOT to Do

- Do not add more governance — the governance substrate is doing its job
- Do not collapse authority boundaries — separation is the strength
- Do not treat all artifacts equally — economic prioritization is needed
- Do not require custom engineering for new projects — generalization is needed

## Do Not Touch Unless Asked

- The Librarian repo (active/librarian/)
- Canonical docs without checkout receipt
- Cross-project mutation paths defined in PROJECT-PROFILE.json
- OpenWork source location (/Users/andrew/Desktop/OpenWork/QA Pilot)
- Sealed epic artifacts without explicit Owner direction

## Required Behavior

- Mark agent work 🔍 Pending; never mark ✅ Verified.
- Use deterministic tools/scripts for exact paths, counts, JSON/YAML, markdown slots, custody, and destructive dry runs.
- This is a Python/script project — no web app checks apply.
