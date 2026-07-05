#!/usr/bin/env python3
"""
QA Pilot QA Packet Ingest Validator — QA-PILOT-QA-PACKET-INGEST-1

Validates governed QA export packets against schema and ingestion rules.

Rules:
    PI-1:  packet_type must be a known packet type
    PI-2:  source_project must be 'librarian'
    PI-3:  consumer_project must be 'qa-pilot'
    PI-4:  authority_status must be valid (authoritative_export/advisory_copy/training_simulated)
    PI-5:  Must not claim authoritative_export when payload is empty or lacks canonical fields
    PI-6:  generated_at must be valid ISO 8601 UTC (Z suffix)
    PI-7:  source_packet_hash must be present and valid SHA-256 hex
    PI-8:  allowed_use must not contain forbidden use categories
    PI-9:  forbidden_use must contain all required forbidden categories
    PI-10: owner_decision_required_for_apply must be true
    PI-11: Must not contain direct Librarian mutation paths in payload
    PI-12: Must not claim training_simulated as authoritative_export
    PI-13: generated_at must not be in the future
    PI-14: No Librarian runtime/MCPController path references
"""

import json
import os
import sys
import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-qa-packet-ingest"
GOV_DOC = REPO_ROOT / "docs" / "governance" / "QA-PILOT-QA-PACKET-INGEST.md"
SCHEMA_FILE = REPO_ROOT / "docs" / "schemas" / "qa-pilot-qa-packet-ingest.schema.json"

KNOWN_PACKET_TYPES = ["qa_claim_registry", "project_state", "milestone_regression", "training_source"]
VALID_AUTHORITY_STATUSES = ["authoritative_export", "advisory_copy", "training_simulated"]
VALID_ALLOWED_USES = ["qa_regression", "training_doc_generation", "simulation"]
REQUIRED_FORBIDDEN_USES = ["direct_librarian_mutation", "owner_decision_substitution", "authority_promotion"]
FORBIDDEN_ALLOWED_USES = ["direct_librarian_mutation"]
FORBIDDEN_LIBRARIAN_PATTERNS = ["MCPController.swift", "Sources/App/", "AppEntry.swift", "librarian/scripts"]
FORBIDDEN_MUTATION_KEYS = ["seal_action", "approve_action", "merge_action", "production_readiness_action", "runtime_mutation_action"]
FORBIDDEN_MUTATION_PATTERNS = ["active/librarian/", "librarian DB write", "librarian MCP register"]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_pi_1(data):
    """PI-1: packet_type must be a known packet type."""
    val = data.get("packet_type", "")
    passed = val in KNOWN_PACKET_TYPES
    return (passed, f"packet_type = '{val}'" if not passed else f"packet_type is '{val}'")


def check_pi_2(data):
    """PI-2: source_project must be 'librarian'."""
    val = data.get("source_project", "")
    passed = val == "librarian"
    return (passed, f"source_project = '{val}'" if not passed else "source_project is librarian")


def check_pi_3(data):
    """PI-3: consumer_project must be 'qa-pilot'."""
    val = data.get("consumer_project", "")
    passed = val == "qa-pilot"
    return (passed, f"consumer_project = '{val}'" if not passed else "consumer_project is qa-pilot")


def check_pi_4(data):
    """PI-4: authority_status must be valid."""
    val = data.get("authority_status", "")
    passed = val in VALID_AUTHORITY_STATUSES
    return (passed, f"authority_status = '{val}'" if not passed else f"authority_status is '{val}'")


def check_pi_5(data):
    """PI-5: Must not claim authoritative_export when payload is empty or lacks canonical fields."""
    status = data.get("authority_status", "")
    if status != "authoritative_export":
        return (True, "Not authoritative_export — skip check")
    payload = data.get("payload")
    if not payload or not isinstance(payload, dict) or len(payload) == 0:
        return (False, "authoritative_export but payload is empty or missing")
    return (True, "authoritative_export has payload")


def check_pi_6(data):
    """PI-6: generated_at must be valid ISO 8601 UTC (Z suffix)."""
    val = data.get("generated_at", "")
    import re
    if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", val):
        return (False, f"generated_at = '{val}' does not match ISO 8601 UTC pattern")
    return (True, f"generated_at is valid ISO 8601 UTC")


def check_pi_7(data):
    """PI-7: source_packet_hash must be present and valid SHA-256 hex."""
    val = data.get("source_packet_hash", "")
    import re
    if not re.match(r"^[a-f0-9]{64}$", val):
        if val == "":
            return (False, "source_packet_hash is empty")
        return (False, f"source_packet_hash = '{val}' is not valid SHA-256 hex")
    return (True, "source_packet_hash is valid SHA-256")


def check_pi_8(data):
    """PI-8: allowed_use must not contain forbidden use categories."""
    uses = data.get("allowed_use", [])
    forbidden_found = [u for u in uses if u in FORBIDDEN_ALLOWED_USES]
    passed = len(forbidden_found) == 0
    detail = f"Contains forbidden allowed_use: {forbidden_found}" if forbidden_found else "No forbidden allowed_use"
    return (passed, detail)


def check_pi_9(data):
    """PI-9: forbidden_use must contain all required forbidden categories."""
    uses = data.get("forbidden_use", [])
    missing = [r for r in REQUIRED_FORBIDDEN_USES if r not in uses]
    passed = len(missing) == 0
    detail = f"Missing required forbidden_use: {missing}" if missing else "All required forbidden_use present"
    return (passed, detail)


def check_pi_10(data):
    """PI-10: owner_decision_required_for_apply must be true."""
    val = data.get("owner_decision_required_for_apply")
    passed = val is True
    return (passed, f"owner_decision_required_for_apply = {val}" if not passed else "owner_decision_required_for_apply is true")


def check_pi_11(data):
    """PI-11: Must not contain direct Librarian mutation paths in payload."""
    payload = data.get("payload")
    if not payload or not isinstance(payload, dict):
        return (True, "No payload to check")

    # Check payload keys for mutation-action patterns
    for key in payload.keys():
        key_lower = key.lower()
        for forbidden in FORBIDDEN_MUTATION_KEYS:
            if forbidden.lower() in key_lower:
                return (False, f"Payload key '{key}' suggests mutation action")

    # Check payload string for mutation path/action references
    payload_str = json.dumps(payload).lower()
    for pattern in FORBIDDEN_MUTATION_PATTERNS:
        if pattern.lower() in payload_str:
            return (False, f"Payload contains mutation path/action '{pattern}'")

    return (True, "No Librarian mutation paths in payload")


def check_pi_12(data):
    """PI-12: Must not claim training_simulated as authoritative_export."""
    status = data.get("authority_status", "")
    if status == "training_simulated":
        uses = data.get("allowed_use", [])
        if "simulation" not in uses:
            return (False, "training_simulated but 'simulation' is not in allowed_use")
        if "qa_regression" in uses:
            return (False, "training_simulated but 'qa_regression' is in allowed_use — cannot regress on sim data")
    return (True, "training_simulated has correct use restrictions")


def check_pi_13(data):
    """PI-13: generated_at must not be in the future (within a small tolerance)."""
    val = data.get("generated_at", "")
    if not val:
        return (True, "No timestamp to check")
    try:
        ts = datetime.datetime.strptime(val, "%Y-%m-%dT%H:%M:%SZ")
        now = datetime.datetime.utcnow()
        # Add 5 second tolerance for clock skew
        if ts > now + datetime.timedelta(seconds=5):
            return (False, f"generated_at '{val}' is in the future")
        return (True, "generated_at is not in the future")
    except ValueError:
        return (True, "Cannot parse timestamp — skip future check")


def check_pi_14():
    """PI-14: No Librarian runtime/MCPController path in ingestion doc/schema."""
    findings = []
    for path in [GOV_DOC, SCHEMA_FILE]:
        if not path.exists():
            continue
        content = path.read_text()
        for pattern in FORBIDDEN_LIBRARIAN_PATTERNS:
            if pattern.lower() in content.lower():
                findings.append(f"Found '{pattern}' in {path.name}")
    if findings:
        return (False, "; ".join(findings))
    return (True, "No Librarian runtime references in ingestion docs")


def validate_fixture(path):
    """Validate a single fixture against schema and PI rules."""
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
        required = [
            "packet_type", "source_project", "consumer_project", "authority_status",
            "generated_at", "source_db_revision", "source_packet_hash", "source_docs",
            "allowed_use", "forbidden_use", "owner_decision_required_for_apply"
        ]
        missing = [f for f in required if f not in data]
        if missing:
            schema_valid = False
            schema_msg = f"Missing required fields: {missing}"
    except jsonschema.ValidationError as e:
        schema_valid = False
        schema_msg = f"Schema validation failed: {e.message}"

    checks = [
        ("PI-1", lambda: check_pi_1(data), "packet_type is known"),
        ("PI-2", lambda: check_pi_2(data), "source_project is librarian"),
        ("PI-3", lambda: check_pi_3(data), "consumer_project is qa-pilot"),
        ("PI-4", lambda: check_pi_4(data), "authority_status valid"),
        ("PI-5", lambda: check_pi_5(data), "authoritative_export has payload"),
        ("PI-6", lambda: check_pi_6(data), "generated_at ISO 8601 UTC"),
        ("PI-7", lambda: check_pi_7(data), "source_packet_hash SHA-256"),
        ("PI-8", lambda: check_pi_8(data), "allowed_use no forbidden"),
        ("PI-9", lambda: check_pi_9(data), "forbidden_use complete"),
        ("PI-10", lambda: check_pi_10(data), "owner_decision_required_for_apply true"),
        ("PI-11", lambda: check_pi_11(data), "no Librarian mutation payload"),
        ("PI-12", lambda: check_pi_12(data), "training_simulated use correct"),
        ("PI-13", lambda: check_pi_13(data), "generated_at not future"),
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
            "PI-1: packet_type must be a known packet type (qa_claim_registry/project_state/milestone_regression/training_source)",
            "PI-2: source_project must be 'librarian'",
            "PI-3: consumer_project must be 'qa-pilot'",
            "PI-4: authority_status must be authoritative_export/advisory_copy/training_simulated",
            "PI-5: Must not claim authoritative_export when payload is empty or missing",
            "PI-6: generated_at must be valid ISO 8601 UTC with Z suffix",
            "PI-7: source_packet_hash must be valid SHA-256 hex (64 hex chars)",
            "PI-8: allowed_use must not contain direct_librarian_mutation",
            "PI-9: forbidden_use must contain all required categories",
            "PI-10: owner_decision_required_for_apply must be true",
            "PI-11: Must not contain direct Librarian mutation paths in payload",
            "PI-12: training_simulated must restrict allowed_use appropriately",
            "PI-13: generated_at must not be in the future",
            "PI-14: No Librarian runtime/MCPController path references in ingestion docs",
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

    pi14_passed, pi14_msg = check_pi_14()
    pi14_prefix = "✅" if pi14_passed else "❌"
    print(f"  {pi14_prefix} PI-14: {pi14_msg}")

    print()
    if include_invalid:
        print(f"Valid fixtures:   {valid_pass}/{valid_total} passed")
        print(f"Invalid fixtures: {invalid_pass}/{invalid_total} rejected")

    all_ok = (valid_pass == valid_total if valid_total > 0 else True)
    all_rejected = (invalid_pass == invalid_total if invalid_total > 0 else True)

    if all_ok and all_rejected and pi14_passed and not parse_errors:
        print("\n✅ ALL CHECKS PASS")
        return 0
    else:
        failures = []
        if not all_ok: failures.append("valid fixtures")
        if not all_rejected: failures.append("invalid fixture rejection")
        if not pi14_passed: failures.append("PI-14")
        if parse_errors: failures.append("parse errors")
        print(f"\n❌ CHECKS FAILED: {', '.join(failures)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
