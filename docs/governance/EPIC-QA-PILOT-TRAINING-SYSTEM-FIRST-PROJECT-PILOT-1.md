# EPIC-QA-PILOT-TRAINING-SYSTEM-FIRST-PROJECT-PILOT-1

**Status:** active
**Owner:** Andrew Hannah
**Authorization:** Owner explicit authorization 2026-07-08
**Pilot target:** Librarian

## Purpose

Use the sealed QA Pilot Training System to generate, validate, and export a real project training/help package from Librarian canonical sources.

## Background

QA Pilot Training System is sealed through EPIC-QA-PILOT-TRAINING-SYSTEM-1, ledger #93–#103. This epic validates the system on a real project.

## Sprint Sequence

| # | Sprint | Purpose |
|---|--------|---------|
| 1 | QA-PILOT-FIRST-PROJECT-PILOT-SOURCE-SELECTION-1 | Select and freeze Librarian canonical source set |
| 2 | QA-PILOT-FIRST-PROJECT-PILOT-PACKAGE-DESIGN-1 | Design training package structure |
| 3 | QA-PILOT-FIRST-PROJECT-PILOT-GENERATION-1 | Generate the training/help package |
| 4 | QA-PILOT-FIRST-PROJECT-PILOT-VALIDATION-1 | Validate the generated package |
| 5 | QA-PILOT-FIRST-PROJECT-PILOT-LEARNING-PATH-1 | Create ordered learning path |
| 6 | QA-PILOT-FIRST-PROJECT-PILOT-EXPORT-AND-REVIEW-1 | Export package for Owner review |

## Bounded Continuation

Authorized through all 6 sprints in order. Stop conditions: validation failure, missing provenance, zero-source content, unsupported authority claim, source hash mismatch, need to mutate Librarian, cross-project write requirement, publication request, MCP authority expansion, design question requiring Owner, need to change sprint order or scope.

## Authority Boundaries

- Librarian remains canonical
- QA Pilot reads, transforms, validates, exports derived training artifacts
- QA Pilot may not mutate Librarian, publish autonomously, grant authority through training material
- Owner decision required before adoption or publication

## Acceptance Criteria

1. Librarian training/help package generated
2. Every artifact has source provenance
3. Validation passes
4. Export package exists
5. Owner review packet exists
6. Publication remains gated by Owner approval
7. No cross-project write
8. No authority expansion
