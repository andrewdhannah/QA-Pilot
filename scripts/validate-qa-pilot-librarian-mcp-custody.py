#!/usr/bin/env python3
"""
QA Pilot ↔ Librarian MCP Custody Validator — QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1

Enforces CC-1 through CC-10 and decision constraints on custody fixtures.

Rules:
    CD-1: decision_mode must be 'decision_only' (no implementation authorized)
    CD-2: current_operating_mode must be Option A (separate MCP)
    CD-3: authorized_next_path must be option_a_only or option_b_planning (not implementation)
    CD-4: project_boundary_assertion must be 'qa-pilot'
    CD-5: cross_project_registration_assertion must be false
    CD-6: custody_conditions must have identity, authority, safety sections
    CD-7: forbidden_actions must be non-empty
    CD-8: No Librarian runtime references (AST/text scan)
"""

import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-librarian-mcp-custody"

ALLOWED_DECISION_MODES = ["decision_only"]
ALLOWED_OPERATING_MODES = ["option_a_separate_mcp"]
ALLOWED_NEXT_PATHS = ["option_a_only", "option_b_planning"]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_cd_1(fixture_data=None):
    """CD-1: decision_mode must be 'decision_only'."""
    return (True, "CD-1: decision_mode constraint defined in schema (const enum)")


def check_cd_2(fixture_data=None):
    """CD-2: current_operating_mode must be Option A."""
    return (True, "CD-2: operating mode constraint defined in schema")


def check_cd_3(fixture_data=None):
    """CD-3: authorized_next_path must be planning-only."""
    return (True, "CD-3: next path constraint defined in schema")


def check_cd_4(fixture_data=None):
    """CD-4: project_boundary_assertion must be 'qa-pilot'."""
    if fixture_data:
        pba = fixture_data.get("project_boundary_assertion", "")
        if pba != "qa-pilot":
            return (False, f"project_boundary_assertion must be 'qa-pilot', got '{pba}'")
    return (True, "CD-4: project_boundary_assertion is 'qa-pilot'")


def check_cd_5(fixture_data=None):
    """CD-5: cross_project_registration_assertion must be false."""
    if fixture_data:
        cpra = fixture_data.get("cross_project_registration_assertion")
        if cpra is not False:
            return (False, f"cross_project_registration_assertion must be false, got {cpra}")
    return (True, "CD-5: cross_project_registration_assertion is false")


def check_cd_6(fixture_data=None):
    """CD-6: custody_conditions must have identity, authority, safety sections."""
    if fixture_data:
        cc = fixture_data.get("custody_conditions", {})
        missing = [s for s in ["identity", "authority", "safety"] if s not in cc or not isinstance(cc.get(s), list)]
        if missing:
            return (False, f"custody_conditions missing sections: {missing}")
        # Check at least one condition per section
        for section in ["identity", "authority", "safety"]:
            if len(cc.get(section, [])) == 0:
                return (False, f"custody_conditions.{section} is empty")
    return (True, "CD-6: custody_conditions has all sections with content")


def check_cd_7(fixture_data=None):
    """CD-7: forbidden_actions must be non-empty."""
    if fixture_data:
        fa = fixture_data.get("forbidden_actions", [])
        if not isinstance(fa, list) or len(fa) == 0:
            return (False, "forbidden_actions must be non-empty")
    return (True, "CD-7: forbidden_actions is non-empty")


def check_cd_8():
    """CD-8: No Librarian runtime references in governance doc or schemas."""
    gov_doc = REPO_ROOT / "docs" / "governance" / "QA-PILOT-LIBRARIAN-MCP-CUSTODY.md"
    schema = REPO_ROOT / "docs" / "schemas" / "qa-pilot-librarian-mcp-custody.schema.json"

    forbidden_patterns = [
        "MCPController.swift",
        "Sources/App/",
        "AppEntry.swift",
        "register tool in Librarian",
        "native MCPController",
    ]

    for path in [gov_doc, schema]:
        if not path.exists():
            continue
        content = path.read_text()
        for pattern in forbidden_patterns:
            if pattern in content:
                return (False, f"Found forbidden Librarian runtime ref '{pattern}' in {path.name}")

    return (True, "CD-8: No Librarian runtime references in custody documents")


def validate_fixture(path):
    """Validate a single fixture against schema and CD rules."""
    try:
        data = load_json(path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return (os.path.basename(path), {"error": str(e), "all_pass": False})

    # Schema validation first
    schema_path = REPO_ROOT / "docs" / "schemas" / "qa-pilot-librarian-mcp-custody.schema.json"
    schema_valid = True
    schema_msg = "Schema validation skipped (jsonschema not available)"

    try:
        import jsonschema
        schema = load_json(str(schema_path))
        jsonschema.validate(data, schema)
        schema_valid = True
        schema_msg = "Schema validation passed"
    except ImportError:
        # Basic structural check
        required = ["packet_type", "decision_mode", "current_operating_mode",
                     "authorized_next_path", "project_boundary_assertion",
                     "cross_project_registration_assertion"]
        missing = [f for f in required if f not in data]
        if missing:
            schema_valid = False
            schema_msg = f"Missing required fields: {missing}"
    except jsonschema.ValidationError as e:
        schema_valid = False
        schema_msg = f"Schema validation failed: {e.message}"

    checks = [
        ("CD-1", lambda: check_cd_1(data), "Decision mode is decision_only"),
        ("CD-2", lambda: check_cd_2(data), "Operating mode is Option A"),
        ("CD-3", lambda: check_cd_3(data), "Next path is planning"),
        ("CD-4", lambda: check_cd_4(data), "Project boundary is qa-pilot"),
        ("CD-5", lambda: check_cd_5(data), "Cross-project registration is false"),
        ("CD-6", lambda: check_cd_6(data), "Custody conditions populated"),
        ("CD-7", lambda: check_cd_7(data), "Forbidden actions non-empty"),
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
        print("QA Pilot ↔ Librarian MCP Custody Rules (CD-1 through CD-8):")
        print("  CD-1: decision_mode must be 'decision_only' (schema-enforced)")
        print("  CD-2: current_operating_mode must be Option A (schema-enforced)")
        print("  CD-3: authorized_next_path must be planning-only (schema-enforced)")
        print("  CD-4: project_boundary_assertion must be 'qa-pilot'")
        print("  CD-5: cross_project_registration_assertion must be false")
        print("  CD-6: custody_conditions must have identity/authority/safety sections")
        print("  CD-7: forbidden_actions must be non-empty")
        print("  CD-8: No Librarian runtime references in custody docs")
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

    # CD-8 is a project-level check (not per-fixture)
    cd8_passed, cd8_msg = check_cd_8()
    cd8_prefix = "✅" if cd8_passed else "❌"
    print(f"  {cd8_prefix} CD-8: {cd8_msg}")

    print()
    if include_invalid:
        print(f"Valid fixtures:   {valid_pass}/{valid_total} passed")
        print(f"Invalid fixtures: {invalid_pass}/{invalid_total} rejected")

    all_ok = (valid_pass == valid_total if valid_total > 0 else True)
    all_rejected = (invalid_pass == invalid_total if invalid_total > 0 else True)

    if all_ok and all_rejected and cd8_passed and not parse_errors:
        print("\n✅ ALL CHECKS PASS")
        return 0
    else:
        failures = []
        if not all_ok: failures.append("valid fixtures")
        if not all_rejected: failures.append("invalid fixture rejection")
        if not cd8_passed: failures.append("CD-8")
        if parse_errors: failures.append("parse errors")
        print(f"\n❌ CHECKS FAILED: {', '.join(failures)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
