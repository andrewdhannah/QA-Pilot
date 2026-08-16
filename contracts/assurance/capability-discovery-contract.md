# Capability Discovery Contract

**Sprint:** QA-PILOT-CAPABILITY-DISCOVERY-1 (#233)
**Status:** ACTIVE — Authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the capability discovery model for detecting missing, incomplete, or inconsistent governance capabilities across onboarded projects.

## 2. Core Principle

**Capability Discovery identifies candidates and gaps.**

It does NOT:
- Create capabilities
- Activate capabilities
- Assign authority
- Modify governance state

## 3. Discovery Finding Types

| Finding Type | Meaning | Example |
|--------------|---------|---------|
| `coverage_gap` | Capability declared but no evidence | "runtime_assurance declared, no evidence in 30 days" |
| `evidence_gap` | Evidence exists but incomplete | "Qualification history has no security findings" |
| `stale_capability` | Capability not recently validated | "Last qualification > 90 days ago" |
| `authority_ambiguity` | Authority boundaries unclear | "Capability scope not declared" |
| `cag_noncompliance` | CAG requirement missing | "Capability not discoverable in projection" |
| `drift_detected` | Capability changed without governance update | "Scope expanded from observe to mutate" |

## 4. Discovery Finding Record

```json
{
  "finding_id": "CDF-001",
  "project_id": "agent-bridge",
  "finding_type": "coverage_gap",
  "capability": "runtime_assurance",
  "description": "Capability declared but no evidence produced in 30 days",
  "severity": "medium",
  "evidence_refs": [],
  "recommendation": "Consider generating runtime evidence or removing capability declaration",
  "discovered_at": "2026-08-16T05:10:00Z",
  "discovered_by": "scripts/discover-capabilities.py",
  "advisory_only": true
}
```

## 5. CAG Compliance Requirements

| Requirement | Check | Finding if Missing |
|-------------|-------|-------------------|
| Declaration | Capability has description | `cag_noncompliance: missing_declaration` |
| Discoverability | Capability in projection | `cag_noncompliance: missing_discoverability` |
| Authority | Boundaries declared | `cag_noncompliance: missing_authority` |
| Validation | Validator exists | `cag_noncompliance: missing_validation` |
| Projection | Startup visibility present | `cag_noncompliance: missing_projection` |

## 6. Drift Detection Rules

| Rule | Condition | Finding |
|------|-----------|---------|
| DR-1 | Capability scope expanded | `drift_detected: scope_expansion` |
| DR-2 | Authority boundary changed | `drift_detected: authority_change` |
| DR-3 | Evidence requirements changed | `drift_detected: evidence_change` |
| DR-4 | Qualification profile changed | `drift_detected: profile_change` |

## 7. Non-Authority Boundary

The discovery engine:

| May Do | May Not Do |
|--------|------------|
| Identify gaps | Create capabilities |
| Recommend action | Activate capabilities |
| Reference evidence | Assign authority |
| Report drift | Modify governance |
| Generate findings | Make decisions |

## 8. Discovery Projection

Discovery results are available through:

```python
def get_capability_discoveries(project_id: str = None) -> dict:
    """
    Returns capability discovery findings.
    
    Returns:
        {
            "discovery_id": str,
            "generated_at": str,
            "findings": [dict],
            "summary": {
                "total": int,
                "by_type": dict,
                "by_severity": dict
            },
            "authority": "observation_only"
        }
    """
    pass
```
