#!/usr/bin/env python3
"""Validator — QA-PILOT-OWNER-DECISION-RECEIPT-STARTUP-SURFACE-1"""
import json, sys
from pathlib import Path
SD = Path(__file__).resolve().parent
S = SD / "qa_pilot_pipeline_startup_surface_odr.py"

def run(*a):
    import subprocess as sp
    try:
        r = sp.run([sys.executable, str(S)] + list(a), capture_output=True, text=True, timeout=15)
        return (json.loads(r.stdout) if r.stdout else {}, r.returncode)
    except Exception as e: return ({"error": str(e)}, 1)

c = lambda n, f, d: (n, f, d)

def do_checks():
    d, _ = run()
    b = d.get("base_pipeline", {})
    o = d.get("odr_layer", {})
    checks = [
        ("OS-1", d.get("advisory_only") is True, f"advisory={d.get('advisory_only')}"),
        ("OS-2", d.get("custody") == "qa-pilot-local", f"custody={d.get('custody')}"),
        ("OS-3", bool(b.get("sealed_head")), f"head={b.get('sealed_head')}"),
        ("OS-4", o.get("status") in ("active", "empty"), f"status={o.get('status')}"),
        ("OS-5", isinstance(o.get("total_receipts"), int), f"total={o.get('total_receipts')}"),
        ("OS-6", "latest_receipt" in o, "has latest_receipt"),
        ("OS-7", "or_linkage" in o, "has or_linkage"),
    ]
    ap = True
    for n, p, m in checks:
        print(f"  {'✅' if p else '❌'} {n}: {m}")
        if not p: ap = False
    print(f"\n{'✅ ALL CHECKS PASS' if ap else '❌ SOME FAILED'}")
    return 0 if ap else 1

if __name__ == "__main__":
    sys.exit(do_checks())
