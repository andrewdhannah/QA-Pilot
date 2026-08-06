# EPIC-QA-PILOT-BROWSER-ONLY-REAL-WORLD-PILOT-1

**Status:** active
**Owner:** Andrew Hannah
**Authorization:** Owner explicit authorization 2026-07-08

## Purpose

Validate the sealed browser-only QA Pilot workflow with a realistic trainer/learner round trip before adding more features.

## Sprint Sequence

| # | Sprint | Purpose |
|---|--------|---------|
| 1 | QA-PILOT-REAL-WORLD-PILOT-PACKAGE-PREP-1 | Prepare pilot deployment package and instructions |
| 2 | QA-PILOT-REAL-WORLD-ROUNDTRIP-VALIDATION-1 | Run full file-based workflow round trip |
| 3 | QA-PILOT-BROWSER-ONLY-USABILITY-POLISH-1 | Fix issues found in round trip |
| 4 | QA-PILOT-BROWSER-ONLY-PUBLICATION-PACKAGE-1 | Prepare GitHub/static-hosting deployment |

## Bounded Continuation

Authorized through all 4 sprints. Stop conditions: backend requirement, install requirement, auth, cloud dependency, cross-project write, Librarian mutation, authority expansion, contract change, order/scope change, unresolved Owner design question.

## Authority Boundaries

- Static browser only, no backend, no auth, no install
- Deployment/result JSON remains custody boundary
- Local identity ≠ authentication
- No Librarian mutation, no cross-project write, no autonomous publication
