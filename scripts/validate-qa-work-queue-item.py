#!/usr/bin/env python3
"""Validator for QA Work Queue Item schema."""
import json, sys
VALID_STATUSES = ["OPEN","TRIAGED","APPROVED","IN_PROGRESS","FIXED","VERIFIED","CLOSED","REJECTED"]
RULES = [
    ("WQ-1", "item_id present", lambda d: bool(d.get("item_id"))),
    ("WQ-2", "status is valid", lambda d: d.get("status") in VALID_STATUSES),
    ("WQ-3", "diagnostic_ref present", lambda d: bool(d.get("diagnostic_ref"))),
    ("WQ-4", "provenance.advisory=true", lambda d: d.get("provenance",{}).get("advisory")==True),
    ("WQ-5", "provenance.no_authority_conferred=true", lambda d: d.get("provenance",{}).get("no_authority_conferred")==True),
]
def main():
    data = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
    all_pass = True
    for rid, desc, fn in RULES:
        passed = fn(data)
        print(f"  {'✅' if passed else '❌'} {rid}: {desc}")
        if not passed: all_pass = False
    return 0 if all_pass else 1
if __name__ == "__main__": sys.exit(main())
