# QA-PILOT-TRAINING-SYSTEM-ARCHITECTURE-1 — Training System Architecture

**Generated:** 2026-07-08
**Sprint:** QA-PILOT-TRAINING-SYSTEM-ARCHITECTURE-1 (Sprint 2/11)
**Epic:** EPIC-QA-PILOT-TRAINING-SYSTEM-1
**Status:** complete_pending_owner_review
**Based on:** QA-PILOT-TRAINING-SYSTEM-RECONCILIATION-PLAN-1 (#93)

---

## A. Component Boundaries

### A.1 Component Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LIBRARIAN (Canonical)                          │
│  docs/  schemas/  governance/  rules/  receipts/  project-state/      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ read-only (adapter queries)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ┌──────────────────────┐     QA PILOT TRAINING SYSTEM                 │
│  │  Knowledge Adapter   │ ← Sprint 3 — reads Librarian canonical      │
│  │  (read-only)         │    sources, returns structured references    │
│  └──────────┬───────────┘                                              │
│             │ provenance + content                                     │
│             ▼                                                          │
│  ┌──────────────────────┐                                              │
│  │  Content Model       │ ← Sprint 4 — schemas for all artifact types │
│  │  (schemas + validate)│    onbording/operator/dev/troubleshoot/arch  │
│  └──────────┬───────────┘    workflow tutorial/validation exercise     │
│             │ validated schemas                                        │
│             ▼                                                          │
│  ┌──────────────────────┐                                              │
│  │  Package Generator   │ ← Sprint 5 — produces training-package/     │
│  │  (transforms)        │    overview.md + lessons/ + examples/ +      │
│  └──────────┬───────────┘    exercises/ + provenance.json             │
│             │ generated packages                                       │
│             ▼                                                          │
│  ┌──────────────────────┐                                              │
│  │  Validation Engine   │ ← Sprint 6 — deterministic pass/fail        │
│  │  (deterministic)     │    source coverage, stale refs, violations   │
│  └──────────┬───────────┘                                              │
│             │ validated packages                                       │
│             ▼                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐                    │
│  │  Learning Paths      │  │  Simulation Expansion │ ← Sprint 7–8     │
│  │  (structured journeys)│  │  (scenario libraries) │                   │
│  └──────────┬───────────┘  └──────────┬───────────┘                    │
│             │                         │                                │
│             ▼                         ▼                                │
│  ┌──────────────────────────────────────────────────────┐              │
│  │  Package Export (Sprint 9) + MCP Surface (Sprint 10) │              │
│  └──────────────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
                                 │ Owner reviews
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     NEW PROJECT ONBOARDING                             │
│  training-package/ → project team consumes advisory training materials │
└─────────────────────────────────────────────────────────────────────────┘
```

### A.2 Component Responsibilities

| Component | Owns | Does Not Own |
|-----------|------|-------------|
| **Knowledge Adapter** | Reading Librarian sources, recording provenance, structuring source references | Librarian write access, source transformation, content generation |
| **Content Model** | Artifact schemas, type definitions, example fixtures, structural validators | Content generation, source retrieval, publication |
| **Package Generator** | Transforming source material into training packages, assembling structure, attaching provenance | Content validation beyond structure, publication, authority decisions |
| **Validation Engine** | Deterministic pass/fail checks, source coverage analysis, stale ref detection, authority violation detection | Content generation, package assembly, repair of failed packages |
| **Learning Paths** | Journey definitions, prerequisite chains, sequencing, progress models | Content generation, package creation, validation |
| **Simulation Expansion** | Scenario libraries, exercise definitions, evaluation models, completion evidence | Simulator runtime, package generation, authority decisions |
| **Package Export** | Package assembly for new projects, delivery format, Owner review packaging | Authoritative publication, auto-deployment, cross-project write |
| **MCP Surface** | Bounded read-only MCP tool for requesting packages, querying status, retrieving artifacts | Librarian mutation, content approval, autonomous publishing |

### A.3 Data Flow Rules

1. Data flows strictly **downstream**: Knowledge Adapter → Content Model → Generator → Validation
2. No component may skip a layer (e.g., Generator must not bypass Content Model to read Librarian directly)
3. Validation Engine is **terminal before learning paths/simulation** — any package that fails validation is not eligible for learning paths
4. Learning Paths and Simulation Expansion are **parallel** — they consume validated packages independently
5. Package Export and MCP Surface are **output-only** — they package and deliver but do not generate content

---

## B. Librarian Interaction Model

### B.1 Access Patterns

The Knowledge Adapter may access Librarian sources through these read-only patterns:

| Pattern | What It Accesses | Authority |
|---------|-----------------|-----------|
| **Document reference** | Specific canonical docs by path (e.g., `docs/governance/*.md`) | Read-only, advisory |
| **Schema reference** | JSON schemas from `docs/schemas/` | Read-only, advisory |
| **Sprint evidence** | Sealed sprint docs, evidence notes from ledger | Read-only, advisory |
| **Receipt reference** | Decision receipts from `receipts/decision-resolutions/` | Read-only, advisory |
| **File inventory** | Directory listing of known source paths | Read-only, advisory |

### B.2 What QA Pilot Cannot Do to Librarian

- No write access to any Librarian file path
- No MCP tool invocation that modifies Librarian state
- No creation of receipts, ledger entries, or handoff entries in Librarian
- No mutation of Librarian sprint-index, sprint-ledger, or startup surfaces
- No assumption of Librarian file paths as stable without Owner confirmation

### B.3 Provenance Recording

Every training artifact must include a `provenance` block that records:

```json
{
  "provenance": {
    "generated_at": "2026-07-08T21:00:00Z",
    "librarian_sources": [
      {"path": "docs/governance/QA-PILOT-PROJECT-GOVERNANCE.md", "revision": "<sha-or-ref>"},
      {"path": "docs/schemas/qa-pilot-evidence-checklist.schema.json", "revision": "<sha-or-ref>"}
    ],
    "generator": "qa-pilot-training-generator",
    "generator_version": "1.0.0",
    "source_hash": "<sha256-of-source-inputs>"
  }
}
```

---

## C. QA Pilot Training Layer Responsibilities

### C.1 What the Training Layer Owns

- **Transformation**: Converting canonical knowledge into training-optimized formats
- **Assembly**: Structuring content into lessons, modules, and learning journeys
- **Validation**: Proving content correctness, completeness, and source fidelity
- **Packaging**: Organizing validated content into deliverable training packages
- **Provenance**: Recording every source reference that contributed to each artifact
- **Delivery surface**: Making completed packages available for Owner review → adoption

### C.2 What the Training Layer Does Not Own

- **Canonical truth**: Librarian remains the authoritative source of all governance, schema, and operational knowledge
- **Publication authority**: Only the Owner may approve adoption of training materials
- **Simulator runtime**: The existing OS simulator is a separate product; the training layer provides content that the sim may optionally consume
- **Agent training**: Agent behavior is governed by Librarian startup protocols and rules docs; training materials teach humans about governed work, not how agents behave

### C.3 Authority Boundary

```
Librarian: writes canonical truth
QA Pilot:  reads canonical truth (adapter)
           transforms into training formats
           validates training artifacts
           packages for delivery
Owner:     reviews packages
           approves adoption
           publishes to new projects
```

---

## D. JSON Course-Pack Architecture

### D.1 Base Schema (adapted from V2 course-pack-v1)

The training system adopts V2's course-pack-v1 JSON schema as the content foundation, extended with governance fields:

```json
{
  "course_pack": {
    "schema_version": "training-pack-v1",
    "id": "training-pack-<uuid>",
    "title": "string",
    "description": "string",
    "intended_audience": "onboarding | operator | developer | architect",
    "prerequisites": ["training-pack-id", "..."],
    
    "governance": {
      "authority_posture": "advisory",
      "owner_decision_required_for_publish": true,
      "validation_status": "draft | validated | failed | owner_approved",
      "source_coverage_pct": 85,
      "last_validated_at": "ISO8601"
    },
    
    "provenance": {
      "librarian_sources": [],
      "generator": "string",
      "generator_version": "string",
      "source_hash": "sha256"
    },
    
    "modules": [
      {
        "id": "module-1",
        "title": "string",
        "chapters": [
          {
            "id": "chapter-1",
            "title": "string",
            "content_type": "text | exercise | quiz | reference",
            "body": "markdown string",
            "sources": ["path/to/librarian/doc.md"]
          }
        ]
      }
    ]
  }
}
```

### D.2 Extension Fields (Added to V2 Base)

| Field | Purpose | Required |
|-------|---------|----------|
| `governance.authority_posture` | Always "advisory" — training artifacts are never authoritative | Yes |
| `governance.owner_decision_required_for_publish` | Must be true — no auto-publication | Yes |
| `governance.validation_status` | Tracks lifecycle: draft → validated → failed → owner_approved | Yes |
| `governance.source_coverage_pct` | What % of content traces to Librarian sources | Yes |
| `provenance.librarian_sources` | Array of source document paths/revisions | Yes |
| `chapters[].sources` | Per-section source references | Yes (minimum 1) |
| `intended_audience` | Who this is for — drives classification | Yes |

### D.3 Artifact Types

| Type | Extension | Description |
|------|-----------|-------------|
| `onboarding_guide` | — | New project team introduction to governed work |
| `operator_guide` | — | Day-to-day operational workflows |
| `developer_guide` | — | How to extend governed projects |
| `troubleshooting_guide` | — | Common failure modes and recovery |
| `architecture_explanation` | — | System architecture overview |
| `workflow_tutorial` | — | Step-by-step guided task walkthrough |
| `validation_exercise` | — | Self-check/quiz to verify understanding |

---

## E. Artifact Lifecycle

```
┌──────────────────────────────────────────────────────────────────────┐
│                        ARTIFACT LIFECYCLE                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐                                                        │
│  │  SOURCE  │  Librarian canonical documents identified by Adapter   │
│  └────┬─────┘                                                        │
│       ▼                                                              │
│  ┌──────────┐                                                        │
│  │   DRAFT  │  Generator produces training-pack from sources         │
│  └────┬─────┘                                                        │
│       ▼                                                              │
│  ┌──────────────┐                                                    │
│  │  VALIDATED   │  Validation Engine passes deterministic checks     │
│  │  or FAILED   │  → proceeds to learning paths or rejected          │
│  └────┬─────────┘                                                    │
│       ▼                                                              │
│  ┌──────────────┐                                                    │
│  │  ASSEMBLED   │  Learning Path or Simulation consumes package      │
│  └────┬─────────┘                                                    │
│       ▼                                                              │
│  ┌──────────────┐                                                    │
│  │  REVIEWABLE  │  Package Export delivers for Owner review          │
│  └────┬─────────┘                                                    │
│       ▼                                                              │
│  ┌──────────────────┐                                                │
│  │  OWNER APPROVED  │  Owner reviews and approves adoption           │
│  └────────┬─────────┘                                                │
│           ▼                                                          │
│  ┌────────────────┐                                                  │
│  │  PUBLISHED     │  New projects receive training package           │
│  └────────────────┘                                                  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### State Machine

| State | Allowed Transitions | Performed By | Evidence |
|-------|-------------------|-------------|----------|
| `source` | → `draft` | Knowledge Adapter | Source reference list |
| `draft` | → `validated`, → `failed` | Validation Engine | Validation receipt |
| `validated` | → `assembled` | Learning Path | Package assembly record |
| `assembled` | → `reviewable` | Package Export | Export receipt |
| `reviewable` | → `owner_approved`, → `failed` | Owner | Owner decision receipt |
| `owner_approved` | → `published` | Package Export | Publication receipt |
| `published` | (terminal) | — | — |
| `failed` | → `draft` (rework) | Generator | Updated source hash |

---

## F. Provenance Requirements

### F.1 Hard Rules

1. **Every training artifact must have at least one Librarian source reference.** Zero-source artifacts are rejected by the Validation Engine.
2. **Every chapter in a training pack must reference at least one source document.** Chapters without source lineage fail validation.
3. **Source references must include a path and a revision identifier.** Bare filenames without revision are insufficient.
4. **Provenance hash must cover all source inputs.** Hash is computed over the concatenation of all referenced source revisions.
5. **Training artifacts may not introduce claims unsupported by source references.** Violations are detected by the Validation Engine's authority check.

### F.2 Provenance Block (Minimum)

```json
{
  "provenance": {
    "librarian_sources": [
      {"path": "docs/governance/QA-PILOT-PROJECT-GOVERNANCE.md", "revision": "abc123def"}
    ],
    "generator": "qa-pilot-training-generator",
    "source_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  }
}
```

### F.3 Integrity Chain

```
Source documents (Librarian canonical)
    → hash each source individually
    → combine into source_hash
    → embed source_hash in training pack provenance
    → Validation Engine recomputes source_hash
    → pass if computed hash matches embedded hash
    → fail if sources changed since generation
```

---

## G. Validation Flow

### G.1 Validation Stages

| Stage | What It Checks | Failure Outcome |
|-------|---------------|-----------------|
| **Schema validity** | Training pack conforms to training-pack-v1 schema | Pack rejected — malformed |
| **Source coverage** | Every chapter has ≥1 library source reference | Pack rejected — missing provenance |
| **Provenance integrity** | `source_hash` matches recomputed hash of referenced sources | Pack rejected — sources stale |
| **Authority posture** | `authority_posture` is `advisory`, `owner_decision_required_for_publish` is `true` | Pack rejected — authority violation |
| **No mutation claims** | Pack contains no Librarian mutation paths, seal claims, or approval language | Pack rejected — authority leak |
| **Source reachability** | Referenced source paths exist in Librarian (or are documented as acceptable gaps) | Warning — stale reference flagged |
| **Content structure** | Module/chapter ordering is valid, no orphaned sections | Pack flagged — structural warning |

### G.2 Deterministic Pass/Fail

The validation engine operates on three outcome levels:

| Level | Meaning | Action |
|-------|---------|--------|
| **PASS** | All checks green | Pack eligible for learning paths |
| **FAIL** | Any hard check fails (authority, provenance, schema) | Pack rejected — must regenerate |
| **WARN** | Soft checks flag issues (stale sources, structural) | Pack proceeds but flagged for Owner review |

### G.3 Authority Violation Patterns (Blocking)

The following patterns cause immediate FAIL regardless of other passing checks:

- `authority_posture` is not `advisory`
- `owner_decision_required_for_publish` is not `true`
- Pack contains `seal_action`, `approve_action`, `merge_action`, or similar mutation keys
- Pack references `active/librarian/Sources/`, `librarian DB write`, or `librarian MCP register`
- Pack claims to be `authoritative`, `canonical`, or `binding` without Owner qualification

---

## H. Simulator Integration Boundary

### H.1 Relationship

The existing local training simulation (`QA-PILOT-LOCAL-TRAINING-SIM-1`, ledger #19) is an **independent, optional downstream consumer** of training packages:

```
Training packages (generated, validated)
         │
         ├─→ Learning Paths → exported to projects
         │
         └─→ Simulation Expansion → scenario libraries for sim runtime
```

### H.2 What the Sim Consumes

- Validated training packages (source-grounded, advisory-only)
- Scenario definitions derived from training content
- Exercise/quiz content for simulation evaluation

### H.3 What the Sim Does Not Consume

- Unvalidated packages (must pass Validation Engine first)
- Raw Librarian source documents (always goes through the training pipeline)
- Canonical governance artifacts (those are for the agent/human, not the sim)

### H.4 Integration Points

| Point | Description | Sprint |
|-------|-------------|--------|
| Scenario library | Training content → structured scenarios for sim runtime | Sprint 8 |
| Exercise evaluation | Exercise definitions → sim can validate completion | Sprint 8 |
| Completion evidence | Sim results → evidence of training completion | Sprint 8 |
| Training package ref | Sim references the training pack that sourced its scenarios | Sprint 8 |

### H.5 Boundary Rules

1. The simulator is **not required** for the training system to function
2. Training packages are complete without a simulator — the sim is an enrichment layer
3. The sim may not modify training packages — only consume them read-only
4. The sim may not bypass validation — only validated packages are eligible for sim scenarios

---

## Architecture Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Content foundation | V2 JSON course-pack schema + governance extensions | Proven format, AI-friendly, separates content from authority |
| Authority model | Advisory-only, Owner-approves-publish | Matches existing QA Pilot governance posture |
| Source lineage | Hard invariant — every chapter must cite sources | Prevents unsupported claims, enables validation |
| Component isolation | Strict 7-component pipeline, no skipping layers | Prevents authority leaks, ensures validation at each stage |
| Simulator role | Optional downstream consumer, not upstream dependency | Decouples training content from simulation runtime |
| Validation | Deterministic PASS/FAIL/WARN with blocking authority patterns | Matches existing QA Pilot validation philosophy |
| MCP surface | Bounded, read-only, advisory | No authority expansion — consistent with bridge pattern |

---

## Artifacts

| Artifact | Path |
|----------|------|
| This architecture document | `docs/planning/QA-PILOT-TRAINING-SYSTEM-ARCHITECTURE-1.md` |
| Epic packet | `docs/governance/EPIC-QA-PILOT-TRAINING-SYSTEM-1.md` |
| Sprint doc | `docs/sprints/QA-PILOT-TRAINING-SYSTEM-ARCHITECTURE-1.md` |
