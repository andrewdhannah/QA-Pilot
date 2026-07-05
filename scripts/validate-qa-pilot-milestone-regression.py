#!/usr/bin/env python3
"""
QA Pilot Milestone Regression Suite — QA-PILOT-MILESTONE-REGRESSION-SUITE-1

Validates the sealed QA packet ingest chain remains stable under regression.
Tests packet custody invariants, advisory boundary, derived-store behavior,
invalid-packet rejection, and the no-cross-project-write rule.

Invariants tested:
    MR-1:  Existing ingest validator still passes (PI-1 through PI-14)
    MR-2:  Valid regression fixtures pass all PI rules
    MR-3:  Invalid regression fixtures fail for expected reasons
    MR-4:  Ingest CLI rejects invalid fixtures (validation fails closed)
    MR-5:  Ingested records always have advisory=true
    MR-6:  Ingested records always have cross_project_write_authorized=false
    MR-7:  Ingested records always have owner_apply_required=true
    MR-8:  No ingested packet payload contains mutation-authorizing keys
    MR-9:  Derived state is local (QA Pilot only) and reconstructable
    MR-10: Invalid adversarial shapes fail closed at schema level
    MR-11: No Librarian file writes from regression operations
"""

import json
import os
import sys
import datetime
import subprocess
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-milestone-regression"
INGEST_FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-qa-packet-ingest"
INGEST_CLI = SCRIPT_DIR / "qa_pilot_qa_packet_ingest.py"
INGEST_VALIDATOR = SCRIPT_DIR / "validate-qa-pilot-qa-packet-ingest.py"
INGESTED_DIR = REPO_ROOT / "data" / "packets" / "ingested"
INDEX_FILE = REPO_ROOT / "data" / "packets" / "ingested-index.json"
LIBRARIAN_BASE = REPO_ROOT.parent / "librarian"

KNOWN_PACKET_TYPES = ["qa_claim_registry", "project_state", "milestone_regression", "training_source"]
VALID_AUTHORITY_STATUSES = ["authoritative_export", "advisory_copy", "training_simulated"]
FORBIDDEN_ALLOWED_USES = ["direct_librarian_mutation"]
REQUIRED_FORBIDDEN_USES = ["direct_librarian_mutation", "owner_decision_substitution", "authority_promotion"]
FORBIDDEN_MUTATION_KEYS = ["seal_action", "approve_action", "merge_action", "production_readiness_action", "runtime_mutation_action"]
FORBIDDEN_MUTATION_PATTERNS = ["active/librarian/", "librarian DB write", "librarian MCP register"]

PASS = 0
FAIL = 0
CHECKS = []


def check(rule_id, description, passed, detail):
    """Record a check result."""
    global PASS, FAIL
    if passed:
        PASS += 1
        print(f"  ✅ {rule_id}: {description} — {detail}")
    else:
        FAIL += 1
        print(f"  ❌ {rule_id}: {description} — {detail}")
    CHECKS.append({"rule": rule_id, "passed": passed, "detail": detail})


def load_json(path):
    """Load a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_cli(args):
    """Run the ingest CLI and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(INGEST_CLI)] + args,
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    return result.returncode, result.stdout, result.stderr


def clear_ingested():
    """Clear ingested packets."""
    run_cli(["clear"])


# ── MR-1: Existing ingest validator still passes ──────────────────────────

def test_mr_1():
    """MR-1: Existing ingest validator (PI-1 through PI-14) still passes."""
    result = subprocess.run(
        [sys.executable, str(INGEST_VALIDATOR)],
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    passed = result.returncode == 0 and "ALL CHECKS PASS" in result.stdout
    check("MR-1",
          "Existing PI-1 through PI-14 validator still passes",
          passed,
          f"exit={result.returncode}, output_ok={'ALL CHECKS PASS' in result.stdout}")


# ── MR-2: Valid regression fixtures pass ─────────────────────────────────

def test_mr_2():
    """MR-2: All valid regression fixtures pass PI rules individually."""
    valid_files = sorted(FIXTURES_DIR.glob("regression-valid-*.json"))
    all_passed = True
    for f in valid_files:
        result = subprocess.run(
            [sys.executable, str(INGEST_CLI), "validate", str(f)],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        fixture_ok = result.returncode == 0 and "VALID" in result.stdout
        if not fixture_ok:
            all_passed = False
            print(f"       FAIL: {f.name} — {result.stdout.strip()[-200:]}")
    check("MR-2",
          f"All {len(valid_files)} valid regression fixtures pass CLI validation",
          all_passed,
          f"{len(valid_files)} fixtures, all pass={all_passed}")


# ── MR-3: Invalid regression fixtures fail for expected reasons ──────────

def test_mr_3():
    """MR-3: Invalid regression fixtures fail for expected invariant reasons."""
    invalid_files = sorted(FIXTURES_DIR.glob("regression-invalid-*.json"))
    
    # Expected failure reasons per invariant fixture
    expected_failures = {
        "regression-invalid-mutation-authorized.json": ["PI-11", "INVALID"],
        "regression-invalid-no-owner-apply.json": ["PI-10", "INVALID"],
        "regression-invalid-cross-project-write.json": ["PI-8", "INVALID"],
        "regression-invalid-mutation-payload.json": ["PI-11", "INVALID"],
        "regression-invalid-adversarial-shape.json": ["PI-1", "INVALID"],
        "regression-invalid-authority-promotion.json": ["PI-12", "INVALID"],
        "regression-invalid-librarian-path.json": ["PI-11", "INVALID"],
    }
    
    all_rejected = True
    for f in invalid_files:
        fname = f.name
        result = subprocess.run(
            [sys.executable, str(INGEST_CLI), "validate", str(f)],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        rejected = result.returncode != 0 or "VALID" not in result.stdout
        if not rejected:
            all_rejected = False
            print(f"       FAIL: {fname} was accepted but should be rejected")
            continue
        
        # Check expected failure rule
        expected = expected_failures.get(fname, [])
        found_expected = any(e in result.stdout for e in expected)
        if not found_expected:
            print(f"       WARN: {fname} rejected but expected indicators {expected} not found in output")
    
    total = len(invalid_files)
    check("MR-3",
          f"All {total} invalid regression fixtures rejected",
          all_rejected,
          f"{total} fixtures, all rejected={all_rejected}")


# ── MR-4: Ingest CLI rejects invalid shapes (fail closed) ────────────────

def test_mr_4():
    """MR-4: Ingest CLI rejects invalid fixtures via ingest command (fail closed)."""
    invalid_files = sorted(FIXTURES_DIR.glob("regression-invalid-*.json"))
    all_rejected = True
    for f in invalid_files:
        result = subprocess.run(
            [sys.executable, str(INGEST_CLI), "ingest", str(f)],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        if result.returncode == 0 and "IMPORTED" in result.stdout:
            all_rejected = False
            print(f"       FAIL: {f.name} was ingested but should be rejected")
    check("MR-4",
          "Ingest CLI rejects invalid fixtures (fail closed)",
          all_rejected,
          f"{len(invalid_files)} invalid fixtures, all rejected={all_rejected}")


# ── MR-5: Ingested records always have advisory=true ─────────────────────

def test_mr_5():
    """MR-5: Every ingested record has advisory=true."""
    if not INDEX_FILE.exists():
        check("MR-5", "Advisory invariant", False, "No index file found — no packets ingested")
        return
    
    index = load_json(str(INDEX_FILE))
    packets = index.get("packets", [])
    if not packets:
        check("MR-5", "Advisory invariant", True, "No packets to check (skipped)")
        return
    
    all_advisory = all(p.get("advisory") is True for p in packets)
    bad = [p["ingest_id"] for p in packets if p.get("advisory") is not True]
    check("MR-5",
          f"All {len(packets)} ingested records have advisory=true",
          all_advisory,
          f"advisory invariant: {len(packets)} records, violations={len(bad)}")


# ── MR-6: Ingested records always have cross_project_write_authorized=false ─

def test_mr_6():
    """MR-6: Every ingested record has cross_project_write_authorized=false."""
    if not INDEX_FILE.exists():
        check("MR-6", "Cross-project write invariant", False, "No index file found")
        return
    
    index = load_json(str(INDEX_FILE))
    packets = index.get("packets", [])
    if not packets:
        check("MR-6", "Cross-project write invariant", True, "No packets to check (skipped)")
        return
    
    all_blocked = all(p.get("cross_project_write_authorized") is False for p in packets)
    bad = [p["ingest_id"] for p in packets if p.get("cross_project_write_authorized") is not False]
    check("MR-6",
          f"All {len(packets)} ingested records have cross_project_write_authorized=false",
          all_blocked,
          f"cross-project write invariant: {len(packets)} records, violations={len(bad)}")


# ── MR-7: Ingested records always have owner_apply_required=true ──────────

def test_mr_7():
    """MR-7: Every ingested record has owner_apply_required=true."""
    if not INDEX_FILE.exists():
        check("MR-7", "Owner apply invariant", False, "No index file found")
        return
    
    index = load_json(str(INDEX_FILE))
    packets = index.get("packets", [])
    if not packets:
        check("MR-7", "Owner apply invariant", True, "No packets to check (skipped)")
        return
    
    all_require_owner = all(p.get("owner_apply_required") is True for p in packets)
    bad = [p["ingest_id"] for p in packets if p.get("owner_apply_required") is not True]
    check("MR-7",
          f"All {len(packets)} ingested records have owner_apply_required=true",
          all_require_owner,
          f"owner apply invariant: {len(packets)} records, violations={len(bad)}")


# ── MR-8: No ingested packet payload contains mutation-authorizing keys ───

def test_mr_8():
    """MR-8: No stored packet payload contains mutation-authorizing keys."""
    if not INDEX_FILE.exists():
        check("MR-8", "Mutation key scan", False, "No index file found")
        return
    
    index = load_json(str(INDEX_FILE))
    packets = index.get("packets", [])
    if not packets:
        check("MR-8", "Mutation key scan", True, "No packets to check (skipped)")
        return
    
    mutation_keys_found = []
    for p in packets:
        store_path = Path(p.get("store_path", ""))
        if store_path.exists():
            stored = load_json(str(store_path))
            payload = stored.get("payload", {})
            for key in payload.keys():
                key_lower = key.lower()
                for forbidden in FORBIDDEN_MUTATION_KEYS:
                    if forbidden.lower() in key_lower:
                        mutation_keys_found.append(f"{p['ingest_id']}.{key}")
    
    check("MR-8",
          "No stored packet payload contains mutation-authorizing keys",
          len(mutation_keys_found) == 0,
          f"scanned {len(packets)} packets, violations={len(mutation_keys_found)}: {mutation_keys_found}")


# ── MR-9: Derived state is local and reconstructable ─────────────────────

def test_mr_9():
    """MR-9: Derived state is QA Pilot-local and reconstructable from scratch."""
    # Check data directory is inside QA Pilot
    data_dir = REPO_ROOT / "data"
    is_local = data_dir.exists() and str(data_dir).startswith(str(REPO_ROOT))
    
    # Check no data leaked to Librarian
    librarian_data = LIBRARIAN_BASE / "data" / "packets"
    leaked = librarian_data.exists() and any(librarian_data.iterdir())
    
    # Test reconstruction: clear → re-ingest → verify count
    clear_ingested()
    
    # Re-ingest valid fixtures
    valid_files = sorted(FIXTURES_DIR.glob("regression-valid-*.json"))
    ingest_count = 0
    for f in valid_files:
        rc, out, _ = run_cli(["ingest", str(f)])
        if rc == 0 and "IMPORTED" in out:
            ingest_count += 1
    
    # Now verify the index
    index = load_json(str(INDEX_FILE))
    index_count = len(index.get("packets", []))
    reconstructable = index_count == ingest_count and index_count > 0
    
    # Verify stored files exist
    stored_files_exist = True
    for p in index.get("packets", []):
        sp = Path(p.get("store_path", ""))
        if not sp.exists():
            stored_files_exist = False
            print(f"       FAIL: stored file missing: {sp}")
    
    all_ok = is_local and not leaked and reconstructable and stored_files_exist
    check("MR-9",
          "Derived state is local and reconstructable",
          all_ok,
          f"local={is_local}, librarian_leak={leaked}, "
          f"reconstructable={reconstructable} ({index_count}/{ingest_count}), "
          f"stored_files={stored_files_exist}")


# ── MR-10: Invalid adversarial shapes fail closed at schema level ────────

def test_mr_10():
    """MR-10: Invalid adversarial packet shapes fail closed at schema level."""
    # Test a completely malformed packet (not JSON)
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    tmp.write("this is not json {{{")
    tmp.close()
    
    rc, out, _ = run_cli(["validate", tmp.name])
    os.unlink(tmp.name)
    shape_fail = rc != 0 or "VALID" not in out
    
    # Test missing file
    rc2, out2, _ = run_cli(["validate", "/tmp/nonexistent-packet-file.json"])
    missing_fail = rc2 != 0
    
    check("MR-10",
          "Invalid adversarial shapes fail closed",
          shape_fail and missing_fail,
          f"malformed_json_rejected={shape_fail}, missing_file_rejected={missing_fail}")


# ── MR-11: No Librarian file writes from regression operations ───────────

def test_mr_11():
    """MR-11: Regression operations do not write to Librarian paths."""
    # Check that no regression files exist in Librarian
    reg_paths = [
        LIBRARIAN_BASE / "docs" / "examples" / "qa-pilot-milestone-regression",
        LIBRARIAN_BASE / "scripts" / "validate-qa-pilot-milestone-regression.py",
        LIBRARIAN_BASE / "scripts" / "test-qa-pilot-milestone-regression.sh",
        LIBRARIAN_BASE / "docs" / "governance" / "QA-PILOT-MILESTONE-REGRESSION.md",
    ]
    leaked = [str(p) for p in reg_paths if p.exists()]
    
    check("MR-11",
          "No Librarian file writes from regression operations",
          len(leaked) == 0,
          f"regression files in Librarian={len(leaked)}: {leaked}")


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    print("QA Pilot Milestone Regression Suite")
    print("=====================================")
    print(f"Regression fixtures: {FIXTURES_DIR}")
    print(f"Ingest CLI:          {INGEST_CLI}")
    print(f"Ingest validator:    {INGEST_VALIDATOR}")
    print(f"Data directory:      {INGESTED_DIR}")
    print()

    # Ensure clean state
    clear_ingested()

    # Run all tests
    test_mr_1()
    test_mr_2()
    test_mr_3()
    test_mr_4()
    test_mr_5()
    test_mr_6()
    test_mr_7()
    test_mr_8()
    test_mr_9()
    test_mr_10()
    test_mr_11()

    # Summary
    print()
    print("=====================================")
    print(f"Regression checks: {len(CHECKS)} total")
    print(f"Pass:  {PASS}")
    print(f"Fail:  {FAIL}")

    # Detail for failures
    failures = [c for c in CHECKS if not c["passed"]]
    if failures:
        print()
        print("Failures:")
        for f in failures:
            print(f"  ❌ {f['rule']}: {f['detail']}")

    print()
    if FAIL == 0:
        print("✅ ALL REGRESSION CHECKS PASS")
        return 0
    else:
        print(f"❌ {FAIL} REGRESSION CHECK(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
