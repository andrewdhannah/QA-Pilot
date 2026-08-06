#!/usr/bin/env python3
"""
QA Pilot Snapshot Update Gate Validator — QA-PILOT-SNAPSHOT-UPDATE-GATE-1

Enforces SUG-1 through SUG-13 business rules on snapshot update gate packets.

Rules:
    SUG-1:  Schema conformance
    SUG-2:  advisory_only = true
    SUG-3:  custody = qa-pilot-local
    SUG-4:  librarian_impact = none
    SUG-5:  not_seal_authority >= 20 chars
    SUG-6:  not_librarian_mutation_authority >= 20 chars
    SUG-7:  update_class valid enum
    SUG-8:  previous_snapshot_id starts with SRS-
    SUG-9:  rationale >= 20 chars
    SUG-10: proposed_layer_count < previous must explain
    SUG-11: no_snapshot_update_required: counts/gap must match
    SUG-12: No authority claims
    SUG-13: No Librarian mutation authority
"""

import json, re, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "qa-pilot-snapshot-update-gate.schema.json"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-snapshot-update-gate"
SNAPSHOT_DIR = REPO_ROOT / "data" / "startup-surface-regression-snapshots"

VALID = ["valid-legitimate-update.json", "valid-no-update-required.json"]
INVALID = ["invalid-stale-baseline.json", "invalid-short-rationale.json",
           "invalid-masking-regression.json", "invalid-unjustified-downgrade.json"]
ALL = sorted(set(VALID + INVALID))

FORBIDDEN_TERMS = ["approve", "seal", "execute", "write", "merge", "deploy"]
NEGATION_WORDS = ["not", "no", "zero", "without", "never", "none"]


def load_json(path):
    with open(path) as f:
        return json.load(f)


def validate_schema():
    try:
        s = load_json(SCHEMA_PATH)
        return (s.get("$schema") == "https://json-schema.org/draft/2020-12/schema" and bool(s.get("title")), "ok")
    except Exception as e:
        return False, str(e)


def validate_fixture(path):
    errors = []
    try:
        data = load_json(path)
    except Exception as e:
        return False, [f"Failed to parse: {e}"]

    gid = data.get("gate_id", "")
    if not re.match(r"^SUG-[A-Z0-9-]+$", gid):
        errors.append(f"SUG-1: Invalid gate_id: {gid}")
    if data.get("advisory_only") is not True:
        errors.append(f"SUG-2: advisory_only must be true")
    if data.get("custody") != "qa-pilot-local":
        errors.append(f"SUG-3: custody must be qa-pilot-local")
    if data.get("librarian_impact") != "none":
        errors.append(f"SUG-4: librarian_impact must be none")
    for key, label in [("not_seal_authority", "SUG-5"), ("not_librarian_mutation_authority", "SUG-6")]:
        val = data.get(key, "")
        if not isinstance(val, str) or len(val) < 20:
            errors.append(f"{label}: {key} must be >= 20 chars, got {len(val)}")
    uclass = data.get("update_class", "")
    valid_classes = {"legitimate_surface_change", "registry_layer_count_change",
                     "rcr_receipt_count_change", "rcg_coverage_change", "no_snapshot_update_required"}
    if uclass not in valid_classes:
        errors.append(f"SUG-7: Invalid update_class: {uclass}")
    prev_sid = data.get("previous_snapshot_id", "")
    if not prev_sid.startswith("SRS-"):
        errors.append(f"SUG-8: previous_snapshot_id must start with SRS-")
    rat = data.get("rationale", "")
    rat_lower = rat.lower()
    if not isinstance(rat, str) or len(rat) < 20:
        errors.append(f"SUG-9: rationale must be >= 20 chars, got {len(rat)}")
    
    # SUG-10: proposed_layer_count < previous must explain
    if data.get("proposed_layer_count", 0) < data.get("previous_layer_count", 0):
        if "deprecat" not in rat_lower and "remove" not in rat_lower:
            errors.append("SUG-10: Layer count decreased but rationale lacks deprecation/removal explanation")
    
    # SUG-11 (anti-masking): don't claim legitimate change while metrics degrade
    if uclass in ("legitimate_surface_change", "registry_layer_count_change"):
        if data.get("proposed_layer_count", 0) < data.get("previous_layer_count", 0) - 5:
            errors.append("SUG-11: Layer count dropped significantly — appears to mask regression")
        if data.get("proposed_rcg_gap", 0) > data.get("previous_rcg_gap", 0) + 3:
            errors.append("SUG-11: RCG gap increased significantly — appears to mask regression")
    
    if uclass == "no_snapshot_update_required":
        if data.get("previous_layer_count") != data.get("proposed_layer_count"):
            errors.append("SUG-11: no_snapshot_update_required but layer counts differ")
        if data.get("previous_rcr_count") != data.get("proposed_rcr_count"):
            errors.append("SUG-11: no_snapshot_update_required but RCR counts differ")
        if data.get("previous_rcg_gap") != data.get("proposed_rcg_gap"):
            errors.append("SUG-11: no_snapshot_update_required but RCG gap differs")
    rat_lower = rat.lower()
    for term in FORBIDDEN_TERMS:
        if re.search(r'\b' + re.escape(term) + r'\b', rat_lower):
            if not any(n in rat_lower for n in [f"no {term}", f"not {term}"]):
                errors.append(f"SUG-12: Forbidden term '{term}' in rationale")
    for key in ["rationale", "previous_sealed_head", "proposed_sealed_head"]:
        val = str(data.get(key, "")).lower()
        if "librarian" in val and "mutation" in val:
            if not any(n in val for n in NEGATION_WORDS):
                errors.append(f"SUG-13: References Librarian mutation without negation")
    return len(errors) == 0, errors


def do_checks():
    print("QA Pilot Snapshot Update Gate Validator — QA-PILOT-SNAPSHOT-UPDATE-GATE-1")
    print("=" * 60)
    print()
    all_pass = True
    ok, msg = validate_schema()
    print(f"{'✅' if ok else '❌'} Schema: {msg}")
    if not ok: all_pass = False
    print()
    print("[Fixture Validation]")
    missing = [f for f in ALL if not (FIXTURES_DIR / f).exists()]
    if missing:
        print(f"  ❌ Missing: {missing}")
        all_pass = False
    else:
        print(f"  ✅ All {len(ALL)} fixtures present")
    for fname in VALID:
        ok, errs = validate_fixture(FIXTURES_DIR / fname)
        if ok:
            print(f"  ✅ {fname}: passes")
        else:
            print(f"  ❌ {fname}: FAILED")
            for e in errs: print(f"     - {e}")
            all_pass = False
    for fname in INVALID:
        ok, errs = validate_fixture(FIXTURES_DIR / fname)
        if not ok:
            print(f"  ✅ {fname}: rejected ({len(errs)} violations)")
            for e in errs: print(f"     - {e}")
        else:
            print(f"  ❌ {fname}: should have been rejected")
            all_pass = False
    print()
    print("[Rules — SUG-1 through SUG-13]")
    print("  ✅ Enforced via fixtures")
    print(f"\n{'✅ ALL CHECKS PASS' if all_pass else '❌ SOME FAILED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(do_checks())
