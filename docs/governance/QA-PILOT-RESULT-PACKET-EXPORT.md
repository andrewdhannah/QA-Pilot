# QA Pilot Result Packet Export — Governance

**Sprint:** QA-PILOT-RESULT-PACKET-EXPORT-1
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Authority:** advisory-only

## Purpose

Export advisory QA result packets from QA Pilot-local evidence packets and composed test cases. Result packets are stored in QA Pilot-local custody for Owner/Librarian review.

## Architecture

```
evidence store (data/evidence/) ──┐
                                  ├──→ result export ──→ result-packet store
test-case store (data/test-cases/)─┘      (data/result-packets/)
```

## RP Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| RP-1 | Reads only QA Pilot-local evidence and test-case stores | Paths check |
| RP-2 | Result packets reference source evidence packet IDs | `provenance.evidence_packets` |
| RP-3 | Result packets reference composed test case IDs | `provenance.test_cases` |
| RP-4 | Result packets include `advisory: true` | Schema const + export enforcement |
| RP-5 | Result packets validate against `qa-result-packet.schema.json` | Schema validation |
| RP-6 | Result packets preserve source_project metadata | Provenance chain |
| RP-7 | No approve/seal/start/advance authority verbs | FORBIDDEN_AUTHORITY_VERBS |
| RP-8 | No source-project mutation paths | `/Sources/`, `/Public/`, `/.librarian/` blocked |
| RP-9 | Malformed evidence or test cases rejected | Required fields check |
| RP-10 | Duplicate export is deterministic | Unique result_id per export |
| RP-11 | Result-packet index is QA Pilot-local only | `data/result-packets/` paths |
| RP-12 | Existing evidence intake and test composition remain green | Validated in test runner |
| RP-13 | Existing custody/startup/architecture regressions remain green | Validated in test runner |

## Result Packet Schema (qa-result-packet.schema.json)

| Field | Required | Description |
|-------|----------|-------------|
| `result_id` | Yes | Pattern `^QR-` |
| `sprint_ids` | Yes | Array of referenced sprint IDs |
| `summary` | Yes | `tests_passed`, `tests_failed`, `defects_found` |
| `advisory` | Yes | Must be `true` |
| `owner_action_required` | Yes | Must be `true` |
| `findings` | Yes | Array of finding objects |
| `exported_at` | Yes | ISO 8601 timestamp |
| `provenance` | No | Evidence and test case references |

## Forbidden

- Writing to Librarian project files
- Mutating Librarian ledgers, receipts, status surfaces, or startup state
- Creating Librarian receipts
- Approving or sealing any sprint
- Treating exported results as Owner decisions
- Importing result packets into Librarian as authority
- Executing fixes or patches based on result packets

## Commands

```
export [--source-evidence PID] [--source-test TC-ID]  Export result packet
validate <path>                     Validate a result packet file
list [--limit N]                    List exported result packets
read <result_id>                    Read an exported result packet
status                              Show store status
clear                               Clear all exported result packets
```
