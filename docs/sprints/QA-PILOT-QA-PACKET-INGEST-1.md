# QA-PILOT-QA-PACKET-INGEST-1 — QA Pilot QA Packet Ingest

**Type:** QA Pilot-side implementation
**Lane:** `parallel_planning`
**Boundary:** `qa_pilot_local`
**Librarian impact:** `none`
**Status:** `active`
**Input dependency:** LIBRARIAN-QA-PACKET-EXPORT-1 (sealed Librarian export packets)
**Authorization:** OD-QA-PILOT-QA-PACKET-INGEST-1 (2026-07-05)

---

## Intent

Implement QA Pilot-local ingestion of governed Librarian QA export packets. Define the schema, validation rules, fixtures, validator, test runner, and ingest CLI so QA Pilot can consume Librarian export packets as advisory/derived/non-authoritative local copies.

This is the QA Pilot-side of the cross-project MCP bridge: packet ingest only. No regression suite, no training sim, no Librarian mutation.

## Summary

Created QA Pilot-local packet ingestion pipeline with 4 valid + 4 invalid fixtures, 14 validation rules (PI-1 through PI-14), validator, test runner (22 tests), governance doc, and ingest CLI (validate/ingest/list/status/clear commands).

## What Changed

### Schema (`docs/schemas/qa-pilot-qa-packet-ingest.schema.json`)
- Draft 2020-12 schema with 11 required custody fields
- Allowed packet types: `qa_claim_registry`, `project_state`, `milestone_regression`, `training_source`
- Authority status: `authoritative_export`, `advisory_copy`, `training_simulated`
- Enforces SHA-256 hash, ISO 8601 UTC timestamp, owner decision required
- Conditional validation: authoritative_export must have payload

### Fixtures (8 total in `docs/examples/qa-pilot-qa-packet-ingest/`)

| Fixture | Type | Purpose |
|---------|------|---------|
| `valid-claim-registry-packet.json` | Valid | Claim registry export from Librarian |
| `valid-project-state-packet.json` | Valid | Project-state snapshot |
| `valid-milestone-regression-packet.json` | Valid | Milestone regression data (advisory_copy) |
| `valid-training-source-packet.json` | Valid | Training source (training_simulated) |
| `invalid-wrong-source-project.json` | Invalid | `source_project` is `qa-pilot`, not `librarian` |
| `invalid-missing-custody-hash.json` | Invalid | Empty `source_packet_hash` |
| `invalid-owner-decision-not-required.json` | Invalid | `owner_decision_required_for_apply` is `false` |
| `invalid-mutation-capable.json` | Invalid | Payload contains `seal_action` key |

### Validator (`scripts/validate-qa-pilot-qa-packet-ingest.py`)
14 rules:

| Rule | Coverage |
|------|----------|
| PI-1 | packet_type known type |
| PI-2 | source_project is librarian |
| PI-3 | consumer_project is qa-pilot |
| PI-4 | authority_status valid |
| PI-5 | authoritative_export has payload |
| PI-6 | generated_at ISO 8601 UTC |
| PI-7 | source_packet_hash SHA-256 |
| PI-8 | allowed_use no forbidden |
| PI-9 | forbidden_use complete |
| PI-10 | owner_decision_required_for_apply true |
| PI-11 | no Librarian mutation payload |
| PI-12 | training_simulated use correct |
| PI-13 | generated_at not future |
| PI-14 | No Librarian runtime refs in docs |

### Test Runner (`scripts/test-qa-pilot-qa-packet-ingest.sh`)
22 tests covering: validator existence, --list-rules, valid fixtures pass, invalid fixtures reject, all 8 fixtures exist, CLI existence, CLI --help, CLI validate (accept/reject), CLI list, CLI status, CLI ingest (import valid packet), CLI clear, governance doc exists, schema valid JSON, PI-14 scan, regression checks on existing QA Pilot validators, valid fixture names, ledger validity, prohibited-zone scan.

### Ingest CLI (`scripts/qa_pilot_qa_packet_ingest.py`)

| Command | Description |
|---------|-------------|
| `validate <path>` | Validate a packet without storing |
| `ingest <path>` | Validate and import into local derived store |
| `list` | List ingested packets |
| `status` | Show ingestion store status |
| `clear` | Clear all ingested packets |

Storage: `data/packets/ingested/` with index at `data/packets/ingested-index.json`.

Each stored record: `ingest_id`, `packet_type`, `source_project`, `authority_status`, `generated_at`, `source_packet_hash`, `store_path`, `ingested_at`, `advisory=True`, `cross_project_write_authorized=False`, `owner_apply_required=True`.

### Governance Doc (`docs/governance/QA-PILOT-QA-PACKET-INGEST.md`)
8 sections: Purpose, Ingestion Rules, Authority Classification, Stored Packet Record, Boundary Rules, Cross-Project Safety, Dependencies, Reference.

## Verification

### Packet Ingest Validator (14 rules)

```
✅ ALL CHECKS PASS
PI-1 through PI-14: all pass
```

### Packet Ingest Test Runner (22 tests)

```
22/22 passed. All tests pass.
```

### Regression: Broader QA Pilot Validators

| Validator | Result |
|-----------|--------|
| Broker plan validator | ✅ PASS |
| Broker audit store validator | ✅ PASS |
| Receipt validator | ✅ PASS |
| (and all others still pass) | ✅ |

### Boundary Scan

| Scan | Result |
|------|--------|
| Prohibited-zone scan | ✅ CLEAN — no QA Pilot packet-ingest files in Librarian |
| PI-14 scan | ✅ No Librarian runtime references in ingestion docs |
| Cross-project write | ✅ All ingested packets marked NOT AUTHORIZED |

## Files Changed

```
Created:
  docs/schemas/qa-pilot-qa-packet-ingest.schema.json
  docs/examples/qa-pilot-qa-packet-ingest/valid-claim-registry-packet.json
  docs/examples/qa-pilot-qa-packet-ingest/valid-project-state-packet.json
  docs/examples/qa-pilot-qa-packet-ingest/valid-milestone-regression-packet.json
  docs/examples/qa-pilot-qa-packet-ingest/valid-training-source-packet.json
  docs/examples/qa-pilot-qa-packet-ingest/invalid-wrong-source-project.json
  docs/examples/qa-pilot-qa-packet-ingest/invalid-missing-custody-hash.json
  docs/examples/qa-pilot-qa-packet-ingest/invalid-owner-decision-not-required.json
  docs/examples/qa-pilot-qa-packet-ingest/invalid-mutation-capable.json
  scripts/validate-qa-pilot-qa-packet-ingest.py
  scripts/test-qa-pilot-qa-packet-ingest.sh
  scripts/qa_pilot_qa_packet_ingest.py
  docs/governance/QA-PILOT-QA-PACKET-INGEST.md
  docs/sprints/QA-PILOT-QA-PACKET-INGEST-1.md
  receipts/decision-resolutions/od-qa-pilot-qa-packet-ingest-1.json
  (ledger update)

Not modified:
  SessionStartup/ (unchanged)
  .librarian/ (unchanged)
  active/librarian/ (unchanged)
  startup-contract.json (unchanged)
  project-index.json (unchanged)
```

## Acceptance Gates

| Gate | Status |
|------|--------|
| Packet ingestion schema drafted | ✅ |
| 4 valid fixtures pass validation | ✅ |
| 4 invalid fixtures rejected | ✅ |
| PI-1 through PI-14 enforced | ✅ |
| Ingest CLI validate command works | ✅ |
| Ingest CLI ingest stores packet with advisory flag | ✅ |
| Ingest CLI list/status/clear work | ✅ |
| Governance doc defines boundary rules | ✅ |
| No Librarian files changed | ✅ |
| No cross-project write paths created | ✅ |
| Existing QA Pilot validators still pass | ✅ |
| All ingested packets marked advisory/cross-project-write-denied | ✅ |

## Upstream Dependencies

| Sprint | Relationship | Status |
|--------|-------------|--------|
| LIBRARIAN-QA-PACKET-EXPORT-1 | Sealed upstream — Librarian export surfaces | ✅ Sealed |
| QA-PILOT-CROSS-PROJECT-MCP-QA-BRIDGE-PLAN-1 | Design authority — bridge architecture | 🔍 Pending Owner review |

## Next Authorized QA Pilot Sprints

1. **QA-PILOT-MILESTONE-REGRESSION-SUITE-1** — regression against ingested packets
2. **QA-PILOT-LOCAL-TRAINING-SIM-1** — training sim from ingested packets
