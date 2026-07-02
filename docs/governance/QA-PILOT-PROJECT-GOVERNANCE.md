# QA Pilot Project Governance — Sandbox Boundary & Cross-Project Rules

**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** Governance documentation only. QA Pilot is a separate add-on project with its own ledger.

---

## 1. Project Identity

| Field | Value |
|-------|-------|
| project_id | `qa-pilot` |
| project_name | QA Pilot |
| canonical_repo | `/Users/andrew/Desktop/CarbideFrame/qa-pilot` |
| workspace_path | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot` |
| sandbox_boundary | `harness_governed` |
| governance_profile | lightweight-custody |

## 2. Sandbox Boundary Type

Based on PROJECT-LEDGER-CUSTODY-SEPARATION-1's four sandbox boundary types, QA Pilot is classified as **`harness_governed`**:

> Uses Librarian harness (profiles, custody, lifecycle) but has its own ledger.

| Characteristic | QA Pilot |
|----------------|----------|
| Owns its own sprint ledger | ✅ `project-state/sprint-ledger.json` |
| Owns its own status surfaces | ✅ FEATURE-STATUS.md, SESSION-HANDOFF.md |
| Owns its own receipts | ✅ `receipts/` directory |
| Owns its own Owner decisions | ✅ `receipts/decision-resolutions/` |
| May reference Librarian harness | ✅ Project selection, custody, lifecycle |
| May not mutate Librarian runtime | ✅ Sources/ is forbidden |
| May not mutate Librarian governance state | ✅ ledger, receipts, status surfaces forbidden |

## 3. Allowed Mutation Paths

QA Pilot may create or modify files under these paths:

| Path | Purpose |
|------|---------|
| `docs/` | Governance, sprint receipts, examples, schemas |
| `scripts/` | Validators, test runners, utility scripts |
| `fixtures/` | Test and validation fixture data |
| `project-state/` | Sprint ledger, work tracking |
| `receipts/` | Decision records, sprint closeouts |
| `PROJECT-IDENTITY.md` | Project identity document |
| `PROJECT-PROFILE.json` | Project profile configuration |
| `FEATURE-STATUS.md` | Feature status surface |
| `SESSION-HANDOFF.md` | Session handoff surface |

## 4. Forbidden Cross-Project Paths

QA Pilot must never touch these paths (in The Librarian):

| Path | Reason |
|------|--------|
| `**/active/librarian/Sources/**` | Librarian runtime enforcement |
| `**/active/librarian/Public/**` | Librarian UI and web assets |
| `**/active/librarian/project-state/sprint-ledger.json` | Librarian sprint ledger |
| `**/active/librarian/receipts/**` | Librarian decision records |
| `**/active/librarian/FEATURE-STATUS.md` | Librarian status surface |
| `**/active/librarian/SESSION-HANDOFF.md` | Librarian handoff surface |
| `**/active/librarian/docs/governance/**` | Librarian governance docs |
| `**/active/librarian/docs/schemas/**` | Librarian schema definitions |
| `**/active/librarian/docs/rules/**` | Librarian startup/protocol rules |
| `**/.librarian/current-project.json` | Workspace pointer file |

## 5. Cross-Project Reference Rules

| Action | Allowed? | Condition |
|--------|----------|-----------|
| Read Librarian governance docs | ✅ Yes | For context and contract alignment |
| Reference Librarian project profile | ✅ Yes | Via project selector |
| Reference Librarian custody | ✅ Yes | Via custody/handoff packets |
| Import Librarian planning evidence as QA Pilot production | 🔍 Only via Owner-authorized sprint | Requires explicit sprint brief |
| Mutate Librarian sprint ledger | 🚫 No | Forbidden cross-project |
| Mutate Librarian receipt store | 🚫 No | Forbidden cross-project |
| Mutate Librarian Owner decisions | 🚫 No | Forbidden cross-project |
| Mutate Librarian runtime/MCP | 🚫 No | Forbidden cross-project |

## 6. Relationship to The Librarian

QA Pilot is an add-on project governed by the per-project ledger model established in PROJECT-LEDGER-CUSTODY-SEPARATION-1:

- **The Librarian** owns governance, harness, custody, project selection, lifecycle cursors, and cross-project coordination.
- **QA Pilot** owns its own sprint ledger, receipts, status surfaces, Owner decisions, and production implementation.
- The Librarian may select QA Pilot as the active project, granting access to QA Pilot's workspace and harness services.
- QA Pilot may reference Librarian governance docs for contract alignment but must not mutate them.

## 7. Non-Goals

- No runtime custody enforcement mutation
- No MCP tool registration
- No Swift service implementation
- No automatic cross-project synchronization
- No auto-import of Librarian planning evidence

## 8. Boundary Invariants

1. QA Pilot ledger entries must not appear in The Librarian ledger.
2. QA Pilot status surfaces must not be updated by Librarian sprints.
3. QA Pilot Owner decisions must not be recorded in Librarian receipt paths.
4. The Librarian planning-only copies of QA Pilot artifacts remain planning-only unless explicitly imported by a QA Pilot-owned sprint.
