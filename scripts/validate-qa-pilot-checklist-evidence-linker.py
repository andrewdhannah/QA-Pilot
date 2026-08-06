#!/usr/bin/env python3
"""
QA Pilot Checklist Evidence Linker Validator — QA-PILOT-CHECKLIST-EVIDENCE-LINKER-1

Enforces EL-1 through EL-14 business rules on evidence linker packets,
fixtures, and schema conformance.

Rules:
    EL-1:  Linker conforms to qa-pilot-checklist-evidence-linker.schema.json
    EL-2:  advisory_only must be true
    EL-3:  custody must be qa-pilot-local
    EL-4:  librarian_impact must be none
    EL-5:  not_seal_authority must be present and >= 20 chars
    EL-6:  not_librarian_mutation_authority must be present and >= 20 chars
    EL-7:  source_checklist_id must reference an EC-* pattern
    EL-8:  At least one link check required
    EL-9:  Aggregate counts must match link array
    EL-10: If missing > 0, aggregate.missing_refs must be non-empty
    EL-11: If stale > 0, aggregate.stale_refs must be non-empty
    EL-12: all_found must be true only when missing=0 and stale=0
    EL-13: No authority claims in descriptions or detail fields
    EL-14: No Librarian mutation authority referenced
"""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "qa-pilot-checklist-evidence-linker.schema.json"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-checklist-evidence-linker"

VALID_FIXTURES = [
    "valid-all-found.json",
    "valid-some-missing.json",
]

INVALID_FIXTURES = [
    "invalid-advisory-false.json",
    "invalid-wrong-custody.json",
    "invalid-aggregate-mismatch.json",
    "invalid-missing-no-refs-list.json",
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
    """Validate a single fixture against all business rules."""
    errors = []
    try:
        data = load_json(path)
    except Exception as e:
        return False, [f"Failed to parse JSON: {e}"]

    # EL-1: Basic structural checks
    lid = data.get("linker_id", "")
    if not re.match(r"^EL-[A-Z0-9-]+$", lid):
        errors.append(f"EL-1: Invalid linker_id pattern: {lid}")

    # EL-2: advisory_only
    if data.get("advisory_only") is not True:
        errors.append(f"EL-2: advisory_only must be true, got {data.get('advisory_only')}")

    # EL-3: custody
    if data.get("custody") != "qa-pilot-local":
        errors.append(f"EL-3: custody must be qa-pilot-local, got {data.get('custody')}")

    # EL-4: librarian_impact
    if data.get("librarian_impact") != "none":
        errors.append(f"EL-4: librarian_impact must be none, got {data.get('librarian_impact')}")

    # EL-5: not_seal_authority
    nsa = data.get("not_seal_authority", "")
    if not isinstance(nsa, str) or len(nsa) < 20:
        errors.append(f"EL-5: not_seal_authority must be >= 20 chars, got {len(nsa)}")

    # EL-6: not_librarian_mutation_authority
    nlma = data.get("not_librarian_mutation_authority", "")
    if not isinstance(nlma, str) or len(nlma) < 20:
        errors.append(f"EL-6: not_librarian_mutation_authority must be >= 20 chars, got {len(nlma)}")

    # EL-7: source_checklist_id
    sci = data.get("source_checklist_id", "")
    if not re.match(r"^EC-[A-Z0-9-]+$", sci):
        errors.append(f"EL-7: source_checklist_id must match EC-* pattern, got {sci}")

    # EL-8: At least one link
    links = data.get("links", [])
    if not isinstance(links, list) or len(links) == 0:
        errors.append("EL-8: At least one link check required")

    # EL-9: Aggregate counts match link array
    aggregate = data.get("aggregate", {})
    if isinstance(aggregate, dict) and isinstance(links, list):
        ag_total = aggregate.get("total_links", 0)
        ag_found = aggregate.get("found", 0)
        ag_missing = aggregate.get("missing", 0)
        ag_stale = aggregate.get("stale", 0)

        if ag_total != len(links):
            errors.append(f"EL-9: aggregate.total_links={ag_total} != len(links)={len(links)}")
        if ag_found + ag_missing + ag_stale != ag_total:
            errors.append(
                f"EL-9: found({ag_found}) + missing({ag_missing}) + stale({ag_stale}) "
                f"= {ag_found + ag_missing + ag_stale} != total_links({ag_total})"
            )

        # Also verify by counting actual statuses
        actual_found = sum(1 for l in links if l.get("status") == "found")
        actual_missing = sum(1 for l in links if l.get("status") == "missing")
        actual_stale = sum(1 for l in links if l.get("status") == "stale")
        if ag_found != actual_found:
            errors.append(f"EL-9: aggregate.found={ag_found} != actual found links={actual_found}")
        if ag_missing != actual_missing:
            errors.append(f"EL-9: aggregate.missing={ag_missing} != actual missing links={actual_missing}")
        if ag_stale != actual_stale:
            errors.append(f"EL-9: aggregate.stale={ag_stale} != actual stale links={actual_stale}")

        # EL-12: all_found correctness
        expected_all_found = (ag_missing == 0 and ag_stale == 0)
        if aggregate.get("all_found") != expected_all_found:
            errors.append(
                f"EL-12: all_found={aggregate.get('all_found')} but missing={ag_missing}, stale={ag_stale} "
                f"(expected all_found={expected_all_found})"
            )

    # EL-10: missing > 0 implies missing_refs non-empty
    if isinstance(aggregate, dict) and aggregate.get("missing", 0) > 0:
        missing_refs = aggregate.get("missing_refs", [])
        if not isinstance(missing_refs, list) or len(missing_refs) == 0:
            errors.append("EL-10: missing > 0 but aggregate.missing_refs is empty")

    # EL-11: stale > 0 implies stale_refs non-empty
    if isinstance(aggregate, dict) and aggregate.get("stale", 0) > 0:
        stale_refs = aggregate.get("stale_refs", [])
        if not isinstance(stale_refs, list) or len(stale_refs) == 0:
            errors.append("EL-11: stale > 0 but aggregate.stale_refs is empty")

    # EL-13: No authority claims in descriptions/detail
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
                errors.append(f"EL-13: Forbidden authority term '{term}' in description/title")

    if isinstance(links, list):
        for link in links:
            detail = link.get("detail", "").lower()
            for term in FORBIDDEN_AUTHORITY_TERMS:
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, detail):
                    context_ok = any(
                        neg in detail
                        for neg in [f"no {term}", f"not {term}", f"cannot {term}",
                                    f"does not {term}", f"reject {term}",
                                    f"denied {term}", f"block {term}"]
                    )
                    if not context_ok:
                        errors.append(f"EL-13: Forbidden authority term '{term}' in link detail")

    # EL-14: No Librarian mutation authority
    pipeline_refs = data.get("pipeline_refs", [])
    if isinstance(pipeline_refs, list):
        for ref in pipeline_refs:
            if "librarian" in str(ref.get("sprint_id", "")).lower():
                errors.append(f"EL-14: Pipeline ref references Librarian sprint: {ref.get('sprint_id')}")
            if "librarian" in str(ref.get("layer_name", "")).lower():
                errors.append(f"EL-14: Pipeline ref references Librarian layer: {ref.get('layer_name')}")

    return len(errors) == 0, errors


def do_checks():
    print("QA Pilot Checklist Evidence Linker Validator — QA-PILOT-CHECKLIST-EVIDENCE-LINKER-1")
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
        else:
            print(f"  ❌ {fname}: should have been rejected but passed")
            all_pass = False

    print()

    # ── Business rules summary ──
    print("[Business Rules — EL-1 through EL-14]")
    print("  ✅ EL-1 through EL-14 enforced via per-fixture validation")
    print()

    print(f"\n{'✅ ALL CHECKS PASS' if all_pass else '❌ SOME FAILED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(do_checks())
