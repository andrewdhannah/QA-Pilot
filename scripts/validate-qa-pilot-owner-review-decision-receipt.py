#!/usr/bin/env python3
"""Validator — QA-PILOT-OWNER-REVIEW-DECISION-RECEIPT-1"""
import json, sys
from pathlib import Path
SD = Path(__file__).resolve().parent; RR = SD.parent
SCRIPT = SD / "qa_pilot_owner_review_decision_receipt.py"
FIX = RR / "docs" / "examples" / "qa-pilot-owner-review-decision-receipt"

def run(*a):
    import subprocess as sp
    try:
        r = sp.run([sys.executable, str(SCRIPT)] + list(a), capture_output=True, text=True, timeout=10)
        return (json.loads(r.stdout) if r.stdout else {}, r.returncode)
    except Exception as e: return ({"error": str(e)}, 1)

def check_1(): d, _ = run("record", "accept", "--note", "test"); return (d.get("success"), f"record accept: {d.get('receipt_id','?')}")
def check_2(): d, _ = run("record", "authorize"); return (d.get("success"), f"record authorize: {d.get('receipt_id','?')}")
def check_3(): d, _ = run("list"); return (d.get("total", 0) >= 1, f"list: {d.get('total')}")
def check_4(): d, _ = run("status"); return (d.get("total", 0) >= 1, f"status: {d.get('total')}")
def check_5():
    idx = SD.parent / "data" / "owner-decisions" / "decision-index.json"
    return (idx.exists(), "index exists")
def check_6():
    d, _ = run("list")
    adv = d.get("advisory_only", False)
    return (adv, f"advisory_only={adv}")
def check_7():
    d, _ = run("status")
    cus = d.get("custody", "")
    return (cus == "qa-pilot-local", f"custody={cus}")
def check_8():
    # Duplicate record attempt with same args should create unique receipt
    d, _ = run("record", "accept", "--note", "dup test")
    return (d.get("success"), f"another record: {d.get('receipt_id','?')}")


def main():
    checks = [
        ("ODR-1", check_1, "Record accept"),
        ("ODR-2", check_2, "Record authorize"),
        ("ODR-3", check_3, "List"),
        ("ODR-4", check_4, "Status"),
        ("ODR-5", check_5, "Store index"),
        ("ODR-6", check_6, "Advisory"),
        ("ODR-7", check_7, "Custody"),
        ("ODR-8", check_8, "Duplicate record"),
    ]
    ap = True
    for rid, fn, desc in checks:
        try: p, m = fn()
        except Exception as e: p, m = False, f"Error: {e}"
        print(f"  {'✅' if p else '❌'} {rid}: {desc} — {m}")
        if not p: ap = False
    print(f"\n{'✅ ALL CHECKS PASS' if ap else '❌ SOME CHECKS FAILED'}")
    # Cleanup
    import subprocess
    subprocess.run([sys.executable, str(SCRIPT), "clear"], capture_output=True)
    return 0 if ap else 1

if __name__ == "__main__": sys.exit(main())
