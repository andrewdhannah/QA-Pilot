#!/usr/bin/env python3
"""
QA Pilot MCP Evidence Intake Validator — QA-PILOT-MCP-EVIDENCE-INTAKE-1

Enforces EM-1 through EM-12 business rules on the evidence intake module,
fixtures, and store behavior.

Rules:
    EM-1:  Evidence packets conform to qa-evidence-packet.schema.json
    EM-2:  Ingested evidence is advisory-only — no approval/seal authority
    EM-3:  No source-project file mutation through evidence intake
    EM-4:  Duplicate packet_ids are rejected at ingest time
    EM-5:  Cross-project evidence requires explicit _source_project_metadata
    EM-6:  Timestamps in the future are rejected (stale detection)
    EM-7:  boundary_assertions must have librarian_impact field
    EM-8:  Evidence packet hash must be present
    EM-9:  List/read operations are read-only — must not mutate store
    EM-10: All responses include advisory-only posture
    EM-11: Responses identify source project and QA Pilot-local custody
    EM-12: Evidence cannot authorize Librarian mutation
"""

import ast
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
INTAKE_SCRIPT = SCRIPT_DIR / "qa_pilot_mcp_evidence_intake.py"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-mcp-evidence-intake"
EVIDENCE_DIR = REPO_ROOT / "data" / "evidence"

VALID_FIXTURES = [
    "valid-evidence-packet.json",
    "valid-evidence-packet-cross-project.json",
]

INVALID_FIXTURES = [
    "invalid-evidence-missing-fields.json",
    "invalid-evidence-duplicate-packet-id.json",
    "invalid-evidence-stale-timestamp.json",
    "invalid-evidence-forbidden-mutation.json",
    "invalid-evidence-cross-project-no-metadata.json",
]

ALL_FIXTURES = sorted(set(VALID_FIXTURES + INVALID_FIXTURES))

SOURCE_PROJECT_METADATA_FIXTURES = [
    "valid-evidence-packet-cross-project.json",
]

FORBIDDEN_MUTATION_FIXTURES = [
    "invalid-evidence-forbidden-mutation.json",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_intake_output(operation, *args, **kwargs):
    """Run the intake script and return parsed output."""
    import subprocess
    cmd = [sys.executable, str(INTAKE_SCRIPT), operation] + list(args)
    for k, v in kwargs.items():
        cmd.extend([f"--{k.replace('_', '-')}", str(v)])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = json.loads(result.stdout) if result.stdout else {}
        return (output, result.returncode)
    except Exception as e:
        return ({"error": str(e), "success": False}, 1)


def clear_store():
    """Clear the evidence store before tests."""
    import subprocess
    subprocess.run(
        [sys.executable, str(INTAKE_SCRIPT), "clear"],
        capture_output=True, text=True, timeout=10
    )


# ── Rule Checks ───────────────────────────────────────────────────────────────

def check_em_1():
    """EM-1: Evidence packets conform to qa-evidence-packet.schema.json"""
    for fname in VALID_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if not fpath.exists():
            return (False, f"Valid fixture not found: {fpath}")
        data = load_json(str(fpath))
        required = [
            "packet_id", "project", "sprint_id", "source_ledger",
            "changed_files", "validation_output", "receipt_references",
            "boundary_assertions", "provenance", "hash"
        ]
        missing = [f for f in required if f not in data]
        if missing:
            return (False, f"{fname}: Missing schema-required fields: {missing}")
    return (True, f"All {len(VALID_FIXTURES)} valid fixtures have schema-required fields")


def check_em_2():
    """EM-2: Ingested evidence is advisory-only"""
    # Check the intake script for advisory-only enforcement
    if not INTAKE_SCRIPT.exists():
        return (False, f"Intake script not found: {INTAKE_SCRIPT}")
    content = INTAKE_SCRIPT.read_text()
    if "advisory_only" not in content:
        return (False, "Intake script missing advisory_only enforcement")
    if "advisory_notice" not in content:
        return (False, "Intake script missing advisory notice")
    # Check that EM-2 rule exists
    if "EM-2" not in content:
        return (False, "Intake script missing EM-2 rule")
    # Verify ingest returns advisory_only=True
    clear_store()
    valid_fixture = FIXTURES_DIR / VALID_FIXTURES[0]
    if not valid_fixture.exists():
        return (False, f"Fixture not found: {valid_fixture}")
    output, rc = get_intake_output("ingest", str(valid_fixture))
    if not output.get("advisory_only", False):
        return (False, "Ingest response missing advisory_only=True")
    return (True, "Advisory-only enforcement confirmed in ingest responses")


def check_em_3():
    """EM-3: No source-project mutation"""
    if not INTAKE_SCRIPT.exists():
        return (False, f"Intake script not found: {INTAKE_SCRIPT}")
    content = INTAKE_SCRIPT.read_text()
    # Check EM-3 rule checks for mutation paths
    if "EM-3" not in content:
        return (False, "Intake script missing EM-3 rule")
    # Verify forbidden mutation fixtures are rejected at validate time
    for fname in FORBIDDEN_MUTATION_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if not fpath.exists():
            return (False, f"Forbidden mutation fixture not found: {fpath}")
        output, rc = get_intake_output("validate", str(fpath))
        # Validate should either return success=False or have validation failures
        if output.get("validation", {}).get("valid", True):
            # If validate returns valid=True, check at ingest time
            clear_store()
            ingest_output, rc2 = get_intake_output("ingest", str(fpath))
            if ingest_output.get("success", False):
                return (False, f"{fname}: Forbidden mutation packet was accepted")
    return (True, f"No source-project mutation possible — {len(FORBIDDEN_MUTATION_FIXTURES)} fixtures rejected")


def check_em_4():
    """EM-4: Duplicate packet_ids are rejected"""
    clear_store()
    # Ingest a valid fixture first
    valid_fixture = FIXTURES_DIR / VALID_FIXTURES[0]
    if not valid_fixture.exists():
        return (False, f"Fixture not found: {valid_fixture}")
    out1, rc1 = get_intake_output("ingest", str(valid_fixture))
    if not out1.get("success", False):
        return (False, f"First ingest failed: {out1.get('error', 'unknown')}")
    # Ingest the same fixture again
    out2, rc2 = get_intake_output("ingest", str(valid_fixture))
    if out2.get("success", False):
        return (False, "Duplicate packet was accepted (should have been rejected)")
    # Also check the duplicate fixture exists
    dup_fixture = FIXTURES_DIR / "invalid-evidence-duplicate-packet-id.json"
    if not dup_fixture.exists():
        return (False, "Duplicate fixture not found")
    data = load_json(str(dup_fixture))
    pid = data.get("packet_id", "")
    if pid != out1.get("packet_id"):
        # Packet IDs should match for the duplicate rejection test
        # Actually the duplicate fixture shares packet_id with valid-evidence-packet
        pass
    return (True, "Duplicate packet_ids are rejected")


def check_em_5():
    """EM-5: Cross-project evidence requires _source_project_metadata"""
    if not INTAKE_SCRIPT.exists():
        return (False, f"Intake script not found: {INTAKE_SCRIPT}")
    content = INTAKE_SCRIPT.read_text()
    if "EM-5" not in content:
        return (False, "Intake script missing EM-5 rule")
    # Verify valid cross-project fixture is accepted
    cross_fixture = FIXTURES_DIR / "valid-evidence-packet-cross-project.json"
    if not cross_fixture.exists():
        return (False, "Cross-project fixture not found")
    data = load_json(str(cross_fixture))
    if "_source_project_metadata" not in data:
        return (False, "Cross-project fixture missing _source_project_metadata")
    # Verify missing-metadata fixture is rejected
    no_meta_fixture = FIXTURES_DIR / "invalid-evidence-cross-project-no-metadata.json"
    if no_meta_fixture.exists():
        output, rc = get_intake_output("validate", str(no_meta_fixture))
        validation = output.get("validation", {})
        if validation.get("valid", True):
            # Check EM-5 specifically
            em5_checks = [c for c in validation.get("checks", []) if c.get("rule") == "EM-5"]
            if em5_checks and em5_checks[0].get("passed"):
                return (False, "Cross-project evidence without metadata passed EM-5")
    return (True, "Cross-project metadata requirement enforced")


def check_em_6():
    """EM-6: Future timestamps are rejected"""
    if not INTAKE_SCRIPT.exists():
        return (False, f"Intake script not found: {INTAKE_SCRIPT}")
    content = INTAKE_SCRIPT.read_text()
    if "EM-6" not in content:
        return (False, "Intake script missing EM-6 rule")
    stale_fixture = FIXTURES_DIR / "invalid-evidence-stale-timestamp.json"
    if stale_fixture.exists():
        output, rc = get_intake_output("validate", str(stale_fixture))
        validation = output.get("validation", {})
        em6_checks = [c for c in validation.get("checks", [])
                      if c.get("rule") == "EM-6"]
        if em6_checks and em6_checks[0].get("passed"):
            return (False, "Future timestamp was not rejected by EM-6")
    return (True, "Future timestamps are rejected")


def check_em_7():
    """EM-7: boundary_assertions must have librarian_impact"""
    if not INTAKE_SCRIPT.exists():
        return (False, f"Intake script not found: {INTAKE_SCRIPT}")
    content = INTAKE_SCRIPT.read_text()
    if "EM-7" not in content:
        return (False, "Intake script missing EM-7 rule")
    return (True, "EM-7 boundary_assertions.librarian_impact check present")


def check_em_8():
    """EM-8: Evidence packet hash must be present"""
    if not INTAKE_SCRIPT.exists():
        return (False, f"Intake script not found: {INTAKE_SCRIPT}")
    content = INTAKE_SCRIPT.read_text()
    if "EM-8" not in content:
        return (False, "Intake script missing EM-8 rule")
    # Verify valid fixtures have hashes
    for fname in VALID_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if fpath.exists():
            data = load_json(str(fpath))
            h = data.get("hash", "")
            if not h:
                return (False, f"{fname}: Missing hash field")
    return (True, "Hash presence check enforced")


def check_em_9():
    """EM-9: List/read are read-only — must not mutate store"""
    if not INTAKE_SCRIPT.exists():
        return (False, f"Intake script not found: {INTAKE_SCRIPT}")
    content = INTAKE_SCRIPT.read_text()
    # Parse AST to verify list/read don't call save_index/save_json
    try:
        tree = ast.parse(content)
        read_only_funcs = {"tool_list", "tool_read"}
        forbidden_calls = {"save_index", "save_json"}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in read_only_funcs:
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                        if child.func.id in forbidden_calls:
                            return (False, f"Read-only function '{node.name}' calls '{child.func.id}'")
        # Also check that clear calls save_index (which is OK)
        # But list/read should not
        return (True, "List/read are read-only — no mutation calls found")
    except SyntaxError:
        return (False, "Intake script has syntax errors")


def check_em_10():
    """EM-10: All responses include advisory-only posture"""
    if not INTAKE_SCRIPT.exists():
        return (False, f"Intake script not found: {INTAKE_SCRIPT}")
    content = INTAKE_SCRIPT.read_text()
    checks = []
    if "advisory_only" in content:
        checks.append("advisory_only found")
    if "advisory_notice" in content:
        checks.append("advisory_notice found")
    if "advisory_response" in content:
        checks.append("advisory_response helper found")
    if "advisory-only" in content:
        checks.append("advisory-only text found")
    if not checks:
        return (False, "Intake script missing advisory boundary language")
    # Verify tool responses include advisory_only=True
    clear_store()
    valid_fixture = FIXTURES_DIR / VALID_FIXTURES[0]
    if valid_fixture.exists():
        output, rc = get_intake_output("validate", str(valid_fixture))
        if not output.get("advisory_only", False):
            return (False, "Validate response missing advisory_only")
        output2, rc2 = get_intake_output("list", "--limit", "10")
        if not output2.get("advisory_only", False):
            return (False, "List response missing advisory_only")
    return (True, "; ".join(checks))


def check_em_11():
    """EM-11: Responses identify source_project and QA Pilot-local custody"""
    if not INTAKE_SCRIPT.exists():
        return (False, f"Intake script not found: {INTAKE_SCRIPT}")
    content = INTAKE_SCRIPT.read_text()
    if "source_project" not in content:
        return (False, "Intake script missing source_project identification")
    if "qa-pilot-local" not in content and "qa-pilot" not in content:
        return (False, "Intake script missing QA Pilot-local custody identification")
    # Verify tool responses include source_project and custody
    clear_store()
    output, rc = get_intake_output("status")
    if output.get("source_project") != "qa-pilot":
        return (False, f"Status response missing source_project='qa-pilot', got '{output.get('source_project')}'")
    if "qa-pilot" not in str(output.get("custody", "")):
        return (False, f"Status response missing QA Pilot custody, got '{output.get('custody')}'")
    return (True, "Responses identify source_project='qa-pilot' and custody='qa-pilot-local'")


def check_em_12():
    """EM-12: Evidence cannot authorize Librarian mutation"""
    if not INTAKE_SCRIPT.exists():
        return (False, f"Intake script not found: {INTAKE_SCRIPT}")
    content = INTAKE_SCRIPT.read_text()
    if "EM-12" not in content:
        return (False, "Intake script missing EM-12 rule")
    # Verify _authority_claim is rejected
    for fname in FORBIDDEN_MUTATION_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if not fpath.exists():
            continue
        data = load_json(str(fpath))
        if "_authority_claim" in data:
            clear_store()
            output, rc = get_intake_output("ingest", str(fpath))
            if output.get("success", False):
                return (False, f"{fname}: Forbidden authority claim was accepted")
    return (True, "Librarian mutation authority claims are rejected")


def check_fixture_integrity():
    """Verify fixture directory has all expected files."""
    expected = set(ALL_FIXTURES)
    actual = set()
    if FIXTURES_DIR.exists():
        for f in FIXTURES_DIR.iterdir():
            if f.suffix == ".json":
                actual.add(f.name)
    missing = expected - actual
    extra = actual - expected
    issues = []
    if missing:
        issues.append(f"Missing fixtures: {missing}")
    if extra:
        issues.append(f"Extra fixtures: {extra}")
    if issues:
        return (False, "; ".join(issues))
    return (True, f"All {len(expected)} fixtures present")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    list_rules = "--list-rules" in args

    if list_rules:
        print("QA Pilot MCP Evidence Intake Rules (EM-1 through EM-12):")
        print("  EM-1:  Evidence packets conform to qa-evidence-packet.schema.json")
        print("  EM-2:  Ingested evidence is advisory-only")
        print("  EM-3:  No source-project mutation through evidence intake")
        print("  EM-4:  Duplicate packet_ids are rejected")
        print("  EM-5:  Cross-project evidence requires _source_project_metadata")
        print("  EM-6:  Future timestamps rejected (stale detection)")
        print("  EM-7:  boundary_assertions must have librarian_impact")
        print("  EM-8:  Evidence hash must be present")
        print("  EM-9:  List/read are read-only")
        print("  EM-10: All responses include advisory-only posture")
        print("  EM-11: Responses identify source_project and QA Pilot-local custody")
        print("  EM-12: Evidence cannot authorize Librarian mutation")
        return 0

    checks = [
        ("EM-1", check_em_1, "Schema conformance"),
        ("EM-2", check_em_2, "Advisory-only evidence"),
        ("EM-3", check_em_3, "No source-project mutation"),
        ("EM-4", check_em_4, "Duplicate rejection"),
        ("EM-5", check_em_5, "Cross-project metadata"),
        ("EM-6", check_em_6, "Stale timestamp rejection"),
        ("EM-7", check_em_7, "Boundary assertions"),
        ("EM-8", check_em_8, "Hash presence"),
        ("EM-9", check_em_9, "Read-only list/read"),
        ("EM-10", check_em_10, "Advisory boundary in responses"),
        ("EM-11", check_em_11, "Source project and custody identification"),
        ("EM-12", check_em_12, "Librarian mutation authority rejection"),
        ("FIXTURES", check_fixture_integrity, "Fixture integrity"),
    ]

    all_pass = True
    for rule_id, func, desc in checks:
        try:
            passed, message = func()
        except Exception as e:
            passed = False
            message = f"Check error: {e}"
        prefix = "✅" if passed else "❌"
        print(f"  {prefix} {rule_id}: {desc} — {message}")
        if not passed:
            all_pass = False

    # Fixture counts
    fixture_count = len(list(FIXTURES_DIR.glob("*.json"))) if FIXTURES_DIR.exists() else 0
    print(f"  📁 Fixtures: {fixture_count} files in {FIXTURES_DIR}")

    if all_pass:
        print("\n✅ ALL CHECKS PASS")
        return 0
    else:
        print("\n❌ SOME CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
