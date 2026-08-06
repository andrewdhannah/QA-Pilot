#!/usr/bin/env python3
"""Validator for QA Work Packet schema."""
import json, sys
VALID_STATUSES = ["authorized","in_progress","completed","failed","cancelled"]
RULES = [
    ("WP-1", "packet_id present", lambda d: bool(d.get("packet_id"))),
    ("WP-2", "queue_item_ref present", lambda d: bool(d.get("queue_item_ref"))),
    ("WP-3", "status is valid", lambda d: d.get("status") in VALID_STATUSES),
    ("WP-4", "failure_context.expected present", lambda d: bool(d.get("failure_context",{}).get("expected"))),
    ("WP-5", "failure_context.actual present", lambda d: bool(d.get("failure_context",{}).get("actual"))),
    ("WP-6", "constraints.must_not_modify present", lambda d: "must_not_modify" in d.get("constraints",{})),
    ("WP-7", "constraints.required_validation present", lambda d: "required_validation" in d.get("constraints",{})),
    ("WP-8", "authority.authorized_by present", lambda d: bool(d.get("authority",{}).get("authorized_by"))),
    ("WP-9", "provenance.advisory=true", lambda d: d.get("provenance",{}).get("advisory")==True),
    ("WP-10", "provenance.no_authority_conferred=true", lambda d: d.get("provenance",{}).get("no_authority_conferred")==True),
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
