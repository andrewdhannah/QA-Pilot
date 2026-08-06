# QA-PILOT-CHECKLIST-REVIEW-PACKET.md — QA Pilot Checklist Review Packet

**Status:** 🔍 Active (sprint #45)
**Authority:** Advisory-only. No approval, seal, execution, write, or sprint-start authority conferred.
**Custody:** QA Pilot-local only. No Librarian mutation permitted.

---

## 1. Purpose

Turn the sealed evidence checklist layer (#44) into an explicit Owner-review packet surface, so checklist readiness can be reviewed without interpreting raw checklist JSON manually. A review packet summarizes checklist posture — item counts by state, blocked items with rationale, overall readiness — into a bounded, reviewable artifact.

---

## 2. Definitions

| Term | Definition |
|------|-----------|
| **Checklist Review Packet** | A QA Pilot-local packet (`CRP-*`) that summarizes an evidence checklist (`EC-*`) for Owner review. |
| **Item Summary** | Count of checklist items by readiness state: total, blocked, degraded, ready. |
| **Overall State** | Aggregate readiness: `blocked` if any required item is blocked, `degraded` if any required item is degraded and none blocked, `ready` if all required items are ready. |
| **Blocked Items** | Items in blocked state with their rationale, surfaced explicitly for Owner attention. |
| **Source Evidence Ref** | Reference to the pipeline evidence that informed the review. |

---

## 3. Schema

The checklist review packet schema is defined at `docs/schemas/qa-pilot-checklist-review-packet.schema.json` (Draft 2020-12).

### 3.1 Required Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `review_packet_id` | string (pattern `^CRP-[A-Z0-9-]+$`) | Unique review packet identifier |
| `source_checklist_id` | string (pattern `^EC-[A-Z0-9-]+$`) | The evidence checklist this reviews |
| `title` | string | Human-readable title |
| `description` | string (min 10 chars) | Review context |
| `item_summary` | object | Counts: total, blocked, degraded, ready |
| `advisory_only` | boolean (`true`) | Always advisory |
| `custody` | string (`qa-pilot-local`) | Local custody only |
| `librarian_impact` | string (`none`) | No Librarian mutation |
| `not_seal_authority` | string (min 20 chars) | Explicit seal-authority disclaimer |
| `not_librarian_mutation_authority` | string (min 20 chars) | Explicit Librarian-mutation disclaimer |
| `created_at` | string (date-time) | ISO 8601 creation timestamp |

### 3.2 Item Summary Fields

| Field | Type | Description |
|-------|------|-------------|
| `total` | integer (>=0) | Total checklist items |
| `blocked` | integer (>=0) | Items in blocked state |
| `degraded` | integer (>=0) | Items in degraded state |
| `ready` | integer (>=0) | Items in ready state |

### 3.3 Overall State

| State | Condition |
|-------|-----------|
| `blocked` | Any required item is blocked |
| `degraded` | Any required item is degraded, none blocked |
| `ready` | All required items are ready |

---

## 4. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| CRP-1 | Review packet must conform to qa-pilot-checklist-review-packet.schema.json | Schema |
| CRP-2 | advisory_only must be true | Schema const |
| CRP-3 | custody must be qa-pilot-local | Schema pattern |
| CRP-4 | librarian_impact must be none | Schema const |
| CRP-5 | not_seal_authority must be present and >= 20 chars | Schema |
| CRP-6 | not_librarian_mutation_authority must be present and >= 20 chars | Schema |
| CRP-7 | source_checklist_id must reference an EC-* pattern | Schema pattern |
| CRP-8 | item_summary total must equal blocked + degraded + ready | Validator |
| CRP-9 | If blocked > 0, blocked_items must be present and non-empty | Schema conditional |
| CRP-10 | No approval, seal, execution, write, or sprint-start authority claimed | Validator |
| CRP-11 | All pipeline refs reference QA Pilot-local custody only | Validator |
| CRP-12 | No Librarian mutation authority referenced | Validator |

---

## 5. Pipeline References

Checklist review packets link to the sealed evidence checklist layer (#44) and the broader advisory pipeline (#33-#43):

| # | Layer | Sprint ID |
|---|-------|-----------|
| 44 | Evidence Checklist | QA-PILOT-EVIDENCE-CHECKLIST-1 |
| 33-43 | Full advisory pipeline | QA-PILOT-MCP-EVIDENCE-INTAKE-1 through QA-PILOT-OWNER-DECISION-RECEIPT-STARTUP-SURFACE-1 |

---

## 6. Authority

- **Advisory-only.** Review packets are advisory artifacts. They do not approve, seal, execute, write, or authorize sprint starts.
- **QA Pilot-local custody.** All review packet data resides within QA Pilot-local paths only.
- **No Librarian mutation.** Review packet validation rejects any reference to Librarian mutation authority.
- **No sealing automation.** Review packets do not trigger or automate sealing.
- **No execution or remediation.** Review packets represent posture only — they do not execute fixes.
- **Existing boundaries preserved.** The #33-#44 advisory-only custody boundaries are unchanged by this contract.

---

## 7. Invariants

| # | Invariant | Enforcement |
|---|-----------|-------------|
| I-1 | All valid review packets must pass schema validation | Schema + validator |
| I-2 | All invalid fixtures must fail schema validation | Validator |
| I-3 | advisory_only=true invariant is unchangeable | Schema const |
| I-4 | custody=qa-pilot-local invariant is unchangeable | Schema pattern |
| I-5 | librarian_impact=none invariant is unchangeable | Schema const |
| I-6 | not_seal_authority must be explicitly stated | Schema |
| I-7 | not_librarian_mutation_authority must be explicitly stated | Schema |
| I-8 | No review packet may claim approval/seal/execute/write authority | Validator |
| I-9 | No review packet may reference Librarian custody | Validator |
| I-10 | All existing #33-#44 validators and test runners remain green | Regression |
