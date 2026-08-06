# QA-PILOT-STARTUP-CONSISTENCY-TEST-ISOLATION-FIX-1

**Lane:** maintenance
**Status:** sprint brief
**Boundary:** QA Pilot-local
**Dependencies:** ARTIFACT-STORAGE-SCALE-AUDIT-1

---

## Problem

The startup consistency test runner (`scripts/test-startup-consistency.sh`) copies the full QA Pilot project tree into each test workspace:

```bash
cp -r "$PROJECT_ROOT"/* "$test_run_dir/"
```

This creates a recursive copy hazard. If the test output directory (`test-runs/`) is itself inside the project tree (which it was), each test run copies its own previous test outputs, producing unbounded recursive directory nesting.

This was the root cause of the ~196,000 file / 1.0 GB artifact discovered in ARTIFACT-STORAGE-SCALE-AUDIT-1.

## Scope

Replace the unbounded recursive copy with a bounded minimal workspace skeleton that provides only the files `run-startup-checks.sh` actually needs.

## Design

### Before

```
cp -r "$PROJECT_ROOT"/* "$test_run_dir/"
```

Copies the entire project tree including any previous test output.

### After

A `create_workspace_skeleton` function that builds a minimal project directory:

```
<temp-dir>/<test-name>/
├── scripts/
│   ├── run-startup-checks.sh      (symlink)
│   ├── check-mcp-health.sh        (symlink)
│   ├── validate-qa-pilot-*.py     (symlinks)
│   └── test-qa-pilot-*.sh         (symlinks)
├── PROJECT-IDENTITY.md            (symlink)
├── PROJECT-PROFILE.json           (symlink)
├── startup-contract.json          (symlink)
├── FEATURE-STATUS.md              (symlink)
├── SESSION-HANDOFF.md             (symlink)
└── project-state/
    └── sprint-ledger.json         (symlink)
```

Using symlinks instead of copies avoids duplication entirely while giving each test a clean working directory.

### Output directory

Move test output from inside the project tree to a temporary location:

- **Before:** `$PROJECT_ROOT/docs/examples/qa-pilot-startup-consistency/test-runs/`
- **After:** `$(mktemp -d)/qa-pilot-startup-consistency/` (cleaned up on exit)

## Acceptance Criteria

1. All 6 test cases (all_present, one_missing, multiple_missing, contradictory_state, degraded_mcp, blocked_mcp) pass.
2. No recursive project copies are possible — the skeleton contains no nested project root.
3. Test output is isolated — written to `/tmp/` not inside the project tree.
4. Existing fixtures and validators are unchanged (only `test-startup-consistency.sh` is modified).
5. Sealed sprint history and ledger state are unaffected.
6. No files outside `scripts/test-startup-consistency.sh` are modified.
