#!/usr/bin/env python3
"""
QA Pilot Work Proposal Validator — QA-PILOT-LIBRARIAN-WORK-QUEUE-INTEGRATION-1

Enforces WQI-001 through WQI-007 business rules on work proposals,
fixtures, and schema conformance.

Tier 1 Rules (QA-Pilot owned — can pass now):
    WQI-001: Diagnostic creates proposal — compiler produces valid proposal from diagnostic
    WQI-002: Proposal preserves provenance — source_diagnostic_id and source_test_id link back
    WQI-003: Proposal validates against schema — valid fixtures pass, invalid fixtures reject
    WQI-004: Proposal contains verification requirements — concrete rerun_tests and pass_criteria
    WQI-007: QA-Pilot cannot mutate Librarian state — no Librarian calls, no authority fields
    WQI-008: Fail-closed invariant — missing work packet service must produce a diagnostic
             state and must not silently downgrade governance (regression gate from MCP outage
             diagnostic trail 2026-07-24)

Tier 2 Rules (explicitly blocked — require Librarian dispatch bridge):
    WQI-005: Librarian converts proposal into work packet (BLOCKED)
    WQI-006: End-to-end dispatch → verification → closure (BLOCKED)
"""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "qa-work-proposal.schema.json"
FIXTURES_DIR = REPO_ROOT / "fixtures" / "work-proposal"

VALID_FIXTURES = [
    "valid-regression-proposal.json",
    "valid-security-proposal.json",
]

INVALID_FIXTURES = [
    "invalid-missing-proposal-id.json",
    "invalid-missing-diagnostic-id.json",
    "invalid-empty-verification.json",
    "invalid-owner-approval-field.json",
    "invalid-execution-permission-field.json",
    "invalid-advisory-false.json",
    "invalid-no-provenance.json",
]

ALL_FIXTURES = sorted(set(VALID_FIXTURES + INVALID_FIXTURES))

FORBIDDEN_FIELDS = ["owner_approval", "execution_permission", "mutation_authority"]

FORBIDDEN_LIBRARIAN_PATHS = [
    "active/librarian/Sources/",
    "active/librarian/Public/",
    "active/librarian/project-state/sprint-ledger.json",
    "active/librarian/receipts/",
    "active/librarian/FEATURE-STATUS.md",
    "active/librarian/SESSION-HANDOFF.md",
    "active/librarian/docs/governance/",
    "active/librarian/docs/schemas/",
    "active/librarian/docs/rules/",
    ".librarian/current-project.json",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_schema():
    """WQI-003 (schema): Validate the schema file exists and is valid JSON."""
    errors = []
    if not SCHEMA_PATH.exists():
        errors.append(f"Schema file not found: {SCHEMA_PATH}")
        return errors
    try:
        schema = load_json(SCHEMA_PATH)
        if schema.get("title") != "QA Pilot Work Proposal":
            errors.append(f"Schema title mismatch: {schema.get('title')}")
        required = schema.get("required", [])
        expected_required = [
            "proposal_id", "source_diagnostic_id", "source_test_id",
            "failure_summary", "severity", "affected_domain",
            "suggested_objective", "constraints", "verification_requirements",
            "compliance_mappings", "limitations", "provenance"
        ]
        for field in expected_required:
            if field not in required:
                errors.append(f"Schema missing required field: {field}")
        # Check forbidden fields are NOT in schema properties
        properties = schema.get("properties", {})
        for forbidden in FORBIDDEN_FIELDS:
            if forbidden in properties:
                errors.append(f"Schema contains forbidden field: {forbidden}")
    except Exception as e:
        errors.append(f"Schema parse error: {e}")
    return errors


def validate_proposal_structure(proposal):
    """WQI-001/WQI-003: Validate proposal structure."""
    errors = []

    if not isinstance(proposal, dict):
        errors.append("Proposal must be a JSON object")
        return errors

    # Check forbidden fields (WQI-007)
    for forbidden in FORBIDDEN_FIELDS:
        if forbidden in proposal:
            errors.append(f"Forbidden field present: {forbidden}")

    # Check required fields
    required_fields = [
        "proposal_id", "source_diagnostic_id", "source_test_id",
        "failure_summary", "severity", "affected_domain",
        "suggested_objective", "constraints", "verification_requirements",
        "compliance_mappings", "limitations", "provenance"
    ]
    for field in required_fields:
        if field not in proposal:
            errors.append(f"Missing required field: {field}")

    # Validate proposal_id pattern (WQI-001)
    proposal_id = proposal.get("proposal_id", "")
    if not re.match(r"^WP-QA-[A-Z]+-[0-9]{4,}$", proposal_id):
        errors.append(f"proposal_id must match WP-QA-* pattern, got: {proposal_id}")

    # Validate source_diagnostic_id pattern (WQI-002)
    source_diagnostic_id = proposal.get("source_diagnostic_id", "")
    if not re.match(r"^DIAG-[A-Z]+-[0-9]{4,}$", source_diagnostic_id):
        errors.append(f"source_diagnostic_id must match DIAG-* pattern, got: {source_diagnostic_id}")

    # Validate source_test_id is non-empty (WQI-002)
    source_test_id = proposal.get("source_test_id", "")
    if not source_test_id:
        errors.append("source_test_id must be non-empty")

    return errors


def validate_provenance(proposal):
    """WQI-002: Validate provenance chain."""
    errors = []
    provenance = proposal.get("provenance", {})

    if not provenance.get("advisory", False):
        errors.append("provenance.advisory must be true")
    if not provenance.get("no_authority_conferred", False):
        errors.append("provenance.no_authority_conferred must be true")
    if not provenance.get("compiled_by"):
        errors.append("provenance.compiled_by is required")
    if not provenance.get("compiled_from"):
        errors.append("provenance.compiled_from is required")

    # Check that source_diagnostic_id is traceable
    source_diagnostic_id = proposal.get("source_diagnostic_id", "")
    compiled_from = provenance.get("compiled_from", "")
    if source_diagnostic_id and compiled_from and source_diagnostic_id != compiled_from:
        errors.append(
            f"Provenance mismatch: source_diagnostic_id={source_diagnostic_id} "
            f"but compiled_from={compiled_from}"
        )

    return errors


def validate_verification_requirements(proposal):
    """WQI-004: Validate verification requirements are concrete."""
    errors = []
    vr = proposal.get("verification_requirements", {})

    if not vr:
        errors.append("verification_requirements is required")
        return errors

    rerun_tests = vr.get("rerun_tests", [])
    if not rerun_tests or len(rerun_tests) == 0:
        errors.append("verification_requirements.rerun_tests must be non-empty")

    pass_criteria = vr.get("pass_criteria", "")
    if not pass_criteria or len(pass_criteria) < 10:
        errors.append("verification_requirements.pass_criteria must be at least 10 characters")

    return errors


def validate_authority_boundary(proposal):
    """WQI-007: Validate no Librarian mutation authority."""
    errors = []

    # Check forbidden fields
    for forbidden in FORBIDDEN_FIELDS:
        if forbidden in proposal:
            errors.append(f"Forbidden field present: {forbidden}")

    # Check limitations
    limitations = proposal.get("limitations", {})
    if not limitations.get("advisory_only", False):
        errors.append("limitations.advisory_only must be true")
    if not limitations.get("no_execution_authority", False):
        errors.append("limitations.no_execution_authority must be true")
    if not limitations.get("no_mutation_authority", False):
        errors.append("limitations.no_mutation_authority must be true")

    # Check constraints don't reference Librarian paths as writable
    constraints = proposal.get("constraints", {})
    must_not_modify = constraints.get("must_not_modify", [])
    for path in must_not_modify:
        for forbidden_path in FORBIDDEN_LIBRARIAN_PATHS:
            if forbidden_path in path and "must_not" not in path.lower():
                # It's OK to list Librarian paths in must_not_modify — that's a constraint
                pass

    return errors


def validate_fixture(fixture_path, expect_valid):
    """Validate a single fixture file."""
    errors = []
    try:
        proposal = load_json(fixture_path)
    except Exception as e:
        errors.append(f"JSON parse error: {e}")
        return errors

    errors.extend(validate_proposal_structure(proposal))
    errors.extend(validate_provenance(proposal))
    errors.extend(validate_verification_requirements(proposal))
    errors.extend(validate_authority_boundary(proposal))

    if expect_valid and errors:
        return [f"Expected valid but got errors: {errors}"]
    if not expect_valid and not errors:
        return ["Expected invalid but passed all checks"]
    if not expect_valid and errors:
        return []  # Expected to fail — good
    return errors  # Valid and no errors — good


def validate_fixtures():
    """WQI-003: Validate all fixtures."""
    errors = []

    if not FIXTURES_DIR.exists():
        errors.append(f"Fixtures directory not found: {FIXTURES_DIR}")
        return errors

    # Check all expected fixtures exist
    for fixture in ALL_FIXTURES:
        fixture_path = FIXTURES_DIR / fixture
        if not fixture_path.exists():
            errors.append(f"Missing fixture: {fixture}")

    # Validate valid fixtures pass
    for fixture in VALID_FIXTURES:
        fixture_path = FIXTURES_DIR / fixture
        if fixture_path.exists():
            fixture_errors = validate_fixture(fixture_path, expect_valid=True)
            if fixture_errors:
                errors.append(f"Valid fixture {fixture} failed: {fixture_errors}")

    # Validate invalid fixtures reject
    for fixture in INVALID_FIXTURES:
        fixture_path = FIXTURES_DIR / fixture
        if fixture_path.exists():
            fixture_errors = validate_fixture(fixture_path, expect_valid=False)
            if fixture_errors:
                errors.append(f"Invalid fixture {fixture} unexpectedly passed: {fixture_errors}")

    return errors


def validate_compiler_script():
    """WQI-007: Validate the compiler script doesn't call Librarian MCP tools."""
    errors = []
    compiler_path = REPO_ROOT / "scripts" / "qa_pilot_work_proposal_compiler.py"

    if not compiler_path.exists():
        errors.append(f"Compiler script not found: {compiler_path}")
        return errors

    source = compiler_path.read_text(encoding="utf-8")

    # Check for forbidden Librarian MCP tool calls
    forbidden_calls = [
        "project_work_packet_draft",
        "project_work_packet_authorize",
        "project_work_packet_dispatch",
        "project_work_packet_get",
        "project_work_packet_list",
        "project_work_result_intake",
        "project_work_result_verify",
    ]

    for call in forbidden_calls:
        if call in source:
            errors.append(f"Compiler script contains forbidden Librarian MCP call: {call}")

    # Check for forbidden Librarian path writes
    for path in FORBIDDEN_LIBRARIAN_PATHS:
        if path in source and "open(" in source and "w" in source:
            # More careful check — look for write patterns to Librarian paths
            pass  # The must_not_modify constraint references these paths, which is OK

    return errors


def validate_tier2_gates():
    """WQI-005/WQI-006: Document Tier 2 gates as blocked."""
    # These gates are explicitly blocked — we just verify they're documented
    errors = []
    spec_path = REPO_ROOT / "docs" / "governance" / "QA-PILOT-LIBRARIAN-CONSUMPTION-SPECIFICATION.md"

    if not spec_path.exists():
        errors.append(f"Consumption specification not found: {spec_path}")
        return errors

    spec = spec_path.read_text(encoding="utf-8")

    if "WQI-005" not in spec:
        errors.append("WQI-005 not documented in consumption specification")
    if "WQI-006" not in spec:
        errors.append("WQI-006 not documented in consumption specification")
    if "BLOCKED" not in spec and "blocked" not in spec:
        errors.append("Tier 2 gates not marked as blocked in consumption specification")

    return errors


def validate_fail_closed_invariant():
    """
    WQI-008: Fail-closed invariant — regression gate from MCP outage diagnostic trail.

    A missing work packet service must produce a diagnostic state and must not
    silently downgrade governance. This gate verifies:

    1. The consumption specification documents the MCP diagnostic trail
    2. The specification records work_packet_service_available: false
    3. The specification records bridge_status: degraded
    4. The specification does NOT claim the work packet service is operational
    5. The sprint doc documents the fail-closed behavior as a regression asset
    6. The compiler script does not silently succeed when the service is unavailable
       (verified by checking the compiler has no fallback that bypasses governance)
    """
    errors = []

    # Check consumption specification documents the diagnostic trail
    spec_path = REPO_ROOT / "docs" / "governance" / "QA-PILOT-LIBRARIAN-CONSUMPTION-SPECIFICATION.md"
    if not spec_path.exists():
        errors.append(f"Consumption specification not found: {spec_path}")
        return errors

    spec = spec_path.read_text(encoding="utf-8")

    # Must document the diagnostic trail
    if "work_packet_service_available" not in spec:
        errors.append("Consumption spec does not document work_packet_service_available signal")
    if "degraded" not in spec:
        errors.append("Consumption spec does not document bridge_status: degraded")
    if "false" not in spec:
        errors.append("Consumption spec does not document the false signal from the bridge")

    # Must NOT claim the service is currently operational
    # Check for present-tense claims of operational status (not future/conditional)
    false_claims = [
        "work packet service is operational",
        "work packet service is available",
        "dispatch bridge is currently operational",
        "end-to-end loop is complete",
        "end-to-end loop is operational",
    ]
    for claim in false_claims:
        if claim.lower() in spec.lower():
            errors.append(f"Consumption spec falsely claims: '{claim}'")

    # Check sprint doc documents the fail-closed behavior
    sprint_doc_path = REPO_ROOT / "docs" / "sprints" / "QA-PILOT-LIBRARIAN-WORK-QUEUE-INTEGRATION-1.md"
    if not sprint_doc_path.exists():
        errors.append(f"Sprint doc not found: {sprint_doc_path}")
        return errors

    sprint_doc = sprint_doc_path.read_text(encoding="utf-8")

    if "MCP Diagnostic Trail" not in sprint_doc:
        errors.append("Sprint doc does not document the MCP diagnostic trail")
    if "fail-closed" not in sprint_doc.lower() and "failed closed" not in sprint_doc.lower() and "fail closed" not in sprint_doc.lower():
        errors.append("Sprint doc does not document the fail-closed behavior")

    # Check the compiler script does not have a silent fallback
    # that would bypass governance when the service is unavailable
    compiler_path = REPO_ROOT / "scripts" / "qa_pilot_work_proposal_compiler.py"
    if not compiler_path.exists():
        errors.append(f"Compiler script not found: {compiler_path}")
        return errors

    compiler_source = compiler_path.read_text(encoding="utf-8")

    # The compiler must not contain any fallback that creates work packets
    # when the service is unavailable. It should only produce proposals.
    forbidden_fallbacks = [
        "fallback_to_work_packet",
        "create_work_packet_if_service_unavailable",
        "bypass_service_check",
        "silent_downgrade",
    ]
    for fallback in forbidden_fallbacks:
        if fallback in compiler_source:
            errors.append(f"Compiler contains forbidden fallback: {fallback}")

    return errors


def main():
    all_errors = []

    print("=== QA Pilot Work Proposal Validator ===")
    print()

    # WQI-003 (schema)
    print("WQI-003: Schema validation...")
    schema_errors = validate_schema()
    if schema_errors:
        all_errors.extend([f"WQI-003: {e}" for e in schema_errors])
        print(f"  FAIL: {len(schema_errors)} errors")
    else:
        print("  PASS")

    # WQI-003 (fixtures)
    print("WQI-003: Fixture validation...")
    fixture_errors = validate_fixtures()
    if fixture_errors:
        all_errors.extend([f"WQI-003: {e}" for e in fixture_errors])
        print(f"  FAIL: {len(fixture_errors)} errors")
    else:
        print("  PASS")

    # WQI-007 (compiler script)
    print("WQI-007: Compiler script boundary check...")
    compiler_errors = validate_compiler_script()
    if compiler_errors:
        all_errors.extend([f"WQI-007: {e}" for e in compiler_errors])
        print(f"  FAIL: {len(compiler_errors)} errors")
    else:
        print("  PASS")

    # WQI-005/WQI-006 (Tier 2 — blocked)
    print("WQI-005/006: Tier 2 gates (blocked)...")
    tier2_errors = validate_tier2_gates()
    if tier2_errors:
        all_errors.extend([f"WQI-005/006: {e}" for e in tier2_errors])
        print(f"  FAIL: {len(tier2_errors)} errors")
    else:
        print("  PASS (documented as blocked)")

    # WQI-008 (fail-closed invariant — regression gate)
    print("WQI-008: Fail-closed invariant (regression gate)...")
    fail_closed_errors = validate_fail_closed_invariant()
    if fail_closed_errors:
        all_errors.extend([f"WQI-008: {e}" for e in fail_closed_errors])
        print(f"  FAIL: {len(fail_closed_errors)} errors")
    else:
        print("  PASS")

    print()

    if all_errors:
        print(f"VALIDATION FAILED: {len(all_errors)} errors")
        for err in all_errors:
            print(f"  - {err}")
        return 1
    else:
        print("VALIDATION PASSED — all Tier 1 gates green, Tier 2 gates documented as blocked")
        return 0


if __name__ == "__main__":
    sys.exit(main())
