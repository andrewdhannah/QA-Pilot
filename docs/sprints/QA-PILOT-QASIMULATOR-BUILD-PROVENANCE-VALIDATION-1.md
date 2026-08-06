# QA-PILOT-QASIMULATOR-BUILD-PROVENANCE-VALIDATION-1 — QASimulator Build Provenance Validation

**Type:** assessment / build pipeline verification
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** assessment
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Dependencies:** #175 sealed (app module audit); Owner decision: QASimulator MIGRATE authorized

---

## Purpose

Determine whether QASimulator.html is the output of an active, reproducible build pipeline or a stale/diverged bundle. This must be resolved before any i18n migration can begin — modifying a build artifact directly risks divergence between source and generated output.

---

## Scope

### Included

| # | Area | Action |
|---|------|--------|
| 1 | Source inventory | Identify all source files contributing to QASimulator bundle |
| 2 | Build pipeline | Confirm `build.js` inputs and outputs |
| 3 | Clean build | Execute build in test environment |
| 4 | Output comparison | Compare regenerated output with current QASimulator.html |
| 5 | Divergence analysis | Determine source/bundle divergence state |
| 6 | Recommendation | Produce migration approach recommendation |

### Build Artifacts to Validate

```
src/  ──>  build.js  ──>  QASimulator.html
  ?                         ?
os-core.js                  desktop/dist.html
os.bundle.js                
health-checks.js            
scoring.js                  
```

### Explicit Non-Scope

This sprint must not:

- Modify any build artifact
- Wire i18n in source or bundle
- Modify build.js
- Change runtime behavior
- Migrate capstone-2

---

## Decision Outcomes

The sprint must produce one of:

**Outcome A — Active build pipeline**

```
src/ → build.js → QASimulator.html
```

Recommendation: Proceed with source-level i18n migration. Modify source files, rebuild.

**Outcome B — Stale/diverged bundle**

```
src/ ✗ build.js ✗ QASimulator.html
```

Recommendation: Decide whether to restore build pipeline or treat bundle as independent legacy artifact.

**Outcome C — Hybrid**

Infrastructure exists but full wiring deferred. Only after knowing whether the build output is trustworthy.

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| BP-1 | Source files contributing to bundle identified |
| BP-2 | Build.js inputs and outputs confirmed |
| BP-3 | Build executed in clean environment |
| BP-4 | Regenerated output vs current QASimulator.html compared |
| BP-5 | Source/bundle divergence determined |
| BP-6 | Migration recommendation produced |
| BP-7 | No product changes made |

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Authorized by:** Andrew Hannah
**Ledger entry:** #176 (authorized)
