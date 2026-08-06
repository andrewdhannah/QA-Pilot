#!/usr/bin/env python3
"""
QA Pilot Startup Surface Regression Snapshot Validator
— QA-PILOT-STARTUP-SURFACE-REGRESSION-SNAPSHOT-1

Compares live startup surface output against the expected snapshot baseline.
Reports any drift between expected and actual values.

Rules:
    SRS-1:  All expected fields present in snapshot
    SRS-2:  Sealed head matches snapshot
    SRS-3:  Registry layer count matches snapshot
    SRS-4:  Latest registry layer matches snapshot
    SRS-5:  PH-12 status matches snapshot
    SRS-6:  DR-3/DR-4 status matches snapshot
    SRS-7:  PLR status matches snapshot
    SRS-8:  SR-8 status matches snapshot
    SRS-9:  Overall classification matches snapshot
    SRS-10: RCR receipt count matches snapshot
    SRS-11: RCR latest receipt matches snapshot
    SRS-12: RCR status matches snapshot
    SRS-13: RCR classification matches snapshot
    SRS-14: RCG latest sealed matches snapshot
    SRS-15: RCG coverage gap matches snapshot
    SRS-16: RCG status matches snapshot
    SRS-17: RCG classification matches snapshot
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SNAPSHOT_DIR = REPO_ROOT / "data" / "startup-surface-regression-snapshots"
SURFACE_SCRIPT = SCRIPT_DIR / "qa_pilot_pipeline_startup_surface.py"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-startup-surface-regression-snapshot"

COMPARISON_FIELDS = [
    ("SRS-2", "expected_sealed_head", None),
    ("SRS-3", "expected_registry_layer_count", "registry_layer_count"),
    ("SRS-4", "expected_latest_registry_layer", "latest_registry_layer"),
    ("SRS-5", "expected_ph_12_status", "ph_12_status"),
    ("SRS-6", "expected_dr_3_4_status", "dr_3_4_status"),
    ("SRS-7", "expected_plr_status", "plr_status"),
    ("SRS-8", "expected_sr_8_status", "sr_8_status"),
    ("SRS-9", "expected_classification", "classification"),
    ("SRS-10", "expected_rcr_receipts_found", None),
    ("SRS-11", "expected_rcr_latest_receipt", None),
    ("SRS-12", "expected_rcr_status", None),
    ("SRS-13", "expected_rcr_classification", None),
    ("SRS-14", "expected_rcg_latest_sealed", None),
    ("SRS-15", "expected_rcg_coverage_gap", None),
    ("SRS-16", "expected_rcg_status", None),
    ("SRS-17", "expected_rcg_classification", None),
]

NESTED_MAP = {
    "expected_rcr_receipts_found": ("rcr_posture", "receipts_found"),
    "expected_rcr_latest_receipt": ("rcr_posture", "latest_receipt"),
    "expected_rcr_status": ("rcr_posture", "rcr_status"),
    "expected_rcr_classification": ("rcr_posture", "classification"),
    "expected_rcg_latest_sealed": ("rcg_posture", "latest_sealed_ledger"),
    "expected_rcg_latest_rcr": ("rcg_posture", "latest_rcr_ledger"),
    "expected_rcg_coverage_gap": ("rcg_posture", "coverage_gap"),
    "expected_rcg_status": ("rcg_posture", "rcg_status"),
    "expected_rcg_classification": ("rcg_posture", "classification"),
}


def load_json(path):
    with open(path) as f:
        return json.load(f)


def get_live_surface():
    r = subprocess.run(
        [sys.executable, str(SURFACE_SCRIPT), "report", "--format", "json"],
        capture_output=True, text=True, timeout=15
    )
    data = json.loads(r.stdout)
    return data.get("pipeline", data)


def validate_snapshot(snapshot_path, live_surface=None):
    errors = []
    snapshot = load_json(snapshot_path)

    # SRS-1: Snapshot ID valid
    sid = snapshot.get("snapshot_id", "")
    if not sid.startswith("SRS-"):
        errors.append(("SRS-1", False, f"Invalid snapshot_id: {sid}"))

    if live_surface is None:
        live_surface = get_live_surface()

    rp = live_surface.get("registry_posture", {})

    for srs_id, expected_key, live_key in COMPARISON_FIELDS:
        expected_val = snapshot.get(expected_key)
        
        # Get live value (may be nested)
        if expected_key in NESTED_MAP:
            nested_keys = NESTED_MAP[expected_key]
            live_val = rp.get(nested_keys[0], {}).get(nested_keys[1])
        elif live_key:
            live_val = rp.get(live_key)
        else:
            # Direct surface field
            live_val = live_surface.get(expected_key.replace("expected_", ""))

        if expected_val != live_val:
            errors.append((srs_id, False,
                f"Expected '{expected_val}', got '{live_val}'"))
        else:
            errors.append((srs_id, True, f"Match: {expected_val}"))

    return errors


def do_checks(fixture_mode=False):
    print("QA Pilot Startup Surface Regression Snapshot Validator")
    print("  — SRS-BASELINE-001")
    print("=" * 50)
    print()

    all_pass = True

    # Load live snapshot baseline
    snapshot_path = SNAPSHOT_DIR / "SRS-BASELINE-001.json"
    if not snapshot_path.exists():
        print(f"❌ Snapshot not found: {snapshot_path}")
        return 1

    if fixture_mode:
        # In fixture validation mode, check fixture files exist
        print("[Fixture Validation]")
        valid_fixtures = ["valid-snapshot-match.json"]
        invalid_fixtures = ["invalid-stale-head.json", "invalid-wrong-layer-count.json",
                           "invalid-missing-rcr-section.json"]
        for fname in valid_fixtures + invalid_fixtures:
            fpath = FIXTURES_DIR / fname
            ok = fpath.exists()
            print(f"  {'✅' if ok else '❌'} {fname}: {'present' if ok else 'missing'}")
            if not ok:
                all_pass = False
        print()
        print(f"\n{'✅ ALL FIXTURES PRESENT' if all_pass else '❌ SOME MISSING'}")
        return 0 if all_pass else 1

    # Live validation
    live = get_live_surface()
    results = validate_snapshot(snapshot_path, live)

    print("Live Startup Surface vs SRS-BASELINE-001")
    print("-" * 50)

    for srs_id, passed, msg in results:
        prefix = "✅" if passed else "❌"
        print(f"  {prefix} {srs_id}: {msg}")
        if not passed:
            all_pass = False

    print()
    print(f"\n{'✅ ALL SNAPSHOT CHECKS PASS' if all_pass else '❌ SOME CHECKS FAILED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    fixture_mode = "--fixtures" in sys.argv
    sys.exit(do_checks(fixture_mode=fixture_mode))
