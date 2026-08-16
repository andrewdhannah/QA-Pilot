# LINK Readiness Contract

**Sprint:** QA-PILOT-FLEET-FRESHNESS-DISCOVERY-1 (#224)
**Status:** INTERFACE DEFINED — Not yet implemented
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the future query surface that LINK will consume to access project assurance state. This contract establishes the interface now so LINK integration can consume a mature assurance state in a future sprint.

**This contract does NOT implement LINK integration.** It only defines the interface.

## 2. Interface Definition

### 2.1 Primary Query

```python
def get_project_assurance_state(project_id: str) -> dict:
    """
    Returns assurance state for a project.
    
    This is the primary interface LINK will consume.
    Returns advisory-only data. No authority conferred.
    
    Args:
        project_id: Canonical project identifier
        
    Returns:
        {
            "status": "operational" | "degraded" | "unknown",
            "freshness": "current" | "aging" | "stale" | "unknown",
            "coverage": "full" | "partial" | "minimal" | "none" | "unknown",
            "findings_summary": {
                "total": int,
                "critical": int,
                "high": int,
                "medium": int,
                "low": int
            },
            "qualification_age": "ISO8601 duration since last qualification",
            "last_qualification": "ISO8601 timestamp or null",
            "missing_domains": ["string"],
            "recommendations": ["string"]
        }
    """
    pass
```

### 2.2 Fleet Query

```python
def get_fleet_assurance_state() -> dict:
    """
    Returns assurance state for all governed projects.
    
    Returns:
        {
            "generated_at": "ISO8601",
            "total_projects": int,
            "projects_by_freshness": {
                "current": int,
                "aging": int,
                "stale": int,
                "unknown": int
            },
            "projects_by_coverage": {
                "full": int,
                "partial": int,
                "minimal": int,
                "none": int,
                "unknown": int
            },
            "attention_needed": [
                {
                    "project_id": "string",
                    "reason": "string",
                    "priority": "critical" | "high" | "medium" | "low"
                }
            ]
        }
    """
    pass
```

## 3. Response Semantics

### 3.1 Status Field

| Status | Condition | Meaning |
|--------|-----------|---------|
| `operational` | Coverage full/partial AND freshness current | Project has sufficient evidence |
| `degraded` | Coverage partial/minimal OR freshness aging/stale | Project has gaps or outdated evidence |
| `unknown` | Coverage unknown OR freshness unknown | Cannot determine state |

### 3.2 Freshness Field

Inherits from fleet freshness policy:
- `current`: Evidence is recent
- `aging`: Evidence is getting old
- `stale`: Evidence is outdated
- `unknown`: Cannot determine freshness

### 3.3 Coverage Field

Inherits from fleet freshness policy:
- `full`: All domains covered
- `partial`: Some domains covered
- `minimal`: Essential domains only
- `none`: No coverage
- `unknown`: Cannot determine coverage

### 3.4 Findings Summary

Aggregated qualification results:
- `total`: Total findings across all qualifications
- `critical`: Critical severity findings
- `high`: High severity findings
- `medium`: Medium severity findings
- `low`: Low severity findings

### 3.5 Qualification Age

ISO 8601 duration since last qualification:
- `P0D` = qualified today
- `P7D` = qualified 7 days ago
- `P30D` = qualified 30 days ago
- `null` = never qualified

## 4. Usage Pattern (Future)

```
LINK Planning Loop:

1. Query: get_fleet_assurance_state()
2. Filter: projects where status == "degraded" OR priority == "critical"
3. Prioritize: sort by findings_summary.critical DESC, qualification_age DESC
4. Recommend: "These projects need attention"
5. Owner decides: which projects to address
```

**Rule:** LINK recommends. Owner decides. System does not act autonomously.

## 5. Implementation Boundary

| Aspect | Status |
|--------|--------|
| Interface definition | ✅ Defined in this contract |
| Data source | ✅ Available from fleet freshness discovery (#224) |
| Implementation | ⏸ Deferred to LINK integration sprint |
| LINK consumption | ⏸ Deferred to LINK integration sprint |

## 6. Advisory Boundary

The interface returns advisory data only:

| Allowed | Forbidden |
|---------|-----------|
| Status assessment | Action scheduling |
| Freshness evaluation | Task dispatch |
| Coverage analysis | Evidence mutation |
| Finding summary | Authorization |
| Recommendation | Autonomous improvement |
