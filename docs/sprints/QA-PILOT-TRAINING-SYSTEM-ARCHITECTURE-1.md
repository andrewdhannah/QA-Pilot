# QA-PILOT-TRAINING-SYSTEM-ARCHITECTURE-1 — Sprint Document

**Sprint ID:** QA-PILOT-TRAINING-SYSTEM-ARCHITECTURE-1
**Epic:** EPIC-QA-PILOT-TRAINING-SYSTEM-1 (Sprint 2/11)
**Type:** Architecture / planning
**Lane:** training_system_epic
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Status:** active
**Authorization:** Owner explicit authorization 2026-07-08

## Purpose

Define the successor training system architecture before any implementation begins. This sprint produces the architectural blueprint that all subsequent sprints in the epic build upon.

## Inputs

- Reconciliation report: `docs/planning/QA-PILOT-TRAINING-SYSTEM-RECONCILIATION-PLAN-1.md`
- Epic packet: `docs/governance/EPIC-QA-PILOT-TRAINING-SYSTEM-1.md`
- V2 course-pack schema: `qa-pilot-v2/docs/COURSE-PROGRAM-SCHEMA.md`
- Current QA Pilot schemas in `docs/schemas/`
- Current QA Pilot governance docs in `docs/governance/`
- Existing training sim: `docs/governance/QA-PILOT-TRAINING-SIM.md`

## Deliverables

1. **System architecture document** (`docs/planning/QA-PILOT-TRAINING-SYSTEM-ARCHITECTURE-1.md`)

### Sections

#### A. Component Boundaries
- Knowledge adapter component
- Training generator component
- Validation engine component
- Learning path component
- Simulation expansion component
- Package export component
- MCP surface component
- Data flow between components

#### B. Librarian Interaction Model
- Read-only access patterns
- Source document references
- Schema/metadata retrieval
- Provenance recording
- What QA Pilot reads vs. what it generates

#### C. QA Pilot Training Layer Responsibilities
- What the training layer owns (transformation, validation, packaging)
- What it does not own (canonical truth, publication authority, simulator)
- Authority boundary between knowledge and derived artifacts

#### D. JSON Course-Pack Architecture
- Adapt V2's course-pack-v1 schema for governed context
- Required extension fields: source references, intended audience, validation status, ownership state, authority posture
- Schema versioning strategy

#### E. Artifact Lifecycle
```
Source Knowledge
    ↓
Adapter retrieves
    ↓
Content Model transforms
    ↓
Generator produces package
    ↓
Validation Engine checks
    ↓
Learning Path assembles
    ↓
Package Export delivers
    ↓
Owner reviews
    ↓
Adoption/Publication
```

#### F. Provenance Requirements
- Every artifact must trace back to specific Librarian sources
- Provenance schema design
- Hash/integrity verification
- Chain of custody for training artifacts

#### G. Validation Flow
- What checks exist at each stage
- Deterministic pass/fail criteria
- Authority violation detection
- Source coverage verification
- Stale reference detection

#### H. Simulator Integration Boundary
- Relationship between training packages and the existing local training sim
- What the sim consumes vs. what it simulates
- Sim as optional downstream consumer, not upstream dependency

## Constraints

- Librarian remains canonical knowledge authority
- QA Pilot produces derived training artifacts only
- No autonomous publishing
- No authority expansion
- No implementation or migration during architecture sprint
- Every training artifact must identify its Librarian source lineage

## Acceptance Criteria

1. Component boundaries clearly defined for all 7 training system components
2. Librarian interaction model documented with read-only access patterns
3. QA Pilot training layer responsibilities explicitly scoped
4. JSON course-pack architecture adapted with governance extension fields
5. Artifact lifecycle documented end-to-end
6. Provenance requirements specified (every artifact must trace to Librarian sources)
7. Validation flow defined with deterministic pass/fail criteria
8. Simulator integration boundary documented
