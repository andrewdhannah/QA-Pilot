# ASSURANCE-ADOPTION-LIBRARIAN-BASELINE-1 — Adoption Baseline Report

**Sprint:** #207
**Date:** 2026-07-20
**Status:** 🔍 Pending Owner review
**Epic:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (Phase 1)

---

## Executive Summary

The Librarian can be represented using the existing assurance language, but the mapping is not 1:1. Five of seven assurance model concepts map directly. Two concepts require new abstraction: **evidence pipeline** and **finding lifecycle** — these are QA Pilot-specific artifacts that do not exist in the Librarian project. This is not a failure of the assurance model; it is the boundary between project-specific implementation and universal assurance semantics.

---

## Mapping Assessment

### Direct Mappings (Clean)

| Assurance Concept | Librarian Equivalent | Quality |
|-------------------|---------------------|---------|
| **Project Identity** | `PROJECT-STARTUP.md`, `startup-contract.json` | ✅ Exact match |
| **Sprint History** | `project-state/sprint-ledger.json` (310 sealed) | ✅ Same schema concept |
| **Governance Documents** | `docs/governance/` (40+ files) | ✅ Same pattern |
| **Owner Authority** | Owner decision receipts, seal records | ✅ Same authority model |
| **Receipts / Evidence** | `receipts/` (40 files) | ✅ Analogous concept, different format |

### Partial Mappings (Adapter Needed)

| Assurance Concept | Librarian Equivalent | Gap |
|-------------------|---------------------|-----|
| **Evidence Lineage** | Receipts exist but no `evidence-lineage.json` | Adapter needed: map receipts → evidence freshness |
| **Owner Decision Queue** | Decisions embedded in seal records; no decision-index.json | Adapter needed: extract decision state from sprint ledger |
| **Risk Prioritization** | No explicit risk model | Gap: no equivalent concept in Librarian |
| **Release Readiness** | `RELEASE-GATE.md` exists but different format | Adapter needed: map release gate → readiness profile |

### No Mappings (QA Pilot-Specific)

| Assurance Concept | Status | Classification |
|-------------------|--------|---------------|
| **Finding Lifecycle** | ❌ Does not exist in Librarian | QA Pilot-specific implementation |
| **Evidence Pipeline (EC/EL)** | ❌ Does not exist in Librarian | QA Pilot-specific implementation |
| **Continuous Assurance Loop** | ❌ Does not exist in Librarian | QA Pilot-specific automation |
| **Pipeline Layer Registry** | ❌ Does not exist in Librarian | QA Pilot-specific registry |

---

## Adoption Friction Points

### Friction 1: Sprint Numbering Gap
QA Pilot uses sequential sealed_numbers (1–206). The Librarian uses a different numbering scheme (latest is #529), and its sprint ledger has 310 entries with different structure. **Severity: Low** — the routing layer can normalize sprint identifiers.

### Friction 2: No Evidence Freshness Store
The Librarian has receipts but no evidence-lineage.json or freshness tracking. Evidence freshness would need to be derived from git timestamps or receipt creation dates. **Severity: Medium** — requires a small adapter.

### Friction 3: No Finding/Risk Model
The Librarian does not use the finding lifecycle or risk prioritization models. These are QA Pilot's assurance implementation, not the universal assurance language. The dashboard would show "no data" for these sections, which is handled gracefully by the existing projection layer. **Severity: Low** — the dashboard already supports absent data (CAL-8, PAR-8).

### Friction 4: File Path Convention Differences
Librarian stores project state in `project-state/` but uses different filenames and formats than QA Pilot. **Severity: Medium** — the routing module's `scan_project_assurance()` would need to handle Librarian's file layout.

---

## ABL Gate Results

| Gate | Result |
|------|--------|
| ABL-1: Project identity mapped | ✅ PASS — startup-contract.json maps directly |
| ABL-2: Receipts map to evidence | ✅ PASS — analog concept, format difference documented |
| ABL-3: Lifecycle records map | ⚠️ PARTIAL — sprint ledger maps, finding lifecycle has no equivalent |
| ABL-4: Sprint history maps | ✅ PASS — both use sprint-ledger.json schema |
| ABL-5: Owner authority aligns | ✅ PASS — same Owner authority model |
| ABL-6: Governance traceable | ✅ PASS — governance docs and receipts both present |
| ABL-7: Gaps classified | ✅ PASS — 3 QA Pilot-specific concepts identified |
| ABL-8: No QA Pilot assumptions required | ⚠️ PARTIAL — evidence freshness adapter would reference QA Pilot patterns |
| ABL-9: Adoption effort measured | ✅ PASS — estimated 1-2 adapter sprints |
| ABL-10: Recommendation produced | ✅ PASS — see below |

---

## Adoption Recommendation

**Recommendation: ADAPT — with minor model refinement.**

The assurance language is more general than expected. Five of seven core concepts map directly. The two QA Pilot-specific concepts (finding lifecycle, evidence pipeline) are implementation details, not assurance semantics.

### Required Changes

| Change | Effort | Priority |
|--------|--------|----------|
| Add Librarian path mapping to `scan_project_assurance()` | Small | Required for adoption |
| Create receipt-to-evidence adapter for freshness tracking | Small | Required for evidence section |
| Document that finding/risk/loop sections show "no data" for projects without them | Documentation | Nice-to-have |

### Not Required

- No changes to the assurance model schema
- No project-specific schema forks
- No modifications to Librarian files
- No changes to QA Pilot's existing behavior

---

## Key Insight

The Librarian adoption test reveals that the assurance operating layer's core concepts (identity, sprint history, governance, owner authority, evidence receipts) are genuinely universal. The concepts that do not transfer (finding lifecycle, evidence pipeline, continuous loop) are QA Pilot's internal automation implementation — they are not part of the assurance language.

This is a positive result. It means the model's abstraction boundaries are in the right place.
