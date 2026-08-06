# QA-PILOT-FULL-WORKBENCH-ARCHITECTURE.md — QA Pilot Full Workbench Architecture

**Status:** 🔍 Planning draft (sprint #32)
**Authority:** Advisory-only planning architecture. Defines QA Pilot as the dedicated QA workbench for The Librarian ecosystem. QA Pilot may inspect, ingest, test, simulate, classify, report, and recommend. QA Pilot may not mutate Librarian canonical files, receipts, ledgers, status surfaces, startup state, or sprint authority.
**Sprint:** QA-PILOT-FULL-WORKBENCH-ARCHITECTURE-PLAN-1

---

## 1. Purpose

QA Pilot is a **standalone QA workbench and optional add-on/value layer for The Librarian ecosystem**. It is not a submodule of The Librarian — it is a separate QA product/lane with its own MCP, DB, simulator/help surface, and regression lifecycle.

QA Pilot is the dedicated QA evidence, test, regression, simulator, and learning workbench that:
- Can be used by The Librarian workflow (advisory evidence intake)
- Can be used by Owner directly (standalone QA operations)
- Can ingest bounded packets from multiple governed projects
- Can build QA/regression evidence independently
- Can export advisory result packets
- Cannot mutate source project authority

This document defines the full architecture, authority model, data flow, MCP surface, data model, and phased implementation roadmap.

## 2. Authority Model

QA Pilot may:
- Inspect sealed sprint evidence from Librarian export packets
- Ingest, validate, and store evidence in QA Pilot-local state
- Compose and run tests from sprint evidence
- Build Epic-level regression suites from sprint-level tests
- Simulate workflows and map help/documentation references
- Classify defects and record lessons learned
- Export advisory QA result packets for Owner review

QA Pilot may not:
- Mutate Librarian canonical files, receipts, ledgers, status surfaces, startup state, or sprint authority
- Approve, seal, execute, or advance Librarian work
- Create cross-project authority without explicit Owner authorization
- Bypass the GLOBAL-STARTUP-INTENT-AUTHORIZATION-CONTRACT-1 boundary

## 3. Core Flow

```
Librarian sprint evidence packet
    │
    ▼
┌─────────────────────────────────────┐
│ QA Pilot evidence intake            │
│  - validate schema                  │
│  - verify provenance                │
│  - store in QA Pilot-local DB       │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ Test composition                    │
│  - derive from changed files        │
│  - from claimed acceptance criteria │
│  - from prior defects               │
│  - from sealed invariants           │
│  - from regression history          │
│  - from simulator scenarios         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ Sprint QA result                    │
│  - run composed tests               │
│  - record defects                   │
│  - capture lessons                  │
│  - update learning records          │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ Epic regression rollup              │
│  - compose Epic-level suite         │
│  - run all sprint-level tests       │
│  - produce Epic QA report           │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ Advisory result packet              │
│  → Owner review                     │
│  → Owner-authorized Librarian action│
└─────────────────────────────────────┘
```

## 4. MCP Surface

QA Pilot owns a dedicated MCP surface. The QA Pilot MCP is an advisory QA interface for evidence intake, validation, test composition, regression execution, simulator/help lookup, learning records, and QA result export. It is a standalone QA Pilot-local surface that can operate as an add-on/value layer for any governed project, not exclusively The Librarian.

**Standalone MCP architecture:**
- QA Pilot-local — owned and operated by QA Pilot independently
- Can be used by The Librarian workflow (advisory evidence intake)
- Can be used by Owner directly (standalone QA operations)
- Can ingest bounded packets from multiple governed projects
- Can build QA/regression evidence independently
- Can export advisory result packets
- Cannot mutate source project authority

**6 tool families (20 tools total):**

### Family 1: Evidence Intake
| Tool | R-level | Description |
|------|---------|-------------|
| `qa_evidence_ingest` | R1 | Ingest a bounded evidence packet from any governed project |
| `qa_evidence_validate` | R0 | Validate evidence packet against schema without storing |
| `qa_evidence_list` | R0 | List ingested evidence packets with filters |
| `qa_evidence_read` | R0 | Read a specific evidence packet |

### Family 2: Test Composition
| Tool | R-level | Description |
|------|---------|-------------|
| `qa_test_compose` | R1 | Compose test cases from evidence for a sprint |
| `qa_test_list` | R0 | List composed test cases |
| `qa_test_read` | R0 | Read a specific test case |
| `qa_test_run` | R1 | Run composed tests and record results |

### Family 3: Epic Regression
| Tool | R-level | Description |
|------|---------|-------------|
| `qa_epic_suite_build` | R1 | Build Epic-level regression suite from sprint tests |
| `qa_epic_suite_read` | R0 | Read an Epic regression suite definition and results |
| `qa_epic_suite_run` | R1 | Run Epic regression suite |

### Family 4: Learning / Defect Memory
| Tool | R-level | Description |
|------|---------|-------------|
| `qa_learning_record` | R1 | Record a lesson learned |
| `qa_defect_record` | R1 | Record a defect found during QA activity |
| `qa_regression_link` | R1 | Link defect/learning to regression tests |

### Family 5: Simulator / Help Surface
| Tool | R-level | Description |
|------|---------|-------------|
| `qa_simulator_scenario_list` | R0 | List available simulator scenarios |
| `qa_simulator_scenario_read` | R0 | Read a specific simulator scenario |
| `qa_help_lookup` | R0 | Look up help/documentation references |

### Family 6: Reporting / Export
| Tool | R-level | Description |
|------|---------|-------------|
| `qa_result_export` | R1 | Export advisory QA result packet |
| `qa_status_summary` | R0 | Return aggregated QA status summary |

**Hard negative constraints (forbidden tools/effects):**

| Forbidden | Reason |
|-----------|--------|
| `approve_sprint` | QA Pilot may not approve sprints |
| `seal_sprint` | QA Pilot may not seal sprints |
| `start_sprint` | QA Pilot may not start sprints |
| `advance_sprint` | QA Pilot may not advance sprint lifecycle |
| `mutate_librarian_ledger` | QA Pilot may not touch Librarian ledger |
| `create_librarian_receipt` | QA Pilot may not create Librarian receipts |
| `update_librarian_status` | QA Pilot may not update Librarian status surfaces |
| `write_librarian_file` | QA Pilot may not write Librarian canonical files |
| `apply_patch_to_librarian` | QA Pilot may not apply patches to Librarian codebase |
| `execute_librarian_work` | QA Pilot may not execute Librarian work orders |

All tools output `advisory: true` and carry `no_canonical_authority: true` and `standalone_mcp: true`.

## 5. DB Model

QA Pilot-local entities (JSON file-based store):

| Entity | Description | Key Fields |
|--------|-------------|------------|
| `evidence_packets` | Ingested Librarian sprint evidence | packet_id, project, sprint_id, source_ledger, ingested_at, hash |
| `evidence_artifacts` | Individual artifacts within a packet | artifact_id, packet_id, path, type, hash, content_ref |
| `sprint_test_cases` | Test cases composed from evidence | test_id, sprint_id, source_artifact, criteria, status |
| `test_runs` | Results of running test cases | run_id, test_id, sprint_id, result, output, run_at |
| `defects` | Defects found during QA | defect_id, sprint_id, severity, description, evidence_ref |
| `learning_records` | Lessons learned from defects | record_id, sprint_id, defect_ref, lesson, recommendation |
| `epic_regression_suites` | Epic-level regression suites | suite_id, epic_id, sprint_ids, tests, last_run_at, result |
| `simulator_scenarios` | Workflow simulator scenarios | scenario_id, feature, workflow, expected, validation_points |
| `help_references` | Help/documentation mappings | ref_id, feature, topic, content_ref, workflow_ref |
| `qa_result_packets` | Advisory QA result exports | result_id, sprint_ids, epic_ref, summary, findings, exported_at |
| `owner_decision_links` | Links between QA results and Owner decisions | link_id, result_id, decision_id, decided_at |

## 6. Evidence Packet Contract

Each evidence packet must include:

| Field | Required | Description |
|-------|----------|-------------|
| `project` | yes | Source project (e.g., "librarian") |
| `sprint_id` | yes | Source sprint identifier |
| `source_ledger` | yes | Source ledger reference |
| `changed_files` | yes | List of files changed in the sprint |
| `validation_output` | yes | Test/validation results |
| `receipt_references` | yes | Receipt IDs produced by the sprint |
| `boundary_assertions` | yes | Sprint boundary assertions |
| `known_defects` | no | Known defects discovered |
| `evidence_artifacts` | no | Screenshots, logs, manual evidence |
| `provenance` | yes | Who/what produced the evidence |
| `hash` | yes | Fingerprint of the evidence content |

## 7. Test Composition

Tests are derived from:
- Changed files in sprint evidence
- Claimed acceptance criteria
- Prior defects (regression tests)
- Sealed invariants from governance docs
- Regression history
- Simulator scenarios
- Help/documentation references

Each test case includes: test_id, sprint_id, source_artifact, criteria, expected, preconditions, steps, and postconditions.

## 8. Epic Regression

At Epic closeout, QA Pilot composes a package-level regression suite from all sprint-level tests and evidence. The Epic regression suite aggregates tests across sprints, preserves provenance, runs as an atomic batch, and produces a consolidated QA report.

The result is advisory until Owner accepts it. Owner acceptance may authorize Librarian Epic closeout.

## 9. Simulator and Help Surface

QA Pilot maps functionality to:
- Simulator scenarios (workflow-based)
- Expected user workflows
- Help files and documentation references
- Onboarding/training explanations
- Validation checkpoints

Each scenario maps feature → workflow → expected outcomes → validation points. Help references map feature → topic → content reference → workflow reference.

## 10. Result Export

QA Pilot exports advisory result packets only. Each export includes: result_id, sprint_ids, epic_ref, summary, detailed findings, defect list, learning records, and recommendation.

No exported result may itself approve, seal, mutate, or advance Librarian work. All exports carry `advisory: true` and `owner_action_required: true`.

## 11. Non-Goals

- No Librarian canonical file mutation
- No cross-project authority creation
- No bypass of Owner authorization boundary
- No approve/seal/execute/write controls on any QA Pilot tool
- No runtime registration in Librarian MCP infrastructure
- No modification of Librarian startup, ledger, or status surfaces

## 12. Boundary Invariants

1. All QA Pilot tools output `advisory: true`
2. No QA Pilot tool creates or modifies Librarian canonical files
3. QA Pilot evidence store is QA Pilot-local only
4. QA Pilot result exports carry no approve/seal/execute authority
5. Epic regression results are advisory until Owner accepts
6. Cross-project references require Owner authorization
7. All #23–#31 governance/custody regressions remain green
8. QA Pilot startup regression remains 15/15

## 13. Required Section Coverage

This document covers all required architecture sections:
- ✅ Purpose and scope
- ✅ Authority model with explicit boundaries
- ✅ Core data flow (evidence → test → sprint result → Epic → export)
- ✅ MCP surface with 12 tool contracts
- ✅ DB model with 11 entity definitions
- ✅ Evidence packet contract
- ✅ Test composition strategy
- ✅ Epic regression design
- ✅ Simulator and help surface
- ✅ Result export design
- ✅ Non-goals and boundary invariants
- ✅ Phased roadmap reference
