# QA Pilot Workbench Capability Foundation

**Type:** Governance / workbench capability layer
**Lane:** qa-pilot/gov-capability
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none
**Input dependencies:** QA-PILOT-PH5-EVIDENCE-STORE-PATH-FIX-1 (#65, sealed)

---

## 1. Purpose

Define the first bounded QA Pilot workbench capability layer on top of the clean governance foundation (#1–#65). This layer creates the core QA workbench object model, command surface, fixtures, and validator for creating, listing, reading, and validating QA work items without changing existing registry, seal, or Owner authority rules.

## 2. Object Model

Every QA workbench item is an advisory-only tracking artifact with these fields:

| Field | Required | Description |
|-------|----------|-------------|
| `qa_item_id` | Yes | Unique identifier (`QA-{CATEGORY}-{NNNN}`) |
| `title` | Yes | Short descriptive title (3-200 chars) |
| `source` | Yes | Origin pipeline stage (`evidence_intake`, `test_composition`, `result_export`, `epic_regression`, `train_sim`, `manual`, `advisory_review`) |
| `status` | Yes | Lifecycle state (`open`, `triaged`, `in_review`, `resolved`, `closed`) |
| `severity` | Yes | Impact severity (`critical`, `high`, `medium`, `low`, `info`) |
| `category` | Yes | Functional category |
| `description` | No | Detailed finding description (≤5000 chars) |
| `evidence_refs` | No | List of evidence artifact references (`EP-*`, `EPIC-*`, `QR-*`, `TC-*`, `ARP-*`) |
| `validator_refs` | No | List of validator rule references |
| `owner_decision_state` | No | Owner decision state (`pending`, `in_review`, `accepted`, `rejected`, `deferred`) |
| `owner_decision_ref` | No | Reference to an Owner decision receipt (`OD-*`) |
| `created_at` | Yes | ISO 8601 creation timestamp |
| `updated_at` | Yes | ISO 8601 last-updated timestamp |
| `advisory_only` | Yes | **Must always be `true`** |
| `custody` | Yes | **Must always be `qa-pilot-local`** |
| `librarian_impact` | Yes | **Must always be `none`** |

## 3. Operations

Six bounded CLI operations are defined:

| Operation | Description | Authority Boundary |
|-----------|-------------|-------------------|
| `create` | Create a new QA item from JSON | Does not imply defect acceptance |
| `list` | List items with optional `--status`, `--severity`, `--source` filters | Read-only |
| `read` | Read single item by ID | Read-only |
| `validate` | Validate item(s) against schema + business rules | Read-only |
| `triage` | Mark item as triaged | Does not imply Owner approval |
| `attach` | Attach evidence reference to item | Advisory tracking only |

## 4. Authority Boundaries

- WB-1: `advisory_only` must always be `true`
- WB-2: `custody` must always be `qa-pilot-local`
- WB-3: `librarian_impact` must always be `none`
- WB-4: Triaged items must not claim `accepted` owner_decision_state
- WB-5: Items must not claim seal/approval/authorization/verification authority
- WB-6: Evidence refs must be properly structured
- WB-7: Accepted `owner_decision_state` requires `owner_decision_ref`
- WB-8: Items must not carry registry/RCR/SRS state fields
- WB-9: No auto-seal — QA items do not confer seal authority
- WB-10: No ledger mutation — QA item operations do not write to the sprint ledger
- WB-11: No Librarian mutation — QA item operations never touch Librarian files

## 5. Fixture Suite

| Fixture | Type | Validates |
|---------|------|-----------|
| `valid-qa-item-functional.json` | Valid | Complete functional finding with evidence/validator refs |
| `valid-qa-item-validator-evidence.json` | Valid | Item with validator rule references |
| `valid-qa-item-advisory-review.json` | Valid | Item with advisory review packet references |
| `valid-qa-item-epic-regression.json` | Valid | Closed item with accepted Owner decision |
| `invalid-missing-evidence-refs.json` | Invalid | Evidence refs with invalid pattern |
| `invalid-unsupported-severity.json` | Invalid | Severity value outside allowed enum |
| `invalid-owner-decision-simulation.json` | Invalid | Accepted state without decision ref |
| `invalid-claiming-approval.json` | Invalid | Authority-claiming language in title/description |
| `invalid-mutation-registry-state.json` | Invalid | Item carrying registry/RCR/SRS fields |

## 6. Validator Rules

The validator (`scripts/validate-qa-pilot-workbench.py`) supports 4 modes:

- **fixture** — Validate all JSON fixture files against schema + business rules
- **validate** — Validate individual JSON files
- **live** — Validate all stored items in the workbench store
- **chain** — Run the full QA Pilot validator chain (summons all 15+ pipeline validators)

The validator enforces 8 business rules (WB-1 through WB-8) plus full JSON Schema compliance.

## 7. Post-Seal Maintenance

Because #66 builds on #65, standard governed maintenance was performed:
- Registry updated to 34 layers (slot #66 added)
- RCR receipt created: `data/registry-change-receipts/RCR-ADD-LAYER-066.json`
- SRS baseline refreshed to #66 via SUG
- SUG receipt: `data/snapshot-update-gate-receipts/SUG-REFRESH-066.json`

## 8. Chain Dependencies

This layer consumes:
- PH (Pipeline Health) — layer ordering preserved
- DR (Drift Detection) — drift detection unchanged
- PLR (Pipeline Layer Registry) — registry slot #66 added
- SRS (Startup Surface Regression Snapshot) — refreshed to #66
- AR (Advisory Review) — AR boundaries preserved
- SUG (Snapshot Update Gate) — governed refresh exercised
- RCR (Registry Change Receipt) — receipt created for #66
- RCG (RCR Closeout Gate) — gap=0 maintained
- MG (MCP Call Loop Guard) — unchanged

## 9. Non-Goals (Explicit)

- Not implementing Librarian Global Advisory Review Mode
- Not implementing MCP tools (CLI only)
- Not building a full UI
- Not automating Owner decisions
- Not replacing existing validator/governance chain
- Not creating broad QA execution workflows
- Not mutating Librarian
- Not creating seal authority
- Not modifying sprint ledger except via normal sprint receipt

## 10. Cross-Reference

- Schema: `docs/schemas/qa-workbench-item.schema.json`
- CLI tool: `scripts/qa_pilot_workbench.py`
- Validator: `scripts/validate-qa-pilot-workbench.py`
- Test runner: `scripts/test-qa-pilot-workbench.sh`
- Fixtures: `docs/examples/qa-pilot-workbench/`
- Sprint receipt: `docs/sprints/QA-PILOT-WORKBENCH-CAPABILITY-FOUNDATION-1.md`
