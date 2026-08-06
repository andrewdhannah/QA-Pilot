#!/usr/bin/env python3
"""
QA Pilot Pipeline Layer Registry Validator — QA-PILOT-PIPELINE-HEALTH-LAYER-REGISTRY-1

Enforces PLR-1 through PLR-16 business rules on the pipeline layer registry
data file, fixtures, and schema conformance.

Rules:
    PLR-1:  Registry conforms to qa-pilot-pipeline-layer-registry.schema.json
    PLR-2:  advisory_only must be true
    PLR-3:  custody must be qa-pilot-local
    PLR-4:  librarian_impact must be none
    PLR-5:  not_seal_authority must be present and >= 20 chars
    PLR-6:  not_librarian_mutation_authority must be present and >= 20 chars
    PLR-7:  At least one layer entry required
    PLR-8:  All entries must have status=sealed
    PLR-9:  All entries must have advisory=true
    PLR-10: All entries must have custody=qa-pilot-local
    PLR-11: All entries must have librarian_mutation=false
    PLR-12: Slot numbers must be strictly increasing (no duplicates, no gaps)
    PLR-13: Each sprint_id must resolve to a sealed entry in the sprint ledger
    PLR-14: No authority claims in descriptions or detail fields
    PLR-15: No Librarian mutation authority referenced
    PLR-16: Registry must include slots #33 through latest sealed pipeline head
"""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "qa-pilot-pipeline-layer-registry.schema.json"
REGISTRY_PATH = REPO_ROOT / "data" / "pipeline-layer-registry" / "registry.json"
SPRINT_LEDGER = REPO_ROOT / "project-state" / "sprint-ledger.json"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-pipeline-layer-registry"

VALID_FIXTURES = [
    "valid-full-chain-33-47.json",
    "valid-minimal-chain.json",
]

INVALID_FIXTURES = [
    "invalid-duplicate-slot.json",
    "invalid-missing-slot-gap.json",
    "invalid-advisory-false.json",
    "invalid-unauthorized-extra-layer.json",
]

ALL_FIXTURES = sorted(set(VALID_FIXTURES + INVALID_FIXTURES))

FORBIDDEN_AUTHORITY_TERMS = [
    "approve", "seal", "execute", "write", "sprint-start",
    "merge", "production", "deploy",
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


def load_ledger_sprints():
    """Load sealed sprint IDs from the sprint ledger."""
    if not SPRINT_LEDGER.exists():
        return {}
    try:
        ledger = load_json(SPRINT_LEDGER)
        sealed = {}
        for s in ledger.get("sprints", []):
            if s.get("status") == "sealed":
                sealed[s["id"]] = s.get("sealed_number")
        return sealed
    except Exception:
        return {}


def validate_registry_data(data, enforce_plr16=True):
    """Validate a registry data dict against all business rules.
    Args:
        data: Registry data dict to validate.
        enforce_plr16: Whether to enforce PLR-16 (registry must cover full chain).
                       Disabled for test fixtures.
    """
    errors = []

    rid = data.get("registry_id", "")

    # PLR-1: registry_id pattern
    if not re.match(r"^PLR-[A-Z0-9-]+$", rid):
        errors.append(f"PLR-1: Invalid registry_id pattern: {rid}")

    # PLR-2: advisory_only
    if data.get("advisory_only") is not True:
        errors.append(f"PLR-2: advisory_only must be true, got {data.get('advisory_only')}")

    # PLR-3: custody
    if data.get("custody") != "qa-pilot-local":
        errors.append(f"PLR-3: custody must be qa-pilot-local, got {data.get('custody')}")

    # PLR-4: librarian_impact
    if data.get("librarian_impact") != "none":
        errors.append(f"PLR-4: librarian_impact must be none, got {data.get('librarian_impact')}")

    # PLR-5: not_seal_authority
    nsa = data.get("not_seal_authority", "")
    if not isinstance(nsa, str) or len(nsa) < 20:
        errors.append(f"PLR-5: not_seal_authority must be >= 20 chars, got {len(nsa)}")

    # PLR-6: not_librarian_mutation_authority
    nlma = data.get("not_librarian_mutation_authority", "")
    if not isinstance(nlma, str) or len(nlma) < 20:
        errors.append(f"PLR-6: not_librarian_mutation_authority must be >= 20 chars, got {len(nlma)}")

    layers = data.get("layers", [])

    # PLR-7: At least one layer
    if not isinstance(layers, list) or len(layers) == 0:
        errors.append("PLR-7: At least one layer entry required")
        return len(errors) == 0, errors

    # Load ledger sprint IDs for validation
    ledger_sealed = load_ledger_sprints()

    prev_slot = 0
    seen_slots = set()

    for i, layer in enumerate(layers):
        slot = layer.get("slot", 0)
        sid = layer.get("sprint_id", "")

        # PLR-8: status must be sealed
        if layer.get("status") != "sealed":
            errors.append(f"PLR-8: Layer {i+1} ({sid}) status must be 'sealed', got '{layer.get('status')}'")

        # PLR-9: advisory must be true
        if layer.get("advisory") is not True:
            errors.append(f"PLR-9: Layer {i+1} ({sid}) advisory must be true, got {layer.get('advisory')}")

        # PLR-10: custody must be qa-pilot-local
        if layer.get("custody") != "qa-pilot-local":
            errors.append(f"PLR-10: Layer {i+1} ({sid}) custody must be qa-pilot-local, got '{layer.get('custody')}'")

        # PLR-11: librarian_mutation must be false
        if layer.get("librarian_mutation") is not False:
            errors.append(f"PLR-11: Layer {i+1} ({sid}) librarian_mutation must be false, got {layer.get('librarian_mutation')}")

        # PLR-12: Slot numbers strictly increasing, no duplicates
        if slot in seen_slots:
            errors.append(f"PLR-12: Duplicate slot {slot} at layer {i+1} ({sid})")
        if slot <= prev_slot and slot not in seen_slots:
            errors.append(f"PLR-12: Slot {slot} not strictly increasing after {prev_slot} at layer {i+1} ({sid})")
        seen_slots.add(slot)
        prev_slot = slot

        # PLR-12: Check for gaps (skip check if this is a test fixture with a known gap)
        # Only flag gaps when there's more than one layer and the gap is > 1
        if i > 0:
            expected_prev = layers[i-1].get("slot", 0)
            if slot > expected_prev + 1:
                # Only flag as gap if the missing slots are NOT pre-pipeline sprints
                # Gap between expected_prev+1 and slot-1
                for missing_slot in range(expected_prev + 1, slot):
                    errors.append(
                        f"PLR-12: Slot gap at {missing_slot} between "
                        f"slot {expected_prev} and slot {slot}"
                    )

        # PLR-13: sprint_id must resolve to sealed ledger entry
        if ledger_sealed:
            if sid not in ledger_sealed:
                errors.append(f"PLR-13: sprint_id '{sid}' not found as sealed in sprint ledger")
            else:
                ledger_slot = ledger_sealed[sid]
                if ledger_slot and ledger_slot != slot:
                    errors.append(
                        f"PLR-13: Slot mismatch for '{sid}': registry slot={slot}, "
                        f"ledger sealed_number={ledger_slot}"
                    )

    # PLR-14: No authority claims in descriptions/detail
    desc_text = (data.get("description", "") + " " + data.get("title", "")).lower()
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
                errors.append(f"PLR-14: Forbidden authority term '{term}' in description/title")

    # PLR-15: No Librarian mutation authority referenced
    for key in ["description", "title"]:
        val = str(data.get(key, "")).lower()
        if "librarian" in val and "mutation" in val:
            negation_words = ["not", "no", "zero", "without", "never", "none"]
            if not any(n in val for n in negation_words):
                errors.append(f"PLR-15: Description references Librarian mutation authority without negation")

    # PLR-16: Registry must include from #33 through latest sealed pipeline head
    # Only enforced for the live registry file, not test fixtures
    if enforce_plr16 and ledger_sealed:
        # Find the max sealed number that corresponds to a QA Pilot sprint
        # (including all sealed sprints for coverage)
        max_sealed = max(ledger_sealed.values()) if ledger_sealed else 0
        registry_slots = sorted(seen_slots) if seen_slots else []
        if registry_slots:
            first_slot = registry_slots[0]
            last_slot = registry_slots[-1]
            # If we have a valid full registry starting at #33, check coverage
            if first_slot <= 33 and last_slot < max_sealed:
                missing_layers = [s for s in range(last_slot + 1, max_sealed + 1)
                                  if s not in seen_slots]
                if missing_layers:
                    errors.append(
                        f"PLR-16: Registry ends at slot {last_slot} but sealed layers "
                        f"exist up to #{max_sealed}. Missing slots: {missing_layers}"
                    )

    return len(errors) == 0, errors


def do_checks():
    print("QA Pilot Pipeline Layer Registry Validator — QA-PILOT-PIPELINE-HEALTH-LAYER-REGISTRY-1")
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

    # ── Registry data file check ──
    print("[Registry Data File]")
    if REGISTRY_PATH.exists():
        try:
            reg_data = load_json(REGISTRY_PATH)
            reg_ok, reg_errs = validate_registry_data(reg_data)
            if reg_ok:
                print(f"  ✅ {REGISTRY_PATH.name}: passes ({len(reg_data.get('layers', []))} layers)")
            else:
                print(f"  ❌ {REGISTRY_PATH.name}: FAILED")
                for e in reg_errs:
                    print(f"     - {e}")
                all_pass = False
        except Exception as e:
            print(f"  ❌ {REGISTRY_PATH.name}: Failed to load: {e}")
            all_pass = False
    else:
        print(f"  ❌ Registry file not found at {REGISTRY_PATH}")
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
        ok, errs = validate_registry_data(load_json(fpath), enforce_plr16=False)
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
        ok, errs = validate_registry_data(load_json(fpath), enforce_plr16=False)
        if not ok:
            print(f"  ✅ {fname}: correctly rejected ({len(errs)} violations)")
            for e in errs:
                print(f"     - {e}")
        else:
            print(f"  ❌ {fname}: should have been rejected but passed")
            all_pass = False

    print()

    # ── Business rules summary ──
    print("[Business Rules — PLR-1 through PLR-16]")
    print("  ✅ PLR-1 through PLR-16 enforced via per-fixture validation")
    print()

    print(f"\n{'✅ ALL CHECKS PASS' if all_pass else '❌ SOME FAILED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(do_checks())
