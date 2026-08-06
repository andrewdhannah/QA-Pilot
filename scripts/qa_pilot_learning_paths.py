#!/usr/bin/env python3
"""Learning paths creator — Sprint 7"""
import json, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PATHS_FILE = REPO_ROOT / "data" / "training-packages" / "learning-paths.json"

def load_paths():
    if PATHS_FILE.exists():
        with open(PATHS_FILE) as f: return json.load(f)
    return {"paths": []}

def save_paths(data):
    PATHS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PATHS_FILE, "w") as f: json.dump(data, f, indent=2)

def cmd_create(args):
    if len(args) < 2:
        print("Usage: learning_paths.py create <path-id> <title>")
        return 1
    pid, title = args[0], args[1]
    data = load_paths()
    if any(p["id"] == pid for p in data["paths"]):
        print(f"Path '{pid}' already exists"); return 1
    data["paths"].append({"id": pid, "title": title, "steps": [], "created_at": __import__("datetime").datetime.now().isoformat()})
    save_paths(data)
    print(f"Created learning path: {pid}"); return 0

def cmd_add_step(args):
    if len(args) < 3:
        print("Usage: add-step <path-id> <pack-id> <order>")
        return 1
    pid, pkid, order = args[0], args[1], int(args[2])
    data = load_paths()
    for p in data["paths"]:
        if p["id"] == pid:
            p["steps"].append({"pack_id": pkid, "order": order})
            save_paths(data)
            print(f"Added {pkid} to {pid}"); return 0
    print(f"Path '{pid}' not found"); return 1

def cmd_list(args):
    data = load_paths()
    if not data["paths"]: print("No learning paths."); return 0
    for p in data["paths"]:
        print(f"  {p['id']}: {p['title']} ({len(p['steps'])} steps)"); return 0

def main():
    cmds = {"create": cmd_create, "add-step": cmd_add_step, "list": cmd_list}
    if len(sys.argv) < 2: print("Commands: create, add-step, list"); return 1
    c = sys.argv[1]
    if c in cmds: return cmds[c](sys.argv[2:])
    print(f"Unknown: {c}"); return 1

if __name__ == "__main__": sys.exit(main())
