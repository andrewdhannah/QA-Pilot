# QA-PILOT-PROJECT-INIT-1 — QA Pilot Project Initialization

**Status:** ✅ Sealed (ledger #1, Owner-approved 2026-07-02 per OD-QA-PILOT-PROJECT-INIT-1-SEAL)

**Sprint type:** Project initialization — QA Pilot as separate harness_governed add-on project
**Sprint ID:** `QA-PILOT-PROJECT-INIT-1`
**Date:** 2026-07-02
**Branch:** N/A (workspace init — no git branch)
**Starting HEAD:** N/A (new project)
**Predecessor:** PROJECT-LEDGER-CUSTODY-SEPARATION-1 (sealed #225 in The Librarian)
**Authorization basis:** Owner-approved per OD-PROJECT-LEDGER-CUSTODY-SEPARATION-1-SEAL
**Authority:** Project initialization only. No production implementation. No runtime custody. No MCP enforcement. No mainline authority changes.

---

## Objective

Initialize QA Pilot as a separate project under The Librarian's per-project ledger model. Create the QA Pilot workspace, identity, project profile, ledger, receipt root, status surfaces, Owner decision path, sandbox boundary, allowed mutation paths, and forbidden cross-project paths.

## Scope

### In scope
- `active/qa-pilot/` workspace directory structure
- PROJECT-IDENTITY.md (project_id, project_name, owner, canonical_repo)
- PROJECT-PROFILE.json (12 required profile fields)
- `project-state/sprint-ledger.json` (initialized with this sprint)
- FEATURE-STATUS.md (status surface)
- SESSION-HANDOFF.md (handoff surface)
- Receipt directories (`receipts/decision-resolutions/`, `receipts/sprint-closeouts/`)
- `docs/governance/QA-PILOT-PROJECT-GOVERNANCE.md` (sandbox boundary rules)
- `docs/sprints/QA-PILOT-PROJECT-INIT-1.md` (this sprint receipt)

### Out of scope
- QA Pilot production implementation import
- Copying Librarian planning-only evidence as production
- Librarian runtime, MCP enforcement, or mainline authority mutation
- Sprint seal or approval

## Project Profile (12 Fields)

| # | Field | Value |
|---|-------|-------|
| 1 | `project_id` | `qa-pilot` |
| 2 | `project_name` | QA Pilot |
| 3 | `repo_path` | `/Users/andrew/Desktop/CarbideFrame/qa-pilot` |
| 4 | `workspace_path` | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot` |
| 5 | `ledger_path` | `project-state/sprint-ledger.json` |
| 6 | `receipt_root` | `receipts/` |
| 7 | `status_surfaces` | `[FEATURE-STATUS.md, SESSION-HANDOFF.md]` |
| 8 | `owner_decision_path` | `receipts/decision-resolutions/` |
| 9 | `active_sprint` | `QA-PILOT-PROJECT-INIT-1` |
| 10 | `sandbox_boundary` | `harness_governed` |
| 11 | `allowed_mutation_paths` | `[docs/, scripts/, fixtures/, project-state/, receipts/, PROFILE, IDENTITY, STATUS surfaces]` |
| 12 | `forbidden_cross_project_paths` | `[Sources/, Public/, sprint-ledger, receipts, status surfaces, governance, schemas, rules, pointer]` |

## Files Created (14 files)

| File | Description |
|------|-------------|
| `PROJECT-IDENTITY.md` | Project identity (project_id, name, owner, repo, status) |
| `PROJECT-PROFILE.json` | 12 required profile fields |
| `project-state/sprint-ledger.json` | Initialized sprint ledger with this sprint entry |
| `FEATURE-STATUS.md` | Status surface with this sprint listed |
| `SESSION-HANDOFF.md` | Handoff surface with this sprint record |
| `receipts/decision-resolutions/.gitkeep` | Decision receipt directory |
| `receipts/sprint-closeouts/.gitkeep` | Sprint closeout receipt directory |
| `docs/governance/QA-PILOT-PROJECT-GOVERNANCE.md` | Sandbox boundary, allowed/forbidden paths, cross-project rules |
| `docs/sprints/QA-PILOT-PROJECT-INIT-1.md` | This sprint receipt |

## Sandbox Boundary

**Type:** `harness_governed`

QA Pilot uses Librarian harness (profiles, custody, lifecycle) but has its own:
- Sprint ledger (`project-state/sprint-ledger.json`)
- Status surfaces (FEATURE-STATUS.md, SESSION-HANDOFF.md)
- Receipts (`receipts/`)
- Owner decisions (`receipts/decision-resolutions/`)

## Allowed Mutation Paths

`docs/`, `scripts/`, `fixtures/`, `project-state/`, `receipts/`, `PROJECT-IDENTITY.md`, `PROJECT-PROFILE.json`, `FEATURE-STATUS.md`, `SESSION-HANDOFF.md`

## Forbidden Cross-Project Paths

Librarian Sources/, Public/, sprint-ledger, receipts, status surfaces, governance docs, schemas, rules, and workspace pointer file.

## Validation Results

### Profile Field Validation
```
Fields defined: 12/12
project_id:      qa-pilot (pattern: ^[a-z][a-z0-9_-]+$)
sandbox_boundary: harness_governed (valid enum)
allowed_mutation_paths:  9 entries
forbidden_cross_project: 11 entries
Result: ALL 12 FIELDS PRESENT ✅
```

### Sprint Ledger Validation
```
File:          project-state/sprint-ledger.json
Valid JSON:    ✅
Sprints:       1 (QA-PILOT-PROJECT-INIT-1)
Sprint status: pending (not sealed)
Result: VALID JSON LEDGER ✅
```

### Status Surface Validation
```
FEATURE-STATUS.md:   Present ✅
SESSION-HANDOFF.md:  Present ✅
sprint entry:        QA-PILOT-PROJECT-INIT-1 present in both ✅
```

### Receipt Path Validation
```
receipts/decision-resolutions/:   Exists ✅
receipts/sprint-closeouts/:       Exists ✅
```

### Prohibited-Zone Scan

```
Forbidden patterns checked:
  active/librarian/Sources/           — NOT touched ✅
  active/librarian/Public/           — NOT touched ✅
  active/librarian/project-state/    — NOT touched ✅
  active/librarian/receipts/         — NOT touched ✅
  active/librarian/FEATURE-STATUS.md — NOT touched ✅
  active/librarian/SESSION-HANDOFF.md— NOT touched ✅
  active/librarian/docs/governance/  — NOT touched ✅
  active/librarian/docs/schemas/     — NOT touched ✅
  .librarian/current-project.json    — NOT touched ✅
  QA Pilot production implementation — NOT imported ✅
Result: CLEAN — no forbidden paths touched
```

### Production Import Check
```
Librarian planning-only QA Pilot artifacts: NOT copied ✅
QA Pilot production implementation: NOT imported ✅
Only project init files created: ✅
```

## Acceptance Gates

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 1 | active/qa-pilot/ exists | **Pass** | Directory created with 7 subdirectories |
| 2 | Project identity exists | **Pass** | PROJECT-IDENTITY.md with 8 identity fields |
| 3 | Project profile exists with 12 required fields | **Pass** | PROJECT-PROFILE.json with all fields |
| 4 | Sprint ledger exists and is valid | **Pass** | sprint-ledger.json — valid JSON, 1 sprint entry |
| 5 | Status surfaces exist | **Pass** | FEATURE-STATUS.md, SESSION-HANDOFF.md both present |
| 6 | Receipt roots exist | **Pass** | decision-resolutions/, sprint-closeouts/ both exist |
| 7 | Sandbox boundary is declared | **Pass** | sandbox_boundary: harness_governed |
| 8 | Allowed mutation paths are declared | **Pass** | 9 paths in allowed_mutation_paths |
| 9 | Forbidden cross-project paths are declared | **Pass** | 11 paths in forbidden_cross_project_paths |
| 10 | Closeout receipt exists and states pending Owner review | **Pass** | This document |
| 11 | No production implementation imported | **Pass** | No QA Pilot production files copied or created |
| 12 | No Librarian runtime/MCP enforcement touched | **Pass** | Prohibited-zone scan CLEAN |

## Unresolved Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| QA Pilot is not yet registered in the workspace pointer file | Low | Pointer registration deferred to after init sprint approval |
| QA Pilot repo has existing content but no governed project structure | Low | Existing repo is separate from active/qa-pilot/ workspace; init sprint is workspace-only |
| Librarian planning-only QA Pilot artifacts need eventual import decision | Low | Requires Owner-authorized sprint to import as production under QA Pilot ledger |

## Recommended Next Sprint

### `QA-PILOT-PRODUCTION-LANE-A-1` (under QA Pilot ledger)

**Scope:** Import the QA Pilot production receipt schema, governance doc, fixtures, validator, and test runner from The Librarian's planning-only evidence into the QA Pilot project ledger as production implementation. This requires explicit Owner authorization.

This is the same work that was previously mis-scoped in The Librarian. Under the QA Pilot ledger, it is correctly scoped as QA Pilot production implementation.

## Closeout

**This sprint does not:**
- Seal itself or any other sprint
- Claim Owner approval of any kind
- Import QA Pilot production implementation
- Copy planning-only evidence as production
- Mutate The Librarian runtime, custody, or MCP enforcement
- Mutate mainline Owner decision authority

**This sprint does:**
- Initialize QA Pilot as a separate project under the per-project ledger model
- Create project workspace, identity, profile (12 fields), ledger, status surfaces, receipt paths
- Define sandbox boundary, allowed mutation paths, forbidden cross-project paths
- Establish QA Pilot as a harness_governed add-on project

**Status: ✅ Sealed (ledger #1, Owner-approved 2026-07-02 per OD-QA-PILOT-PROJECT-INIT-1-SEAL)**

The Owner approved and sealed this sprint on 2026-07-02. Decision receipt: `receipts/decision-resolutions/od-qa-pilot-project-init-1-seal.json`.

**Sprint-ledger entry:** Added as sealed_number=1 in QA Pilot ledger.
**Owner decision receipt:** Created at `receipts/decision-resolutions/od-qa-pilot-project-init-1-seal.json`.
**FEATURE-STATUS.md:** Updated with sealed entry.
**SESSION-HANDOFF.md:** Updated with sealed record.
**Git repo:** Initialized in active/qa-pilot/.
**Next authorized sprint:** QA-PILOT-PRODUCTION-LANE-A-1.
