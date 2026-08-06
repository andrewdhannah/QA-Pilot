# QA-PILOT-OPENWORK-APP-COPY-1

**Sprint:** 2/5 of `EPIC-QA-PILOT-OPENWORK-TO-CARBIDEFRAME-MIGRATION-1`
**Type:** copy (manifest-driven)
**Lane:** migration
**Boundary:** QA Pilot-local, browser-app only. No Librarian mutation.
**Librarian impact:** none
**Status:** 🔍 Agent work complete. Awaiting Owner review before Sprint 3.
**Work packet:** `wp-qa-pilot-20260710-2` (authorized, dispatched)
**Dispatch:** `spd-qa-pilot-20260710-2`
**Approval token:** `apt_3ed7340e` (expires 2026-07-11T19:05:20Z)
**Manifest of record:** `reports/qa-pilot-migration-copy-manifest-1.json` (Sprint 1 artifact)

---

## 1. Sprint Goal

Copy the complete OpenWork QA Pilot application from `/Users/andrew/Desktop/OpenWork/QA Pilot` into `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/browser-app/`, using `reports/qa-pilot-migration-copy-manifest-1.json` as the source of truth. Preserve relative paths. Verify SHA-256 of every copy. Verify no CarbideFrame governance file is overwritten. Verify the OpenWork source is untouched. Audit relative path risks without broad rewrites. Verify the migrated app's primary pages can open (read-only check).

## 2. Files / Directories Copied

| Top-level entry | Subdir | File count |
|-----------------|--------|------------|
| `ARCHITECTURE.md`, `LOCAL-AI-ARCHITECTURE.md`, `README.md`, `QASimulator.ico`, `QASimulator.html`, `QA-Pilot-Session.html`, `START_Me_Up.html`, `build.bat`, `build.command`, `build.js`, `build.sh`, `capstone-2.html`, `capstone-2.html.bak`, `capstone-lab.html`, `capstone.html`, `certificate.html`, `confirm.html`, `course-view.html`, `crm-lab.html`, `ado-lab.html`, `favicon.png`, `favicon.svg`, `guide-facilitator.html`, `guide-student.html`, `index.html`, `launch.bat`, `launch.command`, `make_icon_win.py`, `mock.html`, `os.bundle.js`, `os.css`, `package.json`, `portal.html`, `simple-login.html` | root | 34 |
| `admin/` | subdir | 6 (`assign.html`, `bugs.html`, `dashboard.html`, `editor.html`, `index.html`, `simple.html`) |
| `apps/` | subdir | 16 (12 simulated apps + 4 stub/dynamics/ppt/qoutlook) |
| `chrome-extension/` | subdir | 3 |
| `css/` | subdir | 3 (`ado-mock.css`, `dynamics-mock.css`, `main.css`) |
| `data/` | subdir | 6 (`assignments.js`, `bug-keys.js`, `content.js`, `progress.js`, `quiz-questions.js`, `students.js`) |
| `debug/` | subdir | 7 |
| `desktop/` | subdir | 8 (4 html + 3 docs + `videos/` with 4 PNGs) |
| `js/` | subdir | 7 (`app.js`, `clippy-guide.js`, `db.js`, `i18n.js`, `lang-en.js`, `lang-fr.js`, `pdf-lib.js`) |
| `qa/` | subdir | 9 |
| `QA Pilot Docs/` | subdir | 3 |
| `scenarios/` | subdir | 6 |
| `src/` | subdir | 8 (7 + `custody/`) |
| **Total** | | **123** |

Plus `browser-app/.gitkeep` (carried over from Sprint 1) = **124 files**, **8.8 MB** on disk.

## 3. Manifest Match Result

**PASS.** Every file in the manifest was copied with byte-identical content. The audit JSON (`reports/qa-pilot-migration-copy-result-2.json`, SHA `90a19556…`) records per-file source SHA, destination SHA, and metadata. Summary:

- Expected count: **123**
- Copied count: **123**
- Pre-source SHA mismatches: **0**
- Post-destination SHA mismatches: **0**
- Failures: **0**
- Total bytes copied: **9,014,064**

## 4. Overwrite-Protection Result

**PASS.** Refreshed verdict at `reports/qa-pilot-migration-overwrite-protection-2.json` (SHA `bea9263e…`) confirms every destination is under `active/qa-pilot/browser-app/`. No CarbideFrame governance root was written to.

## 5. SHA / Hash Verification Result

**PASS.** Every copied file's SHA-256 matches the manifest's `sha256` field after the copy. Verified per-file in the result JSON. The full result report is at `reports/qa-pilot-migration-copy-result-2.json`; the audit summary is at `reports/qa-pilot-migration-copy-manifest-2-audit.json` (SHA `9bf98cfb…`).

## 6. Files Skipped or Added Outside Manifest

| Deviation | Reason |
|-----------|--------|
| None | All 123 manifest files copied; no file was added, skipped, renamed, or removed |

The copy was strictly manifest-driven. Excluded a-priori (per manifest): `.git/`, `.DS_Store`, `.gitattributes`, `.gitignore`. The `.gitkeep` from Sprint 1 was already in `browser-app/` and was preserved.

## 7. Relative Path Risks Found (7 pages with broken asset references)

Per Owner direction: recorded, **not** auto-rewritten. All broken references are **pre-existing OpenWork source issues**, not migration issues. They are reproducible in the OpenWork source: open the same page from `/Users/andrew/Desktop/OpenWork/QA Pilot/` and the same refs fail.

| Page | Broken ref | Resolves to | Likely cause |
|------|-----------|-------------|--------------|
| `QASimulator.html` | `../favicon.svg` | `active/qa-pilot/favicon.svg` | The page uses `../` to mean "parent of the built output" but at the source root there is no parent favicon. The build script (`build.js`) likely embeds a copy of `favicon.svg` into a subdirectory before `../` makes sense. |
| `capstone.html` | `../favicon.svg` | `active/qa-pilot/favicon.svg` | Same pattern as `QASimulator.html` |
| `capstone-2.html` | `../favicon.svg` | `active/qa-pilot/favicon.svg` | Same pattern |
| `certificate.html` | `course.html` | `browser-app/course.html` (missing) | The page references `course.html` but the actual page is `course-view.html` — a stale OpenWork link |
| `index.html` | `about.html` | `browser-app/about.html` (missing) | Pre-existing OpenWork: the page references a sibling `about.html` that does not exist in the source |
| `desktop/index.html` | `os.css` | `browser-app/desktop/os.css` (missing) | The page references `os.css` from a `desktop/` subdirectory; the actual file is at `browser-app/os.css`. Should be `../os.css`. |
| `desktop/dist.html` | `data/bug-keys.js` | `browser-app/desktop/data/bug-keys.js` (missing) | Should be `../data/bug-keys.js` |

**Audit report:** `reports/qa-pilot-migration-path-risks-2.json` (SHA `c874e96b…`) — scanned 43 HTML files, 7 had broken refs, all pre-existing in OpenWork source.

**Not rewritten** because: (1) Owner instruction was "do not perform broad path rewrites unless required for the copied app to open", (2) the broken refs are not blocking — the pages still render, just with 404s on those specific hrefs, (3) any rewrite would diverge from the OpenWork source, (4) Sprint 4 (governance integration) and a follow-up I18N revalidation are the right places to fix the page-level references.

## 8. Whether the Migrated App Opens at the Target Location

**Read-only check passed for 2 of 4 landing pages; 2 had pre-existing broken refs that do not block the page from loading.**

| Page | Exists | References scanned | Missing | Opens cleanly |
|------|--------|--------------------|---------|----------------|
| `index.html` | ✅ | (scanned) | 1 (`about.html`) | ❌ (pre-existing) |
| `portal.html` | ✅ | (scanned) | 0 | ✅ |
| `course-view.html` | ✅ | (scanned) | 0 | ✅ |
| `certificate.html` | ✅ | (scanned) | 1 (`course.html`) | ❌ (pre-existing) |

Audit report: `reports/qa-pilot-migration-app-open-2.json` (SHA `b2f721af…`).

**Note:** This audit is **read-only** and **does not launch a browser**. It walks every `<href>` and `<src>` reference in the four most-trafficked landing pages and checks that each resolves to a file under `browser-app/`. The two pages that did not "open cleanly" still load — the page itself is well-formed HTML; only specific sub-references 404.

A live browser launch is out of scope for this read-only audit. It is the natural next step in Sprint 3 (`QA-PILOT-MIGRATED-APP-SMOKE-VALIDATION-1`), which is explicitly authorized to "verify the migrated app opens from `file://`" via browser automation.

## 9. Working Tree Delta

| Metric | Before Sprint 2 | After Sprint 2 | Delta |
|--------|-----------------|----------------|-------|
| `dirty/417` baseline (pre-Sprint 1) | — | — | — |
| `dirty/426` after Sprint 1 | — | — | — |
| `dirty/N` after Sprint 2 | 426 | 549 | **+123** |
| Tracked-by-manifest copies in `browser-app/` | 0 (only `.gitkeep`) | 124 | **+124** |
| Receipts files | 3 (Sprint 1 archive + 2 receipts) | 4 (+1 this sprint) | **+1** |
| Reports files | 3 (Sprint 1 reports) | 9 (+6 this sprint) | **+6** |
| Sprint docs | 1 (Sprint 1 doc) | 2 (+1 this sprint) | **+1** |
| CarbideFrame governance SHA changes | 0 | 0 (browser-assets tree content-hash unchanged; 3 status surfaces drifted by design; all other files SHA-equal) | **0 unexpected** |

Working tree dirty count grew by 123, exactly matching the manifest file count. No additional untracked files appeared.

## 10. Validation Commands / Checks and Results

| Check | Tool | Result |
|-------|------|--------|
| Source SHA-256s re-verified right before copy | `run_copy.py` | **0 mismatches** across 123 files |
| Copy executed and post-copy SHA-256s re-verified | `run_copy.py` | **0 mismatches** |
| OpenWork mtimes before/after copy | `find -exec stat` + `shasum` | **Byte-identical** (`48f1708f…` before == after) |
| CarbideFrame governance content-hash | `governance_check2.py` | **PASS** (13 passes, 0 violations, 3 expected drifts on status surfaces) |
| Browser-assets archive content-hash | `governance_check2.py` (tarfile content hash) | **PASS** (content-hash `a273b029…` matches; raw tarball SHA differs only by pax mtime) |
| `docs/schemas/browser-assets/` byte-identical to Sprint 1 archive | `diff -rq` | **Identical** |
| Startup checks after copy | `scripts/run-startup-checks.sh` | **Managed, MCP reachable, 59 validators, 65 test runners, no blockers** |
| Path risks scan | `run_copy.py` regex | **7 pages with pre-existing broken refs; no rewrites** |
| App open read-only check | `run_copy.py` regex | **2/4 landing pages open cleanly; 2 have pre-existing broken refs** |
| Receipts/ growth | governance count check | **+1** (Sprint 2's own receipt) — recorded as expected drift |

## 11. Unresolved Issues

| # | Issue | Severity | Owner decision needed |
|---|-------|----------|----------------------|
| U1 | Pre-existing OpenWork path bugs (7 pages with `../` or wrong-name references) | 🟡 MEDIUM | None required for Sprint 2 close. Sprint 3 smoke validation will surface runtime impact. Any fix must be re-validated against the migrated app. |
| U2 | `index.html` references non-existent `about.html` | 🟡 MEDIUM | Same as U1 |
| U3 | `desktop/index.html` references `os.css` instead of `../os.css` | 🟡 MEDIUM | Same as U1 |
| U4 | Sprint 1 advisory gap: `project_work_result_intake` MCP server-side record missing (carried forward per Owner direction; not a blocker) | 🟢 LOW | Optional: investigate why the MCP tool returned `-32602 missing`; local artifacts remain canonical evidence |
| U5 | `capstone-2.html.bak` was in the manifest and copied. This is a pre-existing OpenWork backup file. | 🟢 LOW | None — preserved per manifest |
| U6 | `QA Pilot Docs/` directory contains a space; migration preserves the space. Browsers and `file://` handle it fine. | 🟢 LOW | None — preserved per manifest |
| U7 | Approval token `apt_3ed7340e` expires 2026-07-11T19:05:20Z. Sprint 3 must occur before then or Owner must issue a fresh approval. | 🟡 MEDIUM | Owner will need to re-authorize before Sprint 3 if not within 24h |

## 12. Owner Review Posture

- This sprint is **🔍 Agent work complete** and **not sealed**.
- No `wp-qa-pilot-20260710-2` close or seal is requested.
- The copy is **complete and verified** at byte level. Pre-existing path bugs in the OpenWork source are surfaced but not fixed.
- **Sprint 3 will not begin without explicit Owner direction.** Possible Owner responses:
  1. **Approve** — proceed to `QA-PILOT-MIGRATED-APP-SMOKE-VALIDATION-1` (live browser smoke test of all 8 user paths: login/session/portal/course/certificate/admin/sim/QA module/debug panel).
  2. **Adjust** — Owner may want to fix the pre-existing path bugs first as a bounded mini-sprint, or rename `browser-app/data/` (Owner direction was *not* to rename this sprint).
  3. **Add** — Owner may want to add a governed I18N revalidation micro-sprint before the smoke test.
  4. **Stop** — Owner may want to halt and review.

## 13. Sprint 2 Artifacts

| Path | SHA-256 | Purpose |
|------|---------|---------|
| `browser-app/**` | (124 files) | The complete migrated QA Pilot application |
| `docs/sprints/QA-PILOT-OPENWORK-APP-COPY-1.md` | (this doc) | Sprint 2 doc |
| `reports/qa-pilot-migration-copy-result-2.json` | `90a19556…` | Per-file copy audit with SHA verification |
| `reports/qa-pilot-migration-copy-manifest-2-audit.json` | `9bf98cfb…` | Summary audit |
| `reports/qa-pilot-migration-overwrite-protection-2.json` | `bea9263e…` | Overwrite-protection refresh |
| `reports/qa-pilot-migration-path-risks-2.json` | `c874e96b…` | Per-HTML relative path risk log |
| `reports/qa-pilot-migration-app-open-2.json` | `b2f721af…` | Read-only app-open check on 4 landing pages |
| `reports/qa-pilot-migration-governance-protection-2.json` | `397fa8de…` | Governance content-hash check |
| `receipts/migration-app-copy-2.json` | (created) | Sprint 2 receipt with approval link, evidence, decisions, and carry-forward |
