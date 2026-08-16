# E2E-1 Librarian Runtime Audit — Governance Report

**Audit ID:** E2E-1
**Domain:** regression
**Direction:** QA-Pilot → Librarian
**Timestamp:** 2026-08-11T04:25:40.609549+00:00
**Status:** COMPLETE

---

## Audit Status: COMPLETE

| Metric | Run 1 (Before) | Run 2 (After) |
|--------|----------------|---------------|
| Total requirements | 10 | 10 |
| Executable | 8 | 8 |
| PASS | 5 | **8** |
| FAIL | 3 | **0** |
| CAPABILITY_MISSING | 2 | 2 |
| Coverage | 50.0% | **80.0%** |
| Status | INCOMPLETE | **COMPLETE** |

## Conclusion

All 3 Librarian defects remediated. All 8 executable tests pass.
Two capability gaps remain (LINK identity, MCP dispatch) — these require
MCP/API capability that is deliberately not built yet.

The audited Librarian boundary is now verified for the executable surface.
CAPABILITY_MISSING requirements correctly produce no conclusion.

---

## Remediation Proof

### Evidence Structure

```
E2E-1 / Run 1 (immutable baseline)
       │
       ├── 5 PASS
       ├── 3 FAIL
       └── 2 CAPABILITY_MISSING
             │
             ▼
      Governance Report
             │
             ▼
      SHA-256 aggregate

E2E-1 / Run 2 (remediation proof)
       │
       ├── 8 PASS
       ├── 0 FAIL
       └── 2 CAPABILITY_MISSING
             │
             ▼
      Governance Report
             │
             ▼
      SHA-256 aggregate
```

### Before/After Verification Trail

#### Before State (E2E-1 Run 1)

```
E2E-1 Run 1: 2026-08-11T03:37:25.885708+00:00
  PASS:              5
  FAIL:              3
  CAPABILITY_MISSING: 2
  Coverage:          50.0%
  Status:            INCOMPLETE
```

#### After State (E2E-1 Run 2)

```
E2E-1 Run 2: 2026-08-11T04:25:40.609549+00:00
  PASS:              8
  FAIL:              0
  CAPABILITY_MISSING: 2
  Coverage:          80.0%
  Status:            COMPLETE
```

### Librarian Fixes Applied

| Finding | Fix | Owner Decision |
|---------|-----|----------------|
| E2E-1-FIND-001 | Aligned pointer schema to `project_id` as canonical field | `project_id` is canonical |
| E2E-1-FIND-002 | Fixed validator to resolve from workspace boundary (4 levels up) | No — implementation fix |
| E2E-1-FIND-003 | Removed scrum-tracker and runtime-node (incomplete); fixed working-bibliography-extension contract | Removed incomplete, fixed valid |

---

## Evidence Inventory

| Evidence ID | Type | Description | Status |
|-------------|------|-------------|--------|
| E2E-1-EXEC-001 | execution_record | Test execution results for all 10 requirements | Updated (Run 2) |
| E2E-1-FIND-001 | finding | Pointer contract mismatch — field name drift | **Remediated** |
| E2E-1-FIND-002 | finding | Selector routing path bug — validator path resolution | **Remediated** |
| E2E-1-FIND-003 | finding | Contract reconstruction — incomplete startup metadata | **Remediated** |
| E2E-1-CAPGAP-001 | capability_gap | MCP/API capability missing for LINK identity validation | Open (by design) |
| E2E-1-CAPGAP-002 | capability_gap | MCP/API capability missing for MCP dispatch identity validation | Open (by design) |

## Findings

### E2E-1-FIND-001: Pointer Contract Mismatch — REMEDIATED

**Severity:** violation
**Classification:** fail → **pass**

**Run 1:** Workspace `.librarian/current-project.json` uses `project_id` but `validate-startup-registry-selection.py` expects `active_project_id`. Cross-component contract drift.

**Remediation:** Updated `validate-startup-registry-selection.py` (Librarian copy) to accept `project_id` as the canonical field. `active_project_id` is retained as legacy fallback. Updated E2E-1 test to accept `project_id` as canonical.

**Invariant restored:** Pointer field names are consistent between producer and consumer. One canonical field (`project_id`), not two.

### E2E-1-FIND-002: Selector Routing Path Bug — REMEDIATED

**Severity:** violation
**Classification:** fail → **pass**

**Run 1:** `validate-startup-selector-routing.py` computed `PROJECT_INDEX` relative to its own file location (`active/librarian/`) rather than resolving from the workspace boundary.

**Remediation:** Fixed `WORKSPACE_ROOT` to resolve 4 levels up from file location: `Path(__file__).resolve().parent.parent.parent.parent` → workspace root `CarbideFrame/`.

**Invariant restored:** Validators resolve paths from workspace boundary, not from validator file location.

### E2E-1-FIND-003: Contract Reconstruction Gaps — REMEDIATED

**Severity:** violation
**Classification:** fail → **pass**

**Run 1:** Three projects had incomplete startup metadata:
- `scrum-tracker`: `startup_contract` is null, deprecated, directory doesn't exist
- `runtime-node`: `startup_contract` is null, startup_capable=false
- `working-bibliography-extension`: contract missing `contract_schema` and `project_name`

**Remediation:**
- `scrum-tracker`: Removed from workspace-level project-index.json (deprecated, directory doesn't exist on disk)
- `runtime-node`: Removed from workspace-level project-index.json (startup_capable=false, no startup contract)
- `working-bibliography-extension`: Added `contract_schema: "startup-contract-v1"` and `project_name: "Working Bibliography Extension"` to startup contract

**Invariant restored:** Every registered project has complete startup metadata for deterministic reconstruction. No entry is registered but incapable of startup.

---

## Capability Gaps

### E2E-1-CAPGAP-001: MCP/API for LINK Identity Validation

**Required capability:** MCP/API capability
**Tools required:** `project_get_profile`, `project_get_cursor`
**Status:** NOT_AVAILABLE
**Correct behavior:** CAPABILITY_MISSING — no conclusion about Librarian permitted.

### E2E-1-CAPGAP-002: MCP/API for MCP Dispatch Identity Validation

**Required capability:** MCP/API capability
**Tools required:** `project_assemble_context`
**Status:** NOT_AVAILABLE
**Correct behavior:** CAPABILITY_MISSING — no conclusion about Librarian permitted.

---

## SHA-256 Integrity Hash

### Run 1 (Immutable Baseline)

```
Aggregate: 56ba8161a6bcc8dced550e8ef547408184302b5fe75bd61a4d392fd866a0c787
```

| Evidence ID | SHA-256 |
|-------------|---------|
| E2E-1-EXEC-001 | `7bf550aec58eea4fa2fbf2805ccdfb5d2c33064c7b37c8ea63927dd63c1f95c6` |
| E2E-1-FIND-001 | `d030630c19a7b2bcacd327c46754569cd7637250e6f5009a6287467e720a3fd3` |
| E2E-1-FIND-002 | `70158474ef94489e8c1bed62a96915943eca37928cbd465b5d6c1408ea4295a4` |
| E2E-1-FIND-003 | `352906bfa62e13d187b2c84636d8599a1d8d2896a077e5802f1ac82bf5ee5aab` |
| E2E-1-CAPGAP-001 | `b8a57c3233ef34c792e2c73e2ace1e6ef8f8f3f93ad74cf7329662192e1effdd` |
| E2E-1-CAPGAP-002 | `47b0bd80fd2395fcb46e25bc7287a49afcb08217a4aae7e4040ba46d17f209c0` |

---

## Advisory Notice

This report is advisory-only. It does not confer authority, seal, or approval.
All findings are 🔍 Pending Owner review.
QA Pilot ≠ Authority.
