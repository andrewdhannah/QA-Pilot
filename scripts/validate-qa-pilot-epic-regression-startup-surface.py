#!/usr/bin/env python3
"""
QA Pilot Epic Regression Startup Surface Validator
— QA-PILOT-EPIC-REGRESSION-STARTUP-SURFACE-1

Enforces SS-1 through SS-9 rules on pipeline startup surface.
"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SURFACE_SCRIPT = SCRIPT_DIR / "qa_pilot_pipeline_startup_surface.py"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-epic-regression-startup-surface"

VALID_FIXTURES = ["valid-pipeline-report.json"]
INVALID_FIXTURES = ["invalid-stale-claims.json", "invalid-authority-claim.json"]
ALL_FIXTURES = sorted(set(VALID_FIXTURES + INVALID_FIXTURES))


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_surface_output(*args):
    import subprocess
    cmd = [sys.executable, str(SURFACE_SCRIPT)] + list(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return (r.stdout, r.stderr, r.returncode)
    except Exception as e:
        return ("", str(e), 1)


def validate_report_data(data):
    checks = []

    sh = data.get("sealed_head", "")
    checks.append(("SS-1", bool(sh) and "#" in sh, f"Sealed head: {sh}" if sh else "Missing"))

    checks.append(("SS-5", data.get("advisory") is True, f"advisory = {data.get('advisory')}"))
    checks.append(("SS-6", data.get("librarian_mutation_authority") is False,
                   f"librarian_mutation = {data.get('librarian_mutation_authority')}"))

    layers = data.get("pipeline_layers", [])
    layer_names = [l.get("layer") for l in layers]
    expected = ["evidence", "tests", "results", "epic"]
    missing = [e for e in expected if e not in layer_names]
    checks.append(("SS-4", len(missing) == 0,
                   f"Layers: {layer_names}" if not missing else f"Missing: {missing}"))

    # Check for authority claim
    if "_authority_claim" in data:
        checks.append(("SS-AUTH", False, f"Contains _authority_claim"))
    else:
        checks.append(("SS-AUTH", True, "No authority claim"))

    # Stale check
    if data.get("custody") != "qa-pilot-local":
        checks.append(("SS-CUSTODY", False, f"custody = {data.get('custody')}"))
    else:
        checks.append(("SS-CUSTODY", True, "custody = qa-pilot-local"))

    all_pass = all(c[1] for c in checks)
    return (all_pass, checks)


# ── Rule Checks ───────────────────────────────────────────────────────────────

def check_ss_1():
    out, _, rc = get_surface_output("report", "--format", "json")
    try:
        data = json.loads(out)
        pipeline = data.get("pipeline", data)
        sh = pipeline.get("sealed_head", "")
        return (bool(sh) and "#" in sh, f"Sealed head: {sh}" if sh else "Missing")
    except Exception as e:
        return (False, f"Failed to parse report: {e}")


def check_ss_2():
    out, _, rc = get_surface_output("report", "--format", "json")
    try:
        data = json.loads(out)
        return (True, "Report generated successfully with JSON output")
    except Exception as e:
        return (False, f"JSON report failed: {e}")


def check_ss_3():
    out, _, rc = get_surface_output("status")
    has_pipeline = "advisory-only" in out
    has_sealed = "sealed" in out.lower()
    return (has_pipeline and has_sealed, "Status output includes pipeline and sealed info")


def check_ss_4():
    out, _, rc = get_surface_output("report", "--format", "json")
    try:
        data = json.loads(out)
        pipeline = data.get("pipeline", data)
        layers = pipeline.get("pipeline_layers", [])
        layer_names = [l.get("layer") for l in layers]
        expected = ["evidence", "tests", "results", "epic"]
        missing = [e for e in expected if e not in layer_names]
        return (len(missing) == 0, f"Layers: {layer_names}" if not missing else f"Missing: {missing}")
    except Exception as e:
        return (False, f"Failed: {e}")


def check_ss_5():
    out, _, rc = get_surface_output("report", "--format", "json")
    try:
        data = json.loads(out)
        pipeline = data.get("pipeline", data)
        advisory = pipeline.get("advisory")
        # Also check all layers are advisory
        layers = pipeline.get("pipeline_layers", [])
        all_advisory = all(l.get("advisory") for l in layers)
        return (advisory is True and all_advisory,
                f"Pipeline advisory={advisory}, all layers advisory={all_advisory}")
    except Exception as e:
        return (False, f"Failed: {e}")


def check_ss_6():
    out, _, rc = get_surface_output("report", "--format", "json")
    try:
        data = json.loads(out)
        pipeline = data.get("pipeline", data)
        lma = pipeline.get("librarian_mutation_authority")
        return (lma is False, f"librarian_mutation_authority = {lma}")
    except Exception as e:
        return (False, f"Failed: {e}")


def check_ss_7():
    # Validate invalid-stale fixture
    fpath = FIXTURES_DIR / "invalid-stale-claims.json"
    if not fpath.exists():
        return (False, "Fixture not found")
    data = load_json(str(fpath))
    valid, checks = validate_report_data(data)
    # Should be invalid — stale head #99 (> #36), wrong custody, non-advisory, negative counts
    if valid:
        return (False, "Stale claims fixture validated as pass (should fail)")
    # Check specific stale indicators
    sh = data.get("sealed_head", "")
    has_stale_number = "#99" in sh
    wrong_custody = data.get("custody") != "qa-pilot-local"
    non_advisory = data.get("advisory") is not True
    has_mutation = data.get("librarian_mutation_authority") is not False
    stale_detected = has_stale_number or wrong_custody or non_advisory or has_mutation
    return (stale_detected,
            f"Stale indicators: #99={has_stale_number}, custody={wrong_custody}, "
            f"advisory={non_advisory}, mutation={has_mutation}")


def check_ss_8():
    # Validate authority claim fixture
    fpath = FIXTURES_DIR / "invalid-authority-claim.json"
    if not fpath.exists():
        return (False, "Fixture not found")
    data = load_json(str(fpath))
    valid, checks = validate_report_data(data)
    if valid:
        return (False, "Authority claim fixture passed (should fail)")
    auth_result = any(c for c in checks if c[0] == "SS-AUTH" and not c[1])
    return (auth_result, "Authority claim detected" if auth_result else "SS-AUTH should have failed")


def check_ss_9():
    # Validate valid fixture passes
    fpath = FIXTURES_DIR / "valid-pipeline-report.json"
    if not fpath.exists():
        return (False, "Fixture not found")
    data = load_json(str(fpath))
    valid, _ = validate_report_data(data)
    return (valid, "Valid fixture passes acceptance checks")


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
        issues.append(f"Missing: {missing}")
    if extra:
        issues.append(f"Extra: {extra}")
    if issues:
        return (False, "; ".join(issues))
    return (True, f"All {len(expected)} fixtures present")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    checks = [
        ("SS-1", check_ss_1, "Sealed head reported"),
        ("SS-2", check_ss_2, "JSON report generated"),
        ("SS-3", check_ss_3, "Status command works"),
        ("SS-4", check_ss_4, "All 4 layers exposed"),
        ("SS-5", check_ss_5, "All layers advisory-only"),
        ("SS-6", check_ss_6, "Zero Librarian mutation"),
        ("SS-7", check_ss_7, "Stale claims rejected"),
        ("SS-8", check_ss_8, "Authority claims rejected"),
        ("SS-9", check_ss_9, "Valid fixture passes"),
        ("FIXTURES", check_fixture_integrity, "Fixture integrity"),
    ]

    all_pass = True
    for rule_id, func, desc in checks:
        try:
            passed, message = func()
        except Exception as e:
            passed = False
            message = f"Error: {e}"
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
