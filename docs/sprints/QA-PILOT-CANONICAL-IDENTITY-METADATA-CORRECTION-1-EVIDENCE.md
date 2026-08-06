# QA-PILOT-CANONICAL-IDENTITY-METADATA-CORRECTION-1-EVIDENCE.md

**Produced by:** QA-PILOT-CANONICAL-IDENTITY-METADATA-CORRECTION-1 (ledger #167)
**Date:** 2026-07-20
**Classification:** Advisory evidence only — does not perform any decision

---

## Change

| Field | Value |
|-------|-------|
| File | `PROJECT-IDENTITY.md` |
| Field | `canonical_repo` |
| Previous | `/Users/andrew/Desktop/CarbideFrame/qa-pilot` |
| New | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/browser-app` |

**Reason:** Align metadata with Owner-approved canonical state (ODR-PROMOTE-TO-CANONICAL-0001).

---

## Preserved

| Reference | Location | Status |
|-----------|----------|--------|
| Historical OpenWork source | `/Users/andrew/Desktop/OpenWork/QA Pilot/` | Preserved (2 references in SESSION-HANDOFF.md) |
| Migration evidence paths | `receipts/`, `docs/sprints/` | Preserved (migration sprint docs reference old path as historical evidence) |
| Canonical transition evidence | `docs/transitions/` | Preserved (evidence annex references old path as finding) |
| Old CarbideFrame path | `/Users/andrew/Desktop/CarbideFrame/qa-pilot` | Preserved in historical sprint docs and receipts |

The old references are evidence, not errors.

---

## Validation

| # | Check | Result |
|---|-------|--------|
| ID-1 | Canonical identity metadata points to Owner-approved canonical path | ☑ PASS — `canonical_repo` now points to `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/browser-app` |
| ID-2 | Historical migration references preserved | ☑ PASS — OpenWork references preserved in SESSION-HANDOFF.md (2 refs), migration sprint docs, receipts |
| ID-3 | No evidence references resolve to invalid identity | ☑ PASS — new canonical path exists; startup-contract `web_app_root` already correct |
| ID-4 | Startup/project metadata remains consistent | ☑ PASS — startup-contract `project_id=qa-pilot`, `web_app_root=active/qa-pilot/browser-app/`, `application_data_root=active/qa-pilot/browser-app/data/` |
| ID-5 | Change evidence produced | ☑ PASS — this document |
| ID-6 | No unrelated files modified | ☑ PASS — only `PROJECT-IDENTITY.md` modified |

**Overall:** 6 PASS, 0 FAIL

---

## Consumer Validation

### Primary Consumer (Updated)

| Consumer | Field | Previous | New | Status |
|----------|-------|----------|-----|--------|
| `PROJECT-IDENTITY.md` | `canonical_repo` | `/Users/andrew/Desktop/CarbideFrame/qa-pilot` | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/browser-app` | ✅ Updated |

### Secondary Consumers (Not Modified — Findings)

| Consumer | Field | Value | Status | Finding |
|----------|-------|-------|--------|---------|
| `PROJECT-PROFILE.json` | `repo_path` | `/Users/andrew/Desktop/CarbideFrame/qa-pilot` | ⚠ Still references old path | Deferred — not in sprint scope |
| `docs/governance/QA-PILOT-PROJECT-GOVERNANCE.md` | `canonical_repo` | `/Users/andrew/Desktop/CarbideFrame/qa-pilot` | ⚠ Still references old path | Deferred — not in sprint scope |

**Note:** These secondary consumers still reference the old path. The old path exists (`/Users/andrew/Desktop/CarbideFrame/qa-pilot` is a real directory), so the references are not broken — they are inconsistent with the updated canonical identity. This inconsistency should be addressed in a follow-up sprint if the Owner chooses to extend the scope.

### Tertiary Consumers (Read-Only — No Change Required)

| Consumer | Field | Value | Status |
|----------|-------|-------|--------|
| `startup-contract.json` | `web_app_root` | `active/qa-pilot/browser-app/` | ✅ Already correct |
| `startup-contract.json` | `application_data_root` | `active/qa-pilot/browser-app/data/` | ✅ Already correct |
| `SESSION-HANDOFF.md` | references | Historical migration paths | ✅ Preserved (evidence) |
| Migration sprint docs | references | Historical paths | ✅ Preserved (evidence) |
| Migration receipts | references | Historical paths | ✅ Preserved (evidence) |

---

## Scope

| Category | Files Modified |
|----------|---------------|
| Modified | `PROJECT-IDENTITY.md` (1 file, 1 field) |
| Not modified | `PROJECT-PROFILE.json`, `docs/governance/QA-PILOT-PROJECT-GOVERNANCE.md`, all other files |

**Scope classification:** Identity metadata correction only. No feature work, no validator repair, no ODR modification.

---

## Completion Classification

| Gate | Result |
|------|--------|
| ID-1 | PASS |
| ID-2 | PASS |
| ID-3 | PASS |
| ID-4 | PASS |
| ID-5 | PASS |
| ID-6 | PASS |

**Expected result achieved:** 6 PASS, 0 FAIL.

---

**Produced by:** QA-PILOT-CANONICAL-IDENTITY-METADATA-CORRECTION-1 (ledger #167)
**Classification:** Advisory evidence only — does not perform any decision.
