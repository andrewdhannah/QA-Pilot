#!/usr/bin/env python3
"""
QA Pilot Training Sim Validator — QA-PILOT-LOCAL-TRAINING-SIM-1

Validates training simulation cases against governance rules.
Every sim case must be advisory-only and cannot authorize any
downstream action without Owner decision.

Rules:
    TS-1:  sim_id must be present and match expected pattern
    TS-2:  sim_type must be a known type
    TS-3:  advisory must be true (sim cases are advisory/test material only)
    TS-4:  owner_decision_required must be true
    TS-5:  source must reference a valid ingested packet (ingest_id, hash, type)
    TS-6:  reproducible_from must be within QA Pilot local store
    TS-7:  No mutation-authorizing keys or Librarian paths in inputs
    TS-8:  No cross-project write claims in inputs
    TS-9:  Unsafe sim cases must have expected_behavior containing reject/quarantine/block
    TS-10: No Librarian runtime/MCPController path references
"""

import json
import os
import sys
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-training-sim"
CASE_SCHEMA = REPO_ROOT / "docs" / "schemas" / "qa-pilot-training-sim-case.schema.json"
RESULT_SCHEMA = REPO_ROOT / "docs" / "schemas" / "qa-pilot-training-sim-result.schema.json"
INGEST_INDEX = REPO_ROOT / "data" / "packets" / "ingested-index.json"

KNOWN_SIM_TYPES = ["advisory_training", "boundary_test", "rejection_test", "reconstruction_test"]
FORBIDDEN_INPUT_KEYS = ["seal_action", "approve_action", "merge_action", "production_readiness_action", "runtime_mutation_action"]
FORBIDDEN_MUTATION_PATTERNS = ["active/librarian/", "librarian DB write", "librarian MCP register"]
FORBIDDEN_CROSS_PROJECT_KEYS = ["cross_project_write_authorized", "librarian_write_authorized"]
UNSAFE_EXPECTED_PATTERNS = ["reject", "quarantine", "fail", "block", "deny"]
SAFE_STORE_PREFIX = "data/packets/ingested"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Rule checkers ────────────────────────────────────────────────────────

def check_ts_1(data):
    """TS-1: sim_id must be present and match expected pattern."""
    sid = data.get("sim_id", "")
    if not sid:
        return (False, "sim_id is empty")
    if not re.match(r"^qa-pilot-sim-[a-z0-9-]+$", sid):
        return (False, f"sim_id '{sid}' does not match pattern qa-pilot-sim-[a-z0-9-]+")
    return (True, f"sim_id is '{sid}'")


def check_ts_2(data):
    """TS-2: sim_type must be a known type."""
    st = data.get("sim_type", "")
    passed = st in KNOWN_SIM_TYPES
    detail = f"sim_type = '{st}'" if not passed else f"sim_type is '{st}'"
    return (passed, detail)


def check_ts_3(data):
    """TS-3: advisory must be true."""
    adv = data.get("advisory")
    passed = adv is True
    return (passed, f"advisory = {adv}" if not passed else "advisory is true")


def check_ts_4(data):
    """TS-4: owner_decision_required must be true."""
    odr = data.get("owner_decision_required")
    passed = odr is True
    return (passed, f"owner_decision_required = {odr}" if not passed else "owner_decision_required is true")


def check_ts_5(data):
    """TS-5: source must reference a valid ingested packet."""
    source = data.get("source", {})
    if not isinstance(source, dict):
        return (False, "source is not an object")
    ingest_id = source.get("ingest_id", "")
    packet_hash = source.get("packet_hash", "")
    packet_type = source.get("packet_type", "")
    if not ingest_id:
        return (False, "source.ingest_id is empty")
    if not re.match(r"^[a-f0-9]{64}$", packet_hash):
        return (False, f"source.packet_hash '{packet_hash}' is not valid SHA-256")
    if not packet_type:
        return (False, "source.packet_type is empty")
    return (True, f"source references ingest_id='{ingest_id}' type='{packet_type}'")


def check_ts_6(data):
    """TS-6: reproducible_from must be within QA Pilot local store."""
    rf = data.get("reproducible_from", "")
    if not rf.startswith(SAFE_STORE_PREFIX):
        return (False, f"reproducible_from '{rf}' is outside local store (must start with '{SAFE_STORE_PREFIX}')")
    return (True, f"reproducible_from is local: '{rf}'")


def check_ts_7(data):
    """TS-7: No mutation-authorizing keys or Librarian paths in inputs."""
    inputs = data.get("inputs", {})
    if not isinstance(inputs, dict):
        return (True, "No inputs to check (skipped)")

    # Check input keys for mutation-action patterns
    for key in inputs.keys():
        key_lower = key.lower()
        for forbidden in FORBIDDEN_INPUT_KEYS:
            if forbidden.lower() in key_lower:
                return (False, f"Input key '{key}' contains mutation-authorizing pattern")

    # Check input values for Librarian mutation paths
    inputs_str = json.dumps(inputs).lower()
    for pattern in FORBIDDEN_MUTATION_PATTERNS:
        if pattern.lower() in inputs_str:
            return (False, f"Inputs contain Librarian mutation path pattern '{pattern}'")

    return (True, "No mutation-authorizing keys or Librarian paths in inputs")


def check_ts_8(data):
    """TS-8: No cross-project write claims in inputs."""
    inputs = data.get("inputs", {})
    if not isinstance(inputs, dict):
        return (True, "No inputs to check (skipped)")

    for key in inputs.keys():
        for forbidden in FORBIDDEN_CROSS_PROJECT_KEYS:
            if forbidden.lower() in key.lower():
                return (False, f"Input key '{key}' contains cross-project write claim")

    inputs_str = json.dumps(inputs).lower()
    if "cross_project_write_authorized" in inputs_str:
        # If a value literally says true, flag it
        if '"cross_project_write_authorized": true' in inputs_str or "'cross_project_write_authorized': true" in inputs_str:
            return (False, "Inputs contain cross_project_write_authorized=true claim")

    return (True, "No cross-project write claims in inputs")


def check_ts_9(data):
    """TS-9: Unsafe sim cases must have expected_behavior containing reject/quarantine/block."""
    unsafe = data.get("unsafe_action_required", False)
    if not unsafe:
        return (True, "Not unsafe — skip check")

    expected = data.get("expected_behavior", "").lower()
    has_pattern = any(p in expected for p in UNSAFE_EXPECTED_PATTERNS)
    if not has_pattern:
        return (False, "Unsafe sim case but expected_behavior does not contain reject/quarantine/fail/block/deny")
    return (True, f"Unsafe sim case expected_behavior contains rejection indicator")


def check_ts_10():
    """TS-10: No Librarian runtime/MCPController path in sim schema or fixtures."""
    findings = []
    for path in [CASE_SCHEMA, RESULT_SCHEMA]:
        if not path.exists():
            continue
        content = path.read_text()
        forbidden = ["MCPController.swift", "Sources/App/", "AppEntry.swift", "librarian/scripts"]
        for pattern in forbidden:
            if pattern.lower() in content.lower():
                findings.append(f"Found '{pattern}' in {path.name}")
    if findings:
        return (False, "; ".join(findings))
    return (True, "No Librarian runtime references in sim schema")


# ── Fixture validation ──────────────────────────────────────────────────

def validate_fixture(path):
    """Validate a single fixture against all TS rules."""
    try:
        data = load_json(path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return (os.path.basename(path), {"error": str(e), "all_pass": False})

    # Schema validation if jsonschema available
    schema_valid = True
    schema_msg = "Schema validation skipped"
    try:
        import jsonschema
        schema = load_json(str(CASE_SCHEMA))
        jsonschema.validate(data, schema)
        schema_valid = True
        schema_msg = "Schema validation passed"
    except ImportError:
        required = ["sim_id", "sim_type", "source", "scenario", "expected_behavior", "advisory", "owner_decision_required", "generated_at", "reproducible_from"]
        missing = [f for f in required if f not in data]
        if missing:
            schema_valid = False
            schema_msg = f"Missing required fields: {missing}"
    except jsonschema.ValidationError as e:
        schema_valid = False
        schema_msg = f"Schema validation failed: {e.message}"

    checks = [
        ("TS-1", check_ts_1(data), "sim_id pattern"),
        ("TS-2", check_ts_2(data), "sim_type known"),
        ("TS-3", check_ts_3(data), "advisory true"),
        ("TS-4", check_ts_4(data), "owner_decision_required true"),
        ("TS-5", check_ts_5(data), "source references valid packet"),
        ("TS-6", check_ts_6(data), "reproducible_from local"),
        ("TS-7", check_ts_7(data), "no mutation paths"),
        ("TS-8", check_ts_8(data), "no cross-project write claims"),
        ("TS-9", check_ts_9(data), "unsafe case expected_behavior"),
    ]

    all_pass = schema_valid
    results = [{"rule": "SCHEMA", "passed": schema_valid, "message": schema_msg}]

    for rule_id, (passed, message), desc in checks:
        results.append({"rule": rule_id, "passed": passed, "message": message})
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
            "TS-1: sim_id must be present and match pattern qa-pilot-sim-[a-z0-9-]+",
            "TS-2: sim_type must be a known type (advisory_training/boundary_test/rejection_test/reconstruction_test)",
            "TS-3: advisory must be true (sim cases are advisory/test material only)",
            "TS-4: owner_decision_required must be true (Owner decision required for downstream apply)",
            "TS-5: source must reference a valid ingested packet (ingest_id, hash, type)",
            "TS-6: reproducible_from must be within QA Pilot local store (data/packets/ingested/)",
            "TS-7: No mutation-authorizing keys or Librarian mutation paths in inputs",
            "TS-8: No cross-project write claims in inputs",
            "TS-9: Unsafe sim cases must have expected_behavior containing reject/quarantine/block/deny",
            "TS-10: No Librarian runtime/MCPController path references in sim schema",
        ]
        for r in rules:
            print(f"  {r}")
        return 0

    print("QA Pilot Training Sim Validator — QA-PILOT-LOCAL-TRAINING-SIM-1")
    print(f"Fixtures: {FIXTURES_DIR}")
    print()

    if not FIXTURES_DIR.exists():
        print(f"ERROR: Fixtures directory not found: {FIXTURES_DIR}")
        return 1

    if include_invalid:
        files = sorted(FIXTURES_DIR.glob("*.json"))
    else:
        files = sorted(FIXTURES_DIR.glob("sim-valid-*.json"))

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
    ts10_passed, ts10_msg = check_ts_10()
    ts10_prefix = "✅" if ts10_passed else "❌"
    print(f"  {ts10_prefix} TS-10: {ts10_msg}")

    print()
    if include_invalid:
        print(f"Valid fixtures:   {valid_pass}/{valid_total} passed")
        print(f"Invalid fixtures: {invalid_rejected}/{invalid_total} rejected")

    all_ok = (valid_pass == valid_total if valid_total > 0 else True)
    all_rejected = (invalid_rejected == invalid_total if invalid_total > 0 else True)

    if all_ok and all_rejected and ts10_passed and not parse_errors:
        print("\n✅ ALL CHECKS PASS")
        return 0
    else:
        failures = []
        if not all_ok: failures.append("valid fixtures")
        if not all_rejected: failures.append("invalid fixture rejection")
        if not ts10_passed: failures.append("TS-10")
        if parse_errors: failures.append("parse errors")
        print(f"\n❌ CHECKS FAILED: {', '.join(failures)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
