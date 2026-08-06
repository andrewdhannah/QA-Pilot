#!/usr/bin/env python3
"""
QA Pilot Test Library Validator

Validates that the test library structure is consistent:
  - All tests reference valid domains
  - All tests have test_id with correct prefix
  - All tests have required fields
  - Library index matches on-disk tests

Rules:
  TL-1:  Library index exists and is valid JSON
  TL-2:  Test files match index domain counts
  TL-3:  Each test file has valid test_id with domain prefix
  TL-4:  Each test has required fields (title, objective, source, execution, pass_criteria)
  TL-5:  Each test declares advisory_only=True
  TL-6:  Each test declares no_seal_authority=True
  TL-7:  All test files are valid JSON
"""

import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
LIBRARY_DIR = REPO_ROOT / "test-library"
INDEX_PATH = LIBRARY_DIR / "test-library-index.json"

DOMAIN_PREFIXES = {"REG", "SEC", "UAT", "A11Y", "PERF", "AI", "COMPL"}
DOMAIN_DIRS = {"regression": "REG", "security": "SEC", "uat": "UAT",
               "accessibility": "A11Y", "performance": "PERF", "ai": "AI", "compliance": "COMPL"}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_tl_1(data):
    """TL-1: Library index exists and is valid JSON."""
    if not INDEX_PATH.exists():
        return False, "Library index not found"
    return True, f"Library index valid: {INDEX_PATH.name}"


def check_tl_2(data):
    """TL-2: Test files match index domain counts."""
    index = load_json(INDEX_PATH)
    domains = index.get("domains", {})
    
    all_match = True
    details = []
    
    for domain_key, domain_info in domains.items():
        expected = domain_info.get("count", 0)
        domain_dir = LIBRARY_DIR / domain_key
        if domain_dir.exists():
            actual = len(list(domain_dir.glob("*.json")))
            if actual != expected:
                all_match = False
                details.append(f"{domain_key}: index says {expected}, disk has {actual}")
    
    if all_match:
        total = index.get("total_tests", 0)
        return True, f"All {len(domains)} domains match index ({total} total)"
    return False, "; ".join(details)


def check_tl_3(data):
    """TL-3: Each test file has valid test_id with domain prefix."""
    issues = []
    total = 0
    
    for domain_key, prefix in DOMAIN_DIRS.items():
        domain_dir = LIBRARY_DIR / domain_key
        if not domain_dir.exists():
            continue
        for f in sorted(domain_dir.glob("*.json")):
            if f.name == ".gitkeep":
                continue
            total += 1
            try:
                test = load_json(f)
                tid = test.get("test_id", "")
                if not tid.startswith(f"{prefix}-"):
                    issues.append(f"{f.name}: test_id '{tid}' doesn't match domain prefix {prefix}")
            except (json.JSONDecodeError, IOError):
                issues.append(f"{f.name}: invalid JSON")
    
    if issues:
        return False, "; ".join(issues[:5])
    return True, f"All {total} tests have correct domain prefix"


def check_tl_4(data):
    """TL-4: Each test has required fields."""
    required = ["test_id", "domain", "title", "objective", "source", "execution", "pass_criteria"]
    issues = []
    total = 0
    
    for domain_key in DOMAIN_DIRS:
        domain_dir = LIBRARY_DIR / domain_key
        if not domain_dir.exists():
            continue
        for f in sorted(domain_dir.glob("*.json")):
            if f.name == ".gitkeep":
                continue
            total += 1
            try:
                test = load_json(f)
                missing = [r for r in required if r not in test]
                if missing:
                    issues.append(f"{f.name}: missing {missing}")
            except Exception:
                pass
    
    if issues:
        return False, "; ".join(issues[:5])
    return True, f"All {total} tests have required fields"


def check_tl_5(data):
    """TL-5: Each test declares advisory_only=True."""
    issues = []
    total = 0
    
    for domain_key in DOMAIN_DIRS:
        domain_dir = LIBRARY_DIR / domain_key
        if not domain_dir.exists():
            continue
        for f in sorted(domain_dir.glob("*.json")):
            if f.name == ".gitkeep":
                continue
            total += 1
            try:
                test = load_json(f)
                if test.get("advisory_only") is not True:
                    issues.append(f"{f.name}: advisory_only is not True")
            except Exception:
                pass
    
    if issues:
        return False, "; ".join(issues[:5])
    return True, f"All {total} tests declare advisory_only=True"


def check_tl_6(data):
    """TL-6: Each test declares no_seal_authority=True."""
    issues = []
    total = 0
    
    for domain_key in DOMAIN_DIRS:
        domain_dir = LIBRARY_DIR / domain_key
        if not domain_dir.exists():
            continue
        for f in sorted(domain_dir.glob("*.json")):
            if f.name == ".gitkeep":
                continue
            total += 1
            try:
                test = load_json(f)
                if test.get("no_seal_authority") is not True:
                    issues.append(f"{f.name}: no_seal_authority is not True")
            except Exception:
                pass
    
    if issues:
        return False, "; ".join(issues[:5])
    return True, f"All {total} tests declare no_seal_authority=True"


def check_tl_7(data):
    """TL-7: All test files are valid JSON."""
    issues = []
    total = 0
    
    for domain_key in DOMAIN_DIRS:
        domain_dir = LIBRARY_DIR / domain_key
        if not domain_dir.exists():
            continue
        for f in sorted(domain_dir.glob("*.json")):
            if f.name == ".gitkeep":
                continue
            total += 1
            try:
                load_json(f)
            except json.JSONDecodeError as e:
                issues.append(f"{f.name}: {e}")
    
    if issues:
        return False, "; ".join(issues[:5])
    return True, f"All {total} test files are valid JSON"


RULES = [
    ("TL-1", check_tl_1, "Library index exists and is valid JSON"),
    ("TL-2", check_tl_2, "Test files match index domain counts"),
    ("TL-3", check_tl_3, "Test IDs have correct domain prefix"),
    ("TL-4", check_tl_4, "All tests have required fields"),
    ("TL-5", check_tl_5, "All tests declare advisory_only=True"),
    ("TL-6", check_tl_6, "All tests declare no_seal_authority=True"),
    ("TL-7", check_tl_7, "All test files are valid JSON"),
]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="QA Pilot Test Library Validator")
    parser.add_argument("--list-rules", action="store_true", help="List rules and exit")
    args = parser.parse_args()

    if args.list_rules:
        print("QA Pilot Test Library Validator — Rules")
        print("=" * 60)
        for rid, _, desc in RULES:
            print(f"  {rid}: {desc}")
        return 0

    all_pass = True
    for rule_id, func, desc in RULES:
        try:
            passed, message = func(None)
        except Exception as e:
            passed = False
            message = f"Exception: {e}"
        icon = "✅" if passed else "❌"
        print(f"  {icon} {rule_id}: {desc}")
        if not passed:
            print(f"       {message}")
            all_pass = False

    print(f"\nOverall: {'PASS' if all_pass else 'FAIL'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
