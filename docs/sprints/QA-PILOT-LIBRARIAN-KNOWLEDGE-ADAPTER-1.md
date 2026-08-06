# QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER-1 — Sprint Receipt

**Sprint ID:** QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER-1
**Epic:** EPIC-QA-PILOT-TRAINING-SYSTEM-1 (Sprint 3/11)
**Type:** Implementation / knowledge adapter
**Lane:** training_system_epic
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Status:** complete_pending_owner_review
**Authorization:** Owner explicit authorization 2026-07-08

## Scope Satisfied

- Created schema for knowledge adapter output (scan/query/reference/provenance/verify/status operations)
- Created CLI `scripts/qa_pilot_knowledge_adapter.py` with 6 commands
- Created validator `scripts/validate-qa-pilot-knowledge-adapter.py` (14 rules KA-1 through KA-14)
- Created 7 fixtures (4 valid + 3 invalid) in `docs/examples/qa-pilot-knowledge-adapter/`
- Created test runner `scripts/test-qa-pilot-knowledge-adapter.sh` (17 tests)
- Created governance doc `docs/governance/QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER.md`
- Created sprint receipt `docs/sprints/QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER-1.md`

## Coverage

| Rule | Description | Tested |
|------|-------------|--------|
| KA-1 | Adapter version must be 'knowledge-adapter-v1' | ✅ |
| KA-2 | Operation must be valid (6 known types) | ✅ |
| KA-3 | generated_at must be ISO 8601 UTC | ✅ |
| KA-4 | Source refs have path, revision, type, accessible | ✅ |
| KA-5 | Provenance requires provenance_id, sources, source_hash | ✅ |
| KA-6 | source_hash is SHA-256 hex | ✅ |
| KA-7 | Provenance advisory is true | ✅ |
| KA-8 | no_authority_promotion is true | ✅ |
| KA-9 | Verify status matches access + hash | ✅ |
| KA-10 | No Librarian mutation claims in output | ✅ |
| KA-11 | Scan groups sources by type correctly | ✅ |
| KA-12 | Query respects type/keyword filters | ✅ |
| KA-13 | Reference returns accessible per path | ✅ |
| KA-14 | Status reports advisory-only authority | ✅ |

## Hard Boundaries Enforced

- Read-only — all operations are queries against existing files
- No write path to Librarian
- No cross-project write capability
- Advisory-only authority posture
- All provenance records: `advisory: true`, `no_authority_promotion: true`
- No training generation performed (belongs to Sprint 5)

## Progress

```
EPIC-QA-PILOT-TRAINING-SYSTEM-1

[✓] Sprint 1/11 — QA-PILOT-TRAINING-SYSTEM-RECONCILIATION-PLAN-1     (#93)
[✓] Sprint 2/11 — QA-PILOT-TRAINING-SYSTEM-ARCHITECTURE-1           (#94)
[✓] Sprint 3/11 — QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER-1            (pending seal)
[ ] Sprint 4/11 — QA-PILOT-TRAINING-CONTENT-MODEL-1
[ ] Sprint 5/11 — QA-PILOT-TRAINING-PACKAGE-GENERATOR-1
[ ] Sprint 6/11 — QA-PILOT-TRAINING-VALIDATION-ENGINE-1
[ ] Sprint 7/11 — QA-PILOT-LEARNING-PATHS-1
[ ] Sprint 8/11 — QA-PILOT-TRAINING-SIMULATION-EXPANSION-1
[ ] Sprint 9/11 — QA-PILOT-PROJECT-TRAINING-PACKAGE-EXPORT-1
[ ] Sprint 10/11 — QA-PILOT-TRAINING-SYSTEM-MCP-SURFACE-1
[ ] Sprint 11/11 — QA-PILOT-TRAINING-SYSTEM-OPERATIONAL-BASELINE-1
```
