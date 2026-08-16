# QA-Pilot Mission/Capability Reconciliation

**Document type:** State reconciliation and mission boundary  
**Authority:** Owner-decided  
**Status:** ✅ **Owner-decided 2026-08-15**  
**Date:** 2026-08-15  
**Revised:** 2026-08-15 (mission identity updated with compiler + training evidence)

---

## Purpose

This document reconciles QA-Pilot's declared mission with its implemented capabilities. It is not a roadmap. It does not authorize implementation. It establishes what QA-Pilot is, what evidence supports that claim, what capabilities exist at what maturity, and what architectural direction is authorized next.

The conclusion is not that QA-Pilot failed. The conclusion is that QA-Pilot successfully built a governance and assurance substrate. During execution, the center of gravity moved from training platform implementation toward assurance infrastructure. The declared mission and implemented capability set now require reconciliation.

---

## 1. Mission Identity Decision

QA-Pilot was launched with a dual mission: learning platform and assurance framework. During 215 sprints of execution, the repository's actual architecture diverged from this dual identity. The reconciliation required resolving that fork explicitly.

### ~~Option A — Two independent products (original framing)~~

```
QA-Pilot
├── Learning Platform (independent)
└── Assurance Engine (independent)
```

This framing was incorrect. It assumed the training platform was shallow and the assurance engine was real. New evidence shows both are real — the browser-app is a functional training platform with course delivery, quizzes, progress tracking, capstone scoring, and admin tools. The training system pipeline has schemas, validators, and provenance tracking. The missing piece is integration, not capability.

### ~~Option B — Assurance engine replaces training~~

This was the initial assessment. It is no longer valid given the evidence that the training platform is genuinely operational.

### ✅ Option A (Revised) — Dual mission with assurance engine as spine

**Owner Decision:** QA-Pilot is a governed assurance and learning system, with the assurance engine as the architectural foundation and the training platform as a first-class consumer of assurance outputs.

```
QA-Pilot
                Governance Substrate
                        │
                        ▼
              Assurance Engine Core
                        │
      ┌─────────────────┴─────────────────┐
      ▼                                   ▼
 Independent Qualification          Learning Platform
      │                                   │
 Findings / Evidence                  Courses
      │                                   │
      └─────────────────┬─────────────────┘
                        ▼
             Improvement Feedback Loop
```

The learning system is not competing with the assurance engine. It is the human capability-development layer around it. The assurance engine discovers capability gaps. The learning platform converts them into targeted learning. Performance data feeds back to improve qualification. This is a closed-loop assurance system.

**Architectural foundation:** Assurance Engine  
**First-class product surfaces:** (1) Independent Assurance (2) Learning and Capability Development  
**Training role:** Consumer and feedback loop of assurance outputs

---

## 2. Capability Truth Table

The manifest currently declares 14 capabilities as "stable." This is inaccurate. The following table replaces the binary "stable/unstable" classification with a granular maturity model.

### Maturity Levels

| Level | Meaning |
|-------|---------|
| **Operational** | Real capability, demonstrated, general-purpose |
| **Demonstrated** | Works in a bounded case, not yet generalized |
| **Partial** | Exists but does not meet the implied mission |
| **Missing** | Architecture exists, implementation absent |
| **Obsolete** | Superseded by later work, no longer relevant |

### Capability Inventory

#### Governance & Infrastructure (Operational)

| Capability | Implementation | Validation | Maturity | Scope | Limitations |
|------------|---------------|------------|----------|-------|-------------|
| custody | implemented | validated | **operational** | full lifecycle | advisory-only by design |
| receipts | implemented | validated | **operational** | file-backed store | no distributed receipts |
| evidence_store | implemented | validated | **operational** | evidence intake + SDK | read-only SDK |
| workbench | implemented | validated | **operational** | full CLI surface | no web UI |
| validation_pipeline | implemented | validated | **operational** | 71 validators, ~800 rules | self-validation only |
| owner_review_surfaces | implemented | validated | **operational** | 7 review surfaces | advisory-only |
| advisory_chain | implemented | validated | **operational** | 6-layer EP→TC→QR→ERS→PH→DR | no enforcement |
| broker | implemented | validated | **operational** | cross-project MCP | read-only |
| receipt_store | implemented | validated | **operational** | file-backed | no query language |
| work_queue | implemented | validated | **operational** | diagnostic findings → proposals | Tier 2 blocked |
| assurance_contracts | implemented | validated | **operational** | 5 contracts + schema | no contract executor |

#### Independent Qualification (Demonstrated)

| Capability | Implementation | Validation | Maturity | Scope | Limitations |
|------------|---------------|------------|----------|-------|-------------|
| independent_qualification | demonstrated | demonstrated | **demonstrated** | SNA epic: 68 tests, 9 layers | manually constructed, not generalized |
| adversarial_testing | demonstrated | demonstrated | **demonstrated** | 6 critical scenarios | pattern proven, not automated |
| cross_system_evidence | demonstrated | demonstrated | **demonstrated** | SNA vs QA-Pilot comparison | single case |

#### Training Platform (Partial)

| Capability | Implementation | Validation | Maturity | Scope | Limitations |
|------------|---------------|------------|----------|-------|-------------|
| training_sim | implemented | validated | **partial** | case generation only | no runtime, no feedback loop |
| learning_objects | implemented | validated | **partial** | template-based generation | no semantic evaluation |
| scenario_adapter | implemented | validated | **partial** | 5 ported scenarios | hardcoded, not dynamic |
| ai_qualification | implemented | validated | **partial** | 6 dimensions, keyword scoring | no behavioral evaluation |
| training_packages | implemented | validated | **partial** | template-based generation | no LLM-aware content |
| browser_app | implemented | partially validated | **partial** | Win11 visual shell | may lack underlying app logic |

#### Testing Domains (Missing)

| Capability | Implementation | Validation | Maturity | Scope | Limitations |
|------------|---------------|------------|----------|-------|-------------|
| browser_testing | missing | unvalidated | **missing** | headless/CI browser | requires Playwright |
| accessibility_evaluation | missing | unvalidated | **missing** | WCAG compliance | requires axe-core |
| performance_measurement | missing | unvalidated | **missing** | load/render/runtime | requires Lighthouse |
| security_scanning | missing | unvalidated | **missing** | automated security analysis | requires specialized tools |
| sdk_integration | missing | unvalidated | **missing** | evidence SDK queries | requires local server |
| model_evaluation | missing | unvalidated | **missing** | AI behavior evaluation | requires evaluation framework |

#### Generalized Assurance (Missing)

| Capability | Implementation | Validation | Maturity | Scope | Limitations |
|------------|---------------|------------|----------|-------|-------------|
| qualification_compiler | missing | unvalidated | **missing** | contract → test suite | architectural center |
| generic_adapter | missing | unvalidated | **missing** | any-project discovery | requires compiler |
| continuous_qualification | missing | unvalidated | **missing** | drift detection, re-qualify | requires compiler + trigger |

---

## 3. Mission Gap Statement

**QA-Pilot has completed the construction of an assurance substrate but has not completed the construction of a generalized assurance compiler.**

This separates what was built from what was declared:

| Layer | State |
|-------|-------|
| Governance foundation | Built and operational |
| Evidence infrastructure | Built and operational |
| Review and disposition machinery | Built and operational |
| Independent qualification (specific) | Demonstrated (SNA: 67/68) |
| Independent qualification (general) | Not built |
| Training platform (specific) | Partial (templates exist) |
| Training platform (general) | Not built |

The governance substrate is substantially ahead of the mission compiler. The infrastructure is prerequisite to the compiler, not wasted effort. But the compiler — the thing that transforms contracts into executable verification — is the missing architectural center.

---

## 4. Architectural Center

The next architectural primitive is the Qualification Compiler. Everything else follows from it.

```
              Project Artifact
                     │
                     ▼
             Contract Extraction
                     │
                     ▼
              Qualification IR
                     │
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
Workflow Tests  Adversarial Tests  Evidence Rules
    │                │                │
    └────────────────┼────────────────┘
                     ▼
            Qualification Runtime
                     │
                     ▼
            Independent Conclusion
```

Derivative capabilities become inputs to or triggers around the compiler:

- **Generic adapters** → inputs to the compiler (project discovery)
- **Continuous qualification** → trigger around the compiler (seal event → re-qualify)
- **Browser/security/performance** → compiler target domains
- **Training** → either a compiler output (learning objects from findings) or a separate product

---

## 5. Evidence Basis

This reconciliation is supported by:

| Evidence | What it proves |
|----------|---------------|
| SNA independent qualification (67/68) | Independent assurance discovers defects outside target's own test boundary |
| Capability registry gap assessment | 6 missing capabilities honestly documented |
| FEATURE-STATUS.md | 68+ sealed sprints, all governance/infrastructure |
| Sprint ledger | 215 sprints, 105 required-for-operational-v1 all sealed |
| SESSION-HANDOFF.md | Active work is cross-project dependency, not QA-Pilot implementation |
| Manifest vs. capability registry contradiction | "stable" claims vs. honest gap assessment |
| Training system seal without runtime | Sealed ≠ mission-complete |
| Browser-app migration state | Visual shell may lack application logic |

---

## 6. Governance Decision

### State Summary (Updated 2026-08-15)

| Surface | State | Evidence |
|---------|-------|----------|
| Sprint ledger | **COMPLETE** | All 105 required sprints sealed |
| Governance substrate | **OPERATIONAL** | 11 operational capabilities, custody/receipts/review/contracts |
| Independent qualification | **DEMONSTRATED** | SNA: 67/68, 9 layers, 1 finding missed by target's own tests |
| Qualification compiler | **IMPLEMENTED** | IR schema + compiler + evidence generation. 36 tests from SNA IR |
| Training platform | **OPERATIONAL** | Browser-app: courses, quizzes, progress, capstone, admin. Pipeline: schemas, validators, packages |
| Training integration | **INCOMPLETE** | Pipeline generates packages browser-app doesn't read; browser-app generates data pipeline doesn't consume |
| Generic qualification | **PARTIAL** | 2 adapters, not generalized |
| Continuous qualification | **NOT IMPLEMENTED** | No trigger mechanism |
| Mission readiness | **ADVANCING** | Two real capability streams, missing integration layer |

### Disposition

1. **QA-Pilot ledger status:** Complete
2. **QA-Pilot governance substrate:** Operational
3. **QA-Pilot independent qualification capability:** Demonstrated
4. **QA-Pilot qualification compiler:** Implemented (IR → suite → evidence)
5. **QA-Pilot training platform:** Operational (both browser-app and pipeline)
6. **QA-Pilot training integration:** Incomplete (bridge needed)
7. **Mission identity:** Option A (Revised) — dual mission, assurance engine as spine

### Build Priority (Revised)

| Priority | Item | Rationale |
|----------|------|-----------|
| **P0** | Training pipeline ↔ browser-app bridge | Completes the feedback loop. Without it, assurance findings can't become learning, and learning data can't improve qualification |
| **P1** | Generic Adapter Framework | Makes the qualification compiler work for any project |
| **P1** | Compiler assertion expansion | Replace placeholder tests with real implementations |
| **P2** | Continuous Qualification trigger | Event-driven re-qualification |
| **P2** | Training: adaptive paths, sim activation | Operational maturity for learning platform |

---

## Appendix: The Proof Point (Updated)

The 67/68 independent qualification result is not just another test artifact. It is empirical evidence that:

1. Independent assurance can discover defects outside the target system's own test boundary
2. The contract-to-qualification pattern works (6 invariants → 68 tests → 1 finding)
3. The governance substrate (custody, receipts, evidence, review) is sufficient to support independent qualification
4. The missing piece is generalization, not capability

The qualification compiler now exists as an implemented transformation (IR → suite → evidence). The remaining gap is the feedback loop: qualification → findings → learning objects → training delivery → performance data → qualification improvement.

This closed-loop system — governed assurance that discovers capability gaps and converts them into targeted learning and verification loops — is the differentiated capability that neither a standalone QA system nor a standalone LMS provides.

---

## Appendix: Revised Mission Identity (Owner-Decided)

```
QA-Pilot is a governed assurance and learning system,
with the assurance engine as the architectural foundation
and the training platform as a first-class consumer
of assurance outputs.
```

**Architectural foundation:** Assurance Engine  
**First-class surfaces:** (1) Independent Assurance (2) Learning and Capability Development  
**Training role:** Consumer and feedback loop of assurance outputs  
**Integration priority:** Complete the bridge between assurance findings and learning delivery
