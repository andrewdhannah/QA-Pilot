# WP-LVC-001 — Evidence Record

**Work Packet:** WP-LVC-001 — Canonical Vocabulary Definition + Governance State Schema
**Sprint:** LVC-001
**Date:** 2026-08-17
**Status:** COMPLETE

---

## Deliverables Produced

| Deliverable | Path | Status |
|-------------|------|--------|
| Canonical vocabulary document | `contracts/lifecycle-vocabulary.md` | ✅ Complete |
| Machine-checkable schema | `contracts/lifecycle-vocabulary.schema.json` | ✅ Complete |
| Governance state schema (instance-independent) | `contracts/governance-state-schema.md` | ✅ Complete |

## Acceptance Gate Results

| Gate | Question | Result | Evidence |
|------|----------|--------|----------|
| LVC-001-A | Canonical vocabulary exists | ✅ PASS | `contracts/lifecycle-vocabulary.md` — 5 dimensions, legal enums, transition rules, orthogonality invariant |
| LVC-001-B | Each dimension has one authoritative definition | ✅ PASS | Authority sources declared per dimension in `contracts/lifecycle-vocabulary.md` §Canonical Ownership |
| LVC-001-P | Canonical vocabulary is instance-independent and reusable across governed system instances | ✅ PASS | `contracts/governance-state-schema.md` defines instance boundary rules, initialization contract, prohibitions on state copying |

## Dimension Authority Sources (verified)

| Dimension | Authority Source | Verified |
|-----------|-----------------|----------|
| entity_type | Entity classification authority | ✅ |
| lifecycle_state | Canonical lifecycle model (not registry vocabulary) | ✅ |
| qualification_state | Qualification engine | ✅ |
| health_state | Evidence pipeline projection | ✅ |
| execution_policy | Governance policy / Owner decision | ✅ |

## Key Invariants Established

1. **Orthogonality:** No dimension derives authority from another
2. **Instance independence:** Schema reusable, state instance-specific
3. **No state copying:** New instances initialize independently
4. **Legacy preservation:** Legacy fields retained as provenance, not deleted
5. **Conflation detection:** Findings only, no auto-repair

## Migration Boundary (documented)

Legacy fields retained in schema:
- `current_phase` → lifecycle_state (projection, not authority)
- `current_phase_deprecated` → lifecycle_state (projection, not authority)
- `lifecycle_stage` → no direct mapping (retained as provenance)
- `lifecycle_label` → no direct mapping (retained as provenance)

## Files Changed

- `contracts/lifecycle-vocabulary.md` — created
- `contracts/lifecycle-vocabulary.schema.json` — created
- `contracts/governance-state-schema.md` — created
