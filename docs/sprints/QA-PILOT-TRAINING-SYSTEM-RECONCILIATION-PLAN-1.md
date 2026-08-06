# QA-PILOT-TRAINING-SYSTEM-RECONCILIATION-PLAN-1 — Sprint Document

**Sprint ID:** QA-PILOT-TRAINING-SYSTEM-RECONCILIATION-PLAN-1
**Epic:** EPIC-QA-PILOT-TRAINING-SYSTEM-1 (Sprint 1/11)
**Type:** Planning / reconciliation
**Lane:** training_system_epic
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Status:** active
**Authorization:** Owner explicit authorization 2026-07-08

## Purpose

Inventory all prior QA Pilot generations and classify every historical capability before defining any new training system features. This sprint produces the knowledge foundation that every subsequent sprint in the epic builds upon.

## Input Sources

| Source | Location | Status |
|--------|----------|--------|
| Current governed QA Pilot | `Desktop/CarbideFrame/active/qa-pilot` | ✅ Active |
| QA-Pilot (original) | `github.com/andrewdhannah/QA-Pilot` | To inventory |
| QA-PilotV1_5 | `github.com/andrewdhannah/QA-PilotV1_5` | To inventory |
| QA-PilotV2 | `github.com/andrewdhannah/QA-PilotV2` | To inventory |
| qa-pilot-v2 | `github.com/andrewdhannah/qa-pilot-v2` | To inventory |
| Prior desktop artifacts | `Desktop/openwork/` | To inventory |
| Historical CarbideFrame | `Desktop/CarbideFrame/` | To inventory |

## Deliverables

1. **Capability comparison matrix** — capabilities across all generations side-by-side
2. **Feature lineage map** — which features originated where and how they evolved
3. **Retained/deprecated feature list** — explicit classification for every capability
4. **Architecture recommendation** — recommended architecture for the successor training system

## Review Areas

- Onboarding flows
- Simulator/training engine
- Learning paths
- Help generation
- Content storage
- User progress concepts
- Validation mechanisms

## Classification Categories

Every capability identified across all generations must be classified as one of:

| Category | Meaning |
|----------|---------|
| **keep** | Capability is sound and should be preserved in the successor |
| **redesign** | Capability needs rework before inclusion |
| **retire** | Capability is obsolete and should not continue |
| **defer** | Capability is valid but out of scope for this epic |

## Hard Boundaries

- No implementation work
- No migration
- No repository merge
- No Librarian mutation
- Read-only inventory and classification only

## Acceptance Criteria

1. All major historical capabilities classified (keep/redesign/retire/defer)
2. Capability comparison matrix covers all 5 generations
3. Feature lineage map shows evolution across generations
4. Architecture recommendation documents recommended successor approach
5. No implementation, migration, or merge performed
6. All sources inventoried (GitHub repos, Desktop artifacts, CarbideFrame history)

## Completion Evidence

**Status:** complete_pending_owner_review

### Sources Inventoried (5 generations)
| # | Generation | GitHub | Local Path | Inventoried |
|---|-----------|--------|-----------|-------------|
| 1 | QA-Pilot (V1) | `andrewdhannah/QA-Pilot` | `Desktop/openwork/QA Pilot/` | ✅ |
| 2 | QA-PilotV1_5 | `andrewdhannah/QA-PilotV1_5` | `Desktop/OW Old Folder/QA-PilotV1_5/` | ✅ |
| 3 | QA-PilotV2 | `andrewdhannah/qa-pilot-v2` | `Desktop/openwork/QA-PilotV2/`, `Desktop/CarbideFrame/qa-pilot/` | ✅ |
| 4 | Current governed | — | `Desktop/CarbideFrame/active/qa-pilot/` | ✅ |
| 5 | Cross-project bridge | — | `active/librarian` (packet export) | ✅ |

### Deliverables
| Deliverable | Location | Status |
|------------|----------|--------|
| Capability comparison matrix | `docs/planning/QA-PILOT-TRAINING-SYSTEM-RECONCILIATION-PLAN-1.md` §3 | ✅ 25 capabilities mapped |
| Feature lineage map | `docs/planning/QA-PILOT-TRAINING-SYSTEM-RECONCILIATION-PLAN-1.md` §2 | ✅ 3 lineages traced |
| Retained/deprecated list | `docs/planning/QA-PILOT-TRAINING-SYSTEM-RECONCILIATION-PLAN-1.md` §4 | ✅ 9 keep, 4 redesign, 3 retire, 1 defer |
| Architecture recommendation | `docs/planning/QA-PILOT-TRAINING-SYSTEM-RECONCILIATION-PLAN-1.md` §5 | ✅ Hybrid: V2 content format + governed validation |
| Epic packet | `docs/governance/EPIC-QA-PILOT-TRAINING-SYSTEM-1.md` | ✅ All 11 sprints, 6 phases |

### Boundaries Preserved
- ❌ No implementation work performed
- ❌ No migration performed
- ❌ No repository merge performed
- ❌ No Librarian mutation performed
- ✅ Read-only inventory and classification only
