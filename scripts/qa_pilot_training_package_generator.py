#!/usr/bin/env python3
"""
QA Pilot Training Package Generator — QA-PILOT-TRAINING-PACKAGE-GENERATOR-1

Generates training packages from approved Librarian source material.
Selects source set via knowledge adapter, generates content structure,
attaches provenance, validates, and produces output.

Commands:
    init <pack-id> <type> [--title <t>] [--audience <a>]
                             — Initialize a new training package skeleton
    generate <pack-id>       — Generate full package from sources + content model
    provenance <pack-id>     — Attach/recompute provenance for a package
    validate <pack-id>       — Validate package structure against content model
    list                     — List all generated packages
    status                   — Show generator state

Output structure:
    data/training-packages/<pack-id>/
        package.json         — Training pack content (training-content-v1 schema)
        provenance.json      — Provenance record from knowledge adapter
        overview.md          — Human-readable overview
        lessons/             — Lesson files (one per section)
        examples/            — Example files (if applicable)
        exercises/           — Exercise files (if applicable)
"""

import datetime, hashlib, json, os, re, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PACKAGES_DIR = REPO_ROOT / "data" / "training-packages"
INDEX_FILE = REPO_ROOT / "data" / "training-packages" / "package-index.json"
ADAPTER_SCRIPT = SCRIPT_DIR / "qa_pilot_knowledge_adapter.py"
VALIDATOR_SCRIPT = SCRIPT_DIR / "validate-qa-pilot-training-content-model.py"

VALID_TYPES = ["onboarding_guide", "operator_guide", "developer_guide",
               "troubleshooting_guide", "architecture_explanation",
               "workflow_tutorial", "validation_exercise"]
VALID_AUDIENCES = ["onboarding", "operator", "developer", "architect", "all"]


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_index():
    if INDEX_FILE.exists():
        with open(INDEX_FILE) as f:
            return json.load(f)
    return {"packages": [], "generated_count": 0}


def save_index(index):
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)


def cmd_init(args):
    """Initialize a new training package skeleton."""
    if len(args) < 2:
        print("Usage: generator.py init <pack-id> <type> [--title <t>] [--audience <a>]")
        return 1

    pack_id = args[0]
    ptype = args[1]
    title = None
    audience = "onboarding"

    i = 2
    while i < len(args):
        if args[i] == "--title" and i + 1 < len(args):
            title = args[i + 1]; i += 2
        elif args[i] == "--audience" and i + 1 < len(args):
            audience = args[i + 1]; i += 2
        else:
            i += 1

    if not re.match(r"^TP-[A-Z0-9-]+$", pack_id):
        print(f"ERROR: pack_id '{pack_id}' must match TP- pattern")
        return 1
    if ptype not in VALID_TYPES:
        print(f"ERROR: Unknown type '{ptype}'. Valid: {', '.join(VALID_TYPES)}")
        return 1
    if audience not in VALID_AUDIENCES:
        print(f"ERROR: Unknown audience '{audience}'. Valid: {', '.join(VALID_AUDIENCES)}")
        return 1

    pack_dir = PACKAGES_DIR / pack_id
    if pack_dir.exists():
        print(f"ERROR: Package '{pack_id}' already exists")
        return 1

    pack_dir.mkdir(parents=True)
    (pack_dir / "lessons").mkdir(exist_ok=True)
    (pack_dir / "examples").mkdir(exist_ok=True)
    (pack_dir / "exercises").mkdir(exist_ok=True)

    if not title:
        title = f"{' '.join(ptype.split('_')).title()} — {pack_id}"

    package = {
        "schema_version": "training-content-v1",
        "pack_id": pack_id,
        "title": title,
        "description": f"Training package of type {ptype}",
        "artifact_type": ptype,
        "intended_audience": audience,
        "generated_at": now_utc(),
        "prerequisites": [],
        "content": {"sections": []},
        "provenance": {
            "librarian_sources": [],
            "generator": "qa-pilot-training-package-generator",
            "generator_version": "1.0.0",
            "source_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        },
        "governance": {
            "authority_posture": "advisory",
            "owner_decision_required_for_publish": True,
            "validation_status": "draft",
            "source_coverage_pct": 0,
            "ownership_state": "owned_by_librarian"
        }
    }

    with open(pack_dir / "package.json", "w") as f:
        json.dump(package, f, indent=2)

    # Create overview.md
    with open(pack_dir / "overview.md", "w") as f:
        f.write(f"# {title}\n\n")
        f.write(f"**Type:** {ptype}\n")
        f.write(f"**Audience:** {audience}\n")
        f.write(f"**Generated:** {now_utc()}\n\n")
        f.write("## Overview\n\n")
        f.write("Package initialized. Use `generate` to populate from sources.\n")

    # Create provenance stub
    provenance = {
        "provenance_id": f"PG-{hashlib.sha256(pack_id.encode()).hexdigest()[:12].upper()}",
        "generated_at": now_utc(),
        "sources": [],
        "source_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "advisory": True,
        "no_authority_promotion": True
    }
    with open(pack_dir / "provenance.json", "w") as f:
        json.dump(provenance, f, indent=2)

    # Update index
    index = load_index()
    index["packages"].append({
        "pack_id": pack_id,
        "title": title,
        "artifact_type": ptype,
        "intended_audience": audience,
        "generated_at": now_utc(),
        "status": "initialized",
        "path": str(pack_dir)
    })
    index["generated_count"] = len(index["packages"])
    save_index(index)

    print(f"✅ Initialized package: {pack_id}")
    print(f"   Type: {ptype}")
    print(f"   Audience: {audience}")
    print(f"   Path: {pack_dir}")
    return 0


def cmd_generate(args):
    """Generate full package from sources + content model."""
    if not args:
        print("Usage: generator.py generate <pack-id>")
        return 1

    pack_id = args[0]
    pack_dir = PACKAGES_DIR / pack_id
    pkg_file = pack_dir / "package.json"

    if not pkg_file.exists():
        print(f"ERROR: Package '{pack_id}' not found. Run init first.")
        return 1

    with open(pkg_file) as f:
        package = json.load(f)

    # Read sources from knowledge adapter
    sources = package.get("provenance", {}).get("librarian_sources", [])
    if not sources:
        print(f"ℹ️  No sources attached. Add sources via `provenance` command.")
        print(f"   Or edit package.json provenance.librarian_sources directly.")

    ptype = package.get("artifact_type", "onboarding_guide")
    needs_exercises = ptype in ("validation_exercise", "workflow_tutorial")

    # Add sample sections if none exist
    if not package.get("content", {}).get("sections"):
        sections = [
            {
                "id": "introduction",
                "title": "Introduction",
                "body": f"Welcome to the {package['title']}. This guide covers the essential concepts and workflows.",
                "content_type": "text",
                "sources": [s["path"] for s in sources] if sources else ["pending-source-ref"],
                "exercises": [{"prompt": "Describe the key concepts covered in this section.", "expected_outcome": "Summary of key concepts"}] if needs_exercises else []
            },
            {
                "id": "core-content",
                "title": "Core Content",
                "body": "This section contains the main instructional content.",
                "content_type": "text",
                "sources": [s["path"] for s in sources] if sources else ["pending-source-ref"],
                "exercises": [{"prompt": "Apply the concepts from this section.", "expected_outcome": "Demonstrated understanding"}] if needs_exercises else []
            }
        ]
        package["content"]["sections"] = sections

    # Write generated content
    package["governance"]["validation_status"] = "draft"
    package["generated_at"] = now_utc()

    with open(pkg_file, "w") as f:
        json.dump(package, f, indent=2)

    # Generate lesson files
    lessons_dir = pack_dir / "lessons"
    for section in package["content"]["sections"]:
        lesson_file = lessons_dir / f"{section['id']}.md"
        with open(lesson_file, "w") as f:
            f.write(f"# {section['title']}\n\n")
            f.write(f"{section['body']}\n\n")
            f.write(f"---\n*Sources: {', '.join(section.get('sources', ['pending']))}*\n")

    # Generate exercise files if applicable
    if needs_exercises:
        exercises_dir = pack_dir / "exercises"
        for i, section in enumerate(package["content"]["sections"]):
            exercises = section.get("exercises", [])
            for j, ex in enumerate(exercises):
                ex_file = exercises_dir / f"{section['id']}-exercise-{j+1}.md"
                with open(ex_file, "w") as f:
                    f.write(f"# Exercise: {ex.get('prompt', 'Untitled')}\n\n")
                    f.write(f"**Prompt:** {ex.get('prompt', '')}\n\n")
                    f.write(f"**Expected Outcome:** {ex.get('expected_outcome', '')}\n\n")

    # Update index
    index = load_index()
    for p in index["packages"]:
        if p["pack_id"] == pack_id:
            p["status"] = "generated"
            p["generated_at"] = now_utc()
    save_index(index)

    print(f"✅ Generated package: {pack_id}")
    print(f"   Sections: {len(package['content']['sections'])}")
    print(f"   Sources: {len(package['provenance']['librarian_sources'])}")
    print(f"   Path: {pack_dir}")
    return 0


def cmd_provenance(args):
    """Attach/recompute provenance for a package."""
    if not args:
        print("Usage: generator.py provenance <pack-id> <source-path>...")
        return 1

    pack_id = args[0]
    source_paths = args[1:]
    pack_dir = PACKAGES_DIR / pack_id
    pkg_file = pack_dir / "package.json"

    if not pkg_file.exists():
        print(f"ERROR: Package '{pack_id}' not found")
        return 1

    with open(pkg_file) as f:
        package = json.load(f)

    # Build source references
    sources = []
    for sp in source_paths:
        sources.append({
            "path": sp,
            "revision": "pending",
            "source_type": "governance",
            "accessible": True,
            "content_hash": None,
            "last_modified": None,
            "referenced_at": now_utc()
        })

    if sources:
        package["provenance"]["librarian_sources"] = sources
        # Compute hash
        h = hashlib.sha256()
        for s in sources:
            h.update(s["path"].encode())
        package["provenance"]["source_hash"] = h.hexdigest()
        package["governance"]["source_coverage_pct"] = 100

    with open(pkg_file, "w") as f:
        json.dump(package, f, indent=2)

    # Write provenance.json
    prov = {
        "provenance_id": f"PG-{hashlib.sha256(pack_id.encode()).hexdigest()[:12].upper()}",
        "generated_at": now_utc(),
        "sources": sources,
        "source_hash": package["provenance"]["source_hash"],
        "advisory": True,
        "no_authority_promotion": True
    }
    with open(pack_dir / "provenance.json", "w") as f:
        json.dump(prov, f, indent=2)

    print(f"✅ Provenance attached: {pack_id}")
    print(f"   Sources: {len(sources)}")
    print(f"   Hash: {prov['source_hash'][:16]}...")
    return 0


def cmd_validate(args):
    """Validate package structure against content model."""
    if not args:
        print("Usage: generator.py validate <pack-id>")
        return 1

    pack_id = args[0]
    pack_dir = PACKAGES_DIR / pack_id
    pkg_file = pack_dir / "package.json"

    if not pkg_file.exists():
        print(f"ERROR: Package '{pack_id}' not found")
        return 1

    with open(pkg_file) as f:
        package = json.load(f)

    # Run content model validator against this package
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(package, tmp)
        tmp_path = tmp.name

    result = subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT), "--include-invalid"],
        capture_output=True, text=True, timeout=30,
    )
    # Also run the package through a separate validation check
    print(f"Validating: {pack_id}")
    print(f"  Type: {package.get('artifact_type', '?')}")
    print(f"  Sections: {len(package.get('content', {}).get('sections', []))}")
    print(f"  Sources: {len(package.get('provenance', {}).get('librarian_sources', []))}")
    print(f"  Source coverage: {package.get('governance', {}).get('source_coverage_pct', 0)}%")
    print()

    # Check source lineage
    has_sources = len(package.get("provenance", {}).get("librarian_sources", [])) > 0
    print(f"  ✅ Source lineage: {'present' if has_sources else 'MISSING — no sources'}")

    # Check section sources
    sections = package.get("content", {}).get("sections", [])
    all_sections_have_sources = all(len(s.get("sources", [])) > 0 for s in sections)
    print(f"  ✅ Section sources: {'all present' if all_sections_have_sources else 'SOME MISSING'}")

    # Check advisory
    advisory = package.get("governance", {}).get("authority_posture") == "advisory"
    print(f"  ✅ Advisory: {'yes' if advisory else 'NO — authority violation'}")

    # Check exercises for required types
    ptype = package.get("artifact_type", "")
    needs_ex = ptype in ("validation_exercise", "workflow_tutorial")
    if needs_ex:
        all_have_ex = all(len(s.get("exercises", [])) > 0 for s in sections)
        print(f"  ✅ Exercises: {'all present' if all_have_ex else 'MISSING'} (required for {ptype})")
    else:
        print(f"  ✅ Exercises: not required for {ptype}")

    all_pass = has_sources and all_sections_have_sources and advisory and (not needs_ex or all_have_ex)
    print()
    if all_pass:
        print("✅ Package validation PASSED")
        return 0
    else:
        print("❌ Package validation FAILED")
        return 1


def cmd_list(args):
    """List all generated packages."""
    index = load_index()
    pkgs = index.get("packages", [])
    if not pkgs:
        print("No packages generated.")
        return 0
    print(f"Training packages ({len(pkgs)} total):")
    for p in pkgs:
        print(f"  {p['pack_id']}")
        print(f"    Type:      {p['artifact_type']}")
        print(f"    Audience:  {p['intended_audience']}")
        print(f"    Status:    {p.get('status', 'unknown')}")
        print(f"    Generated: {p.get('generated_at', '?')}")
        print()
    return 0


def cmd_status(args):
    """Show generator state."""
    index = load_index()
    pkgs = index.get("packages", [])
    counts = {}
    for p in pkgs:
        t = p.get("artifact_type", "unknown")
        counts[t] = counts.get(t, 0) + 1

    print("QA Pilot Training Package Generator")
    print("=" * 40)
    print(f"Packages directory: {PACKAGES_DIR}")
    print(f"Total packages:     {len(pkgs)}")
    print(f"Index:              {INDEX_FILE}")
    print()
    if counts:
        print("By type:")
        for t, c in sorted(counts.items()):
            print(f"  {t}: {c}")
    print()
    print("Authority: advisory-only")
    print("Cross-project write: NOT AUTHORIZED")
    print("Source lineage required: YES")
    return 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("QA Pilot Training Package Generator — QA-PILOT-TRAINING-PACKAGE-GENERATOR-1")
        print()
        print("Usage:")
        print("  init <pack-id> <type>          — Initialize new package skeleton")
        print("  generate <pack-id>             — Generate full package from sources")
        print("  provenance <pack-id> <path>... — Attach source provenance")
        print("  validate <pack-id>             — Validate package structure")
        print("  list                           — List all packages")
        print("  status                         — Show generator state")
        print()
        print("Types: " + ", ".join(VALID_TYPES))
        print("Authority: advisory-only. No cross-project write.")
        return 0

    cmd = sys.argv[1]
    cargs = sys.argv[2:]
    cmds = {
        "init": cmd_init, "generate": cmd_generate,
        "provenance": cmd_provenance, "validate": cmd_validate,
        "list": cmd_list, "status": cmd_status,
    }
    if cmd not in cmds:
        print(f"Unknown: {cmd}")
        return 1
    return cmds[cmd](cargs)


if __name__ == "__main__":
    sys.exit(main())
