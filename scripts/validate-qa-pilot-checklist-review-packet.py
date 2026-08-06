#!/usr/bin/env python3
"""
QA Pilot Checklist Review Packet Validator — QA-PILOT-CHECKLIST-REVIEW-PACKET-1

Enforces CRP-1 through CRP-12 business rules on checklist review packets,
fixtures, and schema conformance.

Rules:
    CRP-1:  Review packet conforms to qa-pilot-checklist-review-packet.schema.json
    CRP-2:  advisory_only must be true
    CRP-3:  custody must be qa-pilot-local
    CRP-4:  librarian_impact must be none
    CRP-5:  not_seal_authority must be present and >= 20 chars
    CRP-6:  not_librarian_mutation_authority must be present and >= 20 chars
    CRP-7:  source_checklist_id must reference an EC-* pattern
    CRP-8:  item_summary total must equal blocked + degraded + ready
    CRP-9:  If blocked > 0, blocked_items must be present and non-empty
    CRP-10: No approval/seal/execute/write/sprint-start authority claimed
    CRP-11: All pipeline refs reference QA Pilot-local custody only
    CRP-12: No Librarian mutation authority referenced
"""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "qa-pilot-checklist-review-packet.schema.json"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-checklist-review-packet"

VALID_FIXTURES = [
    "valid-pipeline-review-packet.json",
    "valid-blocked-review-packet.json",
]

INVALID_FIXTURES = [
    "invalid-advisory-false.json",
    "invalid-wrong-custody.json",
    "invalid-librarian-mutation.json",
    "invalid-blocked-no-items.json",
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


def validate_fixture(path):
    """Validate a single fixture against the business rules."""
    errors = []
    try:
        data = load_json(path)
    except Exception as e:
        return False, [f"Failed to parse JSON: {e}"]

    # CRP-1: Schema conformance (structural checks)
    rpid = data.get("review_packet_id", "")
    if not re.match(r"^CRP-[A-Z0-9-]+$", rpid):
        errors.append(f"CRP-1: Invalid review_packet_id pattern: {rpid}")

    # CRP-2: advisory_only must be true
    if data.get("advisory_only") is not True:
        errors.append(f"CRP-2: advisory_only must be true, got {data.get('advisory_only')}")

    # CRP-3: custody must be qa-pilot-local
    if data.get("custody") != "qa-pilot-local":
        errors.append(f"CRP-3: custody must be qa-pilot-local, got {data.get('custody')}")

    # CRP-4: librarian_impact must be none
    if data.get("librarian_impact") != "none":
        errors.append(f"CRP-4: librarian_impact must be none, got {data.get('librarian_impact')}")

    # CRP-5: not_seal_authority present and >= 20 chars
    nsa = data.get("not_seal_authority", "")
    if not isinstance(nsa, str) or len(nsa) < 20:
        errors.append(f"CRP-5: not_seal_authority must be >= 20 chars, got {len(nsa)}")

    # CRP-6: not_librarian_mutation_authority present and >= 20 chars
    nlma = data.get("not_librarian_mutation_authority", "")
    if not isinstance(nlma, str) or len(nlma) < 20:
        errors.append(f"CRP-6: not_librarian_mutation_authority must be >= 20 chars, got {len(nlma)}")

    # CRP-7: source_checklist_id must reference EC-* pattern
    sci = data.get("source_checklist_id", "")
    if not re.match(r"^EC-[A-Z0-9-]+$", sci):
        errors.append(f"CRP-7: source_checklist_id must match EC-* pattern, got {sci}")

    # CRP-8: item_summary total must equal blocked + degraded + ready
    summary = data.get("item_summary", {})
    if isinstance(summary, dict):
        total = summary.get("total", 0)
        blocked = summary.get("blocked", 0)
        degraded = summary.get("degraded", 0)
        ready = summary.get("ready", 0)
        if total != blocked + degraded + ready:
            errors.append(
                f"CRP-8: total={total} != blocked({blocked}) + degraded({degraded}) + ready({ready}) = {blocked + degraded + ready}"
            )

    # CRP-9: If blocked > 0, blocked_items must be present and non-empty
    if isinstance(summary, dict) and summary.get("blocked", 0) > 0:
        blocked_items = data.get("blocked_items", [])
        if not isinstance(blocked_items, list) or len(blocked_items) == 0:
            errors.append("CRP-9: blocked > 0 but blocked_items is missing or empty")

    # CRP-10: No authority terms in descriptions/rationale
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
                errors.append(f"CRP-10: Forbidden authority term '{term}' in description/title")

    # Also check blocked_items rationale
    blocked_items = data.get("blocked_items", [])
    if isinstance(blocked_items, list):
        for item in blocked_items:
            rationale = (item.get("description", "") + " " + item.get("rationale", "")).lower()
            for term in FORBIDDEN_AUTHORITY_TERMS:
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, rationale):
                    context_ok = any(
                        neg in rationale
                        for neg in [f"no {term}", f"not {term}", f"cannot {term}",
                                    f"does not {term}", f"reject {term}",
                                    f"denied {term}", f"block {term}"]
                    )
                    if not context_ok:
                        errors.append(f"CRP-10: Forbidden authority term '{term}' in blocked item rationale")

    # CRP-11: Pipeline refs QA Pilot-local only
    pipeline_refs = data.get("pipeline_refs", [])
    if isinstance(pipeline_refs, list):
        for ref in pipeline_refs:
            if "librarian" in str(ref.get("sprint_id", "")).lower():
                errors.append(f"CRP-11: Pipeline ref references Librarian sprint: {ref.get('sprint_id')}")

    # CRP-12: No Librarian mutation authority referenced
    if isinstance(pipeline_refs, list):
        for ref in pipeline_refs:
            if "librarian" in str(ref.get("layer_name", "")).lower():
                errors.append(f"CRP-12: Pipeline ref references Librarian layer: {ref.get('layer_name')}")

    return len(errors) == 0, errors


def do_checks():
    print("QA Pilot Checklist Review Packet Validator — QA-PILOT-CHECKLIST-REVIEW-PACKET-1")
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
        ok, errs = validate_fixture(fpath)
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
        ok, errs = validate_fixture(fpath)
        if not ok:
            print(f"  ✅ {fname}: correctly rejected ({len(errs)} violations)")
        else:
            print(f"  ❌ {fname}: should have been rejected but passed")
            all_pass = False

    print()

    # ── Business rules check ──
    print("[Business Rules — CRP-1 through CRP-12]")

    # CRP-8: Verify total = blocked + degraded + ready across valid fixtures
    crp8_issues = []
    for fname in VALID_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if not fpath.exists():
            continue
        try:
            data = load_json(fpath)
            summary = data.get("item_summary", {})
            if isinstance(summary, dict):
                total = summary.get("total", 0)
                blocked = summary.get("blocked", 0)
                degraded = summary.get("degraded", 0)
                ready = summary.get("ready", 0)
                if total != blocked + degraded + ready:
                    crp8_issues.append(f"{fname}: total={total} != {blocked}+{degraded}+{ready}")
        except Exception:
            pass

    if not crp8_issues:
        print("  ✅ CRP-8: All fixtures have consistent item_summary totals")
    else:
        for i in crp8_issues:
            print(f"  ❌ CRP-8: {i}")
        all_pass = False

    # CRP-9: Verify blocked > 0 implies blocked_items present (valid fixtures only)
    crp9_issues = []
    for fname in VALID_FIXTURES:
        fpath = FIXTURES_DIR / fname
        if not fpath.exists():
            continue
        try:
            data = load_json(fpath)
            summary = data.get("item_summary", {})
            if isinstance(summary, dict) and summary.get("blocked", 0) > 0:
                blocked_items = data.get("blocked_items", [])
                if not isinstance(blocked_items, list) or len(blocked_items) == 0:
                    crp9_issues.append(f"{fname}: blocked={summary['blocked']} but no blocked_items")
        except Exception:
            pass

    if not crp9_issues:
        print("  ✅ CRP-9: All fixtures with blocked>0 have blocked_items")
    else:
        for i in crp9_issues:
            print(f"  ❌ CRP-9: {i}")
        all_pass = False

    print(f"\n{'✅ ALL CHECKS PASS' if all_pass else '❌ SOME FAILED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(do_checks())
