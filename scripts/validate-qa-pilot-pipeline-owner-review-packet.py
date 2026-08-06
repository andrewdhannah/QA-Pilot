#!/usr/bin/env python3
"""
QA Pilot Pipeline Owner Review Packet Validator
— QA-PILOT-PIPELINE-OWNER-REVIEW-PACKET-1
"""
import json, sys
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PACKET_SCRIPT = SCRIPT_DIR / "qa_pilot_pipeline_owner_review_packet.py"
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-pipeline-owner-review-packet"
VALID = ["valid-review-packet.json"]
INVALID = ["invalid-authority-claim.json"]
ALL_FIX = sorted(set(VALID + INVALID))

def load_json(p):
    with open(p) as f:
        return json.load(f)
def run(*a):
    import subprocess
    try:
        r = subprocess.run([sys.executable, str(PACKET_SCRIPT)] + list(a), capture_output=True, text=True, timeout=20)
        return (json.loads(r.stdout) if r.stdout else {}, r.returncode)
    except Exception as e:
        return ({"error": str(e)}, 1)

def check_or_1(): d, _ = run(); return (d.get("advisory") is True, f"advisory={d.get('advisory')}")
def check_or_2(): d, _ = run(); return (d.get("custody") == "qa-pilot-local", f"custody={d.get('custody')}")
def check_or_3(): d, _ = run(); return (d.get("librarian_mutation_authority") is False, f"mutation={d.get('librarian_mutation_authority')}")
def check_or_4(): d, _ = run(); s = d.get("sections", {}); return (len(s) >= 4, f"{len(s)} sections")
def check_or_5(): d, _ = run(); o = d.get("owner_options", []); return (len(o) >= 3, f"{len(o)} options")
def check_or_6(): d, _ = run(); return ("review_id" in d, f"review_id={d.get('review_id','?')}")
def check_or_7():
    f = FIXTURES_DIR / "valid-review-packet.json"
    if not f.exists(): return (False, "fixture missing")
    d = load_json(str(f))
    return (d.get("advisory") is True and d.get("auto_repair") is False, "valid fixture ok")
def check_or_8():
    f = FIXTURES_DIR / "invalid-authority-claim.json"
    if not f.exists(): return (False, "fixture missing")
    d = load_json(str(f))
    return ("_authority_claim" in d, "authority claim detected")
def check_fix():
    e, a = set(ALL_FIX), set()
    if FIXTURES_DIR.exists():
        for f in FIXTURES_DIR.iterdir():
            if f.suffix == ".json": a.add(f.name)
    m = e - a
    return (len(m) == 0, f"All {len(e)} present" if not m else f"Missing {m}")

def main():
    checks = [
        ("OR-1", check_or_1, "Advisory-only"),
        ("OR-2", check_or_2, "Custody qa-pilot-local"),
        ("OR-3", check_or_3, "Zero mutation"),
        ("OR-4", check_or_4, "Pipeline sections"),
        ("OR-5", check_or_5, "Owner options"),
        ("OR-6", check_or_6, "Review ID"),
        ("OR-7", check_or_7, "Valid fixture"),
        ("OR-8", check_or_8, "Invalid fixture markers"),
        ("FIX", check_fix, "Fixture integrity"),
    ]
    ap = True
    for rid, fn, desc in checks:
        try:
            p, m = fn()
        except Exception as e:
            p, m = False, f"Error: {e}"
        print(f"  {'✅' if p else '❌'} {rid}: {desc} — {m}")
        if not p: ap = False
    fc = len(list(FIXTURES_DIR.glob("*.json"))) if FIXTURES_DIR.exists() else 0
    print(f"  📁 Fixtures: {fc} files")
    print(f"\n{'✅ ALL CHECKS PASS' if ap else '❌ SOME CHECKS FAILED'}")
    return 0 if ap else 1

if __name__ == "__main__":
    sys.exit(main())
