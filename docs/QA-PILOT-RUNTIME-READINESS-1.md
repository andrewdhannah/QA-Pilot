# QA-PILOT-RUNTIME-READINESS-1 — Runtime Readiness Audit

**Date:** 2026-08-11
**Audit scope:** Can QA-Pilot operate as a standalone testing system today?
**Classification:** Audit only — no implementation changes.

---

## Executive Summary

**QA-Pilot is runnable as a standalone browser-based testing system for its course platform.** A clean clone can open HTML test files in a browser and execute 165 pre-commit tests with zero external dependencies.

**QA-Pilot is NOT ready to be a governed testing node.** Test results exist only in the browser DOM, there is no CLI runner, no structured output, no environment provenance, and no programmatic interface.

The gap between "standalone test system" and "governed testing node" is substantial but well-defined.

---

## Area 1: Runnable

**Question:** Can a clean machine clone it and execute a test without Librarian?

### Findings

| # | Finding | Classification |
|---|---------|----------------|
| 1.1 | Platform code (`platform/`) is fully self-contained — zero external dependencies, no ES modules, no fetch(), no CDN, no server required | **READY** |
| 1.2 | Pre-commit test suites (P1+P2+P3+Q2-C+MS-13I = 165 tests) have no Librarian dependency | **READY** |
| 1.3 | Platform runs from `file://` — confirmed in `db.js` header and `FILE-COURSE-RUNTIME-SPEC.md` | **READY** |
| 1.4 | README setup: "Open the following files in a browser" — no install, no build, no dependencies | **READY** |
| 1.5 | MS-13H import test uses `XMLHttpRequest` — requires Chrome with `--allow-file-access-from-files` | **FIX** |
| 1.6 | `test-library/` JSON definitions reference Librarian scripts/fixtures that don't exist inside qa-pilot/ | **BLOCKED** |
| 1.7 | `test-runner.html` footer references `TheLibrarian/TEST-RUNBOOK.md` — documentation in another repo | **BLOCKED** |
| 1.8 | No CLI runner, no headless execution, no CI integration — all tests require manual browser-open | **FIX** |

### Verdict

The course platform and its pre-commit tests are standalone. The test-library definitions and test-runbook are not.

---

## Area 2: Test Definition

**Question:** Is there a canonical format for describing a test?

### Findings

| # | Finding | Classification |
|---|---------|----------------|
| 2.1 | Two test libraries exist with different schemas: `qa-pilot/test-library/` (implicit, 15 tests) and `active/qa-pilot/test-library/` (formal JSON Schema, 16 tests) | **FIX** |
| 2.2 | Formal JSON Schema exists at `active/qa-pilot/docs/schemas/qa-test-definition.schema.json` — enforces `advisory_only: true` and `no_seal_authority: true` as const | **READY** |
| 2.3 | Course packs follow `course-pack-v1` schema — fully documented, validated, self-contained | **READY** |
| 2.4 | Browser tests (`scripts/test-*.html`) have ad-hoc inline format — no canonical schema, each file is a bespoke harness | **FIX** |
| 2.5 | `test-library/` definitions are governance/compliance metadata, not executable test specs | **FUTURE NODE** |
| 2.6 | `active/qa-pilot/test-library/` tests reference SDK methods and contracts, not file-system fixtures | **FUTURE NODE** |

### Two Test Libraries

| Aspect | `qa-pilot/test-library/` | `active/qa-pilot/test-library/` |
|--------|--------------------------|----------------------------------|
| Schema | Implicit (no formal schema) | Formal JSON Schema (draft 2020-12) |
| ID pattern | Mixed (`A11Y-WCAG-001`, `EP-REG-001`) | Standardized (`REG-001`, `SEC-001`) |
| Governance flags | None | `advisory_only: true`, `no_seal_authority: true` |
| External deps | Heavy (scripts, fixtures, baselines) | Moderate (SDK methods, contracts) |
| Tests | 15 | 16 |
| Purpose | Compliance evidence definitions | Governed regression/security/uat definitions |

### Verdict

A formal schema exists but is not used by the browser-based test suites. The two libraries serve different purposes (compliance metadata vs. governed test definitions) and are not interchangeable.

---

## Area 3: Runner

**Question:** Is execution deterministic and isolated?

### Findings

| # | Finding | Classification |
|---|---------|----------------|
| 3.1 | Pre-commit suites clear IndexedDB at start (`_clear()` / `resetDatabase()`) — deterministic for sequential runs | **READY** |
| 3.2 | MS-13H runtime test depends on import test state — not self-contained | **FIX** |
| 3.3 | No cross-suite isolation — all tests share same `qa_pilot_v2` IndexedDB (origin-scoped) | **FIX** |
| 3.4 | Inconsistent cleanup — P1/P2/MS-13I clean up, Q2-C/MS-13H do not | **FIX** |
| 3.5 | No `run-startup-checks.sh` or CLI runner exists — all tests are HTML files | **MISSING** |
| 3.6 | No headless browser integration (Puppeteer, Playwright) | **MISSING** |

### Test Tier Structure

| Tier | File | Tests | Layer | Self-Contained? |
|------|------|-------|-------|-----------------|
| P1 | test-smoke.html | 53 | db.js storage + validation | YES |
| P2 | test-p2-smoke.html | 53 | course-loader.js compat | YES |
| P3 | test-p3-smoke.html | 20 | admin UI logic | YES |
| Q2-C | test-q2c-persistence.html | 7 | quiz persistence | YES |
| MS-13I | test-ms13i-regression.html | 32 | runtime hardening | YES |
| MS-13H | test-ms13h-import.html | 79 | import course packs | Needs XHR |
| MS-13H | test-ms13h-runtime.html | ~66 | end-to-end runtime | Needs import first |

**Pre-commit set:** P1+P2+P3+Q2-C+MS-13I = **165 tests** (self-contained)
**Full regression:** + MS-13H = **~310 tests** (not fully self-contained)

### Verdict

The pre-commit set is deterministic for sequential manual runs. The full regression set has state dependencies and no automation.

---

## Area 4: Evidence

**Question:** Are raw outputs preserved, rather than only pass/fail summaries?

### Findings

| # | Finding | Classification |
|---|---------|----------------|
| 4.1 | Browser tests render results as DOM elements — no structured output | **FIX** |
| 4.2 | No evidence storage mechanism — results exist only in browser tab | **MISSING** |
| 4.3 | `.gitignore` lists `screenshots/`, `test-output/`, `coverage/` — planned but never created | **MISSING** |
| 4.4 | `VP-EVIDENCE-PLANE-001.json` is a validation package with structured test results — but it's a one-off, not a systemic output format | **FIX** |
| 4.5 | Validation packages include provenance (`generated_at`, `generator`) — format is sound | **READY** |

### Current Output Format

```
Browser DOM:
  ✅ P1: Storage & Validation (53/53 passed)
  ✅ P2: Course Loader Compat (53/53 passed)
  ...
  🎉 All 53 tests passed
```

### What a Testing Node Would Need

```json
{
  "suite_id": "P1-SMOKE",
  "executed_at": "2026-08-11T01:00:00Z",
  "environment": {
    "browser": "Chrome 136",
    "os": "macOS 15.5",
    "platform_commit": "abc123"
  },
  "results": [
    {"test_id": "P1-001", "name": "validateCoursePack valid", "status": "pass", "duration_ms": 12},
    {"test_id": "P1-002", "name": "validateCoursePack missing id", "status": "fail", "detail": "..."}
  ],
  "summary": {"total": 53, "passed": 52, "failed": 1}
}
```

### Verdict

No machine-readable evidence is produced. The validation package format is sound but not connected to the browser test execution.

---

## Area 5: Identity

**Question:** Can we identify exactly what was tested, where, and with what configuration?

### Findings

| # | Finding | Classification |
|---|---------|----------------|
| 5.1 | Course packs have `version` field (semver) — version tracked | **READY** |
| 5.2 | Test definitions have `test_id` but no version field | **FIX** |
| 5.3 | No environment metadata in test results (browser, OS, date, commit) | **MISSING** |
| 5.4 | No platform code version tracking in test output | **MISSING** |
| 5.5 | Validation packages have `generated_at` and `generator` — provenance format exists | **READY** |

### Verdict

Identity is partially tracked for course packs and validation packages, but not for browser test execution. There is no way to determine what version of the platform was tested, in what environment, at what time.

---

## Area 6: Node Boundary

**Question:** What would eventually need to become the QA-Pilot testing-node contract?

### Inputs (what a node would receive)

| Input | Current State | Required for Node |
|-------|--------------|-------------------|
| Test specification | Two schemas exist (implicit + formal) | Single canonical schema |
| Platform code | `platform/` directory (self-contained) | Same |
| Course packs | `course-packs/` directory (13 packs) | Same |
| Browser environment | Manual | Automated (headless) |

### Outputs (what a node would produce)

| Output | Current State | Required for Node |
|--------|--------------|-------------------|
| Test results | DOM-only, not persisted | Structured JSON with pass/fail/detail/duration |
| Evidence | None | Raw outputs + environment metadata + provenance |
| Report | HTML summary banner | QA-Pilot Report (structured, machine-readable) |
| Receipt | None | Execution receipt for Librarian consumption |

### Interfaces (what a node would expose)

| Interface | Current State | Required for Node |
|-----------|--------------|-------------------|
| Test execution | Browser-only, manual | CLI or headless API |
| Result query | None | Structured result access |
| Status check | None | Readiness/health endpoint |

### Node Contract (eventual)

```json
{
  "contract_schema": "qa-testing-node-v1",
  "node_id": "qa-pilot",
  "capabilities": ["test_execution", "evidence_collection", "report_generation"],
  "inputs": {
    "test_specification": "qa-test-definition-v1",
    "platform_code": "directory",
    "course_packs": "directory"
  },
  "outputs": {
    "test_results": "structured JSON",
    "evidence": "raw outputs + environment + provenance",
    "receipt": "execution receipt for Librarian"
  }
}
```

### Classification: **FUTURE NODE** — the interface does not exist yet

---

## Summary Classification

| Classification | Count | Items |
|---------------|-------|-------|
| **READY** | 10 | Platform self-contained, file:// safe, pre-commit tests runnable, course pack schema, IndexedDB clearing, validation package format, course pack versioning, provenance format |
| **FIX** | 9 | MS-13H XHR, no CLI runner, two test libraries, ad-hoc test format, MS-13H state dependency, no cross-suite isolation, inconsistent cleanup, DOM-only output, test definition versioning |
| **BLOCKED** | 2 | test-library/ references Librarian artifacts, test-runbook in Librarian repo |
| **MISSING** | 6 | CLI/headless runner, evidence storage, environment metadata, platform version tracking, headless browser integration |
| **FUTURE NODE** | 4 | test-library JSON schema as executable, SDK-oriented tests, evidence collection pipeline, testing-node interface |
| **NOT REQUIRED** | 1 | README external references |

---

## Minimum Changes for Standalone Testing

To make QA-Pilot a usable standalone testing system (not yet a node):

| Priority | Change | Why |
|----------|--------|-----|
| **P1** | Add structured JSON output to browser test harness | Results must be machine-readable |
| **P1** | Add environment metadata to test results | Provenance is required for evidence |
| **P2** | Unify the two test libraries under the formal schema | Eliminate confusion about which is canonical |
| **P2** | Make MS-13H tests self-contained (embed test data) | Remove state dependency |
| **P3** | Add a simple CLI runner (shell script + headless Chrome) | Enable automation |

## What NOT to Build Yet

- Do not build the testing-node contract
- Do not build Librarian integration
- Do not build evidence pipeline
- Do not build compliance reporting
- Do not refactor tests to use a test framework (Mocha, Jest, etc.)

## Platform Assumptions

| Assumption | Verified? |
|------------|-----------|
| Modern browser with IndexedDB | YES |
| Chrome with `--allow-file-access-from-files` (for MS-13H) | Recommended |
| No server required | YES |
| No Node.js required | YES |
| No npm/yarn required | YES |
| file:// protocol works | YES |
