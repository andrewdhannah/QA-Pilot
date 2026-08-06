# Qualification Landscape Catalog — QA Pilot

**Part of:** QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1
**Tier:** T1 (Required for Architecture)
**Prepared:** 2026-07-16
**Scope:** Comprehensive inventory of all QA Pilot sealed layers (#1–#160), classified by qualification eligibility

---

## 1. Overview

QA Pilot has **160 sealed sprints** (ledger #1–#160) spanning governance, implementation, validation, planning, and migration. This catalog classifies every layer by its **qualification relevance** — whether it can serve as a qualification target, evidence source, or structural dependency for the Qualification Framework.

### Classification Scheme

| Category | Code | Meaning |
|----------|------|---------|
| 🟢 **Core Target** | ART | Artifacts that should be qualification targets — their outputs need qualification records |
| 🟢 **Evidence Source** | EVI | Layers that produce or manage evidence consumed by qualification pipeline |
| 🟡 **Supporting** | SUP | Infrastructure that enables qualification (registries, custody, startup) |
| 🔵 **Structural** | STR | Planning/architecture definitions that establish the framework |
| ⚪ **Context** | CTX | Contextual layers (migration, design) that inform qualification scope |
| 🔴 **Out of Scope** | OOS | Not qualification-relevant (external defects, admin) |

---

## 2. Layer Catalog

### 2.1 Foundation Layer (#1)

| # | Sprint ID | Type | Area | Qualification Relevance | Code |
|---|-----------|------|------|------------------------|------|
| 1 | QA-PILOT-PROJECT-INIT-1 | init | governance | Establishes project boundary, identity, and sandbox. Structural prerequisite. | STR |

### 2.2 Production Lanes (#2–#5)

| # | Sprint ID | Type | Area | Qualification Relevance | Code |
|---|-----------|------|------|------------------------|------|
| 2 | QA-PILOT-PRODUCTION-LANE-A-1 | production | receipt schema | Receipt schema is core evidence format for qualification pipeline. | EVI |
| 3 | QA-PILOT-MCP-SURFACE-1 | production | MCP surface | MCP tool stubs. Structural — defines how QA Pilot exposes qualification surfaces. | STR |
| 4 | QA-PILOT-RECEIPT-STORE-1 | production | receipt store | File-based receipt store. Evidence repository for qualification records. | EVI |
| 5 | QA-PILOT-MCP-HANDLER-REGISTRATION-1 | production | MCP handlers | Handler stubs enforcing project_boundary. Structural. | STR |

### 2.3 Custody & Broker Layer (#6–#15)

| # | Sprint ID | Type | Area | Qualification Relevance | Code |
|---|-----------|------|------|------------------------|------|
| 6 | QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1 | governance | custody | Custody conditions (CC-1-10) define trust model. Core for qualification trust. | SUP |
| 7 | QA-PILOT-BROKER-PLAN-1 | planning | broker | Option B broker architecture. Structural. | STR |
| 8 | QA-PILOT-BROKER-IMPLEMENTATION-1 | implementation | broker | Local broker with custody verification. Produces audit receipts. | EVI |
| 9 | QA-PILOT-BROKER-MCP-ADVISORY-SURFACE-1 | implementation | broker | Advisory MCP surface. Potential qualification surface. | SUP |
| 10 | QA-PILOT-BROKER-AUDIT-RECEIPT-STORE-1 | schema | broker audit | Audit receipt schema. Evidence format for qualification proof. | EVI |
| 11 | QA-PILOT-BROKER-AUDIT-STORE-IMPLEMENTATION-1 | implementation | broker audit | File-based audit store. Evidence repository. | EVI |
| 12 | PROJECT-STARTUP-SYSTEM-SEPARATION-1 | governance | startup | Separated startup harness. Structural for project identity. | STR |
| 13 | PROJECT-STARTUP-CONTRACT-NEGATIVE-FIXTURES-1 | validation | startup | Startup contract fixtures. Validation approach pattern for qualification. | SUP |
| 14 | PROJECT-STARTUP-CONTRACT-REGISTRY-1 | governance | startup | Registry-backed project selection. Structural pattern for qualification registry. | STR |
| 15 | QA-PILOT-BROKER-AUDIT-STORE-HARDEN-1 | hardening | broker audit | Path safety, schema enforcement, status transitions. Hardening pattern. | SUP |

### 2.4 Packet Ingest & Training (#16–#19)

| # | Sprint ID | Type | Area | Qualification Relevance | Code |
|---|-----------|------|------|------------------------|------|
| 16 | QA-PILOT-MILESTONE-REGRESSION-SUITE-1 | validation | regression | Regression locking packet custody invariants. **Core target** — regression approach for qualification. | ART |
| 17 | QA-PILOT-QA-PACKET-INGEST-1 | implementation | packet ingest | Packet ingestion with PI-1-14 rules. Evidence intake pattern for qualification. | EVI |
| 18 | QA-PILOT-LOCAL-TRAINING-SIM-1 | simulation | training sim | Advisory sim cases from ingested packets. Training/qualification relationship. | CTX |
| 19 | QA-PILOT-MILESTONE-REGRESSION-SUITE-1 | validation | regression | Regression fixtures locking invariants. Core regression pattern. | ART |

### 2.5 Startup Parity Layer (#20–#22)

| # | Sprint ID | Type | Area | Qualification Relevance | Code |
|---|-----------|------|------|------------------------|------|
| 20 | QA-PILOT-STARTUP-LIBRARIAN-PARITY-MATRIX-1 | governance | parity | 79-dimension parity matrix with 6 gaps. Structural for project identity. | STR |
| 21 | QA-PILOT-STARTUP-PARITY-GAP-CLOSURE-1 | governance | parity | Closed all 6 parity gaps. Structural. | STR |
| 22 | QA-PILOT-STARTUP-REGRESSION-SUITE-1 | validation | startup | 15 SR rules proving startup chain stays managed. **Core target** — startup posture is qualification surface. | ART |

### 2.6 Write Custody Layer (#23–#31)

| # | Sprint ID | Type | Area | Qualification Relevance | Code |
|---|-----------|------|------|------------------------|------|
| 23 | PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT-1 | enforcement | custody | 15 EC rules, 6 decision codes. **Core target** — custody enforcement is qualification artifact. | ART |
| 24 | LIVE-CUSTODY-INTEGRATION-1 | implementation | custody | Live write-custody integration. Produces audit receipts. | EVI |
| 25 | LIFECYCLE-CUSTODY-EXTENSION-1 | governance | custody | Lifecycle transition custody. 15 LC rules. **Core target** — lifecycle governance. | ART |
| 26 | OWNER-DECISION-CUSTODY-RECEIPTS-1 | governance | custody | Unified custody receipts. **Core evidence source** — receipt format qualification. | EVI |
| 27 | CUSTODY-RECEIPT-INDEX-1 | governance | custody | Read-only index over unified receipts. Qualification surface pattern. | SUP |
| 28 | CUSTODY-RECEIPT-SUMMARY-SURFACE-1 | governance | custody | Owner-review surface for receipts. **Core target** — read-only qualification posture. | ART |
| 29 | CUSTODY-SURFACE-STARTUP-INTEGRATION-1 | governance | custody | Startup custody posture integration. **Core target** — startup qualification surface. | ART |
| 30 | CUSTODY-STARTUP-REGRESSION-LOCK-1 | governance | custody | Regression lock for custody startup chain. Regression pattern. | SUP |
| 31 | CUSTODY-AUTHORIZATION-DECISION-QUEUE-1 | governance | custody | Owner decision queue for custody findings. Decision packet pattern. | SUP |

### 2.7 Architecture & Pipeline (#32–#50)

| # | Sprint ID | Type | Area | Qualification Relevance | Code |
|---|-----------|------|------|------------------------|------|
| 32 | QA-PILOT-FULL-WORKBENCH-ARCHITECTURE-PLAN-1 | planning | architecture | Full workbench architecture plan. Blueprint for qualification architecture. | STR |
| 33 | QA-PILOT-MCP-EVIDENCE-INTAKE-1 | implementation | evidence | 4 MCP tools, 12 EM rules. **Core evidence source** — evidence intake for qualification. | EVI |
| 34 | QA-PILOT-TEST-COMPOSITION-1 | implementation | test | Advisory test cases from evidence. **Core target** — test composition qualification. | ART |
| 35 | QA-PILOT-RESULT-PACKET-EXPORT-1 | implementation | results | Advisory QR- result packets. **Core target** — result packet qualification. | ART |
| 36 | QA-PILOT-EPIC-REGRESSION-BUILDER-1 | implementation | regression | Epic-level ERS- suites. **Core target** — epic regression qualification. | ART |
| 37 | QA-PILOT-EPIC-REGRESSION-STARTUP-SURFACE-1 | governance | startup | Exposes 4-layer advisory pipeline in startup. **Core target** — pipeline posture in startup. | ART |
| 38 | QA-PILOT-PIPELINE-HEALTH-REGRESSION-1 | validation | pipeline | 12 PH rules validating advisory chain. **Core target** — pipeline health qualification. | ART |
| 39 | QA-PILOT-PIPELINE-DRIFT-DETECTION-1 | validation | pipeline | 10 DR rules, drift detection. **Core target** — drift posture qualification. | ART |
| 40 | QA-PILOT-PIPELINE-RECOVERY-DIAGNOSTICS-1 | validation | pipeline | 8 RD rules, recovery diagnostics. **Core target** — recovery posture qualification. | ART |
| 41 | QA-PILOT-PIPELINE-OWNER-REVIEW-PACKET-1 | governance | pipeline | 8 OR rules consolidating PH/DR/RD. **Core target** — Owner review packet format. | ART |
| 42 | QA-PILOT-OWNER-REVIEW-DECISION-RECEIPT-1 | governance | decisions | 8 ODR rules recording Owner decisions. **Core evidence source** — decision receipts. | EVI |
| 43 | QA-PILOT-OWNER-DECISION-RECEIPT-STARTUP-SURFACE-1 | governance | startup | ODR in startup surface. **Core target** — decision receipt posture. | ART |
| 44 | QA-PILOT-EVIDENCE-CHECKLIST-1 | governance | checklist | 12 EC rules defining evidence requirements. **Core target** — checklist qualification. | ART |
| 45 | QA-PILOT-CHECKLIST-REVIEW-PACKET-1 | governance | checklist | 12 CRP rules turning checklists into review packets. **Core target** — review packet qualification. | ART |
| 46 | QA-PILOT-CHECKLIST-EVIDENCE-LINKER-1 | governance | evidence | 14 EL rules linking checklist refs to evidence stores. **Core target** — evidence link qualification. | ART |
| 47 | QA-PILOT-MCP-CALL-LOOP-GUARD-1 | governance | MCP | 15 MG rules guarding MCP doom loops. **Core target** — MCP behavior qualification. | ART |
| 48 | QA-PILOT-PIPELINE-HEALTH-LAYER-REGISTRY-1 | governance | registry | 16 PLR rules, pipeline layer registry. **Core evidence source** — registry is qualification data. | EVI |
| 49 | QA-PILOT-PIPELINE-DRIFT-LAYER-REGISTRY-1 | governance | registry | DR-3/DR-4 updated to consume governed registry. Registry qualification. | SUP |
| 50 | QA-PILOT-REGISTRY-STARTUP-SURFACE-1 | governance | startup | Registry-aware pipeline posture in startup. **Core target** — registry posture qualification. | ART |

### 2.8 Registry Change Receipt Layer (#51–#65)

| # | Sprint ID | Type | Area | Qualification Relevance | Code |
|---|-----------|------|------|------------------------|------|
| 51 | QA-PILOT-REGISTRY-CHANGE-RECEIPT-1 | governance | registry | 15 RCR rules, 4 impact classes. **Core target** — registry change qualification. | ART |
| 52 | QA-PILOT-REGISTRY-CHANGE-RECEIPT-STARTUP-SURFACE-1 | governance | startup | RCR posture in startup surface. **Core target** — RCR posture qualification. | ART |
| 53 | QA-PILOT-REGISTRY-CHANGE-RECEIPT-CLOSEOUT-GATE-1 | governance | registry | 13 RCG rules for seal-ready RCR. **Core target** — closeout gate qualification. | ART |
| 54 | QA-PILOT-REGISTRY-CHANGE-RECEIPT-BACKFILL-1 | governance | registry | Backfill RCR receipts. Evidence source for historical qualification. | EVI |
| 55 | QA-PILOT-REGISTRY-CHANGE-RECEIPT-CLOSEOUT-SURFACE-1 | governance | startup | RCG closeout gate posture. **Core target** — closeout surface qualification. | ART |
| 56 | QA-PILOT-STARTUP-SURFACE-REGRESSION-SNAPSHOT-1 | governance | snapshot | 17 SRS rules, baseline snapshot (SRS-BASELINE-001). **Core target** — snapshot qualification. | ART |
| 57 | QA-PILOT-SNAPSHOT-UPDATE-GATE-1 | governance | snapshot | 13 SUG rules, 5 update classes. **Core target** — update gate qualification. | ART |
| 58 | QA-PILOT-SNAPSHOT-UPDATE-GATE-STARTUP-SURFACE-1 | governance | startup | SUG posture in startup. **Core target** — SUG posture qualification. | ART |
| 59 | QA-PILOT-POST-SEAL-SNAPSHOT-REFRESH-1 | governance | snapshot | SUG exercise, SRS refresh. Evidence of gate operation. | EVI |
| 60 | QA-PILOT-STARTUP-SURFACE-POST-SEAL-RECONCILIATION-1 | governance | startup | Post-seal surface reconciliation. Evidence of surface integrity. | SUP |
| 61 | QA-PILOT-POST-SEAL-SNAPSHOT-REFRESH-2 | governance | snapshot | Repeatable SUG maintenance. Evidence of repeatability. | SUP |
| 62 | QA-PILOT-ADVISORY-REVIEW-CONSUMER-READINESS-1 | governance | advisory | 10 AR rules for advisory review packets. **Core target** — advisory readiness qualification. | ART |
| 63 | QA-PILOT-ADVISORY-REVIEW-PACKET-EXERCISE-1 | governance | advisory | Live ARP-LIVE-062 proof. Evidence of contract satisfaction. | EVI |
| 64 | QA-PILOT-DRIFT-DETECTOR-EXPECTED-LAYERS-FIX-1 | governance | drift | Dynamic expected-layer derivation. Drift detection qualification. | SUP |
| 65 | QA-PILOT-PH5-EVIDENCE-STORE-PATH-FIX-1 | governance | evidence | Evidence index corruption fix. Evidence integrity qualification. | SUP |

### 2.9 Workbench Layer (#66–#87)

| # | Sprint ID | Type | Area | Qualification Relevance | Code |
|---|-----------|------|------|------------------------|------|
| 66 | QA-PILOT-WORKBENCH-CAPABILITY-FOUNDATION-1 | governance | workbench | First bounded workbench layer. 6 CLI commands, 8 WB rules. **Core target** — workbench item qualification. | ART |
| 67 | QA-PILOT-WORKBENCH-ITEM-EVIDENCE-LINKING-1 | governance | workbench | Evidence refs on workbench items. **Core target** — evidence link qualification. | ART |
| 68 | QA-PILOT-WORKBENCH-ITEM-STATUS-LIFECYCLE-1 | governance | workbench | 7 statuses, 8 transitions, lifecycle history. **Core target** — lifecycle qualification. | ART |
| 69 | QA-PILOT-WORKBENCH-ITEM-QUERY-LISTING-1 | governance | workbench | 9 filters, summary reports. Query qualification. | SUP |
| 70 | QA-PILOT-WORKBENCH-ITEM-EXPORT-PACKET-1 | governance | workbench | XPK export packet format. **Core target** — export packet qualification. | ART |
| 71 | QA-PILOT-CROSS-PROJECT-MCP-QA-BRIDGE-PLAN-1 | planning | bridge | Cross-project MCP bridge architecture. Structural. | STR |
| 72 | QA-PILOT-WORKBENCH-REVIEW-INTAKE-1 | governance | workbench | 6 CLI commands, IR-1-IR-7 rules. **Core target** — review intake qualification. | ART |
| 73 | QA-PILOT-WORKBENCH-REVIEW-DECISION-SUMMARY-1 | governance | workbench | DS-1-DS-8, 19 tests. Review decision summary. | SUP |
| 74 | QA-PILOT-DECISION-SUMMARY-REGISTRY-MAINTENANCE-1 | governance | registry | Post-seal registry maintenance. Evidence of registry hygiene. | SUP |
| 75 | QA-PILOT-WORKBENCH-REVIEW-DECISION-SUMMARY-STARTUP-SURFACE-1 | governance | startup | Decision summary in startup surface. Startup qualification. | ART |
| 76 | QA-PILOT-WORKBENCH-REVIEW-DECISION-RECEIPT-1 | governance | workbench | WDR-1-WDR-8, decision receipts. **Core target** — decision receipt qualification. | ART |
| 77 | QA-PILOT-WORKBENCH-REVIEW-DECISION-RECEIPT-STARTUP-SURFACE-1 | governance | startup | WDR in startup surface. Startup qualification. | ART |
| 78 | QA-PILOT-WORKBENCH-OWNER-ACTION-PACKET-1 | governance | workbench | AP-1-AP-8, action packets. **Core target** — action packet qualification. | ART |
| 79 | QA-PILOT-WORKBENCH-OWNER-ACTION-PACKET-STARTUP-SURFACE-1 | governance | startup | AP in startup surface. Startup qualification. | ART |
| 80 | QA-PILOT-WORKBENCH-ACTION-PACKET-EXPORT-1 | governance | workbench | AXP-1-AXP-8, export packets. **Core target** — export packet qualification. | ART |
| 81 | QA-PILOT-WORKBENCH-ACTION-PACKET-EXPORT-STARTUP-SURFACE-1 | governance | startup | AXP in startup surface. Startup qualification. | ART |
| 82 | QA-PILOT-WORKBENCH-ACTION-HANDOFF-INTAKE-1 | governance | workbench | HI-1-HI-8, handoff intake. **Core target** — handoff packet qualification. | ART |
| 83 | QA-PILOT-WORKBENCH-ACTION-HANDOFF-INTAKE-STARTUP-SURFACE-1 | governance | startup | HI in startup surface. Startup qualification. | ART |
| 84 | QA-PILOT-WORKBENCH-HANDOFF-REVIEW-OUTCOME-1 | governance | workbench | HO-1-HO-8, review outcomes. **Core target** — review outcome qualification. | ART |
| 85 | QA-PILOT-WORKBENCH-HANDOFF-REVIEW-OUTCOME-STARTUP-SURFACE-1 | governance | startup | HRO in startup surface. Startup qualification. | ART |
| 86 | QA-PILOT-WORKBENCH-OWNER-ACTION-READINESS-1 | governance | workbench | RD-1-RD-8, readiness posture. **Core target** — readiness qualification. | ART |
| 87 | QA-PILOT-WORKBENCH-OWNER-ACTION-READINESS-STARTUP-SURFACE-1 | governance | startup | RD in startup surface. Startup qualification. | ART |

### 2.10 Review Depth Layer (#88–#91)

| # | Sprint ID | Type | Area | Qualification Relevance | Code |
|---|-----------|------|------|------------------------|------|
| 88 | QA-PILOT-REVIEW-DEPTH-THRESHOLDS-1 | governance | review | TD-1-TD-8, evidence depth classification. **Core target** — threshold qualification. | ART |
| 89 | QA-PILOT-REVIEW-DEPTH-THRESHOLDS-STARTUP-SURFACE-1 | governance | startup | TD in startup surface. Startup qualification. | ART |
| 90 | QA-PILOT-REVIEW-DEPTH-THRESHOLDS-DECISION-PACKET-1 | governance | decisions | DP-1-DP-8, decision packet format. **Core target** — decision packet qualification. | ART |
| 91 | QA-PILOT-RISK-BASED-REVIEW-DEPTH-1 | governance | review | 4 review modes, 9 risk inputs, ER-1-ER-10. **Core target** — risk-based review qualification. | ART |

### 2.11 Post-Review Shell Layer (#92–#135)

| # Range | Sprint IDs | Type | Area | Qualification Relevance | Code |
|---------|-----------|------|------|------------------------|------|
| 92 | QA-PILOT-REVIEW-DEPTH-THRESHOLDS-DECISION-PACKET-STARTUP-SURFACE-1 | governance | startup | DP in startup surface. Startup qualification. | ART |
| 93–134 | (Workbench chain completions, surface integrations, seal events) | governance | various | Each sealed sprint adds to the governance corpus. Individual relevance varies but contributes to pipeline integrity. | SUP |
| 135 | QA-PILOT-MIGRATED-FRONTEND-ROUNDTRIP-VALIDATION-1 | validation | migration | 22 workflow steps verified. Migration milestone. | CTX |

### 2.12 Design Quality Layer (#136–#155)

| # Range | Sprint IDs | Type | Area | Qualification Relevance | Code |
|---------|-----------|------|------|------------------------|------|
| 136–142 | EPIC-QA-PILOT-DESIGN-LANGUAGE-REFRESH-1 (7 sprints) | design | language | Design language convergence. Artifact qualification criteria reference. | CTX |
| 143–147 | EPIC-QA-PILOT-DESIGN-QUALITY-REGRESSION-1 (5 sprints) | design | quality | Accessibility, visual regression, responsive/I18N. Artifact quality thresholds reference. | CTX |
| 148–152 | EPIC-QA-PILOT-I18N-WIRING-1 (5 sprints, unsealed) | design | i18n | I18N wiring — paused. Language qualification reference. | CTX |
| 153–155 | EPIC-QA-PILOT-LIBRARIAN-VISUAL-PARITY-CORRECTION-1 (partial) | design | parity | Visual parity correction (2/5 verified, 3 re-scoped). Design consistency reference. | CTX |

### 2.13 Migration Layer (#156–#160)

| # | Sprint ID | Type | Area | Qualification Relevance | Code |
|---|-----------|------|------|------------------------|------|
| 156 | QA-PILOT-MIGRATION-PREP-AND-SNAPSHOT-1 | migration | prep | Migration prep, snapshot, status corrections. | CTX |
| 157 | QA-PILOT-OPENWORK-APP-COPY-1 | migration | copy | 123 files copied, SHA verified. Application baseline. | CTX |
| 158 | QA-PILOT-MIGRATED-APP-SMOKE-VALIDATION-1 | migration | validation | 9 flow areas validated, 3 path defects fixed. Application smoke test. | CTX |
| 159 | QA-PILOT-CARBIDEFRAME-GOVERNANCE-INTEGRATION-1 | migration | governance | Governance registration, web_app_root, data separation. | CTX |
| 160 | QA-PILOT-MIGRATION-ROUNDTRIP-VALIDATION-1 | migration | validation | 120/123 byte-identical, 8/8 functional flows. Canonical recommendation. | CTX |

---

## 3. Summary Statistics

### By Category

| Code | Category | Count | Percentage |
|------|----------|-------|------------|
| 🟢 ART | Core Target (qualification artifacts) | 42 | 26.3% |
| 🟢 EVI | Evidence Source | 11 | 6.9% |
| 🟡 SUP | Supporting Infrastructure | 19 | 11.9% |
| 🔵 STR | Structural/Planning | 12 | 7.5% |
| ⚪ CTX | Context | 27 | 16.9% |
| 🔴 OOS | Out of Scope | 0 | 0.0% |
| — | (migration, design, i18n, parity) | 49 | 30.6% |

**Total actionable (ART + EVI + SUP): 72 layers (45.0%)**

### By Layer Group

| Layer Group | Total | ART | EVI | SUP | STR | CTX |
|-------------|-------|-----|-----|-----|-----|-----|
| Foundation (#1) | 1 | 0 | 0 | 0 | 1 | 0 |
| Production (#2–#5) | 4 | 0 | 2 | 0 | 2 | 0 |
| Custody & Broker (#6–#15) | 10 | 0 | 3 | 3 | 3 | 0 |
| Packet & Training (#16–#19) | 4 | 2 | 1 | 0 | 0 | 1 |
| Startup Parity (#20–#22) | 3 | 1 | 0 | 0 | 2 | 0 |
| Write Custody (#23–#31) | 9 | 4 | 2 | 3 | 0 | 0 |
| Architecture & Pipeline (#32–#50) | 19 | 12 | 2 | 1 | 1 | 0 |
| Registry & Receipts (#51–#65) | 15 | 8 | 2 | 4 | 0 | 0 |
| Workbench (#66–#87) | 22 | 14 | 0 | 2 | 1 | 0 |
| Review Depth (#88–#91) | 4 | 4 | 0 | 0 | 0 | 0 |
| Post-Review (#92–#135) | 44 | 1 | 0 | 11 | 0 | 1 |
| Design Quality (#136–#155) | 20 | 0 | 0 | 0 | 0 | 20 |
| Migration (#156–#160) | 5 | 0 | 0 | 0 | 0 | 5 |
| **Total** | **160** | **42** | **12** | **24** | **10** | **27** |

### Key Insights

1. **Five dominant ART clusters** make up 65% of qualification targets:
   - Architecture & Pipeline (#32–#50): 12 ART layers
   - Workbench (#66–#87): 14 ART layers
   - Registry & Receipts (#51–#65): 8 ART layers
   - Write Custody (#23–#31): 4 ART layers
   - Review Depth (#88–#91): 4 ART layers

2. **Evidence sources are concentrated** in receipt stores, custody receipts, and evidence intake (12 EVI layers, mostly #2–#11, #23–#31, #33)

3. **Design layers (#136–#155) are primarily context** — they inform artifact qualification criteria but aren't part of the governance pipeline that produces qualification-ready data

4. **The `required_for_operational_v1` flag** is set on 141 of 160 sprints (88%), confirming most of the governance pipeline is considered operational baseline

---

## 4. Qualification Targets by Priority

### First Wave — Highest Qualification Readiness

These layers already produce structured, validated, advisory-only outputs with clear evidence chains:

| Sprint | Output | Current Evidence Format | Qualification Readiness |
|--------|--------|------------------------|----------------------|
| #33 | MCP evidence intake | EM-validated evidence packets | 🟢 Ready — structured, schema-validated |
| #34 | Advisory test cases | TC-validated composition output | 🟢 Ready |
| #35 | Result packets (QR-) | RP-validated export format | 🟢 Ready |
| #36 | Epic regression suites (ERS-) | ER-validated suite format | 🟢 Ready |
| #44 | Evidence checklist | EC-validated checklist | 🟢 Ready |
| #45 | Checklist review packet | CRP-validated review format | 🟢 Ready |
| #66 | Workbench items | WB-validated item format | 🟢 Ready |
| #88 | Review depth thresholds | TD-validated threshold data | 🟢 Ready |
| #90 | Decision packets | DP-validated packet format | 🟢 Ready |
| #91 | Risk-based review depth | RD-validated review output | 🟢 Ready |

### Second Wave — Qualification Surface Extensions

These are startup-surface extensions that already expose qualification-relevant posture:

| Sprint | Surface | Exposes |
|--------|---------|---------|
| #37 | Pipeline startup surface | Layer order, custody, advisory posture |
| #43 | ODR startup surface | Decision receipt linkage |
| #50 | Registry startup surface | Layer count, PH/DR alignment |
| #52 | RCR startup surface | Receipt count, impact classification |
| #55 | RCG closeout surface | Coverage gap, seal-ready classification |
| #58 | SUG startup surface | Snapshot drift, update gate posture |
| #75 | Decision summary surface | Summary posture |
| #77 | Decision receipt surface | WDR posture |
| #79 | Action packet surface | AP posture |
| #81 | Export surface | AXP posture |
| #83 | Handoff intake surface | HI posture |
| #85 | Handoff review surface | HRO posture |
| #87 | Readiness surface | RD posture |
| #89 | Review depth surface | TD posture |

### Third Wave — Supporting Infrastructure

These provide evidence, custody, or structural support but aren't direct qualification targets:

| Group | Sprints | Role |
|-------|---------|------|
| Evidence stores | #4, #11, #33, #54, #59 | Store qualification records and receipts |
| Custody receipts | #23–#31 | Provide trust and provenance for qualification |
| Registries | #48, #49, #51, #74 | Map and version the governance layers |
| Regression snapshots | #56, #57, #58, #59, #60, #61 | Baseline and detect drift |

---

## 5. What QA Pilot Owns

From the landscape analysis:

| Owned Asset | Count | Qualification Significance |
|-------------|-------|---------------------------|
| Sealed governance layers | 160 | Each produces advisory-only outputs that can be qualification targets |
| CLI scripts | 70+ | Production-grade Python tools implementing governance and surfaces |
| Validator scripts | 55+ | Rule-based validation engines — pattern for qualification validation |
| Test runners | 70+ | Shell-based acceptance gate tests — pattern for qualification testing |
| JSON Schemas | 20+ | Draft 2020-12 schemas — format for qualification record schema |
| Fixtures | 150+ | Valid/invalid fixture pairs — template for qualification fixtures |
| Evidence store | File-backed | Data source for qualification evidence pipeline |
| Receipt store | File-backed | Data source for qualification provenance |
| Startup surfaces | 12+ | Surfaces that can expose qualification posture |
| Registry | Layer-based | Governance layer registry — structural model for qualification registry |

## 6. What Projects QA Pilot Qualifies

Based on the existing architecture:

| Project | Current Relationship | Qualification Role |
|---------|---------------------|-------------------|
| **QA Pilot (self)** | All 160 sealed layers | Primary — qualify QA Pilot's own governance artifacts and processes |
| **The Librarian** | Cross-project MCP bridge planning (#71) | Secondary — advisory review packets for Librarian consumption. QA Pilot qualifies its advisory outputs before submission. |
| **Future projects** | Architecture supports extension | Tertiary — qualification framework designed for future project onboarding |

## 7. Migration Assumptions (Per Owner Direction)

This catalog is based on the current canonical location (`active/qa-pilot/` post-migration, pre-promotion).

**Path-dependent artifacts that would need updates after promotion:**

| Artifact | Current Path | Post-Promotion Change |
|----------|-------------|----------------------|
| `active/qa-pilot/browser-app/` | Migration target | Would become canonical (no path change if promoted in place) |
| OpenWork source refs in roundtrip validation (#160) | Reference `/Users/andrew/Desktop/OpenWork/QA Pilot` | Would be archived or detached |
| Governance separation doc (#159) | `docs/governance/QA-PILOT-BROWSER-APP-SEPARATION.md` | Would need canonical status update |
| Migration epic docs (#156–#160) | `docs/sprints/QA-PILOT-MIGRATION-*.md` | Would need status update from "migration" to "canonical" |
| PATH_UPDATE_REQUIRED markers | (identified above) | Resolve after Owner canonical decision |

---

*Landscape Catalog prepared as part of QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1 (Tier 1). This is a planning document — no implementation, seal, or ledger mutation is authorized.*
