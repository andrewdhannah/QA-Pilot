# QA-PILOT-MIGRATION-PREP-AND-SNAPSHOT-1

**Sprint:** 1/5 of `EPIC-QA-PILOT-OPENWORK-TO-CARBIDEFRAME-MIGRATION-1`
**Type:** prep + snapshot (no copy yet)
**Lane:** migration
**Boundary:** QA Pilot-local, browser-app only. No Librarian mutation.
**Librarian impact:** none
**Status:** 🔍 Agent work complete. Awaiting Owner review before Sprint 2.
**Work packet:** `wp-qa-pilot-20260710-1` (authorized, dispatched)
**Dispatch:** `spd-qa-pilot-20260710-1`
**Approval token:** `apt_bb2995d2` (expires 2026-07-11T18:53:52Z)

---

## 1. Sprint Goal

Prepare for the Option A migration of the complete QA Pilot application from `/Users/andrew/Desktop/OpenWork/QA Pilot` into `active/qa-pilot/browser-app/`. **Sprint 1 performs no file copy.** It captures the current CarbideFrame QA Pilot state, archives the existing browser-assets as design reference, verifies the planned copy cannot overwrite any governance file, and produces the final copy manifest for Sprint 2.

## 2. Exact Paths Inspected

| # | Path | Role | Access |
|---|------|------|--------|
| 1 | `/Users/andrew/Desktop/OpenWork/QA Pilot` | Complete QA Pilot source (read-only) | Read-only |
| 2 | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot` | CarbideFrame QA Pilot (governance + incomplete browser shell) | Read + bounded writes (status surfaces, new docs/reports/receipts) |
| 3 | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/docs/schemas/browser-assets/` | CarbideFrame browser training platform (Librarian-converged design) | Read + archive |
| 4 | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/browser-app/` | New dedicated web-app root (created by this sprint, empty) | Read + .gitkeep only |
| 5 | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/scripts/` | CarbideFrame governance framework | Read-only (no write) |
| 6 | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/docs/governance/` | Governance contracts | Read + this new doc only |
| 7 | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/project-state/sprint-ledger.json` | Sprint ledger | Read-only (no write) |
| 8 | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/receipts/` | Receipts root | Read + new artifact only |
| 9 | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/reports/` | Reports root | Read + new artifact only |
| 10 | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/data/` | Governance operational data store | Read-only (no write) |
| 11 | `/Users/andrew/Desktop/CarbideFrame/active/librarian/` | CarbideFrame Librarian (cross-project reference) | Not accessed |
| 12 | `/Users/andrew/Desktop/CarbideFrame/reports/QA-PILOT-SOURCE-OF-TRUTH-RECONCILIATION-1.md` | Source reconciliation (Option A recommendation) | Read-only |

## 3. Snapshot / Archive Actions Performed

| Action | Path | SHA-256 | Bytes | Entries |
|--------|------|---------|-------|---------|
| tar.gz of `docs/schemas/browser-assets/` | `receipts/browser-assets-snapshot.tar.gz` | `ad86d395c7e37c1ca84da3a48e67d81a2efb3073f743b827f5b8f93f6bfa603a` | 110,750 | 21 |

### Governance status-surface checksums (captured before any write)

| File | SHA-256 |
|------|---------|
| `STARTUP-STATE.md` | `5c84af4091f344f58526d3f2945e21938f26c79bf92aaf4a37dc22e8583ffe06` |
| `PROJECT-IDENTITY.md` | `c2a5740823c0f1c33f7516f64b744499c52cbeaeffa04958b6a5ff668812ea03` |
| `PROJECT-PROFILE.json` | `67b6c79cc6a66320b8634cd0172ea37133256541f8313ee70d2daf15f76edd7e` |
| `startup-contract.json` | `e3bbc1c8b1c734371adc5f445d6e135690c71968543975e61e1bc2ca085d4379` |
| `FEATURE-STATUS.md` (before) | `ef1c091eb76ad00043c01e0206129f795ff9a14c73c6e28fbcdc81df1c4e9ab0` |
| `SESSION-HANDOFF.md` (before) | `5fb241adeef2469fb40441968f95dcb06b25538e990328f65ba7628c0dff4a54` |
| `project-state/sprint-ledger.json` | `7259bd7e30b940102cc165b985079b3ef651f2767aaeca812a956602ee83b21d` |

## 4. Files / Directories Protected from Overwrite

All governance roots were protected from any write this sprint, and the planned Sprint 2 copy was verified to land entirely under `browser-app/`:

- `scripts/` — Python governance framework (~170 scripts, 59 validators, 65 test runners)
- `docs/governance/` — Governance contracts (including this doc and the new epic doc)
- `docs/schemas/` — JSON schemas (including the archived browser-assets subtree)
- `fixtures/` — Validator fixtures
- `project-state/sprint-ledger.json` — Canonical sprint ledger (no new entries this sprint)
- `receipts/` — Receipts root (only added `browser-assets-snapshot.tar.gz` and `migration-prep-snapshot-1.json`)
- `data/` — Governance operational data store (no write)
- `config/` — Broker config (no write)
- `PROJECT-IDENTITY.md`, `PROJECT-PROFILE.json`, `startup-contract.json`, `PROJECT-STARTUP.md` — Identity/profile/contract (no write)
- `FEATURE-STATUS.md`, `SESSION-HANDOFF.md`, `STARTUP-STATE.md` — Status surfaces (intentional corrections applied; checksum drift is expected and recorded in the receipt)
- `CLAUDE.md` — Workspace adapter (no write)
- `/Users/andrew/Desktop/CarbideFrame/active/librarian/` — Cross-project, read-only
- `/Users/andrew/Desktop/OpenWork/QA Pilot/` — Source, read-only

## 5. Final Copy Manifest

`reports/qa-pilot-migration-copy-manifest-1.json`

- SHA-256: `c85fda640f617ef2dc2b6162496e2d05c09a409206b1382f0479aa7c57406ef0`
- File count: **123** content files (excludes `.git/`, `.DS_Store`, `.gitattributes`, `.gitignore`)
- Total bytes: **9,014,064** (≈ 8.6 MB)
- Overwrite collisions: **0** (browser-app/ is empty; created this sprint)
- Governance collisions: **0**
- 6 `data/*` files (`assignments.js`, `bug-keys.js`, `content.js`, `progress.js`, `quiz-questions.js`, `students.js`) are annotated as landing on `browser-app/data/` — intentionally distinct from the governance `data/` root per Owner direction R5 in the reconciliation report.

The manifest lists every file with source absolute path, source relative path, destination absolute path, destination relative path, SHA-256, and size in bytes.

## 6. Overwrite Protection Verdict

`reports/qa-pilot-migration-overwrite-protection-1.json`

- `verdict`: **PASS**
- `destination_root_empty`: true
- Every destination is under `active/qa-pilot/browser-app/`; no path escapes the web-app root; no destination collides with a forbidden governance file or directory.

## 7. Status Corrections Made

| Surface | Before | After | Why |
|---------|--------|-------|-----|
| `FEATURE-STATUS.md` — visual parity row | "In Progress (Sprint 3/5 complete)" | "Re-scoped — paused pending migration validation (Sprint 2/5 verified, Sprints 3-5 paused)" | Sprint 3 was completed against an incomplete browser shell; Sprints 4-5 are paused by Owner direction |
| `FEATURE-STATUS.md` — I18N row | "5/5 sprints complete" implied via sprint count in `EPIC-QA-PILOT-DESIGN-QUALITY-REGRESSION-1` row and the prior handoff's claim | "5 sprints run, none sealed; revalidation required post-migration" | I18N wiring was performed against the same incomplete shell; Owner decision 2026-07-09 paused it before any seal |
| `FEATURE-STATUS.md` — added new row | — | `EPIC-QA-PILOT-OPENWORK-TO-CARBIDEFRAME-MIGRATION-1` active row | New epic creation is observable in the canonical status surface |
| `SESSION-HANDOFF.md` — top section | Belonged to visual parity epic | Replaced with the new migration epic as the active epic | Top handoff must always reflect the current active epic |
| `SESSION-HANDOFF.md` — visual parity section | Stated Sprint 3 complete | Re-scoped with explicit "Sprint 2/5 verified" + reason | Mirrors FEATURE-STATUS correction |
| `SESSION-HANDOFF.md` — I18N section | Claimed "5/5 sprints complete" | "5 sprints run, none sealed" | Same correction as FEATURE-STATUS |

No ledger, profile, identity, contract, schema, fixture, script, governance doc (other than the new epic + sprint doc), or receipt was modified.

## 8. Risks

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| R1 | Path reference breakage — OpenWork pages use relative paths. Moving to `browser-app/` could break `css/main.css` etc. references in pages that themselves live in subdirectories like `admin/` or `apps/`. | 🟡 MEDIUM | Sprint 3 smoke validation will open every page in a browser; relative path audit is part of acceptance |
| R2 | Manifest desync — if OpenWork source changes between Sprint 1 and Sprint 2, manifest SHA-256s will be stale. | 🟡 MEDIUM | Re-run `python3 .../build_manifest.py` at the top of Sprint 2; abort if SHA mismatches expected |
| R3 | `data/` purpose drift — `browser-app/data/` and the governance `data/` root are different roots but have the same name. Future maintainers could confuse them. | 🟡 MEDIUM | Sprint 4 adds an explicit `browser-app/data/README.md` distinguishing the two stores |
| R4 | I18N revalidation scope — the 99 extra EN keys (279 vs 180) and ~200 extra FR lines from `docs/schemas/browser-assets/i18n/` must be merged into the migrated app's `i18n/lang-*.js` | 🟡 MEDIUM | Out of scope for the migration epic; a follow-up I18N revalidation epic is the only path to I18N seal |
| R5 | Visual parity shell-styling is now orphaned — the CarbideFrame browser-assets HTML pages styled by Sprints 1-3 are no longer the canonical browser app. | 🟢 LOW | `docs/schemas/browser-assets/` is preserved as archived design reference; the new visual-parity epic targets `browser-app/` |
| R6 | Approval token expiry — `apt_bb2995d2` expires 2026-07-11T18:53:52Z. Sprint 2 must occur before then or a new approval must be requested. | 🟡 MEDIUM | Owner will be informed; Sprint 2 will not start without a fresh token if expired |

## 9. Validation Performed

- ✅ `bash scripts/run-startup-checks.sh` — managed mode, MCP reachable, no blockers introduced
- ✅ Manifest is well-formed JSON; 123 files; 0 overwrites; 0 governance collisions
- ✅ Browser-assets archive is a valid tar.gz with 21 entries; SHA-256 recorded
- ✅ Receipt `migration-prep-snapshot-1.json` is valid JSON
- ✅ Manifest dest paths all begin with `browser-app/`; no path escapes the web-app root
- ✅ No `scripts/`, `docs/governance/` (existing docs), `docs/schemas/`, `fixtures/`, `project-state/`, `receipts/` (existing receipts), `data/`, `config/`, `PROJECT-IDENTITY.md`, `PROJECT-PROFILE.json`, `startup-contract.json`, `PROJECT-STARTUP.md`, `CLAUDE.md`, or `active/librarian/` was modified
- ✅ `/Users/andrew/Desktop/OpenWork/QA Pilot/` was not modified (read-only this sprint)

## 10. Owner Review Posture

- This sprint is **🔍 Agent work complete** and **not sealed**.
- No `wp-qa-pilot-20260710-1` close or seal is requested.
- Sprint 2 (file copy) **must not begin** without explicit Owner direction. Possible Owner responses:
  1. **Approve** — proceed to Sprint 2 with this manifest as the source of truth.
  2. **Adjust** — Owner may want a different destination, exclusions, or post-copy layout (e.g., remap `browser-app/data/` to `browser-app/courses/` to remove the `data/` name shadowing).
  3. **Re-scope** — Owner may want to fold the I18N revalidation into the migration epic.
  4. **Stop** — Owner may want to halt and reconsider the Option A approach.
- The visual parity and I18N epics remain paused regardless of Sprint 2's outcome; the explicit Owner authorization to re-scope those epics is recorded in `SESSION-HANDOFF.md` and `FEATURE-STATUS.md`.

## 11. Sprint 1 Artifacts

| Path | Purpose |
|------|---------|
| `docs/governance/EPIC-QA-PILOT-OPENWORK-TO-CARBIDEFRAME-MIGRATION-1.md` | Epic governance record |
| `docs/sprints/QA-PILOT-MIGRATION-PREP-AND-SNAPSHOT-1.md` | This sprint doc |
| `receipts/browser-assets-snapshot.tar.gz` | Archived design reference |
| `receipts/migration-prep-snapshot-1.json` | Snapshot receipt with all SHA-256s and corrections log |
| `reports/qa-pilot-migration-copy-manifest-1.json` | Final copy plan for Sprint 2 |
| `reports/qa-pilot-migration-overwrite-protection-1.json` | Overwrite protection verdict |
| `browser-app/.gitkeep` | Marks the new web-app root |
| `FEATURE-STATUS.md` (updated) | Status surface correction |
| `SESSION-HANDOFF.md` (updated) | Status surface correction |
