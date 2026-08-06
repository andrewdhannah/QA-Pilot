# EXT-DEFECT-001 — #27 Test Runner Path Resolution Bug

**Status:** ✅ Fixed (2026-07-06)
**Introduced by:** Pre-existing (CUSTODY-RECEIPT-INDEX-1, #27)
**Discovered during:** CUSTODY-RECEIPT-SUMMARY-SURFACE-1 seal review
**Affected sprint:** CUSTODY-RECEIPT-INDEX-1 (#27)
**Triggered by:** Owner review gate requiring #27 runner to remain green

---

## Description

The `test-custody-receipt-index.sh` (#27) test runner used **relative paths** for its external regression checks (AG-26 through AG-29):

```bash
# BEFORE (broken when CWD != project root):
"AG-26:#23:bash scripts/test-project-wide-write-custody-enforcement.sh"
"AG-27:#24:bash scripts/test-live-custody-integration.sh"
"AG-28:#25:bash scripts/test-lifecycle-custody-extension.sh"
"AG-29:#26:bash scripts/test-owner-decision-custody-receipts.sh"
```

These commands fail with exit 127 (`command not found`) when the test runner is invoked from any directory other than the project root. By contrast, AG-30 and AG-31 in the same file correctly used `$PROJECT_ROOT/scripts/...`.

## Evidence

```
# From /tmp (wrong CWD):
bash scripts/test-project-wide-write-custody-enforcement.sh  → exit 127

# From project root (correct CWD):
bash scripts/test-project-wide-write-custody-enforcement.sh  → exit 0  (passes)
```

## Fix Applied

Changed lines 172-175 to use `$PROJECT_ROOT` absolute paths, matching the pattern used by AG-30 and AG-31:

```bash
# AFTER (works from any CWD):
"AG-26:#23:bash $PROJECT_ROOT/scripts/test-project-wide-write-custody-enforcement.sh"
"AG-27:#24:bash $PROJECT_ROOT/scripts/test-live-custody-integration.sh"
"AG-28:#25:bash $PROJECT_ROOT/scripts/test-lifecycle-custody-extension.sh"
"AG-29:#26:bash $PROJECT_ROOT/scripts/test-owner-decision-custody-receipts.sh"
```

**Result:** #27 test runner now returns 38/38 from any working directory.

## Non-Regression Proof

The fix changes only path resolution in test invocation — it does **not** alter:
- #27 index behavior or semantics (`custody-receipt-index.py` untouched)
- Custody receipts (none modified)
- #23/#24/#25/#26 behavior (only invocation path, not the runners themselves)
- Index output (deterministic output confirmed identical before/after)

## Caveat for Sprint Seal

This defect is **pre-existing** and **external** to CUSTODY-RECEIPT-SUMMARY-SURFACE-1. The summary surface sprint did not introduce, worsen, or interact with this defect. The fix was applied to satisfy the acceptance gate requirement that #27 remain green.
