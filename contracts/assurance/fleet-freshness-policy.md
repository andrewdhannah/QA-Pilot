# Fleet Freshness Policy Contract

**Sprint:** QA-PILOT-FLEET-FRESHNESS-DISCOVERY-1 (#224)
**Status:** ACTIVE — Authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the freshness policy for fleet-wide evidence assessment. Establish how QA-Pilot determines whether evidence is current, aging, stale, or unknown across governed projects.

## 2. Critical Distinction: Freshness ≠ Quality

| Concept | Meaning | Example |
|---------|---------|---------|
| **Freshness** | How recent is the evidence? | "This snapshot was captured 5 minutes ago" |
| **Quality** | Is the evidence passing or failing? | "This qualification result is a FINDING" |

**Fresh evidence can be bad.** A fresh failing qualification = attention needed NOW.
**Old evidence can be valid.** A historical record = still valid proof, just not recent.

**Rule:** Freshness assessment must never conflate age with correctness.

## 3. Freshness Windows

### 3.1 Record Semantics (Immutable Events)

Records are historical proof. Age does not invalidate them.

| Label | Age Range | Meaning |
|-------|-----------|---------|
| `current` | < 60 minutes | Recently produced. Active evidence. |
| `historical` | 60 min – 4 hours | Valid historical proof. Not recent, but still reliable. |
| `archived` | >= 4 hours | Long-term evidence. Valid as history, not as current state. |

**Rule:** Records NEVER get the `stale` label. A 7-day-old record is `archived`, not `stale`.

### 3.2 Snapshot Semantics (Mutable State)

Snapshots are current-state observations. Age invalidates them.

| Label | Age Range | Meaning |
|-------|-----------|---------|
| `current` | < 15 minutes | Recent observation. State is likely still valid. |
| `aging` | 15 – 60 minutes | Observation is getting old. State may have changed. |
| `stale` | > 60 minutes | Observation is outdated. State may be significantly different. |

**Rule:** Snapshots that exceed their refresh interval are `stale`, not `archived`.

### 3.3 Unknown State

| Condition | Label | Meaning |
|-----------|-------|---------|
| No evidence exists | `unknown` | Cannot assess freshness. Coverage gap. |
| Evidence exists but timestamps missing | `unknown` | Cannot compute age. |
| Evidence class cannot be determined | `unknown` | Cannot apply correct freshness model. |

## 4. Coverage Model

### 4.1 Coverage Domains

| Domain | Evidence Types | Required for |
|--------|---------------|--------------|
| `runtime_action` | Action events | Runtime assurance |
| `runtime_lifecycle` | Lifecycle events | Runtime assurance |
| `runtime_resource` | Resource observations | Runtime assurance |
| `qualification` | QR-* records | Qualification assurance |
| `security` | Security findings | Security assurance |
| `accessibility` | A11y findings | Accessibility assurance |

### 4.2 Coverage States

| State | Condition | Meaning |
|-------|-----------|---------|
| `full` | All expected domains have current evidence | Comprehensive coverage |
| `partial` | Some domains have evidence, others missing or stale | Gaps exist |
| `minimal` | Only essential domains have evidence | Basic coverage only |
| `none` | No evidence in any domain | No coverage |
| `unknown` | Cannot determine coverage | Assessment impossible |

### 4.3 Coverage Assessment Algorithm

```
For each project:
  For each domain:
    If domain has evidence AND freshness != stale:
      domain_status = covered
    Else:
      domain_status = uncovered
  
  If all domains covered:
    coverage = full
  If >= 50% domains covered:
    coverage = partial
  If only essential domains covered:
    coverage = minimal
  If no domains covered:
    coverage = none
  If cannot determine:
    coverage = unknown
```

## 5. Freshness Assessment Output

### 5.1 Per-Project Assessment

```json
{
  "project_id": "librarian",
  "freshness_state": "current",
  "coverage_state": "partial",
  "domains": {
    "runtime_action": { "status": "covered", "freshness": "current", "count": 1 },
    "runtime_lifecycle": { "status": "uncovered", "freshness": "unknown", "count": 0 },
    "runtime_resource": { "status": "uncovered", "freshness": "unknown", "count": 0 },
    "qualification": { "status": "covered", "freshness": "historical", "count": 5 },
    "security": { "status": "uncovered", "freshness": "unknown", "count": 0 },
    "accessibility": { "status": "uncovered", "freshness": "unknown", "count": 0 }
  },
  "missing_domains": ["runtime_lifecycle", "runtime_resource", "security", "accessibility"],
  "last_qualification": "2026-08-16",
  "recommendations": [
    "Consider adding runtime lifecycle event capture",
    "Consider adding security evidence"
  ]
}
```

### 5.2 Fleet Summary

```json
{
  "generated_at": "2026-08-16T04:10:00Z",
  "total_projects": 2,
  "projects_by_freshness": {
    "current": 1,
    "aging": 0,
    "stale": 0,
    "unknown": 1
  },
  "projects_by_coverage": {
    "full": 0,
    "partial": 1,
    "minimal": 1,
    "none": 0,
    "unknown": 0
  },
  "attention_needed": [
    {
      "project_id": "librarian",
      "reason": "partial coverage with uncovered domains",
      "priority": "medium"
    }
  ]
}
```

## 6. Advisory Boundary

### 6.1 Allowed Output

| Output Type | Example |
|-------------|---------|
| Observation | "Librarian has partial runtime evidence coverage" |
| Recommendation | "Consider adding runtime lifecycle event capture" |
| Priority signal | "QA-Pilot needs attention: stale snapshots" |

### 6.2 Forbidden Output

| Output Type | Example |
|-------------|---------|
| Scheduling | "Run accessibility qualification on 2026-08-17" |
| Dispatch | "Send qualification task to agent" |
| Mutation | "Update project evidence store" |
| Authorization | "Approve remediation for coverage gap" |

**Rule:** The discovery engine recommends. The Owner decides. The system does not act.

## 7. LINK Readiness Interface

Future LINK integration will consume:

```python
def get_project_assurance_state(project_id: str) -> dict:
    """
    Returns assurance state for a project.
    
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
            "qualification_age": "ISO8601 duration since last qualification"
        }
    """
    pass
```

This interface is defined now but NOT implemented. LINK will consume it in a future sprint.
