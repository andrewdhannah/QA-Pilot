#!/usr/bin/env python3
"""
QA Pilot Broker Advisory Surface Validator — QA-PILOT-BROKER-MCP-ADVISORY-SURFACE-1

Enforces advisory surface boundaries and behavior rules.

Rules:
    VA-1: Advisory surface script exists
    VA-2: Surface has no Librarian/MCPController references (except rejection context)
    VA-3: Surface delegates to sealed broker module
    VA-4: Surface response includes all required fields
    VA-5: Surface authority is advisory_only
    VA-6: Surface governance doc exists
    VA-7: Surface schema exists and is valid JSON
    VA-8: Fixtures exist (valid and invalid)
    VA-9: All valid fixtures expect acceptance
    VA-10: All invalid fixtures expect rejection
    VA-11: Unsupported command fixture exists
    VA-12: Missing custody fixture exists
    VA-13: Wrong project fixture exists
    VA-14: Cross-project handler fixture exists
    VA-15: Unsupported tool fixture exists
    VA-16: Non-advisory authority fixture exists
    VA-17: Disabled broker fixture exists
    VA-18: Malformed input fixture exists
    VA-19: No Librarian runtime references in surface docs
"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SURFACE_SCRIPT = SCRIPT_DIR / "qa_pilot_broker_advisory_surface.py"
GOV_DOC = REPO_ROOT / "docs" / "governance" / "QA-PILOT-BROKER-MCP-ADVISORY-SURFACE.md"
SCHEMA_FILE = REPO_ROOT / "docs" / "schemas" / "qa-pilot-broker-mcp-advisory-surface.schema.json"
FIXTURES_DIR = REPO_ROOT / "fixtures" / "broker-advisory-surface"
EXAMPLES_DIR = REPO_ROOT / "docs" / "examples" / "broker-advisory-surface"

REQUIRED_RESPONSE_FIELDS = [
    "surface", "command", "project_id", "authority", "accepted",
    "custody_verified", "audit_receipt_id", "broker_commit_or_version",
    "timestamp", "limitations",
]

SUPPORTED_COMMANDS = [
    "qa_pilot_broker_accept",
    "qa_pilot_broker_audit",
    "qa_pilot_broker_list_audit",
    "qa_pilot_broker_status",
    "qa_pilot_broker_enable",
    "qa_pilot_broker_disable",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_va_1():
    """VA-1: Advisory surface script exists."""
    exists = SURFACE_SCRIPT.exists()
    return (exists, f"VA-1: Advisory surface script {'exists' if exists else 'not found'}")


def check_va_2():
    """VA-2: Surface has no Librarian/MCPController references (except rejection context)."""
    if not SURFACE_SCRIPT.exists():
        return (False, "VA-2: Surface script not found")
    content = SURFACE_SCRIPT.read_text()
    for pattern in ["MCPController.swift", "Sources/App/", "AppEntry.swift", "register tool in Librarian"]:
        if pattern.lower() in content.lower():
            return (False, f"VA-2: Found forbidden ref '{pattern}' in surface script")
    if "MCPController" in content:
        for line in content.split("\n"):
            if "MCPController" in line and "not register native MCPController" not in line.lower() and "does not register" not in line.lower():
                return (False, f"VA-2: Found MCPController not in rejection context: '{line.strip()}'")
    return (True, "VA-2: No Librarian runtime references in surface script")


def check_va_3():
    """VA-3: Surface delegates to sealed broker module."""
    if not SURFACE_SCRIPT.exists():
        return (False, "VA-3: Surface script not found")
    content = SURFACE_SCRIPT.read_text()
    has_import = "librarian_broker_qa_pilot" in content
    has_delegation = "get_broker()" in content or "broker." in content
    return ((has_import and has_delegation), "VA-3: Surface delegates to sealed broker" if (has_import and has_delegation) else "VA-3: Surface does not delegate to sealed broker")


def check_va_4():
    """VA-4: Surface response includes all required fields (schema structural check)."""
    if not SCHEMA_FILE.exists():
        return (True, "VA-4: Schema structural check deferred to schema validation")
    try:
        schema = load_json(str(SCHEMA_FILE))
        required = schema.get("required", [])
        missing = [f for f in REQUIRED_RESPONSE_FIELDS if f not in required]
        if missing:
            return (False, f"VA-4: Schema missing required fields: {missing}")
        return (True, f"VA-4: All {len(REQUIRED_RESPONSE_FIELDS)} required response fields present in schema")
    except (json.JSONDecodeError, OSError) as e:
        return (False, f"VA-4: Schema error: {e}")


def check_va_5():
    """VA-5: Surface authority is advisory_only (schema check)."""
    if not SCHEMA_FILE.exists():
        return (True, "VA-5: Schema check deferred")
    try:
        schema = load_json(str(SCHEMA_FILE))
        authority = schema.get("properties", {}).get("authority", {})
        if authority.get("const") != "advisory_only":
            return (False, f"VA-5: Schema authority const is not advisory_only")
        return (True, "VA-5: Surface authority is advisory_only")
    except (json.JSONDecodeError, OSError) as e:
        return (False, f"VA-5: Schema error: {e}")


def check_va_6():
    """VA-6: Surface governance doc exists."""
    exists = GOV_DOC.exists()
    return (exists, f"VA-6: Governance doc {'exists' if exists else 'not found'}")


def check_va_7():
    """VA-7: Surface schema exists and is valid JSON."""
    if not SCHEMA_FILE.exists():
        return (False, "VA-7: Schema not found")
    try:
        load_json(str(SCHEMA_FILE))
        return (True, "VA-7: Schema exists and is valid JSON")
    except (json.JSONDecodeError, OSError):
        return (False, "VA-7: Schema is not valid JSON")


def check_va_8():
    """VA-8: Fixtures exist (valid and invalid)."""
    if not FIXTURES_DIR.exists():
        return (False, "VA-8: Fixtures directory not found")
    valid = list(FIXTURES_DIR.glob("valid-*.json"))
    invalid = list(FIXTURES_DIR.glob("invalid-*.json"))
    total = len(valid) + len(invalid)
    return (total >= 4, f"VA-8: {total} fixtures ({len(valid)} valid, {len(invalid)} invalid)")


def check_va_9():
    """VA-9: All valid fixtures expect acceptance."""
    if not FIXTURES_DIR.exists():
        return (True, "VA-9: No fixtures to check")
    for f in sorted(FIXTURES_DIR.glob("valid-*.json")):
        try:
            data = load_json(str(f))
            if data.get("expected_behavior") not in ("accepted", "accepted_or_not_found"):
                return (False, f"VA-9: Valid fixture '{f.name}' does not expect acceptance")
        except (json.JSONDecodeError, OSError) as e:
            return (False, f"VA-9: Cannot read fixture '{f.name}': {e}")
    return (True, "VA-9: All valid fixtures expect acceptance")


def check_va_10():
    """VA-10: All invalid fixtures expect rejection."""
    if not FIXTURES_DIR.exists():
        return (True, "VA-10: No fixtures to check")
    for f in sorted(FIXTURES_DIR.glob("invalid-*.json")):
        try:
            data = load_json(str(f))
            if data.get("expected_behavior") != "rejected":
                return (False, f"VA-10: Invalid fixture '{f.name}' does not expect rejection")
        except (json.JSONDecodeError, OSError) as e:
            return (False, f"VA-10: Cannot read fixture '{f.name}': {e}")
    return (True, "VA-10: All invalid fixtures expect rejection")


def check_va_11_through_18():
    """VA-11-18: Specific rejection fixtures exist."""
    if not FIXTURES_DIR.exists():
        return (True, "No fixtures to check")

    checks = [
        ("VA-11", "invalid-unsupported-command", "Unsupported command"),
        ("VA-12", "invalid-missing-custody", "Missing custody"),
        ("VA-13", "invalid-wrong-project", "Wrong project"),
        ("VA-14", "invalid-cross-project", "Cross-project handler"),
        ("VA-15", "invalid-unsupported-tool", "Unsupported tool"),
        ("VA-16", "invalid-authoritative-claim", "Non-advisory authority"),
        ("VA-17", "invalid-disabled-broker", "Disabled broker"),
        ("VA-18", "invalid-malformed", "Malformed/parse error"),
    ]

    results = []
    all_found = True
    for rule_id, pattern, desc in checks:
        found = list(FIXTURES_DIR.glob(f"{pattern}*.json"))
        if found:
            results.append((True, f"{rule_id}: {desc} fixture exists"))
        else:
            results.append((False, f"{rule_id}: {desc} fixture not found"))
            all_found = False

    return (all_found, results)


def check_va_19():
    """VA-19: No Librarian runtime references in surface docs."""
    files_to_check = [GOV_DOC, SCHEMA_FILE]
    forbidden_patterns = [
        "MCPController.swift",
        "Sources/App/",
        "AppEntry.swift",
        "register tool in Librarian",
    ]
    for path in files_to_check:
        if not path.exists():
            continue
        content = path.read_text()
        for pattern in forbidden_patterns:
            if pattern.lower() in content.lower():
                return (False, f"VA-19: Found forbidden Librarian ref '{pattern}' in {path.name}")
    return (True, "VA-19: No Librarian runtime references in surface docs")


def main():
    args = sys.argv[1:]
    list_rules = "--list-rules" in args

    if list_rules:
        rules = [
            "VA-1: Advisory surface script exists",
            "VA-2: Surface has no Librarian/MCPController references",
            "VA-3: Surface delegates to sealed broker module",
            "VA-4: Surface response includes all required fields",
            "VA-5: Surface authority is advisory_only",
            "VA-6: Surface governance doc exists",
            "VA-7: Surface schema exists and is valid JSON",
            "VA-8: Fixtures exist (valid and invalid)",
            "VA-9: All valid fixtures expect acceptance",
            "VA-10: All invalid fixtures expect rejection",
            "VA-11: Unsupported command fixture exists",
            "VA-12: Missing custody fixture exists",
            "VA-13: Wrong project fixture exists",
            "VA-14: Cross-project handler fixture exists",
            "VA-15: Unsupported tool fixture exists",
            "VA-16: Non-advisory authority fixture exists",
            "VA-17: Disabled broker fixture exists",
            "VA-18: Malformed input fixture exists",
            "VA-19: No Librarian runtime references in surface docs",
        ]
        for r in rules:
            print(f"  {r}")
        return 0

    checks = [
        ("VA-1", check_va_1, "Surface script exists"),
        ("VA-2", check_va_2, "No Librarian refs"),
        ("VA-3", check_va_3, "Delegates to broker"),
        ("VA-4", check_va_4, "Required fields present"),
        ("VA-5", check_va_5, "Advisory-only authority"),
        ("VA-6", check_va_6, "Governance doc exists"),
        ("VA-7", check_va_7, "Schema valid"),
        ("VA-8", check_va_8, "Fixtures exist"),
        ("VA-9", check_va_9, "Valid fixture structure"),
        ("VA-10", check_va_10, "Invalid fixture structure"),
        ("VA-11-18", check_va_11_through_18, "Specific rejection fixtures"),
        ("VA-19", check_va_19, "No Librarian refs in docs"),
    ]

    all_pass = True
    for rule_id, func, desc in checks:
        if rule_id == "VA-11-18":
            passed, results = func()
            for sp, msg in results:
                prefix = "✅" if sp else "❌"
                print(f"  {prefix} {msg}")
                if not sp:
                    all_pass = False
            continue

        passed, msg = func()
        prefix = "✅" if passed else "❌"
        print(f"  {prefix} {rule_id}: {msg}")
        if not passed:
            all_pass = False

    print()
    if all_pass:
        print("✅ ALL CHECKS PASS")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
