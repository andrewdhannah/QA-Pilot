# QA-PILOT-ASSURANCE-PROFILE-ARCHITECTURE-1 — Evidence

**Produced by:** #185
**Date:** 2026-07-20
**Status:** Architecture document — defines assurance profile framework

---

## 1. Assurance Profile Contract

### Schema

```json
{
  "profile_id": "string (unique identifier)",
  "name": "string (human-readable)",
  "version": "string (semver)",
  
  "standards": [
    {
      "reference": "string (e.g. SOC2, GDPR Article 17)",
      "description": "string"
    }
  ],

  "controls": [
    {
      "id": "string (control identifier)",
      "description": "string",
      "capabilities": ["security", "privacy", "accessibility", "performance", "regression", "uat", "language"],
      "evidence_required": ["implementation", "documentation", "test_result"],
      "finding_classification_default": "OBSERVATION",
      "escalation_rule": "OWNER_DECISION_REQUIRED (if drift detected)"
    }
  ],

  "authority_level": "advisory"
}
```

### Rules

- Every profile has an `authority_level: advisory` — no profile can assert compliance
- `evidence_required` is a hint to QA Pilot, not a certification checklist
- `escalation_rule` defines when OBSERVATION becomes OWNER_DECISION_REQUIRED

---

## 2. Control-to-Capability Mapping

### Capability → Control Coverage

| QA Pilot Capability | Example Controls |
|--------------------|------------------|
| Security | Auth boundaries, config review, dependency scan, secret detection |
| Privacy/Compliance | Data collection, analytics declarations, storage practices |
| Accessibility | WCAG criteria, semantic elements, keyboard nav, form labels |
| Performance | Response times, throughput, resource usage |
| Regression | Change impact, test coverage, evidence comparison |
| UAT | Requirements alignment, scenario completeness |
| Language | Translation parity, missing key detection |

### Control → Capability Example (SOC2 CC6.1)

```json
{
  "control_id": "CC6.1",
  "description": "Logical and physical access controls",
  "mapped_capabilities": [
    {"capability": "security", "check": "authentication flow inspection"},
    {"capability": "security", "check": "authorization boundary analysis"},
    {"capability": "regression", "check": "access control change detection"}
  ],
  "expected_evidence": ["implementation", "documentation"]
}
```

---

## 3. Evidence Expectation Model

| Evidence Type | Definition | QA Pilot Action |
|--------------|------------|----------------|
| implementation | Source code implements the control | Static analysis, pattern matching |
| documentation | Supporting doc describes the control | Artifact discovery, content validation |
| test_result | Test evidence confirms the control | Test execution, evidence comparison |

### Expectations per evidence type

- **implementation:** QA Pilot checks source for control-relevant patterns
- **documentation:** QA Pilot discovers and classifies existing docs (not create new ones)
- **test_result:** QA Pilot runs relevant capability and captures output

---

## 4. Finding Taxonomy Inheritance

### Capability-level → Profile-level mapping

| Capability Finding | Profile Finding | When |
|-------------------|----------------|------|
| PASS | PASS | All mapped controls pass |
| OBSERVATION | OBSERVATION | Minor variance, no escalation |
| GAP | OWNER_DECISION_REQUIRED | Control evidence not found |
| OWNER_DECISION_REQUIRED | OWNER_DECISION_REQUIRED | Capability escalated |

### Taxonomy rules

- Profile inherits from capability findings — it does not redefine them
- A single OWNER_DECISION_REQUIRED at capability level escalates the entire profile
- Profile-level PASS requires all mapped capabilities to PASS for that control

---

## 5. Librarian Handoff Format

```json
{
  "assurance_report": {
    "profile": "SOC2",
    "generated_at": "ISO8601",
    "overall": "OWNER_DECISION_REQUIRED",
    
    "control_summary": [
      {
        "id": "CC6.1",
        "status": "OBSERVATION",
        "evidence_found": ["implementation", "documentation"],
        "finding": "Access controls identified; documented procedure exists",
        "capability_results": {
          "security": "PASS",
          "regression": "OBSERVATION"
        }
      }
    ],
    
    "authority_level": "advisory",
    "owner_action_required": true
  }
}
```

### Handoff rules

- `owner_action_required: true` when any control is OWNER_DECISION_REQUIRED
- Evidence is advisory — QA Pilot does not assert compliance
- Librarian consumes as evidence, not as decision

---

## Acceptance Gates

| Gate | Result |
|------|--------|
| PA-1 | PASS — Assurance profile contract defined with schema + rules |
| PA-2 | PASS — Control-to-capability mapping defined with 7 capabilities |
| PA-3 | PASS — Evidence expectation model defined (3 types) |
| PA-4 | PASS — Finding taxonomy inheritance defined (capability→profile mapping) |
| PA-5 | PASS — Librarian handoff format defined with escalation rules |
| PA-6 | PASS — No compliance claims — all profiles authority_level: advisory |
| PA-7 | PASS — Evidence artifact produced (this document) |

**7 PASS, 0 FAIL**

---

**Classification:** Advisory architecture definition — does not authorize implementation.
