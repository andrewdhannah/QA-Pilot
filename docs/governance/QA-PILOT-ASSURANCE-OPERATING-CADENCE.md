# QA Pilot Assurance Operating Cadence

**Version:** 1.0
**Effective:** 2026-07-20
**Epic:** EPIC-QA-PILOT-ASSURANCE-OPERATIONS-INTEGRATION-1

---

## Overview

This document defines the operating rhythms for the QA Pilot assurance layer. It establishes the cadence for assurance runs, Owner reviews, calibration measurements, and maturity assessments.

## Cadence Rhythms

### Daily — Owner Dashboard Check
| Element | Detail |
|---------|--------|
| **What** | Run `qa_pilot_owner_dashboard.py report` |
| **Owner reviews** | Active findings, Owner queue, stale evidence |
| **Expected duration** | <5 minutes |
| **Output** | Awareness of current assurance posture |

### Weekly — Assurance Run
| Element | Detail |
|---------|--------|
| **What** | Run continuous assurance loop scripts |
| **Triggers** | Finding lifecycle refresh, evidence freshness scan, risk reprioritization |
| **Owner action** | Acknowledge new findings, review Owner queue |
| **Expected duration** | <30 minutes |
| **Output** | Updated findings, refreshed evidence, recalibrated risk |

### Per-Sprint — Calibration Measurement
| Element | Detail |
|---------|--------|
| **What** | Run `qa_pilot_assurance_calibration.py report` |
| **Measures** | False-positive rate, stale-state frequency, decision queue quality, evidence freshness, projection accuracy |
| **Owner action** | Compare against baseline, identify trends |
| **Output** | Calibration report attached to sprint record |

### Per-Epic — Maturity Assessment
| Element | Detail |
|---------|--------|
| **What** | Run maturity model assessment against Stage 1–5 criteria |
| **Measures** | All stages still satisfied, calibration drift, governance policy currency |
| **Owner action** | Approve maturity stage, identify improvement areas |
| **Output** | Maturity assessment recorded in epic documentation |

## Operating Boundaries

| Boundary | Rule |
|----------|------|
| Assurance runs never modify source stores | Read-only operations only |
| Calibration measurements never change system behavior | Observational only |
| Owner reviews produce decisions, not findings | Findings are pre-decisional |
| Maturity assessments are advisory only | Cannot block operations |

## Drift Detection

Long-term drift is detected by comparing calibration measurements across sprints:

| Signal | What It Indicates | Response |
|--------|-------------------|----------|
| Increasing false-positive rate | Model generating too many non-actionable findings | Review finding thresholds, adjust risk model |
| Increasing stale-state frequency | Evidence not being refreshed | Check continuous assurance loop health |
| Decreasing decision queue throughput | Owner not engaging | Review queue quality, reduce noise |
| Decreasing projection accuracy | Dashboard/source divergence | Fix data binding, check for stale caches |
| Decreasing Owner interaction rate | Dashboard not providing value | Review dashboard usefulness, adjust sections |
