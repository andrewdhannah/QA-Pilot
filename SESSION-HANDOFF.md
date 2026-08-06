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

**Ledger updated:** 2026-07-24
**Latest sealed sprint:** #214 QA-PILOT-LIBRARIAN-WORK-QUEUE-INTEGRATION-1
**Active epic:** EPIC-ASSURANCE-CONTRACT-EVOLUTION-1 (Phase 4 — directed)
**Authorized sprints:** none — #214 sealed; Tier 2 dependency on LIBRARIAN-WORK-PACKET-SERVICE-ACTIVATION-1 (not yet created)
**Deferred sprints:** QA-PILOT-POST-CANONICAL-SURFACE-REASSESSMENT-1 (→ Phase 2)
**Future sprint:** QA-PILOT-REGRESSION-LEARNING-LOOP-1 (deferred — requires end-to-end loop operational)

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
| 3 | LIBRARIAN-WORK-PACKET-SERVICE-ACTIVATION-1 | Librarian | Not yet created — activate DB-backed work packet dispatch/intake/verification/closure |
| 4 | QA-PILOT-REGRESSION-LEARNING-LOOP-1 | QA-Pilot | Deferred — verified fixes become reusable regression tests |

Sprints 1-2 (QA-Pilot side) are sealed. The end-to-end loop requires sprint 3 (Librarian). The feedback loop requires both.

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
