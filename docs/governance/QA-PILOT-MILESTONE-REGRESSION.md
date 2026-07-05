# QA Pilot Milestone Regression — Governance Document

**Sprint:** QA-PILOT-MILESTONE-REGRESSION-SUITE-1
**Lane:** parallel_planning
**Boundary:** QA Pilot-local only
**Authority:** advisory-only. No cross-project write authority.

---

## 1. Purpose

Define and execute a regression suite that proves the sealed QA Pilot QA packet ingest chain (QA-PILOT-QA-PACKET-INGEST-1, ledger #17) remains stable. The regression suite locks the following invariants:

| Invariant | MR Rule | Description |
|-----------|---------|-------------|
| Ingest validator stability | MR-1 | Existing PI-1 through PI-14 validator still passes |
| Valid fixture ingress | MR-2 | Valid regression fixtures pass all PI rules |
| Invalid fixture rejection | MR-3 | Invalid regression fixtures fail for expected invariant reasons |
| Fail-closed validation | MR-4 | Ingest CLI rejects invalid fixtures (no false positives) |
| Advisory invariant | MR-5 | All ingested records have `advisory: true` |
| Cross-project write invariant | MR-6 | All ingested records have `cross_project_write_authorized: false` |
| Owner-apply invariant | MR-7 | All ingested records have `owner_apply_required: true` |
| No mutation payload | MR-8 | No stored packet payload contains mutation-authorizing keys |
| Local/reconstructable state | MR-9 | Derived state is QA Pilot-local and reconstructable from scratch |
| Adversarial fail-closed | MR-10 | Invalid adversarial shapes fail closed at schema level |
| Boundary integrity | MR-11 | No Librarian file writes from regression operations |

## 2. Regression Invariants

### 2.1 Advisory Boundary

Every packet ingested through the QA Pilot ingest chain is marked `advisory: true` at the stored-record level. No packet can bypass this flag through payload manipulation. The ingest CLI always hardcodes `advisory: True` in the index entry regardless of packet content.

**Protected invariant:** Ingested packets are evidence/input only, never authoritative.

### 2.2 Cross-Project Write Prohibition

Every ingested record has `cross_project_write_authorized: false`. The ingest CLI always hardcodes this value. No packet can claim cross-project write authority through allowed_use or payload fields.

**Protected invariant:** QA Pilot never gains write authority over Librarian through packet ingestion.

### 2.3 Owner-Apply Requirement

Every ingested record has `owner_apply_required: true`. The ingest CLI always hardcodes this value. No packet can bypass the Owner apply gate.

**Protected invariant:** Owner decision is always required before any apply action triggered by ingested content.

### 2.4 Fail-Closed Validation

Invalid packet shapes (adversarial payloads, missing fields, unknown types, mutation paths) are unconditionally rejected at validation time. The ingest command refuses to store packets that fail validation.

**Protected invariant:** Invalid packets are never stored in the derived store.

### 2.5 Local/Reconstructable State

All derived state lives under `data/packets/ingested/` within the QA Pilot workspace. No data leaks to Librarian paths. State can be fully reconstructed by clearing and re-ingesting from source fixtures.

**Protected invariant:** Derived state is local and auditable. Loss of the derived store does not affect Librarian.

## 3. Scope

### In Scope
- Regression fixtures testing packet custody invariants (valid + invalid)
- Regression validator (Python) asserting all MR-1 through MR-11 invariants
- Regression test runner (shell) — one-command execution
- Boundary scan: prove no Librarian file writes
- Reconstruction test: clear → re-ingest → verify
- Stored record verification: advisory, cross-project-write, owner-apply fields

### Explicitly Out of Scope (Hard Boundaries)
- No new ingest semantics or schema changes
- No training behavior or simulation implementation
- No MCP bridge activation
- No packet application path
- No authority promotion from Librarian export to QA Pilot write authority
- No Owner decision bypass
- No Librarian file mutation
- No changes to the sealed QA-PILOT-QA-PACKET-INGEST-1 schema or CLI

## 4. Fixture Summary

### Valid Fixtures (pass ingest validation)

| Fixture | Type | Purpose |
|---------|------|---------|
| `regression-valid-claim-registry-packet.json` | qa_claim_registry | Valid upstream export for ingestion test |
| `regression-valid-project-state-packet.json` | project_state | Valid upstream export for ingestion test |
| `regression-valid-milestone-regression-packet.json` | milestone_regression | Valid packet for regression context |
| `regression-valid-training-source-packet.json` | training_source | Valid training_simulated packet |
| `regression-valid-derived-reconstruct.json` | project_state | Used for derived-state reconstruction test |

### Invalid Fixtures (rejected by ingest validation)

| Fixture | Invariant Violated | Expected Failure |
|---------|-------------------|------------------|
| `regression-invalid-mutation-authorized.json` | PI-11 | Payload contains `seal_action` |
| `regression-invalid-no-owner-apply.json` | PI-10 | `owner_decision_required_for_apply: false` |
| `regression-invalid-cross-project-write.json` | PI-8 | `allowed_use` contains `direct_librarian_mutation` |
| `regression-invalid-mutation-payload.json` | PI-11 | Payload contains Librarian mutation path |
| `regression-invalid-adversarial-shape.json` | PI-1 | Unknown `packet_type` |
| `regression-invalid-authority-promotion.json` | PI-12 | `training_simulated` with `qa_regression` in allowed_use |
| `regression-invalid-librarian-path.json` | PI-11 | Payload references Librarian runtime path |

## 5. Dependencies

| Sprint | Dependency Type | Status |
|--------|----------------|--------|
| QA-PILOT-QA-PACKET-INGEST-1 (#17) | Sealed ingest pipeline under test | ✅ Sealed |
| QA-PILOT-BROKER-AUDIT-STORE-HARDEN-1 (#15) | Broker audit store (regression context) | ✅ Sealed |
| PROJECT-STARTUP-CONTRACT-REGISTRY-1 (#14) | Registry selection (startup context) | ✅ Sealed |
| LIBRARIAN-QA-PACKET-EXPORT-1 | Upstream source (planned Librarian-side export) | 🔍 Planned |

## 6. Next Valid Consumers

After this regression suite is sealed, the following sprints are authorized:

- **QA-PILOT-LOCAL-TRAINING-SIM-1** — Build local training simulation using the proven ingest chain, guaranteed by this regression suite
- **QA-PILOT-CROSS-PROJECT-MCP-QA-BRIDGE-PLAN-1** (follow-up) — Bridge activation only after regression stability is confirmed

## 7. Reference

- **Regression validator:** `scripts/validate-qa-pilot-milestone-regression.py`
- **Test runner:** `scripts/test-qa-pilot-milestone-regression.sh`
- **Fixtures:** `docs/examples/qa-pilot-milestone-regression/`
- **Schema under test:** `docs/schemas/qa-pilot-qa-packet-ingest.schema.json`
- **Ingest CLI under test:** `scripts/qa_pilot_qa_packet_ingest.py`
- **Sprint authorization:** QA-PILOT-QA-PACKET-INGEST-1-SEAL
