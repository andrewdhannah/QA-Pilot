# Qualification Baseline v1

**Document type:** Assurance baseline  
**Authority:** Owner-decided  
**Status:** ✅ **Owner-decided 2026-08-15**  
**Date:** 2026-08-15  
**Purpose:** Define the minimum qualification standard against which any artifact can be evaluated, regardless of when it was created.

---

## Purpose

This baseline defines what QA-Pilot checks when it qualifies an artifact. It is the reference standard for both forward qualification (new work) and retroactive qualification (historical work).

The baseline is intentionally domain-agnostic. Domain-specific profiles (security, accessibility, performance) select subsets of these checks and add domain-specific tests.

---

## Core Check Categories

### 1. Contract

| Check | ID | Description |
|-------|----|-------------|
| Acceptance criteria mapped | CT-001 | Artifact has defined acceptance criteria |
| Invariants identified | CT-002 | Contractual invariants are explicit |
| Stop conditions defined | CT-003 | Conditions that halt work are documented |
| Scope boundaries | CT-004 | What is in/out of scope is defined |

### 2. Evidence

| Check | ID | Description |
|-------|----|-------------|
| Receipt exists | EV-001 | A governance receipt records the work |
| Evidence provenance | EV-002 | Evidence has traceable source and hash |
| Evidence freshness | EV-003 | Evidence is not stale relative to the work |
| Evidence completeness | EV-004 | Required evidence types are present |

### 3. Authority

| Check | ID | Description |
|-------|----|-------------|
| Owner boundary defined | AU-001 | Owner authority is explicit |
| Agent authority constrained | AU-002 | Agent capabilities are bounded |
| Cross-project mutation authorized | AU-003 | Any cross-project write has custody authorization |
| Seal authority | AU-004 | Only the Owner can seal |

### 4. Testing

| Check | ID | Description |
|-------|----|-------------|
| Positive path | TS-001 | Legitimate workflows produce correct outcomes |
| Negative path | TS-002 | Forbidden states are rejected |
| Failure path | TS-003 | Error conditions are handled gracefully |
| Regression path | TS-004 | Existing functionality is not broken |

### 5. Operational

| Check | ID | Description |
|-------|----|-------------|
| Startup behavior | OP-001 | System starts in a defined state |
| Persistence | OP-002 | State survives restart |
| Recovery | OP-003 | System recovers from corruption or crash |
| Drift detection | OP-004 | Changes from baseline are detectable |

---

## Domain-Specific Extensions

The core checks above apply to all artifacts. Domain profiles add specialized checks:

### Security Domain

| Check | ID | Description |
|-------|----|-------------|
| Authorization boundary | SC-001 | Access control is enforced |
| Input validation | SC-002 | External input is validated |
| Dependency scan | SC-003 | Dependencies are known and current |
| Mutation path analysis | SC-004 | Write paths are controlled |

### Accessibility Domain

| Check | ID | Description |
|-------|----|-------------|
| WCAG conformance | AC-001 | Meets applicable WCAG level |
| Keyboard navigation | AC-002 | All interactions are keyboard-accessible |
| Screen reader semantics | AC-003 | ARIA roles and labels are correct |
| Contrast ratios | AC-004 | Color contrast meets minimums |

### Performance Domain

| Check | ID | Description |
|-------|----|-------------|
| Load time | PF-001 | Initial load within threshold |
| Render time | PF-002 | UI renders within threshold |
| Memory usage | PF-003 | No unbounded memory growth |
| Scalability | PF-004 | Degrades gracefully under load |

### Compliance Domain

| Check | ID | Description |
|-------|----|-------------|
| Data lineage | CO-001 | Data origins are traceable |
| Retention policy | CO-002 | Data lifecycle is governed |
| Audit trail | CO-003 | Actions are logged |
| Consent model | CO-004 | User consent is managed |

### AI Governance Domain

| Check | ID | Description |
|-------|----|-------------|
| Model behavior bounds | AI-001 | AI actions are constrained |
| Provenance of outputs | AI-002 | AI-generated content is attributed |
| Human oversight | AI-003 | Critical decisions require human approval |
| Drift monitoring | AI-004 | Model behavior is monitored for drift |

---

## Disposition Model

When qualifying an artifact against this baseline:

| Disposition | Meaning | When to use |
|-------------|---------|-------------|
| **PASS** | Meets current qualification standard | All applicable checks pass |
| **FINDING** | Violates current standard | One or more applicable checks fail |
| **NOT APPLICABLE** | Standard did not exist or does not apply | The check category predates the artifact or is irrelevant to its domain |

### NOT APPLICABLE Rules

A check is NOT APPLICABLE when:

1. **Temporal:** The check was defined after the artifact was sealed. Example: a 2025 sprint cannot fail a 2026 accessibility requirement.
2. **Domain:** The check does not apply to the artifact's type. Example: a database migration does not apply WCAG checks.
3. **Scope:** The check is outside the artifact's declared scope. Example: a governance receipt sprint does not require browser testing.

The qualification record must state *why* a check is NOT APPLICABLE.

---

## Applicability Matrix

| Artifact Type | Functional | Evidence | Authority | Testing | Operational | Security | A11y | Perf | Compliance | AI Gov |
|---------------|:----------:|:--------:|:---------:|:-------:|:-----------:|:--------:|:----:|:----:|:----------:|:------:|
| Epic contract | ✓ | ✓ | ✓ | ✓ | ✓ | ○ | ○ | ○ | ○ | ○ |
| Sprint (governance) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | ○ | ○ |
| Sprint (implementation) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ○ | ○ | ○ | ○ |
| Sprint (frontend) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| Sprint (training) | ✓ | ✓ | ✓ | ✓ | ✓ | ○ | ○ | — | — | ✓ |
| Browser app | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| Qualification suite | ✓ | ✓ | ✓ | ✓ | ✓ | ○ | — | — | — | ○ |

**Legend:** ✓ = required, ○ = optional (apply if relevant), — = not applicable

---

## Usage

### Forward Qualification (New Work)

1. Work item created
2. Qualification profile selected based on work type
3. Baseline checks applied
4. Domain-specific tests executed
5. Evidence produced
6. Disposition recorded

### Retroactive Qualification (Historical Work)

1. Historical epic/sprint selected
2. Contract and evidence extracted from sealed records
3. Applicability determined (temporal, domain, scope)
4. Baseline checks applied where applicable
5. Domain-specific tests executed where applicable
6. Evidence produced as new qualification record
7. Original seal preserved — never modified

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| v1 | 2026-08-15 | Initial baseline — 20 core checks, 14 domain checks, 6 artifact types |
