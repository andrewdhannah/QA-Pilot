#!/usr/bin/env python3
"""
QA Pilot MCP Surface Validator — QA-PILOT-MCP-SURFACE-1

Enforces MP-1 through MP-4 business rules on QA Pilot MCP tool stub fixtures.

Rules:
    MP-1: Register tools must classify submitted receipts as advisory evidence only
    MP-2: Query/list/status tools must be read-only (R0)
    MP-3: No MCP tool may claim or imply approval, seal, merge, or production-readiness
    MP-4: All tool outputs must include advisory/read-only boundary statements

Tool-specific rules:
    R-1:  Input receipt in register must have authority='advisory'
    R-2:  Register output must have advisory_only=true
    R-3:  Register output non_effects must contain advisory language
    G-1:  Get input receipt_id must match qapr- pattern and be non-empty
    G-2:  Get output must include advisory_notice
    L-1:  List input must have limit (1-100)
    L-2:  List output must include advisory_notice
    S-1:  Status input must be empty object
    S-2:  Status output must not contain action/seal/approve language
"""

import json
import os
import re
import sys
from pathlib import Path

ALLOWED_TOOL_NAMES = [
    "qa_pilot_receipt_register",
    "qa_pilot_receipt_get",
    "qa_pilot_receipt_list",
    "qa_pilot_receipt_status",
]
ALLOWED_AUTHORITIES = ["R0_read_only", "R1_advisory_mutation"]
REGISTER_TOOLS = ["qa_pilot_receipt_register"]
READ_ONLY_TOOLS = ["qa_pilot_receipt_get", "qa_pilot_receipt_list", "qa_pilot_receipt_status"]
FORBIDDEN_OUTPUT_WORDS = [
    "approved", "sealed", "merged", "production_ready",
    "auto_approve", "auto_seal", "grant_authority",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_mp_1(data):
    """MP-1: Register tools must classify submitted receipts as advisory evidence only."""
    if data.get("tool_name") != "qa_pilot_receipt_register":
        return (True, "Not a register tool — skipped")
    receipt = data.get("input", {}).get("receipt", {})
    auth = receipt.get("authority", "")
    if auth != "advisory":
        return (False, f"Register receipt authority must be 'advisory', got '{auth}'")
    stmt = receipt.get("non_approval_statement", "")
    if len(stmt) < 20:
        return (False, f"Register receipt non_approval_statement too short ({len(stmt)} chars)")
    return (True, "Register receipt properly classified as advisory evidence")


def check_mp_2(data):
    """MP-2: Query/list/status tools must be read-only (R0)."""
    tool = data.get("tool_name", "")
    auth = data.get("authority", "")
    if tool in READ_ONLY_TOOLS and auth != "R0_read_only":
        return (False, f"Tool '{tool}' is a query tool but authority is '{auth}' (expected R0_read_only)")
    if tool == "qa_pilot_receipt_register" and auth != "R1_advisory_mutation":
        return (False, f"Tool '{tool}' is a register tool but authority is '{auth}' (expected R1_advisory_mutation)")
    return (True, f"Tool '{tool}' has correct authority '{auth}'")


def check_mp_3(data):
    """MP-3: No MCP tool may claim or imply approval, seal, merge, or production-readiness."""
    output = data.get("output", {})
    output_str = json.dumps(output).lower()
    for word in FORBIDDEN_OUTPUT_WORDS:
        if word in output_str:
            # Check if it's negated
            lines_containing = [l for l in output_str.split("\n") if word in l.lower()]
            # If the word appears only in non_effects/advisory notice with negation, it's OK
            non_effects = [str(e).lower() for e in output.get("non_effects", [])]
            advisory = output.get("advisory_notice", "").lower()
            all_negated = True
            for line in lines_containing:
                if word in line and "does not" not in line and "advisory" not in line and "no " not in line:
                    all_negated = False
            if not all_negated:
                return (False, f"Output contains or implies '{word}' which violates advisory-only boundary")
    return (True, "No forbidden authority claims in output")


def check_mp_4(data):
    """MP-4: All tool outputs must include advisory/read-only boundary statements."""
    output = data.get("output", {})
    tool = data.get("tool_name", "")

    # Register output must have advisory_only=true and non_effects
    if tool == "qa_pilot_receipt_register":
        if not output.get("advisory_only"):
            return (False, "Register output must have advisory_only=true")
        ne = output.get("non_effects", [])
        has_advisory = any("advisory" in str(e).lower() or "does not" in str(e).lower() for e in ne)
        if not has_advisory:
            return (False, "Register output non_effects must contain advisory/negation language")

    # Query/list/status must have advisory_notice
    if tool in READ_ONLY_TOOLS:
        notice = output.get("advisory_notice", "")
        if len(notice) < 10:
            return (False, f"Tool '{tool}' output missing or too short advisory_notice")

    return (True, f"Advisory boundary present in '{tool}' output")


def check_r_1(data):
    """R-1: Input receipt in register must have authority='advisory'."""
    if data.get("tool_name") != "qa_pilot_receipt_register":
        return (True, "Skipped")
    receipt = data.get("input", {}).get("receipt", {})
    auth = receipt.get("authority", "")
    if auth != "advisory":
        return (False, f"R-1: receipt.authority must be 'advisory', got '{auth}'")
    return (True, "R-1: receipt.authority is advisory")


def check_r_2(data):
    """R-2: Register output must have advisory_only=true."""
    if data.get("tool_name") != "qa_pilot_receipt_register":
        return (True, "Skipped")
    if data.get("output", {}).get("advisory_only") is not True:
        return (False, "R-2: register output advisory_only must be true")
    return (True, "R-2: register output advisory_only=true")


def check_r_3(data):
    """R-3: Register output non_effects must contain advisory language."""
    if data.get("tool_name") != "qa_pilot_receipt_register":
        return (True, "Skipped")
    ne = data.get("output", {}).get("non_effects", [])
    has_advisory = any("does not" in str(e).lower() or "advisory" in str(e).lower() for e in ne)
    if not has_advisory:
        return (False, "R-3: register output non_effects must contain advisory language")
    return (True, "R-3: register output non_effects contains advisory language")


def check_g_1(data):
    """G-1: Get input receipt_id must match qapr- pattern and be non-empty."""
    if data.get("tool_name") != "qa_pilot_receipt_get":
        return (True, "Skipped")
    rid = data.get("input", {}).get("receipt_id", "")
    if not rid:
        return (False, "G-1: get input receipt_id is empty")
    if not re.match(r"^qapr-\d{8}-\d{3,}$", rid):
        return (False, f"G-1: get input receipt_id must match qapr- pattern, got '{rid}'")
    return (True, f"G-1: get input receipt_id '{rid}' is valid")


def check_g_2(data):
    """G-2: Get output must include advisory_notice."""
    if data.get("tool_name") != "qa_pilot_receipt_get":
        return (True, "Skipped")
    notice = data.get("output", {}).get("advisory_notice", "")
    if len(notice) < 10:
        return (False, "G-2: get output must include advisory_notice (min 10 chars)")
    return (True, "G-2: get output includes advisory_notice")


def check_l_1(data):
    """L-1: List input must have limit (1-100)."""
    if data.get("tool_name") != "qa_pilot_receipt_list":
        return (True, "Skipped")
    limit = data.get("input", {}).get("limit")
    if limit is None:
        return (False, "L-1: list input must have 'limit' field")
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        return (False, f"L-1: list input limit must be 1-100, got {limit}")
    return (True, f"L-1: list input limit={limit} is valid")


def check_l_2(data):
    """L-2: List output must include advisory_notice."""
    if data.get("tool_name") != "qa_pilot_receipt_list":
        return (True, "Skipped")
    notice = data.get("output", {}).get("advisory_notice", "")
    if len(notice) < 10:
        return (False, "L-2: list output must include advisory_notice (min 10 chars)")
    return (True, "L-2: list output includes advisory_notice")


def check_s_1(data):
    """S-1: Status input must be empty object."""
    if data.get("tool_name") != "qa_pilot_receipt_status":
        return (True, "Skipped")
    inp = data.get("input", {})
    if inp != {}:
        return (False, f"S-1: status input must be empty, got keys: {list(inp.keys())}")
    return (True, "S-1: status input is empty")


def check_s_2(data):
    """S-2: Status output must not claim seal/approve authority."""
    if data.get("tool_name") != "qa_pilot_receipt_status":
        return (True, "Skipped")
    output = data.get("output", {})
    out_str = json.dumps(output).lower()
    for word in ["seal", "approve", "sealed", "approved"]:
        notice = output.get("advisory_notice", "").lower()
        # Check if the word appears outside of advisory_notice
        output_without_notice = {k: v for k, v in output.items() if k != "advisory_notice"}
        if word in json.dumps(output_without_notice).lower():
            return (False, f"S-2: status output contains '{word}' in non-notice field")
    return (True, "S-2: status output has no seal/approve authority claims")


def validate_fixture(path):
    """Validate a single fixture against all rules."""
    try:
        data = load_json(path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return (os.path.basename(path), {"error": str(e), "all_pass": False})

    checks = [
        ("MP-1", check_mp_1, "Register tools classify as advisory"),
        ("MP-2", check_mp_2, "Query/list/status tools are R0"),
        ("MP-3", check_mp_3, "No authority claims in output"),
        ("MP-4", check_mp_4, "Advisory boundary statements present"),
        ("R-1", check_r_1, "Register: receipt authority advisory"),
        ("R-2", check_r_2, "Register: output advisory_only"),
        ("R-3", check_r_3, "Register: non_effects advisory"),
        ("G-1", check_g_1, "Get: receipt_id pattern"),
        ("G-2", check_g_2, "Get: advisory_notice"),
        ("L-1", check_l_1, "List: limit 1-100"),
        ("L-2", check_l_2, "List: advisory_notice"),
        ("S-1", check_s_1, "Status: empty input"),
        ("S-2", check_s_2, "Status: no seal/approve"),
    ]

    results = []
    all_pass = True
    for rule_id, func, desc in checks:
        passed, message = func(data)
        results.append({"rule": rule_id, "description": desc, "passed": passed, "message": message})
        if not passed:
            all_pass = False

    return (os.path.basename(path), {"all_pass": all_pass, "checks": results})


def main():
    args = sys.argv[1:]
    run_all = "--all" in args
    include_invalid = "--include-invalid" in args
    list_rules = "--list-rules" in args
    fixture_paths = [a for a in args if not a.startswith("--")]

    if list_rules:
        print("QA Pilot MCP Surface Rules (MP-1 through MP-4 + tool-specific):")
        print("  MP-1: Register tools classify submitted receipts as advisory evidence only")
        print("  MP-2: Query/list/status tools must be read-only (R0)")
        print("  MP-3: No MCP tool output may claim approval/seal/merge/production-readiness")
        print("  MP-4: All tool outputs include advisory/read-only boundary statements")
        print("  R-1:  Register input receipt authority='advisory'")
        print("  R-2:  Register output advisory_only=true")
        print("  R-3:  Register output non_effects contain advisory language")
        print("  G-1:  Get input receipt_id matches qapr- pattern")
        print("  G-2:  Get output includes advisory_notice")
        print("  L-1:  List input has limit (1-100)")
        print("  L-2:  List output includes advisory_notice")
        print("  S-1:  Status input is empty object")
        print("  S-2:  Status output has no seal/approve claims")
        return 0

    # Determine fixtures directory
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    fixtures_dir = repo_root / "docs" / "examples" / "qa-pilot-mcp-surface"

    if not fixtures_dir.exists():
        print(f"ERROR: Fixtures directory not found: {fixtures_dir}")
        return 1

    if fixture_paths:
        files = [Path(f) for f in fixture_paths]
    elif include_invalid:
        files = sorted(fixtures_dir.glob("*.json"))
    elif run_all:
        files = sorted(fixtures_dir.glob("valid-*.json"))
    else:
        files = sorted(fixtures_dir.glob("valid-*.json"))

    if not files:
        print(f"No fixture files found")
        return 1

    results = []
    valid_pass = 0
    valid_total = 0
    invalid_pass = 0
    invalid_total = 0

    for f in files:
        fname = f.name
        is_invalid = fname.startswith("invalid-")
        result = validate_fixture(str(f))
        results.append(result)

        if not is_invalid:
            valid_total += 1
            if result[1].get("all_pass"):
                valid_pass += 1
        else:
            invalid_total += 1
            if not result[1].get("all_pass"):
                invalid_pass += 1

    has_errors = False
    for fname, r in results:
        if "error" in r:
            print(f"  ❌ {fname} — ERROR: {r['error']}")
            has_errors = True
            continue

        prefix = "✅" if r["all_pass"] else "❌"
        check_count = len(r["checks"])
        pass_count = sum(1 for c in r["checks"] if c["passed"])
        print(f"  {prefix} {fname} — {pass_count}/{check_count} checks pass")

        if not r["all_pass"]:
            has_errors = True
            for c in r["checks"]:
                if not c["passed"]:
                    print(f"       FAIL {c['rule']}: {c['message']}")

    print()
    if include_invalid or run_all:
        print(f"Valid fixtures:   {valid_pass}/{valid_total} passed"
              f"{' (all pass)' if valid_pass == valid_total else ''}")
        print(f"Invalid fixtures: {invalid_pass}/{invalid_total} rejected{' (all rejected)' if invalid_pass == invalid_total else ''}")

        valid_ok = valid_pass == valid_total if valid_total > 0 else True
        invalid_ok = invalid_pass == invalid_total if invalid_total > 0 else True

        if valid_ok and invalid_ok and not has_errors:
            print("\n✅ ALL CHECKS PASS")
            return 0
        else:
            print(f"\n❌ SOME CHECKS FAILED"
                  f" ({valid_pass}/{valid_total} valid pass"
                  f", {invalid_pass}/{invalid_total} invalid rejected)")
            return 1
    else:
        if valid_pass == valid_total and valid_total > 0:
            print("✅ ALL CHECKS PASS")
            return 0
        else:
            print("❌ SOME CHECKS FAILED")
            return 1


if __name__ == "__main__":
    sys.exit(main())
