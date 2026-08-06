#!/usr/bin/env python3
"""Backfill validation for QA Pilot registry change receipts.

Checks that backfill RCR receipts cover #48-#53, no duplicated ledger numbers,
and all receipts pass RCR schema validation.
"""
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RCR_DATA_DIR = REPO_ROOT / "data" / "registry-change-receipts"

def load_json(path):
    with open(path) as f:
        return json.load(f)

def main():
    errors = []
    
    if not RCR_DATA_DIR.exists():
        print("❌ RCR data directory not found")
        return 1
    
    receipts = []
    for f in sorted(RCR_DATA_DIR.glob("*.json")):
        try:
            data = load_json(f)
            if data.get("receipt_id", "").startswith("RCR-"):
                receipts.append(data)
        except Exception as e:
            errors.append(f"Failed to parse {f.name}: {e}")
    
    if not receipts:
        print("❌ No RCR receipts found")
        return 1
    
    print(f"Found {len(receipts)} RCR receipts")
    
    # Check coverage: #48-#53
    covered_ledgers = {r["ledger_number"] for r in receipts}
    expected = set(range(48, 54))
    missing = expected - covered_ledgers
    if missing:
        errors.append(f"Missing RCR receipts for ledgers: {sorted(missing)}")
    else:
        print(f"✅ All ledgers #48-#53 covered")
    
    # Check no duplicates
    ledger_list = [r["ledger_number"] for r in receipts]
    dups = {x for x in ledger_list if ledger_list.count(x) > 1}
    if dups:
        errors.append(f"Duplicate ledger entries: {sorted(dups)}")
    else:
        print(f"✅ No duplicate ledger numbers")
    
    # Check all receipts have advisory_only=true
    non_advisory = [r["receipt_id"] for r in receipts if r.get("advisory_only") is not True]
    if non_advisory:
        errors.append(f"Non-advisory receipts: {non_advisory}")
    else:
        print(f"✅ All receipts advisory_only=true")
    
    # Check all have valid impact
    valid_impacts = {"adds_layer", "updates_layer", "no_registry_impact", "deprecates_layer"}
    bad_impact = [r["receipt_id"] for r in receipts if r.get("registry_impact") not in valid_impacts]
    if bad_impact:
        errors.append(f"Invalid impact classes: {bad_impact}")
    else:
        print(f"✅ All receipts have valid impact classes")
    
    # Check adds_layer receipts have layer_slot_added
    for r in receipts:
        if r["registry_impact"] == "adds_layer":
            if "layer_slot_added" not in r:
                errors.append(f"{r['receipt_id']}: adds_layer missing layer_slot_added")
    
    if not any(e.startswith("RCR-") for e in errors):
        print(f"✅ adds_layer receipts have layer_slot_added")
    
    # Summary
    print(f"\nSummary: {len(receipts)} receipts, {len(errors)} issues")
    for e in errors:
        print(f"  ❌ {e}")
    
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
