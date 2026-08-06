#!/usr/bin/env python3
"""
QA Pilot Owner Review Decision Receipt — QA-PILOT-OWNER-REVIEW-DECISION-RECEIPT-1

Records Owner decisions from the review packet (#41) as bounded advisory artifacts.

Usage:
    python3 scripts/qa_pilot_owner_review_decision_receipt.py record <option> [--note "text"]
    python3 scripts/qa_pilot_owner_review_decision_receipt.py list [--limit N]
    python3 scripts/qa_pilot_owner_review_decision_receipt.py read <receipt_id>
    python3 scripts/qa_pilot_owner_review_decision_receipt.py status
    python3 scripts/qa_pilot_owner_review_decision_receipt.py clear
"""

import argparse, hashlib, json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_DIR = REPO_ROOT / "data" / "owner-decisions"
INDEX_FILE = DATA_DIR / "decision-index.json"
ADVISORY_NOTICE = (
    "This decision receipt is advisory-only. It records an Owner decision for "
    "audit trail but does not itself approve, seal, merge, or assert production readiness."
)
VALID_OPTIONS = ["accept", "authorize", "defer", "reject"]
RECEIPT_PATTERN = re.compile(r"^ODR-\d{8}-")

ODR_RULES = {
    "ODR-1": "Records only valid options (accept/authorize/defer/reject)",
    "ODR-2": "Receipts include advisory: true",
    "ODR-3": "Receipts include custody: qa-pilot-local",
    "ODR-4": "Receipts do not create seal/repair/mutation authority",
    "ODR-5": "Record is read-only after creation",
    "ODR-6": "Duplicate receipts are not created",
    "ODR-7": "Store index is QA Pilot-local",
}

def load_index():
    if not INDEX_FILE.exists():
        return {"store": "qap-odr-v1", "receipts": {}, "advisory_notice": ADVISORY_NOTICE}
    return json.loads(INDEX_FILE.read_text())

def save_index(idx):
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(idx, indent=2) + "\n")

def advisory(**kw):
    r = {"advisory_only": True, "source_project": "qa-pilot", "custody": "qa-pilot-local",
         "advisory_notice": ADVISORY_NOTICE, "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    r.update(kw); return r

def cmd_record(args):
    option = args.option
    if option not in VALID_OPTIONS:
        return advisory(tool="odr_record", success=False, error=f"Invalid option '{option}'. Valid: {VALID_OPTIONS}")

    idx = load_index()
    ts = datetime.now(timezone.utc)
    date_str = ts.strftime("%Y%m%d")
    short_hash = hashlib.md5((option + str(ts)).encode()).hexdigest()[:6]
    receipt_id = f"ODR-{date_str}-{short_hash}"

    if receipt_id in idx.get("receipts", {}):
        return advisory(tool="odr_record", success=False, receipt_id=receipt_id, error="Duplicate receipt_id")

    receipt = {
        "receipt_id": receipt_id,
        "decision": option,
        "owner_note": args.note or "",
        "advisory": True,
        "custody": "qa-pilot-local",
        "librarian_mutation_authority": False,
        "recorded_at": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_review_packet": "#41 QA-PILOT-PIPELINE-OWNER-REVIEW-PACKET-1",
    }

    store_path = DATA_DIR / f"{receipt_id}.json"
    store_path.parent.mkdir(parents=True, exist_ok=True)
    store_path.write_text(json.dumps(receipt, indent=2) + "\n")

    idx.setdefault("receipts", {})[receipt_id] = {
        "receipt_id": receipt_id, "decision": option, "advisory": True,
        "recorded_at": receipt["recorded_at"], "store_path": str(store_path),
    }
    save_index(idx)

    return advisory(tool="odr_record", success=True, receipt_id=receipt_id, decision=option, receipt=receipt)

def cmd_list(args):
    idx = load_index()
    all_r = list(idx.get("receipts", {}).values())[:args.limit]
    return advisory(tool="odr_list", success=True, total=len(idx.get("receipts", {})), receipts=all_r)

def cmd_read(args):
    idx = load_index()
    rid = args.receipt_id
    if rid not in idx.get("receipts", {}):
        return advisory(tool="odr_read", success=False, receipt_id=rid, found=False, error="Not found")
    sp = Path(idx["receipts"][rid].get("store_path", ""))
    if not sp.exists():
        return advisory(tool="odr_read", success=False, receipt_id=rid, found=False, error="File missing")
    return advisory(tool="odr_read", success=True, receipt_id=rid, found=True, receipt=json.loads(sp.read_text()))

def cmd_status(args):
    idx = load_index(); rs = idx.get("receipts", {})
    by_opt = {}
    for r in rs.values():
        o = r.get("decision", "?"); by_opt[o] = by_opt.get(o, 0) + 1
    return advisory(tool="odr_status", success=True, total=len(rs), by_decision=by_opt)

def cmd_clear(args):
    idx = load_index(); c = len(idx.get("receipts", {}))
    for r in idx.get("receipts", {}).values():
        Path(r.get("store_path", "")).unlink(missing_ok=True)
    idx["receipts"] = {}; save_index(idx)
    return advisory(tool="odr_clear", success=True, cleared=c)

def main():
    p = argparse.ArgumentParser(description="QA Pilot Owner Decision Receipt")
    s = p.add_subparsers(dest="cmd", required=True)
    rp = s.add_parser("record"); rp.add_argument("option", choices=VALID_OPTIONS); rp.add_argument("--note", default="")
    lp = s.add_parser("list"); lp.add_argument("--limit", type=int, default=50)
    rdp = s.add_parser("read"); rdp.add_argument("receipt_id")
    s.add_parser("status"); s.add_parser("clear")
    a = p.parse_args()

    if a.cmd == "record": r = cmd_record(a)
    elif a.cmd == "list": r = cmd_list(a)
    elif a.cmd == "read": r = cmd_read(a)
    elif a.cmd == "status": r = cmd_status(a)
    elif a.cmd == "clear": r = cmd_clear(a)
    else: r = advisory(success=False, error=f"Unknown: {a.cmd}")
    print(json.dumps(r, indent=2))
    sys.exit(0 if r.get("success", False) else 1)

if __name__ == "__main__":
    main()
