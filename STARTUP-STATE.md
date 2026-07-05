# STARTUP-STATE.md — QA Pilot

**Generated:** 2026-07-05T22:17:21Z

## Current State

- **Project:** QA Pilot
- **Workspace root:** /Users/andrew/Desktop/CarbideFrame
- **Active project root:** /Users/andrew/Desktop/CarbideFrame/active/qa-pilot
- **Historical root:** /Users/andrew/Desktop/OpenWork
- **Operating mode:** managed
- **Active work session:** none
- **MCP:** reachable (via Librarian)
- **Git branch:** main
- **Last commit:** 1652698 QA-PILOT-BROKER-AUDIT-STORE-IMPLEMENTATION-1-SEAL
- **Working tree:** dirty/45 changed or untracked
- **Validators:** 11
- **Test runners:** 11
- **Blockers:** none detected

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

- **OS/Version:** Darwin Andrews-MacBook-Pro.local 24.6.0 Darwin Kernel Version 24.6.0: Fri Feb 27 19:33:24 PST 2026; root:xnu-11417.140.69.709.8~1/RELEASE_X86_64 x86_64
- **Python version:** Python 3.14.4
- **Startup checks:** /Users/andrew/Desktop/CarbideFrame/active/qa-pilot/scripts/run-startup-checks.sh
- **Validator count:** 11
- **Test runner count:** 11

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
