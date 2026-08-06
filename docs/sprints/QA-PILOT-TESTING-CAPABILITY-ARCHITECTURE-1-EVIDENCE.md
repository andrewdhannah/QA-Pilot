# QA-PILOT-TESTING-CAPABILITY-ARCHITECTURE-1 — Architecture Definition

**Produced by:** #178
**Date:** 2026-07-20
**Status:** Architecture document — defines contracts, boundaries, and roadmap
**Relation:** Feeds into EPIC-QA-PILOT-UNIVERSAL-TESTING-CAPABILITY-FOUNDATION-1

---

## Deliverable 1: Input Contract

### 1.1 Project Context

| Field | Source | Example |
|-------|--------|---------|
| Application identity | PROJECT-IDENTITY.md | `qa-pilot` |
| Repository structure | Filesystem scan | `browser-app/`, `src/`, `apps/` |
| Runtime configuration | content.js, db.js | Offline browser app, IndexedDB |
| Technology stack | File extensions, build.js | HTML/CSS/JS, vanilla, Node build |
| Deployment model | Desktop shell, QASimulator | `file://` safe, self-contained |

### 1.2 Librarian Context

| Field | Librarian Source | QA Pilot Consumption |
|-------|------------------|---------------------|
| Approved requirements | project_work_get | Sprint scope, acceptance gates |
| Sprint intent | sprint-ledger.json | Active work items, sealed history |
| Acceptance criteria | Work packets | Expected outcomes per item |
| Known risks | Evidence receipts | Risk-classified findings |
| Evidence history | Receipt store | Previous test results, drift data |

### 1.3 Application Knowledge (Extracted at Audit Time)

| Knowledge | Detection Method |
|-----------|-----------------|
| Routes/Pages | `find . -name "*.html"` |
| UI surfaces | Element tree scan |
| Modules | `apps/*` directory inventory |
| Data models | content.js, db.js schema |
| Dependencies | Script tag inventory |
| Translation keys | lang-en.js key extraction |

---

## Deliverable 2: Test Artifact Model

### 2.1 Base Schema

```
TestArtifact:
  identity:          UUID
  source_context:    { project_id, sprint_id, work_item_id }
  intent:            string (what is being tested)
  classification:    enum(security, uat, regression, performance, accessibility, language)
  execution_method:  enum(static_analysis, scripted, manual_guided, automated)
  expected_outcome:  { pass_criteria, fail_criteria }
  evidence_output:   { summary, detail_path, classification }
  authority_level:   enum(advisory, requires_owner_review)
```

### 2.2 Specializations

| Type | Additional Fields | Evidence Format |
|------|------------------|----------------|
| SecurityTest | target_surface, threat_vector, auth_requirement | Vulnerability checklist, boundary scan |
| UATScenario | workflow_steps, user_role, acceptance_gate | Scenario execution log |
| RegressionTest | changed_files, impacted_components, previous_results | Pass/fail matrix |
| PerformanceTest | metric, threshold, workload | Latency/throughput report |
| AccessibilityTest | wcag_criteria, element_selector | Violation report |
| LanguageTest | key_list, source_page, expected_language | Missing key report, parity matrix |

---

## Deliverable 3: Execution Model

```
┌─────────────────────────────────────────────────┐
│                  QA Pilot                        │
│                                                  │
│  Generate TestArtifact                           │
│      │                                           │
│      v                                           │
│  Validate (schema + governance checks)           │
│      │                                           │
│      v                                           │
│  Execute (static analysis / guided / automated)  │
│      │                                           │
│      v                                           │
│  Capture Evidence                                 │
│      │                                           │
│      v                                           │
│  Classify (PASS / OBSERVATION / FAIL / BLOCKED)  │
│      │                                           │
│      v                                           │
│  Output Evidence Package                         │
└─────────────────────────────────────────────────┘
         │
         v
    Librarian Evidence Chain
    (advisory attachment, not decision)
```

**Governance invariant:** QA Pilot generates evidence. Librarian makes decisions. Evidence packages are advisory attachments, not authority grants.

---

## Deliverable 4: Librarian Integration Boundary

| Direction | Librarian → QA Pilot | QA Pilot → Librarian |
|-----------|---------------------|---------------------|
| Data flow | Sprint intent, scope, constraints, risk context | Validation plans, execution results, evidence packages, observations |
| Authority | Decision authority | Validation authority only |
| Mutation | None by QA Pilot | None — read-only consumption |
| Evidence | Receives and classifies | Produces and attaches |
| Interface | project_work_get, sprint-ledger.json | Evidence receipt, file output |

**Rule:** QA Pilot never writes to Librarian state. All evidence is advisory attachment.

---

## Deliverable 5: Capability Roadmap

### Phase 1 (First Implementation Wave)

| Capability | Pilot | Rationale |
|------------|-------|-----------|
| Language | #177 QASimulator I18N | Existing pattern from #170–#173 |
| Regression | Sprint-ledger history | Existing evidence chains, changed-file detection |
| UAT | Requirements + acceptance criteria | Work packet inputs already structured |

### Phase 2

| Capability | Dependency |
|------------|------------|
| Accessibility | UI surface inventory (established in #172/#175) |

### Phase 3

| Capability | Dependency |
|------------|------------|
| Performance | Workload definitions, runtime profiling |

### Phase 4

| Capability | Dependency |
|------------|------------|
| Security | Stronger boundary definition (credentials, tools, reporting) |

---

## Acceptance Gates

| Gate | Result |
|------|--------|
| CA-1 | PASS — Input contract defined with 3 sources |
| CA-2 | PASS — Test artifact model defined (base + 6 specializations) |
| CA-3 | PASS — Execution model defined (Generate → Validate → Execute → Capture → Classify → Output) |
| CA-4 | PASS — Librarian integration boundary defined (bidirectional, non-mutating) |
| CA-5 | PASS — Capability roadmap produced (4 phases) |
| CA-6 | PASS — No implementation changes made |
| CA-7 | PASS — Evidence produced (this document) |

**7 PASS, 0 FAIL**

---

**Classification:** Advisory architecture definition — does not authorize implementation.
