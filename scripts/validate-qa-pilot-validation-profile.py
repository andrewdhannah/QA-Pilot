#!/usr/bin/env python3
"""
QA Pilot Validation Profile Validator

Validates project validation profiles against the schema.
Ensures profiles correctly bridge startup to QA-Pilot testing.

Rules:
  VP-1: Profile has valid schema version
  VP-2: Profile has project_id
  VP-3: Enabled domains is non-empty array of valid domain values
  VP-4: Required reviews is non-empty array
  VP-5: advisory_only is true
  VP-6: no_seal_authority is true
  VP-7: startup_routing.available is boolean
  VP-8: qa_pilot_version is present
"""

import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PROFILES_DIR = REPO_ROOT / "profiles"

VALID_DOMAINS = {"regression", "security", "uat", "accessibility", "performance", "ai", "compliance"}
VALID_REVIEWS = {"owner", "peer", "automated_only"}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_vp_1(data):
    v = data.get("profile_schema")
    if v == "qa-project-validation-profile-v1":
        return True, f"Schema version correct: {v}"
    return False, f"Schema version mismatch: {v}"


def check_vp_2(data):
    pid = data.get("project_id")
    if pid and isinstance(pid, str) and len(pid) > 0:
        return True, f"Project ID: {pid}"
    return False, "Missing project_id"


def check_vp_3(data):
    domains = data.get("enabled_domains", [])
    if not domains or not isinstance(domains, list):
        return False, "enabled_domains is empty or not an array"
    invalid = [d for d in domains if d not in VALID_DOMAINS]
    if invalid:
        return False, f"Invalid domains: {invalid}"
    return True, f"{len(domains)} valid domains: {domains}"


def check_vp_4(data):
    reviews = data.get("required_reviews", [])
    if not reviews or not isinstance(reviews, list):
        return False, "required_reviews is empty or not an array"
    invalid = [r for r in reviews if r not in VALID_REVIEWS]
    if invalid:
        return False, f"Invalid review types: {invalid}"
    return True, f"Reviews: {reviews}"


def check_vp_5(data):
    ao = data.get("advisory_only")
    if ao is True:
        return True, "advisory_only is True"
    return False, f"advisory_only is {ao}, expected True"


def check_vp_6(data):
    nsa = data.get("no_seal_authority")
    if nsa is True:
        return True, "no_seal_authority is True"
    return False, f"no_seal_authority is {nsa}, expected True"


def check_vp_7(data):
    sr = data.get("startup_routing", {})
    avail = sr.get("available")
    if isinstance(avail, bool):
        return True, f"startup_routing.available: {avail}"
    return False, f"startup_routing.available must be boolean, got {type(avail).__name__}"


def check_vp_8(data):
    version = data.get("qa_pilot_version")
    if version and isinstance(version, str) and len(version) > 0:
        return True, f"QA-Pilot version: {version}"
    return False, "qa_pilot_version missing or empty"


RULES = [
    ("VP-1", check_vp_1, "Schema version correct"),
    ("VP-2", check_vp_2, "Project ID present"),
    ("VP-3", check_vp_3, "Enabled domains valid"),
    ("VP-4", check_vp_4, "Required reviews valid"),
    ("VP-5", check_vp_5, "advisory_only is true"),
    ("VP-6", check_vp_6, "no_seal_authority is true"),
    ("VP-7", check_vp_7, "startup_routing.available is boolean"),
    ("VP-8", check_vp_8, "qa_pilot_version present"),
]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="QA Pilot Validation Profile Validator")
    parser.add_argument("paths", nargs="*", help="Profile JSON files to validate")
    parser.add_argument("--all", action="store_true", help="Validate all profiles in profiles/")
    parser.add_argument("--list-rules", action="store_true", help="List rules and exit")
    args = parser.parse_args()

    if args.list_rules:
        print("QA Pilot Validation Profile Validator — Rules")
        print("=" * 60)
        for rid, _, desc in RULES:
            print(f"  {rid}: {desc}")
        return 0

    profiles = []
    if args.paths:
        profiles = args.paths
    elif args.all:
        if PROFILES_DIR.exists():
            for f in sorted(PROFILES_DIR.glob("*validation*.json")):
                profiles.append(str(f))
    else:
        if PROFILES_DIR.exists():
            for f in sorted(PROFILES_DIR.glob("*validation*.json")):
                profiles.append(str(f))

    if not profiles:
        print("No profile files found")
        return 0

    all_pass = True
    for path in profiles:
        name = Path(path).name
        try:
            data = load_json(path)
        except Exception as e:
            print(f"  ❌  {name}: Failed to parse: {e}")
            all_pass = False
            continue

        results = []
        file_pass = True
        for rid, func, desc in RULES:
            try:
                passed, msg = func(data)
            except Exception as e:
                passed = False
                msg = f"Exception: {e}"
            results.append((rid, passed, msg))
            if not passed:
                file_pass = False

        if file_pass:
            print(f"  ✅  {name} — all rules pass")
        else:
            all_pass = False
            print(f"  ❌  {name} — FAILED")
            for rid, passed, msg in results:
                if not passed:
                    print(f"       {rid}: {msg}")

    print(f"\nOverall: {'PASS' if all_pass else 'FAIL'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
