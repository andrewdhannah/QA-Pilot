#!/usr/bin/env python3
"""Validator for Training Package Generator — PG-1 through PG-6"""
import json, os, re, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
GENERATOR = SCRIPT_DIR / "qa_pilot_training_package_generator.py"
GOV_DOC = REPO_ROOT / "docs" / "governance" / "QA-PILOT-TRAINING-PACKAGE-GENERATOR.md"

def pg1():
    """PG-1: Generator script exists"""
    return GENERATOR.exists(), str(GENERATOR)

def pg2():
    """PG-2: Generator --help works"""
    import subprocess
    r = subprocess.run([sys.executable, str(GENERATOR), "--help"], capture_output=True, text=True, timeout=10)
    return r.returncode == 0, f"exit={r.returncode}"

def pg3():
    """PG-3: Generator init creates package"""
    import subprocess, shutil
    test_id = "TP-TEST-PG3"
    pkg_dir = REPO_ROOT / "data" / "training-packages" / test_id
    if pkg_dir.exists(): shutil.rmtree(pkg_dir)

    r = subprocess.run([sys.executable, str(GENERATOR), "init", test_id, "onboarding_guide", "--title", "Test Package"], capture_output=True, text=True, timeout=10)
    created = pkg_dir.exists() and (pkg_dir / "package.json").exists()
    if pkg_dir.exists(): shutil.rmtree(pkg_dir)
    return created and r.returncode == 0, f"exit={r.returncode}, created={created}"

def pg4():
    """PG-4: Generator list works"""
    import subprocess
    r = subprocess.run([sys.executable, str(GENERATOR), "list"], capture_output=True, text=True, timeout=10)
    return r.returncode == 0, f"exit={r.returncode}"

def pg5():
    """PG-5: Generator status works"""
    import subprocess
    r = subprocess.run([sys.executable, str(GENERATOR), "status"], capture_output=True, text=True, timeout=10)
    return r.returncode == 0, f"exit={r.returncode}"

def pg6():
    """PG-6: Governance doc exists"""
    return GOV_DOC.exists(), str(GOV_DOC)

CHECKS = [("PG-1", pg1), ("PG-2", pg2), ("PG-3", pg3), ("PG-4", pg4), ("PG-5", pg5), ("PG-6", pg6)]

def main():
    if "--list-rules" in sys.argv:
        for rid, func in CHECKS:
            desc = func.__doc__ or ""
            print(f"  {rid}: {desc}")
        return 0

    all_pass = True
    for rid, func in CHECKS:
        passed, detail = func()
        p = "✅" if passed else "❌"
        print(f"  {p} {rid}: {detail}")
        if not passed:
            all_pass = False
    print()
    print(f"{'✅ ALL CHECKS PASS' if all_pass else '❌ SOME CHECKS FAILED'}")
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
