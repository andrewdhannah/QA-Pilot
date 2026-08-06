# QA-PILOT-MCP-SURFACE.md — QA Pilot MCP Surface

**Status:** 🔍 Planning draft (sprint #32)
**Authority:** QA Pilot owns a dedicated MCP surface. The QA Pilot MCP is an advisory QA interface for evidence intake, validation, test composition, regression execution, simulator/help lookup, learning records, and QA result export. It does not expose tools that approve, seal, mutate Librarian canonical state, advance sprints, create Librarian receipts, or exercise cross-project authority.

---

## 1. Standalone Architecture

QA Pilot operates as a **standalone QA workbench and optional add-on/value layer for The Librarian ecosystem**.

The QA Pilot MCP surface is:
- QA Pilot-local — owned and operated by QA Pilot independently
- Usable by The Librarian workflow (advisory evidence intake)
- Usable by Owner directly (standalone QA operations)
- Capable of ingesting bounded packets from multiple governed projects
- Capable of building QA/regression evidence independently
- Capable of exporting advisory result packets
- **Not** capable of mutating source project authority

QA Pilot is not a submodule of The Librarian. It is a separate QA product/lane with its own MCP, DB, simulator/help surface, and regression lifecycle.

## 2. Tool Families

### Family 1: Evidence Intake (R0/R1)

| Tool | R-level | Description |
|------|---------|-------------|
| `qa_evidence_ingest` | R1 | Ingest a bounded evidence packet into QA Pilot-local store from any governed project |
| `qa_evidence_validate` | R0 | Validate an evidence packet against schema without storing |
| `qa_evidence_list` | R0 | List ingested evidence packets with filters (project, sprint, date) |
| `qa_evidence_read` | R0 | Read a specific evidence packet by ID |

**Behavior:** Accepts evidence from any governed project that respects the evidence packet contract. Rejects packets with missing required fields, invalid schema, unknown project, or missing provenance.

### Family 2: Test Composition (R0/R1)

| Tool | R-level | Description |
|------|---------|-------------|
| `qa_test_compose` | R1 | Compose test cases from evidence for a sprint |
| `qa_test_list` | R0 | List composed test cases with filters (sprint, status, tag) |
| `qa_test_read` | R0 | Read a specific test case by ID |
| `qa_test_run` | R1 | Run composed tests and record results (live or dry-run) |

**Behavior:** Tests are derived from changed files, acceptance criteria, prior defects, sealed invariants, regression history, simulator scenarios. Results are advisory only.

### Family 3: Epic Regression (R0/R1)

| Tool | R-level | Description |
|------|---------|-------------|
| `qa_epic_suite_build` | R1 | Build Epic-level regression suite from sprint tests |
| `qa_epic_suite_read` | R0 | Read an Epic regression suite definition and results |
| `qa_epic_suite_run` | R1 | Run an Epic regression suite (advisory output) |

**Behavior:** Builds cross-sprint regression suites. Results are advisory until Owner accepts. No approve/seal/advance authority.

### Family 4: Learning / Defect Memory (R1)

| Tool | R-level | Description |
|------|---------|-------------|
| `qa_learning_record` | R1 | Record a lesson learned from a defect, regression, or observation |
| `qa_defect_record` | R1 | Record a defect found during QA activity |
| `qa_regression_link` | R1 | Link a defect/learning record to specific regression tests |

**Behavior:** All records are advisory. Defect severity and status tracked within QA Pilot. No cross-project mutation.

### Family 5: Simulator / Help Surface (R0/R1)

| Tool | R-level | Description |
|------|---------|-------------|
| `qa_simulator_scenario_list` | R0 | List available simulator scenarios |
| `qa_simulator_scenario_read` | R0 | Read a specific simulator scenario |
| `qa_help_lookup` | R0 | Look up help/documentation references by feature or topic |

**Behavior:** Scenarios and references built from sprint evidence, governance docs, and manual input. Advisory-only. No help/doc mutation.

### Family 6: Reporting / Export (R0/R1)

| Tool | R-level | Description |
|------|---------|-------------|
| `qa_result_export` | R1 | Export advisory QA result packet for Owner review |
| `qa_status_summary` | R0 | Return aggregated QA status summary |

**Behavior:** All exports carry `advisory: true` and `owner_action_required: true`. No export may approve, seal, mutate, or advance work in any project.

## 3. Hard Negative Constraints

The following tools or effects are **forbidden** in the QA Pilot MCP surface:

| Forbidden Tool/Effect | Reason |
|----------------------|--------|
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

These constraints are enforced by the QA Pilot MCP tool contracts. Any tool output that claims these capabilities is rejected.

## 4. Standalone Invariants

1. QA Pilot MCP is owned and operated by QA Pilot independently
2. QA Pilot MCP can accept evidence from any governed project that respects the evidence contract
3. QA Pilot MCP can build QA/regression evidence independently of any source project
4. QA Pilot MCP can export advisory result packets without source project involvement
5. QA Pilot MCP cannot mutate source project authority, files, receipts, ledgers, status, or sprint state
6. QA Pilot MCP tools are advisory-only (`advisory: true`)
7. QA Pilot MCP enforces hard negative constraints at the tool definition level
8. QA Pilot MCP cross-project references require explicit Owner authorization

## 5. Common Response Envelope

All tools return this envelope:

```json
{
  "tool": "<tool_name>",
  "advisory": true,
  "no_canonical_authority": true,
  "project_boundary": "qa-pilot",
  "standalone_mcp": true,
  "multi_project_capable": true,
  "cross_project_registration": false,
  "result": { ... },
  "timestamp": "<ISO 8601>"
}
```
