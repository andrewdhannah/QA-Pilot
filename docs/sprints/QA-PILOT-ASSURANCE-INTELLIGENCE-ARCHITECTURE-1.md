# QA-PILOT-ASSURANCE-INTELLIGENCE-ARCHITECTURE-1 — Assurance Intelligence Architecture

**Type:** assessment / architecture definition
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** assurance
**Boundary:** QA Pilot-local, Librarian advisory boundary
**Dependencies:** #190 (continuous assurance loop)

---

## Purpose

Extend QA Pilot from continuous assurance execution into explainable assurance intelligence. The system can run and refresh evidence; this layer makes that evidence traceable over time — providing lineage, risk context, and historical assurance state.

---

## Deliverables

### Phase 1 — Evidence Lineage Model

| Field | Description |
|-------|-------------|
| change_id | Commit or change reference identifier |
| affected_files | Files changed |
| impacted_profiles | Assurance profiles selected |
| executed_checks | Capabilities run |
| evidence_produced | Evidence file references |
| findings_generated | Findings per profile |
| timestamps | When each stage executed |
| validation_freshness | Age of each evidence artifact |

**Example:**

```json
{
  "change_id": "commit-abc123",
  "affected_profiles": ["security", "privacy"],
  "evidence": ["security-report-188", "privacy-report-186"],
  "finding_state": "OWNER_DECISION_REQUIRED"
}
```

### Phase 2 — Risk Prioritization

**Design principle:** Prioritize without converting evidence into authorization.

**Classification inputs:**

- Assurance profile severity
- Affected system area
- Data sensitivity
- Authentication/security impact
- Evidence age
- Unresolved findings count

**Output:**

```
HIGH ATTENTION → Security finding + authentication change
REVIEW        → Privacy observation + storage modification
MONITOR       → Documentation-only change
```

### Phase 3 — Assurance History (Flight Recorder)

```
Commit → Impact Assessment → Profiles Executed → Evidence Generated
  → Findings Changed → Owner Decisions
```

---

## Scope

### Included

- Evidence lineage schema definition
- Change-to-evidence relationship model
- Risk prioritization classification (advisory only)
- Historical assurance state retention model
- Existing profile compatibility verification

### Explicit Non-Scope

| Excluded | Reason |
|----------|--------|
| Automated risk acceptance | Preserves Owner authority |
| Release authorization | Preserves Librarian boundary |
| Compliance scoring | Preserves decision boundary |
| Replacement of Librarian governance | Not within QA Pilot scope |
| Modification of existing capability contracts | Foundation is stable |

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| AI-1 | Evidence lineage schema defined |
| AI-2 | Change-to-evidence relationships preserved |
| AI-3 | Risk prioritization remains advisory |
| AI-4 | Historical assurance state retention defined |
| AI-5 | Librarian boundary preserved |
| AI-6 | Existing assurance profiles continue unchanged |
| AI-7 | Evidence package produced |

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Ledger entry:** #191 (authorized)
