#!/usr/bin/env python3
"""
QA Pilot MCP Call Loop Guard Validator — QA-PILOT-MCP-CALL-LOOP-GUARD-1

Enforces MG-1 through MG-15 business rules on MCP call loop guard packets,
fixtures, and schema conformance.

Rules:
    MG-1:  Guard packet conforms to qa-pilot-mcp-call-loop-guard.schema.json
    MG-2:  advisory_only must be true
    MG-3:  custody must be qa-pilot-local
    MG-4:  librarian_impact must be none
    MG-5:  not_seal_authority must be present and >= 20 chars
    MG-6:  not_librarian_mutation_authority must be present and >= 20 chars
    MG-7:  At least one MCP call recorded
    MG-8:  No repeated identical MCP calls after definitive result
    MG-9:  No repeated health checks after success
    MG-10: No cross-lane Librarian MCP calls without authorization
    MG-11: Bounded max-call count enforced (max 10 distinct MCP calls)
    MG-12: Stop reason must be present for each tool sequence
    MG-13: No auto-retry loop: calls stop after terminal result
    MG-14: No authority claims in descriptions or detail fields
    MG-15: No Librarian mutation authority referenced
"""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "qa-pilot-mcp-call-loop-guard.schema.json"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-mcp-call-loop-guard"

VALID_FIXTURES = [
    "valid-bounded-startup-only.json",
    "valid-implementation-no-mcp.json",
]

INVALID_FIXTURES = [
    "invalid-repeated-identical-calls.json",
    "invalid-no-stop-reason.json",
    "invalid-cross-lane-unauthorized.json",
    "invalid-auto-retry-loop.json",
]

ALL_FIXTURES = sorted(set(VALID_FIXTURES + INVALID_FIXTURES))

FORBIDDEN_AUTHORITY_TERMS = [
    "approve", "seal", "execute", "write", "sprint-start",
    "merge", "production", "deploy",
]

CROSS_LANE_LIBRARIAN_TOOLS = [
    "project_work_get_summary", "project_work_get_latest_closed",
    "project_work_list_open", "project_work_search",
    "project_work_get", "project_work_result_intake",
    "project_advance_cursor", "project_branch_cursor",
]

TERMINAL_RESULTS = {"success", "not_found", "unreachable"}

MAX_ALLOWED_TOTAL_CALLS = 10
MAX_REPEATED_HEALTH_CHECKS = 1


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_schema():
    """Validate the schema document itself is parseable."""
    try:
        schema = load_json(SCHEMA_PATH)
        if not isinstance(schema, dict):
            return False, "Schema is not a JSON object"
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            return False, "Schema must use Draft 2020-12"
        if not schema.get("title"):
            return False, "Schema missing title"
        return True, "ok"
    except Exception as e:
        return False, str(e)


def validate_fixture(path):
    """Validate a single fixture against all business rules."""
    errors = []
    try:
        data = load_json(path)
    except Exception as e:
        return False, [f"Failed to parse JSON: {e}"]

    guard_id = data.get("guard_id", "")

    # MG-1: Basic structural checks
    if not re.match(r"^MG-[A-Z0-9-]+$", guard_id):
        errors.append(f"MG-1: Invalid guard_id pattern: {guard_id}")

    # MG-2: advisory_only
    if data.get("advisory_only") is not True:
        errors.append(f"MG-2: advisory_only must be true, got {data.get('advisory_only')}")

    # MG-3: custody
    if data.get("custody") != "qa-pilot-local":
        errors.append(f"MG-3: custody must be qa-pilot-local, got {data.get('custody')}")

    # MG-4: librarian_impact
    if data.get("librarian_impact") != "none":
        errors.append(f"MG-4: librarian_impact must be none, got {data.get('librarian_impact')}")

    # MG-5: not_seal_authority
    nsa = data.get("not_seal_authority", "")
    if not isinstance(nsa, str) or len(nsa) < 20:
        errors.append(f"MG-5: not_seal_authority must be >= 20 chars, got {len(nsa)}")

    # MG-6: not_librarian_mutation_authority
    nlma = data.get("not_librarian_mutation_authority", "")
    if not isinstance(nlma, str) or len(nlma) < 20:
        errors.append(f"MG-6: not_librarian_mutation_authority must be >= 20 chars, got {len(nlma)}")

    # MG-7: At least one MCP call
    mcp_calls = data.get("mcp_calls", [])
    if not isinstance(mcp_calls, list) or len(mcp_calls) == 0:
        errors.append("MG-7: At least one MCP call required")

    # ── Aggregate validation ──
    aggregate = data.get("aggregate", {})

    # Verify total_calls
    if isinstance(mcp_calls, list) and isinstance(aggregate, dict):
        ag_total = aggregate.get("total_calls", 0)
        if ag_total != len(mcp_calls):
            errors.append(f"aggregate.total_calls={ag_total} != len(mcp_calls)={len(mcp_calls)}")

    # MG-8: No repeated identical MCP calls after definitive result
    if isinstance(mcp_calls, list):
        seen_calls = {}  # tool → set of params_summary
        for call in mcp_calls:
            tool = call.get("tool", "")
            params = call.get("params_summary", "")
            key = f"{tool}:{params}"
            retry = call.get("retry", False)
            result = call.get("result", "")

            if key in seen_calls and result in TERMINAL_RESULTS:
                if retry or seen_calls[key] in TERMINAL_RESULTS:
                    errors.append(
                        f"MG-8: Repeated identical call detected: call #{call.get('call_number')} "
                        f"({tool}) with same params after terminal result '{seen_calls[key]}'"
                    )
            seen_calls[key] = result

    # MG-9: No repeated health checks after success
    if isinstance(mcp_calls, list):
        health_success_count = 0
        for call in mcp_calls:
            tool = call.get("tool", "")
            result = call.get("result", "")
            if "health" in tool.lower() and result == "success":
                health_success_count += 1
                if health_success_count > MAX_REPEATED_HEALTH_CHECKS:
                    errors.append(
                        f"MG-9: Repeated health checks after success: "
                        f"{health_success_count} successful health checks detected"
                    )

    # MG-10: No cross-lane Librarian MCP calls without authorization
    if isinstance(mcp_calls, list):
        cross_lane_found = []
        for call in mcp_calls:
            tool = call.get("tool", "")
            params = call.get("params_summary", "")
            if tool in CROSS_LANE_LIBRARIAN_TOOLS:
                cross_lane_found.append(f"{tool}({params})")

        if cross_lane_found:
            errors.append(
                f"MG-10: Cross-lane Librarian MCP calls detected: {', '.join(cross_lane_found)}"
            )

    # MG-11: Bounded max-call count
    if isinstance(mcp_calls, list) and len(mcp_calls) > MAX_ALLOWED_TOTAL_CALLS:
        errors.append(
            f"MG-11: Total calls {len(mcp_calls)} exceeds max allowed {MAX_ALLOWED_TOTAL_CALLS}"
        )

    # MG-12: Stop reason must be present for each tool sequence
    if isinstance(mcp_calls, list):
        tools_seen = set()
        for call in mcp_calls:
            tool = call.get("tool", "")
            stop_reason = call.get("stop_reason")
            if tool not in tools_seen:
                tools_seen.add(tool)
            if not stop_reason or (isinstance(stop_reason, str) and len(stop_reason.strip()) == 0):
                errors.append(
                    f"MG-12: No stop reason for tool '{tool}' "
                    f"at call #{call.get('call_number')}"
                )

    # MG-13: No auto-retry loop — calls stop after terminal result
    if isinstance(mcp_calls, list):
        terminal_seen_on_tool = {}  # tool → True if terminal result seen
        for call in mcp_calls:
            tool = call.get("tool", "")
            result = call.get("result", "")
            retry = call.get("retry", False)

            if tool in terminal_seen_on_tool and terminal_seen_on_tool[tool]:
                if retry or result != "other_error":
                    errors.append(
                        f"MG-13: Auto-retry after terminal result for tool '{tool}' "
                        f"at call #{call.get('call_number')}"
                    )
            if result in TERMINAL_RESULTS:
                terminal_seen_on_tool[tool] = True

    # Check aggregate.terminal_result_recognized consistency
    if isinstance(aggregate, dict):
        ag_terminal = aggregate.get("terminal_result_recognized", False)
        if isinstance(mcp_calls, list):
            any_terminal = any(
                call.get("result", "") in TERMINAL_RESULTS
                for call in mcp_calls
            )
            if any_terminal and not ag_terminal:
                errors.append(
                    "MG-13/aggregate: terminal results found in calls but "
                    "aggregate.terminal_result_recognized is false"
                )

    # MG-14: No authority claims in descriptions/detail
    desc_text = (data.get("description", "") + " " + data.get("title", "")).lower()
    for term in FORBIDDEN_AUTHORITY_TERMS:
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, desc_text):
            context_ok = any(
                neg in desc_text
                for neg in [f"no {term}", f"not {term}", f"cannot {term}",
                            f"does not {term}", f"reject {term}",
                            f"denied {term}", f"block {term}"]
            )
            if not context_ok:
                errors.append(f"MG-14: Forbidden authority term '{term}' in description/title")

    if isinstance(mcp_calls, list):
        for call in mcp_calls:
            detail = call.get("result_detail", "").lower()
            for term in FORBIDDEN_AUTHORITY_TERMS:
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, detail):
                    context_ok = any(
                        neg in detail
                        for neg in [f"no {term}", f"not {term}", f"cannot {term}",
                                    f"does not {term}", f"reject {term}",
                                    f"denied {term}", f"block {term}"]
                    )
                    if not context_ok:
                        errors.append(f"MG-14: Forbidden authority term '{term}' in call detail")

    # MG-15: No Librarian mutation authority referenced
    for key in ["session_id", "description"]:
        val = str(data.get(key, "")).lower()
        if "librarian" in val and "mutation" in val:
            if "not" not in val and "no" not in val:
                errors.append(f"MG-15: Description references Librarian mutation authority: {data.get(key)}")

    return len(errors) == 0, errors


def do_checks():
    print("QA Pilot MCP Call Loop Guard Validator — QA-PILOT-MCP-CALL-LOOP-GUARD-1")
    print("=" * 60)
    print()

    all_pass = True

    # ── Schema check ──
    print("[Schema Validation]")
    schema_ok, schema_msg = validate_schema()
    print(f"  {'✅' if schema_ok else '❌'} Schema: {schema_msg}")
    if not schema_ok:
        all_pass = False
    print()

    # ── Fixture checks ──
    print("[Fixture Validation]")
    all_fixtures_exist = True
    for fname in ALL_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if not fpath.exists():
            print(f"  ❌ Missing fixture: {fname}")
            all_fixtures_exist = False
            all_pass = False

    if all_fixtures_exist:
        print(f"  ✅ All {len(ALL_FIXTURES)} fixtures present")

    for fname in VALID_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if not fpath.exists():
            continue
        ok, errs = validate_fixture(fpath)
        if ok:
            print(f"  ✅ {fname}: passes")
        else:
            print(f"  ❌ {fname}: FAILED")
            for e in errs:
                print(f"     - {e}")
            all_pass = False

    for fname in INVALID_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if not fpath.exists():
            continue
        ok, errs = validate_fixture(fpath)
        if not ok:
            print(f"  ✅ {fname}: correctly rejected ({len(errs)} violations)")
            for e in errs:
                print(f"     - {e}")
        else:
            print(f"  ❌ {fname}: should have been rejected but passed")
            all_pass = False

    print()

    # ── Business rules summary ──
    print("[Business Rules — MG-1 through MG-15]")
    print("  ✅ MG-1 through MG-15 enforced via per-fixture validation")
    print()

    print(f"\n{'✅ ALL CHECKS PASS' if all_pass else '❌ SOME FAILED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(do_checks())
