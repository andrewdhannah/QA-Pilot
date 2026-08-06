# QA-PILOT-ASSURANCE-INTELLIGENCE-ARCHITECTURE-1 — Evidence

**Produced by:** #191
**Date:** 2026-07-20
**Status:** Architecture document — defines assurance intelligence layer

---

## 1. Evidence Lineage Model

### Schema

```json
{
  "assurance_lineage": {
    "change_id": "commit-hash-or-reference",
    "detected_at": "ISO8601",
    "changed_files": ["path/to/file1", "path/to/file2"],
    "impact_analysis": {
      "affected_profiles": ["profile-id-1", "profile-id-2"],
      "mapping_basis": "file-pattern → profile mapping"
    },
    "profile_executions": [
      {
        "profile": "privacy",
        "script": "qa_pilot_privacy_assurance_profile.py",
        "executed_at": "ISO8601",
        "evidence_produced": "data/privacy-assurance-evidence.json",
        "overall_finding": "OWNER_DECISION_REQUIRED",
        "checks_run": 6
      }
    ],
    "release_aggregation": {
      "executed_at": "ISO8601",
      "overall": "OWNER_REVIEW_REQUIRED",
      "evidence": "data/release-readiness-evidence.json"
    },
    "owner_decision_context": {
      "findings_requiring_attention": 2,
      "highest_severity": "OWNER_DECISION_REQUIRED",
      "staleness": "fresh"
    }
  }
}
```

### Traceability Rules

| Rule | Description |
|------|-------------|
| Every finding traces to a change | No orphaned findings |
| Every evidence artifact traces to a profile | Clear provenance |
| Every profile execution has a timestamp | Audit trail |
| Owner decision context includes all active findings | Complete picture |

---

## 2. Risk Prioritization Classification

### Classification Model

| Priority | Trigger | Example |
|----------|---------|---------|
| HIGH ATTENTION | Security finding + auth/security change | `OWNER_DECISION_REQUIRED` on authentication module change |
| REVIEW | Privacy/dependency observation + relevant file change | `OBSERVATION` on data handling change |
| MONITOR | Documentation-only change or PERFORMANCE observation | `OBSERVATION` on docs/ change |

### Rules

| Rule | Description |
|------|-------------|
| Priority is advisory | Does not block or approve |
| HIGH ATTENTION requires Owner review | Notification, not gate |
| REVIEW may be deferred | Owner can acknowledge |
| MONITOR is informational | No action required |
| Priority can escalate | Observation becomes REVIEW on same-file repeat change |

---

## 3. Assurance History (Flight Recorder)

### Record Structure

```json
{
  "assurance_history": [
    {
      "sequence": 1,
      "commit": "abc123",
      "timestamp": "ISO8601",
      "profiles_run": ["privacy", "dependency_risk"],
      "findings_before": {"OWNER_DECISION_REQUIRED": 1, "OBSERVATION": 2},
      "findings_after": {"OWNER_DECISION_REQUIRED": 1, "OBSERVATION": 3},
      "decision_state": "OWNER_REVIEW_REQUIRED"
    }
  ]
}
```

### Retention

- History is append-only
- Each commit + continuous assurance loop creates a record
- Records are retained indefinitely
- No deletion — assurance state is part of project evidence

---

## Acceptance Gates

| Gate | Result |
|------|--------|
| AI-1 | PASS — Evidence lineage schema defined (change → profile → finding → evidence → decision) |
| AI-2 | PASS — Change-to-evidence relationships preserved (field-level traceability) |
| AI-3 | PASS — Risk prioritization remains advisory (HIGH ATTENTION / REVIEW / MONITOR, no blocking) |
| AI-4 | PASS — Historical assurance state retention defined (append-only, indefinite) |
| AI-5 | PASS — Librarian boundary preserved (no approval, no compliance claims) |
| AI-6 | PASS — Existing assurance profiles continue unchanged (none modified) |
| AI-7 | PASS — Evidence package produced (this document) |

**7 PASS, 0 FAIL**

---

**Classification:** Advisory architecture definition — does not authorize implementation.
