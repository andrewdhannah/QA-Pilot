# QA-PILOT READINESS REPORT

**Generated:** 2026-07-23
**Project:** QA Pilot
**Purpose:** Pre-implementation baseline for QA-PILOT-SDK-INTEGRATION-1

---

## 1. Current Maturity

| Dimension | Rating | Evidence |
|-----------|--------|----------|
| **Project validation** | ✅ MATURE | 73 test runners, 63 validators, ~1,150 test cases, ~800 business rules |
| **Evidence intake** | ✅ MATURE | 52 schemas, 481 examples, MCP evidence intake (EM-1–12), evidence lineage, finding lifecycle |
| **Custody enforcement** | ✅ MATURE | 22+ validators enforce `librarian_impact=none`, 10 custody conditions (CC-1–10) |
| **Librarian integration** | ⚠️ FUNCTIONAL | Knowledge adapter (filesystem scrape), broker layer, QA packet ingest |
| **SDK consumption** | ❌ MISSING | No governed SDK for Librarian evidence access. Knowledge adapter directly reads filesystem paths. |
| **Epic validation** | ⚠️ PARTIAL | Epic regression builder exists (ER-1–13) but validates QA-Pilot-local artifacts only. No system-level composition validation. |
| **Epic scenario execution** | ❌ MISSING | No capability to consume Librarian evidence artifacts and validate epic completeness. |
| **Composition validation** | ❌ MISSING | No graph-based validation of evidence relationships across projects. |
| **Projection provenance** | ❌ MISSING | No surface-level validation of evidence projections and their freshness. |
| **CI/automation** | ❌ MISSING | Zero CI configuration. All tests run manually. |
| **Governance documentation** | ✅ MATURE | 76 governance docs, 52 schemas, complete parity matrix. |

---

## 2. Existing Capability Matrix

```
Capability                      Status        Location
──────────────────────────────────────────────────────────────
Test execution                  EXISTS        73 test-*.sh runners
Validator enforcement           EXISTS        63 validate-*.py scripts
Schema contract verification    EXISTS        52 JSON schemas
Evidence intake (local)         EXISTS        data/ evidence files, MCP evidence intake
Evidence lineage tracking       EXISTS        qa_pilot_evidence_lineage.py
Finding lifecycle               EXISTS        data/finding-lifecycle.json (16 OPEN findings)
Receipt creation (local)        EXISTS        qa_pilot_receipt_store.py, data/receipts/
Librarian knowledge reading     EXISTS*       qa_pilot_knowledge_adapter.py (filesystem scrape)
Librarian packet ingest         EXISTS        qa_pilot_qa_packet_ingest.py (sealed Librarian exports)
Librarian→QA broker routing     EXISTS        librarian_broker_qa_pilot.py (Option B)
Custory enforcement             EXISTS        10 conditions, 12 validators
Training sim                    EXISTS        Training system (11 sprints sealed)
Design/accessibility/UAT        EXISTS        Capability modules
Risk-based review               EXISTS        Risk-based review depth
Owner dashboard                 EXISTS        Owner dashboard (LIB_RECEIPT/LIB_LEDGER/LIB_GATE)
Epic regression builder         PARTIAL       Only validates QA-Pilot-local artifacts
Projection provenance           MISSING       No surface freshness validation
SDK consumption                 MISSING       No governed read-only query surface
System composition validation   MISSING       No cross-project graph validation
Epic seal proof                 MISSING       No end-to-end epic verification
CI/automation pipeline          MISSING       No build server integration
```

*Knowledge adapter reads `active/librarian/` filesystem paths directly — this is the pattern that should move behind the SDK.

---

## 3. Designed vs Built vs Assumed

### What QA-Pilot was DESIGNED to become

From the architecture plan (ledger #32), full workbench architecture, and epic regression builder:

> "System-level composition verifier" — not a project test collection.
> 
> Consumes evidence → evaluates scenarios → reports validation results.
> 
> Validates boundaries, provenance, freshness, authority, and completeness.

### What QA-Pilot BUILT

110 sealed sprints across multiple epics:

| Epic | Sprints | What It Built |
|------|---------|---------------|
| Project Init | #1 | Identity, profile, governance |
| Production Lane A/B | #2–#5 | Receipt schema, MCP surface, receipt store, handler registration |
| Librarian MCP Custody | #6 | Option A/B custody decision |
| Broker | #7–#11 | Option B broker plan, implementation, advisory surface, audit store |
| Startup Separation | #12–#14 | Contract registry, negative fixtures |
| Hardening | #15 | Broker audit store hardening |
| QA Packet Ingest | #17 | Librarian export ingestion |
| Milestone Regression | #18 | Regression fixtures, no-cross-project rule |
| Training Sim | #19 | Sim case generation |
| Parity Matrix | #20–#22 | 79-dimension parity analysis, gap closure, regression suite |
| Write Custody | #23–#31 | 6-layer custody chain (enforcement, live integration, lifecycle, receipts, index, summary, surface, startup lock) |
| Full Workbench Architecture | #32 | Architecture plan |
| MCP Evidence Intake | #33 | Evidence intake surface |
| Test Composition | #34 | Test case derivation from evidence |
| Result Export | #35 | Advisory result packet export |
| Epic Regression | #36–#37 | Epic-level regression builder + startup surface |
| Pipeline | #38–#41 | Health, drift, diagnostics, owner review |
| Owner Review | #42–#43 | Decision receipts, startup surface |
| Evidence Checklist | #44–#46 | Checklist, review packet, evidence linker |
| MCP Loop Guard | #47 | Doom-loop prevention |
| Layer Registry | #48–#55 | Registry, drift fix, change receipts, closeout gate, backfill, surface |
| Snapshot Update Gate | #56–#61 | Regression snapshot, update gate, surface, refresh |
| Advisory Review | #62–#65 | Consumer readiness, packet exercise, drift fix, evidence store fix |
| Workbench Chain | #66–#86 | Full workbench chain (21 sprints) |
| Review Depth/Risk | #87–#91 | Risk-based review depth thresholds |
| Browser-Only Pilot | #87–#91 | Real-world browser-only pilot |
| Design Quality | #143–#147 | Accessibility, visual harness, responsive/i18n |
| Design Language | #136–#142 | 50+ tokens, 15+ component classes |
| Migration | #156–#160 | OpenWork → CarbideFrame browser-app copy |
| Assurance Operations | #166–#206 | 6-sprint assurance operating layer: calibration, routing, governance maturity, metrics, calibration, quality profiles |
| Assurance Adoption | #207–#210 | 4 external consumer adoption phases (Librarian, Agent Bridge, Runtime Node) |
| Assurance Contract Evolution | #211–#213 | Evidence freshness semantics, evidence state separation |

### What QA-Pilot ASSUMED (implicitly or planned but not built)

| Assumption | Status | Risk |
|------------|--------|------|
| Librarian evidence is available for consumption | ⚠️ Knowledge adapter scrapes filesystem — not governed | MEDIUM — no freshness/schema/authority guarantees |
| Composition validation works at epic level | ⚠️ Epic regression builder exists but only validates QA-Pilot-local artifacts | MEDIUM — no cross-project graph |
| Evidence Plane outputs are accessible | ⚠️ Evidence plane evaluator output exists in Librarian but QA-Pilot has no SDK to read it | HIGH — will block epic validation |
| Projection provenance is verifiable | ❌ No surface freshness validation exists | HIGH — dashboard projection repair is prerequisite |
| SDK consumption is a simple addition | ❌ No SDK, no query protocol, no capability-oriented surface defined | MEDIUM — requires contract design |

---

## 4. Current Authority Boundary

### Confirmed Boundaries (verified against 22+ validators)

```
LIBRARIAN                              QA-PILOT
─────────────────────                  ─────────────────────
Owns evidence         ───read-only──→  Consumes evidence
Owns provenance       ───read-only──→  Evaluates scenarios
Owns governance state ───read-only──→  Reports validation results
Owns receipts         ───read-only──→  References (librarian_receipt_refs)
Owns ledger           ───read─── ──→  Knowledge adapter (filesystem)
```

### Boundary Violations to Correct

| Issue | Current | Target |
|-------|---------|--------|
| Knowledge adapter reads `active/librarian/` filesystem paths | Direct filesystem scrape | Move behind SDK query surface |
| Evidence plane outputs consumed without schema validation | Implicit trust | Validate through SDK with diagnostic-finding-v1 schema |
| No freshness verification on Librarian evidence | Accepts whatever exists | SDK must return freshness metadata |
| No authority verification on consumed evidence | Accepts whatever exists | SDK must confirm governed provenance |

### Verified non-violations (QA-Pilot does NOT currently):

- ✅ Write Librarian state — 22+ validators enforce `librarian_impact = "none"`
- ✅ Create unofficial receipts — All receipts explicitly `advisory`
- ✅ Maintain duplicate evidence stores — `data/evidence/` index is empty
- ✅ Scrape internal files that should move behind SDK — Knowledge adapter scrapes governance/schema/rule files, which is the current integration point but should migrate to SDK
- ✅ Parallel authority path — No seal/approve/merge authority exists

---

## 5. SDK Requirements Derived from Actual Validator Needs

### Dependency Map

```
Epic Validation Contract
    ↓
Required evidence queries              Derived from
──────────────────────────────────────────────────
Evidence snapshot           OE-001 evaluator output, evidence-provenance-model
Diagnostic findings         OE-002 diagnostic-finding-v1 schema
Composition graph           OE-003 evidence-composition-graph-v1 (nodes, edges, dependency levels)
Authority resolution        OE-004 authority resolution records
Runtime provenance          OE-005 runtime/build provenance (commit SHA, branch, dirty flag)
Projection provenance       OE-006 projection/surface freshness
Epic validation artifacts   Epic validation contract + E4 evidence bundles
```

### Minimal SDK Surface (derived from validator needs)

```python
# The SDK must expose exactly 5 capability-oriented queries —
# no more, no less. Each returns governed, schema-validated artifacts.

EvidenceProvider
    ├── getEvidenceSnapshot()        → EvidenceProvenanceRecord[]
    ├── getFindings()                → DiagnosticFinding[]
    ├── getCompositionGraph()        → EvidenceCompositionGraph
    ├── getProvenanceChain()         → ProvenanceRecord[]
    └── getValidationArtifacts()     → EpicValidationArtifact[]
```

### What the SDK Must NOT Expose

- ❌ No path-based filesystem access
- ❌ No mutation endpoints
- ❌ No cursor state
- ❌ No receipt creation
- ❌ No authority arbitration

### Consumers of the SDK (existing QA-Pilot modules that will migrate)

| Module | Current | SDK Target |
|--------|---------|------------|
| `qa_pilot_knowledge_adapter.py` | Filesystem scrape → SDK | `getEvidenceSnapshot()`, `getProvenanceChain()` |
| `qa_pilot_epic_regression_builder.py` | QA-Pilot-local only → SDK | `getCompositionGraph()`, `getValidationArtifacts()` |
| `qa_pilot_qa_packet_ingest.py` | Sealed exports only → SDK | `getValidationArtifacts()` |
| `qa_pilot_mcp_evidence_intake.py` | Local evidence only → SDK | `getEvidenceSnapshot()`, `getFindings()` |
| `qa_pilot_owner_dashboard.py` | LIB_RECEIPT/LIB_LEDGER references → SDK | `getEvidenceSnapshot()`, `getProvenanceChain()` |

---

## 6. Capacity Check

### Current Metrics

| Metric | Value |
|--------|-------|
| Total scripts | 212 (~56,000 lines) |
| Core modules (qa_pilot_*.py) | 61 (~18,770 lines) |
| Validators (validate-*.py) | 63 (~18,019 lines, ~800 rules) |
| Test runners (test-*.sh) | 73 (~12,826 lines, ~1,150 tests) |
| Schemas | 52 |
| Governance docs | 76 |
| Example fixtures | 481 across 69 domains |
| Data artifacts | 464 files across 24 directories |
| Operational receipts | 90 |
| Open findings | 16 (2 HIGH_ATTENTION, 0 acknowledged) |
| CI/CD | None |
| Git status | Stable on main |

### Maintenance Burden

| Factor | Assessment |
|--------|-----------|
| Validator coverage | Strong — every module has validator + test runner |
| Duplication risk | Existing patterns are consistent (test-*.sh + validate-*.py + schema + governance + fixtures per component) |
| Dependency chain | Well-documented in sprint-ledger, FEATURE-STATUS.md, SESSION-HANDOFF.md |
| Cross-project risk | Extensively guarded (22+ validators check `librarian_impact=none`) |
| Finding backlog | 16 OPEN findings all from 2026-07-20 — none acknowledged or resolved |

### Prerequisite Blockers for SDK Integration

| Blocker | SeverITY | Requires |
|---------|----------|----------|
| Evidence Plane projection repair | HIGH | DASHBOARD-PROJECTION-PROVENANCE-REPAIR-1 must complete first — QA-Pilot needs a stable projection target |
| Evidence index empty | MEDIUM | `data/evidence/` index is empty — no artifacts registered. QA-Pilot's own evidence store needs population before it can validate others |
| No freshness verification | MEDIUM | Current knowledge adapter accepts any file state without freshness checks |

---

## 7. Recommended Implementation Order

```
Step 0: DASHBOARD-PROJECTION-PROVENANCE-REPAIR-1 (prerequisite)
    ↓
Step 1: QA-PILOT-SDK-INTEGRATION-1
    ├── DRAFT: SDK contract (EvidenceProvider interface + schema)
    ├── IMPLEMENT: 5 query methods (read-only, governed)
    ├── MIGRATE: Knowledge adapter from filesystem scrape → SDK
    └── VERIFY: QPSDK-001 through QPSDK-005 acceptance gates
    ↓
Step 2: QA-PILOT-EPIC-VALIDATION-SCENARIOS-1
    ├── Epic scenario suites derived from SDK surface
    ├── Composition validation (grapht topology, node relationships)
    ├── Provenance chain validation (freshness, authority linkage)
    └── Epic seal proof (does the evidence compose to a valid system state?)
```

---

## 8. Authorization Blockers

| Blocker | Status | Owner Action Required |
|---------|--------|----------------------|
| Dashboard projection repair | UNRESOLVED | Prerequisite work in Librarian session |
| SDK contract definition | PENDING | Requires QA-PILOT-SDK-INTEGRATION-1 authorization |
| Knowledge adapter migration plan | PENDING | SDK must exist before migration |
| Epic validation artifact schema | PENDING | Must be defined in SDK contract |

**No immediate blockers to starting QA-PILOT-SDK-INTEGRATION-1 provided the Dashboard Projection Repair is scheduled to complete first.**

---

*This report was produced by a governed agent. Findings are advisory-only. All status markers are 🔍 Pending Owner verification.*
