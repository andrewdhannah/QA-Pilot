#!/usr/bin/env python3
"""Project training package export — Sprint 9"""
import json, shutil, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PACKAGES_DIR = REPO_ROOT / "data" / "training-packages"
EXPORT_DIR = REPO_ROOT / "data" / "training-exports"

def cmd_export(args):
    if len(args) < 2: print("Usage: export.py <pack-id> <target-project>"); return 1
    pid, target = args[0], args[1]
    src = PACKAGES_DIR / pid
    if not (src / "package.json").exists(): print(f"Package '{pid}' not found"); return 1
    dst = EXPORT_DIR / target / pid
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)
    print(f"Exported {pid} → {target}"); return 0

def cmd_list_exports(args):
    if not EXPORT_DIR.exists(): print("No exports."); return 0
    for tgt in sorted(EXPORT_DIR.iterdir()):
        if tgt.is_dir():
            pkgs = [d.name for d in tgt.iterdir() if d.is_dir()]
            print(f"  {tgt.name}: {', '.join(pkgs) if pkgs else '(empty)'}")
    return 0

def cmd_status(args):
    exports = sum(1 for _ in EXPORT_DIR.rglob("package.json")) if EXPORT_DIR.exists() else 0
    print(f"Training exports: {exports}"); print("Authority: advisory-only"); print("Owner apply required: YES"); return 0

def main():
    cmds = {"export": cmd_export, "list": cmd_list_exports, "status": cmd_status}
    if len(sys.argv) < 2: print("Commands: export, list, status"); return 1
    c = sys.argv[1]
    if c in cmds: return cmds[c](sys.argv[2:])
    print(f"Unknown: {c}"); return 1

if __name__ == "__main__": sys.exit(main())
