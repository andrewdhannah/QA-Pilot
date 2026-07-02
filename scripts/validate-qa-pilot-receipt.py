#!/usr/bin/env python3
"""
QA Pilot Production Receipt Validator — QA-PILOT-PRODUCTION-LANE-A-1

Enforces PR-1 through PR-12 business rules on QA Pilot production receipt fixtures.

Usage:
    python3 scripts/validate-qa-pilot-receipt.py [--all] [--include-invalid] [--list-rules] [<fixture-path>...]

Rules:
    PR-1:  Receipt uses valid Draft 2020-12 schema
    PR-2:  authority is const 'advisory'
    PR-3:  non_approval_statement is present and >= 20 characters
    PR-4:  content_hash matches sha256: pattern
    PR-5:  receipt_id follows qapr- pattern
    PR-6:  packet_type is from allowed enum
    PR-7:  librarian_receipt_refs has valid receipt_type enum
    PR-8:  qa_packet_refs has valid packet_type enum
    PR-9:  limitations is non-empty (required)
    PR-10: If status is blocked or partial, escalation_triggers must be non-empty
    PR-11: If results.summary.outcome is fail or blocked, recommendation must not be 'proceed'
    PR-12: evidence_kind values are from allowed production set
"""

import json
import os
import re
import sys
from pathlib import Path

# Allowed enums
ALLOWED_PACKET_TYPES = [
    "QAProductionReceipt",
    "QAProductionEvidenceReceipt",
    "QAProductionVerificationReceipt",
    "QAProductionReadinessReceipt",
]
ALLOWED_LIBRARIAN_RECEIPT_TYPES = [
    "chain_validation",
    "apply_receipt",
    "owner_action_receipt",
    "candidate_receipt",
    "registry_snapshot",
]
ALLOWED_QA_PACKET_TYPES = [
    "QAPlanningPacket",
    "QAEvidenceChecklist",
    "QAManualVerificationScript",
    "QAReadinessAssessment",
]
ALLOWED_EVIDENCE_KINDS = [
    "document_review",
    "fixture_validation",
    "validator_output",
    "command_output",
    "screenshot_reference",
    "human_observation",
    "repository_status",
    "receipt_reference",
    "schema_validation",
    "hash_verification",
]
ALLOWED_STATUSES = ["draft", "completed", "partial", "blocked", "superseded"]
ALLOWED_OUTCOMES = ["pass", "partial_pass", "fail", "blocked", "inconclusive"]
ALLOWED_RECOMMENDATIONS = [
    "proceed",
    "proceed_with_caveats",
    "request_revision",
    "owner_review_required",
    "do_not_proceed",
]
ALLOWED_CHECK_STATUSES = ["pass", "fail", "blocked", "skipped", "inconclusive"]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_pr_1(data):
    """PR-1: Receipt uses valid schema (has $schema field pointing to receipt schema)."""
    schema = data.get("$schema", "")
    if "qa-pilot-receipt.schema.json" not in schema:
        return (False, "Missing or invalid $schema reference (expected qa-pilot-receipt.schema.json)")
    return (True, "Valid $schema reference")


def check_pr_2(data):
    """PR-2: authority is const 'advisory'."""
    auth = data.get("authority", "")
    if auth != "advisory":
        return (False, f"authority must be 'advisory', got '{auth}'")
    return (True, "authority is advisory")


def check_pr_3(data):
    """PR-3: non_approval_statement is present and >= 20 characters."""
    stmt = data.get("non_approval_statement", "")
    if not stmt:
        return (False, "non_approval_statement is missing")
    if len(stmt) < 20:
        return (False, f"non_approval_statement too short ({len(stmt)} chars, need >= 20)")
    return (True, f"non_approval_statement present ({len(stmt)} chars)")


def check_pr_4(data):
    """PR-4: content_hash matches sha256: pattern."""
    ch = data.get("content_hash", "")
    if not re.match(r"^sha256:[A-Fa-f0-9]{64}$", ch):
        return (False, f"content_hash must match sha256:[64 hex chars], got '{ch[:30]}...'")
    return (True, "content_hash has valid sha256: pattern")


def check_pr_5(data):
    """PR-5: receipt_id follows qapr- pattern."""
    rid = data.get("receipt_id", "")
    if not re.match(r"^qapr-\d{8}-\d{3,}$", rid):
        return (False, f"receipt_id must match qapr-YYYYMMDD-NNN pattern, got '{rid}'")
    return (True, f"receipt_id '{rid}' is valid")


def check_pr_6(data):
    """PR-6: packet_type is from allowed enum."""
    pt = data.get("packet_type", "")
    if pt not in ALLOWED_PACKET_TYPES:
        return (False, f"packet_type '{pt}' not in allowed set: {ALLOWED_PACKET_TYPES}")
    return (True, f"packet_type '{pt}' is valid")


def check_pr_7(data):
    """PR-7: librarian_receipt_refs has valid receipt_type enum."""
    refs = data.get("librarian_receipt_refs", [])
    if not isinstance(refs, list):
        return (False, "librarian_receipt_refs must be an array")
    for i, ref in enumerate(refs):
        rt = ref.get("receipt_type", "")
        if rt not in ALLOWED_LIBRARIAN_RECEIPT_TYPES:
            return (False, f"librarian_receipt_refs[{i}].receipt_type '{rt}' invalid")
        rid = ref.get("receipt_id", "")
        if not re.match(r"^nrr-\d{8}-\d{3,}$", rid):
            return (False, f"librarian_receipt_refs[{i}].receipt_id '{rid}' must match nrr- pattern")
    return (True, f"All {len(refs)} librarian_receipt_refs valid")


def check_pr_8(data):
    """PR-8: qa_packet_refs has valid packet_type enum."""
    refs = data.get("qa_packet_refs", [])
    if not isinstance(refs, list):
        return (False, "qa_packet_refs must be an array")
    for i, ref in enumerate(refs):
        pt = ref.get("packet_type", "")
        if pt not in ALLOWED_QA_PACKET_TYPES:
            return (False, f"qa_packet_refs[{i}].packet_type '{pt}' invalid")
    return (True, f"All {len(refs)} qa_packet_refs valid")


def check_pr_9(data):
    """PR-9: limitations is non-empty."""
    lims = data.get("limitations", [])
    if not isinstance(lims, list) or len(lims) == 0:
        return (False, "limitations must be a non-empty array")
    return (True, f"limitations has {len(lims)} entries")


def check_pr_10(data):
    """PR-10: If status is blocked or partial, escalation_triggers must be non-empty."""
    status = data.get("status", "")
    if status in ("blocked", "partial"):
        triggers = data.get("escalation_triggers", [])
        if not isinstance(triggers, list) or len(triggers) == 0:
            return (False, f"status is '{status}' but escalation_triggers is empty or missing")
        # Validate trigger structure
        for i, t in enumerate(triggers):
            if "trigger" not in t:
                return (False, f"escalation_triggers[{i}] missing 'trigger'")
            if "severity" not in t:
                return (False, f"escalation_triggers[{i}] missing 'severity'")
            sev = t.get("severity", "")
            if sev not in ("low", "medium", "high", "critical"):
                return (False, f"escalation_triggers[{i}].severity '{sev}' invalid")
        return (True, f"Escalation triggers present ({len(triggers)} items)")
    return (True, f"Status '{status}' does not require escalation_triggers")


def check_pr_11(data):
    """PR-11: If results.summary.outcome is fail or blocked, recommendation must not be 'proceed'."""
    results = data.get("results")
    if results is None:
        return (True, "No results block — PR-11 skipped")
    summary = results.get("summary", {})
    outcome = summary.get("outcome", "")
    if outcome in ("fail", "blocked"):
        rec = data.get("recommendation", {})
        rec_val = rec.get("recommendation", "")
        if rec_val == "proceed":
            return (False, f"outcome is '{outcome}' but recommendation is 'proceed'")
    return (True, f"Recommendation consistent with outcome '{outcome}'")


def check_pr_12(data):
    """PR-12: evidence_kind values are from allowed production set (includes production-only kinds)."""
    evidence = data.get("production_evidence", [])
    if not isinstance(evidence, list):
        return (False, "production_evidence must be an array")
    for i, ev in enumerate(evidence):
        ek = ev.get("evidence_kind", "")
        if ek not in ALLOWED_EVIDENCE_KINDS:
            return (False, f"production_evidence[{i}].evidence_kind '{ek}' not in allowed set")
    return (True, f"All {len(evidence)} evidence items have valid evidence_kind")


def validate_fixture(path, allow_invalid=False):
    """Validate a single fixture against all PR rules. Returns (filename, results_dict)."""
    try:
        data = load_json(path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return (os.path.basename(path), {"error": str(e), "all_pass": False})

    checks = [
        ("PR-1", check_pr_1, "Valid schema reference"),
        ("PR-2", check_pr_2, "Authority is advisory"),
        ("PR-3", check_pr_3, "Non-approval statement"),
        ("PR-4", check_pr_4, "Content hash format"),
        ("PR-5", check_pr_5, "Receipt ID format"),
        ("PR-6", check_pr_6, "Packet type"),
        ("PR-7", check_pr_7, "Librarian receipt refs"),
        ("PR-8", check_pr_8, "QA packet refs"),
        ("PR-9", check_pr_9, "Limitations"),
        ("PR-10", check_pr_10, "Escalation triggers for blocked/partial"),
        ("PR-11", check_pr_11, "Recommendation consistency"),
        ("PR-12", check_pr_12, "Evidence kind allowed"),
    ]

    results = []
    all_pass = True
    for rule_id, func, desc in checks:
        passed, message = func(data)
        results.append({"rule": rule_id, "description": desc, "passed": passed, "message": message})
        if not passed:
            all_pass = False

    return (os.path.basename(path), {"all_pass": all_pass, "checks": results})


def main():
    args = sys.argv[1:]
    run_all = "--all" in args
    include_invalid = "--include-invalid" in args
    list_rules = "--list-rules" in args
    fixture_paths = [a for a in args if not a.startswith("--")]

    if list_rules:
        print("QA Pilot Production Receipt Rules (PR-1 through PR-12):")
        print("  PR-1:  Receipt uses valid Draft 2020-12 schema reference")
        print("  PR-2:  authority is const 'advisory'")
        print("  PR-3:  non_approval_statement is present and >= 20 characters")
        print("  PR-4:  content_hash matches sha256:[64 hex chars] pattern")
        print("  PR-5:  receipt_id follows qapr-YYYYMMDD-NNN pattern")
        print("  PR-6:  packet_type is from allowed enum (4 production types)")
        print("  PR-7:  librarian_receipt_refs has valid receipt_type and receipt_id")
        print("  PR-8:  qa_packet_refs has valid packet_type enum")
        print("  PR-9:  limitations is non-empty array")
        print("  PR-10: If status is blocked/partial, escalation_triggers must be non-empty")
        print("  PR-11: If outcome is fail/blocked, recommendation must not be 'proceed'")
        print("  PR-12: evidence_kind values from allowed production set (10 kinds)")
        return 0

    # Determine fixtures directory
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    fixtures_dir = repo_root / "docs" / "examples" / "qa-pilot-receipt"

    if not fixtures_dir.exists():
        print(f"ERROR: Fixtures directory not found: {fixtures_dir}")
        return 1

    if fixture_paths:
        files = [Path(f) for f in fixture_paths]
    elif include_invalid:
        files = sorted(fixtures_dir.glob("*.json"))
    elif run_all:
        # --all mode runs valid fixtures only (like default, but more explicit output)
        files = sorted(fixtures_dir.glob("valid-*.json"))
    else:
        # Default: run only valid fixtures
        files = sorted(fixtures_dir.glob("valid-*.json"))

    if not files:
        print(f"No fixture files found")
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
            # For invalid fixtures, we expect them to fail — a "pass" here means
            # the validator correctly rejected them (all_pass=False is expected).
            # We track whether the validator behaved as expected.
            if not result[1].get("all_pass"):
                invalid_pass += 1

    # Print results
    has_errors = False
    for fname, r in results:
        if "error" in r:
            print(f"  ❌ {fname} — ERROR: {r['error']}")
            has_errors = True
            continue

        prefix = "✅" if r["all_pass"] else "❌"
        check_count = len(r["checks"])
        pass_count = sum(1 for c in r["checks"] if c["passed"])
        print(f"  {prefix} {fname} — {pass_count}/{check_count} checks pass")

        if not r["all_pass"]:
            has_errors = True
            for c in r["checks"]:
                if not c["passed"]:
                    print(f"       FAIL {c['rule']}: {c['message']}")

    print()
    if include_invalid or run_all:
        print(f"Valid fixtures:   {valid_pass}/{valid_total} passed"
              f"{' (all pass)' if valid_pass == valid_total else ''}")
        print(f"Invalid fixtures: {invalid_pass}/{invalid_total} rejected{' (all rejected)' if invalid_pass == invalid_total else ''}")

        # Summary
        valid_ok = valid_pass == valid_total if valid_total > 0 else True
        invalid_ok = invalid_pass == invalid_total if invalid_total > 0 else True

        if valid_ok and invalid_ok and not has_errors:
            print("\n✅ ALL CHECKS PASS")
            return 0
        else:
            print(f"\n❌ SOME CHECKS FAILED"
                  f" ({valid_pass}/{valid_total} valid pass"
                  f", {invalid_pass}/{invalid_total} invalid rejected)")
            return 1
    else:
        if valid_pass == valid_total and valid_total > 0:
            print("✅ ALL CHECKS PASS")
            return 0
        else:
            print("❌ SOME CHECKS FAILED")
            return 1


if __name__ == "__main__":
    sys.exit(main())
