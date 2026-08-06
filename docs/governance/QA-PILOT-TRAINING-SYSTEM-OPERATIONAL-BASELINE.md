# QA Pilot — EPIC-QA-PILOT-TRAINING-SYSTEM-1 Operational Baseline

**Sprint:** QA-PILOT-TRAINING-SYSTEM-OPERATIONAL-BASELINE-1 (Sprint 11/11)
**Epic:** EPIC-QA-PILOT-TRAINING-SYSTEM-1
**Status:** complete_pending_owner_review

## Completed System

| Component | Sprint | Script | Status |
|-----------|--------|--------|--------|
| Knowledge Adapter | 3 | `qa_pilot_knowledge_adapter.py` | ✅ |
| Content Model | 4 | `validate-qa-pilot-training-content-model.py` | ✅ |
| Package Generator | 5 | `qa_pilot_training_package_generator.py` | ✅ |
| Validation Engine | 6 | `qa_pilot_training_validation_engine.py` | ✅ |
| Learning Paths | 7 | `qa_pilot_learning_paths.py` | ✅ |
| Simulation Expansion | 8 | `qa_pilot_training_simulation_expansion.py` | ✅ |
| Package Export | 9 | `qa_pilot_training_package_export.py` | ✅ |
| MCP Surface | 10 | `qa_pilot_training_mcp_surface.py` | ✅ |

## System Architecture

```
Librarian Canonical Knowledge
         ↓
Knowledge Adapter (read-only, Sprint 3)
         ↓
Content Model (schemas + validation, Sprint 4)
         ↓
Package Generator (produces training-packages, Sprint 5)
         ↓
Validation Engine (deterministic PASS/FAIL/WARN, Sprint 6)
         ↓
    ┌────┴────┐
    ↓         ↓
Learning    Simulation
Paths       Expansion
(Sprint 7)  (Sprint 8)
    ↓         ↓
    └────┬────┘
         ↓
Package Export + MCP Surface (Sprints 9-10)
         ↓
New Project Onboarding / Help Files
```

## Hard Boundaries (All Sprints)

| Boundary | Enforced |
|----------|----------|
| No Librarian canonical state mutation | ✅ All adapters read-only |
| No seal authority | ✅ No seal/approve/merge in any script |
| No automatic acceptance/rejection | ✅ Owner decision required for publish |
| No cross-project write path | ✅ All scripts QA Pilot-local |
| No MCP authority expansion | ✅ Sprint 10 is read-only query surface |
| Every artifact has source lineage | ✅ Hard invariant in generator + validator |
| Advisory-only posture | ✅ `advisory: true` in all artifacts |
| Training can fail validation | ✅ Deterministic FAIL outcomes |

## Operational Rules

1. **Knowledge sources**: Only Librarian canonical docs. No external or unverified sources.
2. **Generation pipeline**: Source → Adapter → Content Model → Generator → Validation → Package
3. **Validation is terminal**: Failed packages do not proceed to export
4. **Owner approval required**: Every published package requires explicit Owner decision
5. **No auto-repair**: Failed validation requires regeneration, not auto-fix
6. **Librarian remains canonical**: QA Pilot never writes to Librarian
7. **Simulator is optional**: Training system works without simulation layer

## Regression Suite

Run all component test suites to verify no regression:

```bash
for t in test-qa-pilot-knowledge-adapter.sh test-qa-pilot-training-content-model.sh test-qa-pilot-training-package-generator.sh; do
  bash "scripts/$t" || echo "REGRESSION: $t"
done
```

## Maintenance Rules

- Adding a new artifact type requires: schema update + validator rule + fixture + test
- Changing source format requires: adapter update + provenance hash recomputation
- No dependency on simulation layer for core training pipeline
- All data persisted under `data/training-packages/` (gitignored)
- All scripts under `scripts/` are advisory-only by declaration
