# QA-PILOT-MILESTONE-REGRESSION-SUITE-1 — Sprint Receipt

**Sprint ID:** QA-PILOT-MILESTONE-REGRESSION-SUITE-1
**Type:** Validation / regression suite
**Lane:** parallel_planning
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Input dependency:** QA-PILOT-QA-PACKET-INGEST-1 (sealed ledger #17)

## Scope Satisfied

- Created 12 regression fixtures (5 valid + 7 invalid) in `docs/examples/qa-pilot-milestone-regression/`
  - Valid: claim-registry, project-state, milestone-regression, training-source, derived-reconstruct
  - Invalid: mutation-authorized, no-owner-apply, cross-project-write, mutation-payload, adversarial-shape, authority-promotion, librarian-path
- Created regression validator `scripts/validate-qa-pilot-milestone-regression.py` (11 rules MR-1 through MR-11)
- Created regression test runner `scripts/test-qa-pilot-milestone-regression.sh` (15 tests)
- Created governance doc `docs/governance/QA-PILOT-MILESTONE-REGRESSION.md` (7 sections)
- Created sprint receipt `docs/sprints/QA-PILOT-MILESTONE-REGRESSION-SUITE-1.md`

## Coverage

| Invariant | Rule | Fixtures | Status |
|-----------|------|----------|--------|
| Ingest validator stability | MR-1 | — | Validated |
| Valid fixture ingress | MR-2 | 5 valid | Validated |
| Invalid fixture rejection | MR-3 | 7 invalid | Validated |
| Fail-closed validation | MR-4 | 7 invalid | Validated |
| Advisory invariant | MR-5 | 5 ingested | Validated |
| Cross-project write invariant | MR-6 | 5 ingested | Validated |
| Owner-apply invariant | MR-7 | 5 ingested | Validated |
| No mutation payload | MR-8 | 5 ingested | Validated |
| Local/reconstructable state | MR-9 | 5 ingested | Validated |
| Adversarial fail-closed | MR-10 | malformed | Validated |
| Boundary integrity | MR-11 | — | Validated |

## Hard Boundaries Enforced

- ❌ No Librarian file mutation
- ❌ No MCP bridge activation
- ❌ No local-training-sim implementation
- ❌ No packet application path
- ❌ No authority promotion from Librarian export to QA Pilot write authority
- ❌ No Owner decision bypass

## Next Authorized Sprint

QA-PILOT-LOCAL-TRAINING-SIM-1 — Build local training simulation using the proven ingest chain, after regression stability is confirmed.
