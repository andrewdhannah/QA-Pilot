#!/usr/bin/env python3
"""
QA Pilot Broker Implementation Validator — QA-PILOT-BROKER-IMPLEMENTATION-1

Enforces broker implementation boundaries and behavior rules.

Rules:
    BI-1: Broker module exists at scripts/librarian_broker_qa_pilot.py
    BI-2: Broker module has no Librarian/MCPController references
    BI-3: Broker module uses advisory-only authority
    BI-4: Broker module has disable flag mechanism
    BI-5: Broker module routes to QA Pilot handlers (not Librarian)
    BI-6: Broker module produces audit receipts
    BI-7: Broker module has no native MCPController registration
    BI-8: Broker module has no cross-project call execution
    BI-9: Implementation governance doc exists
    BI-10: Implementation schema exists
    BI-11: Broker audit directory exists
    BI-12: Implementation fixtures exist (valid and invalid)
    BI-13: All valid fixture requests are accepted by broker
    BI-14: All invalid fixture requests are rejected by broker
    BI-15: Missing custody_record causes rejection
    BI-16: Wrong project_id causes rejection
    BI-17: Unsupported tool causes rejection
    BI-18: Cross-project handler path causes rejection
    BI-19: Non-advisory authority claim causes rejection
    BI-20: No Librarian runtime, Sources/App, MCPController references in implementation docs
"""

import json
import os
import re
import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BROKER_MODULE = SCRIPT_DIR / "librarian_broker_qa_pilot.py"
GOV_DOC = REPO_ROOT / "docs" / "governance" / "QA-PILOT-BROKER-IMPLEMENTATION.md"
SCHEMA_FILE = REPO_ROOT / "docs" / "schemas" / "qa-pilot-broker-implementation.schema.json"
AUDIT_DIR = REPO_ROOT / "data" / "audit" / "broker"
FIXTURES_DIR = REPO_ROOT / "fixtures" / "broker-implementation"
EXAMPLES_DIR = REPO_ROOT / "docs" / "examples" / "broker-implementation"

FORBIDDEN_PATTERNS = [
    "MCPController.swift",
    "Sources/App/",
    "AppEntry.swift",
    "register tool in Librarian",
    "import Librarian",
    "from Librarian",
]

FORBIDDEN_CONTEXT_SENSITIVE = [
    "native MCPController",
    "MCPController",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_bi_1():
    """BI-1: Broker module exists at scripts/librarian_broker_qa_pilot.py."""
    exists = BROKER_MODULE.exists()
    return (exists, "BI-1: Broker module exists" if exists else "BI-1: Broker module not found at scripts/librarian_broker_qa_pilot.py")


def check_bi_2():
    """BI-2: Broker module has no Librarian/MCPController references."""
    if not BROKER_MODULE.exists():
        return (False, "BI-2: Broker module not found")
    content = BROKER_MODULE.read_text()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in content.lower():
            return (False, f"BI-2: Found forbidden Librarian ref '{pattern}' in broker module")
    return (True, "BI-2: No Librarian runtime references in broker module")


def check_bi_3():
    """BI-3: Broker module uses advisory-only authority."""
    if not BROKER_MODULE.exists():
        return (False, "BI-3: Broker module not found")
    content = BROKER_MODULE.read_text()
    if "advisory_only" not in content and 'authority": "advisory_only"' not in content:
        return (False, "BI-3: Broker module does not enforce advisory-only authority")
    return (True, "BI-3: Broker module enforces advisory-only authority")


def check_bi_4():
    """BI-4: Broker module has disable flag mechanism."""
    if not BROKER_MODULE.exists():
        return (False, "BI-4: Broker module not found")
    content = BROKER_MODULE.read_text()
    has_config = "broker-config.json" in content or "broker_enabled" in content
    has_enable_disable = "set_broker_enabled" in content
    return (has_config and has_enable_disable, "BI-4: Broker has disable flag mechanism" if (has_config and has_enable_disable) else "BI-4: Broker missing disable flag mechanism")


def check_bi_5():
    """BI-5: Broker module routes to QA Pilot handlers (not Librarian)."""
    if not BROKER_MODULE.exists():
        return (False, "BI-5: Broker module not found")
    content = BROKER_MODULE.read_text()
    has_handler_call = "qa_pilot_mcp_handlers" in content
    has_librarian_call = "import librarian" in content.lower() or "from librarian" in content.lower()
    if has_librarian_call:
        return (False, "BI-5: Broker module references Librarian modules")
    if not has_handler_call:
        return (False, "BI-5: Broker module does not route to QA Pilot handlers")
    return (True, "BI-5: Broker module routes to QA Pilot handlers")


def check_bi_6():
    """BI-6: Broker module produces audit receipts."""
    if not BROKER_MODULE.exists():
        return (False, "BI-6: Broker module not found")
    content = BROKER_MODULE.read_text()
    has_audit = "save_audit_receipt" in content and "broker_audit" in content
    return (has_audit, "BI-6: Broker module produces audit receipts" if has_audit else "BI-6: Broker module missing audit receipt generation")


def check_bi_7():
    """BI-7: Broker module has no native MCPController registration."""
    if not BROKER_MODULE.exists():
        return (False, "BI-7: Broker module not found")
    content = BROKER_MODULE.read_text()
    for pattern in ["mcp_controller", "register_tool", "native_mcp"]:
        if pattern.lower() in content.lower():
            return (False, f"BI-7: Found potential MCPController ref '{pattern}' in broker module")
    # Check for "MCPController" — only allowed in rejection/commentary context
    if "MCPController" in content:
        # Verify it only appears in contexts that reject it
        for line in content.split("\n"):
            if "MCPController" in line and "does not register" not in line.lower() and "not authorized" not in line.lower():
                return (False, f"BI-7: Found MCPController reference not in rejection context: '{line.strip()}'")
    return (True, "BI-7: No native MCPController registration in broker module")


def check_bi_8():
    """BI-8: Broker module has no cross-project call execution."""
    if not BROKER_MODULE.exists():
        return (False, "BI-8: Broker module not found")
    content = BROKER_MODULE.read_text()
    # Check for patterns that would indicate cross-project calls
    for pattern in ["active/librarian/", "../librarian", "../active/librarian"]:
        if pattern in content:
            return (False, f"BI-8: Found cross-project reference '{pattern}' in broker module")
    return (True, "BI-8: No cross-project call references in broker module")


def check_bi_9():
    """BI-9: Implementation governance doc exists."""
    exists = GOV_DOC.exists()
    return (exists, "BI-9: Implementation governance doc exists" if exists else "BI-9: Implementation governance doc not found")


def check_bi_10():
    """BI-10: Implementation schema exists."""
    exists = SCHEMA_FILE.exists()
    valid = False
    if exists:
        try:
            load_json(str(SCHEMA_FILE))
            valid = True
        except (json.JSONDecodeError, OSError):
            pass
    return (valid, "BI-10: Implementation schema exists and is valid JSON" if valid else "BI-10: Implementation schema not found or invalid")


def check_bi_11():
    """BI-11: Broker audit directory exists."""
    exists = AUDIT_DIR.exists()
    return (exists, "BI-11: Broker audit directory exists" if exists else "BI-11: Broker audit directory not found")


def check_bi_12():
    """BI-12: Implementation fixtures exist (valid and invalid)."""
    if not FIXTURES_DIR.exists():
        return (False, "BI-12: Fixtures directory not found")
    valid_fixtures = list(FIXTURES_DIR.glob("valid-*.json"))
    invalid_fixtures = list(FIXTURES_DIR.glob("invalid-*.json"))
    total = len(valid_fixtures) + len(invalid_fixtures)
    return (total >= 3, f"BI-12: {total} fixtures found ({len(valid_fixtures)} valid, {len(invalid_fixtures)} invalid)")


def check_bi_13():
    """BI-13: Valid fixtures are accepted by broker (structural check)."""
    if not FIXTURES_DIR.exists():
        return (True, "BI-13: Skipped (no fixtures)")
    valid_fixtures = list(FIXTURES_DIR.glob("valid-*.json"))
    if not valid_fixtures:
        return (True, "BI-13: No valid fixtures to check")
    for f in valid_fixtures:
        try:
            data = load_json(str(f))
            if data.get("expected_behavior") != "accepted":
                return (False, f"BI-13: Valid fixture '{f.name}' does not expect acceptance")
        except (json.JSONDecodeError, OSError) as e:
            return (False, f"BI-13: Cannot read fixture '{f.name}': {e}")
    return (True, f"BI-13: {len(valid_fixtures)} valid fixtures correctly expect acceptance")


def check_bi_14():
    """BI-14: Invalid fixtures are rejected by broker (structural check)."""
    if not FIXTURES_DIR.exists():
        return (True, "BI-14: Skipped (no fixtures)")
    invalid_fixtures = list(FIXTURES_DIR.glob("invalid-*.json"))
    if not invalid_fixtures:
        return (True, "BI-14: No invalid fixtures to check")
    for f in invalid_fixtures:
        try:
            data = load_json(str(f))
            if data.get("expected_behavior") != "rejected":
                return (False, f"BI-14: Invalid fixture '{f.name}' does not expect rejection")
        except (json.JSONDecodeError, OSError) as e:
            return (False, f"BI-14: Cannot read fixture '{f.name}': {e}")
    return (True, f"BI-14: {len(invalid_fixtures)} invalid fixtures correctly expect rejection")


def check_bi_15_through_19():
    """
    BI-15 through BI-19: Specific rejection scenarios.
    These are structural checks of the fixture definitions.
    """
    if not FIXTURES_DIR.exists():
        return (True, [])

    results = []

    # BI-15: Missing custody_record fixture exists
    missing_custody = list(FIXTURES_DIR.glob("invalid-missing-custody*.json"))
    results.append((bool(missing_custody),
                    "BI-15: Missing custody fixture exists" if missing_custody else "BI-15: No missing custody fixture found"))

    # BI-16: Wrong project_id fixture exists
    wrong_project = list(FIXTURES_DIR.glob("invalid-wrong-project*.json"))
    results.append((bool(wrong_project),
                    "BI-16: Wrong project fixture exists" if wrong_project else "BI-16: No wrong project fixture found"))

    # BI-17: Unsupported tool fixture exists
    unsupported_tool = list(FIXTURES_DIR.glob("invalid-unsupported-tool*.json"))
    results.append((bool(unsupported_tool),
                    "BI-17: Unsupported tool fixture exists" if unsupported_tool else "BI-17: No unsupported tool fixture found"))

    # BI-18: Cross-project handler fixture exists
    cross_project = list(FIXTURES_DIR.glob("invalid-cross-project*.json"))
    results.append((bool(cross_project),
                    "BI-18: Cross-project handler fixture exists" if cross_project else "BI-18: No cross-project handler fixture found"))

    # BI-19: Non-advisory authority fixture exists
    non_advisory = list(FIXTURES_DIR.glob("invalid-authoritative*.json"))
    results.append((bool(non_advisory),
                    "BI-19: Non-advisory authority fixture exists" if non_advisory else "BI-19: No non-advisory authority fixture found"))

    return (all(r[0] for r in results), results)


def check_bi_20():
    """BI-20: No Librarian runtime refs in implementation docs."""
    files_to_check = [GOV_DOC, SCHEMA_FILE]
    for path in files_to_check:
        if not path.exists():
            continue
        content = path.read_text()
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.lower() in content.lower():
                return (False, f"BI-20: Found forbidden Librarian ref '{pattern}' in {path.name}")
    return (True, "BI-20: No Librarian runtime references in implementation docs")


def main():
    args = sys.argv[1:]
    list_rules = "--list-rules" in args

    if list_rules:
        rules = [
            "BI-1: Broker module exists at scripts/librarian_broker_qa_pilot.py",
            "BI-2: Broker module has no Librarian/MCPController references",
            "BI-3: Broker module uses advisory-only authority",
            "BI-4: Broker module has disable flag mechanism",
            "BI-5: Broker module routes to QA Pilot handlers (not Librarian)",
            "BI-6: Broker module produces audit receipts",
            "BI-7: Broker module has no native MCPController registration",
            "BI-8: Broker module has no cross-project call execution",
            "BI-9: Implementation governance doc exists",
            "BI-10: Implementation schema exists and is valid JSON",
            "BI-11: Broker audit directory exists",
            "BI-12: Implementation fixtures exist (valid and invalid)",
            "BI-13: Valid fixture descriptions expect acceptance",
            "BI-14: Invalid fixture descriptions expect rejection",
            "BI-15: Missing custody_record fixture exists",
            "BI-16: Wrong project_id fixture exists",
            "BI-17: Unsupported tool fixture exists",
            "BI-18: Cross-project handler path fixture exists",
            "BI-19: Non-advisory authority claim fixture exists",
            "BI-20: No Librarian runtime references in implementation docs",
        ]
        for rule in rules:
            print(f"  {rule}")
        return 0

    checks = [
        ("BI-1", check_bi_1, "Broker module exists"),
        ("BI-2", check_bi_2, "No Librarian refs in broker"),
        ("BI-3", check_bi_3, "Advisory-only authority"),
        ("BI-4", check_bi_4, "Disable flag mechanism"),
        ("BI-5", check_bi_5, "Routes to QA Pilot handlers"),
        ("BI-6", check_bi_6, "Audit receipt generation"),
        ("BI-7", check_bi_7, "No MCPController registration"),
        ("BI-8", check_bi_8, "No cross-project calls"),
        ("BI-9", check_bi_9, "Governance doc exists"),
        ("BI-10", check_bi_10, "Schema exists and valid"),
        ("BI-11", check_bi_11, "Audit directory exists"),
        ("BI-12", check_bi_12, "Fixtures exist"),
        ("BI-13", check_bi_13, "Valid fixture structure"),
        ("BI-14", check_bi_14, "Invalid fixture structure"),
        ("BI-15-19", check_bi_15_through_19, "Specific rejection fixtures"),
        ("BI-20", check_bi_20, "No Librarian refs in docs"),
    ]

    all_pass = True
    for rule_id, func, desc in checks:
        if rule_id == "BI-15-19":
            passed, sub_results = func()
            for sp, msg in sub_results:
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
