#!/usr/bin/env python3
"""
QA Pilot Work Proposal Compiler — QA-PILOT-LIBRARIAN-WORK-QUEUE-INTEGRATION-1

Compiles a diagnostic report (qa-diagnostic-report.schema.json) into a
work proposal (qa-work-proposal.schema.json).

Rules:
    - Deterministic: same input always produces same output
    - No Librarian MCP calls
    - No filesystem mutation outside QA-Pilot
    - Preserves provenance chain (diagnostic_id, test_id, detected_by, validation_run, pipeline_run)
    - Generates proposal_id from diagnostic domain + sequence
    - Maps diagnostic fields to proposal fields per the contract

Usage:
    python3 qa_pilot_work_proposal_compiler.py compile <diagnostic-report.json> [--output <proposal.json>]
    python3 qa_pilot_work_proposal_compiler.py validate <proposal.json>
    python3 qa_pilot_work_proposal_compiler.py status
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "qa-work-proposal.schema.json"
DIAGNOSTIC_SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "qa-diagnostic-report.schema.json"

# Domain to proposal ID prefix mapping
DOMAIN_PREFIX = {
    "regression": "REG",
    "security": "SEC",
    "uat": "UAT",
    "accessibility": "A11Y",
    "performance": "PERF",
    "ai": "AI",
    "compliance": "COMP",
}

# Status mapping (observational only — QA-Pilot does not control Librarian states)
STATUS_MAPPING = [
    {"proposal_status": "OPEN", "librarian_equivalent": "proposal_created"},
    {"proposal_status": "REVIEW_REQUIRED", "librarian_equivalent": "owner_review"},
    {"proposal_status": "APPROVED", "librarian_equivalent": "packet_authorized"},
    {"proposal_status": "EXECUTING", "librarian_equivalent": "agent_active"},
    {"proposal_status": "VERIFIED", "librarian_equivalent": "validation_passed"},
    {"proposal_status": "CLOSED", "librarian_equivalent": "owner_closed"},
]

# Field mapping documentation
DIAGNOSTIC_TO_PROPOSAL_MAPPING = (
    "report_id->source_diagnostic_id, test_id->source_test_id, "
    "failure->failure_summary, severity->severity, domain->affected_domain, "
    "constraints->constraints, provenance.detected_by->provenance.detected_by, "
    "provenance.validation_run->provenance.validation_run, "
    "provenance.pipeline_run->provenance.pipeline_run"
)

PROPOSAL_TO_WORK_PACKET_MAPPING = (
    "suggested_objective->scope, source_diagnostic_id->work_id_provenance, "
    "constraints.must_not_modify->forbidden_paths, "
    "constraints.required_validation->validators_required, "
    "verification_requirements.rerun_tests->evidence_required, "
    "verification_requirements.pass_criteria->acceptance_gates.pass_criteria, "
    "affected_domain->work_type, severity->agent_role_priority"
)

FORBIDDEN_FIELDS = ["owner_approval", "execution_permission", "mutation_authority"]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_diagnostic_report(report):
    """Validate that the input is a proper diagnostic report."""
    errors = []

    if not isinstance(report, dict):
        errors.append("Diagnostic report must be a JSON object")
        return errors

    # Check required fields from qa-diagnostic-report.schema.json
    required_fields = ["report_id", "generated_at", "test_id", "domain", "failure", "provenance"]
    for field in required_fields:
        if field not in report:
            errors.append(f"Missing required field: {field}")

    # Validate report_id pattern
    report_id = report.get("report_id", "")
    if not re.match(r"^DIAG-[A-Z]+-[0-9]{4,}$", report_id):
        errors.append(f"report_id must match DIAG-* pattern, got: {report_id}")

    # Validate domain
    domain = report.get("domain", "")
    valid_domains = list(DOMAIN_PREFIX.keys())
    if domain not in valid_domains:
        errors.append(f"domain must be one of {valid_domains}, got: {domain}")

    # Validate provenance
    provenance = report.get("provenance", {})
    if not provenance.get("advisory", False):
        errors.append("provenance.advisory must be true")
    if not provenance.get("no_authority_conferred", False):
        errors.append("provenance.no_authority_conferred must be true")

    # Validate failure
    failure = report.get("failure", {})
    if not failure.get("expected"):
        errors.append("failure.expected is required")
    if not failure.get("actual"):
        errors.append("failure.actual is required")

    return errors


def generate_proposal_id(diagnostic_report, sequence=1):
    """Generate a deterministic proposal_id from the diagnostic report."""
    domain = diagnostic_report.get("domain", "regression")
    prefix = DOMAIN_PREFIX.get(domain, "REG")
    report_id = diagnostic_report.get("report_id", "")

    # Extract the numeric part from the report_id for the sequence
    match = re.search(r"(\d+)$", report_id)
    if match:
        seq_num = int(match.group(1)) + 10000  # Offset to avoid collision with diagnostic IDs
    else:
        seq_num = 10000 + sequence

    return f"WP-QA-{prefix}-{seq_num:04d}"


def compile_proposal(diagnostic_report, sequence=1):
    """
    Compile a diagnostic report into a work proposal.

    This is the core function — deterministic, no Librarian calls,
    no filesystem mutation outside QA-Pilot.
    """
    # Validate input
    errors = validate_diagnostic_report(diagnostic_report)
    if errors:
        raise ValueError(f"Invalid diagnostic report: {'; '.join(errors)}")

    report_id = diagnostic_report["report_id"]
    test_id = diagnostic_report["test_id"]
    domain = diagnostic_report["domain"]
    severity = diagnostic_report.get("severity", "MEDIUM")
    failure = diagnostic_report["failure"]
    constraints = diagnostic_report.get("constraints", {})
    provenance_in = diagnostic_report.get("provenance", {})

    # Generate proposal_id
    proposal_id = generate_proposal_id(diagnostic_report, sequence)

    # Build failure_summary from diagnostic failure
    failure_summary = {
        "expected": failure["expected"],
        "actual": failure["actual"],
    }
    if "reproduction" in failure:
        failure_summary["reproduction"] = failure["reproduction"]
    if "contract_ref" in failure:
        failure_summary["contract_ref"] = failure["contract_ref"]
    if "evidence_refs" in failure:
        failure_summary["evidence_refs"] = failure["evidence_refs"]

    # Build constraints
    must_not_modify = constraints.get("must_not_modify", ["No constraints specified in diagnostic report"])
    required_validation = constraints.get("required_validation", ["No validation requirements specified in diagnostic report"])

    # Build verification_requirements
    verification_requirements = {
        "rerun_tests": required_validation if required_validation else [f"rerun {test_id}"],
        "pass_criteria": f"All tests in {test_id} must pass with zero failures. "
                         f"Expected: {failure['expected']}. "
                         f"The fix must not introduce new failures.",
        "regression_test_proposed": False,
    }

    # Build suggested_objective
    suggested_objective = (
        f"Repair {domain} failure detected by {test_id}. "
        f"Expected: {failure['expected']}. "
        f"Actual: {failure['actual']}. "
        f"Severity: {severity}."
    )

    # Build compliance_mappings
    compliance_mappings = {
        "diagnostic_to_proposal": DIAGNOSTIC_TO_PROPOSAL_MAPPING,
        "proposal_to_work_packet": PROPOSAL_TO_WORK_PACKET_MAPPING,
        "status_mapping": STATUS_MAPPING,
    }

    # Build limitations (fixed — advisory only)
    limitations = {
        "advisory_only": True,
        "no_execution_authority": True,
        "no_mutation_authority": True,
        "requires_owner_approval": True,
        "requires_librarian_draft": True,
        "notes": "This proposal is advisory-only. It confers no authority. "
                 "The Owner must review and the Librarian must create a work packet draft.",
    }

    # Build provenance
    provenance_out = {
        "advisory": True,
        "no_authority_conferred": True,
        "compiled_by": "qa_pilot_work_proposal_compiler.py",
        "compiled_from": report_id,
        "compiled_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if "detected_by" in provenance_in:
        provenance_out["detected_by"] = provenance_in["detected_by"]
    if "validation_run" in provenance_in:
        provenance_out["validation_run"] = provenance_in["validation_run"]
    if "pipeline_run" in provenance_in:
        provenance_out["pipeline_run"] = provenance_in["pipeline_run"]

    # Assemble proposal
    proposal = {
        "proposal_id": proposal_id,
        "source_diagnostic_id": report_id,
        "source_test_id": test_id,
        "failure_summary": failure_summary,
        "severity": severity,
        "affected_domain": domain,
        "suggested_objective": suggested_objective,
        "constraints": {
            "must_not_modify": must_not_modify,
            "required_validation": required_validation,
        },
        "verification_requirements": verification_requirements,
        "compliance_mappings": compliance_mappings,
        "limitations": limitations,
        "provenance": provenance_out,
    }

    return proposal


def validate_proposal(proposal):
    """Validate a compiled proposal against the contract rules."""
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
    if not source_test_id or len(source_test_id) < 1:
        errors.append("source_test_id must be non-empty")

    # Validate verification_requirements (WQI-004)
    vr = proposal.get("verification_requirements", {})
    if not vr.get("rerun_tests"):
        errors.append("verification_requirements.rerun_tests must be non-empty")
    if not vr.get("pass_criteria") or len(vr.get("pass_criteria", "")) < 10:
        errors.append("verification_requirements.pass_criteria must be at least 10 characters")

    # Validate limitations (WQI-007)
    limitations = proposal.get("limitations", {})
    if not limitations.get("advisory_only", False):
        errors.append("limitations.advisory_only must be true")
    if not limitations.get("no_execution_authority", False):
        errors.append("limitations.no_execution_authority must be true")
    if not limitations.get("no_mutation_authority", False):
        errors.append("limitations.no_mutation_authority must be true")

    # Validate provenance (WQI-002)
    provenance = proposal.get("provenance", {})
    if not provenance.get("advisory", False):
        errors.append("provenance.advisory must be true")
    if not provenance.get("no_authority_conferred", False):
        errors.append("provenance.no_authority_conferred must be true")
    if not provenance.get("compiled_by"):
        errors.append("provenance.compiled_by is required")
    if not provenance.get("compiled_from"):
        errors.append("provenance.compiled_from is required")

    # Validate constraints
    constraints = proposal.get("constraints", {})
    if not constraints.get("must_not_modify"):
        errors.append("constraints.must_not_modify must be non-empty")
    if not constraints.get("required_validation"):
        errors.append("constraints.required_validation must be non-empty")

    return errors


def cmd_compile(args):
    """Compile a diagnostic report into a work proposal."""
    if len(args) < 1:
        print("Usage: compile <diagnostic-report.json> [--output <proposal.json>]", file=sys.stderr)
        return 1

    input_path = args[0]
    output_path = None
    if "--output" in args:
        idx = args.index("--output")
        if idx + 1 < len(args):
            output_path = args[idx + 1]

    try:
        report = load_json(input_path)
    except Exception as e:
        print(f"Error loading diagnostic report: {e}", file=sys.stderr)
        return 1

    try:
        proposal = compile_proposal(report)
    except ValueError as e:
        print(f"Error compiling proposal: {e}", file=sys.stderr)
        return 1

    # Validate the compiled proposal
    errors = validate_proposal(proposal)
    if errors:
        print(f"Compiled proposal failed validation:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    proposal_json = json.dumps(proposal, indent=2)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(proposal_json)
        print(f"Proposal written to {output_path}")
    else:
        print(proposal_json)

    return 0


def cmd_validate(args):
    """Validate a work proposal."""
    if len(args) < 1:
        print("Usage: validate <proposal.json>", file=sys.stderr)
        return 1

    try:
        proposal = load_json(args[0])
    except Exception as e:
        print(f"Error loading proposal: {e}", file=sys.stderr)
        return 1

    errors = validate_proposal(proposal)
    if errors:
        print(f"Proposal validation FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("Proposal validation PASSED")
    return 0


def cmd_status():
    """Print compiler status."""
    print(f"QA Pilot Work Proposal Compiler")
    print(f"  Schema: {SCHEMA_PATH}")
    print(f"  Diagnostic schema: {DIAGNOSTIC_SCHEMA_PATH}")
    print(f"  Forbidden fields: {', '.join(FORBIDDEN_FIELDS)}")
    print(f"  Status mappings: {len(STATUS_MAPPING)}")
    print(f"  Domain prefixes: {len(DOMAIN_PREFIX)}")
    return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: qa_pilot_work_proposal_compiler.py <compile|validate|status> [args]", file=sys.stderr)
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "compile":
        return cmd_compile(args)
    elif command == "validate":
        return cmd_validate(args)
    elif command == "status":
        return cmd_status()
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print("Usage: qa_pilot_work_proposal_compiler.py <compile|validate|status> [args]", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
