# EPIC-QA-PILOT-TRAINING-SYSTEM-1 — Training System Epic

**Status:** active
**Owner:** Andrew Hannah
**Authorization:** Owner explicit authorization 2026-07-08
**Epic ID:** EPIC-QA-PILOT-TRAINING-SYSTEM-1

## Purpose

Create a governed training system where Librarian canonical knowledge flows through QA Pilot's training layer to produce validated training artifacts for new project onboarding and help packages.

## Authority Model

```
Librarian canonical knowledge
        ↓
QA Pilot training layer (advisory transforms)
        ↓
Validated training artifacts
        ↓
Owner approves adoption/publication
```

- Librarian owns canonical truth
- QA Pilot transforms and validates
- Generated training artifacts are derived outputs
- Owner approves adoption/publication

## Phases and Sprints

### Phase 1 — Reconciliation & Architecture (Sprints 1–2)

| # | Sprint | Type | Purpose |
|---|--------|------|---------|
| 1 | QA-PILOT-TRAINING-SYSTEM-RECONCILIATION-PLAN-1 | Planning | Inventory all prior QA Pilot generations, classify capabilities |
| 2 | QA-PILOT-TRAINING-SYSTEM-ARCHITECTURE-1 | Architecture | Define successor architecture, component boundaries |

### Phase 2 — Knowledge Connection (Sprints 3–4)

| # | Sprint | Type | Purpose |
|---|--------|------|---------|
| 3 | QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER-1 | Implementation | Create controlled bridge from Librarian knowledge to QA Pilot training |
| 4 | QA-PILOT-TRAINING-CONTENT-MODEL-1 | Implementation | Define training artifact structures (schemas, examples, validators) |

### Phase 3 — Training Generation (Sprints 5–6)

| # | Sprint | Type | Purpose |
|---|--------|------|---------|
| 5 | QA-PILOT-TRAINING-PACKAGE-GENERATOR-1 | Implementation | Generate training packages from approved source material |
| 6 | QA-PILOT-TRAINING-VALIDATION-ENGINE-1 | Implementation | Validate generated training deterministically |

### Phase 4 — Learning Experience (Sprints 7–8)

| # | Sprint | Type | Purpose |
|---|--------|------|---------|
| 7 | QA-PILOT-LEARNING-PATHS-1 | Implementation | Create structured learning journeys |
| 8 | QA-PILOT-TRAINING-SIMULATION-EXPANSION-1 | Implementation | Expand local training sim with scenario libraries |

### Phase 5 — Project Bootstrap (Sprints 9–10)

| # | Sprint | Type | Purpose |
|---|--------|------|---------|
| 9 | QA-PILOT-PROJECT-TRAINING-PACKAGE-EXPORT-1 | Implementation | Create training packages for new projects |
| 10 | QA-PILOT-TRAINING-SYSTEM-MCP-SURFACE-1 | Implementation | Optional bounded MCP access for training package requests |

### Phase 6 — Operational Baseline (Sprint 11)

| # | Sprint | Type | Purpose |
|---|--------|------|---------|
| 11 | QA-PILOT-TRAINING-SYSTEM-OPERATIONAL-BASELINE-1 | Governance | Lock completed system with ops docs, regression suite, maintenance rules |

## Hard Boundaries (All Sprints)

- No Librarian canonical state mutation
- No seal authority
- No automatic acceptance/rejection
- No cross-project write path
- No MCP authority expansion
- Every generated artifact must have source lineage to Librarian knowledge
- Owner remains the only decision authority

## Epic Completion Criteria

1. All 11 sprints sealed by Owner
2. Training system produces validated training artifacts from Librarian knowledge
3. Every artifact answers "What Librarian sources created this?"
4. Training can fail validation deterministically
5. Operational documentation, regression suite, and maintenance rules exist
6. No authority boundary weakened
