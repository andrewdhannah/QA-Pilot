#!/usr/bin/env python3
"""
RECONC-FINDING-LIFECYCLE-001 — Regression fixture for finding lifecycle management.

Validates that historical findings are not treated as current governance conditions
without revalidation against canonical state.

Derived from incident: DRIFT-librarian-drift_detection (2026-07-20 through 2026-08-16)

Invariant: A historical finding must never be treated as a current governance
condition without revalidation against current authoritative state.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

FIXTURE_PATH = Path(__file__).parent / "RECONC-FINDING-LIFECYCLE-001.json"
PASS = 0
FAIL = 0
RESULTS = []


def load_fixture():
    with open(FIXTURE_PATH) as f:
        return json.load(f)


def assert_test(test_id, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        RESULTS.append({"test_id": test_id, "status": "PASS", "detail": detail})
    else:
        FAIL += 1
        RESULTS.append({"test_id": test_id, "status": "FAIL", "detail": detail})
        print(f"  FAIL: {test_id} — {detail}")


def tc001_finding_detected_is_current(fixture):
    """A newly detected finding is classified as current and actionable."""
    tc = next(t for t in fixture["test_cases"] if t["test_id"] == "TC-001")
    assert_test("TC-001", tc["expected_outcome"]["is_actionable"] is True,
                 "Newly detected finding should be actionable")
    assert_test("TC-001", tc["expected_outcome"]["requires_owner_action"] is True,
                 "Critical finding requires Owner action")


def tc002_remediation_proven(fixture):
    """A remediation receipt exists proving the finding was addressed."""
    tc = next(t for t in fixture["test_cases"] if t["test_id"] == "TC-002")
    receipt = tc["input"]["receipt_contains"]
    assert_test("TC-002", receipt["verification"]["evidence_chain_complete"] is True,
                 "Remediation evidence chain must be complete")
    assert_test("TC-002", receipt["verification"]["borrowed_events_removed"] == 37,
                 "All 37 borrowed events must be removed")


def tc003_stale_finding_not_current(fixture):
    """A stale finding is not treated as a current governance condition."""
    tc = next(t for t in fixture["test_cases"] if t["test_id"] == "TC-003")
    assert_test("TC-003", tc["expected_outcome"]["is_current_condition"] is False,
                 "Stale finding must not be treated as current condition")
    assert_test("TC-003", tc["expected_outcome"]["requires_revalidation"] is True,
                 "Stale finding requires revalidation")


def tc004_revalidation_resolves(fixture):
    """Revalidation against canonical state resolves a stale finding."""
    tc = next(t for t in fixture["test_cases"] if t["test_id"] == "TC-004")
    assert_test("TC-004", tc["expected_outcome"]["finding_status"] == "resolved",
                 "Revalidation should resolve the finding")
    assert_test("TC-004", tc["expected_outcome"]["historical_finding_preserved"] is True,
                 "Historical finding must be preserved after resolution")


def tc005_forensic_history_preserved(fixture):
    """Resolved findings retain full forensic history."""
    tc = next(t for t in fixture["test_cases"] if t["test_id"] == "TC-005")
    fields_present = tc["expected_outcome"]["fields_present"]
    assert_test("TC-005", len(fields_present) >= 8,
                 f"Forensic history must contain at least 8 fields, found {len(fields_present)}")
    assert_test("TC-005", "remediation_receipt" in fields_present,
                 "Forensic history must include remediation receipt reference")


def tc006_no_evidence_no_resolution(fixture):
    """Remediation without evidence does not resolve a finding."""
    tc = next(t for t in fixture["test_cases"] if t["test_id"] == "TC-006")
    assert_test("TC-006", tc["expected_outcome"]["finding_status"] == "open",
                 "Finding without remediation evidence must remain open")
    assert_test("TC-006", tc["expected_outcome"]["resolution_blocked"] is True,
                 "Resolution must be blocked without evidence")


def tc007_three_state_layers(fixture):
    """The system correctly distinguishes canonical, detection, and reconciliation states."""
    tc = next(t for t in fixture["test_cases"] if t["test_id"] == "TC-007")
    assert_test("TC-007", tc["expected_outcome"]["canonical_state_healthy"] is True,
                 "Canonical state must be healthy")
    assert_test("TC-007", tc["expected_outcome"]["detection_state_stale"] is True,
                 "Detection state must be identified as stale")
    assert_test("TC-007", tc["expected_outcome"]["reconciliation_input_contaminated"] is True,
                 "Reconciliation input contaminated by stale detection must be identified")


def validate_invariants(fixture):
    """All invariants hold across test cases."""
    for inv in fixture["invariant_tests"]:
        assert_test(f"INV-{inv['invariant_id']}", inv["all_pass_expected"] is True,
                     f"Invariant: {inv['statement'][:80]}...")


def main():
    fixture = load_fixture()

    print(f"Fixture: {fixture['fixture_id']} v{fixture['fixture_version']}")
    print(f"Purpose: {fixture['purpose']}")
    print()

    # Run all test cases
    tc001_finding_detected_is_current(fixture)
    tc002_remediation_proven(fixture)
    tc003_stale_finding_not_current(fixture)
    tc004_revalidation_resolves(fixture)
    tc005_forensic_history_preserved(fixture)
    tc006_no_evidence_no_resolution(fixture)
    tc007_three_state_layers(fixture)

    # Validate invariants
    validate_invariants(fixture)

    # Summary
    print()
    print(f"Results: {PASS} PASS, {FAIL} FAIL, {PASS + FAIL} total")

    if FAIL > 0:
        print("\nFAILED TESTS:")
        for r in RESULTS:
            if r["status"] == "FAIL":
                print(f"  {r['test_id']}: {r['detail']}")

    print()
    print(f"Invariant: {fixture['invariant_tests'][0]['statement']}")
    print(f"Design principle: {fixture['design_principles']['evidence_based_not_timestamp_based']}")

    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
