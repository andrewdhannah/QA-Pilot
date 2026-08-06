# Sprint Receipt — QA-PILOT-WORKBENCH-ITEM-QUERY-LISTING-1

**Ledger #69**
**Lane:** governance
**Type:** substantive capability / workbench retrieval
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none
**Input dependencies:** QA-PILOT-WORKBENCH-ITEM-STATUS-LIFECYCLE-1 (#68, sealed)

## Deliverables

### CLI Commands (4 new)
- `query` — Rich query interface with 9+ filters, text or JSON output
- `count` — Count items matching filters, optional group-by (status/severity/category)
- `report` — Cross-item summary report with counts and advisory disclaimer
- `export-summary` — Export current workbench summary as JSON to stdout or file

### Enhanced List Filters
`list` and `query` support: `--status`, `--severity`, `--category`, `--source`, `--evidence-type`, `--has-evidence`, `--needs-review`, `--deferred`, `--resolved-locally`, `--created-after`, `--created-before`

### Validator Rules (WQ)
- **WQ-1**: Items must not have authority-claiming content in queryable fields
- **WQ-2**: Items with lifecycle must have consistent status for query reliability
- **WQ-3**: Items must not claim verification in lifecycle reasons

### Fixtures (10 new, 43 total)
- 5 valid: evidence item, needs-review item, deferred item, resolved item, mixed-severity item
- 5 invalid: approval-claiming, registry-carrying, lifecycle-mutating, verification-claiming, seal-semantics

### Authority Boundaries
- Query results do not imply validation or approval
- Summary counts do not imply Owner approval
- `resolved_locally` remains local/advisory only
- No query operation mutates items
- All output carries advisory-only disclaimer

## Validation
- Tests: **25/25 pass**
- Fixtures: **43/43 pass**
- PH/DR/PLR/SRS/WB: **ALL PASS**
