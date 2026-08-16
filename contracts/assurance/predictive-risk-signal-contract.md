# Predictive Risk Signal Contract

**Sprint:** QA-PILOT-PREDICTIVE-RISK-SIGNALS-1 (#240)
**Status:** ACTIVE — Owner-authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define forward-looking risk indicators derived from current state, patterns, and trajectory.

## 2. Core Distinction

| Concept | Meaning | Time Frame |
|---------|---------|------------|
| Risk Assessment | Current observed risk | Now |
| Predictive Signal | Projected future condition | Future |

**Keep these separate.** Do not modify existing risk records.

## 3. Signal Semantics

| Term | Definition | Not |
|------|------------|-----|
| `signal` | Forward-looking indicator | Finding, failure, or requirement |
| `projected_condition` | What may happen | What will happen |
| `confidence` | How certain the projection is | Authority to act |
| `basis` | What data supports the projection | Root cause |
| `time_horizon` | When this may occur | Deadline |

## 4. Signal Categories

| Category | Meaning | Example |
|----------|---------|---------|
| `emerging_risk` | Risk may increase | "Risk trajectory increasing" |
| `evidence_degradation` | Evidence quality may decline | "Coverage decreasing" |
| `planning_drift` | Planning accuracy may worsen | "Repeated underestimation" |

## 5. Confidence Rules

| Condition | Confidence |
|-----------|------------|
| Multiple patterns with large samples | high |
| Some patterns with moderate samples | medium |
| Few patterns or small samples | low |
| No patterns or insufficient data | insufficient |

## 6. Non-Authority Boundary

Predictive signals:

| May Do | May Not Do |
|--------|------------|
| Project conditions | Create findings |
| Show confidence | Create work packets |
| Reference patterns | Assign priorities |
| Explain basis | Trigger remediation |
| Report time horizon | Modify state |
