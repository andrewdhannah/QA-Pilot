#!/usr/bin/env python3
"""
Training System MCP Surface — Sprint 10
Bounded read-only MCP access: request package, query status, retrieve artifacts.
No Librarian mutation, no content approval, no autonomous publishing.
"""
import json, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PACKAGES_DIR = REPO_ROOT / "data" / "training-packages"

def cmd_request(args):
    if not args: print("Usage: mcp-surface.py request <pack-id>"); return 1
    pid = args[0]
    pkg_file = PACKAGES_DIR / pid / "package.json"
    if not pkg_file.exists(): print(f"Package '{pid}' not found"); return 1
    pkg = json.loads(pkg_file.read_text())
    print(json.dumps({
        "pack_id": pid, "title": pkg.get("title"), "type": pkg.get("artifact_type"),
        "audience": pkg.get("intended_audience"), "status": pkg.get("governance", {}).get("validation_status"),
        "source_count": len(pkg.get("provenance", {}).get("librarian_sources", [])),
        "advisory": True
    }, indent=2)); return 0

def cmd_status(args):
    count = len([d for d in PACKAGES_DIR.iterdir() if d.is_dir() and (d / "package.json").exists()]) if PACKAGES_DIR.exists() else 0
    print(json.dumps({"packages_available": count, "authority": "advisory-only", "read_only": True, "cross_project_write": "NOT AUTHORIZED"}, indent=2))
    return 0

def cmd_retrieve(args):
    if len(args) < 2: print("Usage: mcp-surface.py retrieve <pack-id> <file>"); return 1
    pid, fname = args[0], args[1]
    f = PACKAGES_DIR / pid / fname
    if not f.exists(): print(f"File '{fname}' not found in {pid}"); return 1
    print(f.read_text()); return 0

def main():
    cmds = {"request": cmd_request, "status": cmd_status, "retrieve": cmd_retrieve}
    if len(sys.argv) < 2: print("Commands: request, status, retrieve"); return 1
    c = sys.argv[1]
    if c in cmds: return cmds[c](sys.argv[2:])
    print(f"Unknown: {c}"); return 1

if __name__ == "__main__": sys.exit(main())
