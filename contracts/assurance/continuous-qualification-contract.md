# Continuous Qualification Contract

**Sprint:** QA-PILOT-CONTINUOUS-QUALIFICATION-1 (#226)
**Status:** ACTIVE — Authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the controlled requalification lifecycle when assurance-relevant state changes. Establish trigger classes, qualification run records, and append-only history invariants.

## 2. Trigger Classes

| Trigger Type | Source | Response | Authority |
|--------------|--------|----------|-----------|
| `evidence_change` | New runtime event ingested | Requalify affected profile | observation_only |
| `capability_change` | Capability declaration updated | Requalify capability profile | observation_only |
| `finding_change` | New finding pattern detected | Recalculate risk | observation_only |
| `freshness_expiry` | Evidence window exceeded | Flag for requalification | observation_only |
| `policy_change` | Qualification baseline updated | Requalify all affected | observation_only |

## 3. Qualification Run Record

Every execution produces a new immutable record:

```json
{
  "qualification_run_id": "QCR-20260816-001",
  "trigger": {
    "trigger_type": "evidence_change",
    "source_ref": "RAE-20260816T040741-32f10699",
    "triggered_at": "2026-08-16T04:25:00Z",
    "triggered_by": "system"
  },
  "profile": "runtime-evidence-qualification-v1",
  "input_refs": [
    "RAE-20260816T040741-32f10699"
  ],
  "result": {
    "disposition": "PASS",
    "findings_count": 0,
    "qr_record_id": "QR-20260816-001"
  },
  "authority": "observation_only",
  "executed_at": "2026-08-16T04:25:01Z",
  "executed_by": "scripts/continuous-qualification.py"
}
```

## 4. Append-Only History

The qualification history is append-only:

```
Run 001: PASS    (2026-08-16T04:25:00Z)
Run 002: PASS    (2026-08-16T04:30:00Z)
Run 003: FINDING (2026-08-16T04:35:00Z)
```

**Never:**
- Modify an existing run record
- Delete a run record
- Reorder run records

**Only:**
- Append new run records
- Query historical records

## 5. Trigger Evaluation

### 5.1 Evidence Change Trigger

When new evidence is ingested:
1. Check if evidence affects any qualification profile
2. If yes, create qualification trigger
3. Trigger qualification execution
4. Append result to history

### 5.2 Freshness Expiry Trigger

When evidence ages beyond threshold:
1. Check freshness state of all projects
2. If any project has stale critical evidence, create trigger
3. Trigger requalification
4. Append result to history

### 5.3 Finding Change Trigger

When new findings are detected:
1. Check if finding pattern has changed
2. If new pattern detected, create trigger
3. Trigger risk recalculation
4. Append result to history

## 6. Deterministic Replay

Same inputs must produce same outputs:

```
qualify(evidence_set, profile, baseline) → result
qualify(evidence_set, profile, baseline) → result  (same output)
```

**Requirements:**
- No randomness
- No time-dependent scoring (except timestamps)
- No external state dependencies
- Deterministic qualification engine

## 7. Failure Isolation

One failed qualification must not disable others:

```
Run 001: PASS     (project A)
Run 002: ERROR    (project B — isolated failure)
Run 003: PASS     (project C)
```

Project B's failure does not affect A or C.

## 8. Risk Integration Chain

```
Evidence Change
       │
       △
Qualification Trigger
       │
       △
Qualification Run → QR-* Record
       │
       △
Finding Pattern Update
       │
       △
Risk Recalculation
       │
       △
Discovery Projection Update
```

## 9. Authority Boundary

The continuous qualification engine:

| May Do | May Not Do |
|--------|------------|
| Create qualification triggers | Create work packets |
| Execute qualification runs | Assign owners |
| Append QR-* records | Close findings |
| Update risk state | Approve remediation |
| Update discovery projection | Dispatch tasks |
| Produce recommendations | Make Owner decisions |

## 10. LINK Readiness Interface

```python
def get_assurance_state(project_id: str = None) -> dict:
    """
    Returns current assurance state.
    
    If project_id provided, returns single project state.
    If None, returns fleet state.
    
    Returns:
        {
            "projects": [...],
            "fleet_summary": {...},
            "last_qualification": "ISO8601",
            "qualification_count": int
        }
    """
    pass

def get_latest_qualification(project_id: str) -> dict:
    """
    Returns latest qualification result for a project.
    
    Returns:
        {
            "qualification_run_id": "string",
            "disposition": "PASS" | "FINDING",
            "findings_count": int,
            "executed_at": "ISO8601",
            "trigger": {...}
        }
    """
    pass

def get_risk_state(project_id: str = None) -> dict:
    """
    Returns risk state. Delegates to risk engine.
    """
    pass
```
