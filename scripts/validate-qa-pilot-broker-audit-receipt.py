#!/usr/bin/env python3
"""
QA Pilot Broker Audit Receipt Validator — QA-PILOT-BROKER-AUDIT-RECEIPT-STORE-1

Enforces BA-1 through BA-12 on broker audit receipt fixtures.

Rules:
    BA-1: receipt_type must be 'broker_audit'
    BA-2: active_project_id must be 'qa-pilot'
    BA-3: target_project_id must be 'qa-pilot'
    BA-4: requested_tool must belong to sealed QA Pilot MCP/advisory broker surface
    BA-5: handler_path must be QA Pilot project-local (active/qa-pilot/)
    BA-6: authority_level must be 'R0' (read-only) or 'R1' (advisory)
    BA-7: advisory_only must be true
    BA-8: output_effects must not include approval, seal, merge, production_readiness, or runtime_mutation
    BA-9: custody_record_id must be present and non-empty
    BA-10: rollback_reference must be present and non-empty
    BA-11: validation_result must be pass, fail, blocked, or advisory_only
    BA-12: No Librarian runtime/MCPController path may appear as an implementation target
"""

import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-broker-audit"
GOV_DOC = REPO_ROOT / "docs" / "governance" / "QA-PILOT-BROKER-AUDIT-RECEIPT-STORE.md"
SCHEMA_FILE = REPO_ROOT / "docs" / "schemas" / "qa-pilot-broker-audit-receipt.schema.json"

SEALED_SURFACE_TOOLS = [
    "qa_pilot_receipt_register",
    "qa_pilot_receipt_get",
    "qa_pilot_receipt_list",
    "qa_pilot_receipt_status",
]

ALLOWED_AUTHORITY_LEVELS = ["R0", "R1"]
ALLOWED_VALIDATION_RESULTS = ["pass", "fail", "blocked", "advisory_only"]
FORBIDDEN_OUTPUT_EFFECTS = ["approval", "seal", "merge", "production_readiness", "runtime_mutation"]
FORBIDDEN_PATTERNS = ["MCPController.swift", "Sources/App/", "AppEntry.swift"]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_ba_1(data):
    """BA-1: receipt_type must be 'broker_audit'."""
    val = data.get("receipt_type", "")
    passed = val == "broker_audit"
    return (passed, f"receipt_type = '{val}'" if not passed else "receipt_type is broker_audit")


def check_ba_2(data):
    """BA-2: active_project_id must be 'qa-pilot'."""
    val = data.get("active_project_id", "")
    passed = val == "qa-pilot"
    return (passed, f"active_project_id = '{val}'" if not passed else "active_project_id is qa-pilot")


def check_ba_3(data):
    """BA-3: target_project_id must be 'qa-pilot'."""
    val = data.get("target_project_id", "")
    passed = val == "qa-pilot"
    return (passed, f"target_project_id = '{val}'" if not passed else "target_project_id is qa-pilot")


def check_ba_4(data):
    """BA-4: requested_tool must belong to sealed surface."""
    val = data.get("requested_tool", "")
    passed = val in SEALED_SURFACE_TOOLS
    return (passed, f"requested_tool = '{val}'" if not passed else f"tool '{val}' is in sealed surface")


def check_ba_5(data):
    """BA-5: handler_path must be QA Pilot project-local."""
    val = data.get("handler_path", "")
    passed = val.startswith("active/qa-pilot/")
    return (passed, f"handler_path = '{val}'" if not passed else "handler_path is project-local")


def check_ba_6(data):
    """BA-6: authority_level must be R0 or R1."""
    val = data.get("authority_level", "")
    passed = val in ALLOWED_AUTHORITY_LEVELS
    return (passed, f"authority_level = '{val}'" if not passed else f"authority_level is {val}")


def check_ba_7(data):
    """BA-7: advisory_only must be true."""
    val = data.get("advisory_only")
    passed = val is True
    return (passed, f"advisory_only = {val}" if not passed else "advisory_only is true")


def check_ba_8(data):
    """BA-8: output_effects must not include forbidden effects."""
    effects = data.get("output_effects", [])
    forbidden_found = [e for e in effects if e in FORBIDDEN_OUTPUT_EFFECTS]
    passed = len(forbidden_found) == 0
    detail = f"Contains forbidden effects: {forbidden_found}" if forbidden_found else "No forbidden output effects"
    return (passed, detail)


def check_ba_9(data):
    """BA-9: custody_record_id must be present and non-empty."""
    val = data.get("custody_record_id", "")
    passed = bool(val) and len(str(val)) > 0
    return (passed, f"custody_record_id = '{val}'" if not passed else "custody_record_id present")


def check_ba_10(data):
    """BA-10: rollback_reference must be present and non-empty."""
    val = data.get("rollback_reference", "")
    passed = bool(val) and len(str(val)) > 0
    return (passed, f"rollback_reference = '{val}'" if not passed else "rollback_reference present")


def check_ba_11(data):
    """BA-11: validation_result must be a valid value."""
    val = data.get("validation_result", "")
    passed = val in ALLOWED_VALIDATION_RESULTS
    return (passed, f"validation_result = '{val}'" if not passed else f"validation_result is {val}")


def check_ba_12():
    """BA-12: No Librarian runtime/MCPController path in fixture content."""
    for path in [GOV_DOC, SCHEMA_FILE]:
        if not path.exists():
            continue
        content = path.read_text()
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.lower() in content.lower():
                return (False, f"Found Librarian runtime ref '{pattern}' in {path.name}")
    return (True, "BA-12: No Librarian runtime references in audit receipt docs")


def validate_fixture(path):
    """Validate a single fixture against schema and BA rules."""
    try:
        data = load_json(path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return (os.path.basename(path), {"error": str(e), "all_pass": False})

    schema_path = SCHEMA_FILE
    schema_valid = True
    schema_msg = "Schema validation skipped (jsonschema not available)"

    try:
        import jsonschema
        schema = load_json(str(schema_path))
        jsonschema.validate(data, schema)
        schema_valid = True
        schema_msg = "Schema validation passed"
    except ImportError:
        required = ["audit_id", "receipt_type", "active_project_id", "target_project_id",
                     "requested_tool", "custody_record_id", "handler_path", "authority_level",
                     "advisory_only", "output_effects", "audit_timestamp", "rollback_reference",
                     "validation_result"]
        missing = [f for f in required if f not in data]
        if missing:
            schema_valid = False
            schema_msg = f"Missing required fields: {missing}"
    except jsonschema.ValidationError as e:
        schema_valid = False
        schema_msg = f"Schema validation failed: {e.message}"

    checks = [
        ("BA-1", lambda: check_ba_1(data), "receipt_type is broker_audit"),
        ("BA-2", lambda: check_ba_2(data), "active_project_id is qa-pilot"),
        ("BA-3", lambda: check_ba_3(data), "target_project_id is qa-pilot"),
        ("BA-4", lambda: check_ba_4(data), "tool in sealed surface"),
        ("BA-5", lambda: check_ba_5(data), "handler_path project-local"),
        ("BA-6", lambda: check_ba_6(data), "authority_level R0 or R1"),
        ("BA-7", lambda: check_ba_7(data), "advisory_only is true"),
        ("BA-8", lambda: check_ba_8(data), "no forbidden output effects"),
        ("BA-9", lambda: check_ba_9(data), "custody_record_id present"),
        ("BA-10", lambda: check_ba_10(data), "rollback_reference present"),
        ("BA-11", lambda: check_ba_11(data), "validation_result valid"),
    ]

    all_pass = schema_valid
    results = [{"rule": "SCHEMA", "description": "Schema valid", "passed": schema_valid, "message": schema_msg}]

    for rule_id, func, desc in checks:
        passed, message = func()
        results.append({"rule": rule_id, "description": desc, "passed": passed, "message": message})
        if not passed:
            all_pass = False

    return (os.path.basename(path), {"all_pass": all_pass, "checks": results})


def main():
    args = sys.argv[1:]
    list_rules = "--list-rules" in args
    include_invalid = "--include-invalid" in args

    if list_rules:
        rules = [
            "BA-1: receipt_type must be 'broker_audit'",
            "BA-2: active_project_id must be 'qa-pilot'",
            "BA-3: target_project_id must be 'qa-pilot'",
            "BA-4: requested_tool must belong to sealed surface",
            "BA-5: handler_path must be QA Pilot project-local",
            "BA-6: authority_level must be R0 or R1",
            "BA-7: advisory_only must be true",
            "BA-8: output_effects must not contain approval/seal/merge/production_readiness/runtime_mutation",
            "BA-9: custody_record_id must be present and non-empty",
            "BA-10: rollback_reference must be present and non-empty",
            "BA-11: validation_result must be pass/fail/blocked/advisory_only",
            "BA-12: No Librarian runtime/MCPController path in implementation targets",
        ]
        for r in rules:
            print(f"  {r}")
        return 0

    if not FIXTURES_DIR.exists():
        print(f"ERROR: Fixtures directory not found: {FIXTURES_DIR}")
        return 1

    if include_invalid:
        files = sorted(FIXTURES_DIR.glob("*.json"))
    else:
        files = sorted(FIXTURES_DIR.glob("valid-*.json"))

    if not files:
        print("No fixture files found")
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

    parse_errors = False
    for fname, r in results:
        if "error" in r:
            print(f"  ❌ {fname} — ERROR: {r['error']}")
            parse_errors = True
            continue
        prefix = "✅" if r["all_pass"] else "❌"
        check_count = len(r["checks"])
        pass_count = sum(1 for c in r["checks"] if c["passed"])
        print(f"  {prefix} {fname} — {pass_count}/{check_count} checks pass")
        if not r["all_pass"]:
            for c in r["checks"]:
                if not c["passed"]:
                    print(f"       FAIL {c['rule']}: {c['message']}")

    ba12_passed, ba12_msg = check_ba_12()
    ba12_prefix = "✅" if ba12_passed else "❌"
    print(f"  {ba12_prefix} BA-12: {ba12_msg}")

    print()
    if include_invalid:
        print(f"Valid fixtures:   {valid_pass}/{valid_total} passed")
        print(f"Invalid fixtures: {invalid_pass}/{invalid_total} rejected")

    all_ok = (valid_pass == valid_total if valid_total > 0 else True)
    all_rejected = (invalid_pass == invalid_total if invalid_total > 0 else True)

    if all_ok and all_rejected and ba12_passed and not parse_errors:
        print("\n✅ ALL CHECKS PASS")
        return 0
    else:
        failures = []
        if not all_ok: failures.append("valid fixtures")
        if not all_rejected: failures.append("invalid fixture rejection")
        if not ba12_passed: failures.append("BA-12")
        if parse_errors: failures.append("parse errors")
        print(f"\n❌ CHECKS FAILED: {', '.join(failures)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
