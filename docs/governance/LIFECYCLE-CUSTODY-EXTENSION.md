# LIFECYCLE-CUSTODY-EXTENSION.md — Lifecycle Transition Custody Extension

**Status:** 🔍 Pending (not sealed)
**Authority:** Extends custody enforcement across QA Pilot lifecycle transitions. Consumes PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT-1 (#23) and LIVE-CUSTODY-INTEGRATION-1 (#24) without changing either contract.
**Sprint:** LIFECYCLE-CUSTODY-EXTENSION-1

---

## 1. Purpose

Extend custody enforcement across QA Pilot lifecycle transitions so phase/state movement is governed by the same custody posture established in #23 and live-integrated in #24.

**Core invariant:**
> Every lifecycle transition must pass through custody checks before state mutation.

## 2. Lifecycle Custody Rules

| Rule | Description |
|------|-------------|
| LC-1 | Default decision is block unless lifecycle authority is proven |
| LC-2 | Governed lifecycle transitions require Owner approval |
| LC-3 | Active project membership does not grant lifecycle authority |
| LC-4 | Unauthorized transitions return LIFECYCLE_CUSTODY_VIOLATION |
| LC-5 | Authority-file lifecycle effects require warning plus Owner approval |
| LC-6 | Owner approval must name the transition, phase, or project |
| LC-7 | Broad lifecycle/project-root approval is invalid |
| LC-8 | Sealed lifecycle evidence is immutable |
| LC-9 | Post-release lifecycle changes require patch order |
| LC-10 | Generated lifecycle state must be deterministic-tool-only |
| LC-11 | No auto-promotion — lifecycle transitions are governed changes |
| LC-12 | If lifecycle state is unknown, block |
| LC-13 | Lifecycle custody does not bypass project-wide write custody (#23) |
| LC-14 | Lifecycle custody does not alter live write contract (#24) |
| LC-15 | Approved transitions preserve approval provenance |

## 3. Architecture

```
Lifecycle Request → lifecycle-custody-extension.py
                          ↓
            ┌─────────────┼─────────────┐
            ↓             ↓             ↓
         ALLOW        BLOCK/LC_*    REQUIRES_OWNER
            ↓             ↓             ↓
      State change    No change     No change
      + receipt       + receipt     + warning
                                    (unless approval)
```

## 4. Modes

| Mode | Behavior |
|------|----------|
| `live` | Evaluate custody; persist state change if ALLOWed; produce audit receipt |
| `dry-run` | Evaluate custody; return decision without state mutation; produce advisory receipt |

## 5. Decision Codes

| Code | Meaning |
|------|---------|
| ALLOW | Lifecycle transition permitted |
| LIFECYCLE_CUSTODY_VIOLATION | Unauthorized transition |
| REQUIRES_OWNER_APPROVAL | Governed transition needs Owner approval |
| FORBIDDEN_SEALED_EVIDENCE | Sealed lifecycle evidence immutable |
| FORBIDDEN_POST_RELEASE_ROUTINE_EDIT | Post-release lifecycle needs patch order |
| GENERATED_LIFECYCLE_ONLY | Generated lifecycle state deterministic-tool-only |

## 6. Known Lifecycle Transitions

| From | To | Condition |
|------|----|-----------|
| Phase 1 (Plan) | Phase 2 | Planning complete, work packet ready |

Additional transitions (Phase 2+) are registered in the MCP lifecycle cursor when the project advances.

## 7. Relationship to Sealed Contracts

| Contract | Relationship |
|----------|-------------|
| #23 PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT-1 | Not modified — lifecycle custody is additive, not substitutive |
| #24 LIVE-CUSTODY-INTEGRATION-1 | Not modified — lifecycle custody is a separate enforcement path |

## 8. Non-Goals

- No Librarian mutation
- No cross-project lifecycle authority
- No auto-approval, auto-seal, auto-promotion, or auto-execution
- No weakening of #23 or #24 contracts

## 9. Boundary Invariants

1. Every lifecycle transition passes through custody checks before state mutation
2. Dry-run mode never mutates state
3. All denied transitions produce audit receipts
4. Approved transitions record approval provenance
5. Known transitions are validated before custody checks
6. #23 and #24 contracts remain unchanged
