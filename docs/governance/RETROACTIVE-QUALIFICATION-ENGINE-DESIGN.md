# Retroactive Qualification Engine — Design

**Document type:** Architecture design  
**Authority:** Owner-authorized  
**Status:** ✅ **Owner-authorized 2026-08-15**  
**Date:** 2026-08-15  
**Purpose:** Define how QA-Pilot qualifies historical work against current assurance standards without mutating sealed records.

---

## Core Principle

**Seals are immutable history. Qualification is a living assessment.**

A sealed sprint record is never modified. A retroactive qualification adds a new evidence layer on top of the historical record. The result is a qualification history that grows over time as standards evolve.

```
Sprint #123
    │
    ├── Original seal (immutable)
    ├── Original evidence (immutable)
    ├── Original validator results (immutable)
    ├── Original acceptance criteria (immutable)
    │
    └── Qualification History (append-only)
          │
          ├── Qualification Pass #1 (2026-08-15)
          │     ├── Baseline: v1
          │     ├── Compiler: v1.0.0
          │     ├── Domains: functional, evidence, authority, testing, operational
          │     ├── Evidence: QE-SPRINT-123-PASS1.json
          │     ├── Findings: 0
          │     └── Disposition: PASS
          │
          ├── Qualification Pass #2 (future)
          │     ├── Baseline: v2 (new security checks added)
          │     ├── Compiler: v2.0.0
          │     ├── Domains: functional, evidence, authority, testing, operational, security
          │     ├── Evidence: QE-SPRINT-123-PASS2.json
          │     ├── Findings: 1 (SC-001: authorization boundary unclear)
          │     └── Disposition: FINDING
          │
          └── ...
```

---

## Architecture

```
Historical Sprint/Epic
        │
        ▼
Contract + Evidence Extraction
        │
        ▼
Applicability Determination
        │
        ├── Temporal: did this check exist when the work was done?
        ├── Domain: does this check apply to this artifact type?
        └── Scope: is this check within the artifact's declared scope?
        │
        ▼
Qualification Profile Selection
        │
        ├── Core checks (always apply where applicable)
        └── Domain checks (selected by artifact type)
        │
        ▼
Qualification Compiler
        │
        ▼
Domain-Specific Test Suites
        │
        ▼
Evidence Collection
        │
        ▼
Retroactive Qualification Record
        │
        ├── never modifies original seal
        ├── appends to qualification history
        └── produces independent evidence artifact
```

---

## Key Distinction: Retest vs Requalify

| Operation | Question Asked | Scope |
|-----------|---------------|-------|
| **Retest** | Does the code still work? | Functional correctness |
| **Requalify** | Does this work satisfy the current governance, authority, evidence, and quality model? | Full assurance profile |

Retesting is a subset of requalification. A sprint might pass all functional tests but fail requalification because:

- No evidence receipt was generated
- Authority boundaries were unclear
- An agent action was not Owner-authorized
- Provenance was incomplete
- A contract invariant was never tested
- Accessibility/security requirements were absent

The code might be fine. The governance evidence might not be.

---

## Qualification Record Schema

```json
{
  "qualification_id": "QR-SPRINT-123-PASS1",
  "qualification_type": "retroactive",
  "target": {
    "type": "sprint",
    "id": "SPRINT-123",
    "sealed_at": "2025-06-15T00:00:00Z",
    "seal_authority": "Owner"
  },
  "baseline": {
    "version": "v1",
    "reference": "QUALIFICATION-BASELINE-V1.md"
  },
  "compiler": {
    "version": "1.0.0",
    "ir_id": "IR-SPRINT-123-RETRO-1"
  },
  "applicability": {
    "core_checks": {
      "CT-001": "applicable",
      "CT-002": "applicable",
      "EV-001": "applicable",
      "EV-002": "applicable",
      "AU-001": "applicable",
      "AU-002": "applicable",
      "TS-001": "applicable",
      "TS-002": "applicable",
      "OP-001": "not_applicable",
      "OP-004": "not_applicable"
    },
    "domain_checks": {
      "SC-001": "not_applicable",
      "AC-001": "not_applicable",
      "PF-001": "not_applicable"
    },
    "reasons": {
      "OP-001": "startup regression checks did not exist at seal time",
      "OP-004": "drift detection not implemented until sprint #39",
      "SC-001": "security domain not defined until baseline v1",
      "AC-001": "accessibility checks not applicable to governance sprint",
      "PF-001": "performance checks not applicable to governance sprint"
    }
  },
  "results": {
    "total_checks": 20,
    "applicable_checks": 15,
    "passed": 15,
    "findings": 0,
    "not_applicable": 5
  },
  "disposition": "PASS",
  "evidence": "QE-SPRINT-123-PASS1.json",
  "executed_at": "2026-08-15T22:00:00Z"
}
```

---

## Execution Model

### Step 1: Target Selection

Select the historical epic or sprint to qualify. Epics are the preferred unit because they contain enough semantic context for meaningful qualification.

### Step 2: Contract Extraction

From the sealed sprint/epic record, extract:
- Acceptance criteria
- Invariants
- Authority constraints
- Lifecycle rules
- Evidence that was produced
- Validators that were run

### Step 3: Applicability Determination

For each check in the Qualification Baseline:
- **Temporal:** Was this check defined before or after the artifact was sealed?
- **Domain:** Does this check apply to this artifact type? (Use the Applicability Matrix)
- **Scope:** Is this check within the artifact's declared scope?

Mark each check as: `applicable`, `not_applicable`, or `deferred`.

### Step 4: Profile Selection

Based on artifact type, select the appropriate domain profile:
- Governance sprints → core + authority + evidence
- Implementation sprints → core + testing + operational
- Frontend sprints → core + testing + accessibility + performance
- Training sprints → core + testing + AI governance

### Step 5: Compile and Execute

Use the Qualification Compiler with the extracted contract and selected profile to generate and execute the qualification suite.

### Step 6: Produce Evidence

Generate a Retroactive Qualification Record. This is a new evidence artifact that:
- References the original sprint by ID
- Never modifies the original seal
- Records applicability decisions with reasons
- Produces findings with remediation recommendations
- Gets its own qualification ID (QR-*)

### Step 7: Disposition

| Disposition | Action |
|-------------|--------|
| PASS | Record qualification. No further action. |
| FINDING | Record qualification. Create finding record. Owner decides remediation. |
| NOT APPLICABLE | Record why. No finding. |

---

## Batch Qualification

For qualifying an entire project history:

1. **Start with epics** — each epic has a contract, scope, and bounded acceptance criteria
2. **Qualify each epic** — produces an epic-level qualification record
3. **Descend into sprints only where needed** — if an epic qualifies, sprints within it are lower risk
4. **Correlate findings** — if multiple sprints share a finding pattern, it's a systemic issue
5. **Produce a project-level qualification summary**

```
Project History
    │
    ├── Epic 1 → Qualification Record (PASS)
    ├── Epic 2 → Qualification Record (FINDING: 2 findings)
    │     ├── Sprint 2a → Detailed qualification (finding localized)
    │     ├── Sprint 2b → Spot check (clean)
    │     └── Sprint 2c → Spot check (clean)
    ├── Epic 3 → Qualification Record (PASS)
    └── Epic 4 → Qualification Record (NOT APPLICABLE: predates baseline)
```

---

## Relationship to Training

Retroactive qualification produces finding patterns that feed the learning platform:

```
Retroactive Qualification
    │
    ├── Findings: "governance sprints often lack evidence receipts"
    ├── Findings: "frontend sprints often miss accessibility checks"
    ├── Findings: "training sprints lack provenance tracking"
    │
    ▼
Pattern Analysis
    │
    ▼
Learning Objects (from qa_pilot_lesson_generator.py)
    │
    ▼
Training Delivery (browser-app)
    │
    ▼
Future Work Improvement
    │
    ▼
Stronger Forward Qualification
```

This is the closed-loop system: historical qualification produces patterns that improve future work through training.

---

## Implementation Scope (EPIC-RETROACTIVE-QUALIFICATION-ENGINE-1)

### Phase 1: Core Engine
- Retroactive qualification record schema
- Applicability determination logic
- Integration with Qualification Compiler
- Single-epic qualification execution

### Phase 2: Batch Execution
- Project history traversal
- Epic-first qualification strategy
- Sprint-level spot checking
- Finding correlation

### Phase 3: Integration
- Findings → Learning Objects pipeline
- Training delivery of qualification patterns
- Continuous re-qualification on baseline changes

---

## Key Invariants

1. **Original seals are never modified.** Qualification adds a new layer.
2. **Applicability is explicit.** Every check has a reason for being applicable or not.
3. **Temporal fairness.** A 2025 sprint cannot fail a 2026 requirement.
4. **Domain relevance.** Checks only apply where the domain matches.
5. **Evidence is independent.** Retroactive qualification produces its own evidence artifacts.
6. **Findings are advisory.** Retroactive findings require Owner disposition.
