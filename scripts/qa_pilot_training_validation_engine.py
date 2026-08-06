#!/usr/bin/env python3
"""
QA Pilot Training Validation Engine — QA-PILOT-TRAINING-VALIDATION-ENGINE-1

Deterministic validation of generated training packages.
Checks source coverage, stale references, missing sections,
unsupported claims, and authority violations.

Commands:
    check <pack-id>       — Run all validation checks on a package
    check --all           — Run validation on all generated packages
    sources <pack-id>     — Validate source coverage for a package
    authority <pack-id>   — Validate authority posture
    status                — Show validation engine state

Outcome levels:
    PASS   — All checks green
    FAIL   — Hard check failed (authority, provenance, schema)
    WARN   — Soft check flagged (stale sources, structural concerns)
"""

import datetime, hashlib, json, os, re, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PACKAGES_DIR = REPO_ROOT / "data" / "training-packages"
LIBRARIAN_ROOT = REPO_ROOT.parent.parent / "active" / "librarian"

FORBIDDEN_AUTHORITY_PATTERNS = [
    "this is authoritative", "canonical truth", "binding requirement",
    "must be followed by all", "automatically applies", "enforced by system"
]
FORBIDDEN_MUTATION_PATTERNS = [
    "seal_action", "approve_action", "merge_action",
    "librarian db write", "librarian mcp register"
]
MIN_SOURCE_COVERAGE_PCT = 50


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_package(pack_id):
    pkg_file = PACKAGES_DIR / pack_id / "package.json"
    if not pkg_file.exists():
        return None
    with open(pkg_file) as f:
        return json.load(f)


def check_schema_validity(pkg):
    """VE-1: Schema validity — pack has required fields."""
    required = ["schema_version", "pack_id", "artifact_type", "intended_audience",
                 "content", "provenance", "governance"]
    missing = [r for r in required if r not in pkg]
    passed = len(missing) == 0
    return ("VE-1", passed, "Schema valid" if passed else f"Missing: {missing}")


def check_source_coverage(pkg):
    """VE-2: Source coverage — provenance has ≥1 source and sections reference sources."""
    prov_sources = pkg.get("provenance", {}).get("librarian_sources", [])
    sections = pkg.get("content", {}).get("sections", [])

    has_prov = len(prov_sources) >= 1
    sections_have_sources = all(len(s.get("sources", [])) > 0 for s in sections) if sections else False

    pct = pkg.get("governance", {}).get("source_coverage_pct", 0)
    coverage_ok = pct >= MIN_SOURCE_COVERAGE_PCT

    all_pass = has_prov and sections_have_sources and coverage_ok
    detail = f"provenance_sources={len(prov_sources)}, sections_sourced={sections_have_sources}, coverage={pct}%"
    return ("VE-2", all_pass, detail)


def check_stale_references(pkg):
    """VE-3: Stale reference detection — check referenced sources still exist."""
    prov_sources = pkg.get("provenance", {}).get("librarian_sources", [])
    stale = []
    for src in prov_sources:
        src_path = src.get("path", "")
        full_path = LIBRARIAN_ROOT / src_path
        if not full_path.exists():
            stale.append(src_path)
    passed = len(stale) == 0
    detail = f"Stale: {stale}" if stale else "All sources accessible"
    return ("VE-3", passed, detail)


def check_missing_sections(pkg):
    """VE-4: Missing sections — content has at least 1 section."""
    sections = pkg.get("content", {}).get("sections", [])
    passed = len(sections) >= 1
    detail = f"{len(sections)} section(s)" if passed else "No sections"
    return ("VE-4", passed, detail)


def check_authority_violations(pkg):
    """VE-5: Authority violations — no forbidden authority claims."""
    body = json.dumps(pkg).lower()
    violations = [p for p in FORBIDDEN_AUTHORITY_PATTERNS if p.lower() in body]
    passed = len(violations) == 0
    detail = f"Violations: {violations}" if violations else "No authority violations"
    return ("VE-5", passed, detail)


def check_mutation_paths(pkg):
    """VE-6: No Librarian mutation paths."""
    body = json.dumps(pkg).lower()
    violations = [p for p in FORBIDDEN_MUTATION_PATTERNS if p.lower() in body]
    passed = len(violations) == 0
    detail = f"Found: {violations}" if violations else "No mutation paths"
    return ("VE-6", passed, detail)


def check_advisory_posture(pkg):
    """VE-7: Advisory posture — governance fields correct."""
    gov = pkg.get("governance", {})
    auth_ok = gov.get("authority_posture") == "advisory"
    owner_ok = gov.get("owner_decision_required_for_publish") is True
    all_pass = auth_ok and owner_ok
    detail_parts = []
    if not auth_ok: detail_parts.append(f"posture={gov.get('authority_posture')}")
    if not owner_ok: detail_parts.append("owner_decision not required")
    return ("VE-7", all_pass, "; ".join(detail_parts) if detail_parts else "Advisory posture correct")


def check_exercise_requirement(pkg):
    """VE-8: Exercise requirement for validation_exercise and workflow_tutorial."""
    atype = pkg.get("artifact_type", "")
    if atype not in ("validation_exercise", "workflow_tutorial"):
        return ("VE-8", True, f"Not required for {atype}")
    sections = pkg.get("content", {}).get("sections", [])
    missing = [s.get("id", "?") for s in sections if not s.get("exercises")]
    passed = len(missing) == 0
    return ("VE-8", passed, f"Sections missing exercises: {missing}" if missing else "All sections have exercises")


def check_provenance_hash(pkg):
    """VE-9: Provenance hash validity."""
    h = pkg.get("provenance", {}).get("source_hash", "")
    passed = bool(re.match(r"^[a-f0-9]{64}$", h))
    return ("VE-9", passed, "Hash valid" if passed else f"Invalid hash: {h[:20]}...")


def check_pack_id_format(pkg):
    """VE-10: Pack ID format."""
    pid = pkg.get("pack_id", "")
    passed = bool(re.match(r"^TP-[A-Z0-9-]+$", pid))
    return ("VE-10", passed, f"pack_id = '{pid}'")


ALL_CHECKS = [
    check_schema_validity, check_source_coverage, check_stale_references,
    check_missing_sections, check_authority_violations, check_mutation_paths,
    check_advisory_posture, check_exercise_requirement, check_provenance_hash,
    check_pack_id_format,
]


def run_validation(pkg):
    results = []
    for check_fn in ALL_CHECKS:
        rule_id, passed, detail = check_fn(pkg)
        results.append({"rule": rule_id, "passed": passed, "detail": detail})
    return results


def cmd_check(args):
    """Run all validation checks on a package."""
    check_all = "--all" in args
    pack_ids = []

    if check_all:
        if PACKAGES_DIR.exists():
            pack_ids = [d.name for d in PACKAGES_DIR.iterdir() if d.is_dir() and d.name != "__pycache__" and (d / "package.json").exists()]
        if not pack_ids:
            print("No packages found to validate.")
            return 0
    else:
        if not args or args[0] == "--all":
            print("Usage: validation_engine.py check <pack-id> | check --all")
            return 1
        pack_ids = [args[0]]

    overall_all_pass = True
    for pid in pack_ids:
        pkg = load_package(pid)
        if not pkg:
            print(f"❌ Package '{pid}' not found")
            overall_all_pass = False
            continue

        results = run_validation(pkg)
        all_pass = all(r["passed"] for r in results)
        if not all_pass:
            overall_all_pass = False

        print(f"Validation: {pid}")
        for r in results:
            p = "✅" if r["passed"] else "❌"
            print(f"  {p} {r['rule']}: {r['detail']}")
        print(f"  Overall: {'PASS' if all_pass else 'FAIL'}")

        # WARN for coverage below threshold but not critical
        coverage = pkg.get("governance", {}).get("source_coverage_pct", 0)
        if 0 < coverage < MIN_SOURCE_COVERAGE_PCT:
            print(f"  ⚠️  WARN: Source coverage {coverage}% below recommended {MIN_SOURCE_COVERAGE_PCT}%")
        print()

    return 0 if overall_all_pass else 2


def cmd_sources(args):
    """Validate source coverage for a package."""
    if not args:
        print("Usage: validation_engine.py sources <pack-id>")
        return 1
    pkg = load_package(args[0])
    if not pkg:
        print(f"Package '{args[0]}' not found")
        return 1

    prov = pkg.get("provenance", {})
    sections = pkg.get("content", {}).get("sections", [])

    print(f"Source coverage: {args[0]}")
    print(f"  Provenance sources: {len(prov.get('librarian_sources', []))}")
    print(f"  Declared coverage:  {pkg.get('governance', {}).get('source_coverage_pct', 0)}%")
    print(f"  Sections:           {len(sections)}")
    for s in sections:
        srcs = s.get("sources", [])
        print(f"    {s.get('id', '?')}: {len(srcs)} source(s)")
        for sp in srcs:
            exists = "✅" if (LIBRARIAN_ROOT / sp).exists() else "❌"
            print(f"      {exists} {sp}")

    prov_sources = prov.get("librarian_sources", [])
    all_accessible = all((LIBRARIAN_ROOT / s["path"]).exists() for s in prov_sources if "path" in s) if prov_sources else False
    sections_sourced = all(len(s.get("sources", [])) > 0 for s in sections) if sections else False

    if prov_sources and sections_sourced and all_accessible:
        print("\n✅ Source coverage PASS")
        return 0
    else:
        print("\n❌ Source coverage FAIL")
        return 1


def cmd_authority(args):
    """Validate authority posture."""
    if not args:
        print("Usage: validation_engine.py authority <pack-id>")
        return 1
    pkg = load_package(args[0])
    if not pkg:
        print(f"Package '{args[0]}' not found")
        return 1

    passed = True

    # Check governance fields
    gov = pkg.get("governance", {})
    auth = gov.get("authority_posture") == "advisory"
    print(f"  Authority posture: {'✅ advisory' if auth else '❌ ' + str(gov.get('authority_posture'))}")
    if not auth: passed = False

    owner = gov.get("owner_decision_required_for_publish") is True
    print(f"  Owner decision:    {'✅ required' if owner else '❌ not required'}")
    if not owner: passed = False

    # Check content for claims
    body = json.dumps(pkg).lower()
    for pat in FORBIDDEN_AUTHORITY_PATTERNS:
        if pat in body:
            print(f"  ❌ Authority claim: '{pat}'")
            passed = False

    # Check mutation paths
    for pat in FORBIDDEN_MUTATION_PATTERNS:
        if pat in body:
            print(f"  ❌ Mutation path: '{pat}'")
            passed = False

    print(f"\n{'✅ Authority PASS' if passed else '❌ Authority FAIL'}")
    return 0 if passed else 1


def cmd_status(args):
    """Show validation engine state."""
    count = 0
    if PACKAGES_DIR.exists():
        count = len([d for d in PACKAGES_DIR.iterdir() if d.is_dir() and (d / "package.json").exists()])

    print("QA Pilot Training Validation Engine")
    print("=" * 40)
    print(f"Packages available:   {count}")
    print(f"Validation checks:    {len(ALL_CHECKS)} (VE-1 to VE-{len(ALL_CHECKS)})")
    print(f"Min source coverage:  {MIN_SOURCE_COVERAGE_PCT}%")
    print(f"Authority posture:    advisory-only")
    print(f"Owner decision:       required")
    print(f"Cross-project write:  NOT AUTHORIZED")
    return 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("QA Pilot Training Validation Engine — QA-PILOT-TRAINING-VALIDATION-ENGINE-1")
        print()
        print("Usage:")
        print("  check <pack-id>        — Run all validation checks")
        print("  check --all            — Validate all packages")
        print("  sources <pack-id>      — Validate source coverage per-section")
        print("  authority <pack-id>    — Validate authority posture")
        print("  status                 — Show engine state")
        print()
        print("Outcomes: PASS / FAIL / WARN")
        return 0

    cmd = sys.argv[1]
    cargs = sys.argv[2:]
    cmds = {"check": cmd_check, "sources": cmd_sources, "authority": cmd_authority, "status": cmd_status}
    if cmd not in cmds:
        print(f"Unknown: {cmd}")
        return 1
    return cmds[cmd](cargs)


if __name__ == "__main__":
    sys.exit(main())
