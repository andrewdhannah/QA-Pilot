# Assurance Projection Contract

**Sprint:** QA-PILOT-LINK-ASSURANCE-INTEGRATION-1 (#227)
**Status:** ACTIVE — Authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the read-only projection API that exposes governed assurance state to planning workflows. LINK consumes this projection for planning context. LINK does not write to QA-Pilot state.

## 2. Core Principle

LINK answers: **"What assurance context should influence planning?"**
LINK does NOT answer: **"What should the project do?"**

| Allowed | Forbidden |
|---------|-----------|
| Read assurance state | Mutate QR records |
| Display risk context | Alter risk scores |
| Show recommendations | Modify evidence |
| Trace provenance | Trigger qualification |
| Show freshness | Hide staleness |

## 3. Projection Schema

### 3.1 Project Assurance State

```json
{
  "project_id": "librarian",
  "projection_timestamp": "2026-08-16T04:30:00Z",
  "assurance_state": {
    "status": "operational" | "degraded" | "unknown",
    "risk_band": "healthy" | "monitor" | "attention_required" | "urgent",
    "risk_score": 23,
    "coverage": "full" | "partial" | "minimal" | "none" | "unknown",
    "freshness": "current" | "aging" | "stale" | "unknown",
    "qualification_status": "pass" | "finding" | "untested"
  },
  "drivers": [
    "missing_security_coverage"
  ],
  "recommendations": [
    "Consider adding security evidence coverage"
  ],
  "evidence_refs": [
    {
      "ref": "QR-20260816-001",
      "type": "qualification_result",
      "disposition": "PASS"
    }
  ],
  "provenance": {
    "risk_assessment_id": "RA-20260816-librarian",
    "qualification_run_id": "QCR-20260816-001",
    "freshness_assessment_source": "discover-fleet-freshness.py"
  },
  "authority": "observation_only"
}
```

### 3.2 Fleet Assurance State

```json
{
  "projection_timestamp": "2026-08-16T04:30:00Z",
  "total_projects": 2,
  "by_status": {
    "operational": 1,
    "degraded": 1,
    "unknown": 0
  },
  "by_risk_band": {
    "healthy": 0,
    "monitor": 2,
    "attention_required": 0,
    "urgent": 0
  },
  "attention_needed": [
    {
      "project_id": "librarian",
      "risk_band": "monitor",
      "reasons": ["missing_security_coverage"]
    }
  ],
  "projects": [...]
}
```

### 3.3 Assurance History

```json
{
  "project_id": "librarian",
  "history": [
    {
      "qualification_run_id": "QCR-20260816-001",
      "disposition": "PASS",
      "executed_at": "2026-08-16T04:26:29Z",
      "trigger_type": "evidence_change"
    }
  ],
  "total_runs": 5,
  "last_run": "QCR-20260816-001"
}
```

## 4. Query Interface

### 4.1 get_project_assurance_state

```python
def get_project_assurance_state(project_id: str) -> dict:
    """
    Returns assurance state for a single project.
    
    Read-only. No mutation operations.
    
    Returns:
        {
            "project_id": str,
            "projection_timestamp": str,
            "assurance_state": {
                "status": str,
                "risk_band": str,
                "risk_score": int,
                "coverage": str,
                "freshness": str,
                "qualification_status": str
            },
            "drivers": [str],
            "recommendations": [str],
            "evidence_refs": [dict],
            "provenance": dict,
            "authority": "observation_only"
        }
    """
    pass
```

### 4.2 get_fleet_assurance_state

```python
def get_fleet_assurance_state() -> dict:
    """
    Returns assurance state for all governed projects.
    
    Read-only. No mutation operations.
    
    Returns:
        {
            "projection_timestamp": str,
            "total_projects": int,
            "by_status": dict,
            "by_risk_band": dict,
            "attention_needed": [dict],
            "projects": [dict]
        }
    """
    pass
```

### 4.3 get_assurance_history

```python
def get_assurance_history(project_id: str) -> dict:
    """
    Returns qualification history for a project.
    
    Read-only. Append-only history.
    
    Returns:
        {
            "project_id": str,
            "history": [dict],
            "total_runs": int,
            "last_run": str
        }
    """
    pass
```

## 5. Planning Context Example

When a planning agent requests assurance context:

```python
# Agent asks for planning context
context = get_project_assurance_state("librarian")

# Agent receives:
{
    "project_id": "librarian",
    "assurance_state": {
        "status": "operational",
        "risk_band": "monitor",
        "risk_score": 23,
        "coverage": "partial",
        "freshness": "current",
        "qualification_status": "pass"
    },
    "drivers": ["missing_security_coverage"],
    "recommendations": ["Consider adding security evidence coverage"]
}

# Agent uses this context in planning:
"Create authentication sprint"
  +
  "Security qualification coverage is partial"
  +
  "Recommendation: include security qualification gate"
  ↓
  Better-informed planning decision
```

## 6. Staleness Visibility Rule

LINK must never hide freshness. The projection always includes:

```json
{
  "assurance_state": {
    "freshness": "stale"
  }
}
```

If evidence is stale, the planning agent sees:
- "Evidence is stale — risk assessment may be outdated"
- "Consider refreshing evidence before major planning decisions"

LINK does NOT:
- Hide stale data
- Auto-refresh stale data
- Treat stale data as current

## 7. Provenance Chain

Every assurance item traces to source:

```
LINK View
   ↓
Assurance Projection
   ↓
Risk Assessment (RA-*)
   ↓
Qualification Result (QCR-*)
   ↓
Evidence Record (RAE-*/RLE-*/RRO-*)
```

## 8. Non-Authority Boundary

The projection API:

| May Do | May Not Do |
|--------|------------|
| Read assurance state | Create work packets |
| Display risk context | Assign owners |
| Show recommendations | Close findings |
| Trace provenance | Approve remediation |
| Show freshness | Trigger qualification directly |
| Provide planning context | Make planning decisions |
