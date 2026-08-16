# Cross-System Evidence Exchange Contract

**Sprint:** Cross-System Contract Hardening (#236)
**Status:** ACTIVE — Owner-authorized 2026-08-16

---

## 1. Purpose

Define how external systems submit evidence without becoming governance actors.

## 2. Question

**How does an external system submit evidence without becoming a governance actor?**

## 3. Evidence Submission Requirements

### 3.1 Producer Identity

Every evidence submission must declare:

```json
{
  "producer_identity": {
    "system": "string",
    "component": "string",
    "version": "string",
    "instance_id": "string"
  }
}
```

### 3.2 Evidence Class

Evidence must declare its class:

| Class | Meaning | Authority |
|-------|---------|-----------|
| `observation` | What was observed | No authority |
| `measurement` | Quantitative data | No authority |
| `finding` | Evaluation result | Advisory only |
| `recommendation` | Suggested action | Advisory only |

### 3.3 Timestamps

Every evidence item must have:

- `captured_at` — when the evidence was created
- `submitted_at` — when the evidence was submitted
- `valid_until` — optional expiration

### 3.4 Provenance

Evidence must trace its origin:

```json
{
  "provenance": {
    "source_system": "string",
    "source_component": "string",
    "observation_context": "string",
    "verification_state": "verified | unverified | stale"
  }
}
```

### 3.5 Authority Semantics

Evidence submission MUST NOT:

| Forbidden | Reason |
|-----------|--------|
| Include authorization fields | Evidence does not authorize |
| Include dispatch fields | Evidence does not dispatch |
| Include approval fields | Evidence does not approve |
| Modify governance state | Evidence is observation only |

## 4. Validation Requirements

| Requirement | Rule |
|-------------|------|
| Schema conformance | Evidence must conform to declared schema |
| Provenance completeness | All provenance fields required |
| Timestamp consistency | captured_at <= submitted_at |
| Authority boundary | No authorization fields present |
| Producer identity | Non-empty, valid system identifier |

## 5. Receipt

Successful submission produces:

```json
{
  "receipt_id": "string",
  "evidence_id": "string",
  "producer": "string",
  "received_at": "ISO8601",
  "validation_passed": true,
  "advisory_only": true
}
```
