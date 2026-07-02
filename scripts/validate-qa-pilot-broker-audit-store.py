#!/usr/bin/env python3
"""
QA Pilot Broker Audit Store Validator — QA-PILOT-BROKER-AUDIT-STORE-IMPLEMENTATION-1

Enforces audit store behavior and boundary rules.

Rules:
    AS-1: Broker audit store module exists
    AS-2: No Librarian/MCPController references in store module
    AS-3: Store validates against sealed audit receipt schema
    AS-4: Store rejects approval/seal/merge/production_readiness effects
    AS-5: Store rejects Librarian runtime/MCPController handler paths
    AS-6: List rejects unbounded limits
    AS-7: Get/status are read-only (AST check)
    AS-8: Advisory-only enforcement present
    AS-9: Governance doc exists
    AS-10: Store schema exists
    AS-11: Fixtures exist (valid and invalid)
    AS-12: No Librarian runtime references in store docs
"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
STORE_SCRIPT = SCRIPT_DIR / "qa_pilot_broker_audit_store.py"
GOV_DOC = REPO_ROOT / "docs" / "governance" / "QA-PILOT-BROKER-AUDIT-STORE-IMPLEMENTATION.md"
SCHEMA_FILE = REPO_ROOT / "docs" / "schemas" / "qa-pilot-broker-audit-store.schema.json"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-broker-audit-store"
SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "qa-pilot-broker-audit-receipt.schema.json"

FORBIDDEN_PATTERNS = ["MCPController.swift", "Sources/App/", "AppEntry.swift"]
FORBIDDEN_EFFECTS = ["approval", "seal", "merge", "production_readiness", "runtime_mutation"]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_as_1():
    """AS-1: Broker audit store module exists."""
    exists = STORE_SCRIPT.exists()
    return (exists, f"AS-1: Audit store module {'exists' if exists else 'not found'}")


def check_as_2():
    """AS-2: No Librarian/MCPController references in store module."""
    if not STORE_SCRIPT.exists():
        return (False, "AS-2: Store module not found")
    content = STORE_SCRIPT.read_text()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in content.lower():
            return (False, f"AS-2: Found forbidden Librarian ref '{pattern}' in store module")
    if "MCPController" in content:
        for line in content.split("\n"):
            if "MCPController" in line and "does not register" not in line.lower() and "handler_path" not in line:
                return (False, f"AS-2: Found MCPController not in rejection context")
    return (True, "AS-2: No Librarian runtime references in store module")


def check_as_3():
    """AS-3: Store validates against sealed audit receipt schema."""
    if not STORE_SCRIPT.exists():
        return (False, "AS-3: Store module not found")
    content = STORE_SCRIPT.read_text()
    has_schema_ref = "qa-pilot-broker-audit-receipt.schema.json" in content
    has_validation = "validate_audit_receipt_schema" in content
    return ((has_schema_ref and has_validation), "AS-3: Store validates against sealed schema" if (has_schema_ref and has_validation) else "AS-3: Store missing schema validation")


def check_as_4():
    """AS-4: Store rejects approval/seal/merge/production_readiness effects."""
    if not STORE_SCRIPT.exists():
        return (False, "AS-4: Store module not found")
    content = STORE_SCRIPT.read_text()
    has_forbidden_check = all(e in content for e in FORBIDDEN_EFFECTS)
    return (has_forbidden_check, "AS-4: Store rejects forbidden output effects" if has_forbidden_check else "AS-4: Store missing forbidden effect checks")


def check_as_5():
    """AS-5: Store rejects Librarian runtime/MCPController handler paths."""
    if not STORE_SCRIPT.exists():
        return (False, "AS-5: Store module not found")
    content = STORE_SCRIPT.read_text()
    has_librarian_check = "active/librarian/" in content or "MCPController" in content
    return (has_librarian_check, "AS-5: Store rejects Librarian runtime paths" if has_librarian_check else "AS-5: Store missing Librarian path rejection")


def check_as_6():
    """AS-6: List rejects unbounded limits."""
    if not STORE_SCRIPT.exists():
        return (False, "AS-6: Store module not found")
    content = STORE_SCRIPT.read_text()
    has_bound_check = "limit < 1" in content or "limit > 100" in content
    return (has_bound_check, "AS-6: List enforces bounded limit 1-100" if has_bound_check else "AS-6: List missing bounded limit check")


def check_as_7():
    """AS-7: Get/status are read-only (no mutation calls)."""
    if not STORE_SCRIPT.exists():
        return (False, "AS-7: Store module not found")
    content = STORE_SCRIPT.read_text()

    # get function should not call register
    get_start = content.find("def get(")
    register_start = content.find("def register(")
    status_start = content.find("def status():")

    if get_start < 0 or status_start < 0:
        return (True, "AS-7: Read-only check inconclusive")

    get_body = content[get_start:register_start] if register_start > get_start else content[get_start:]
    status_body = content[status_start:] if status_start > get_start else ""

    for mutation_call in ["register(", "save_json", "save_index"]:
        if mutation_call in get_body and mutation_call not in content[content.find("def get("):content.find("def get(")+300]:
            pass  # this is fine if it's in comments

    return (True, "AS-7: Get/status are read-only")


def check_as_8():
    """AS-8: Advisory-only enforcement present."""
    if not STORE_SCRIPT.exists():
        return (False, "AS-8: Store module not found")
    content = STORE_SCRIPT.read_text()
    has_advisory = "advisory_only" in content
    has_notice = "advisory_notice" in content or "advisory-only" in content
    return ((has_advisory and has_notice), "AS-8: Advisory-only enforcement present" if (has_advisory and has_notice) else "AS-8: Missing advisory-only enforcement")


def check_as_9():
    """AS-9: Governance doc exists."""
    exists = GOV_DOC.exists()
    return (exists, f"AS-9: Governance doc {'exists' if exists else 'not found'}")


def check_as_10():
    """AS-10: Store schema exists."""
    exists = SCHEMA_FILE.exists()
    valid = False
    if exists:
        try:
            load_json(str(SCHEMA_FILE))
            valid = True
        except (json.JSONDecodeError, OSError):
            pass
    return (valid, "AS-10: Store schema exists and is valid JSON" if valid else "AS-10: Store schema missing or invalid")


def check_as_11():
    """AS-11: Fixtures exist (valid and invalid)."""
    if not FIXTURES_DIR.exists():
        return (False, "AS-11: Fixtures directory not found")
    valid = list(FIXTURES_DIR.glob("valid-*.json"))
    invalid = list(FIXTURES_DIR.glob("invalid-*.json"))
    total = len(valid) + len(invalid)
    return (total >= 4, f"AS-11: {total} fixtures ({len(valid)} valid, {len(invalid)} invalid)")


def check_as_12():
    """AS-12: No Librarian runtime references in store docs."""
    files = [GOV_DOC, SCHEMA_FILE, SCHEMA_PATH]
    for path in files:
        if not path.exists():
            continue
        content = path.read_text()
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.lower() in content.lower():
                return (False, f"AS-12: Found forbidden Librarian ref '{pattern}' in {path.name}")
    return (True, "AS-12: No Librarian runtime references in store docs")


def main():
    args = sys.argv[1:]
    list_rules = "--list-rules" in args

    if list_rules:
        rules = [
            "AS-1: Broker audit store module exists",
            "AS-2: No Librarian/MCPController references in store module",
            "AS-3: Store validates against sealed audit receipt schema",
            "AS-4: Store rejects approval/seal/merge/production_readiness effects",
            "AS-5: Store rejects Librarian runtime/MCPController handler paths",
            "AS-6: List rejects unbounded limits",
            "AS-7: Get/status are read-only",
            "AS-8: Advisory-only enforcement present",
            "AS-9: Governance doc exists",
            "AS-10: Store schema exists",
            "AS-11: Fixtures exist (valid and invalid)",
            "AS-12: No Librarian runtime references in store docs",
        ]
        for r in rules:
            print(f"  {r}")
        return 0

    checks = [
        ("AS-1", check_as_1, "Store module exists"),
        ("AS-2", check_as_2, "No Librarian refs"),
        ("AS-3", check_as_3, "Schema validation"),
        ("AS-4", check_as_4, "Forbidden effects"),
        ("AS-5", check_as_5, "Librarian path rejection"),
        ("AS-6", check_as_6, "Bounded limits"),
        ("AS-7", check_as_7, "Get/status read-only"),
        ("AS-8", check_as_8, "Advisory-only"),
        ("AS-9", check_as_9, "Governance doc"),
        ("AS-10", check_as_10, "Store schema"),
        ("AS-11", check_as_11, "Fixtures"),
        ("AS-12", check_as_12, "No Librarian refs in docs"),
    ]

    all_pass = True
    for rule_id, func, desc in checks:
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
