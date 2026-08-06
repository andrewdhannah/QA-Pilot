# ARTIFACT-STORAGE-SCALE-AUDIT-1 — Storage and Artifact Topology Audit

**Date:** 2026-07-08
**Scope:** Librarian (`active/librarian`) + QA Pilot (`active/qa-pilot`)
**Type:** Read-only topology survey. No files modified.

---

## Executive Summary

The combined Librarian + QA Pilot project occupies **~4.4 GB on disk**.

Of that, **~3.1 GB (~70%) is a Swift build cache** (`.build/` — debug dSYMs, object files, package checkouts) that can be regenerated on demand. Excluding build artifacts, the source, docs, and data footprint is **~1.3 GB**.

Within that 1.3 GB, the single largest contributor is a **pathological recursive generation artifact** in QA Pilot: `docs/examples/qa-pilot-startup-consistency/test-runs/` contains ~196,000 files in 429 nested directories (up to 62 levels deep) totalling **~1.0 GB**. This is a runaway test-runner output — a single generator bug inflates QA Pilot from ~624 real files (3.5 MB) to 197,000 files (1.0 GB).

The remaining ~300 MB is legitimate project content: governance docs, schemas, scripts, fixtures, receipts, evidence, and operational state.

---

## Artifact Classification

### Category 1 — Human-Authored Governance (Keep as files)

| Project | Count | Size | Description |
|---------|-------|------|-------------|
| Librarian sprint docs | 486 | 4.3 MB | ~97% hand-authored, unique planning records |
| Librarian governance docs | 153 | 1.7 MB | Design specs, protocols, operating modes |
| Librarian schemas | 126 | 792 KB | Canonical JSON Schema definitions |
| QA Pilot sprint docs | 87 | 508 KB | Hand-authored sprint records |
| QA Pilot governance docs | 50 | 356 KB | Architecture and governance docs |
| QA Pilot schemas | 48 | 264 KB | JSON Schema definitions |

**Verdict:** Keep as filesystem-native, Git-tracked Markdown/JSON. These are the authoritative behavioral reference. No changes needed.

---

### Category 2 — Active Configuration/State (May move to DB)

| Project | Count | Size | Description |
|---------|-------|------|-------------|
| Librarian `project-state/` | 11 JSON files | 1.1 MB | Sprint ledger, indexes, tracker data, audit logs |
| QA Pilot `project-state/` | 1 JSON file | 132 KB | Sprint ledger |

**Verdict:** These are operational state files. The project already has a "DB-first" trajectory documented. No immediate action needed — these are the canonical sources today and will naturally migrate to DB storage as part of the existing DB-backfill epics. Keep as filesystem JSON until DB migration completes.

---

### Category 3 — Evidence/History (Indexed, not duplicated)

| Project | Count | Size | Description |
|---------|-------|------|-------------|
| Librarian `receipts/` | 96 files | 396 KB | Owner decisions, custody receipts, closeouts |
| QA Pilot `receipts/` | 55 files | 180 KB | Decision receipts, custody records |
| QA Pilot `data/` | ~124 files | 772 KB | Generated operational records (gitignored) |

**Observations:**
- Librarian `receipts/` has 77 files in `decision-resolutions/` — these are auditable Owner decision records. They should remain as committed evidence.
- QA Pilot `data/` is already gitignored — generated output from script runs. It regenerates deterministically.
- Some QA Pilot `receipts/owner-decision-custody/` files are auto-generated with hash-based filenames (`odcr-*.json`). These are ephemeral runtime artifacts.

**Verdict:** Keep committed receipts as files. The `data/` directory is already correctly gitignored. No changes needed.

---

### Category 4 — Generated Fixtures (Migration candidates)

| Project | Count | Size | Description |
|---------|-------|------|-------------|
| Librarian `fixtures/` | 1,121 files | 6.2 MB | 971 JSON, 83 MD, 32 TXT — hand-crafted test data |
| QA Pilot hand-authored fixtures | 21 files | 88 KB | Small set, well-organized |

**Observations:**
- Librarian's 1,121 fixtures are **hand-crafted test data for validation harnesses**, not auto-generated. They are the authoritative test corpus.
- QA Pilot's fixture directory is modest (21 files, 88 KB). The real "fixture explosion" is the recursive artifact (Category 5).

**Verdict:** Keep as files. These are the canonical test oracles. They are not auto-generated and do not need DB migration.

---

### Category 5 — Pathological/Runaway Artifacts (Cleanup needed)

| Artifact | Count | Size | Description |
|----------|-------|------|-------------|
| QA Pilot `docs/examples/qa-pilot-startup-consistency/test-runs/` | ~196,000 files | ~1.0 GB | Recursive generation bug — 429 nested directories, 62 levels deep |

**Details:** This is a recursive test-runner output from what appears to be `validate-qa-pilot-startup-consistency.py` or a related script. Each test run recursively copied the project directory structure into `test-runs/`, creating a nested chain that photographs the full project at every level. Paths look like:

```
docs/examples/qa-pilot-startup-consistency/test-runs/contradictory_state/
  docs/examples/qa-pilot-startup-consistency/test-runs/all_present/
    ...
```

This inflates QA Pilot from **624 real files (3.5 MB)** to **196,811 files (1.0 GB)**.

**Not currently gitignored.** If this was ever committed, it would bloat the repository.

**Recommendation:** Delete the recursive `test-runs/` directory and add `docs/examples/*/test-runs/` to `.gitignore` to prevent recurrence.

---

### Category 6 — Build/Runtime Artifacts (Clean as needed)

| Artifact | Count | Size | Description |
|----------|-------|------|-------------|
| Librarian `.build/` | 1 directory | 3.1 GB | SwiftPM build cache (debug dSYMs, object files, checkouts) |
| Librarian `__pycache__/` (scripts) | 6 .pyc files | ~25 KB | Compiled Python bytecode |
| QA Pilot `__pycache__/` (scripts) | 2 .pyc files | ~25 KB | Compiled Python bytecode |
| `.DS_Store` files | ~5 found | minimal | macOS metadata |

**Coverage gaps in `.gitignore`:**
- Librarian: `__pycache__/` and `*.pyc` not covered
- QA Pilot: `docs/examples/*/test-runs/` not covered (critical)
- Both: `.DS_Store` patterns work correctly

**Verdict:** Build cache is expected and disposable. Python bytecode is negligible. Add `__pycache__/` and `*.pyc` to Librarian's `.gitignore` for completeness.

---

### Category 7 — Stale/Duplicate/Derived Content

| Artifact | Count | Size | Description |
|----------|-------|------|-------------|
| Librarian `docs 3/` | 3 files | 12 KB | Stale duplicate docs subtree (model-evals only) |
| Librarian `_archive/` | 113 files | 3.7 MB | Historical sprint packs and old assets |
| Librarian `startup_backup_20260602/` | unknown | unknown | Backup directory, not gitignored |

**Verdict:** Low priority. These are small and do not affect daily work. Consider cleaning `docs 3/` (clearly a stale artifact from a rename) and adding `startup_backup_*/` to `.gitignore`.

---

## Summary Table

| # | Class | Count | Size | Keep as Files? | Action |
|---|-------|-------|------|----------------|--------|
| 1 | Human-authored governance | ~950 files | ~8 MB | Yes | No change |
| 2 | Active config/state | ~12 files | ~1.2 MB | Maybe → DB | Migrate per existing DB epics |
| 3 | Evidence/history | ~275 files | ~1.3 MB | Yes | Index committed receipts |
| 4 | Generated fixtures | ~1,142 files | ~6.3 MB | Yes | Hand-authored fixtures are canonical |
| 5 | **Pathological artifact** | **~196,000 files** | **~1.0 GB** | **No** | **Delete + gitignore** |
| 6 | Build artifacts | 1 dir + ~8 files | ~3.1 GB | No | Add `.gitignore` gaps |
| 7 | Stale/duplicate | ~116 files | ~3.7 MB | No | Clean on convenience |

---

## Recommendations (Ranked by Impact)

### Immediate — High Impact

**1. Remove the recursive test-runs artifact and prevent recurrence.**
- Delete `active/qa-pilot/docs/examples/qa-pilot-startup-consistency/test-runs/`
- Add `docs/examples/*/test-runs/` to QA Pilot's `.gitignore`
- Impact: recovers ~1.0 GB and removes ~196,000 files from the project tree
- Risk: very low — fully deterministic generated output

### Before Rust Migration Begins

**2. Add `.gitignore` gaps.**
- Librarian: add `__pycache__/`, `*.pyc`, `startup_backup_*/`
- QA Pilot: add `docs/examples/*/test-runs/`
- Impact: small, prevents future artifacts from being tracked

**3. Clean stale content.**
- Remove Librarian `docs 3/` (clearly a duplicate from a rename)
- Review `_archive/` for what's still needed
- Impact: recovers ~3.7 MB

### During Rust Migration (Epic 0—Behavior Lock)

**4. Snapshot the fixture corpus as the oracle baseline.**
- The ~1,121 Librarian fixtures + ~21 QA Pilot fixtures constitute the behavioral reference for validators
- Ensure `make rust-oracle` can reference these by path without copying them
- No filesystem changes needed — just tooling references

### Longer Term (Post-MVP)

**5. Index committed receipts for faster query.**
- The 173 receipt files across both projects are authoritative but flat on disk
- If query performance becomes an issue, index them rather than duplicating their content elsewhere
- This is naturally handled by the DB migration epics already planned

---

## Oracle Readiness for Rust Migration

The existing fixture corpus is well-structured for use as a Rust migration oracle:

| Requirement | Status |
|-------------|--------|
| Deterministic input data | ✓ Hand-authored JSON fixtures with known-valid and known-invalid cases |
| Expected output defined | ✓ Validator rules (14+ per domain) specify pass/fail criteria |
| No auto-generated drift | ✓ Fixtures are version-controlled, not regenerated |
| Complete coverage | ✓ 1,121 fixtures across all governance domains |

No changes needed to the fixture corpus for Epic 0. The `make rust-oracle` comparison can use the existing filesystem paths.

---

## Appendix: Real Project Size (Excluding Artifacts)

What the projects actually contain when you strip out the recursive artifact and build cache:

| Project | Real Files | Real Size | Real File Count |
|---------|-----------|-----------|-----------------|
| Librarian (source only) | ~6,300 | ~87 MB | 6,306 source files |
| QA Pilot (real content) | ~624 | ~3.5 MB | 624 files |
| **Combined real content** | **~6,900** | **~90 MB** | **~6,900 files** |

The apparent 4.4 GB / 239,000 files is approximately **98% build cache + recursive artifact**. The project itself is compact and well-organized.
