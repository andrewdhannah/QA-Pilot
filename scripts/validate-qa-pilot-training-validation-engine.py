#!/usr/bin/env python3
"""Validator for Training Validation Engine — VE checks"""
import json, os, sys
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
ENGINE = SCRIPT_DIR / "qa_pilot_training_validation_engine.py"
GOV_DOC = SCRIPT_DIR.parent / "docs" / "governance" / "QA-PILOT-TRAINING-VALIDATION-ENGINE.md"

def ve1():
    import subprocess; r = subprocess.run([sys.executable, str(ENGINE), "--help"], capture_output=True, text=True, timeout=10)
    return r.returncode == 0, f"exit={r.returncode}"
def ve2():
    import subprocess; r = subprocess.run([sys.executable, str(ENGINE), "status"], capture_output=True, text=True, timeout=10)
    return r.returncode == 0 and "advisory-only" in r.stdout, f"exit={r.returncode}"
def ve3():
    return ENGINE.exists(), str(ENGINE)
def ve4():
    return GOV_DOC.exists(), str(GOV_DOC)
def ve5():
    import subprocess; r = subprocess.run([sys.executable, str(ENGINE), "check", "nonexistent"], capture_output=True, text=True, timeout=10)
    return r.returncode != 0, f"exit={r.returncode}"

CHECKS = [("VE-1", ve1, "CLI works"), ("VE-2", ve2, "Status reports advisory"), ("VE-3", ve3, "Engine exists"), ("VE-4", ve4, "Gov doc exists"), ("VE-5", ve5, "Rejects nonexistent")]

def main():
    import subprocess
    if "--list-rules" in sys.argv:
        for rid, _, d in CHECKS: print(f"  {rid}: {d}")
        return 0
    all_pass = True
    for rid, func, desc in CHECKS:
        passed, detail = func()
        p = "✅" if passed else "❌"
        print(f"  {p} {rid}: {detail}")
        if not passed: all_pass = False
    print(f"\n{'✅ ALL PASS' if all_pass else '❌ SOME FAILED'}")
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
