# Governance Audit Verification — Assurance Control Contract

**Control ID:** GAV-001
**Date:** 2026-08-16
**Status:** OPERATIONAL
**Authority:** Observer — reports evidence, does not decide closure

---

## Purpose

Convert audit completion verification from a remediation artifact into a recurring governance control. The verifier produces evidence; closure remains governance authority.

## Current State → Desired State

```
Current:
  Audit finding → Work order → Implementation → Verification script (manual)

Desired:
  Audit Registry → Verification Runner → Audit Verification Evidence
       → Correlation → Qualification Signal (if drift) → Owner Review
```

## Contract

### Input

```json
{
  "audit_id": "governance-audit-2026-08-16",
  "scope": "all | critical_only | specific_findings",
  "timestamp": "ISO-8601"
}
```

### Output: AuditVerificationResult

```json
{
  "control_id": "GAV-001",
  "audit_id": "governance-audit-2026-08-16",
  "verification_timestamp": "2026-08-16T06:10:00Z",
  "findings_checked": 20,
  "resolved_count": 5,
  "deferred_count": 12,
  "in_progress_count": 2,
  "planned_count": 1,
  "failed_count": 0,
  "missing_evidence": [],
  "verification_status": "PASS | FAIL | DEGRADED",
  "evidence_refs": [
    {
      "finding_id": "AUDIT-001",
      "status": "RESOLVED",
      "receipt": "LCR-WP002-LIBRARIAN-WORKBENCH-001.json",
      "verified_at": "2026-08-16T06:10:00Z"
    }
  ],
  "authority": "none",
  "note": "Verifier reports evidence state. Closure remains governance authority."
}
```

### Semantics

The verifier answers:

| Question | Field |
|---|---|
| "Has every finding been addressed?" | resolved_count = total - deferred - in_progress |
| "Is evidence present for resolved findings?" | missing_evidence[] |
| "Has any evidence drifted?" | correlation with previous verification |
| "What is the overall status?" | verification_status |

The verifier does NOT answer:

| Question | Authority |
|---|---|
| "Is this finding closed?" | Owner decision |
| "Should this finding be reopened?" | Owner decision |
| "Is the evidence sufficient?" | Qualification engine |

## Scheduled Execution

| Cadence | Trigger | Purpose |
|---|---|---|
| Startup | App launch | Baseline verification |
| Milestone | Work order completion | Regression check |
| Owner-requested | Manual | Ad hoc audit |
| Drift-triggered | Evidence change | Divergence detection |

## Governance Loop Integration

```
Audit Registry
      ↓
Verification Runner (GAV-001)
      ↓
Audit Verification Evidence
      ↓
Correlation Engine
      ↓
Qualification Signal (if drift detected)
      ↓
Owner Review (if evidence missing)
```

### Drift Detection

If a previously resolved finding loses its receipt:

```
RESOLVED finding
       ↓
missing evidence detected
       ↓
AUDIT_EVIDENCE_DRIFT signal
       ↓
review required
```

No automatic reopening. The system reports divergence.

### Regression Protection

The verification becomes a gate for:
- Release readiness
- Governance baseline updates
- Major architecture transitions

## Implementation

### Files

| File | Purpose |
|---|---|
| `scripts/verify-governance-audit-completion.py` | Core verification logic |
| `scripts/gav-001-runner.py` | Scheduled runner with evidence persistence |
| `governance-audit-verification-results/` | Verification evidence storage |

### MCP Tool

`governance_audit_verify` — runs verification and returns AuditVerificationResult.

### Evidence Storage

Each verification run produces:
```
governance-audit-verification-results/
  GAV-001-{timestamp}.json    # AuditVerificationResult
  GAV-001-latest.json         # Symlink to most recent
```

## Acceptance Criteria

### G1 — Contract Compliance

Every verification produces AuditVerificationResult with all required fields.

### G2 — Evidence Persistence

Verification results are stored, not just printed.

### G3 — Drift Detection

If evidence disappears between verifications, a signal is generated.

### G4 — No False Closure

The verifier never sets finding status. It only reports evidence state.

### G5 — Cadence Coverage

At least one verification exists for each scheduled cadence.
