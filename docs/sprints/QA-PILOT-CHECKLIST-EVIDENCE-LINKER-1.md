# Sprint Receipt — QA-PILOT-CHECKLIST-EVIDENCE-LINKER-1

**Status:** 🔍 Active
**Type:** Governance / checklist evidence linker contract
**Lane:** governance
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none

---

## Scope Satisfied

Added a deterministic linking layer between evidence checklists (#44) and the actual pipeline evidence stores (#33-#45). Validates that evidence refs inside each checklist item point to real, existing pipeline artifacts — evidence packets, test cases, result packets, epic suites, and other stored records. Each link resolves to found, missing, or stale with aggregate status reporting.

## Deliverables

| Artifact | Path |
|----------|------|
| Schema | `docs/schemas/qa-pilot-checklist-evidence-linker.schema.json` |
| Governance doc | `docs/governance/QA-PILOT-CHECKLIST-EVIDENCE-LINKER.md` |
| Valid fixture 1 | `docs/examples/qa-pilot-checklist-evidence-linker/valid-all-found.json` |
| Valid fixture 2 | `docs/examples/qa-pilot-checklist-evidence-linker/valid-some-missing.json` |
| Invalid fixture 1 | `docs/examples/qa-pilot-checklist-evidence-linker/invalid-advisory-false.json` |
| Invalid fixture 2 | `docs/examples/qa-pilot-checklist-evidence-linker/invalid-wrong-custody.json` |
| Invalid fixture 3 | `docs/examples/qa-pilot-checklist-evidence-linker/invalid-aggregate-mismatch.json` |
| Invalid fixture 4 | `docs/examples/qa-pilot-checklist-evidence-linker/invalid-missing-no-refs-list.json` |
| Validator | `scripts/validate-qa-pilot-checklist-evidence-linker.py` (14 EL rules) |
| Test runner | `scripts/test-qa-pilot-checklist-evidence-linker.sh` |

## Linker Schema

- **Required fields:** linker_id (EL-*), source_checklist_id (EC-*), title, description, links (min 1), aggregate (total_links, found, missing, stale, all_found), advisory_only, custody, librarian_impact, not_seal_authority, not_librarian_mutation_authority, created_at
- **Link statuses:** found, missing, stale
- **Aggregate rules:** total_links == len(links), found + missing + stale == total_links
- **Boundary fields:** advisory_only=true, custody=qa-pilot-local, librarian_impact=none, authority disclaimers

## Business Rules (14 EL rules)

| Rule | Description |
|------|-------------|
| EL-1 | Conform to qa-pilot-checklist-evidence-linker.schema.json |
| EL-2 | advisory_only must be true |
| EL-3 | custody must be qa-pilot-local |
| EL-4 | librarian_impact must be none |
| EL-5 | not_seal_authority must be present and >= 20 chars |
| EL-6 | not_librarian_mutation_authority must be present and >= 20 chars |
| EL-7 | source_checklist_id must reference an EC-* pattern |
| EL-8 | At least one link check required |
| EL-9 | Aggregate counts must match link array exactly |
| EL-10 | If missing > 0, aggregate.missing_refs must be non-empty |
| EL-11 | If stale > 0, aggregate.stale_refs must be non-empty |
| EL-12 | all_found=true only when missing=0 and stale=0 |
| EL-13 | No authority claims in descriptions, titles, or detail fields |
| EL-14 | No Librarian mutation authority referenced |

## Stores Scanned

- `data/evidence/evidence-index.json` (#33)
- `data/test-cases/test-case-index.json` (#34)
- `data/result-packets/result-packet-index.json` (#35)
- `data/epic-regression/epic-regression-index.json` (#36)
- `data/owner-decisions/` (#42)
- `docs/examples/qa-pilot-evidence-checklist/` (#44)
- `docs/examples/qa-pilot-checklist-review-packet/` (#45)

## Validation

- **Validator:** 14/14 EL rules defined and enforced
- **Valid fixtures:** 2/2 pass
- **Invalid fixtures:** 4/4 correctly rejected
- **Existing validators:** All chain validators remain green
- **No Librarian files modified**

## Authorization

Sprint authorized 2026-07-07 by Owner: "I authorize QA Pilot sprint QA-PILOT-CHECKLIST-EVIDENCE-LINKER-1."

**Next authorized sprint:** None — awaiting Owner direction.
