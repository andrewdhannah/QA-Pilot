# QA Pilot Continuous Validation Pipeline — QA-PILOT-CONTINUOUS-VALIDATION-PIPELINE-1

**Sprint:** QA-PILOT-CONTINUOUS-VALIDATION-PIPELINE-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review
**Authority:** Advisory only. Pipeline produces validation packages for owner review. Does not approve, seal, or authorize releases.

## 1. Purpose

Automate the validation lifecycle. Turn QA-Pilot from a manually-run framework into a continuous assurance pipeline that triggers on new work orders, selects applicable tests, executes through adapters, and produces validation packages for owner review.

## 2. Pipeline Architecture

```
Trigger (manual, cron, or webhook)
    │
    ▼
Contract Compatibility (15 rules)
    │
    ▼
SDK Health Check
    │
    ▼
Test Selection by Domain
    │
    ├── regression
    ├── security
    ├── uat
    ├── accessibility
    ├── ai
    └── (future: performance, compliance)
    │
    ▼
Test Execution (all selected tests)
    │
    ▼
Validation Package
    │
    ├── pipeline-result.json
    ├── pipeline-summary.md
    └── per-domain results
    │
    ▼
Owner Review
```

## 3. Pipeline Commands

| Command | Purpose |
|---|---|
| `--list-domains` | List available test domains with counts |
| `--quick` | Quick check: contracts + SDK only |
| `--status` | Show last pipeline run status |
| `--domains <list>` | Run specific domains (e.g. `regression,security`) |
| `--project <path>` | Validate a specific project path |
| `(no args)` | Full validation run across all populated domains |

## 4. Pipeline Results

| Metric | Value |
|--------|-------|
| Pipeline version | `qa-pilot-continuous-pipeline-v1` |
| Compatibility rules | 15 (10 PC + 5 LC) |
| Populated domains | 5 (regression, security, UAT, accessibility, AI) |
| Test count | 16 governed tests |
| Run types | Full, quick, selected domains |
| History | All runs saved to `data/pipeline/history/` |

## 5. Files

| File | Description |
|---|---|
| `scripts/qa-pilot-pipeline.sh` | Continuous validation pipeline (bash) |
| `scripts/test-qa-pilot-pipeline.sh` | 8 tests (8/8 pass) |
| `docs/governance/QA-PILOT-CONTINUOUS-VALIDATION-PIPELINE-1.md` | This governance document |
| `data/pipeline/last-run.json` | Most recent pipeline status |
| `data/pipeline/history/` | All pipeline run history |
| `*/validation-package/*/` | Per-run validation packages |

## 6. Key Invariants

| Invariant | Enforced By |
|---|---|
| Advisory only | `provenance.advisory: true` in every result |
| No authority conferred | `provenance.no_authority_conferred: true` |
| No automatic approvals | All results require owner review |
| Test library validation | TL-1 through TL-7 rules pass before execution |

## 7. QA-Pilot Complete State

| Phase | Work Orders | Status |
|---|---|---|
| Infrastructure Boundary | 4 | ✅ |
| Teaching Capability | 5 | ✅ |
| Qualification | 1 | ✅ |
| Portability | 1 | ✅ |
| Production Hardening | 1 | ✅ |
| Operational Proof | 1 | ✅ |
| Governance Maintenance | 1 | ✅ |
| Expansion | 1 | ✅ |
| External Pilot | 1 | ✅ |
| Test Domain Expansion | 1 | ✅ |
| **Continuous Pipeline** | **1** | **✅ ← Complete** |
| **Total** | **19** | **All sealed** |
