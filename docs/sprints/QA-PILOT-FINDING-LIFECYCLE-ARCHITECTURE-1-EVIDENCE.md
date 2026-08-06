# QA-PILOT-FINDING-LIFECYCLE-ARCHITECTURE-1 — Evidence

**Produced by:** #199
**Date:** 2026-07-20
**Status:** Architecture document — defines finding lifecycle management

---

## 1. Finding State Model

### States

```
OPEN
  ↓ (Owner acknowledges)
ACKNOWLEDGED
  ↓ (Owner assigns action)
ACTION_ASSIGNED
  ↓ (Work in progress)
IN_PROGRESS
  ↓ (Resolution evidence produced)
RESOLVED
  ↓ (QA Pilot re-validates)
VERIFIED
```

### Terminal States (No Further Action)

```
ACCEPTED_RISK     — Owner accepts finding without resolution
DEFERRED          — Action postponed to future sprint
NOT_APPLICABLE    — Finding no longer relevant (Owner determination)
```

### Transition Rules

| From | To | Trigger | Authority |
|------|----|---------|-----------|
| OPEN | ACKNOWLEDGED | Owner reviews finding | Owner |
| ACKNOWLEDGED | ACTION_ASSIGNED | Owner assigns owner | Owner |
| ACTION_ASSIGNED | IN_PROGRESS | Work started | Owner/team |
| IN_PROGRESS | RESOLVED | Evidence produced | QA Pilot (advisory) |
| RESOLVED | VERIFIED | QA Pilot re-validates | QA Pilot (advisory) |
| Any | ACCEPTED_RISK | Owner decides | Owner |
| Any | DEFERRED | Owner decides | Owner |
| Any | NOT_APPLICABLE | Owner decides | Owner |
| Any | OPEN | New evidence of same finding | QA Pilot |

**Rule:** QA Pilot proposes resolution verification. Owner accepts risk. No automatic closure.

---

## 2. Owner Acknowledgment Queue

### Structure

```json
{
  "owner_queue": {
    "high_attention": [
      {
        "finding_id": "PRIV-001",
        "description": "Analytics declaration mismatch",
        "state": "OPEN",
        "age_hours": 4,
        "acknowledged": false
      }
    ],
    "review": [
      {
        "finding_id": "DEP-001",
        "description": "Dependency version tracking",
        "state": "ACKNOWLEDGED",
        "assigned_to": "engineering",
        "acknowledged": true
      }
    ]
  }
}
```

### Queue Rules

- HIGH ATTENTION findings must be acknowledged before release readiness can change
- REVIEW findings are informational — acknowledgment optional
- MONITOR findings do not appear in the queue
- Aging HIGH ATTENTION findings escalate after configurable threshold

---

## 3. Resolution Evidence Binding

### Extended Lineage

```json
{
  "finding_lifecycle": {
    "finding_id": "PRIV-001",
    "original_evidence": "data/privacy-assurance-evidence.json",
    "risk_classification": "HIGH_ATTENTION",
    "owner_actions": [
      {
        "action": "ACKNOWLEDGED",
        "by": "Owner",
        "timestamp": "ISO8601"
      },
      {
        "action": "ASSIGNED",
        "to": "engineering",
        "timestamp": "ISO8601"
      }
    ],
    "resolution_evidence": "data/privacy-resolution-evidence.json",
    "final_state": "RESOLVED",
    "verified_at": "ISO8601"
  }
}
```

### Binding Rules

- Resolution evidence is produced by QA Pilot after Owner action
- Resolution does not delete or overwrite the original finding evidence
- History record retains both the finding and its resolution

---

## 4. Escalation Model

### Triggers (Advisory Only)

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Unacknowledged HIGH ATTENTION | > 24 hours | Finding flag: stale |
| Repeated same finding | 3 instances | Flag: recurring pattern |
| New finding on previously resolved area | Any | Re-open finding (advisory) |
| HIGH ATTENTION during release | Any | Release readiness: OWNER_REVIEW_REQUIRED |

### Escalation Rules

- Escalation is advisory — QA Pilot flags, does not block
- Repeated findings are notifications, not automatic blockers
- Re-opened findings retain original history + new evidence

---

## Acceptance Gates

| Gate | Result |
|------|--------|
| FL-1 | PASS — Finding state model defined (7 states + 3 terminal) |
| FL-2 | PASS — Owner acknowledgment queue designed with priority levels |
| FL-3 | PASS — Resolution evidence binding defined (extended lineage) |
| FL-4 | PASS — Escalation model defined (advisory triggers, no automatic blocking) |
| FL-5 | PASS — No automatic finding closure (all transitions require Owner or advisory verification) |
| FL-6 | PASS — Evidence produced (this document) |

**6 PASS, 0 FAIL**

---

**Classification:** Advisory architecture definition — does not authorize implementation.
