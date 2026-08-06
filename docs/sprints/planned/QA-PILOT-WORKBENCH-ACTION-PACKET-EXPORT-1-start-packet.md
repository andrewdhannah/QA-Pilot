# Start Packet — QA-PILOT-WORKBENCH-ACTION-PACKET-EXPORT-1

**Type:** Implementation — action packet export surface
**Status:** 🔍 Start packet prepared — awaiting Owner authorization
**Predecessor:** QA-PILOT-WORKBENCH-OWNER-ACTION-PACKET-STARTUP-SURFACE-1 (sealed #79)
**QA Pilot ledger head:** #79

---

## 1. Objective

Add an export surface for QA Pilot workbench action packets so bounded owner action packets can be packaged for downstream execution/review handoff without executing them, mutating source records, or authorizing execution.

## 2. Motivation

QA Pilot's workbench can define action packets, review decisions, intake records, and workbench items, but there is no clean export surface that packages these into a bounded deliverable for handoff to a downstream consumer (e.g., Librarian execution lane, Owner review queue, or regression test lane). The export must be read-only, custodial, and explicitly non-authorizing.

## 3. Scope

### Will Do

1. **Export packet schema** — define the JSON schema for a bounded action-packet export
2. **Bind export to these source IDs:**
   - Action packet ID
   - Review decision receipt ID
   - Decision summary ID
   - Intake ID
   - Workbench item ID
   - Evidence IDs (one or more)
3. **CLI commands:**
   - `action-export` — create an export packet from source IDs
   - `action-export-read` — read a specific export by ID
   - `action-export-list` — list all exports
   - `action-export-validate` — validate an export against schema
   - `action-export-status` — show export store status
4. **Storage:** `data/workbench-action-packet-exports/`
5. **Validator rules** rejecting these claims in export artifacts:
   - Execution authority
   - Authorization to proceed
   - Seal or approval status
   - Verification completion
   - Closure of source items
   - Source record mutation
   - Any claim of canonical effect
6. **Preserve advisory/custodial language** in all export artifacts

### Will Not Do

- ❌ No execution of exported work
- ❌ No authorization of downstream execution
- ❌ No approval of intakes or evidence
- ❌ No verification of evidence
- ❌ No closure of workbench items or action packets
- ❌ No mutation of source records or packets
- ❌ No seal creation
- ❌ No canonical effect claims
- ❌ No changes to Librarian startup protocol, regression cadence, or must-fix sprints

## 4. Authority Boundary

| Rule | Value |
|------|-------|
| Authority mode | advisory/custodial |
| Execution authority | explicitly denied |
| Authorization authority | explicitly denied |
| Seal authority | explicitly denied |
| Source mutation | explicitly denied |
| Canonical effect | explicitly denied |
| Production mutation allowed | `false` |

## 5. Acceptance Criteria

- [ ] Export packet schema defined and valid JSON
- [ ] Export binds to all 6 source ID types
- [ ] 5 CLI commands implemented
- [ ] Exports stored under `data/workbench-action-packet-exports/`
- [ ] Validator rejects execution, authorization, seal, approval, verification, closure, source mutation claims
- [ ] All export artifacts use advisory/custodial language
- [ ] Positive fixture (valid export) passes validator
- [ ] Negative fixture (export claiming execution authority) fails validator

## 6. Pre-requisites

- [x] QA-PILOT-WORKBENCH-OWNER-ACTION-PACKET-STARTUP-SURFACE-1 sealed (#79)
- [x] QA Pilot ledger at #79
- [x] Workbench infrastructure exists
- [x] Review decision receipt infrastructure exists

## 7. Start Packet Metadata

```
packet_id: START-PACKET-QA-ACTION-EXPORT-001
prepared_at: 2026-07-08T06:20:00Z
prepared_by: OpenWork agent
status: awaiting_owner_authorization
authority_mode: advisory/custodial
qa_pilot_ledger_head: 79
predecessor: QA-PILOT-WORKBENCH-OWNER-ACTION-PACKET-STARTUP-SURFACE-1
```
