# QA-PILOT-SDK-INTEGRATION-1 — Sprint Doc

**Project:** QA Pilot
**Type:** infrastructure boundary
**Boundary:** QA Pilot-local (consumes Librarian evidence through governed SDK)
**Librarian impact:** none (SDK reads from `data/evidence-plane/` — read-only)
**Status:** 🔍 Pending Owner review
**Authority:** advisory-only

---

## Sprint Goal

Establish the governed read-only SDK boundary between QA Pilot and the Librarian evidence plane. Replace Knowledge Adapter filesystem scraping with capability-oriented SDK queries.

## Sprint Scope

1. Create `scripts/qa_pilot_evidence_sdk.py` — EvidenceProvider class with 5 query methods
2. Create `docs/schemas/qa-pilot-sdk-integration.schema.json` — SDK response schema
3. Create `docs/governance/QA-PILOT-SDK-INTEGRATION-1.md` — governance doc
4. Create `scripts/validate-qa-pilot-sdk-integration.py` — SDK validator
5. Create `scripts/test-qa-pilot-sdk-integration.sh` — test runner
6. Create `docs/examples/qa-pilot-sdk-integration/` — 5 valid + 4 invalid fixtures
7. Migrate `scripts/qa_pilot_knowledge_adapter.py` — replace filesystem scrape with SDK
8. Verify all QPSDK acceptance gates

## Acceptance Gates

| Gate | Status | Evidence |
|------|--------|----------|
| QPSDK-001 | 🔍 | SDK-only connection — no direct Librarian path access |
| QPSDK-002 | 🔍 | Evidence snapshot schema-valid |
| QPSDK-003 | 🔍 | Findings valid against diagnostic-finding-v1 |
| QPSDK-004 | 🔍 | Composition graph topology preserved |
| QPSDK-005 | 🔍 | No mutation path through SDK |

## Schema

- SDK response envelope: `docs/schemas/qa-pilot-sdk-integration.schema.json`
- Findings: `diagnostic-finding-v1` (inline in evidence plane output)
- Graph: `evidence-composition-graph-v1` (inline in evidence plane output)

## Files Created / Modified

| File | Action | Description |
|------|--------|-------------|
| `scripts/qa_pilot_evidence_sdk.py` | CREATE | SDK implementation |
| `scripts/qa_pilot_knowledge_adapter.py` | MODIFY | Migrate to SDK |
| `docs/schemas/qa-pilot-sdk-integration.schema.json` | CREATE | SDK schema |
| `docs/governance/QA-PILOT-SDK-INTEGRATION-1.md` | CREATE | Governance doc |
| `docs/sprints/QA-PILOT-SDK-INTEGRATION-1.md` | CREATE | This sprint doc |
| `scripts/validate-qa-pilot-sdk-integration.py` | CREATE | Validator |
| `scripts/test-qa-pilot-sdk-integration.sh` | CREATE | Test runner |
| `docs/examples/qa-pilot-sdk-integration/*` | CREATE | Fixtures |
| `reports/QA-PILOT-SDK-INTEGRATION-1-COMPLETION.md` | CREATE | Completion report |

## Verification

- All valid fixtures pass
- All invalid fixtures reject
- Knowledge Adapter no longer accesses `active/librarian/*` paths directly
- SDK status reports read-only, no mutation paths
- QPSDK gates all verified
