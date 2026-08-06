# Sprint Receipt — QA-PILOT-MCP-EVIDENCE-INTAKE-1

## Status: ✅ **Sealed**

**Type:** Implementation / MCP evidence intake
**Lane:** implementation
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Authorization:** Owner-approved 2026-07-06 per explicit authorization.

## Scope Satisfied

Implemented QA Pilot's first standalone MCP evidence-intake surface for bounded evidence packets.

### Deliverables

| Delivery | Path | Status |
|----------|------|--------|
| MCP evidence intake implementation | `scripts/qa_pilot_mcp_evidence_intake.py` | ✅ 4 tools: ingest, validate, list, read |
| Evidence store (file-backed) | `data/evidence/` + `data/evidence/evidence-index.json` | ✅ |
| Validator (EM-1 through EM-12 rules) | `scripts/validate-qa-pilot-mcp-evidence-intake.py` | ✅ 12 EM rules pass |
| Test runner (25 tests) | `scripts/test-qa-pilot-mcp-evidence-intake.sh` | ✅ 25/25 pass |
| Fixtures (7 total: 2 valid, 5 invalid) | `docs/examples/qa-pilot-mcp-evidence-intake/` | ✅ Valid, duplicate, stale, cross-project, missing-fields, forbidden-mutation |
| Governance doc | Embedded in intake script docstring | ✅ |

### EM Rules Coverage

| Rule | Description | Status |
|------|-------------|--------|
| EM-1 | Schema conformance (qa-evidence-packet.schema.json) | ✅ |
| EM-2 | Advisory-only evidence (no approval/seal authority) | ✅ |
| EM-3 | No source-project mutation through evidence intake | ✅ |
| EM-4 | Duplicate packet_ids rejected | ✅ |
| EM-5 | Cross-project evidence requires `_source_project_metadata` | ✅ |
| EM-6 | Future timestamps rejected (stale detection) | ✅ |
| EM-7 | `boundary_assertions.librarian_impact` required | ✅ |
| EM-8 | Evidence hash must be present | ✅ |
| EM-9 | List/read are read-only (AST-verified) | ✅ |
| EM-10 | All responses include advisory-only posture | ✅ |
| EM-11 | Responses identify source_project and QA Pilot-local custody | ✅ |
| EM-12 | Evidence cannot authorize Librarian mutation | ✅ |

### Acceptance Gates

| Gate | Result |
|------|--------|
| All new MCP evidence-intake tests pass | ✅ 25/25 |
| Validator ALL CHECKS PASS | ✅ 12/12 EM rules |
| Existing #23–#32 regressions remain green | ✅ SR 15/15, AP 13/13, MR 11/11 |
| No Librarian files modified | ✅ git diff shows 0 Librarian files |
| No source-project authority mutation possible | ✅ EM-3, EM-12 enforce this |
| QA Pilot can ingest, validate, list, read evidence as standalone MCP | ✅ 4 tools all working |

## Evidence Intake MCP Tools

| Tool | Description | Authority |
|------|-------------|-----------|
| `qa_evidence_ingest` | Validate and store an evidence packet | R1 (advisory-only) |
| `qa_evidence_validate` | Validate an evidence packet without storing | R0 (read-only) |
| `qa_evidence_list` | List ingested evidence packets, optional project filter | R0 (read-only) |
| `qa_evidence_read` | Read a stored evidence packet by packet_id | R0 (read-only) |

## Hard Constraints Enforced

- All MCP responses include `advisory_only: true` and advisory notice
- All MCP responses identify source project (`qa-pilot`) and custody (`qa-pilot-local`)
- Evidence packets are validated against EM-1 through EM-12 before storage
- Stored records are QA Pilot-local only (`data/evidence/`)
- Malformed packets are rejected at validate or ingest time
- Cross-project packets require `_source_project_metadata` with `source_project_id`
- Duplicate `packet_id` values are rejected deterministically
- Result/export behavior explicitly out of scope

## Forbidden Paths (explicitly not implemented)

- No sprint approval/seal/start/advance authority
- No Librarian ledger mutation
- No Librarian file writes
- No Owner decision substitution
- No cross-project write authority
- No test composition, simulator integration, or result export

## Sealed by

Owner decision 2026-07-06.

## Next authorized sprint

Awaiting Owner direction. Candidates: QA-PILOT-MCP-EVIDENCE-COMPOSITION-1 (test composition tools), QA-PILOT-MCP-SIMULATOR-INTEGRATION-1 (simulator/help surface), or QA-PILOT-MCP-RESULT-EXPORT-1 (result/export surface).
