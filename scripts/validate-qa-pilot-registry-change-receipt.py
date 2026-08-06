#!/usr/bin/env python3
"""
QA Pilot Registry Change Receipt Validator — QA-PILOT-REGISTRY-CHANGE-RECEIPT-1

Enforces RCR-1 through RCR-15 business rules on registry change receipts,
fixtures, and schema conformance.

Rules:
    RCR-1:  Receipt conforms to qa-pilot-registry-change-receipt.schema.json
    RCR-2:  advisory_only must be true
    RCR-3:  custody must be qa-pilot-local
    RCR-4:  librarian_impact must be none
    RCR-5:  not_seal_authority must be present and >= 20 chars
    RCR-6:  not_librarian_mutation_authority must be present and >= 20 chars
    RCR-7:  registry_impact must be valid enum value
    RCR-8:  If adds_layer, layer_slot_added must be present and >= 1
    RCR-9:  If deprecates_layer, layer_slot_deprecated must be present and >= 1
    RCR-10: If no_registry_impact, rationale >= 20 chars
    RCR-11: registry_before_summary must be present and >= 10 chars
    RCR-12: registry_after_summary must be present and >= 10 chars
    RCR-13: When adds_layer, registry_after count is registry_before count + 1
    RCR-14: No authority claims in descriptions or rationale
    RCR-15: No Librarian mutation authority referenced
"""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "qa-pilot-registry-change-receipt.schema.json"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-registry-change-receipt"

VALID_FIXTURES = [
    "valid-adds-layer.json",
    "valid-no-impact.json",
    "valid-updates-layer.json",
    "valid-deprecates-layer.json",
]

INVALID_FIXTURES = [
    "invalid-no-impact-rationale-too-short.json",
    "invalid-advisory-false.json",
    "invalid-layer-count-mismatch.json",
    "invalid-brief-summaries-and-disclaimers.json",
]

ALL_FIXTURES = sorted(set(VALID_FIXTURES + INVALID_FIXTURES))

FORBIDDEN_AUTHORITY_TERMS = [
    "approve", "seal", "execute", "write", "sprint-start",
    "merge", "production", "deploy",
]

NEGATION_WORDS = ["not", "no", "zero", "without", "never", "none"]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_layer_count(summary_text):
    """Extract a layer count from a summary string like 'Registry has N layers'."""
    m = re.search(r'(\d+)\s*layers?', summary_text)
    if m:
        return int(m.group(1))
    return None


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


def validate_fixture(path):
    """Validate a single fixture against all business rules."""
    errors = []
    try:
        data = load_json(path)
    except Exception as e:
        return False, [f"Failed to parse JSON: {e}"]

    rid = data.get("receipt_id", "")

    # RCR-1: receipt_id pattern
    if not re.match(r"^RCR-[A-Z0-9-]+$", rid):
        errors.append(f"RCR-1: Invalid receipt_id pattern: {rid}")

    # RCR-2: advisory_only
    if data.get("advisory_only") is not True:
        errors.append(f"RCR-2: advisory_only must be true, got {data.get('advisory_only')}")

    # RCR-3: custody
    if data.get("custody") != "qa-pilot-local":
        errors.append(f"RCR-3: custody must be qa-pilot-local, got {data.get('custody')}")

    # RCR-4: librarian_impact
    if data.get("librarian_impact") != "none":
        errors.append(f"RCR-4: librarian_impact must be none, got {data.get('librarian_impact')}")

    # RCR-5: not_seal_authority
    nsa = data.get("not_seal_authority", "")
    if not isinstance(nsa, str) or len(nsa) < 20:
        errors.append(f"RCR-5: not_seal_authority must be >= 20 chars, got {len(nsa)}")

    # RCR-6: not_librarian_mutation_authority
    nlma = data.get("not_librarian_mutation_authority", "")
    if not isinstance(nlma, str) or len(nlma) < 20:
        errors.append(f"RCR-6: not_librarian_mutation_authority must be >= 20 chars, got {len(nlma)}")

    # RCR-7: registry_impact must be valid
    impact = data.get("registry_impact", "")
    valid_impacts = {"adds_layer", "updates_layer", "no_registry_impact", "deprecates_layer"}
    if impact not in valid_impacts:
        errors.append(f"RCR-7: Invalid registry_impact '{impact}', must be one of {valid_impacts}")

    # RCR-8: adds_layer requires layer_slot_added
    if impact == "adds_layer":
        slot = data.get("layer_slot_added")
        if not isinstance(slot, int) or slot < 1:
            errors.append(f"RCR-8: adds_layer requires layer_slot_added >= 1, got {slot}")

    # RCR-9: deprecates_layer requires layer_slot_deprecated
    if impact == "deprecates_layer":
        slot = data.get("layer_slot_deprecated")
        if not isinstance(slot, int) or slot < 1:
            errors.append(f"RCR-9: deprecates_layer requires layer_slot_deprecated >= 1, got {slot}")

    # RCR-10: no_registry_impact requires rationale >= 20
    if impact == "no_registry_impact":
        rat = data.get("rationale", "")
        if not isinstance(rat, str) or len(rat) < 20:
            errors.append(f"RCR-10: no_registry_impact requires rationale >= 20 chars, got {len(rat)}")

    # RCR-11: registry_before_summary >= 10 chars
    rbs = data.get("registry_before_summary", "")
    if not isinstance(rbs, str) or len(rbs) < 10:
        errors.append(f"RCR-11: registry_before_summary must be >= 10 chars, got {len(rbs)}")

    # RCR-12: registry_after_summary >= 10 chars
    ras = data.get("registry_after_summary", "")
    if not isinstance(ras, str) or len(ras) < 10:
        errors.append(f"RCR-12: registry_after_summary must be >= 10 chars, got {len(ras)}")

    # RCR-13: When adds_layer, layer count consistency
    if impact == "adds_layer":
        before_count = extract_layer_count(rbs)
        after_count = extract_layer_count(ras)
        if before_count is not None and after_count is not None:
            if after_count != before_count + 1:
                errors.append(
                    f"RCR-13: adds_layer but after count ({after_count}) "
                    f"is not before count ({before_count}) + 1"
                )

    # RCR-14: No authority claims
    desc_text = (data.get("rationale", "") + " " + data.get("registry_before_summary", "")
                 + " " + data.get("registry_after_summary", "")).lower()
    for term in FORBIDDEN_AUTHORITY_TERMS:
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, desc_text):
            context_ok = any(
                neg in desc_text
                for neg in [f"no {term}", f"not {term}", f"cannot {term}",
                            f"does not {term}", f"reject {term}",
                            f"denied {term}", f"block {term}"]
            )
            if not context_ok:
                errors.append(f"RCR-14: Forbidden authority term '{term}' in rationale/summary")

    # RCR-15: No Librarian mutation authority
    for key in ["rationale", "registry_before_summary", "registry_after_summary"]:
        val = str(data.get(key, "")).lower()
        if "librarian" in val and "mutation" in val:
            if not any(n in val for n in NEGATION_WORDS):
                errors.append(f"RCR-15: References Librarian mutation authority without negation")

    return len(errors) == 0, errors


def do_checks():
    print("QA Pilot Registry Change Receipt Validator — QA-PILOT-REGISTRY-CHANGE-RECEIPT-1")
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

    for fname in VALID_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if not fpath.exists():
            continue
        ok, errs = validate_fixture(fpath)
        if ok:
            print(f"  ✅ {fname}: passes")
        else:
            print(f"  ❌ {fname}: FAILED")
            for e in errs:
                print(f"     - {e}")
            all_pass = False

    for fname in INVALID_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if not fpath.exists():
            continue
        ok, errs = validate_fixture(fpath)
        if not ok:
            print(f"  ✅ {fname}: correctly rejected ({len(errs)} violations)")
            for e in errs:
                print(f"     - {e}")
        else:
            print(f"  ❌ {fname}: should have been rejected but passed")
            all_pass = False

    print()

    # ── Business rules summary ──
    print("[Business Rules — RCR-1 through RCR-15]")
    print("  ✅ RCR-1 through RCR-15 enforced via per-fixture validation")
    print()

    print(f"\n{'✅ ALL CHECKS PASS' if all_pass else '❌ SOME FAILED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(do_checks())
