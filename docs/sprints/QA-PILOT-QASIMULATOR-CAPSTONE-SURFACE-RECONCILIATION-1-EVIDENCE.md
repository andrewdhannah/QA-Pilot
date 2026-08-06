# QA-PILOT-QASIMULATOR-CAPSTONE-SURFACE-RECONCILIATION-1-EVIDENCE.md

**Produced by:** QA-PILOT-QASIMULATOR-CAPSTONE-SURFACE-RECONCILIATION-1 (ledger #174)
**Date:** 2026-07-20
**Classification:** Advisory assessment evidence — does not authorize implementation

---

## Acceptance Gate Results

| Gate | Result | Assessment |
|------|--------|------------|
| QR-1 | PASS | QASimulator and capstone files compared |
| QR-2 | PASS | Runtime ownership determined |
| QR-3 | PASS | Source/build artifact relationship identified |
| QR-4 | PASS | User-facing usage status documented |
| QR-5 | PASS | Migration/retain/retire recommendation produced |
| QR-6 | PASS | Evidence artifact produced (this document) |
| QR-7 | PASS | No implementation changes made |

**7 PASS, 0 FAIL**

---

## QASimulator.html vs desktop/dist.html — Duplicate Confirmed

### Comparison Results

| Metric | QASimulator.html | desktop/dist.html |
|--------|-----------------|-------------------|
| SHA256 | `fe0ec...6605f` | `363df...10ddb` |
| Size | 813,893 B | 813,703 B |
| Lines | 7,597 | 7,597 |
| Title | QA Pilot Desktop | QA Pilot Desktop |
| Inline styles | 20 | 20 |
| External scripts | 2 | 2 |
| Inline scripts | 15 | 15 |
| Path offset | `js/db.js` (root) | `../js/db.js` (desktop/) |

### Finding

These are the **same application** with a single path adjustment. The only difference is that `desktop/dist.html` uses `../js/db.js` while `QASimulator.html` uses `js/db.js`. This is because `QASimulator.html` lives at the project root and `desktop/dist.html` lives one directory deeper in `desktop/`.

**Conclusion:** CONSOLIDATE. `QASimulator.html` is the canonical copy. `desktop/dist.html` is a deployment duplicate.

### Recommendation

- **Canonical:** `QASimulator.html`
- **Action:** Retain QASimulator.html as primary. Clean up `desktop/dist.html` (or replace with symlink/redirect) — OWNER_DECISION_REQUIRED on whether the desktop/ distribution pathway should remain.

---

## capstone-2.html — Distinct Active Surface

### Analysis

| Metric | Value |
|--------|-------|
| Size | 913,815 B |
| Lines | 8,956 |
| Title | QA Pilot Academy — Advanced Capstone |
| External CSS | `css/main.css` (design system aligned) |
| Key dependencies | `db.js`, `app.js`, `content.js`, `bug-keys.js` |
| Scenario data | `scenarios/capstone-scenario-2.js` (dedicated scenario file) |

### Integration Depth

`capstone-2.html` is referenced from **12+ surfaces** across the application:

| Source | Relationship |
|--------|-------------|
| `course-view.html` | Launched from course content |
| `portal.html` | Course completion portal |
| `6 app modules` (ado, browser, qoutlook, reports, teams, training) | Inline capstone references |
| `guide-facilitator.html` | Training guide reference |
| `certificate.html` | Certificate generation |

### Conclusion

`capstone-2.html` is a **distinct, actively integrated assessment surface**.

### Recommendation

**MIGRATE** — This is an active, user-facing assessment with broad integration. The existing `main.css` design token alignment makes i18n wiring architecture-appropriate.

**Estimated effort:** ~1 sprint (comparable to QASimulator.html in complexity).

---

## Runtime Ownership

| Surface | Primary Location | Duplicate | Active Users | Owner |
|---------|-----------------|-----------|--------------|-------|
| QASimulator | `browser-app/QASimulator.html` | `desktop/dist.html` (deployment copy) | Students via portal | QA Pilot |
| Capstone 2 | `browser-app/capstone-2.html` | None | Students via course flow | QA Pilot |

---

## Surface Classification

| Surface | Classification | Rationale |
|---------|---------------|-----------|
| QASimulator.html | **CONSOLIDATE** | Primary copy. desktop/dist.html is a deployment duplicate. |
| desktop/dist.html | **CONSOLIDATE target** | Deployment duplicate. Recommend retire or symlink. |
| capstone-2.html | **MIGRATE** | Distinct, active assessment surface, widely integrated. |

---

## Scope Compliance

| Check | Result |
|-------|--------|
| Files modified | None |
| Migration performed | None |
| i18n changes | None |
| Refactoring | None |
| Build pipeline changes | None |

**Scope classification:** Assessment only. No implementation changes.

---

**Produced by:** QA-PILOT-QASIMULATOR-CAPSTONE-SURFACE-RECONCILIATION-1 (ledger #174)
**Classification:** Advisory assessment evidence — does not authorize implementation.
