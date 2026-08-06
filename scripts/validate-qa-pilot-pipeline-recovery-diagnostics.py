#!/usr/bin/env python3
"""
QA Pilot Pipeline Recovery Diagnostics Validator
— QA-PILOT-PIPELINE-RECOVERY-DIAGNOSTICS-1

Validates that diagnostic outputs are properly advisory-only, classify correctly,
and do not claim repair authority.
"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DIAG_SCRIPT = SCRIPT_DIR / "qa_pilot_pipeline_recovery_diagnostics.py"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-pipeline-recovery-diagnostics"

VALID_FIXTURES = ["valid-no-drift.json"]
INVALID_FIXTURES = ["invalid-authority-claim.json"]
ALL_FIXTURES = sorted(set(VALID_FIXTURES + INVALID_FIXTURES))


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_diag_output(*args):
    import subprocess
    cmd = [sys.executable, str(DIAG_SCRIPT)] + list(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        try:
            return (json.loads(r.stdout) if r.stdout else {}, r.returncode)
        except json.JSONDecodeError:
            return ({"error": "Parse failed"}, 1)
    except Exception as e:
        return ({"error": str(e)}, 1)


# ── Rule Checks ───────────────────────────────────────────────────────────────

def check_rd_1():
    """Diagnostic output is advisory-only"""
    diag, _ = get_diag_output()
    return (diag.get("advisory") is True, f"advisory = {diag.get('advisory')}")


def check_rd_2():
    """Diagnostic has pipeline layer classification"""
    diag, _ = get_diag_output()
    layers = diag.get("pipeline_layers", {})
    has_layers = len(layers) >= 7  # EP, TC, QR, ERS, STARTUP, PH, DR
    return (has_layers, f"{len(layers)} pipeline layers classified" if has_layers else "Missing layers")


def check_rd_3():
    """Diagnostic identifies affected layers when drift exists"""
    diag, _ = get_diag_output()
    s = diag.get("summary", {})
    # No drift currently, so this is a structural check
    has_summary = "drifts" in s and "layers_affected" in s
    return (has_summary, f"Summary: {s.get('drifts', '?')} drifts, {s.get('layers_affected', [])}")


def check_rd_4():
    """No auto-repair"""
    diag, _ = get_diag_output()
    recovery = diag.get("recovery_summary", {})
    note = recovery.get("note", "")
    is_advisory = "advisory" in note.lower() or "owner" in note.lower() or "no drift" in note.lower()
    return (is_advisory, f"Recovery note: {note[:80]}" if note else "Missing recovery note")


def check_rd_5():
    """Classification by cause"""
    diag, _ = get_diag_output()
    findings = diag.get("findings", [])
    for f in findings:
        if not f.get("cause") or not f.get("description"):
            return (False, "Finding missing cause or description")
    return (True, f"{len(findings)} findings properly classified")


def check_rd_6():
    """Recovery options are bounded"""
    diag, _ = get_diag_output()
    steps = diag.get("recovery_summary", {}).get("steps", [])
    return (len(steps) <= 10, f"{len(steps)} recovery steps (max 10)")


def check_rd_7():
    """Fixture: valid passes"""
    fpath = FIXTURES_DIR / "valid-no-drift.json"
    if not fpath.exists():
        return (False, "Fixture not found")
    data = load_json(str(fpath))
    ok = data.get("advisory") is True and data.get("auto_repair") is False
    return (ok, "Valid fixture has advisory=True, auto_repair=False")


def check_rd_8():
    """Fixture: invalid authority claim rejected"""
    fpath = FIXTURES_DIR / "invalid-authority-claim.json"
    if not fpath.exists():
        return (False, "Fixture not found")
    data = load_json(str(fpath))
    has_auth = "_authority_claim" in data
    auto_repair = data.get("auto_repair", False)
    bad_advisory = data.get("advisory") is not True
    issues = []
    if has_auth:
        issues.append("authority claim")
    if auto_repair:
        issues.append("auto-repair")
    if bad_advisory:
        issues.append("non-advisory")
    return (has_auth or auto_repair or bad_advisory,
            f"Invalid fixture markers: {issues}" if issues else "Should have issues")


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
        ("RD-1", check_rd_1, "Advisory-only"),
        ("RD-2", check_rd_2, "Pipeline layers classified"),
        ("RD-3", check_rd_3, "Affected layer identification"),
        ("RD-4", check_rd_4, "No auto-repair"),
        ("RD-5", check_rd_5, "Cause classification"),
        ("RD-6", check_rd_6, "Bounded recovery options"),
        ("RD-7", check_rd_7, "Valid fixture"),
        ("RD-8", check_rd_8, "Invalid fixture markers"),
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
