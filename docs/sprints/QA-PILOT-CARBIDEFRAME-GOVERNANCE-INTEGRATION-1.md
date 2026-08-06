# QA-PILOT-CARBIDEFRAME-GOVERNANCE-INTEGRATION-1

**Sprint:** 4/5 of `EPIC-QA-PILOT-OPENWORK-TO-CARBIDEFRAME-MIGRATION-1`
**Type:** governance integration
**Lane:** migration
**Boundary:** QA Pilot-local, startup-contract + PROJECT-PROFILE + governance doc only. No Librarian mutation.
**Librarian impact:** none
**Status:** 🔍 Agent work complete. Awaiting Owner review before Sprint 5.
**Approval token:** `apt_5fd5e21b` (expires 2026-07-14T06:54:16Z)

---

## 1. Sprint Goal

Register the migrated QA Pilot browser application (`browser-app/`) as a known CarbideFrame application surface within the QA Pilot governance framework. Update the startup contract, project profile, and status surfaces to acknowledge the web app's presence. Codify the separation between governance data (`data/`) and application data (`browser-app/data/`). Do not absorb browser-app contents into governance state.

## 2. Changes Made

### 2a. `startup-contract.json` — Governance surface awareness (3 changes)

| Field | Before | After | Rationale |
|-------|--------|-------|-----------|
| `is_web_app` | `false` | `true` | QA Pilot now has a browser web application in addition to its Python governance framework |
| `verification_surfaces` | 4 entries (scripts, tests, schemas, fixtures) | 5 entries (+ "Web application under browser-app/ (124 files, validated Sprint 3)") | Acknowledges the web app exists without absorbing it into governance validation |
| `required_files` | 5 files | 6 files (+ `browser-app/index.html`) | Required file check now verifies the web app entry point exists |
| `context_sources` | 5 entries | 6 entries (+ `browser-app/index.html` as optional context) | Agents can reference the web app for context without it being governance-mandatory |

### 2b. `startup-contract.json` — New fields added

| New field | Value | Purpose |
|-----------|-------|---------|
| `web_app_root` | `"active/qa-pilot/browser-app/"` | Canonical path reference for the web app root |
| `web_app_data_separation` | Object with `governance_data_root`, `application_data_root`, and `note` | Codifies the Owner-directed separation between governance `data/` and application `browser-app/data/` |

### 2c. `PROJECT-PROFILE.json` — Mutation path update

| Change | Before | After |
|--------|--------|-------|
| `allowed_mutation_paths` | 8 entries (docs, scripts, fixtures, project-state, receipts, identity, profile, status surfaces) | 9 entries (+ `"browser-app/"`) |

This ensures that future sprints modifying files under `browser-app/` do not trigger custody write violations. The entry is deliberately placed between `receipts/` and `PROJECT-IDENTITY.md` — governance boundaries followed by the application root.

### 2d. `docs/governance/QA-PILOT-BROWSER-APP-SEPARATION.md` — New governance doc

Created to codify the **three-domain separation**:

| Domain | Path | Governance scope |
|--------|------|-----------------|
| Governance framework | `scripts/`, `docs/governance/`, `docs/schemas/`, `fixtures/`, `project-state/`, `receipts/`, `config/` | ✅ In scope |
| Governance operational data | `data/` (root) | ✅ In scope |
| Browser application | `browser-app/` | ❌ Out of scope |

The doc also specifies:
- Why/browser-app/data/ is distinct from root `data/`
- That no governance validator may read or index `browser-app/` content
- That the migration epic's 4 completed sprints each confirmed the separation was honored
- Future enforcement rules for agents and validators

### 2e. `FEATURE-STATUS.md` — Migration epic row updated

Updated the migration epic row from "Sprint 1/5" to "Sprint 4/5 complete", listing all 4 completed sprints by name.

### 2f. `SESSION-HANDOFF.md` — Top section updated

Updated the active epic status to Sprint 4/5 complete, updated authorization tokens, Sprint 5 listed as awaiting Owner direction.

## 3. Sprint 4 Acceptance Gates

| Gate | Pass criteria | Result |
|------|---------------|--------|
| AG-INT-1 | browser-app/ registered in startup-contract | ✅ `is_web_app=true`, `web_app_root` added, `web_app_data_separation` recorded |
| AG-INT-2 | PROJECT-PROFILE allows browser-app/ mutations | ✅ `allowed_mutation_paths` includes `"browser-app/"` |
| AG-INT-3 | Separation doc created; codifies data/ vs browser-app/data/ | ✅ `docs/governance/QA-PILOT-BROWSER-APP-SEPARATION.md` (3 domains, 6 enforcement rules) |
| AG-INT-4 | Governance/content separation preserved (no absorption) | ✅ Governance validators unchanged; no browser-app files indexed in governance state; no new schemas/validators for browser-app |
| AG-INT-5 | Startup checks remain managed | ✅ Managed, MCP reachable |
| AG-INT-6 | No OpenWork or Librarian files modified | ✅ Confirmed |
| AG-INT-7 | Governance check passes | ✅ PASS (10 passes, 6 drifts OK, 0 violations) |

## 4. Files Changed

| Path | Action | Description |
|------|--------|-------------|
| `startup-contract.json` | Modified | `is_web_app`, `web_app_root`, `web_app_data_separation`, additional `verification_surfaces`, `required_files`, `context_sources` |
| `PROJECT-PROFILE.json` | Modified | `allowed_mutation_paths` + `"browser-app/"` |
| `docs/governance/QA-PILOT-BROWSER-APP-SEPARATION.md` | Created | Three-domain separation governance doc |
| `FEATURE-STATUS.md` | Modified | Migration epic row updated to Sprint 4/5 |
| `SESSION-HANDOFF.md` | Modified | Top section and sprint sequence updated |

No governance scripts, schemas, fixtures, validators, test runners, or operational data were modified. No OpenWork or Librarian files were touched.

## 5. Unresolved Issues

| # | Issue | Severity | Owner decision needed |
|---|-------|----------|----------------------|
| U1 | MCP tools (`project_work_result_intake`, `project_work_packet_draft`) non-functional — Sprint 4 artifacts use local-file receipt pattern | 🟢 LOW | None — carried forward from Sprint 1, accepted as advisory |
| U2 | Approval token `apt_5fd5e21b` expires 2026-07-14T06:54:16Z | 🟡 MEDIUM | Owner re-authorization needed for Sprint 5 if outside window |

## 6. Owner Review Posture

🔍 **Pending.** Sprint 4 complete. Sprint 5 (`QA-PILOT-MIGRATION-ROUNDTRIP-VALIDATION-1`) is not started. Awaiting Owner direction.
