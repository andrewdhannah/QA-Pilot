# QA-PILOT-ASSURANCE-PLATFORM-OPERATIONAL-REVIEW-1 — Assurance Platform Operational Review

**Artifact class:** operational review
**Date:** 2026-07-20
**Status:** Review — no authority change

---

## 1. Evidence Scale

### Current Metrics

| Metric | Value |
|--------|-------|
| Total evidence files | 16 |
| Evidence types | Release, risk, lineage, history, per-profile outputs |
| Storage format | JSON, file-based |
| Largest file | ~50 KB |
| Age of oldest evidence | < 24 hours (all refreshed within session) |

### Scalability Assessment

| Concern | Assessment |
|---------|------------|
| Storage growth over months/years | Low risk — JSON at ~50KB per profile execution is sustainable. A project with daily assurance runs over 2 years produces ~36MB of evidence. |
| Indexing | Not yet needed at current scale. If evidence exceeds 500+ files, a lightweight index (evidence-manifest.json) should be introduced. |
| Archival policy | Not defined. Recommend: archive evidence older than 90 days to compressed storage; retain evidence manifest indefinitely. |
| Retrieval performance | Currently O(n) scan over data/ directory. Acceptable at current scale. For >1000 files, indexing required. |

**Recommendation:** Evidence model is sustainable at current scale. Introduce evidence manifest index when file count exceeds 500.

---

## 2. Multi-Project Operation

### Current Architecture

| Property | Status |
|----------|--------|
| Project isolation | Implicit — data/ directory is project-scoped |
| Profile reuse | Profiles reference capabilities by name; no cross-project isolation |
| Cross-project boundaries | Not yet tested — all work performed within single QA Pilot project |

### Assessment

| Concern | Assessment |
|---------|------------|
| Project isolation | Sufficient for single-project. Multi-project would need project-prefixed evidence paths. |
| Profile portability | Profiles are capability-name based. If capabilities are consistent across projects, profiles can be shared. |
| Librarian integration | Continuous assurance loop (#190) already consumes Librarian context. Multi-project would require project routing. |

**Recommendation:** Architecture supports multi-project but has not been exercised. Profile portability is the strongest feature — capabilities are generic, profiles are configuration. A multi-project pilot would validate the isolation model.

---

## 3. Human Workflow

### Current Decision Surfaces

| Surface | Format | Owner Action |
|---------|--------|--------------|
| Release readiness | `data/release-readiness-evidence.json` | Review, decide |
| Risk prioritization | `data/risk-prioritization-evidence.json` | Review HIGH ATTENTION items |
| Assurance history | `data/assurance-history.json` | Audit, traceability |
| Release governance | `data/release-governance-evidence.json` | Decision package |

### Gaps

| Gap | Impact | Mitigation |
|-----|--------|------------|
| No unresolved finding queue | Owner must manually re-read full reports | Add finding queue with acknowledgment status |
| No escalation time tracking | Cannot measure finding age | Add escalation timestamp to findings |
| No Owner acknowledgment receipt | Cannot prove Owner reviewed evidence | Add Owner acknowledgment field (manual, not automatic) |
| No finding retirement workflow | Findings accumulate without resolution | Add finding lifecycle: open → acknowledged → resolved → archived |

**Recommendation:** The evidence model is complete. The missing layer is Owner workflow — acknowledgment, resolution tracking, and finding lifecycle. This is the highest-value human experience improvement.

---

## 4. Model Governance

### Current Model-Assisted Architecture

| Property | Status |
|----------|--------|
| Model role | Proposes insights — never decides |
| Validation layer | QA Pilot validates model output before evidence |
| Provenance | Model-generated suggestions are labeled as such |
| Confidence handling | Not yet implemented — all model output treated equally |

### Governance Requirements

| Requirement | Status |
|-------------|--------|
| Model version tracked | ⚠️ Not yet implemented |
| Model output labeled as non-authoritative | ✅ Always advisory |
| Owner can distinguish model vs capability evidence | ✅ Model evidence has distinct classification |
| Model can be disabled independently | ⚠️ Not yet — no feature flag |
| Evaluation fixtures for model output | ⚠️ Not yet created |

**Recommendation:** Add model version tracking to evidence provenance. Add feature flag for model-assisted suggestions. Create evaluation fixtures if model output is used for automated decisions (currently it is not — all model output is manually reviewed).

---

## 5. Product Boundary

### Current Role

QA Pilot currently functions as an **internal assurance capability** of the broader governance framework (Librarian + QA Pilot). It is not a standalone product — it requires project context and Librarian evidence history for full operation.

### Options

| Option | Commitment | Viability |
|--------|-----------|-----------|
| Internal capability | Low — continue current model | ✅ Current state |
| Standalone product | High — separate packaging, distribution, documentation | ⚠️ Possible but would require extraction from Librarian context |
| Platform component | Medium — reusable assurance module | ✅ Strongest alignment with architecture |

### Recommendation

QA Pilot should remain an **internal assurance capability** of the governance framework. The strongest use case is as a reusable assurance module that consumes Librarian context and produces evidence for Librarian custody. Standalone productization would require significant investment in project-agnostic packaging, configuration, and documentation that would not immediately improve the current project's assurance posture.

---

## 6. V2 Priority Recommendations

| Priority | Area | Action |
|----------|------|--------|
| 1 | Owner workflow | Add finding lifecycle (open → acknowledged → resolved), acknowledgment queue, escalation timestamps |
| 2 | Evidence indexing | Add evidence manifest when file count approaches 500 |
| 3 | Model governance | Track model version, add feature flag, create evaluation fixtures |
| 4 | Multi-project pilot | Test profile portability across project boundaries |
| 5 | Scale archiving | Define 90-day archive policy for evidence retention |

---

**Classification:** Operational review — no authority change.
