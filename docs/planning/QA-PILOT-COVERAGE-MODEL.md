# QA Pilot Qualification Coverage Model

**Sprint:** QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1
**Status:** Planning — defines how coverage is measured, reported, and gated
**Dependency:** QA-PILOT-QUALIFICATION-ARCHITECTURE.md (§3.3 Coverage Levels)

---

## 0. Coverage Authority Boundary

Coverage is **measurement, not enforcement**. QA Pilot reports coverage gaps; it does not block releases autonomously. The release gate behavior is determined by the qualification profile (Node Profile extension) and the Owner's configured thresholds.

---

## 1. Coverage Dimensions

Coverage is measured across four dimensions:

| Dimension | Measures | Source |
|-----------|----------|--------|
| **Interface** | Every known interface has at least one test | Component metadata (routes, APIs, schemas) |
| **Authority** | Every authority boundary has adversarial tests | Node classification, authority model |
| **Domain** | Every enabled qualification domain has test coverage per component | Qualification profile |
| **Change** | Every structural change in a sprint has corresponding test regeneration | Sprint ledger diff |

### 1.1 Interface Coverage

For each component, every registered interface must be enumerated and tested:

```
Component: NODE-OWNER-QUEUE

Interfaces:
  POST /api/owner/action    →  3 tests (structural)
  GET  /api/owner/pending   →  2 tests (structural)
  WebSocket /events/owner   →  2 tests (behavioral)

Interface Coverage: 3/3 interfaces exercised (100%)
```

**Rule:** If an interface exists in the component metadata but no test references it, that is a coverage gap regardless of how many other tests exist.

### 1.2 Authority Coverage

For each component with an authority classification, adversarial tests must exist for that boundary type:

```
Component: NODE-OWNER-QUEUE
Classification: authority_boundary

Expected adversarial tests:
  ✓ AUTHZ-ACCESS-001 (unauth → 401)
  ✓ AUTHZ-ACCESS-002 (non-owner → 403)
  ✓ AUTHZ-ESCALATION-001 (privilege escalation → 403)
  ✓ AI-AUTH-ESCALATION-001 (self-escalation → 403)
  ✓ AI-RCPT-FORGERY-001 (receipt forgery → 403)

Authority Coverage: 5/5 required adversarial tests (100%)
```

**Rule:** Each classification tag has a minimum adversarial test suite (defined in the security taxonomy). Missing adversarial tests for authority-boundary components are blocking at `required` level.

### 1.3 Domain Coverage

For each enabled qualification domain, every component must meet the domain coverage threshold:

```
Component: NODE-LIBRARIAN-CORE

Domain Coverage:
  functional:  42/42 tests, 100% pass    →  QUALIFIED
  security:    18/18 tests, 100% pass    →  QUALIFIED
  performance:  6/6  tests, 100% pass    →  QUALIFIED

Overall: QUALIFIED
```

**Rule:** If a domain is enabled at `required` level and any component lacks coverage, the domain is not qualified.

### 1.4 Change Coverage

When a sprint seals, affected components must have regenerated tests:

```
Sprint: SOME-SPRINT-1
Changed: NODE-OWNER-QUEUE (new endpoint added), NODE-REGISTRY (schema updated)

Regeneration:
  NODE-OWNER-QUEUE:  +3 tests (structural for new endpoint)
                      2 tests updated (revision bump)
  NODE-REGISTRY:      +1 test (new schema validation)
                      4 tests unchanged (no interface change)

Change Coverage: 100% (all changed components regenerated)
```

**Rule:** A component that changed in a sprint must have its qualification tests regenerated. Regeneration does not mean all tests change — it means the test set is re-evaluated against the new component state.

---

## 2. Coverage Levels — Behavior

| Level | Interface | Authority | Domain | Change | Release Gate Impact |
|-------|-----------|-----------|--------|--------|---------------------|
| `informational` | Reported | Not required | Not required | Not required | None — dashboard only |
| `advisory` | Reported | Reported | Required @ ≥90% | Required | Warning in receipt, does not block |
| `required` | Required @ 100% | Required @ 100% | Required @ 100% | Required @ 100% | Blocks release qualification if unmet |

### 2.1 Level Inheritance

If a component has no explicit coverage level, the domain-level setting applies:

```
Domain: security (level: required)
  ↓
All components in security domain: coverage level = required
  ↓
Exception: NODE-DOC-SERVER (coverage level: informational, explicit override)
```

### 2.2 Explicit Override

A component may declare a lower coverage level than its domain default:

```json
{
  "node_id": "NODE-DOC-SERVER",
  "qualification_profile": {
    "security": { "level": "informational" },
    "functional": { "level": "required" }
  }
}
```

This is useful for components that are not security-sensitive but are part of a security-qualified system. The override must be explicit — implicit exemption is not permitted.

---

## 3. Coverage Calculation

### 3.1 Per-Component Score

```
coverage_score = passed_tests / required_tests

where:
  required_tests = interface_count * structural_multiplier
                 + adversarial_suite_count
                 + domain_tests
```

### 3.2 Per-Domain Score

```
domain_score = min(coverage_score across all components in domain)
```

The domain is only as strong as its weakest component.

### 3.3 Per-Project Score (Aggregate)

```
project_score = weighted average across required domains
                (release_gate.required_domains only)
```

Optional and advisory domains do not affect the aggregate score.

---

## 4. Gap Detection and Reporting

### 4.1 Gap Types

| Gap Type | Detection | Severity |
|----------|-----------|----------|
| Missing interface test | Component has interface with 0 test references | Blocking if level = required |
| Missing adversarial suite | Component has classification with 0 adversarial tests | Blocking if level = required |
| Missing domain coverage | Domain enabled but component has 0 tests in that domain | Blocking if level = required |
| Stale test revision | Test revision < component version | Advisory |
| Unexercised code path | Code location referenced by component but not by any test | Informational |
| Manual domain gap | Domain test expected but none authored | Advisory |

### 4.2 Report Format

```json
{
  "component": "NODE-OWNER-QUEUE",
  "coverage": {
    "interface": {
      "total": 3,
      "covered": 3,
      "score": 1.0,
      "status": "qualified"
    },
    "authority": {
      "required": 5,
      "executed": 5,
      "score": 1.0,
      "status": "qualified"
    },
    "domain": {
      "security": {
        "required": 12,
        "executed": 12,
        "passed": 12,
        "score": 1.0,
        "status": "qualified"
      }
    }
  },
  "gaps": [],
  "status": "QUALIFIED"
}
```

### 4.3 Gap Example

```json
{
  "component": "NODE-DATA-STORE",
  "coverage": {
    "interface": {
      "total": 5,
      "covered": 4,
      "gaps": [
        {
          "type": "missing_interface_test",
          "interface": "DELETE /api/records/{id}",
          "severity": "blocking",
          "reason": "Interface exists in component metadata but no test references it"
        }
      ],
      "score": 0.8,
      "status": "insufficient"
    }
  },
  "gaps": [
    {
      "type": "missing_interface_test",
      "interface": "DELETE /api/records/{id}",
      "classification": "authority_boundary",
      "suggested_tests": [
        "AUTHZ-ACCESS-001 (unauth → 401)",
        "AUTHZ-ACCESS-002 (non-owner → 403)"
      ]
    }
  ],
  "status": "INSUFFICIENT"
}
```

---

## 5. Regeneration and Coverage

When tests are regenerated due to a component change, coverage is recalculated:

| Event | Coverage Impact |
|-------|----------------|
| New component registered | Coverage drops to 0% → tests must be generated |
| New interface added | Interface coverage drops → structural tests generated |
| Interface removed | Coverage may increase (fewer interfaces to cover) — tests removed or retired |
| Classification changed | Authority coverage may drop → adversarial suite regenerated |
| Schema updated | Behavioral tests may need revision bump |
| Code location changed | Code references updated, tests regenerate with new locations |
| Component deprecated | Tests retired with DEPRECATED status (not failed) |

---

## 6. Edge Cases

### 6.1 Components With No Security Classification

If a component has no security-relevant classification tags (e.g., a static documentation server), is it a coverage gap?

**Rule:** No. The component's qualification profile must explicitly set `security: { level: "informational" }` or omit the domain. Implicit classification is not permitted. If no classification exists, no security tests are required, and no coverage gap is reported.

### 6.2 Generated Test That Cannot Execute

If the test generator creates a test that targets a route that no longer exists by the time of execution:

**Rule:** The test is marked STALE and re-generated. Coverage is temporarily reported as insufficient until regeneration completes. A stale test does not count as a failure.

### 6.3 Multiple Components Share an Interface

If two components both reference the same route:

**Rule:** The route must be tested from the context of each component's authority model. Coverage is counted once per component, not once per route.

---

## 7. Acceptance Gates for Coverage Model Implementation

| Gate | Requirement |
|------|-------------|
| COV-P1 | Interface coverage calculation defined and validated |
| COV-P2 | Authority coverage calculation defined and validated |
| COV-P3 | Domain coverage calculation defined and validated |
| COV-P4 | Change coverage calculation defined and validated |
| COV-P5 | Coverage level inheritance rules defined |
| COV-P6 | Gap detection logic for all 6 gap types |
| COV-P7 | Coverage report format defined |
| COV-P8 | Regeneration coverage recalculation rules defined |
| COV-P9 | Edge case handling (unclassified components, stale tests, shared interfaces) |

---

*Coverage model for QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1. Planning only. No implementation authority conferred.*
