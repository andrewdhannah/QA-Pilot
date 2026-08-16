# E8-R Full Corpus Reproducibility — Governance Report

**Audit ID:** E8-R
**Domain:** regression
**Direction:** QA-Pilot Runner → Librarian (frozen 307-test corpus, two runs)
**Timestamp:** 2026-08-11T06:00:00Z
**Status:** COMPLETE

---

## Audit Status: COMPLETE

E8-R proves that the full 307-test historical assurance corpus produces mechanically reproducible results across multiple runs.

---

## Results

| Metric | Run A | Run B | Match |
|--------|-------|-------|-------|
| Corpus size | 307 | 307 | ✓ |
| Executed | 307 | 307 | ✓ |
| PASS | 228 | 228 | ✓ |
| FAIL | 79 | 79 | ✓ |
| ERROR | 0 | 0 | ✓ |

---

## Structural Reproducibility

| Comparison | Result |
|---|---|
| Corpus hash | c9b7a99be34ab7abe0811cf54c5e4303... |
| Test IDs | ✓ MATCH |
| Requirements | ✓ MATCH |
| Source sprints | ✓ MATCH |
| Execution counts | ✓ MATCH |
| Result schema | ✓ MATCH |

---

## Observational Reproducibility

| Metric | Run A | Run B | Match |
|---|---|---|---|
| PASS | 228 | 228 | ✓ |
| FAIL | 79 | 79 | ✓ |
| Individual divergences | — | — | 0 |

**Full observational MATCH**

---

## Reconciliation: 149 vs 307

| Source | Count | Scope |
|---|---|---|
| E2E-4 | 149 | Bounded planning sample (first 50 sprints) |
| E2E-8 | 307 | Full historical expansion (all 122 ASSURANCE_READY sprints) |
| E8-R | 307 | Reproducibility run of E2E-8 corpus |

The 149 requirements from E2E-4 were a bounded planning sample. The 307 requirements from E2E-8 represent the full extraction from all 122 ASSURANCE_READY sprints. E8-R confirms the 307-test corpus is reproducible.

---

## What E8-R Proves

```
E2E-8
307 requirements
      ↓
307 test artifacts
      ↓
FREEZE
      │
      ├───────────────┐
      ▼               ▼
    RUN A            RUN B
      │               │
      ▼               ▼
   228 PASS        228 PASS
    79 FAIL         79 FAIL
      │               │
      └───────┬───────┘
              ▼
       E8-R comparison
       MATCH (0 divergences)
```

The 79 failures are properties of the observed system, not execution noise.

---

## The 79 FAILs Are Now the Most Valuable Artifact

Each FAIL represents:

| Field | Content |
|---|---|
| Source sprint | Which Librarian sprint |
| Historical claim | What Librarian claimed |
| Requirement | What QA-Pilot derived |
| Observed behavior | What actually happened |
| Expected behavior | What the assertion required |
| Evidence | Execution record |
| Reproducibility | Confirmed across 2 runs |

These 79 discrepancies are now a structured corpus for governance classification:

- HISTORICAL_CLAIM_NOT_OPERATIONAL
- INTENTIONAL_BEHAVIOR_CHANGE
- REGRESSION
- TEST_CONSTRUCTION_DEFECT
- ENVIRONMENT_DEPENDENT
- EVIDENCE_INSUFFICIENT

---

## State

```
E2E-1:  Governance substrate       ✓
E2E-2:  Runtime/API substrate      ✓
E2E-3:  Browser substrate          ✓
E2E-4:  Assurance discovery        ✓ (reconstruct)
E2E-5:  Agent test construction    ✓ (construct)
E2E-6:  Constructed-test execution ✓ (execute)
E2E-7:  Reproducibility            ✓ (reproduce)
E2E-8:  Full historical assurance  ✓ (scale)
E8-R:   Full corpus reproducibility ✓ (reproduce full)

Next:    Failure classification → Assurance Corpus v1
```

---

## QA-Pilot Assurance Corpus v1 — Ready to Freeze

After failure classification, the following will be frozen:

```
QA-PILOT ASSURANCE CORPUS v1
├── Source Manifest
├── 307 Requirements
├── Test Plans
├── 307 Test Artifacts
├── Execution Records
├── Evidence
├── Reproducibility Record
└── 79 Discrepancy Records
```

---

## SHA-256 Integrity

```
E8-R-EXEC-001: 950df7626ec5d753f37d501ba260d2156ccda7685aab4978f5f1bd2f4c99a0a6
```

---

## Advisory Notice

This report is advisory-only. It does not confer authority, seal, or approval.
All findings are 🔍 Pending Owner review.
QA Pilot ≠ Authority.
