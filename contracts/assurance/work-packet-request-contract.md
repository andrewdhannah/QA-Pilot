# Work Packet Request Contract

**Sprint:** QA-PILOT-WORK-PACKET-INTEGRATION-1 (#243)
**Status:** ACTIVE — Owner-authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the translation from accepted improvement proposals to work packet creation requests.

## 2. Handoff Rules

| Input | Condition | Output |
|-------|-----------|--------|
| Accepted proposal | status = "accepted" | Work packet request |
| Rejected proposal | status = "rejected" | No output, no penalty |
| Pending proposal | status = "pending_owner_review" | No output |

## 3. Request Record

```json
{
  "request_id": "WPR-001",
  "proposal_id": "IP-001",
  "project_id": "agent-bridge",
  "created_at": "2026-08-16T06:30:00Z",
  "recommendation_refs": ["PR-001"],
  "evidence_refs": ["CD-001"],
  "risk_context": {
    "current_risk": 42,
    "risk_band": "monitor"
  },
  "owner_decision_id": "OD-001",
  "requested_scope": "evidence_enhancement",
  "expected_outcome": "Improved evidence coverage",
  "status": "submitted",
  "work_packet_id": null,
  "advisory_only": true
}
```

## 4. Translation Rules

| Proposal Field | Request Field | Transform |
|----------------|---------------|-----------|
| proposal_id | proposal_id | Direct reference |
| recommendation_refs | recommendation_refs | Direct reference |
| evidence_refs | evidence_refs | Direct reference |
| risk_context | risk_context | Direct copy |
| expected_outcome | expected_outcome | Direct copy |
| owner_decision | owner_decision_id | Reference to decision record |

## 5. Non-Authority Boundary

Work packet requests:

| May Do | May Not Do |
|--------|------------|
| Translate proposals | Create work packets directly |
| Reference evidence | Dispatch agents |
| Include context | Assign owners |
| Submit to Librarian | Modify lifecycle |
| Await Librarian processing | Approve execution |
