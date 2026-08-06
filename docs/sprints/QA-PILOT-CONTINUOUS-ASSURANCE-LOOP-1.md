# QA-PILOT-CONTINUOUS-ASSURANCE-LOOP-1 — Continuous Assurance Loop

**Type:** implementation / assurance infrastructure
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** assurance
**Boundary:** QA Pilot-local, Librarian advisory boundary
**Dependencies:** #189 (release readiness aggregation)

---

## Purpose

Move QA Pilot from event-driven assessment to continuous assurance. Repository changes trigger impact detection, relevant profile selection, targeted validation, and updated evidence — without manual invocation.

---

## Scope

### Included

| # | Area | Action |
|---|------|--------|
| 1 | Change detection | Watch repository for modifications (git-based) |
| 2 | Impact analysis | Determine which assurance profiles are affected by changes |
| 3 | Targeted validation | Run only affected capability profiles, not full suite |
| 4 | Evidence update | Update existing evidence packages with new findings |
| 5 | Staleness detection | Flag evidence older than a configurable threshold |

### Flow

```
Repository change
      ↓
Impact detection (which files changed?)
      ↓
Profile selection (which assurance profiles affected?)
      ↓
Targeted validation (run affected capabilities)
      ↓
Evidence update (merge new findings into existing packages)
      ↓
Staleness check (flag aging evidence)
      ↓
Owner notification (decision surface updated)
```

### Non-Scope

- Real-time file watching (daemon/service)
- CI/CD integration
- Release gate automation
- Change approval

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| CL-1 | Change detection implemented (git diff) |
| CL-2 | Impact-to-profile mapping defined |
| CL-3 | Targeted validation executes only affected profiles |
| CL-4 | Evidence packages updated incrementally |
| CL-5 | Staleness threshold configurable |
| CL-6 | Evidence produced |
| CL-7 | No automated release decisions |

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Ledger entry:** #190 (authorized)
