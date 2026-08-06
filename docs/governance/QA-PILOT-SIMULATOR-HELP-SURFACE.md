# QA-PILOT-SIMULATOR-HELP-SURFACE.md — QA Pilot Simulator and Help Surface

**Status:** 🔍 Planning draft (sprint #32)
**Authority:** Advisory-only. Simulator scenarios and help references are QA Pilot-local data products. No cross-project mutation.

---

## 1. Simulator Surface

QA Pilot maps Librarian functionality to simulator scenarios for training, validation, and onboarding.

### Scenario Structure

Each scenario captures:

| Field | Description |
|-------|-------------|
| `scenario_id` | Unique identifier |
| `feature` | The feature being simulated |
| `workflow` | Step-by-step workflow description |
| `expected` | Expected outcome of the workflow |
| `validation_points` | Specific checkpoints to validate during simulation |

### Scenario Sources

Scenarios are derived from:
- Sprint acceptance criteria
- Governance doc invariants
- Sealed contract boundary assertions
- Defect/regression history
- Manual test scripts
- Help/documentation references

### Simulator Tools

| Tool | R-level | Description |
|------|---------|-------------|
| `qa_simulator_map` | R1 | Map a feature/workflow to a simulator scenario |
| `qa_simulator_list` | R0 | List available simulator scenarios |
| `qa_simulator_run` | R1 | Run a simulator scenario (advisory output) |

### Validation Checkpoints

Each scenario may include validation checkpoints — assertions that must hold true for the simulation to be marked as passing. Checkpoints are advisory and do not confer approval or seal authority.

## 2. Help Surface

QA Pilot maps Librarian functionality to help references for onboarding, training, and documentation.

### Help Reference Structure

Each reference captures:

| Field | Description |
|-------|-------------|
| `ref_id` | Unique identifier |
| `feature` | The feature being documented |
| `topic` | Specific topic |
| `content_ref` | Reference to documentation content (file path or URL) |
| `workflow_ref` | Linked workflow/scenario (optional) |

### Help Tools

| Tool | R-level | Description |
|------|---------|-------------|
| `qa_help_lookup` | R0 | Look up help references by feature or topic |
| `qa_help_map` | R1 | Map a feature/topic to a help reference |

### Help Content Sources

Help references are derived from:
- Governance docs
- Project startup docs
- Sprint receipts
- Schema definitions
- Fixture documentation
- Test runner documentation

## 3. Integration with Test Composition

Simulator scenarios and help references feed into test composition during `qa_test_compose`:

- Each scenario's validation points become test cases
- Each help reference's content may define expected behavior
- Scenarios may be tagged as "regression-relevant" to include in Epic suites
- Help references may be tagged as "onboarding" or "reference"

## 4. Invariants

1. All simulator and help data is QA Pilot-local
2. No simulator scenario or help reference confers authority
3. Validation checkpoints are advisory only
4. Help references never mutate source documentation
5. Scenarios are derived from sealed, Owner-approved content only
6. No cross-project mutation of Librarian help/simulator systems
