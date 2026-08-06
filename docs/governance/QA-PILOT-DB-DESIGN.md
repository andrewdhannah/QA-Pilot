# QA-PILOT-DB-DESIGN.md — QA Pilot Database Design

**Status:** 🔍 Planning draft (sprint #32)
**Authority:** Advisory-only. Defines QA Pilot-local file-based storage entities. No cross-project mutation.

---

## Storage Model

QA Pilot uses a file-based JSON store (following the pattern established by the broker audit store). Each entity type has its own directory under `data/qa/` with an index file and individual entity files.

## Entities

### 1. evidence_packets

**Directory:** `data/qa/evidence/packets/`
**Index:** `data/qa/evidence/packet-index.json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| packet_id | string | yes | Unique ID, format `EP-<timestamp>-<seq>` |
| project | string | yes | Source project |
| sprint_id | string | yes | Source sprint |
| source_ledger | string | yes | Ledger reference |
| changed_files | array | yes | Files changed |
| validation_output | object | yes | Test results |
| receipt_references | array | yes | Receipt IDs |
| boundary_assertions | object | yes | Boundary assertions |
| known_defects | array | no | Defects |
| evidence_artifacts | array | no | Artifacts |
| provenance | object | yes | Source + timestamp |
| hash | string | yes | Content fingerprint |
| ingested_at | string | yes | When ingested |

### 2. evidence_artifacts

**Directory:** `data/qa/evidence/artifacts/`
**Index:** `data/qa/evidence/artifact-index.json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| artifact_id | string | yes | Unique ID |
| packet_id | string | yes | Parent packet |
| path | string | yes | File path |
| type | string | yes | Artifact type |
| hash | string | yes | Content hash |
| content_ref | string | no | Reference to stored content |

### 3. sprint_test_cases

**Directory:** `data/qa/tests/cases/`
**Index:** `data/qa/tests/test-index.json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| test_id | string | yes | Unique ID, format `TC-<sprint>-<seq>` |
| sprint_id | string | yes | Source sprint |
| source_artifact | string | yes | Evidence artifact ref |
| criteria | string | yes | Acceptance criteria |
| expected | string | no | Expected outcome |
| preconditions | array | no | Preconditions |
| steps | array | no | Test steps |
| postconditions | array | no | Postconditions |
| status | string | yes | composed/ready/run/passed/failed/blocked |
| tags | array | no | Tags |

### 4. test_runs

**Directory:** `data/qa/tests/runs/`
**Index:** `data/qa/tests/run-index.json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| run_id | string | yes | Unique ID, format `TR-<timestamp>-<seq>` |
| test_id | string | yes | Test reference |
| sprint_id | string | yes | Sprint reference |
| result | string | yes | passed/failed/error/skipped |
| output | string | no | Run output |
| run_at | string | yes | Timestamp |

### 5. defects

**Directory:** `data/qa/defects/`
**Index:** `data/qa/defect-index.json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| defect_id | string | yes | Unique ID, format `DF-<sprint>-<seq>` |
| sprint_id | string | yes | Source sprint |
| severity | string | yes | low/medium/high/critical |
| description | string | yes | Defect description |
| evidence_ref | string | no | Reference to evidence |
| status | string | yes | open/confirmed/fixed/closed |

### 6. learning_records

**Directory:** `data/qa/learning/`
**Index:** `data/qa/learning-index.json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| record_id | string | yes | Unique ID, format `LR-<timestamp>-<seq>` |
| sprint_id | string | yes | Source sprint |
| defect_ref | string | no | Linked defect |
| source_type | string | yes | defect/regression/observation/violation/improvement |
| lesson | string | yes | Lesson text |
| recommendation | string | no | Recommendation |
| tags | array | no | Tags |
| recorded_at | string | yes | Timestamp |

### 7. epic_regression_suites

**Directory:** `data/qa/epic/suites/`
**Index:** `data/qa/epic/suite-index.json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| suite_id | string | yes | Unique ID, format `ERS-<epic>-<seq>` |
| epic_id | string | yes | Epic identifier |
| sprint_ids | array | yes | Sprint IDs |
| tests | array | yes | Test references |
| last_run_at | string | no | Last run timestamp |
| result | object | no | Run results |
| status | string | yes | building/ready/running/completed/failed |

### 8. simulator_scenarios

**Directory:** `data/qa/simulator/scenarios/`
**Index:** `data/qa/simulator/scenario-index.json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| scenario_id | string | yes | Unique ID |
| feature | string | yes | Feature name |
| workflow | string | yes | Workflow description |
| expected | string | yes | Expected outcome |
| validation_points | array | yes | Validation checkpoints |

### 9. help_references

**Directory:** `data/qa/help/`
**Index:** `data/qa/help-index.json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| ref_id | string | yes | Unique ID |
| feature | string | yes | Feature name |
| topic | string | yes | Topic |
| content_ref | string | yes | Reference to documentation |
| workflow_ref | string | no | Linked workflow |

### 10. qa_result_packets

**Directory:** `data/qa/results/`
**Index:** `data/qa/result-index.json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| result_id | string | yes | Unique ID, format `QR-<timestamp>-<seq>` |
| sprint_ids | array | yes | Sprint IDs |
| epic_ref | string | no | Epic reference |
| summary | object | yes | Result summary |
| findings | array | yes | Detailed findings |
| defects | array | no | Defect references |
| learning_records | array | no | Learning references |
| recommendation | string | no | Recommendation |
| exported_at | string | yes | Export timestamp |

### 11. owner_decision_links

**Directory:** `data/qa/decisions/`
**Index:** `data/qa/decision-index.json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| link_id | string | yes | Unique ID |
| result_id | string | yes | QA result reference |
| decision_id | string | yes | Owner decision reference |
| decided_at | string | yes | Decision timestamp |

## Storage Conventions

- All entities stored as individual JSON files
- Index files contain sorted list of entity IDs with creation timestamps
- Bounded listing (max 200 per query, default 50)
- Schema validation on write (reject if missing required fields)
- Immutable identity fields after creation
- Deterministic sorting by creation timestamp

## Invariants

1. All data is QA Pilot-local — no Librarian paths touched
2. No entity contains approve/seal/execute/write controls
3. All result entities carry `advisory: true`
4. All defect/learning data is advisory until Owner accepts
5. Cross-project references require explicit Owner authorization
6. Storage follows the pattern established by the broker audit store (#11, #15)
