# QA Pilot SDK Integration — QA-PILOT-SDK-INTEGRATION-1

**Sprint:** QA-PILOT-SDK-INTEGRATION-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** Advisory only. Read-only. No cross-project mutation.

---

## 1. Purpose

Create the governed read-only SDK boundary between QA Pilot and the Librarian evidence plane. Replace the Knowledge Adapter's direct filesystem reads (`open(active/librarian/...)`) with capability-oriented queries against governed evidence contracts.

This is an **infrastructure boundary work order**, not a product expansion. It establishes the trust boundary that all later QA-Pilot phases (epic validation, onboarding, teaching, testing) depend on.

## 2. Architecture

```
                    Librarian
                       │
                       │  SDK (new boundary)
                       ▼
              Evidence Query Surface
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
 Evidence Snapshot  Findings     Provenance
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                  QA-Pilot
                       │
                       ▼
             Epic Composition Validation
```

### SDK Surface

| SDK Function | Contract Source | Purpose |
|---|---|---|
| `getEvidenceSnapshot()` | OE-001 Evidence Plane | Consume current evidence state |
| `getFindings()` | OE-002 Diagnostic Finding | Consume diagnostic findings |
| `getCompositionGraph()` | OE-003 Composition Graph | Validate relationships |
| `getProvenanceChain()` | OE-005/OE-006 | Validate lineage chains |
| `getValidationArtifacts()` | Epic Validation Contract | Validate seal requirements |

### Migration Target

| Current | → | Target |
|---------|---|--------|
| Knowledge Adapter: `open(active/librarian/...)` | → | SDK: `provider.getEvidenceSnapshot()` |
| Filesystem path resolution | → | Capability-oriented queries |
| No schema validation | → | Evidence-provenance, diagnostic-finding-v1, composition-graph-v1 schemas |

## 3. Scope (In scope)

1. **SDK read contract** — expose only validator-required queries (5 methods)
2. **Knowledge Adapter migration** — replace filesystem scraping with SDK query calls
3. **Epic validation foundation** — prove QA-Pilot can retrieve findings, graph, provenance, and validation artifacts through the SDK

Acceptance condition: QA-Pilot receives the same evidence information without direct Librarian path access.

## 4. Scope (Out of scope / Non-goals)

- ❌ No mutation APIs — no cursor updates, receipt creation, or authority arbitration
- ❌ No second evidence store — QA-Pilot references, does not own source evidence
- ❌ No epic scenario suites yet (future work order)
- ❌ No onboarding/teaching surface expansion (future)
- ❌ No CI pipeline setup
- ❌ QA-Pilot does not mutate Librarian state
- ❌ QA-Pilot does not generate authoritative receipts
- ❌ QA-Pilot does not resolve findings
- ❌ QA-Pilot does not repair failed validations

## 5. Acceptance Gates

| Gate | Criteria |
|------|----------|
| **QPSDK-001** | QA-Pilot connects through SDK only — no direct Librarian path access |
| **QPSDK-002** | Evidence snapshot retrieval produces schema-valid governed package |
| **QPSDK-003** | Findings validate against diagnostic-finding-v1 schema |
| **QPSDK-004** | Composition graph retrieval preserves topology (nodes, edges, levels) |
| **QPSDK-005** | No mutation path exists through SDK |

## 6. Authority Boundaries

- **Librarian** owns evidence, provenance, and governance state
- **QA-Pilot** consumes evidence, evaluates scenarios, reports validation results
- **SDK** is the governed bridge — read-only, capability-oriented, no mutation paths

The SDK does not confer approval, seal, merge, or production-readiness authority.

## 7. Schema

See `docs/schemas/qa-pilot-sdk-integration.schema.json` for the SDK response schema.

The SDK validates all output against:
- `diagnostic-finding-v1` (inline in findings)
- `evidence-composition-graph-v1` (inline in composition graph)
- `qa-pilot-sdk-integration.schema.json` (SDK response envelope)

## 8. Files

| File | Description |
|------|-------------|
| `scripts/qa_pilot_evidence_sdk.py` | SDK implementation (EvidenceProvider class + CLI) |
| `scripts/qa_pilot_knowledge_adapter.py` | Updated — uses SDK instead of filesystem scrape |
| `scripts/validate-qa-pilot-sdk-integration.py` | Validator for SDK integration |
| `scripts/test-qa-pilot-sdk-integration.sh` | Test runner for SDK integration |
| `docs/schemas/qa-pilot-sdk-integration.schema.json` | SDK response schema |
| `docs/examples/qa-pilot-sdk-integration/` | Valid and invalid fixtures |
| `docs/governance/QA-PILOT-SDK-INTEGRATION-1.md` | This governance document |

## 9. Implementation Notes

- The SDK consumes `data/evidence-plane/latest-evaluation.json` from the CarbideFrame evidence plane
- All 5 query methods return `read_only_validation` metadata proving no mutation path exists
- The Knowledge Adapter is migrated from filesystem scraping to SDK query calls
- Every SDK result includes `read_only: true` and `no_mutation_authority: true`

## 10. Dependencies

- **Prerequisite:** DASHBOARD-PROJECTION-PROVENANCE-REPAIR-1 (stable projection target)
- **Prerequisite:** QA-PILOT-000 (context inventory complete)
- **Consumes:** OE-001 through OE-006 evidence plane outputs
- **Provides:** Governed SDK surface for QA-PILOT-EPIC-SCENARIO-SUITES (future)
