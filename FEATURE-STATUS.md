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
| **QA-PILOT-RECEIPT-STORE-1** | ✅ **Sealed (ledger #4, Owner-approved 2026-07-02 per OD-QA-PILOT-RECEIPT-STORE-1-SEAL)** | QA Pilot Receipt Store. Implemented local receipt store for register/get/list/status with schema validation, advisory enforcement, and bounded listing. 14/14 tests pass. All existing validation still passes. Prohibited-zone scan clean. See `docs/sprints/QA-PILOT-RECEIPT-STORE-1.md`. |
| **QA-PILOT-MCP-HANDLER-REGISTRATION-1** | ✅ **Sealed (ledger #5, Owner-approved 2026-07-02 per OD-QA-PILOT-MCP-HANDLER-REGISTRATION-1-SEAL)** | QA Pilot MCP Handler Registration. Wired MCP surface contracts to receipt store as QA Pilot-owned handler stubs. All handlers enforce project_boundary=qa-pilot and cross_project_registration=false. 14/14 tests pass. All existing validation still passes. Prohibited-zone scan clean. See `docs/sprints/QA-PILOT-MCP-HANDLER-REGISTRATION-1.md`. |
| **QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1** | ✅ **Sealed (ledger #6, Owner-approved 2026-07-02 per OD-QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1-SEAL)** | QA Pilot ↔ Librarian MCP Custody Packet. Decision-only sprint: preserved Option A, authorized Option B planning only. Documented 10 custody conditions (CC-1-10). See `docs/sprints/QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1.md`. |
| **QA-PILOT-BROKER-PLAN-1** | ✅ **Sealed (ledger #7, Owner-approved 2026-07-02 per OD-QA-PILOT-BROKER-PLAN-1-SEAL)** | QA Pilot Option B Broker Plan. Planning/design sprint: defined broker model, planned tool shapes, custody CC-1-10 mapping, audit receipt requirements, rollback requirements, future mutation envelope. 18/18 tests pass. No implementation authorized. See `docs/sprints/QA-PILOT-BROKER-PLAN-1.md`. |
| **QA-PILOT-BROKER-IMPLEMENTATION-1** | ✅ **Sealed (ledger #8, Owner-approved 2026-07-02 per OD-QA-PILOT-BROKER-IMPLEMENTATION-1-SEAL)** | QA Pilot Option B Broker Implementation. Implemented QA Pilot-local broker in `scripts/librarian_broker_qa_pilot.py` with custody verification (CC-1-10), advisory-only enforcement, audit receipt generation, disable flag. All 32 implementation tests pass. No Librarian mutation. No MCPController registration. See `docs/sprints/QA-PILOT-BROKER-IMPLEMENTATION-1.md`. |
| **QA-PILOT-BROKER-MCP-ADVISORY-SURFACE-1** | ✅ **Sealed (ledger #9, Owner-approved 2026-07-02 per OD-QA-PILOT-BROKER-MCP-ADVISORY-SURFACE-1-SEAL)** | QA Pilot Broker MCP Advisory Surface. QA Pilot-local advisory MCP-style surface for the sealed broker. 6 commands (accept, audit, list-audit, status, enable, disable). All 36 advisory surface tests pass. No native MCP registration. No Librarian mutation. See `docs/sprints/QA-PILOT-BROKER-MCP-ADVISORY-SURFACE-1.md`. |
| **QA-PILOT-BROKER-AUDIT-RECEIPT-STORE-1** | 🔍 **Pending Owner review (ledger #10)** | QA Pilot Broker Audit Receipt Store. Schema, governance, fixtures, validator, and test runner for broker audit receipts. 13 required fields, 12 BA rules. 3/3 valid fixtures pass, 4/4 invalid rejected. 19/19 tests pass. See `docs/sprints/QA-PILOT-BROKER-AUDIT-RECEIPT-STORE-1.md`. |

## 2. Project Profile

| Field | Value |
|-------|-------|
| project_id | `qa-pilot` |
| sandbox_boundary | `harness_governed` |
| active_sprint | `QA-PILOT-BROKER-PLAN-1` |
| ledger_path | `project-state/sprint-ledger.json` |
