#!/usr/bin/env python3
"""Validator for QA Diagnostic Report schema (schema validation)."""
import json, sys
RULES = [
    ("DR-1", "report_id present", lambda d: bool(d.get("report_id"))),
    ("DR-2", "failure.expected present", lambda d: bool(d.get("failure", {}).get("expected"))),
    ("DR-3", "failure.actual present", lambda d: bool(d.get("failure", {}).get("actual"))),
    ("DR-4", "provenance.advisory=true", lambda d: d.get("provenance", {}).get("advisory") == True),
    ("DR-5", "provenance.no_authority_conferred=true", lambda d: d.get("provenance", {}).get("no_authority_conferred") == True),
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
