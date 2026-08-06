#!/usr/bin/env python3
"""Training simulation expansion — Sprint 8. Builds on QA-PILOT-LOCAL-TRAINING-SIM-1."""
import json, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCENARIOS_FILE = REPO_ROOT / "data" / "training-packages" / "sim-scenarios.json"

def load(): return json.loads(SCENARIOS_FILE.read_text()) if SCENARIOS_FILE.exists() else {"scenarios": []}
def save(d): SCENARIOS_FILE.parent.mkdir(parents=True, exist_ok=True); SCENARIOS_FILE.write_text(json.dumps(d, indent=2))

def cmd_create(args):
    if len(args) < 3: print("Usage: sim-expansion.py create <id> <pack-id> <title>"); return 1
    sid, pid, title = args[0], args[1], args[2]
    d = load()
    if any(s["id"] == sid for s in d["scenarios"]): print(f"Scenario '{sid}' exists"); return 1
    d["scenarios"].append({"id": sid, "pack_id": pid, "title": title, "exercises": [], "created_at": __import__("datetime").datetime.now().isoformat()})
    save(d); print(f"Created scenario: {sid}"); return 0

def cmd_add_exercise(args):
    if len(args) < 3: print("Usage: add-exercise <scenario-id> <prompt> <expected>"); return 1
    sid, prompt, expected = args[0], args[1], args[2]
    d = load()
    for s in d["scenarios"]:
        if s["id"] == sid:
            s["exercises"].append({"prompt": prompt, "expected_outcome": expected})
            save(d); print(f"Exercise added to {sid}"); return 0
    print(f"Scenario '{sid}' not found"); return 1

def cmd_list(args):
    d = load()
    if not d["scenarios"]: print("No scenarios."); return 0
    for s in d["scenarios"]: print(f"  {s['id']}: {s['title']} (pack={s['pack_id']}, {len(s['exercises'])} exercises)"); return 0

def cmd_status(args):
    d = load()
    print(f"Sim scenarios: {len(d['scenarios'])}"); print("Authority: advisory-only"); return 0

def main():
    cmds = {"create": cmd_create, "add-exercise": cmd_add_exercise, "list": cmd_list, "status": cmd_status}
    if len(sys.argv) < 2: print("Commands: create, add-exercise, list, status"); return 1
    c = sys.argv[1]
    if c in cmds: return cmds[c](sys.argv[2:])
    print(f"Unknown: {c}"); return 1

if __name__ == "__main__": sys.exit(main())
