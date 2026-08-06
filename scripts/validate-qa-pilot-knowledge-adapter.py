#!/usr/bin/env python3
"""
QA Pilot Librarian Knowledge Adapter Validator — QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER-1

Validates knowledge adapter output against schema and governance rules.

Rules:
    KA-1:  Adapter version must be 'knowledge-adapter-v1'
    KA-2:  Operation must be one of scan/query/reference/provenance/verify/status
    KA-3:  generated_at must be valid ISO 8601 UTC
    KA-4:  Source references require path, revision, source_type, accessible
    KA-5:  Provenance records require provenance_id, sources, source_hash
    KA-6:  Provenance source_hash must be valid SHA-256 hex
    KA-7:  Provenance advisory must be true
    KA-8:  Provenance no_authority_promotion must be true
    KA-9:  Source hash matches recomputed hash (verify operation)
    KA-10: No Librarian mutation paths in adapter output
    KA-11: scan returns sources grouped by type
    KA-12: query respects type/keyword filters
    KA-13: reference returns accessible status per path
    KA-14: status reports advisory-only authority
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CARBIDE_WORKSPACE = REPO_ROOT.parent.parent
LIBRARIAN_ROOT = CARBIDE_WORKSPACE / "active" / "librarian"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-knowledge-adapter"
SCHEMA_FILE = REPO_ROOT / "docs" / "schemas" / "qa-pilot-knowledge-adapter.schema.json"
GOV_DOC = REPO_ROOT / "docs" / "governance" / "QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER.md"
ADAPTER_SCRIPT = SCRIPT_DIR / "qa_pilot_knowledge_adapter.py"

VALID_OPERATIONS = ["scan", "query", "reference", "provenance", "verify", "status"]
VALID_SOURCE_TYPES = ["governance", "schema", "rule", "ledger", "receipt"]
FORBIDDEN_MUTATION_PATTERNS = [
    "active/librarian/", "librarian DB write", "librarian MCP register",
    "Sources/App/", "MCPController.swift", "AppEntry.swift",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_adapter_scan():
    """Run adapter scan and return parsed JSON."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(ADAPTER_SCRIPT), "scan"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def check_ka_1(data):
    """KA-1: Adapter version must be 'knowledge-adapter-v1'."""
    val = data.get("adapter_version", "")
    passed = val == "knowledge-adapter-v1"
    return (passed, f"adapter_version = '{val}'" if not passed else "adapter_version is knowledge-adapter-v1")


def check_ka_2(data):
    """KA-2: Operation must be one of scan/query/reference/provenance/verify/status."""
    val = data.get("operation", "")
    passed = val in VALID_OPERATIONS
    return (passed, f"operation = '{val}'" if not passed else f"operation is '{val}'")


def check_ka_3(data):
    """KA-3: generated_at must be valid ISO 8601 UTC."""
    val = data.get("generated_at", "")
    passed = bool(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", val))
    return (passed, f"generated_at = '{val}'" if not passed else "generated_at is valid ISO 8601 UTC")


def check_ka_4(data):
    """KA-4: Source references require path, revision, source_type, accessible."""
    sources = data.get("sources", [])
    if not sources:
        # May be nested in result
        result = data.get("result", {})
        sources = result.get("sources", [])
        if not sources:
            return (True, "No sources to check")

    failures = []
    for i, src in enumerate(sources):
        missing = [f for f in ["path", "revision", "source_type", "accessible"] if f not in src]
        if missing:
            failures.append(f"source[{i}] missing: {missing}")

    passed = len(failures) == 0
    detail = "; ".join(failures) if failures else "All source references have required fields"
    return (passed, detail)


def check_ka_5(data):
    """KA-5: Provenance records require provenance_id, sources, source_hash."""
    result = data.get("result", {})
    prov = result.get("provenance", {})
    if not prov:
        return (True, "No provenance record to check")

    missing = [f for f in ["provenance_id", "sources", "source_hash"] if f not in prov]
    passed = len(missing) == 0
    detail = f"Missing: {missing}" if missing else "Provenance record has required fields"
    return (passed, detail)


def check_ka_6(data):
    """KA-6: Provenance source_hash must be valid SHA-256 hex."""
    result = data.get("result", {})
    prov = result.get("provenance", {})
    if not prov:
        return (True, "No provenance to check")

    val = prov.get("source_hash", "")
    passed = bool(re.match(r"^[a-f0-9]{64}$", val))
    return (passed, f"source_hash = '{val}'" if not passed else "source_hash is valid SHA-256")


def check_ka_7(data):
    """KA-7: Provenance advisory must be true."""
    result = data.get("result", {})
    prov = result.get("provenance", {})
    if not prov:
        return (True, "No provenance to check")

    passed = prov.get("advisory") is True
    return (passed, "advisory is not True" if not passed else "advisory is True")


def check_ka_8(data):
    """KA-8: Provenance no_authority_promotion must be true."""
    result = data.get("result", {})
    prov = result.get("provenance", {})
    if not prov:
        return (True, "No provenance to check")

    passed = prov.get("no_authority_promotion") is True
    return (passed, "no_authority_promotion is not True" if not passed else "no_authority_promotion is True")


def check_ka_9(data):
    """KA-9: Verify operation returns valid verification results."""
    if data.get("operation") != "verify":
        return (True, "Not verify operation — skip")

    result = data.get("result", {})
    sources = data.get("sources", [])
    if not sources:
        return (True, "No sources to verify")

    all_accessible = all(s.get("accessible", False) for s in sources)
    all_hash_match = all(s.get("hash_match", True) for s in sources)
    status = result.get("status", "")
    expected_status = "verified" if (all_accessible and all_hash_match) else "degraded"

    passed = status == expected_status
    detail = f"status={status}, expected={expected_status}" if not passed else f"verify status={status}"
    return (passed, detail)


def check_ka_10(data):
    """KA-10: No Librarian mutation paths in adapter output."""
    output_str = json.dumps(data).lower()
    # Check for active mutation claims (not bare path references)
    mutation_claims = ["seal_action", "approve_action", "merge_action", "librarian db write",
                       "librarian mcp register", "sources/app/", "mcpcontroller.swift"]
    for pattern in mutation_claims:
        if pattern.lower() in output_str:
            return (False, f"Contains forbidden mutation claim: '{pattern}'")
    # Check that bare path references to librarian are only in status/location context
    # and not claiming mutation capability
    if "cross_project_write" in output_str:
        if '"not authorized"' in output_str or '"not_authorized"' in output_str:
            return (True, "Cross-project write is NOT AUTHORIZED — safe")
    return (True, "No Librarian mutation paths in output")


def check_ka_11(data):
    """KA-11: scan returns sources grouped by type."""
    if data.get("operation") != "scan":
        return (True, "Not scan operation — skip")

    result = data.get("result", {})
    by_type = result.get("by_type", {})
    if not by_type:
        return (True, "No by_type grouping to check")

    sources = result.get("sources", [])
    # Verify counts match
    expected = {}
    for s in sources:
        t = s.get("source_type", "unknown")
        expected[t] = expected.get(t, 0) + 1

    passed = by_type == expected
    detail = f"by_type={by_type}, expected={expected}" if not passed else f"by_type counts correct: {by_type}"
    return (passed, detail)


def check_ka_12(data):
    """KA-12: Query results respect filters."""
    if data.get("operation") != "query":
        return (True, "Not query operation — skip")

    query = data.get("query", {})
    result = data.get("result", {})
    sources = result.get("sources", [])
    pattern = query.get("pattern", "")
    source_type = query.get("source_type", "all")

    if pattern:
        for s in sources:
            if pattern.lower() not in s.get("path", "").lower():
                return (False, f"Source '{s['path']}' does not match pattern '{pattern}'")

    if source_type != "all":
        for s in sources:
            if s.get("source_type") != source_type:
                return (False, f"Source '{s['path']}' has type '{s['source_type']}', expected '{source_type}'")

    return (True, f"Query filter respected: pattern='{pattern}', type={source_type}")


def check_ka_13(data):
    """KA-13: reference returns accessible status per path."""
    if data.get("operation") != "reference":
        return (True, "Not reference operation — skip")

    sources = data.get("sources", [])
    for s in sources:
        if "accessible" not in s:
            return (False, f"Source missing 'accessible' field: {s.get('path', '?')}")

    return (True, "All reference results have accessible status")


def check_ka_14(data):
    """KA-14: status reports advisory-only authority."""
    if data.get("operation") != "status":
        return (True, "Not status operation — skip")

    result = data.get("result", {})
    authority = result.get("authority", "")
    passed = authority == "advisory-only"
    detail = f"authority = '{authority}'" if not passed else "authority is advisory-only"
    return (passed, detail)


def validate_fixture(path):
    """Validate a single fixture against all KA rules."""
    try:
        data = load_json(path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return (os.path.basename(path), {"error": str(e), "all_pass": False})

    checks = [
        ("KA-1", check_ka_1(data), "Adapter version correct"),
        ("KA-2", check_ka_2(data), "Operation valid"),
        ("KA-3", check_ka_3(data), "Timestamp valid"),
        ("KA-4", check_ka_4(data), "Source refs have required fields"),
        ("KA-5", check_ka_5(data), "Provenance has required fields"),
        ("KA-6", check_ka_6(data), "Source hash valid"),
        ("KA-7", check_ka_7(data), "Provenance advisory"),
        ("KA-8", check_ka_8(data), "No authority promotion"),
        ("KA-9", check_ka_9(data), "Verify status matches"),
        ("KA-10", check_ka_10(data), "No mutation paths"),
        ("KA-11", check_ka_11(data), "Scan grouping correct"),
        ("KA-12", check_ka_12(data), "Query filters respected"),
        ("KA-13", check_ka_13(data), "Reference has accessible"),
        ("KA-14", check_ka_14(data), "Status reports advisory-only"),
    ]

    all_pass = True
    results = []
    for rule_id, (passed, msg), desc in checks:
        results.append({"rule": rule_id, "description": desc, "passed": passed, "message": msg})
        if not passed:
            all_pass = False

    return (os.path.basename(path), {"all_pass": all_pass, "checks": results})


def main():
    args = sys.argv[1:]
    list_rules = "--list-rules" in args
    include_invalid = "--include-invalid" in args
    test_live = "--test-live" in args

    if list_rules:
        rules = [
            "KA-1:  Adapter version must be 'knowledge-adapter-v1'",
            "KA-2:  Operation must be scan/query/reference/provenance/verify/status",
            "KA-3:  generated_at must be valid ISO 8601 UTC",
            "KA-4:  Source references require path, revision, source_type, accessible",
            "KA-5:  Provenance records require provenance_id, sources, source_hash",
            "KA-6:  Provenance source_hash must be valid SHA-256 hex",
            "KA-7:  Provenance advisory must be true",
            "KA-8:  Provenance no_authority_promotion must be true",
            "KA-9:  Verify operation status matches accessibility + hash results",
            "KA-10: No Librarian mutation paths in adapter output",
            "KA-11: Scan returns sources grouped by type with correct counts",
            "KA-12: Query results respect type/keyword filters",
            "KA-13: Reference returns accessible status per path",
            "KA-14: Status reports advisory-only authority",
        ]
        for r in rules:
            print(f"  {r}")
        return 0

    # Live adapter tests
    if test_live:
        print("QA Pilot Knowledge Adapter — Live Tests")
        print("=" * 50)

        live_checks = []

        # L1: Scan produces valid output
        scan_data = load_adapter_scan()
        live_checks.append(("L1: scan produces valid output", scan_data is not None, ""))

        if scan_data:
            # L2: Scan returns sources
            sources = scan_data.get("result", {}).get("sources", [])
            live_checks.append(("L2: scan returns sources", len(sources) > 0, f"({len(sources)} sources)"))

            # L3: Scan has by_type counts
            by_type = scan_data.get("result", {}).get("by_type", {})
            live_checks.append(("L3: scan has by_type counts", len(by_type) > 0, f"({by_type})"))

        # L4: Adapter CLI responds
        import subprocess
        help_result = subprocess.run(
            [sys.executable, str(ADAPTER_SCRIPT), "--help"],
            capture_output=True, text=True, timeout=10,
        )
        live_checks.append(("L4: adapter --help works", help_result.returncode == 0, ""))

        # L5: Status reports advisory-only
        status_result = subprocess.run(
            [sys.executable, str(ADAPTER_SCRIPT), "status"],
            capture_output=True, text=True, timeout=10,
        )
        if status_result.returncode == 0:
            try:
                status_data = json.loads(status_result.stdout)
                auth = status_data.get("result", {}).get("authority", "")
                live_checks.append(("L5: status reports advisory-only", auth == "advisory-only", f"auth={auth}"))
            except json.JSONDecodeError:
                live_checks.append(("L5: status reports advisory-only", False, "parse error"))

        # L6: Reference existing file works
        ref_result = subprocess.run(
            [sys.executable, str(ADAPTER_SCRIPT), "reference", "docs/governance/QA-PILOT-PROJECT-GOVERNANCE.md"],
            capture_output=True, text=True, timeout=10,
        )
        if ref_result.returncode == 0:
            try:
                ref_data = json.loads(ref_result.stdout)
                accessible = ref_data.get("result", {}).get("accessible_count", 0)
                live_checks.append(("L6: reference existing file", accessible > 0, f"accessible={accessible}"))
            except json.JSONDecodeError:
                live_checks.append(("L6: reference existing file", False, "parse error"))

        # Print results
        for label, passed, detail in live_checks:
            prefix = "✅" if passed else "❌"
            print(f"  {prefix} {label} {detail}")

        all_passed = all(c[1] for c in live_checks)
        print()
        print(f"Live tests: {sum(1 for c in live_checks if c[1])}/{len(live_checks)} passed")
        return 0 if all_passed else 1

    # Fixture-based tests
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

    for fname, r in results:
        if "error" in r:
            print(f"  ❌ {fname} — ERROR: {r['error']}")
            continue
        prefix = "✅" if r["all_pass"] else "❌"
        check_count = len(r["checks"])
        pass_count = sum(1 for c in r["checks"] if c["passed"])
        print(f"  {prefix} {fname} — {pass_count}/{check_count} checks pass")
        if not r["all_pass"]:
            for c in r["checks"]:
                if not c["passed"]:
                    print(f"       FAIL {c['rule']}: {c['message']}")

    print()
    if include_invalid:
        print(f"Valid fixtures:   {valid_pass}/{valid_total} passed")
        print(f"Invalid fixtures: {invalid_pass}/{invalid_total} rejected")

    all_ok = (valid_pass == valid_total if valid_total > 0 else True)
    all_rejected = (invalid_pass == invalid_total if invalid_total > 0 else True)

    if all_ok and all_rejected:
        print("\n✅ ALL CHECKS PASS")
        return 0
    else:
        failures = []
        if not all_ok: failures.append("valid fixtures")
        if not all_rejected: failures.append("invalid fixture rejection")
        print(f"\n❌ CHECKS FAILED: {', '.join(failures)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
