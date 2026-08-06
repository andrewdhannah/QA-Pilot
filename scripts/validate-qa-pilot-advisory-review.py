#!/usr/bin/env python3
"""
QA Pilot Training Sim Advisory Review Validator — QA-PILOT-TRAINING-SIM-ADVISORY-REVIEW-1

Validates advisory review outputs for training sim cases/results.
Every review output must be read-only advisory with no apply path,
no training behavior, no MCP bridge behavior, no packet mutation,
no cross-project write, and Owner decision required.

Rules:
    AR-1:  review_id must be present and match expected pattern
    AR-2:  source_sim_id must reference a valid sim case pattern
    AR-3:  review_type must be a known type (summary/detailed)
    AR-4:  advisory must be true (review output is advisory-only)
    AR-5:  no_apply_path must be true (no packet application path)
    AR-6:  no_train_behavior must be true (no model-training behavior)
    AR-7:  no_bridge_behavior must be true (no MCP bridge behavior)
    AR-8:  no_mutation_authorized must be true (no packet mutation)
    AR-9:  no_cross_project_write must be true (no cross-project write)
    AR-10: owner_decision_required must be true (Owner decision needed)
"""

import json
import os
import sys
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-advisory-review"
REVIEW_SCHEMA = REPO_ROOT / "docs" / "schemas" / "qa-pilot-advisory-review.schema.json"

GUARD_BOOLEAN_FIELDS = [
    ("AR-4", "advisory"),
    ("AR-5", "no_apply_path"),
    ("AR-6", "no_train_behavior"),
    ("AR-7", "no_bridge_behavior"),
    ("AR-8", "no_mutation_authorized"),
    ("AR-9", "no_cross_project_write"),
    ("AR-10", "owner_decision_required"),
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Rule checkers ────────────────────────────────────────────────────────

def check_ar_1(data):
    """AR-1: review_id must be present and match expected pattern."""
    rid = data.get("review_id", "")
    if not rid:
        return (False, "review_id is empty")
    if not re.match(r"^qa-pilot-review-[a-z0-9-]+$", rid):
        return (False, f"review_id '{rid}' does not match pattern qa-pilot-review-[a-z0-9-]+")
    return (True, f"review_id is '{rid}'")


def check_ar_2(data):
    """AR-2: source_sim_id must reference a valid sim case pattern."""
    sid = data.get("source_sim_id", "")
    if not sid:
        return (False, "source_sim_id is empty")
    if not re.match(r"^qa-pilot-sim-[a-z0-9-]+$", sid):
        return (False, f"source_sim_id '{sid}' does not match sim pattern")
    return (True, f"source_sim_id references sim '{sid}'")


def check_ar_3(data):
    """AR-3: review_type must be a known type."""
    rt = data.get("review_type", "")
    passed = rt in ("summary", "detailed")
    return (passed, f"review_type = '{rt}'" if not passed else f"review_type is '{rt}'")


def check_guard_bool(data, rule_id, field):
    """Check a required guard boolean field is true."""
    val = data.get(field)
    passed = val is True
    return (passed, f"{field} = {val}" if not passed else f"{field} is true")


def check_ar_4_to_10(data):
    """Check all guard boolean invariants (AR-4 through AR-10)."""
    results = []
    for rule_id, field in GUARD_BOOLEAN_FIELDS:
        passed, msg = check_guard_bool(data, rule_id, field)
        results.append((rule_id, passed, msg))
    return results


def check_ar_11():
    """AR-11: No Librarian runtime/MCPController path in review schema."""
    if not REVIEW_SCHEMA.exists():
        return (True, "Schema not found — skip")
    content = REVIEW_SCHEMA.read_text()
    forbidden = ["MCPController.swift", "Sources/App/", "AppEntry.swift", "librarian/scripts"]
    findings = [p for p in forbidden if p.lower() in content.lower()]
    if findings:
        return (False, f"Found Librarian refs in schema: {findings}")
    return (True, "No Librarian runtime references in review schema")


# ── Fixture validation ──────────────────────────────────────────────────

def validate_fixture(path):
    """Validate a single fixture against all AR rules."""
    try:
        data = load_json(path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return (os.path.basename(path), {"error": str(e), "all_pass": False})

    # Schema validation
    schema_valid = True
    schema_msg = "Schema validation skipped"
    try:
        import jsonschema
        schema = load_json(str(REVIEW_SCHEMA))
        jsonschema.validate(data, schema)
        schema_valid = True
        schema_msg = "Schema validation passed"
    except ImportError:
        required = [
            "review_id", "source_sim_id", "review_type", "summary",
            "advisory", "no_apply_path", "no_train_behavior", "no_bridge_behavior",
            "no_mutation_authorized", "no_cross_project_write",
            "owner_decision_required", "generated_at"
        ]
        missing = [f for f in required if f not in data]
        if missing:
            schema_valid = False
            schema_msg = f"Missing required fields: {missing}"
    except jsonschema.ValidationError as e:
        schema_valid = False
        schema_msg = f"Schema validation failed: {e.message}"

    # Run AR rules
    checks = [
        ("AR-1", check_ar_1(data)),
        ("AR-2", check_ar_2(data)),
        ("AR-3", check_ar_3(data)),
    ]
    for rule_id, passed, msg in check_ar_4_to_10(data):
        checks.append((rule_id, (passed, msg)))

    all_pass = schema_valid
    results = [{"rule": "SCHEMA", "passed": schema_valid, "message": schema_msg}]

    for rule_id, (passed, msg) in checks:
        results.append({"rule": rule_id, "passed": passed, "message": msg})
        if not passed:
            all_pass = False

    return (os.path.basename(path), {"all_pass": all_pass, "checks": results})


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    list_rules = "--list-rules" in args
    include_invalid = "--include-invalid" in args

    if list_rules:
        rules = [
            "AR-1: review_id must match pattern qa-pilot-review-[a-z0-9-]+",
            "AR-2: source_sim_id must reference a valid sim case pattern",
            "AR-3: review_type must be summary or detailed",
            "AR-4: advisory must be true (review output is advisory-only)",
            "AR-5: no_apply_path must be true (no packet application path)",
            "AR-6: no_train_behavior must be true (no model-training behavior)",
            "AR-7: no_bridge_behavior must be true (no MCP bridge behavior)",
            "AR-8: no_mutation_authorized must be true (no packet mutation)",
            "AR-9: no_cross_project_write must be true (no cross-project write)",
            "AR-10: owner_decision_required must be true (Owner decision required)",
            "AR-11: No Librarian runtime/MCPController path references in review schema",
        ]
        for r in rules:
            print(f"  {r}")
        return 0

    print("QA Pilot Advisory Review Validator — QA-PILOT-TRAINING-SIM-ADVISORY-REVIEW-1")
    print(f"Fixtures: {FIXTURES_DIR}")
    print()

    if not FIXTURES_DIR.exists():
        print(f"ERROR: Fixtures directory not found: {FIXTURES_DIR}")
        return 1

    if include_invalid:
        files = sorted(FIXTURES_DIR.glob("*.json"))
    else:
        files = sorted(FIXTURES_DIR.glob("review-valid-*.json"))

    if not files:
        print("No fixture files found")
        return 1

    valid_pass = 0
    valid_total = 0
    invalid_rejected = 0
    invalid_total = 0
    parse_errors = False

    for f in files:
        fname = f.name
        is_invalid = "invalid" in fname
        result = validate_fixture(str(f))
        r = result[1]

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

        if not is_invalid:
            valid_total += 1
            if r["all_pass"]:
                valid_pass += 1
        else:
            invalid_total += 1
            if not r["all_pass"]:
                invalid_rejected += 1

    print()
    ar11_passed, ar11_msg = check_ar_11()
    ar11_prefix = "✅" if ar11_passed else "❌"
    print(f"  {ar11_prefix} AR-11: {ar11_msg}")

    print()
    if include_invalid:
        print(f"Valid fixtures:   {valid_pass}/{valid_total} passed")
        print(f"Invalid fixtures: {invalid_rejected}/{invalid_total} rejected")

    all_ok = (valid_pass == valid_total if valid_total > 0 else True)
    all_rejected = (invalid_rejected == invalid_total if invalid_total > 0 else True)

    if all_ok and all_rejected and ar11_passed and not parse_errors:
        print("\n✅ ALL CHECKS PASS")
        return 0
    else:
        failures = []
        if not all_ok: failures.append("valid fixtures")
        if not all_rejected: failures.append("invalid fixture rejection")
        if not ar11_passed: failures.append("AR-11")
        if parse_errors: failures.append("parse errors")
        print(f"\n❌ CHECKS FAILED: {', '.join(failures)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
