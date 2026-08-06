# QA-PILOT-ADVISORY-REVIEW-CONSUMER-READINESS.md — QA Pilot Advisory Review Consumer Readiness

**Status:** 🔍 Active (sprint #62)
**Authority:** Advisory-only. No approval, seal, execution, or sprint-start authority conferred.
**Custody:** QA Pilot-local only. No Librarian mutation permitted.

---

## 1. Purpose

Define how QA Pilot sprint completion reports, validator results, startup surface posture, registry state, RCR receipts, PLR state, SUG state, MG state, and Owner-review posture map into a bounded advisory review packet for future consumption by the Librarian Global Advisory Review Mode.

**QA Pilot is a consumer only.** The Librarian owns the global advisory review mode. MCP is the access boundary. Review output is advisory evidence only. The Owner remains the sole seal authority.

---

## 2. QA Pilot Advisory Review Packet Schema

### 2.1 Packet Structure

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `packet_id` | string (pattern `^ARP-[A-Z0-9-]+$`) | yes | Unique advisory review packet identifier |
| `sprint_id` | string | yes | The sprint being reviewed |
| `ledger_number` | integer | yes | Ledger number of the sprint |
| `prior_sealed_head` | string | yes | Prior sealed head before this sprint |
| `claimed_posture` | string | yes | Summary of claimed posture changes |
| `completion_summary` | string (min 20) | yes | Sprint completion description |
| `posture_sections` | object | yes | Current startup surface posture |
| `validator_results` | array | yes | Results from all 7 QA Pilot validators |
| `librarian_impact` | string | yes | Must be "none" |
| `pending_owner_decision` | string | yes | Current Owner decision state |
| `advisory_only` | boolean (true) | yes | Always advisory |
| `defines_new_authority` | boolean (false) | yes | Must be false |
| `mode_owner` | string | yes | Must be "librarian" |
| `created_at` | string (date-time) | yes | Creation timestamp |

### 2.2 Posture Sections

| Sub-field | Source | Description |
|-----------|--------|-------------|
| `sealed_head` | Startup surface | Latest sealed sprint |
| `sealed_number` | Startup surface | Latest sealed number |
| `registry_layer_count` | Startup surface / PLR | Layer registry count |
| `registry_classification` | Startup surface | Registry Posture classification |
| `rcr_receipts_found` | Startup surface / RCR | RCR receipt count |
| `rcr_status` | Startup surface | RCR posture status |
| `rcg_coverage_gap` | Startup surface / RCG | Closeout gate gap |
| `rcg_status` | Startup surface | RCG status |
| `srs_captured_at` | Startup surface / SUG | SRS snapshot capture point |
| `srs_current` | Startup surface / SUG | Whether snapshot is current |

### 2.3 Validator Results

Each validator result includes:
- `validator`: validator script name
- `status`: "pass", "fail", or "absent"
- `summary`: one-line result summary

Required validators: surface validate, SRS, SUG, RCR, RCG, PLR, MG.

---

## 3. Business Rules

| Rule | Description |
|------|-------------|
| AR-1 | Packet conforms to advisory review packet schema |
| AR-2 | advisory_only must be true |
| AR-3 | defines_new_authority must be false |
| AR-4 | mode_owner must be "librarian" |
| AR-5 | librarian_impact must be "none" |
| AR-6 | Packet must not contain approve/seal/execute verbs as actions |
| AR-7 | All 7 posture sections must be present or marked absent |
| AR-8 | All 7 validator results must be present or marked absent |
| AR-9 | Packet preserves Owner review/seal boundary |
| AR-10 | No authority claims in descriptions |

---

## 4. Authority

- **Advisory-only.** Review packets are advisory evidence. They do not approve, seal, execute, or authorize sprint starts.
- **QA Pilot is consumer.** The Librarian owns the global advisory review mode.
- **No Librarian mutation.** No Librarian files modified.
- **Owner remains sole seal authority.** No automation may seal based on review packets.
- **No MCP implementation.** This sprint defines the packet contract only.

---

## 5. Invariants

| # | Invariant | Enforcement |
|---|-----------|-------------|
| I-1 | All valid packets must pass schema validation | Schema + validator |
| I-2 | All invalid fixtures must fail validation | Validator |
| I-3 | advisory_only=true is unchangeable | Schema const |
| I-4 | defines_new_authority=false is unchangeable | Schema const |
| I-5 | mode_owner="librarian" is unchangeable | Schema const |
| I-6 | librarian_impact="none" is unchangeable | Schema const |
| I-7 | No packet may claim approval/seal/execute authority | Validator |
| I-8 | All existing #33-#62 validators remain green | Regression |
