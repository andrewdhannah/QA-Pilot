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

## 2. Project Profile

| Field | Value |
|-------|-------|
| project_id | `qa-pilot` |
| sandbox_boundary | `harness_governed` |
| active_sprint | `QA-PILOT-PROJECT-INIT-1` |
| ledger_path | `project-state/sprint-ledger.json` |
