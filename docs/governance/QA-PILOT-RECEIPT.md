# QA Pilot Production Receipt — Governance

**Sprint:** QA-PILOT-PRODUCTION-LANE-A-1 (alias QA-PILOT-RECEIPT-SCHEMA-1)
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** Advisory only. No runtime custody enforcement. No production QA Pilot repo mutation. No mainline authority changes.

---

## 1. Purpose

Define the canonical QA Pilot production receipt schema and validation path. This establishes the first production Lane A artifact under the QA Pilot project ledger, defining the receipt format, evidence-kind mappings, authority envelope, and cross-project Librarian receipt store bridge that production QA Pilot work will use.

## 2. Scope

### In scope
- JSON Schema for QA Pilot production receipts (Draft 2020-12)
- Governance document for production receipts
- Valid and invalid production receipt fixtures
- Python validator with business rules (PR-1 through PR-12)
- Bash test runner with QA Pilot regression guards
- QA Pilot sprint closeout receipt

### Out of scope
- Runtime custody enforcement mutation
- QA Pilot production repo mutation (`qa-pilot-v2`, `QA-PilotV2`)
- Mainline Owner decision authority alteration
- Automatic promotion of QA findings into approval, seal, merge, or production-readiness authority
- MCP tool registration for QA Pilot receipts
- Swift service implementation
- The Librarian repo mutation

## 3. Packet Shape

### QA Pilot Production Receipt (`QAProductionReceipt`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `receipt_id` | string (pattern `qapr-\d{8}-\d{3,}`) | ✅ | Canonical QA Pilot receipt identifier |
| `packet_type` | enum[4] | ✅ | Type of production receipt |
| `schema_version` | const `qap-production-v1` | ✅ | Production schema version |
| `project_id` | string | ✅ | Project scope |
| `sprint_id` | string | ✅ | Sprint that generated this receipt |
| `source_sprint_receipt` | string | ✅ | Path to authorizing sprint receipt |
| `predecessor_dry_run_refs` | string[] | | References to preceding dry-run sprints |
| `created_at` | ISO 8601 | ✅ | Timestamp |
| `created_by` | string | ✅ | Creator identity |
| `model_or_agent` | string | | Model identifier |
| `authority` | const `advisory` | ✅ | Always advisory |
| `status` | enum[5] | ✅ | Lifecycle status |
| `non_approval_statement` | string (≥20 chars) | ✅ | Explicit non-approval language |
| `content_hash` | string (SHA-256) | ✅ | Real content hash |
| `librarian_receipt_refs` | object[] | ✅ | Links to Librarian receipt store |
| `qa_packet_refs` | object[] | ✅ | Links to QA Pilot packets |
| `production_evidence` | object[] | | Evidence collected during run |
| `results` | object | | Check results and summary |
| `recommendation` | object | | Advisory recommendation |
| `limitations` | string[] (≥1) | ✅ | Authority boundary acknowledgment |
| `escalation_triggers` | object[] | | Owner escalation conditions |

### Packet Types

| Enum Value | Description |
|------------|-------------|
| `QAProductionReceipt` | General production receipt |
| `QAProductionEvidenceReceipt` | Evidence collection receipt |
| `QAProductionVerificationReceipt` | Manual verification receipt |
| `QAProductionReadinessReceipt` | Readiness assessment receipt |

### Authority Model

All QA Pilot production receipts are **advisory-only**. The `authority` field is const `advisory`. Every receipt must include an explicit `non_approval_statement` (≥20 characters). No receipt may claim approval, sealing, merge authority, production readiness, or runtime custody enforcement.

### Librarian Receipt Store Bridge

`librarian_receipt_refs` connects QA Pilot receipts to the Librarian's node-registry receipt store (`nrr-*` pattern). This enables cross-system traceability: a QA Pilot production receipt can reference the chain validation, owner action, or apply receipts that were generated alongside it.

### Evidence Kinds (Production)

The dry-run evidence kinds (document_review, fixture_validation, validator_output, command_output, screenshot_reference, human_observation, repository_status, receipt_reference) are extended with two production-specific kinds:

| Evidence Kind | Description |
|---------------|-------------|
| `schema_validation` | JSON Schema validation of a packet or receipt |
| `hash_verification` | SHA-256 hash verification of content integrity |

### Content Hash

Production receipts use real SHA-256 content hashes (`sha256:[A-Fa-f0-9]{64}`), not the dry-run `"not-final"` placeholder. The content hash is the receipt's self-hash for integrity verification.

## 4. Business Rules (PR-1 through PR-12)

| Rule | Description | Enforcement |
|------|-------------|-------------|
| PR-1 | Receipt uses valid schema | Schema validation |
| PR-2 | authority is const `advisory` | Schema const |
| PR-3 | non_approval_statement is present and ≥20 characters | Field check |
| PR-4 | content_hash matches `sha256:` pattern | Pattern check |
| PR-5 | receipt_id follows `qapr-` pattern | Pattern check |
| PR-6 | packet_type is from allowed enum | Enum check |
| PR-7 | librarian_receipt_refs has valid receipt_type enum | Enum check |
| PR-8 | qa_packet_refs has valid packet_type enum | Enum check |
| PR-9 | limitations is non-empty | Field check |
| PR-10 | Blocked/partial status requires escalation_triggers | Conditional |
| PR-11 | Fail/blocked outcome cannot recommend `proceed` | Conditional |
| PR-12 | evidence_kind is from allowed production set | Enum check |

## 5. Relationship to Existing Components

| Component | Relationship |
|-----------|-------------|
| `docs/schemas/qa-pilot-receipt.schema.json` | New — Draft 2020-12 production receipt schema (QA Pilot-owned) |
| `docs/examples/qa-pilot-receipt/` | New — production receipt fixtures (QA Pilot-owned) |
| `scripts/validate-qa-pilot-receipt.py` | New — PR-1 through PR-12 validator (QA Pilot-owned) |
| `scripts/test-qa-pilot-receipt.sh` | New — test runner with QA Pilot regression guards |
| `active/librarian/docs/schemas/` | Cross-reference — original planning-only evidence source |
| `active/librarian/scripts/` | Cross-reference — original planning-only validator/test source |

## 6. Non-Goals

- No runtime custody enforcement mutation
- No QA Pilot production repo mutation (`qa-pilot-v2`, `QA-PilotV2`)
- No mainline authority changes
- No MCP tool registration
- No Swift service implementation
- No automatic promotion of QA findings
- No cross-packet validation between production receipt types
- No The Librarian repo mutation

## 7. Required Boundaries

1. Do not mutate `active/librarian/` (The Librarian repo)
2. Do not mutate `qa-pilot-v2/` or `QA-PilotV2/` (production QA Pilot repos)
3. Do not alter mainline Owner decision records
4. Do not claim QA approval, sealing, merge authority, or production readiness
5. All receipts are advisory-only with explicit non-approval language
6. Production receipts may reference, but do not supersede, the Librarian receipt store
