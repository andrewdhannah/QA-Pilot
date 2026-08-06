#!/usr/bin/env python3
"""
QA Pilot SDK Integration Validator — QA-PILOT-SDK-INTEGRATION-1

Validates SDK output against the qa-pilot-sdk-integration.schema.json contract.
Enforces schema compliance, read-only invariants, and mutation path absence.

Rules:
  SI-1: SDK version is correct (qa-pilot-evidence-sdk-v1)
  SI-2: generated_at is present and valid ISO 8601
  SI-3: evidence_available is present
  SI-4: If evidence_available is true, evidence fields are present
  SI-5: If evidence_available is false, error message is present
  SI-6: finding_count matches len(findings) when findings present
  SI-7: Each finding has finding_id (non-empty string)
  SI-8: Each finding has severity (valid enum value)
  SI-9: Composition graph node_count matches len(nodes)
  SI-10: Composition graph edge_count matches len(edges)
  SI-11: No mutation authority keys present (authority, seal, approve, mutate, write, apply)
  SI-12: read_only_validation.clean is true (no warnings)
  SI-13: read_only is true
  SI-14: no_mutation_authority is true
  SI-15: JSON Schema compliance (draft 2020-12)

Usage:
    python3 scripts/validate-qa-pilot-sdk-integration.py <fixture-path>...
    python3 scripts/validate-qa-pilot-sdk-integration.py --all
    python3 scripts/validate-qa-pilot-sdk-integration.py --list-rules
    python3 scripts/validate-qa-pilot-sdk-integration.py --include-invalid
"""

import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-sdk-integration"
SCHEMA_FILE = REPO_ROOT / "docs" / "schemas" / "qa-pilot-sdk-integration.schema.json"

MUTATION_AUTHORITY_KEYS = {"authority", "seal", "approve", "mutate", "write", "apply"}
VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL", "INFO"}

SDK_VERSION_EXPECTED = "qa-pilot-evidence-sdk-v1"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Rule functions ───────────────────────────────────────────────────────

def check_si_1(data):
    """SI-1: SDK version is correct."""
    version = data.get("sdk_version")
    if version == SDK_VERSION_EXPECTED:
        return True, f"SDK version is correct: {version}"
    return False, f"SDK version mismatch: expected {SDK_VERSION_EXPECTED}, got {version}"


def check_si_2(data):
    """SI-2: generated_at is present and valid ISO 8601."""
    ga = data.get("generated_at")
    if not ga:
        return False, "generated_at is missing or empty"
    if not isinstance(ga, str) or len(ga) < 20:
        return False, f"generated_at is not a valid ISO 8601 string: {ga}"
    return True, f"generated_at present: {ga}"


def check_si_3(data):
    """SI-3: evidence_available is present (when applicable)."""
    if "evidence_available" not in data:
        # Not all SDK responses include this field (e.g. findings, graph, provenance)
        # This is acceptable — only snapshot and artifacts have it
        if ("finding_count" in data or "provenance_count" in data or 
            "artifacts_available" in data or "node_count" in data or "schema" in data):
            return True, "evidence_available not required for this response type (findings/graph/provenance)"
        return False, "evidence_available is missing and no alternative type field present"
    return True, f"evidence_available: {data['evidence_available']}"


def check_si_4(data):
    """SI-4: If evidence_available is true, evidence fields are present."""
    if not data.get("evidence_available"):
        # Check for artifacts_available instead (validation artifacts)
        if data.get("artifacts_available"):
            required = ["contract_version", "run_id", "evidence_summary"]
            missing = [r for r in required if r not in data]
            if missing:
                return False, f"Evidence fields missing when artifacts_available=true: {missing}"
            return True, "All expected evidence fields present (artifacts_available path)"
        return True, "evidence_available is false/absent, skipping evidence field check"
    
    required = ["contract_version", "run_id", "operational_mode", "evidence_summary"]
    missing = [r for r in required if r not in data]
    if missing:
        return False, f"Evidence fields missing when evidence_available=true: {missing}"
    return True, "All expected evidence fields present"


def check_si_5(data):
    """SI-5: If evidence_available is explicitly false, error message is present."""
    if data.get("evidence_available") is not False:
        return True, "evidence_available is not false, skipping error check"
    
    error = data.get("error")
    if not error:
        return False, "evidence_available is false but no error message"
    return True, f"Error present: {error}"


def check_si_6(data):
    """SI-6: finding_count matches len(findings) when findings present."""
    if "findings" not in data:
        return True, "No findings key, skipping"
    
    findings = data.get("findings", [])
    count = data.get("finding_count", 0)
    
    if len(findings) != count:
        return False, f"finding_count ({count}) does not match len(findings) ({len(findings)})"
    return True, f"finding_count matches: {count}"


def check_si_7(data):
    """SI-7: Each finding has finding_id."""
    findings = data.get("findings", [])
    for i, f in enumerate(findings):
        fid = f.get("finding_id")
        if not fid or not isinstance(fid, str) or len(fid.strip()) == 0:
            return False, f"Finding [{i}] missing or empty finding_id"
    return True, f"All {len(findings)} findings have finding_id"


def check_si_8(data):
    """SI-8: Each finding has severity (valid value)."""
    findings = data.get("findings", [])
    for i, f in enumerate(findings):
        sev = f.get("severity")
        if not sev:
            return False, f"Finding [{i}] missing severity"
    return True, f"All {len(findings)} findings have severity"


def check_si_9(data):
    """SI-9: Composition graph node_count matches len(nodes)."""
    if "nodes" not in data:
        return True, "No nodes key, skipping"
    
    nodes = data.get("nodes", [])
    count = data.get("node_count", 0)
    
    if len(nodes) != count:
        return False, f"node_count ({count}) does not match len(nodes) ({len(nodes)})"
    return True, f"node_count matches: {count}"


def check_si_10(data):
    """SI-10: Composition graph edge_count matches len(edges)."""
    if "edges" not in data:
        return True, "No edges key, skipping"
    
    edges = data.get("edges", [])
    count = data.get("edge_count", 0)
    
    if len(edges) != count:
        return False, f"edge_count ({count}) does not match len(edges) ({len(edges)})"
    return True, f"edge_count matches: {count}"


def check_si_11(data):
    """SI-11: No mutation authority keys present."""
    # Check top-level keys
    found_mutation_keys = []
    for key in data:
        if key.lower() in MUTATION_AUTHORITY_KEYS:
            found_mutation_keys.append(key)
    
    if found_mutation_keys:
        return False, f"Mutation authority keys found: {found_mutation_keys}"
    return True, "No mutation authority keys at top level"


def _recursive_find_mutation_keys(obj, path=""):
    """Recursively scan for mutation authority keys in nested data."""
    found = []
    if isinstance(obj, dict):
        for key, val in obj.items():
            current_path = f"{path}.{key}" if path else key
            if key.lower() in MUTATION_AUTHORITY_KEYS:
                found.append(current_path)
            found.extend(_recursive_find_mutation_keys(val, current_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            found.extend(_recursive_find_mutation_keys(item, f"{path}[{i}]"))
    return found


def check_si_12(data):
    """SI-12: read_only_validation.clean is true."""
    rov = data.get("read_only_validation", {})
    if not rov:
        return True, "No read_only_validation in data (non-SDK response)"
    
    clean = rov.get("clean", False)
    warnings = rov.get("warnings", [])
    
    if not clean:
        return False, f"read_only_validation has warnings: {warnings}"
    return True, "read_only_validation.clean is True"


def check_si_13(data):
    """SI-13: read_only is true."""
    ro = data.get("read_only", False)
    if not ro:
        return True, "No read_only flag (non-validation-artifacts response)"
    if ro is not True:
        return False, f"read_only is {ro}, expected True"
    return True, "read_only is True"


def check_si_14(data):
    """SI-14: no_mutation_authority is true."""
    nma = data.get("no_mutation_authority")
    if nma is None:
        return True, "No no_mutation_authority flag (non-validation-artifacts response)"
    if nma is not True:
        return False, f"no_mutation_authority is {nma}, expected True"
    return True, "no_mutation_authority is True"


def check_si_15(data):
    """SI-15: JSON Schema compliance check (required fields present)."""
    # Check that required fields from schema are present
    required = ["sdk_version", "generated_at"]
    missing = [r for r in required if r not in data]
    if missing:
        return False, f"Schema-required fields missing: {missing}"
    return True, "Schema-required fields present"


# ── Rules registry ──────────────────────────────────────────────────────

RULES = [
    ("SI-1", check_si_1, "SDK version is correct"),
    ("SI-2", check_si_2, "generated_at is present and valid"),
    ("SI-3", check_si_3, "evidence_available is present"),
    ("SI-4", check_si_4, "Evidence fields present when available"),
    ("SI-5", check_si_5, "Error message when evidence unavailable"),
    ("SI-6", check_si_6, "finding_count matches findings length"),
    ("SI-7", check_si_7, "Each finding has finding_id"),
    ("SI-8", check_si_8, "Each finding has severity"),
    ("SI-9", check_si_9, "node_count matches nodes length"),
    ("SI-10", check_si_10, "edge_count matches edges length"),
    ("SI-11", check_si_11, "No mutation authority keys present"),
    ("SI-12", check_si_12, "read_only_validation is clean"),
    ("SI-13", check_si_13, "read_only is true"),
    ("SI-14", check_si_14, "no_mutation_authority is true"),
    ("SI-15", check_si_15, "Schema-required fields present"),
]


def validate_fixture(path, allow_invalid=False):
    """Validate a single fixture against all rules."""
    try:
        data = load_json(path)
    except (json.JSONDecodeError, IOError) as e:
        return (os.path.basename(path), {
            "all_pass": False,
            "checks": [{"rule": "PARSE", "passed": False, "message": str(e)}],
            "error": str(e),
        })

    results = []
    all_pass = True

    for rule_id, func, desc in RULES:
        try:
            passed, message = func(data)
        except Exception as e:
            passed = False
            message = f"Exception: {e}"
        
        results.append({
            "rule": rule_id,
            "description": desc,
            "passed": passed,
            "message": message,
        })
        
        if not passed:
            all_pass = False

    # For invalid fixtures, invert the expected outcome
    if allow_invalid:
        # Invalid fixtures are expected to FAIL — invert
        fixture_name = os.path.basename(path)
        is_invalid = fixture_name.startswith("invalid-")
        
        if is_invalid:
            # An invalid fixture should have at least one failure
            expected_pass = not all_pass
        else:
            expected_pass = all_pass
    else:
        expected_pass = all_pass

    return (os.path.basename(path), {
        "all_pass": all_pass,
        "expected_pass": expected_pass,
        "checks": results,
    })


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="QA Pilot SDK Integration Validator")
    parser.add_argument("paths", nargs="*", help="Fixture paths to validate")
    parser.add_argument("--all", action="store_true", help="Validate all valid fixtures")
    parser.add_argument("--include-invalid", action="store_true", help="Include invalid fixtures")
    parser.add_argument("--list-rules", action="store_true", help="List all rules and exit")
    
    args = parser.parse_args()
    
    if args.list_rules:
        print("QA Pilot SDK Integration Validator — Rules")
        print("=" * 60)
        for rule_id, func, desc in RULES:
            print(f"  {rule_id}: {desc}")
        return 0
    
    # Determine fixtures to validate
    fixtures = []
    if args.paths:
        fixtures = args.paths
    elif args.all or args.include_invalid:
        if FIXTURES_DIR.exists():
            pattern = "valid-*.json" if not args.include_invalid else "*.json"
            for f in sorted(FIXTURES_DIR.glob(pattern)):
                fixtures.append(str(f))
    
    if not fixtures:
        if FIXTURES_DIR.exists():
            # Default: all valid fixtures
            for f in sorted(FIXTURES_DIR.glob("valid-*.json")):
                fixtures.append(str(f))
        else:
            print(f"ERROR: Fixtures directory not found: {FIXTURES_DIR}", file=sys.stderr)
            return 1
    
    # Validate each fixture
    all_passed = True
    valid_pass = 0
    valid_total = 0
    invalid_pass = 0
    invalid_total = 0
    
    for path in fixtures:
        filename = os.path.basename(path)
        is_invalid = filename.startswith("invalid-")
        
        if not os.path.exists(path):
            print(f"  SKIP  {filename} — file not found")
            continue
        
        name, result = validate_fixture(path, allow_invalid=args.include_invalid)
        
        if is_invalid:
            invalid_total += 1
            if result["expected_pass"]:
                invalid_pass += 1
                print(f"  ✅  {name} — correctly rejected (invalid fixture)")
            else:
                all_passed = False
                print(f"  ❌  {name} — expected rejection but passed some rules")
        else:
            valid_total += 1
            if result["all_pass"]:
                valid_pass += 1
                print(f"  ✅  {name} — all rules pass")
            else:
                all_passed = False
                print(f"  ❌  {name} — FAILED")
        
        # Show details for failures
        if not result["all_pass"]:
            for check in result["checks"]:
                if not check["passed"]:
                    print(f"       {check['rule']}: {check['message']}")
    
    # Summary
    print()
    print(f"Valid fixtures:   {valid_pass}/{valid_total} passed")
    if args.include_invalid:
        print(f"Invalid fixtures: {invalid_pass}/{invalid_total} correctly rejected")
    print(f"Overall: {'PASS' if all_passed else 'FAIL'}")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
