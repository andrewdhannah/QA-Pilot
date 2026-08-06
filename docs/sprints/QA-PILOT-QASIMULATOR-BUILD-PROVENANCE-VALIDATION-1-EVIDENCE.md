# QA-PILOT-QASIMULATOR-BUILD-PROVENANCE-VALIDATION-1-EVIDENCE.md

**Produced by:** QA-PILOT-QASIMULATOR-BUILD-PROVENANCE-VALIDATION-1 (ledger #176)
**Date:** 2026-07-20
**Classification:** Advisory assessment evidence — does not authorize implementation

---

## Acceptance Gates

| Gate | Result | Assessment |
|------|--------|------------|
| BP-1 | PASS | Source files identified: `src/os-core.js`, `src/event-bus.js`, `src/compositor.js`, `src/workspaces.js`, `src/health-checks.js`, `src/scoring.js`, `src/keyboard-shortcuts.js`, `os.css`, `desktop/index.html`, `apps/*`, `scenarios/*`, `js/db.js` |
| BP-2 | PASS | build.js confirmed: `node build.js` → QASimulator.html, os.bundle.js, desktop/dist.html + updates capstone-2.html |
| BP-3 | PASS | Build executed: `node build.js` completed with exit code 0 |
| BP-4 | PASS | Regenerated QASimulator.html compared with current — git diff shows NO changes (identical) |
| BP-5 | PASS | **No divergence** — current QASimulator.html is the clean output of the build pipeline |
| BP-6 | PASS | Recommendation: **Outcome A — Active build pipeline** |
| BP-7 | PASS | No product changes made |

**7 PASS, 0 FAIL**

---

## Outcome: A — Active Build Pipeline

```
src/os-core.js
src/event-bus.js
src/compositor.js
src/workspaces.js
src/health-checks.js
src/scoring.js
src/keyboard-shortcuts.js
os.css
desktop/index.html           build.js        QASimulator.html
apps/*               ──>  (node)  ──>  os.bundle.js
scenarios/*                                 desktop/dist.html
js/db.js                                    (capstone-2.html updated)
```

**Build executes cleanly.** Current output matches source. No divergence detected.

---

## Key Findings

### 1. Build.js produces 4 outputs

| Output | Purpose |
|--------|---------|
| QASimulator.html | Canonical self-contained application (773KB) |
| os.bundle.js | Dev bundle for desktop/index.html |
| desktop/dist.html | Desktop deployment copy (auto-regenerated — also a build output) |
| capstone-2.html | Synced with current OS content via getOSContent |

### 2. desktop/dist.html is a build artifact

The build regenerates `desktop/dist.html` automatically. Removing it is ineffective without modifying `build.js` or its deployment strategy. The consolidation decision needs to address the build pipeline, not just the output file.

### 3. capstone-2.html is partially build-generated

The build updates capstone-2.html's `getOSContent` function with the current OS build. This means capstone-2.html is not entirely independent — it has a build-time dependency on the QASimulator source tree.

### 4. No divergence

Current QASimulator.html matches build output. The pipeline is deterministic and reproducible. Source modifications will produce predictable bundle output.

---

## Recommendation

**Proceed with source-level i18n migration.** The build pipeline is active and trustworthy. Modifications should be made to `src/` source files and/or `build.js`, then the build regenerates QASimulator.html.

### Required steps for i18n migration:

| Step | Target | Action |
|------|--------|--------|
| 1 | `src/os-core.js` | Add i18n.js, lang-en.js, lang-fr.js to build.js script list |
| 2 | `build.js` | Include i18n scripts in bundle head section |
| 3 | `src/os-core.js` | Wire visible strings to `__('key')` |
| 4 | `desktop/index.html` | Add `initI18n()` and `renderLangToggle()` calls |
| 5 | `js/lang-en.js`, `js/lang-fr.js` | Add QASimulator keys |
| 6 | Rebuild | `node build.js` |

---

## Scope Compliance

| Check | Result |
|-------|--------|
| Build artifacts modified | None |
| Source files modified | None |
| i18n changes | None |
| Runtime behavior changed | None |

**Scope classification:** Assessment only. Build validation only.

---

**Produced by:** QA-PILOT-QASIMULATOR-BUILD-PROVENANCE-VALIDATION-1 (ledger #176)
**Classification:** Advisory assessment evidence — does not authorize implementation.
