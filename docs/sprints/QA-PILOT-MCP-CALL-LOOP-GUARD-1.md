# Sprint Receipt — QA-PILOT-MCP-CALL-LOOP-GUARD-1

**Status:** ✅ Sealed
**Type:** Governance / MCP call loop guard contract
**Lane:** governance
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none

---

## Scope Satisfied

Created the first bounded MCP call loop guard layer for QA Pilot agent sessions. Closes defect QA-PILOT-OPEN-WORK-MCP-DOOM-LOOP-DEFECT-1 by defining an enforceable, Owner-reviewable guard packet schema (MG-*) capturing an agent session's MCP tool-call trace and validating against 15 business rules (MG-1 through MG-15) covering:

1. No repeated identical MCP calls after definitive result (MG-8)
2. No repeated health checks after success (MG-9)
3. No cross-lane Librarian MCP calls from QA Pilot without authorization (MG-10)
4. Bounded max-call count enforced — max 10 total calls (MG-11)
5. Stop reason required for each tool sequence (MG-12)
6. No auto-retry loop after terminal result (MG-13)
7. Authority boundary enforcement — advisory-only, no seal/Librarian mutation authority (MG-14, MG-15)

## Deliverables

| Artifact | Path |
|----------|------|
| Schema | `docs/schemas/qa-pilot-mcp-call-loop-guard.schema.json` |
| Governance doc | `docs/governance/QA-PILOT-MCP-CALL-LOOP-GUARD.md` |
| Valid fixture 1 | `docs/examples/qa-pilot-mcp-call-loop-guard/valid-bounded-startup-only.json` |
| Valid fixture 2 | `docs/examples/qa-pilot-mcp-call-loop-guard/valid-implementation-no-mcp.json` |
| Invalid fixture 1 | `docs/examples/qa-pilot-mcp-call-loop-guard/invalid-repeated-identical-calls.json` |
| Invalid fixture 2 | `docs/examples/qa-pilot-mcp-call-loop-guard/invalid-no-stop-reason.json` |
| Invalid fixture 3 | `docs/examples/qa-pilot-mcp-call-loop-guard/invalid-cross-lane-unauthorized.json` |
| Invalid fixture 4 | `docs/examples/qa-pilot-mcp-call-loop-guard/invalid-auto-retry-loop.json` |
| Validator | `scripts/validate-qa-pilot-mcp-call-loop-guard.py` (15 MG rules) |
| Test runner | `scripts/test-qa-pilot-mcp-call-loop-guard.sh` |

## Guard Schema

- **Required fields:** guard_id (MG-*), session_id, title, description, mcp_calls (min 1), aggregate (total_calls, unique_tools, repeated_identical_calls, repeated_health_checks, stop_reason_present, cross_lane_detected, bounded, no_auto_retry_loop, terminal_result_recognized), advisory_only, custody, librarian_impact, authority disclaimers
- **Call result types:** success, not_found, unreachable, other_error
- **Session phases:** startup, implementation, verification, diagnostic, seal
- **Boundary fields:** advisory_only=true, custody=qa-pilot-local, librarian_impact=none, authority disclaimers

## Business Rules (15 MG rules)

| Rule | Description |
|------|-------------|
| MG-1 | Conform to qa-pilot-mcp-call-loop-guard.schema.json |
| MG-2 | advisory_only must be true |
| MG-3 | custody must be qa-pilot-local |
| MG-4 | librarian_impact must be none |
| MG-5 | not_seal_authority must be present and >= 20 chars |
| MG-6 | not_librarian_mutation_authority must be present and >= 20 chars |
| MG-7 | At least one MCP call recorded |
| MG-8 | No repeated identical MCP calls after definitive result |
| MG-9 | No repeated health checks after success |
| MG-10 | No cross-lane Librarian MCP calls without authorization |
| MG-11 | Bounded max-call count enforced (max 10 distinct MCP calls) |
| MG-12 | Stop reason must be present for each tool sequence |
| MG-13 | No auto-retry loop: calls stop after terminal result |
| MG-14 | No authority claims in descriptions or detail fields |
| MG-15 | No Librarian mutation authority referenced |

## Owner Key Instruction Implemented

> "Do not diagnose a doom loop unless the trace shows repeated MCP calls after a successful or expected terminal result. Treat startup-only -32602 add-on responses as expected and non-blocking under startup protocol §3.2."

Implemented via MG-8 and MG-13: repeated identical calls are only flagged if they occur *after* a definitive terminal result (success, not_found/-32602, unreachable). A single startup sequence of -32602 results across different tools does not trigger MG-8 or MG-13 because each call uses a different tool with different params.

## Validation

- **Validator:** 15/15 MG rules defined and enforced
- **Valid fixtures:** 2/2 pass
- **Invalid fixtures:** 4/4 correctly rejected
- **Test runner:** 27/27 tests pass
- **Existing validators:** All chain validators remain green (verified)
- **No Librarian files modified**

## Authorization

Sprint authorized 2026-07-07 by Owner: "I authorize QA Pilot sprint QA-PILOT-MCP-CALL-LOOP-GUARD-1."

Sealed 2026-07-07 by Owner: "I approve and seal QA Pilot sprint QA-PILOT-MCP-CALL-LOOP-GUARD-1 as ledger #47."

**Next authorized sprint:** None — awaiting Owner direction.

## Defect Closure

This sprint closes defect `QA-PILOT-OPEN-WORK-MCP-DOOM-LOOP-DEFECT-1` (Receipt: `receipts/defects/QA-PILOT-OPEN-WORK-MCP-DOOM-LOOP-DEFECT-1.md`).
All 8 guard conditions from the defect are satisfied:

| # | Condition | Implementation |
|---|-----------|---------------|
| 1 | Detect repeated identical MCP calls | MG-8: validator checks for same tool+params after terminal result |
| 2 | Detect repeated health checks after success | MG-9: flags >1 successful health check on same tool |
| 3 | Detect cross-lane Librarian MCP calls | MG-10: blocks unauthorized Librarian project tools from QA Pilot |
| 4 | Require bounded max-call count | MG-11: enforces max 10 total MCP calls per session |
| 5 | Require stop reason | MG-12: each call sequence must document why it stopped |
| 6 | Require Owner-visible diagnostic packet | MG-* guard packet is the diagnostic packet; schema defined |
| 7 | No automatic retry loop | MG-13: rejects calls after definitive terminal result |
| 8 | No Librarian mutation authority | MG-15: rejects any Librarian mutation references; MG-2/3/4 enforce advisory-only/local |
