# QA Pilot Assurance Maturity Model

**Version:** 1.0
**Effective:** 2026-07-20
**Epic:** EPIC-QA-PILOT-ASSURANCE-OPERATIONS-INTEGRATION-1

---

## Overview

This model defines 5 maturity stages for the assurance operating layer. Each stage has defined criteria, evidence requirements, and a transition gate to the next stage.

## Maturity Stages

### Stage 1: Initial — Capability Construction
*Equivalent: Phases 0–Pre (#166–#200)*

| Criterion | Requirement |
|-----------|-------------|
| Basic assurance capabilities exist | Finding lifecycle, evidence pipeline, risk prioritization |
| Owner can view findings | Raw store access or script |
| Evidence is collected | At least one evidence source operational |
| Pass rate | Validation scripts execute without errors |

**Transition to Stage 2:** All core lifecycle stages produce connected output (AG-1 from Sprint 201).

### Stage 2: Defined — Baseline Established
*Equivalent: Phase 1 (#201)*

| Criterion | Requirement |
|-----------|-------------|
| Canonical baseline exists | Sprint 201 baseline reconciliation complete |
| Lifecycle chain verified | All 6 stages communicate correctly |
| Registry authoritative | Pipeline layer registry covers all sealed layers |
| Operational metrics captured | Baseline metrics recorded for future comparison |

**Transition to Stage 3:** Registry covers all sealed layers through current sprint.

### Stage 3: Managed — Registry Authority
*Equivalent: Phase 2 (#202)*

| Criterion | Requirement |
|-----------|-------------|
| Registry complete | All sealed sprints registered in authoritative layer map |
| Health baselines current | Pipeline health checks pass without stale-baseline warnings |
| Data maintenance automated | Registry extension occurs with each seal |
| Sparse slots documented | Gaps classified as expected sparsity, not missing data |

**Transition to Stage 4:** Owner-facing dashboard operational with multi-project support.

### Stage 4: Measured — Operational Visibility
*Equivalent: Phase 3 (#203–#204)*

| Criterion | Requirement |
|-----------|-------------|
| Owner dashboard operational | CLI dashboard with text and JSON modes |
| All 6 dashboard sections present | Health, findings, risk, evidence, queue, readiness |
| Projection invariant enforced | Dashboard does not create, approve, or override state |
| Multi-project routing available | At least 2 projects routable with preserved boundaries |
| Projection accuracy verified | Dashboard state matches source records |

**Transition to Stage 5:** Operational calibration baseline established.

### Stage 5: Optimizing — Calibrated Operations
*Equivalent: Phase 4 (#205–#206)*

| Criterion | Requirement |
|-----------|-------------|
| Calibration baseline captured | False-positive rate, stale-state frequency, decision queue quality measured |
| Governance policy documented | Written policy for assurance operations |
| Operating cadence defined | Rhythms for runs, reviews, and calibrations documented |
| Drift detection active | Long-term model drift monitored |
| Owner feedback loop established | Owner acknowledges, accepts, or rejects findings regularly |

## Maturity Assessment

| Stage | Status | Evidence |
|-------|--------|----------|
| 1: Initial | ✅ Complete | #166–#200 sealed (33 assurance capability sprints) |
| 2: Defined | ✅ Complete | #201 sealed, lifecycle chain verified |
| 3: Managed | ✅ Complete | #202 sealed, 193 layers in registry |
| 4: Measured | ✅ Complete | #203 sealed (dashboard), #204 sealed (routing) |
| 5: Optimizing | 🔜 Sprint 206 | Calibration captured (#205), governance (#206 in progress) |

## Recurring Assessment

Maturity should be reassessed at the start of each new epic. The assessment checks:
1. Are all Stage 1–4 criteria still met?
2. Has calibration drifted since last assessment?
3. Are governance policies still current?
4. Has the operating cadence been followed?
