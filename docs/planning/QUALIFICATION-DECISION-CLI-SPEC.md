# Qualification Decision Packet CLI Spec

**Part of:** QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1
**Tier:** T2 (Required for Operationalization)
**Prepared:** 2026-07-16
**Status:** Proposed — CLI interface specification

---

## 1. Design

Follow the existing QA Pilot decision packet pattern from sealed sprint #90 (`QA-PILOT-REVIEW-DEPTH-THRESHOLDS-DECISION-PACKET-1`).

**Pattern reference:** `scripts/qa_pilot_review_depth_thresholds_decision_packet.py`
**Target script:** `scripts/qa_pilot_qualification_decision.py`
**Output format:** CLI-generated Markdown + structured receipt

## 2. CLI Interface

```
qa-pilot qualification decision <command> [options]

Commands:
  create     Create a new qualification decision packet
  list       List qualification decision packets
  read       Read a specific decision packet
  validate   Validate a decision packet against schema
  status     Show decision packet store status

Global options:
  --format <text|json>    Output format (default: text)
  --store <path>          Override decision store path
```

### 2.1 `create`

```
qa-pilot qualification decision create \
  --target-id <target_id> \
  --qualification-type <artifact|process|reviewer> \
  --qualification-level <level> \
  --reason "<decision rationale>" \
  --decision <accept|defer|reject|modify> \
  [--owner-note "<note>"] \
  [--supersedes <record-id>] \
  [--dry-run]
```

**Generates:**
- `docs/decisions/QUALIFICATION-DECISION-XXXX.md` — Markdown decision document
- Receipt in decision store (`data/qualification-decisions/`)

**Output (Markdown):**
```markdown
# Qualification Decision — QUALIFICATION-DECISION-0001

**Target:** <target_id>
**Type:** <qualification_type>
**Level:** <qualification_level>
**Decision:** <accept|defer|reject|modify>
**Date:** 2026-07-16
**Assessor:** OpenWork (DeepSeek V4 Flash)

## Rationale
<reason>

## Supporting Evidence
- <evidence ref 1>
- <evidence ref 2>

## Authority Disclaimer
This decision packet connects qualification posture to Owner review.
It does not authorize implementation, seal, ledger mutation,
or cross-project writes. Custody is qa-pilot-local.
Librarian impact is none.
```

### 2.2 `list`

```
qa-pilot qualification decision list [--status <status>] [--limit <n>]
```

Lists decision packets with ID, target, level, decision, date.

### 2.3 `read`

```
qa-pilot qualification decision read <decision-id>
```

Prints full decision packet in text or JSON format.

### 2.4 `validate`

```
qa-pilot qualification decision validate [<decision-id>]
```

Validates decision packet(s) against schema. Returns pass/fail with rule violations.

### 2.5 `status`

```
qa-pilot qualification decision status
```

Shows store statistics: total packets, by decision type, by level, latest packet.

## 3. Decision Packet Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Qualification Decision Packet",
  "type": "object",
  "required": [
    "packet_id",
    "target_id",
    "qualification_type",
    "qualification_level",
    "decision",
    "rationale",
    "assessed_at",
    "assessed_by",
    "advisory_only",
    "custody",
    "librarian_impact"
  ],
  "properties": {
    "packet_id": { "type": "string", "pattern": "^QUALIFICATION-DECISION-[0-9]{4}$" },
    "target_id": { "type": "string" },
    "qualification_type": { "type": "string", "enum": ["artifact", "process", "reviewer"] },
    "qualification_level": { "type": "string", "enum": ["unqualified", "spot_checked", "peer_reviewed", "audited", "exempt"] },
    "decision": { "type": "string", "enum": ["accept", "defer", "reject", "modify"] },
    "rationale": { "type": "string", "minLength": 1 },
    "owner_note": { "type": "string" },
    "supersedes": { "type": "string" },
    "evidence_refs": {
      "type": "array",
      "items": { "type": "object" }
    },
    "assessed_at": { "type": "string", "format": "date-time" },
    "assessed_by": { "type": "string" },
    "advisory_only": { "type": "boolean", "const": true },
    "custody": { "type": "string", "const": "qa-pilot-local" },
    "librarian_impact": { "type": "string", "const": "none" }
  }
}
```

## 4. Validation Rules

| Rule | Check | Error Message |
|------|-------|---------------|
| QD-1 | advisory_only must be True | `advisory_only must be True` |
| QD-2 | custody must be qa-pilot-local | `custody must be qa-pilot-local` |
| QD-3 | librarian_impact must be 'none' | `librarian_impact must be 'none'` |
| QD-4 | decision must be valid enum | `decision must be accept/defer/reject/modify` |
| QD-5 | rationale must not be empty | `rationale must not be empty` |
| QD-6 | no authority-claiming fields | `forbidden field claims authority` |
| QD-7 | no seal/approval/verify language | `rationale contains authority-claiming term` |
| QD-8 | no registry/RCR/SRS fields | `packet carries registry/RCR/SRS field` |
| QD-9 | packet_id must be unique | `packet_id already exists` |
| QD-10 | target_id must resolve | `target_id not found in QA Pilot layers` |
