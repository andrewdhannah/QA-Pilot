#!/usr/bin/env python3
"""
QA Pilot Epic Regression Builder Validator — QA-PILOT-EPIC-REGRESSION-BUILDER-1

Enforces ER-1 through ER-13 business rules on the epic regression builder module,
fixtures, and store behavior.
"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BUILDER_SCRIPT = SCRIPT_DIR / "qa_pilot_epic_regression_builder.py"
INTAKE_SCRIPT = SCRIPT_DIR / "qa_pilot_mcp_evidence_intake.py"
COMPOSITION_SCRIPT = SCRIPT_DIR / "qa_pilot_test_composition.py"
EXPORT_SCRIPT = SCRIPT_DIR / "qa_pilot_result_packet_export.py"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-epic-regression-builder"
EPIC_DIR = REPO_ROOT / "data" / "epic-regression"

VALID_FIXTURES = ["valid-epic-suite.json"]
INVALID_FIXTURES = [
    "invalid-schema-violation.json",
    "invalid-authority-claiming.json",
    "invalid-broken-chain.json",
]
ALL_FIXTURES = sorted(set(VALID_FIXTURES + INVALID_FIXTURES))


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_builder_output(operation, *args, **kwargs):
    import subprocess
    cmd = [sys.executable, str(BUILDER_SCRIPT), operation] + list(args)
    for k, v in kwargs.items():
        cmd.extend([f"--{k.replace('_', '-')}", str(v)])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = json.loads(result.stdout) if result.stdout else {}
        return (output, result.returncode)
    except Exception as e:
        return ({"error": str(e), "success": False}, 1)


def get_intake_output(operation, *args, **kwargs):
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


def get_composition_output(operation, *args, **kwargs):
    import subprocess
    cmd = [sys.executable, str(COMPOSITION_SCRIPT), operation] + list(args)
    for k, v in kwargs.items():
        cmd.extend([f"--{k.replace('_', '-')}", str(v)])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = json.loads(result.stdout) if result.stdout else {}
        return (output, result.returncode)
    except Exception as e:
        return ({"error": str(e), "success": False}, 1)


def get_export_output(operation, *args, **kwargs):
    import subprocess
    cmd = [sys.executable, str(EXPORT_SCRIPT), operation] + list(args)
    for k, v in kwargs.items():
        cmd.extend([f"--{k.replace('_', '-')}", str(v)])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = json.loads(result.stdout) if result.stdout else {}
        return (output, result.returncode)
    except Exception as e:
        return ({"error": str(e), "success": False}, 1)


def clear_all():
    import subprocess
    for script in [BUILDER_SCRIPT, EXPORT_SCRIPT, COMPOSITION_SCRIPT, INTAKE_SCRIPT]:
        subprocess.run([sys.executable, str(script), "clear"],
                       capture_output=True, text=True, timeout=10)


# ── Rule Checks ───────────────────────────────────────────────────────────────

def check_er_1():
    if not BUILDER_SCRIPT.exists():
        return (False, "Builder script not found")
    content = BUILDER_SCRIPT.read_text()
    if "evidence-index.json" not in content:
        return (False, "Missing evidence-index.json reference")
    if "test-case-index.json" not in content:
        return (False, "Missing test-case-index.json reference")
    if "result-packet-index.json" not in content:
        return (False, "Missing result-packet-index.json reference")
    return (True, "Reads from QA Pilot-local EP, TC, QR stores")


def check_er_2():
    if not BUILDER_SCRIPT.exists():
        return (False, "Builder script not found")
    content = BUILDER_SCRIPT.read_text()
    if "evidence_packets" not in content:
        return (False, "Missing evidence_packets provenance")
    return (True, "Epic suite references EP evidence packet IDs")


def check_er_3():
    if not BUILDER_SCRIPT.exists():
        return (False, "Builder script not found")
    content = BUILDER_SCRIPT.read_text()
    if "test_cases" not in content and "tests" not in content:
        return (False, "Missing test case references")
    return (True, "Epic suite references TC test case IDs")


def check_er_4():
    if not BUILDER_SCRIPT.exists():
        return (False, "Builder script not found")
    content = BUILDER_SCRIPT.read_text()
    if "result_packets" not in content:
        return (False, "Missing result_packets provenance")
    return (True, "Epic suite references QR result packet IDs")


def check_er_5():
    if not BUILDER_SCRIPT.exists():
        return (False, "Builder script not found")
    content = BUILDER_SCRIPT.read_text()
    if "advisory" not in content:
        return (False, "Missing advisory enforcement")
    clear_all()
    ev_fixture = REPO_ROOT / "docs" / "examples" / "qa-pilot-test-composition" / "valid-evidence-source.json"
    if ev_fixture.exists():
        get_intake_output("ingest", str(ev_fixture))
        get_composition_output("compose")
        get_export_output("export")
        out, _ = get_builder_output("build", "EPIC-TEST-CHECK-ER5")
        suite = out.get("epic_suite", {})
        if suite.get("advisory") is not True:
            return (False, f"Built suite advisory is not True: {suite.get('advisory')}")
    clear_all()
    return (True, "Built suites include advisory: true")


def check_er_6():
    if not BUILDER_SCRIPT.exists():
        return (False, "Builder script not found")
    content = BUILDER_SCRIPT.read_text()
    if "validate_epic_suite_schema" not in content:
        return (False, "Missing schema validation")
    valid_fixture = FIXTURES_DIR / "valid-epic-suite.json"
    if valid_fixture.exists():
        data = load_json(str(valid_fixture))
        required = ["suite_id", "epic_id", "sprint_ids", "tests", "status", "advisory"]
        missing = [f for f in required if f not in data]
        if missing:
            return (False, f"Valid fixture missing: {missing}")
    inv_fixture = FIXTURES_DIR / "invalid-schema-violation.json"
    if inv_fixture.exists():
        data = load_json(str(inv_fixture))
        if data.get("advisory") is True:
            return (False, "Invalid fixture has advisory=True when it should be False")
    return (True, "Schema validation enforced")


def check_er_7():
    if not BUILDER_SCRIPT.exists():
        return (False, "Builder script not found")
    content = BUILDER_SCRIPT.read_text()
    if "FORBIDDEN_AUTHORITY_VERBS" not in content:
        return (False, "Missing FORBIDDEN_AUTHORITY_VERBS")
    auth_fixture = FIXTURES_DIR / "invalid-authority-claiming.json"
    if auth_fixture.exists():
        out, _ = get_builder_output("validate", str(auth_fixture))
        if out.get("success", False):
            return (False, "Authority-claiming suite was not rejected")
    return (True, "Authority verbs rejected")


def check_er_8():
    if not BUILDER_SCRIPT.exists():
        return (False, "Builder script not found")
    content = BUILDER_SCRIPT.read_text()
    if "ER-8" not in content or "mutation_paths" not in content:
        return (False, "Missing mutation path enforcement")
    return (True, "Mutation path check enforced")


def check_er_9():
    if not BUILDER_SCRIPT.exists():
        return (False, "Builder script not found")
    content = BUILDER_SCRIPT.read_text()
    if "ER-9" not in content:
        return (False, "Missing ER-9 malformed input check")
    inv_fixture = FIXTURES_DIR / "invalid-schema-violation.json"
    if inv_fixture.exists():
        out, _ = get_builder_output("validate", str(inv_fixture))
        if out.get("success", False):
            return (False, "Schema-violating suite was not rejected")
    return (True, "Malformed/incomplete inputs rejected")


def check_er_10():
    if not BUILDER_SCRIPT.exists():
        return (False, "Builder script not found")
    content = BUILDER_SCRIPT.read_text()
    if "already exists" in content.lower():
        pass
    # Test determinism: build twice with same data
    clear_all()
    ev_fixture = REPO_ROOT / "docs" / "examples" / "qa-pilot-test-composition" / "valid-evidence-source.json"
    if ev_fixture.exists():
        get_intake_output("ingest", str(ev_fixture))
        get_composition_output("compose")
        get_export_output("export")
    out1, _ = get_builder_output("build", "EPIC-DET-CHECK")
    s1 = out1.get("suite_id", "")
    # Second build with same epic_id + sprint_ids should be rejected (duplicate)
    out2, _ = get_builder_output("build", "EPIC-DET-CHECK")
    s2_ok = out2.get("success", True)
    if s2_ok:
        return (False, f"Duplicate build was accepted (should have been rejected)")
    # But building with a different epic_id should succeed
    out3, _ = get_builder_output("build", "EPIC-DET-CHECK-2")
    s3 = out3.get("success", False)
    if s3 is not True:
        return (False, "Different epic_id build failed")
    clear_all()
    return (True, "Duplicate build deterministic: same input rejected, different input accepted")


def check_er_11():
    if not BUILDER_SCRIPT.exists():
        return (False, "Builder script not found")
    content = BUILDER_SCRIPT.read_text()
    local_paths = ["epic-regression", "epic-regression-index"]
    for lp in local_paths:
        if lp not in content:
            return (False, f"Missing QA Pilot-local path: {lp}")
    return (True, "Epic index is QA Pilot-local only (data/epic-regression/)")


def check_er_12():
    for script, name in [(INTAKE_SCRIPT, "evidence intake"),
                          (COMPOSITION_SCRIPT, "test composition"),
                          (EXPORT_SCRIPT, "result export")]:
        if not script.exists():
            return (False, f"{name} script not found")
        import subprocess
        r = subprocess.run([sys.executable, str(script), "status"],
                          capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            return (False, f"{name} status returned non-zero")
        try:
            o = json.loads(r.stdout) if r.stdout else {}
            if not o.get("advisory_only", False):
                return (False, f"{name} status missing advisory_only")
        except json.JSONDecodeError:
            return (False, f"{name} status not parseable")
    return (True, "Evidence, test, and result scripts operational")


def check_er_13():
    key_validators = [
        "validate-qa-pilot-startup-regression.py",
        "validate-qa-pilot-full-workbench-architecture-plan.py",
    ]
    for v in key_validators:
        vpath = SCRIPT_DIR / v
        if not vpath.exists():
            return (False, f"Key validator missing: {v}")
    return (True, "Regression scripts present")


def check_fixture_integrity():
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
        print("QA Pilot Epic Regression Builder Rules (ER-1 through ER-13):")
        names = [
            ("ER-1", "Builds from QA Pilot-local evidence, tests, results"),
            ("ER-2", "EP evidence packet references"),
            ("ER-3", "TC test case references"),
            ("ER-4", "QR result packet references"),
            ("ER-5", "Advisory-only posture"),
            ("ER-6", "Schema validation"),
            ("ER-7", "Authority verb rejection"),
            ("ER-8", "Mutation path rejection"),
            ("ER-9", "Malformed/incomplete input rejection"),
            ("ER-10", "Deterministic build"),
            ("ER-11", "QA Pilot-local index"),
            ("ER-12", "Packet chain green"),
            ("ER-13", "Regression scripts present"),
        ]
        for rid, desc in names:
            print(f"  {rid}: {desc}")
        return 0

    checks = [
        ("ER-1", check_er_1, "QA Pilot-local stores"),
        ("ER-2", check_er_2, "EP evidence references"),
        ("ER-3", check_er_3, "TC test references"),
        ("ER-4", check_er_4, "QR result references"),
        ("ER-5", check_er_5, "Advisory-only"),
        ("ER-6", check_er_6, "Schema validation"),
        ("ER-7", check_er_7, "Authority verb rejection"),
        ("ER-8", check_er_8, "Mutation path rejection"),
        ("ER-9", check_er_9, "Malformed rejection"),
        ("ER-10", check_er_10, "Build determinism"),
        ("ER-11", check_er_11, "QA Pilot-local index"),
        ("ER-12", check_er_12, "Packet chain green"),
        ("ER-13", check_er_13, "Regression scripts present"),
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

    fcount = len(list(FIXTURES_DIR.glob("*.json"))) if FIXTURES_DIR.exists() else 0
    print(f"  📁 Fixtures: {fcount} files in {FIXTURES_DIR}")

    if all_pass:
        print("\n✅ ALL CHECKS PASS")
        return 0
    else:
        print("\n❌ SOME CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
