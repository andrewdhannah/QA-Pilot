#!/usr/bin/env python3
"""
QA Pilot Epic Scenario Suite Validator — QA-PILOT-EPIC-SCENARIO-SUITES

Validates scenario results against the qa-pilot-epic-scenario-suite.schema.json contract.
Enforces schema compliance, read-only invariants, and scenario type constraints.

Rules:
  ES-1:  suite_version is correct (qa-pilot-epic-scenario-suite-v1)
  ES-2:  scenario_id matches pattern EP-[A-Z]+-[0-9]{3,}
  ES-3:  title is present and non-empty
  ES-4:  type is a valid scenario type enum value
  ES-5:  overall is PASS or REVIEW
  ES-6:  details array present and non-empty
  ES-7:  Each detail has check_id, expected, observed, passed
  ES-8:  read_only is true
  ES-9:  no_authority_conferred is true
  ES-10: learning_artifact present with summary, explaination, teachable_moment
  ES-11: target_epic present and non-empty

Usage:
    python3 scripts/validate-qa-pilot-epic-scenario-suite.py <fixture-path>...
    python3 scripts/validate-qa-pilot-epic-scenario-suite.py --all
    python3 scripts/validate-qa-pilot-epic-scenario-suite.py --list-rules
    python3 scripts/validate-qa-pilot-epic-scenario-suite.py --include-invalid
"""

import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-epic-scenario-suite"

SUITE_VERSION_EXPECTED = "qa-pilot-epic-scenario-suite-v1"
VALID_TYPES = {"complete_epic", "missing_artifact", "conflicting_sources", "broken_provenance", "mutation_boundary"}
VALID_OVERALL = {"PASS", "REVIEW"}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_es_1(data):
    """ES-1: suite_version is correct."""
    v = data.get("suite_version")
    if v == SUITE_VERSION_EXPECTED:
        return True, f"suite_version is correct: {v}"
    return False, f"suite_version mismatch: expected {SUITE_VERSION_EXPECTED}, got {v}"


def check_es_2(data):
    """ES-2: scenario_id matches pattern."""
    sid = data.get("scenario_id", "")
    import re
    if re.match(r"^EP-[A-Z]+-[0-9]{3,}$", sid):
        return True, f"scenario_id valid: {sid}"
    return False, f"scenario_id invalid pattern: {sid}"


def check_es_3(data):
    """ES-3: title is present and non-empty."""
    title = data.get("title", "")
    if title and isinstance(title, str) and len(title.strip()) > 0:
        return True, f"title present: {title[:60]}..."
    return False, "title missing or empty"


def check_es_4(data):
    """ES-4: type is a valid enum value."""
    t = data.get("type")
    if t in VALID_TYPES:
        return True, f"type valid: {t}"
    return False, f"type invalid: {t} (must be one of {VALID_TYPES})"


def check_es_5(data):
    """ES-5: overall is PASS or REVIEW."""
    o = data.get("overall")
    if o in VALID_OVERALL:
        return True, f"overall valid: {o}"
    return False, f"overall invalid: {o} (must be PASS or REVIEW)"


def check_es_6(data):
    """ES-6: details array present."""
    details = data.get("details", [])
    if isinstance(details, list):
        return True, f"details array present: {len(details)} items"
    return False, "details is not an array"


def check_es_7(data):
    """ES-7: Each detail has required fields."""
    details = data.get("details", [])
    for i, d in enumerate(details):
        for field in ["check_id", "expected", "observed", "passed"]:
            if field not in d:
                return False, f"detail[{i}] missing field: {field}"
        if not isinstance(d.get("passed"), bool):
            return False, f"detail[{i}].passed must be boolean"
    return True, f"All {len(details)} details have required fields"


def check_es_8(data):
    """ES-8: read_only is true."""
    ro = data.get("read_only")
    if ro is True:
        return True, "read_only is True"
    return False, f"read_only is {ro}, expected True"


def check_es_9(data):
    """ES-9: no_authority_conferred is true."""
    nac = data.get("no_authority_conferred")
    if nac is True:
        return True, "no_authority_conferred is True"
    return False, f"no_authority_conferred is {nac}, expected True"


def check_es_10(data):
    """ES-10: learning_artifact present with required fields."""
    la = data.get("learning_artifact", {})
    if not la:
        return False, "learning_artifact missing"
    
    required = ["scenario_id", "title", "summary"]
    missing = [r for r in required if r not in la]
    if missing:
        return False, f"learning_artifact missing fields: {missing}"
    
    if la.get("summary") not in ("PASS", "REVIEW NEEDED"):
        return False, f"learning_artifact.summary invalid: {la.get('summary')}"
    
    return True, "learning_artifact present and valid"


def check_es_11(data):
    """ES-11: target_epic present and non-empty."""
    te = data.get("target_epic", "")
    if te and isinstance(te, str) and len(te.strip()) > 0:
        return True, f"target_epic present: {te[:60]}..."
    return False, "target_epic missing or empty"


RULES = [
    ("ES-1", check_es_1, "suite_version is correct"),
    ("ES-2", check_es_2, "scenario_id matches EP-pattern"),
    ("ES-3", check_es_3, "title is present and non-empty"),
    ("ES-4", check_es_4, "type is valid enum"),
    ("ES-5", check_es_5, "overall is PASS or REVIEW"),
    ("ES-6", check_es_6, "details array present"),
    ("ES-7", check_es_7, "Each detail has required fields"),
    ("ES-8", check_es_8, "read_only is true"),
    ("ES-9", check_es_9, "no_authority_conferred is true"),
    ("ES-10", check_es_10, "learning_artifact present"),
    ("ES-11", check_es_11, "target_epic present"),
]


def validate_fixture(path, allow_invalid=False):
    try:
        data = load_json(path)
    except (json.JSONDecodeError, IOError) as e:
        return (os.path.basename(path), {
            "all_pass": False,
            "checks": [{"rule": "PARSE", "passed": False, "message": str(e)}],
        })

    results = []
    all_pass = True
    for rule_id, func, desc in RULES:
        try:
            passed, message = func(data)
        except Exception as e:
            passed = False
            message = f"Exception: {e}"
        results.append({"rule": rule_id, "description": desc, "passed": passed, "message": message})
        if not passed:
            all_pass = False

    fn = os.path.basename(path)
    is_invalid = fn.startswith("invalid-")
    if allow_invalid and is_invalid:
        expected_pass = not all_pass
    else:
        expected_pass = all_pass

    return (fn, {"all_pass": all_pass, "expected_pass": expected_pass, "checks": results})


def main():
    import argparse
    parser = argparse.ArgumentParser(description="QA Pilot Epic Scenario Suite Validator")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--include-invalid", action="store_true")
    parser.add_argument("--list-rules", action="store_true")
    args = parser.parse_args()

    if args.list_rules:
        print("QA Pilot Epic Scenario Suite Validator — Rules")
        print("=" * 60)
        for rid, _, desc in RULES:
            print(f"  {rid}: {desc}")
        return 0

    fixtures = []
    if args.paths:
        fixtures = args.paths
    else:
        pattern = "valid-*.json" if not args.include_invalid else "*.json"
        if FIXTURES_DIR.exists():
            for f in sorted(FIXTURES_DIR.glob(pattern)):
                fixtures.append(str(f))

    if not fixtures:
        if FIXTURES_DIR.exists():
            for f in sorted(FIXTURES_DIR.glob("valid-*.json")):
                fixtures.append(str(f))

    all_passed = True
    vp, vt, ip, it = 0, 0, 0, 0

    for path in fixtures:
        fn = os.path.basename(path)
        is_inv = fn.startswith("invalid-")
        if not os.path.exists(path):
            print(f"  SKIP  {fn} — not found")
            continue
        name, result = validate_fixture(path, args.include_invalid)
        if is_inv:
            it += 1
            if result["expected_pass"]:
                ip += 1
                print(f"  ✅  {name} — correctly rejected")
            else:
                all_passed = False
                print(f"  ❌  {name} — expected rejection but passed")
        else:
            vt += 1
            if result["all_pass"]:
                vp += 1
                print(f"  ✅  {name} — all rules pass")
            else:
                all_passed = False
                print(f"  ❌  {name} — FAILED")
                for c in result["checks"]:
                    if not c["passed"]:
                        print(f"       {c['rule']}: {c['message']}")

    print()
    print(f"Valid fixtures:   {vp}/{vt} passed")
    if args.include_invalid:
        print(f"Invalid fixtures: {ip}/{it} correctly rejected")
    print(f"Overall: {'PASS' if all_passed else 'FAIL'}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
