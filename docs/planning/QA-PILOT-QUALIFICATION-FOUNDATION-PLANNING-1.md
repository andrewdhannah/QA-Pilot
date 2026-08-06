# Sprint Planning Report — QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1

**Prepared:** 2026-07-16
**Author:** OpenWork (DeepSeek V4 Flash)
**Status:** ✅ Authorized 2026-07-16 (Owner decision per explicit authorization)
**Project:** QA Pilot
**Lane:** planning / qualification foundation
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** reference read-only (no implementation dependency)
**Authorization:** Owner-authorized 2026-07-16 — see `receipts/decision-resolutions/OD-QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1-AUTHORIZATION.md`

---

## 0. Executive Summary

`QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1` does not exist in the workspace as a document, sprint, work packet, or ledger entry. It is a **proposed sprint** following the established QA Pilot naming convention (`QA-PILOT-<DESCRIPTIVE-NAME>-<NUMBER>`).

This report:

1. Documents the search performed to confirm the sprint does not exist
2. Maps the existing qualification landscape in the CarbideFrame workspace
3. Analyzes the logical scope of this proposed sprint based on name and context
4. Defines a concrete sprint plan with deliverables, acceptance gates, and boundaries
5. Provides the Owner with a decision-ready proposal

---

## 1. Search Results — Not Found

The following comprehensive search was performed:

| Scope | Method | Result |
|-------|--------|--------|
| All text files (`.md`, `.json`, `.txt`, `.py`, `.sh`, `.html`, `.js`, `.css`) | Full-text grep across entire workspace | Not found |
| All 18 zip/tar.gz archives (reports, deliverables, test lanes) | File listing + extracted content grep | Not found |
| `active/qa-pilot/project-state/sprint-ledger.json` (3630 lines, 160 sealed sprints) | Full scan by ID | Not found |
| `active/qa-pilot/packets/` (3 work packets) | Content read | Not found |
| `active/qa-pilot/dispatch/` (3 sprint dispatch packets) | Content read | Not found |
| `inbox/`, `archive/`, `evidence/`, `fixtures/` | Full-text grep | Not found |
| Substring variants: `QUALIFICATION-FOUNDATION`, `FOUNDATION-PLANNING`, `QA-PILOT-QUALIFICATION` | Fuzzy grep | Not found |

**Conclusion:** This sprint does not yet exist in any form — no document, ledger entry, work packet, or archived artifact.

---

## 2. Qualification Landscape — Existing Context

### 2.1 Librarian Qualification Work

The Librarian project contains the primary qualification infrastructure in the workspace:

| Artifact | Type | Status | Description |
|----------|------|--------|-------------|
| `MODEL-QUALIFICATION-REGISTRY-1` | Sprint (sealed) | Planning only | Model Qualification Registry (MQR) — evidence-based eligibility system mapping model IDs to qualification records for governed agent roles. 17-field schema, 4 states, 5 task categories, 11-role matrix. |
| `docs/planning/MODEL-QUALIFICATION-REGISTRY.md` | Planning doc | Complete | Full MQR definition: schema, lifecycle, import pipeline, qualification structure, role integration, shared evidence, Model Router connection. 533 lines. |
| `TRUST-QUALIFICATION-SUITE-1` | Planning doc | Proposed | Agent Trust Control Suite — validates governance composability, boundary enforcement, receipt chain integrity, stale-state handling. 14 test groups across 2 control layers. 854 lines. |
| `AGCC-LOCAL-MODEL-QUALIFICATION-INTEGRATION-1` | Sprint | Implemented | Local model qualification integration for AGCC runtime |
| `WIN-RUNTIME-QUALIFICATION-1` + reconciliation | Sprint | Implemented | Windows runtime qualification |

The MQR defines:
- **17-field qualification record schema** with model_id, provider, runtime, task_category, qualification_level, evidence_ids, pass_rate, etc.
- **4 qualification levels:** `unqualified`, `fast_pass`, `qualified`, `expert`
- **5 task categories:** `code_generation`, `planning`, `security_review`, `documentation`, `routing`
- **Evidence import pipeline** from existing model shootout infrastructure
- **Role qualification matrix** with 11 governed agent roles

### 2.2 QA Pilot Current State

The QA Pilot project is in a **holding state** after completing its migration epic:

| Asset | Status |
|-------|--------|
| `EPIC-QA-PILOT-OPENWORK-TO-CARBIDEFRAME-MIGRATION-1` | ✅ Fully sealed (ledger #156–#160) |
| Active work session | None |
| Next authorized work | Awaiting Owner direction |
| Validator count | 59 |
| Test runner count | 65 |
| Latest recommendation | PROMOTE_TO_CANONICAL_WITH_NOTES |

QA Pilot currently has **no qualification-specific content** — grep for "qualif" across all QA Pilot docs returns zero qualification-related references (only incidental word matches in unrelated contexts).

### 2.3 Gap Analysis

```
Librarian                                              QA Pilot
─────────────────────────────────────                  ─────────────────────────────────────
MQR schema ✓                                            No qualification framework ✗
Trust Qualification Suite ✓                             No qualification test harness ✗
Model qualification records ✓ (planning only)           No QA-item → qualification bridge ✗
Runtime qualification (Win/AGCC) ✓                      No evidence-based qualification pipeline ✗
                                                                                              
QUALIFICATION GAP:                                       
  - QA Pilot has 160 sealed sprints of QA governance    
  - Zero of those sprints address qualification         
  - The Librarian qualification work is model-centric   
  - QA Pilot needs a product/process qualification layer
```

---

## 3. Sprint Definition — QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1

### 3.1 Goal

Establish the planning and architectural foundation for a **QA Pilot Qualification Framework** — a governed, evidence-based system that qualifies QA Pilot's own QA processes, checklist items, review depths, and output artifacts against defined quality thresholds. This is the QA Pilot counterpart to the Librarian's Model Qualification Registry, but scoped to **process and artifact qualification** rather than model qualification.

### 3.2 Motivation

- QA Pilot has 160 sealed sprints of QA governance infrastructure (evidence checklists, review packets, risk-based review depth, workbench items, decision receipts, custody enforcement, pipeline health, drift detection, etc.)
- There is currently **no qualification layer** that answers: "For this QA artifact type, at this quality threshold, has this process demonstrated sufficient evidence?"
- The Librarian MQR answers this for models; QA Pilot needs the same for **QA processes and artifacts**

### 3.3 Owner Decisions Incorporated

The following Owner decisions (2026-07-16) govern this sprint's scope and execution:

| # | Question | Owner Decision |
|---|----------|----------------|
| 1 | Migration canonical status blocking? | **Not blocking.** Dependency = tracked. Proceed in parallel. Use current QA Pilot canonical location with migration recommendation as compatibility input. Planning output must include a migration assumption section identifying artifacts needing path updates after promotion. |
| 2 | Priority among scope areas? | **Tier-based.** Tier 1 (architecture foundation): Landscape Catalog, Schema Design, Evidence Pipeline, Qualification Execution Model. Tier 2 (operationalization): Decision Packet CLI, Validator/Fixture Strategy. Tier 3 (future refinement): Reviewer Workflows, Reporting/Dashboards. Depth concentrates on Tier 1. |
| 3 | Librarian read boundary? | **Contracts readable, implementation prohibited.** Librarian governance contracts (MQR docs, sealed contracts, schemas, public interfaces, qualification artifacts) are read-only reference allowed. Librarian implementation files (source code, internal models) are not allowed. QA Pilot may understand Librarian contracts but may not become dependent on Librarian implementation. |
| 4 | Qualification subject dimensions? | **All three, staged.** Artifact Qualification (first implementation target — required). Process Qualification (defined now, not overbuilt). Reviewer Qualification (defined now, not overbuilt). |
| 5 | Decision packet format? | **Existing QA Pilot CLI pattern.** Use `qa-pilot decision create` generating Markdown output at `docs/decisions/QUALIFICATION-DECISION-XXXX.md` + receipt artifact. No new decision mechanism. |

### 3.4 Scope — Tiered Priority

#### Tier 1 — Required for Architecture (Primary Depth)

| Area | Deliverable | Owner Rationale |
|------|-------------|----------------|
| **Landscape Catalog** | Inventory of QA Pilot assets: what QA Pilot owns, what projects it qualifies, what qualification targets exist | Foundation — must understand the domain before designing |
| **Qualification Schema Design** | Core data model: IDs, relationships, validation rules | Architecture — the schema is the contract |
| **Evidence Pipeline** | Artifact provenance: receipts, lineage, custody | Architecture — how evidence flows into qualification |
| **Qualification Execution Model** | How qualification runs: inputs, outputs, lifecycle | Architecture — the operational model |

#### Tier 2 — Required for Operationalization

| Area | Deliverable |
|------|-------------|
| **Decision Packet Model** | CLI/API surface for qualification decision packets |
| **Validator and Fixture Strategy** | Validation rules and test fixture approach |

#### Tier 3 — Future Refinement

| Area | Deliverable |
|------|-------------|
| **Reviewer Workflows** | Human-in-the-loop qualification review processes |
| **Reporting/Dashboard Surfaces** | Qualification posture visibility |

### 3.5 Qualification Dimensions (Staged Model)

```
Qualification
├── Artifact Qualification ─── Required (first implementation target)
│   └── Does the output satisfy requirements?
│
├── Process Qualification ─── Defined (modeled now, not overbuilt)
│   └── Was the work performed through approved workflow?
│
└── Reviewer Qualification ─── Defined (modeled now, not overbuilt)
    └── Was human/owner decision authority correctly applied?
```

### 3.6 Migration Assumption Section

This sprint proceeds in parallel with the pending migration canonical decision (`PROMOTE_TO_CANONICAL_WITH_NOTES`).

**Dependency tracking:** The migration canonical decision is tracked but NOT blocking.

**Assumptions:**
- Current canonical location: `active/qa-pilot/browser-app/` (post-migration, pre-promotion)
- Qualification contracts are defined against the intended architecture, not current repo layout
- Any artifacts requiring path updates after promotion will be identified in the planning output with explicit `PATH_UPDATE_REQUIRED` markers

**Migration compatibility inputs:**
- EPIC-QA-PILOT-OPENWORK-TO-CARBIDEFRAME-MIGRATION-1 (sealed, #156–#160)
- Roundtrip validation report (120/123 byte-identical, 3 intentional Sprint 3 path fixes)
- Governance integration doc (3-domain separation model)

### 3.7 Librarian Access Rules

| Category | Allowed | Examples |
|----------|---------|---------|
| **Governance contracts** | ✅ Read-only reference | MQR documentation, sealed sprint receipts, schemas, public interfaces, qualification-related artifacts |
| **Implementation files** | ❌ Not allowed | Source code, internal implementation models, runtime internals |
| **Dependency** | ❌ Not allowed | QA Pilot must not become dependent on Librarian internals. It may understand Librarian contracts. |

### 3.8 Not in Scope

- ❌ No implementation of qualification records or pipeline
- ❌ No new schemas deployed to production paths (proposed only)
- ❌ No modification of existing QA Pilot validators or governance layers
- ❌ No new test runners or fixtures (strategy defined, not created)
- ❌ No Librarian implementation file access
- ❌ No cross-project write authority
- ❌ No seal authority conferred
- ❌ No model qualification — this is process/artifact qualification only

### 3.9 Proposed Deliverables

| # | Tier | Deliverable | Format | Description |
|---|------|-------------|--------|-------------|
| 1 | T1 | Qualification Landscape Catalog | `docs/planning/QUALIFICATION-LANDSCAPE-CATALOG.md` | Comprehensive inventory of all QA Pilot layers (#1–#160) classified by qualification eligibility, with target identification |
| 2 | T1 | Qualification Framework Architecture | `docs/governance/QA-PILOT-QUALIFICATION-FRAMEWORK.md` | Full architecture definition: scope, schema, levels, evidence pipeline, execution model, role integration |
| 3 | T1 | QA Pilot Qualification Record Schema | `docs/schemas/qa-pilot-qualification-record.schema.json` (proposed) | Core data model: IDs, relationships, field types, validation rules (Draft 2020-12) |
| 4 | T1 | Evidence Pipeline Blueprint | Embedded in framework doc | Artifact provenance, receipt lineage, custody chain, feed design from existing QA Pilot layers |
| 5 | T1 | Qualification Execution Model | Embedded in framework doc | Inputs, outputs, lifecycle states, trigger conditions |
| 6 | T2 | Decision Packet CLI Spec | `docs/planning/QUALIFICATION-DECISION-CLI-SPEC.md` | CLI/API surface specification for `qa-pilot decision create` following existing pattern |
| 7 | T2 | Validator & Fixture Strategy | Embedded in framework doc | Validation rules design, fixture taxonomy, test approach |
| 8 | T3 | Reviewer Workflow Model | Embedded in framework doc | Human-in-the-loop qualification review process design |
| 9 | T3 | Reporting Surface Concepts | Embedded in framework doc | Qualification posture visibility, dashboard concepts |
| 10 | — | Sprint Sequence Plan | Embedded in framework doc | 3–5 implementation sprint sequence with dependencies and Owner review points |
| 11 | — | Decision Packet | `docs/decisions/QUALIFICATION-DECISION-0001.md` + receipt | CLI-generated decision packet per existing QA Pilot pattern |
| 12 | — | Authorization Receipt | `receipts/decision-resolutions/OD-QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1-AUTHORIZATION.md` | Owner authorization record |
| 13 | — | This Planning Report | `docs/planning/QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1.md` | Sprint planning document (updated with Owner decisions) |

### 3.10 Acceptance Gates

| Gate | Tier | Criteria |
|------|------|----------|
| AG-1 | T1 | All 160 sealed QA Pilot layers classified by qualification eligibility with target identification |
| AG-2 | T1 | Qualification scope clearly defined with all three dimensions (artifact/process/reviewer) staged per Owner direction |
| AG-3 | T1 | Qualification Record schema proposed with IDs, relationships, field types, and validation rules |
| AG-4 | T1 | Qualification levels defined with clear thresholds per artifact type |
| AG-5 | T1 | Evidence pipeline documented: provenance, receipts, lineage, custody, feed design |
| AG-6 | T1 | Qualification execution model defined: inputs, outputs, lifecycle states, trigger conditions |
| AG-7 | T1 | Boundary definition complete: QA Pilot vs. Librarian qualification separation per Owner access rules |
| AG-8 | T1 | Migration assumption section included with path-update markers for post-promotion artifacts |
| AG-9 | T2 | Decision packet CLI spec defined following existing QA Pilot pattern |
| AG-10 | T2 | Validator and fixture strategy designed |
| AG-11 | T3 | Reviewer workflow model defined (future refinement) |
| AG-12 | T3 | Reporting surface concepts documented |
| AG-13 | — | Sprint sequence proposed (3–5 sprints) with dependencies and Owner review points |
| AG-14 | — | Decision packet produced using CLI-generated Markdown format |
| AG-15 | — | Authorization receipt produced and recorded |
| AG-16 | — | No existing QA Pilot governance files modified |
| AG-17 | — | Librarian access: contracts readable, implementation files NOT accessed |
| AG-18 | — | Planning-only — no implementation delivered |

### 3.15 Input Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| QA Pilot sprint ledger (#1–#160) | Reference | ✅ Available |
| QA Pilot governance layer catalog (all validators, schemas, fixtures, test runners) | Reference | ✅ Available |
| Librarian MODEL-QUALIFICATION-REGISTRY-1 | Reference (read-only) | ✅ Sealed |
| Librarian TRUST-QUALIFICATION-SUITE-1 | Reference (read-only) | ✅ Proposed |
| EPIC-QA-PILOT-OPENWORK-TO-CARBIDEFRAME-MIGRATION-1 | Prerequisite epic | ✅ Sealed |
| EPIC-QA-PILOT-DESIGN-QUALITY-REGRESSION-1 | Reference | ✅ Sealed |
| QA-PILOT-RISK-BASED-REVIEW-DEPTH-1 | Reference | ✅ Sealed |
| QA-PILOT-WORKBENCH-CAPABILITY-FOUNDATION-1 | Reference | ✅ Sealed |

### 3.12 Authority Boundary

```
┌─────────────────────────────────────────────────────────────────┐
│                    QA Pilot Boundary                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1             │  │
│  │  Planning Only — No Implementation                        │  │
│  │  Owner-Authorized 2026-07-16                              │  │
│  │                                                           │  │
│  │  Reads: QA Pilot governance layers (advisory-only)        │  │
│  │  Reads: Librarian governance contracts (read-only ref)    │  │
│  │  Writes: docs/planning/* (new planning docs)              │  │
│  │  Writes: docs/governance/* (new governance docs)          │  │
│  │  Writes: docs/decisions/* (decision packets)              │  │
│  │  Writes: receipts/decision-resolutions/* (receipts)       │  │
│  │                                                           │  │
│  │  ❌ No existing QA Pilot governance file modification     │  │
│  │  ❌ No Librarian implementation file access               │  │
│  │  ❌ No Librarian source code read or modified             │  │
│  │  ❌ No schema deployment to production paths              │  │
│  │  ❌ No test runner or fixture creation                    │  │
│  │  ❌ No Ledger mutation                                   │  │
│  │  ❌ No Cross-project write                               │  │
│  │  ❌ No seal authority                                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Existing QA Pilot Governance (sealed, immutable)                │
│  160 sealed sprints, 59 validators, 65 test runners             │
└─────────────────────────────────────────────────────────────────┘
```

### 3.13 Decision Packet Format

Per Owner direction: use the existing QA Pilot CLI-generated decision packet pattern.

**Pattern reference:** `scripts/qa_pilot_review_depth_thresholds_decision_packet.py`

**Target command:** `qa-pilot decision create`

**Output structure:**
- `docs/decisions/QUALIFICATION-DECISION-XXXX.md` — Markdown decision document
- Receipt artifact in receipts store

**Constraints:**
- Consistent with existing sealed sprint workflow
- Reproducible and machine-verifiable
- Easy to review in Markdown
- Can later produce structured receipts
- No new decision mechanism introduced

### 3.14 Proposed Sprint Sequence (Follow-on)

| Sprint | Tier | Description | Dependencies |
|--------|------|-------------|--------------|
| **QA-PILOT-QUALIFICATION-SCHEMA-1** | T1 | Deploy Qualification Record schema, validator, and fixtures | This planning sprint |
| **QA-PILOT-QUALIFICATION-EVIDENCE-PIPELINE-1** | T1 | Implement evidence pipeline from existing QA Pilot layers to qualification records | Schema sprint |
| **QA-PILOT-QUALIFICATION-EXECUTION-1** | T1 | Implement qualification execution model: inputs, outputs, lifecycle | Pipeline sprint |
| **QA-PILOT-QUALIFICATION-REVIEW-SURFACE-1** | T2 | Create Owner review surface and decision packet CLI | Execution sprint |
| **QA-PILOT-QUALIFICATION-ROUNDTRIP-VALIDATION-1** | T3 | End-to-end validation with real QA Pilot data | All above |

---

## 4. Related Workspace Context

### 4.1 What QA Pilot Already Has (160 sealed sprints)

The qualification framework would build on these existing governance layers:

| Layer Group | Sprints | Relevance to Qualification |
|-------------|---------|---------------------------|
| Evidence pipeline | #33–#46 (MCP evidence intake, test composition, result packet export, checklists, evidence linker) | 🟢 Core — evidence is foundation of qualification |
| Review depth | #88–#91 (review depth thresholds, risk-based review, decision packets) | 🟢 Core — risk levels inform qualification thresholds |
| Workbench | #66–#87 (workbench items, decisions, action packets, handoff intake) | 🟢 Core — workbench items are qualification targets |
| Custody | #23–#31 (write custody, lifecycle custody, custody receipts) | 🟡 Supporting — custody proofs inform qualification trust |
| Pipeline health | #37–#40, #47–#65 (pipeline health, drift, registry, snapshots) | 🟡 Supporting — pipeline integrity informs qualification |
| Startup surfaces | Multiple (startup parity, regression snapshots, surfaces) | 🟡 Supporting — startup surfaces expose qualification posture |
| Migration | #156–#160 (app migration, governance integration, roundtrip) | ⚪ Context — migration complete |
| Design/I18N | #136–#155 (design language, quality regression, visual parity) | ⚪ Context — design quality informs artifact qualification criteria |

### 4.2 Key Design Patterns to Follow

The sprint should follow these established QA Pilot design patterns:

| Pattern | Precedent | Application |
|---------|-----------|-------------|
| Schema + Validator + Fixtures | `QA-PILOT-WORKBENCH-CAPABILITY-FOUNDATION-1` (#66) | Qualification Record schema with valid/invalid fixtures |
| CLI Operations | `qa_pilot_workbench.py` (6 commands) | CLI for qualification record CRUD |
| Advisory-only enforcement | All sealed sprints | Qualification records are advisory — never auto-authorize |
| Startup surface extension | `QA-PILOT-WORKBENCH-CAPABILITY-FOUNDATION-STARTUP-SURFACE-1` | Expose qualification posture in startup report |
| Registry change receipt | #51, #54, #55 | RCR for registry-impacting qualification additions |
| Snapshot update gate | #56, #57, #58, #59 | SUG for qualification regression baselines |

### 4.3 Distinction from Librarian Qualification

| Dimension | Librarian MQR | QA Pilot Qualification (Proposed) |
|-----------|---------------|-----------------------------------|
| **Subject** | AI Models | QA Processes & Artifacts |
| **Task categories** | code_generation, planning, security, docs, routing | evidence_collection, review_depth, checklist_compliance, workbench_item, audit_trail |
| **Qualification objects** | model_id + task_category | process_step + artifact_type |
| **Evidence source** | Model shootout runs | Existing QA Pilot governance pipeline (#33–#160) |
| **Consumer** | Model Router, Work Intake Agent | QA Pilot startup surface, Owner review panel |
| **Trust model** | 3-tier (first-party, vetted, published) | 2-tier (pipeline-verified, Owner-audited) |

---

## 5. Status

✅ **Authorized 2026-07-16** per Owner explicit authorization with the following constraints:

| Constraint | Value |
|------------|-------|
| Migration canonical promotion | Tracked as dependency, NOT blocking |
| Priority model | Tier 1 (architecture) receives primary depth |
| Librarian access | Contracts readable, implementation files prohibited |
| Qualification dimensions | Artifact (required), Process (defined), Reviewer (defined) |
| Decision packet format | Existing QA Pilot CLI-generated pattern (`qa-pilot decision create`) |
| Implementation | Planning-only — no schema deployment, no test runner creation, no ledger mutation |

**Authorization receipt:** `receipts/decision-resolutions/OD-QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1-AUTHORIZATION.md`

---

*Report generated by OpenWork (DeepSeek V4 Flash) on 2026-07-16. Updated with Owner decisions and authorization 2026-07-16. This is a planning-only document. No implementation, seal, or ledger mutation is authorized.*
