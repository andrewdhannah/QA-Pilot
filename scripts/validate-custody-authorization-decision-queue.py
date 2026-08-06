#!/usr/bin/env python3
"""
validate-custody-authorization-decision-queue.py — Decision Queue Validator

Validates that custody posture findings surfaced during startup are governed
by the Owner decision queue and remain advisory only.

Rules:
  CDQ-1:  advisory must be true
  CDQ-2:  owner_required must be true
  CDQ-3:  No approve/seal/execute/write controls (queue entry does not confer authority)
  CDQ-4:  No index mutation claim
  CDQ-5:  No custody receipt creation claim
  CDQ-6:  No sprint advancement claim
  CDQ-7:  source must be "startup_report"
  CDQ-8:  Cross-project entries require owner_authorized: true
  CDQ-9:  status must be "pending" on creation (owner_decision must be null)
  CDQ-10: owner_decision must be null on creation
  CDQ-11: finding_type must be from allowed set
  CDQ-12: custody_context.contract_id must reference valid sealed contract if present

Modes:
  fixture   — Validate fixture files against CDQ rules
  validate  — Validate a specific queue entry JSON
"""

import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_FILE = os.path.join(PROJECT_ROOT, "docs/schemas/custody-authorization-decision-queue.schema.json")

ALLOWED_FINDING_TYPES = {
    "degraded_custody", "missing_receipt", "stale_index",
    "violation_detected", "review_item", "cross_project_reference"
}

KNOWN_SEALED_CONTRACTS = [
    "#23", "#24", "#25", "#26", "#27", "#28", "#29", "#30"
]

FORBIDDEN_CONTROL_WORDS = ["approve", "seal", "execute", "write"]

results = []
exit_code = 0


def check(rule_id: str, condition: bool, message: str):
    global exit_code
    status = "PASS" if condition else "FAIL"
    results.append((rule_id, status, message))
    if not condition:
        exit_code = 1


def read_file(path: str) -> str:
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def json_parse(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def validate_entry(data: dict) -> list:
    """Validate a single queue entry against all CDQ rules."""
    entry_results = []

    # CDQ-1: advisory must be true
    advisory = data.get("advisory", False)
    entry_results.append(("CDQ-1", advisory is True,
        "advisory=true" if advisory is True
        else f"advisory={advisory} — must be true"))

    # CDQ-2: owner_required must be true
    owner_req = data.get("owner_required", False)
    entry_results.append(("CDQ-2", owner_req is True,
        "owner_required=true" if owner_req is True
        else f"owner_required={owner_req} — must be true"))

    # CDQ-3: No approve/seal/execute/write controls
    controls = data.get("controls", data.get("surface_controls", {}))
    if isinstance(controls, dict):
        forbidden_active = [w for w in FORBIDDEN_CONTROL_WORDS if controls.get(w) is True]
    else:
        forbidden_active = []
    entry_results.append(("CDQ-3", len(forbidden_active) == 0,
        "No approve/seal/execute/write controls" if len(forbidden_active) == 0
        else f"Forbidden controls: {forbidden_active}"))

    # CDQ-4: No index mutation claim
    index_claim = data.get("index_mutated", False) or \
        data.get("claims", {}).get("index_mutated", False)
    entry_results.append(("CDQ-4", not index_claim,
        "No index mutation claim" if not index_claim
        else "Claims index mutation — REJECTED"))

    # CDQ-5: No receipt creation claim
    receipt_claim = data.get("receipt_created", False) or \
        data.get("claims", {}).get("receipt_created", False)
    entry_results.append(("CDQ-5", not receipt_claim,
        "No receipt creation claim" if not receipt_claim
        else "Claims receipt creation — REJECTED"))

    # CDQ-6: No sprint advancement claim
    sprint_claim = data.get("sprint_advanced", False) or \
        data.get("claims", {}).get("sprint_advanced", False)
    entry_results.append(("CDQ-6", not sprint_claim,
        "No sprint advancement claim" if not sprint_claim
        else "Claims sprint advancement — REJECTED"))

    # CDQ-7: source must be "startup_report"
    source = data.get("source", "")
    entry_results.append(("CDQ-7", source == "startup_report",
        f"source='{source}'" if source == "startup_report"
        else f"source='{source}' — must be 'startup_report'"))

    # CDQ-8: Cross-project entries require owner_authorized
    cross_project = data.get("cross_project", False)
    owner_auth = data.get("owner_authorized", False)
    if cross_project:
        cdq8_ok = owner_auth is True
        entry_results.append(("CDQ-8", cdq8_ok,
            "Cross-project entry has owner_authorized=true" if cdq8_ok
            else "Cross-project entry without owner_authorized — REJECTED"))
    else:
        entry_results.append(("CDQ-8", True,
            "Not a cross-project entry"))

    # CDQ-9: status must be "pending" on creation
    # Post-creation states (owner_reviewed, deferred) require owner_decision or owner_decided_at
    status = data.get("status", "")
    owner_dec = data.get("owner_decision")
    owner_decided_at = data.get("owner_decided_at")
    has_owner_action = owner_dec is not None or owner_decided_at is not None

    if has_owner_action:
        # Entry has been through Owner review — status can be owner_reviewed or deferred
        cdq9_ok = status in ("owner_reviewed", "deferred")
        cdq9_msg = f"status='{status}' (post-creation with Owner action — {'allowed' if cdq9_ok else 'should be owner_reviewed or deferred'})"
    else:
        # Fresh entry — must be pending
        cdq9_ok = status == "pending"
        cdq9_msg = f"status='{status}'" if status == "pending" else f"status='{status}' — fresh entry must be 'pending'"
    entry_results.append(("CDQ-9", cdq9_ok, cdq9_msg))

    # CDQ-10: owner_decision must be null on creation
    if has_owner_action:
        cdq10_ok = owner_dec in ("accept", "reject", "defer")
        cdq10_msg = f"owner_decision='{owner_dec}' (post-creation — {'valid' if cdq10_ok else 'must be accept/reject/defer'})"
    else:
        cdq10_ok = owner_dec is None
        cdq10_msg = "owner_decision=null" if owner_dec is None else f"owner_decision='{owner_dec}' — must be null on creation"
    entry_results.append(("CDQ-10", cdq10_ok, cdq10_msg))

    # CDQ-11: finding_type must be from allowed set
    ft = data.get("finding_type", "")
    entry_results.append(("CDQ-11", ft in ALLOWED_FINDING_TYPES,
        f"finding_type='{ft}'" if ft in ALLOWED_FINDING_TYPES
        else f"finding_type='{ft}' — must be one of {sorted(ALLOWED_FINDING_TYPES)}"))

    # CDQ-12: custody_context.contract_id must reference valid sealed contract
    ctx = data.get("custody_context", {})
    contract_id = ctx.get("contract_id", "") if isinstance(ctx, dict) else ""
    if contract_id:
        cdq12_ok = contract_id in KNOWN_SEALED_CONTRACTS
        entry_results.append(("CDQ-12", cdq12_ok,
            f"contract_id='{contract_id}' in known sealed contracts" if cdq12_ok
            else f"contract_id='{contract_id}' — not in known sealed contracts"))
    else:
        entry_results.append(("CDQ-12", True,
            "No contract_id reference (valid for general findings)"))

    return entry_results


def validate_fixture(fixture_path: str) -> dict:
    """Validate a single fixture file against CDQ rules."""
    content = read_file(fixture_path)
    data = json_parse(content) if content else None
    name = os.path.basename(fixture_path)

    if data is None:
        return {"valid": False, "results": [("CDQ-FMT", False, "Invalid JSON")], "name": name}

    entry_results = validate_entry(data)

    is_negative = any(w in name for w in [
        "claims-", "false", "unauthorized", "not-", "not-pending", "not-null",
        "advisory-false", "owner-required-false", "source-not", "invalid"
    ])

    fi_fails = sum(1 for _, s, _ in entry_results if (isinstance(s, bool) and not s) or s == "FAIL")

    if is_negative:
        has_failure = fi_fails > 0
        entry_results.append(("CDQ-OVERALL", has_failure,
            f"Negative fixture: {fi_fails} CDQ violations detected (expected)" if has_failure
            else "Negative fixture: no CDQ violations found — should have been rejected"))
    else:
        all_pass = fi_fails == 0
        entry_results.append(("CDQ-OVERALL", all_pass,
            "All CDQ rules pass" if all_pass
            else f"{fi_fails} CDQ violations"))

    return {"valid": fi_fails == 0 if not is_negative else fi_fails > 0,
            "results": entry_results, "name": name}


def list_fixtures(fixtures_dir: str = None) -> list:
    if fixtures_dir is None:
        fixtures_dir = os.path.join(PROJECT_ROOT, "docs/examples/custody-authorization-decision-queue")
    fixtures = []
    if os.path.isdir(fixtures_dir):
        for f in sorted(os.listdir(fixtures_dir)):
            if f.endswith(".json"):
                fixtures.append(os.path.join(fixtures_dir, f))
    return fixtures


def main():
    global exit_code

    parser = argparse.ArgumentParser(description="Custody Authorization Decision Queue Validator")
    parser.add_argument("mode", nargs="?", default="fixture",
                        choices=["fixture", "validate"])
    parser.add_argument("--input", help="Input file for validate mode")
    parser.add_argument("--fixture-dir", help="Fixture directory override")

    args = parser.parse_args()

    print("Custody Authorization Decision Queue Validator")
    print("==============================================")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Mode: {args.mode}")
    print()

    if args.mode == "fixture":
        fixtures_dir = args.fixture_dir if args.fixture_dir else \
            os.path.join(PROJECT_ROOT, "docs/examples/custody-authorization-decision-queue")
        fixtures = sorted(os.listdir(fixtures_dir)) if os.path.isdir(fixtures_dir) else []

        if not fixtures:
            print("No fixtures found.")
            sys.exit(1)

        pass_count = 0
        fail_count = 0
        for fi_file in fixtures:
            fi_path = os.path.join(fixtures_dir, fi_file) if not fi_file.startswith("/") else fi_file
            if not fi_path.endswith(".json"):
                continue
            result = validate_fixture(fi_path)
            name = result["name"]
            is_valid = result["valid"]
            fi_results = result["results"]

            if is_valid:
                pass_count += 1
                print(f"  ✅  {name}: ALL CDQ CHECKS PASS")
            else:
                fail_count += 1
                print(f"  ❌  {name}: CDQ VIOLATIONS")
            for rule_id, status, message in fi_results:
                symbol = "✅" if status else "❌"
                print(f"       {symbol}  {rule_id}: {message}")

        print()
        print(f"Fixture results: {pass_count} passed, {fail_count} failed")
        if fail_count > 0:
            exit_code = 1

    elif args.mode == "validate":
        if not args.input:
            print("❌  validate mode requires --input <file>")
            sys.exit(1)
        result = validate_fixture(args.input)
        name = result["name"]
        is_valid = result["valid"]
        print(f"Validation of {name}: {'PASS' if is_valid else 'FAIL'}")
        for rule_id, status, message in result["results"]:
            symbol = "✅" if status else "❌"
            print(f"  {symbol}  {rule_id}: {message}")
        if not is_valid:
            exit_code = 1

    passes = sum(1 for _, s, _ in results if s == "PASS")
    fails = sum(1 for _, s, _ in results if s == "FAIL")
    print()
    print("=" * 50)
    print(f"Results: {passes} passed, {fails} failed")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
