# FEATURE-STATUS.md — QA Pilot

This file tracks the verification status of features in the QA Pilot project.

## Status Legend
- `🔍` Pending — A feature has changed and needs verification.
- `✅` Verified — A feature has been confirmed working.
- `🚫` Blocked — A dependency or issue prevents work.
- `⏸️` Deferred — Work is intentionally paused.
- `⚠️` Unstable — Feature works but has known issues.

---

## 1. Current Active / Next

| Sprint | Status | Detail Doc |
|--------|--------|------------|
| **QA-PILOT-PROJECT-INIT-1** | ✅ **Sealed (ledger #1, Owner-approved 2026-07-02 per OD-QA-PILOT-PROJECT-INIT-1-SEAL)** | QA Pilot project initialization. Created workspace, identity, profile (12 fields), ledger, status surfaces, receipt paths, sandbox governance. No production implementation imported. See `docs/sprints/QA-PILOT-PROJECT-INIT-1.md`. |
| **QA-PILOT-PRODUCTION-LANE-A-1** | ✅ **Sealed (ledger #2, Owner-approved 2026-07-02 per OD-QA-PILOT-PRODUCTION-LANE-A-1-SEAL)** | QA Pilot production Lane A (Receipt Schema). Imported QA Pilot receipt schema, governance, fixtures, validator, and test runner from Librarian planning-only evidence as QA Pilot-owned production implementation. 14/14 tests pass. Prohibited-zone scan clean. See `docs/sprints/QA-PILOT-PRODUCTION-LANE-A-1.md`. |
| **QA-PILOT-MCP-SURFACE-1** | ✅ **Sealed (ledger #3, Owner-approved 2026-07-02 per OD-QA-PILOT-MCP-SURFACE-1-SEAL)** | QA Pilot MCP Surface (Lane B). Defined 4 MCP tool stubs (register, get, list, status) with contracts, schema, fixtures, validator, and test runner. 14/14 tests pass. Existing receipt validation still passes. Prohibited-zone scan clean. See `docs/sprints/QA-PILOT-MCP-SURFACE-1.md`. |
| **QA-PILOT-RECEIPT-STORE-1** | 🔍 **Pending (ledger #4, awaiting Owner review)** | QA Pilot Receipt Store. Implemented local receipt store for register/get/list/status with schema validation, advisory enforcement, and bounded listing. 14/14 tests pass. All existing validation still passes. Prohibited-zone scan clean. See `docs/sprints/QA-PILOT-RECEIPT-STORE-1.md`. |

## 2. Project Profile

| Field | Value |
|-------|-------|
| project_id | `qa-pilot` |
| sandbox_boundary | `harness_governed` |
| active_sprint | `QA-PILOT-RECEIPT-STORE-1` |
| ledger_path | `project-state/sprint-ledger.json` |
