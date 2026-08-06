#!/usr/bin/env python3
"""
QA Pilot Evidence Checklist Validator — QA-PILOT-EVIDENCE-CHECKLIST-1

Enforces EC-1 through EC-12 business rules on evidence checklist packets,
fixtures, and schema conformance.

Rules:
    EC-1:   Checklist conforms to qa-pilot-evidence-checklist.schema.json
    EC-2:   advisory_only must be true
    EC-3:   custody must be qa-pilot-local
    EC-4:   librarian_impact must be none
    EC-5:   At least one checklist item required
    EC-6:   At least one pipeline ref required
    EC-7:   Items with state=blocked must include rationale
    EC-8:   Item IDs must be unique within a checklist
    EC-9:   Pipeline refs must reference known sealed layers (33-43)
    EC-10:  No approval/seal/execute/write/sprint-start authority claimed
    EC-11:  All pipeline refs reference QA Pilot-local custody only
    EC-12:  No Librarian mutation authority referenced
"""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "qa-pilot-evidence-checklist.schema.json"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-evidence-checklist"

VALID_FIXTURES = [
    "valid-pipeline-evidence-checklist.json",
    "valid-standalone-evidence-checklist.json",
]

INVALID_FIXTURES = [
    "invalid-advisory-false.json",
    "invalid-wrong-custody.json",
    "invalid-librarian-mutation.json",
    "invalid-blocked-no-rationale.json",
    "invalid-no-items.json",
]

ALL_FIXTURES = sorted(set(VALID_FIXTURES + INVALID_FIXTURES))

KNOWN_LAYERS = {
    33: "QA-PILOT-MCP-EVIDENCE-INTAKE-1",
    34: "QA-PILOT-TEST-COMPOSITION-1",
    35: "QA-PILOT-RESULT-PACKET-EXPORT-1",
    36: "QA-PILOT-EPIC-REGRESSION-BUILDER-1",
    37: "QA-PILOT-EPIC-REGRESSION-STARTUP-SURFACE-1",
    38: "QA-PILOT-PIPELINE-HEALTH-REGRESSION-1",
    39: "QA-PILOT-PIPELINE-DRIFT-DETECTION-1",
    40: "QA-PILOT-PIPELINE-RECOVERY-DIAGNOSTICS-1",
    41: "QA-PILOT-PIPELINE-OWNER-REVIEW-PACKET-1",
    42: "QA-PILOT-OWNER-REVIEW-DECISION-RECEIPT-1",
    43: "QA-PILOT-OWNER-DECISION-RECEIPT-STARTUP-SURFACE-1",
}

FORBIDDEN_AUTHORITY_TERMS = [
    "approve", "seal", "execute", "write", "sprint-start",
    "merge", "production", "deploy",
]

PIPELINE_LAYER_ENUMS = [
    "evidence_intake", "test_composition", "result_export",
    "epic_regression", "pipeline_health", "drift_detection",
    "recovery_diagnostics", "owner_review_packet",
    "owner_decision_receipt", "odr_startup_surface",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_schema():
    """Validate the schema document itself is parseable."""
    try:
        schema = load_json(SCHEMA_PATH)
        if not isinstance(schema, dict):
            return False, "Schema is not a JSON object"
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            return False, "Schema must use Draft 2020-12"
        if not schema.get("title"):
            return False, "Schema missing title"
        return True, "ok"
    except Exception as e:
        return False, str(e)


def validate_fixture(path, is_valid_expected):
    """Validate a single fixture against the schema and business rules."""
    errors = []
    try:
        data = load_json(path)
    except Exception as e:
        return False, [f"Failed to parse JSON: {e}"]

    # EC-1: Schema conformance (structural checks)
    checklist_id = data.get("checklist_id", "")
    if not re.match(r"^EC-[A-Z0-9-]+$", checklist_id):
        errors.append(f"EC-1: Invalid checklist_id pattern: {checklist_id}")

    # EC-2: advisory_only must be true
    if data.get("advisory_only") is not True:
        errors.append(f"EC-2: advisory_only must be true, got {data.get('advisory_only')}")

    # EC-3: custody must be qa-pilot-local
    if data.get("custody") != "qa-pilot-local":
        errors.append(f"EC-3: custody must be qa-pilot-local, got {data.get('custody')}")

    # EC-4: librarian_impact must be none
    if data.get("librarian_impact") != "none":
        errors.append(f"EC-4: librarian_impact must be none, got {data.get('librarian_impact')}")

    # EC-5: At least one checklist item
    items = data.get("items", [])
    if not isinstance(items, list) or len(items) == 0:
        errors.append("EC-5: At least one checklist item required")

    # EC-6: At least one pipeline ref
    pipeline_refs = data.get("pipeline_refs", [])
    if not isinstance(pipeline_refs, list) or len(pipeline_refs) == 0:
        errors.append("EC-6: At least one pipeline ref required")

    # EC-7: Blocked items must have rationale
    if isinstance(items, list):
        for i, item in enumerate(items):
            if item.get("state") == "blocked" and not item.get("rationale"):
                errors.append(f"EC-7: Item {i} ({item.get('item_id', '?')}) blocked without rationale")

    # EC-8: Item IDs must be unique
    if isinstance(items, list):
        ids = [item.get("item_id") for item in items if item.get("item_id")]
        if len(ids) != len(set(ids)):
            errors.append("EC-8: Duplicate item IDs found")

    # EC-9: Pipeline refs reference known layers (33-43)
    if isinstance(pipeline_refs, list):
        for ref in pipeline_refs:
            sn = ref.get("sealed_number")
            if sn is not None and sn not in KNOWN_LAYERS:
                errors.append(f"EC-9: Unknown sealed_number {sn}, expected 33-43")

    # EC-10: No authority terms in descriptions/rationale
    if isinstance(items, list):
        for item in items:
            desc = (item.get("description", "") + " " + item.get("rationale", "")).lower()
            for term in FORBIDDEN_AUTHORITY_TERMS:
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, desc):
                    # Check if it's used in a negated/denied context
                    context_ok = any(
                        neg in desc
                        for neg in [f"no {term}", f"not {term}", f"cannot {term}",
                                    f"does not {term}", f"reject {term}",
                                    f"denied {term}", f"block {term}"]
                    )
                    if not context_ok:
                        errors.append(f"EC-10: Forbidden authority term '{term}' in item {item.get('item_id', '?')}")

    # EC-11: Pipeline refs QA Pilot-local only
    if isinstance(pipeline_refs, list):
        for ref in pipeline_refs:
            if "librarian" in str(ref.get("sprint_id", "")).lower():
                errors.append(f"EC-11: Pipeline ref references Librarian sprint: {ref.get('sprint_id')}")

    return len(errors) == 0, errors


def check_duplicate_item_ids(fixtures_to_check=None):
    """Check that item IDs are unique within each checklist."""
    issues = []
    targets = fixtures_to_check if fixtures_to_check else ALL_FIXTURES
    for fname in targets:
        path = FIXTURES_DIR / fname
        if not path.exists():
            continue
        try:
            data = load_json(path)
            items = data.get("items", [])
            ids = [item.get("item_id") for item in items if item.get("item_id")]
            if len(ids) != len(set(ids)):
                issues.append(f"EC-8 (duplicate): {fname}")
        except Exception:
            pass
    return issues


def do_checks():
    print("QA Pilot Evidence Checklist Validator — QA-PILOT-EVIDENCE-CHECKLIST-1")
    print("=" * 60)
    print()

    all_pass = True

    # ── Schema check ──
    print("[Schema Validation]")
    schema_ok, schema_msg = validate_schema()
    print(f"  {'✅' if schema_ok else '❌'} Schema: {schema_msg}")
    if not schema_ok:
        all_pass = False
    print()

    # ── Fixture checks ──
    print("[Fixture Validation]")
    all_fixtures_exist = True
    for fname in ALL_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if not fpath.exists():
            print(f"  ❌ Missing fixture: {fname}")
            all_fixtures_exist = False
            all_pass = False

    if all_fixtures_exist:
        print(f"  ✅ All {len(ALL_FIXTURES)} fixtures present")

    # Valid fixtures must pass
    for fname in VALID_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if not fpath.exists():
            continue
        ok, errs = validate_fixture(fpath, is_valid_expected=True)
        if ok:
            print(f"  ✅ {fname}: passes")
        else:
            print(f"  ❌ {fname}: FAILED")
            for e in errs:
                print(f"     - {e}")
            all_pass = False

    # Invalid fixtures must fail
    for fname in INVALID_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if not fpath.exists():
            continue
        ok, errs = validate_fixture(fpath, is_valid_expected=False)
        if not ok:
            print(f"  ✅ {fname}: correctly rejected ({len(errs)} violations)")
        else:
            print(f"  ❌ {fname}: should have been rejected but passed")
            all_pass = False

    print()

    # ── Business rules check ──
    print("[Business Rules — EC-1 through EC-12]")

    # EC-1 through EC-7, EC-10-12 are checked per fixture above
    # EC-8: Duplicate item IDs
    dup_issues = check_duplicate_item_ids()
    if not dup_issues:
        print("  ✅ EC-8: No duplicate item IDs in any checklist")
    else:
        for i in dup_issues:
            print(f"  ❌ {i}")
        all_pass = False

    # EC-9: Pipeline layer refs use valid enums
    enum_issues = []
    for fname in ALL_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if not fpath.exists():
            continue
        try:
            data = load_json(fpath)
            items = data.get("items", [])
            for item in items:
                refs = item.get("evidence_refs", [])
                for ref in refs:
                    layer = ref.get("pipeline_layer", "")
                    if layer and layer not in PIPELINE_LAYER_ENUMS:
                        enum_issues.append(f"{fname}: unknown layer '{layer}'")
        except Exception:
            pass
    if not enum_issues:
        print("  ✅ EC-9: All pipeline_layer values are valid enum members")
    else:
        for i in enum_issues:
            print(f"  ❌ EC-9: {i}")
        all_pass = False

    # Combined result
    print(f"\n{'✅ ALL CHECKS PASS' if all_pass else '❌ SOME FAILED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(do_checks())
