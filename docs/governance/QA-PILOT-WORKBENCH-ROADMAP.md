# QA-PILOT-WORKBENCH-ROADMAP.md — QA Pilot Workbench Implementation Roadmap

**Status:** 🔍 Planning draft (sprint #32)
**Authority:** Advisory-only phased implementation plan. No sprint is authorized by this roadmap — each requires separate Owner authorization.

---

## Phase Overview

| Phase | Sprint | Focus | R-level Tools |
|-------|--------|-------|---------------|
| 1 | QA-PILOT-MCP-EVIDENCE-INTAKE-1 | MCP evidence intake | qa_evidence_ingest, validate, list, read |
| 2 | QA-PILOT-DB-EVIDENCE-STORE-1 | QA DB / evidence store | All entities storage layer |
| 3 | QA-PILOT-TEST-COMPOSITION-1 | Test composition | qa_test_compose, qa_test_run |
| 4 | QA-PILOT-SPRINT-RESULT-PACKETS-1 | Sprint result packets | qa_result_export (sprint-level) |
| 5 | QA-PILOT-EPIC-REGRESSION-BUILDER-1 | Epic regression builder | qa_epic_suite_build, qa_epic_suite_run |
| 6 | QA-PILOT-SIMULATOR-HELP-INTEGRATION-1 | Simulator/help integration | qa_simulator_map, qa_simulator_run, qa_help_lookup |
| 7 | QA-PILOT-DASHBOARD-REPORTING-1 | Dashboard/reporting | Status aggregation, summary views |
| 8 | QA-PILOT-LIBRARIAN-IMPORT-SURFACE-1 | Librarian import/read-only advisory surface | Advisory export to Librarian |

## Phase Details

### Phase 1: QA-PILOT-MCP-EVIDENCE-INTAKE-1

**Goal:** Implement the first four QA Pilot-local MCP tools for bounded Librarian QA evidence packet handling.

**Deliverables:**
- `scripts/qa_evidence_intake.py` — ingest/validate/list/read CLI
- Evidence packet validator (schema-based)
- Test runner for intake operations
- Governance doc update
- Status surface updates

**Boundary:** QA Pilot-local only. No Librarian mutation.

### Phase 2: QA-PILOT-DB-EVIDENCE-STORE-1

**Goal:** Implement the QA Pilot-local file-based evidence store covering all 11 entities.

**Deliverables:**
- Storage module with register/get/list/status for each entity type
- Schema validation on write
- Index management with bounded listing
- Corruption handling
- Test runner

**Boundary:** Follows the broker audit store pattern (#11, #15).

### Phase 3: QA-PILOT-TEST-COMPOSITION-1

**Goal:** Compose and run test cases from sprint evidence.

**Deliverables:**
- Test composition engine (derives tests from evidence)
- Test runner with live/dry-run modes
- Result recording to test_runs entity
- Test case lifecycle management

**Boundary:** Advisory-only test results. No approve/seal authority.

### Phase 4: QA-PILOT-SPRINT-RESULT-PACKETS-1

**Goal:** Export advisory sprint-level QA result packets.

**Deliverables:**
- Result packet assembly from sprint tests, defects, learning records
- Export CLI per qa-result-packet.schema.json
- Owner decision linking

**Boundary:** All exports carry `advisory: true` and `owner_action_required: true`.

### Phase 5: QA-PILOT-EPIC-REGRESSION-BUILDER-1

**Goal:** Build and run Epic-level regression suites from sprint-level tests.

**Deliverables:**
- Epic suite composition from sprint tests
- Suite execution with aggregated results
- Epic-level QA report export

**Boundary:** Results advisory until Owner accepts.

### Phase 6: QA-PILOT-SIMULATOR-HELP-INTEGRATION-1

**Goal:** Integrate simulator scenarios and help references.

**Deliverables:**
- Simulator scenario management (map/list/run)
- Help reference management (map/lookup)
- Integration with test composition

**Boundary:** QA Pilot-local only.

### Phase 7: QA-PILOT-DASHBOARD-REPORTING-1

**Goal:** Provide status aggregation and summary views.

**Deliverables:**
- QA status summary surface
- Defect/learning trend views
- Regression coverage metrics
- Export readiness indicators

**Boundary:** Read-only aggregation of QA Pilot-local data.

### Phase 8: QA-PILOT-LIBRARIAN-IMPORT-SURFACE-1

**Goal:** Create a read-only advisory surface for Librarian to consume QA Pilot results.

**Deliverables:**
- Advisory QA result export in Librarian-readable format
- Cross-reference with Librarian sprint data
- No Librarian file mutation

**Boundary:** Advisory export only. No mutation of Librarian state.

## Recommended First Implementation Sprint

```
QA-PILOT-MCP-EVIDENCE-INTAKE-1
```

Implement the first four QA Pilot-local MCP tools for bounded Librarian QA evidence packet handling: ingest, validate, list, and read. Store evidence only in QA Pilot-local state.

## Roadmap Invariants

1. Each phase is separately Owner-authorizable
2. No phase implies authorization for any other phase
3. All phases respect QA Pilot-local boundary
4. No phase creates approve/seal/execute/write authority
5. Phase 8 (Librarian surface) requires explicit cross-project authorization
6. Existing #23–#31 governance/custody regressions remain green throughout all phases
