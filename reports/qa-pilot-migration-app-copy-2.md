# QA-PILOT-OPENWORK-APP-COPY-1 — Completion Report

**Sprint:** 2/5 of `EPIC-QA-PILOT-OPENWORK-TO-CARBIDEFRAME-MIGRATION-1`
**Status:** 🔍 Agent work complete. Awaiting Owner review.
**Generated:** 2026-07-10T19:11Z
**Work packet:** `wp-qa-pilot-20260710-2` (authorized, dispatched)
**Approval token:** `apt_3ed7340e` (expires 2026-07-11T19:05:20Z)
**Manifest of record:** `reports/qa-pilot-migration-copy-manifest-1.json` (Sprint 1 artifact, sha `c85fda64…`)
**Companion artifacts:** this report, sprint doc, copy-result JSON, copy-audit JSON, overwrite-protection JSON, path-risks JSON, app-open JSON, governance-protection JSON, receipt JSON.

---

## 1. Sprint 2 Outcome (one-line)

The complete OpenWork QA Pilot application (123 content files, 9,014,064 bytes) was copied into `active/qa-pilot/browser-app/` with byte-level SHA-256 verification on every file (0 mismatches), with zero governance overwrites, with the OpenWork source byte-identical before/after, and with the CarbideFrame governance framework remaining green. Pre-existing OpenWork path bugs in 7 HTML pages are recorded but not auto-rewritten, per Owner direction.

## 2. Acceptance Gates

| Gate | Pass criteria | Result |
|------|---------------|--------|
| AG-COPY-1 | All 123 files copied, byte and SHA-256 match | ✅ 123/123, 0 mismatches |
| AG-COPY-2 | No governance file modified/added | ✅ Governance verdict PASS, browser-assets content-hash identical |
| AG-COPY-3 | OpenWork source untouched | ✅ mtimes before/after byte-identical (`48f1708f…` both) |
| AG-COPY-4 | All destinations under `browser-app/`; data/ separation | ✅ 123 destinations, 6 land on `browser-app/data/*` |
| AG-COPY-5 | CarbideFrame validators remain green | ✅ Startup managed, 59 validators, 65 test runners |
| AG-COPY-6 | Relative path risk audit (no broad rewrites) | ✅ 7 broken refs found, 0 auto-rewrites; all pre-existing in OpenWork |
| AG-COPY-7 | Migrated app opens (file:// target) | ⚠ Read-only check: 2/4 landing pages clean, 2 have pre-existing broken refs; pages still load, just specific sub-refs 404 |
| AG-COPY-8 | Skipped/added files explained | ✅ No deviations from manifest |

## 3. Hard Boundaries Honored

- ✅ No overwrite of CarbideFrame governance files (verified by content-hash)
- ✅ No mutation of CarbideFrame Librarian files (not accessed)
- ✅ No mutation of OpenWork QA Pilot source (mtimes byte-identical)
- ✅ No backend/auth/telemetry/external deps added
- ✅ No visual parity or I18N wiring work performed
- ✅ OpenWork source not marked archived or superseded
- ✅ Epic not sealed (this report is 🔍 Pending)
- ✅ `browser-app/data/` kept distinct from governance `data/`
- ✅ `docs/schemas/browser-assets/` preserved as design reference (content-hash unchanged)

## 4. Files Created This Sprint (8)

| Path | SHA-256 |
|------|---------|
| `docs/sprints/QA-PILOT-OPENWORK-APP-COPY-1.md` | (new) |
| `reports/qa-pilot-migration-copy-result-2.json` | `90a19556…` |
| `reports/qa-pilot-migration-copy-manifest-2-audit.json` | `9bf98cfb…` |
| `reports/qa-pilot-migration-overwrite-protection-2.json` | `bea9263e…` |
| `reports/qa-pilot-migration-path-risks-2.json` | `c874e96b…` |
| `reports/qa-pilot-migration-app-open-2.json` | `b2f721af…` |
| `reports/qa-pilot-migration-governance-protection-2.json` | `397fa8de…` |
| `receipts/migration-app-copy-2.json` | (new) |

Plus the 124 files copied into `browser-app/`. Total: 132 new files, 0 governance files modified.

## 5. Open Owner Decisions

The Owner should review and respond before Sprint 3 begins:

1. **Approve Sprint 3 as-planned** — proceed to `QA-PILOT-MIGRATED-APP-SMOKE-VALIDATION-1` (live browser smoke test of 8 user paths: login/session, portal/course, quiz/progress, certificate, admin, simulator, QA module, debug panel; plus build scripts).
2. **Adjust** — fix the 7 pre-existing path bugs first as a bounded mini-sprint, or any other tweak.
3. **Add** — insert a governed I18N revalidation micro-sprint before the smoke test.
4. **Stop** — halt and review.

The approval token `apt_3ed7340e` expires **2026-07-11T19:05:20Z**. Sprint 3 will not begin without a fresh token if expired.

## 6. Carried-Forward Advisory Gap (Sprint 1)

The `project_work_result_intake` MCP tool returned `MCP error -32602: ...missing` for every payload shape (Sprint 1 and Sprint 2). The local artifacts are the canonical evidence. This is recorded as an advisory integration gap, not a blocker.

## 7. Next

Sprint 3 (`QA-PILOT-MIGRATED-APP-SMOKE-VALIDATION-1`) is **not started**. The agent is stopped and awaiting Owner direction.
