#!/usr/bin/env python3
"""
Sync training packages to browser-compatible localStorage format.
Produces a JSON file that can be loaded into the browser via Developer Tools
or served alongside the static HTML assets.
"""
import json, os, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PACKAGES_DIR = REPO_ROOT / "data" / "training-packages"
EXPORT_DIR = REPO_ROOT / "data" / "training-exports"

def main():
    output = {}

    if PACKAGES_DIR.exists():
        for pkg_dir in sorted(PACKAGES_DIR.iterdir()):
            pkg_file = pkg_dir / "package.json"
            if pkg_file.exists():
                pkg = json.loads(pkg_file.read_text())
                pid = pkg.get("pack_id", pkg_dir.name)
                output[pid] = {
                    "title": pkg.get("title", pid),
                    "description": pkg.get("description", ""),
                    "artifact_type": pkg.get("artifact_type", ""),
                    "content": pkg.get("content", {"sections": []}),
                    "governance": pkg.get("governance", {}),
                    "generated_at": pkg.get("generated_at", "")
                }

    # Write browser load file
    output_file = EXPORT_DIR / "browser-content-data.json"
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Synced {len(output)} package(s) to {output_file}")
    print()
    for pid, data in output.items():
        sections = len(data.get("content", {}).get("sections", []))
        print(f"  {pid}: {data['title'][:50]} ({sections} sections)")

    # Also write a compact version for direct localStorage injection
    # Format: qapilot_training_content JSON
    print()
    print("To load in browser:")
    print(f"  1. Open browser DevTools (F12)")
    print(f"  2. Go to Console tab")
    print(f"  3. Paste the contents of the file below into localStorage:")
    print(f"     localStorage.setItem('qapilot_training_content', JSON.stringify({json.dumps(output)}))")
    print(f"  Or serve browser-content-data.json alongside the HTML and load via fetch()")

if __name__ == "__main__":
    sys.exit(main())
