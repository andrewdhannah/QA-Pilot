# STARTUP-STATE.md — QA Pilot

**Generated:** 2026-08-20T02:42:51Z

## Current State

- **Project:** QA Pilot
- **Workspace root:** unknown
- **Active project root:** /Users/andrew/Desktop/CarbideFrame/active/qa-pilot
- **Historical root:** unknown
- **Operating mode:** managed
- **Active work session:** none
- **MCP:** reachable
- **Git branch:** main
- **Last commit:** eb5f801 docs: define Phase 7 success criterion and empirical validation framework
- **Working tree:** dirty/92 changed or untracked
- **Validators:** 77
- **Test runners:** 83
- **Blockers:** none detected

## Custody Posture (Startup Integration)

- **Custody surface:** ok
- **Posture:** available
- **Detail:** 12 custody receipts indexed
- **Total receipts indexed:** 12
- **By custody source:** lifecycle=3, live=2, write=7
- **By decision type:** approvals=10, denied=2, warning=0, dry_run=0
- **Violation codes:** WRITE_SCOPE_VIOLATION=2
- **Mutation status:** blocked=2, mutated=10
- **Owner approval present:** 2
- **Owner approval absent:** 10
- **Sealed contract references #23–#28:** #23=7, #24=3, #25=4, #26=0, #27=0, #28=0
- **Review items:** none detected
- **Approval/seal/execute/write controls:** none

## QA Pilot Identity

- **Identity file:** /Users/andrew/Desktop/CarbideFrame/active/qa-pilot/PROJECT-IDENTITY.md
- **Profile file:** /Users/andrew/Desktop/CarbideFrame/active/qa-pilot/PROJECT-PROFILE.json
- **Startup contract:** /Users/andrew/Desktop/CarbideFrame/active/qa-pilot/startup-contract.json
- **Sprint ledger:** /Users/andrew/Desktop/CarbideFrame/active/qa-pilot/project-state/sprint-ledger.json
- **Web app:** false (Python/script project)
- **Sandbox boundary:** harness_governed

## Required Files

- ✅ PROJECT-IDENTITY.md
- ✅ PROJECT-PROFILE.json
- ✅ project-state/sprint-ledger.json
- ✅ SESSION-HANDOFF.md
- ✅ FEATURE-STATUS.md
- ✅ startup-contract.json

## Execution Contract (ENV-CONTRACT-1)

- **OS/Version:** Darwin AndrewsMac.local 24.6.0 Darwin Kernel Version 24.6.0: Fri Feb 27 19:33:24 PST 2026; root:xnu-11417.140.69.709.8~1/RELEASE_X86_64 x86_64
- **Python version:** Python 3.14.4
- **Startup checks:** /Users/andrew/Desktop/CarbideFrame/active/qa-pilot/scripts/run-startup-checks.sh
- **Validator count:** 77
- **Test runner count:** 83

## Next

- Review SESSION-HANDOFF.md for next concrete task
- Keep startup bounded; do not search the repository unless the task requires it.
- Use project-root handoff at /Users/andrew/Desktop/CarbideFrame/active/qa-pilot/SESSION-HANDOFF.md.

## Do Not Touch Unless Asked

- The Librarian repo (active/librarian/)
- Canonical docs without checkout receipt
- Cross-project mutation paths defined in PROJECT-PROFILE.json

## Required Behavior

- Output the bounded startup report from AGENT-START.md.
- Mark agent work 🔍 Pending; never mark ✅ Verified.
- Use deterministic tools/scripts for exact paths, counts, JSON/YAML, markdown slots, custody, and destructive dry runs.
- This is a Python/script project — no web app checks apply.
