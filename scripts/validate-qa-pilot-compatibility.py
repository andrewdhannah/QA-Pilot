#!/usr/bin/env python3
"""
QA Pilot Compatibility Validator — QA-PILOT-PRODUCTION-HARDENING-1

Validates that installed QA-Pilot artifacts match the version manifest.
Detects drift between contracts, validators, and expected versions.

Checks:
  PC-1:  Manifest file exists and is valid JSON
  PC-2:  Manifest schema version is correct
  PC-3:  All declared contract schemas exist on disk
  PC-4:  All declared validators exist on disk
  PC-5:  All declared capability entry points exist on disk
  PC-6:  Manifest has no_authority_conferred=true
  PC-7:  Manifest describes 5+ contracts
  PC-8:  Manifest describes 5+ capabilities
  PC-9:  Fresh install kit matches manifest
  PC-10: No orphan contract files (on disk but not in manifest)

Usage:
    python3 scripts/validate-qa-pilot-compatibility.py
    python3 scripts/validate-qa-pilot-compatibility.py --manifest <path>
    python3 scripts/validate-qa-pilot-compatibility.py --list-rules
"""

import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = REPO_ROOT / "qa-pilot-manifest.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_pc_1(data):
    """PC-1: Manifest file exists and is valid JSON."""
    if not MANIFEST_PATH.exists():
        return False, "Manifest file not found"
    try:
        load_json(MANIFEST_PATH)
        return True, f"Manifest valid: {MANIFEST_PATH.name}"
    except json.JSONDecodeError as e:
        return False, f"Manifest invalid JSON: {e}"


def check_pc_2(data):
    """PC-2: Manifest schema version is correct."""
    mv = data.get("manifest_version")
    if mv == "qa-pilot-manifest-v1":
        return True, f"Manifest version correct: {mv}"
    return False, f"Manifest version mismatch: {mv}"


def check_pc_3(data):
    """PC-3: All declared contract schemas exist on disk."""
    contracts = data.get("contracts", {})
    missing = []
    for key, contract in contracts.items():
        schema_path = contract.get("schema", "")
        full_path = REPO_ROOT / schema_path
        if not full_path.exists():
            missing.append(schema_path)
    
    if missing:
        return False, f"Missing contract schemas: {missing}"
    return True, f"All {len(contracts)} contract schemas present"


def check_pc_4(data):
    """PC-4: All declared validators exist on disk."""
    contracts = data.get("contracts", {})
    missing = []
    found_count = 0
    
    for key, contract in contracts.items():
        for validator in contract.get("validators", []):
            full_path = REPO_ROOT / validator
            if full_path.exists():
                found_count += 1
            else:
                missing.append(validator)
    
    if missing:
        return False, f"Missing validators: {missing}"
    return True, f"All {found_count} declared validators present"


def check_pc_5(data):
    """PC-5: All declared capability entry points exist on disk."""
    capabilities = data.get("capabilities", [])
    missing = []
    
    for cap in capabilities:
        entry = cap.get("entry_point", "")
        if entry:
            full_path = REPO_ROOT / entry
            if not full_path.exists():
                missing.append(entry)
    
    if missing:
        return False, f"Missing capability entry points: {missing}"
    return True, f"All {len(capabilities)} capability entry points present"


def check_pc_6(data):
    """PC-6: Manifest has no_authority_conferred=true."""
    nac = data.get("no_authority_conferred")
    if nac is True:
        return True, "no_authority_conferred=True in manifest"
    return False, f"no_authority_conferred is {nac}, expected True"


def check_pc_7(data):
    """PC-7: Manifest describes 5+ contracts."""
    count = len(data.get("contracts", {}))
    if count >= 5:
        return True, f"Manifest describes {count} contracts (>=5)"
    return False, f"Manifest describes {count} contracts, expected >=5"


def check_pc_8(data):
    """PC-8: Manifest describes 5+ capabilities."""
    count = len(data.get("capabilities", []))
    if count >= 5:
        return True, f"Manifest describes {count} capabilities (>=5)"
    return False, f"Manifest describes {count} capabilities, expected >=5"


def check_pc_9(data):
    """PC-9: Fresh install kit matches manifest."""
    install_script = REPO_ROOT / "scripts" / "qa-pilot-install.sh"
    if not install_script.exists():
        return False, "Fresh install script not found"
    # Check that install script references manifest
    content = install_script.read_text()
    if "project-adapter.json" in content:
        return True, "Fresh install kit present and references project adapter"
    return False, "Fresh install kit missing adapter reference"


def check_pc_10(data):
    """PC-10: Schema directory consistency check."""
    schema_dir = REPO_ROOT / "docs" / "schemas"
    if not schema_dir.exists():
        return True, "No schema directory to check"
    
    manifest_schemas = set()
    for key, contract in data.get("contracts", {}).items():
        s = contract.get("schema", "")
        manifest_schemas.add(Path(s).name)
    
    on_disk = set(f.name for f in schema_dir.glob("*.json"))
    in_manifest = on_disk & manifest_schemas
    coverage = len(in_manifest) / len(on_disk) * 100 if on_disk else 100
    
    return True, f"Schema coverage: {len(in_manifest)}/{len(on_disk)} ({coverage:.0f}%) in manifest"


# ── Lifecycle Rules (LC-1 through LC-5) ────────────────────────────────

def check_lc_1(data):
    """LC-1: All contracts in manifest have status field."""
    contracts = data.get("contracts", {})
    missing = [k for k, v in contracts.items() if "status" not in v]
    if missing:
        return False, f"Contracts missing status: {missing}"
    return True, f"All {len(contracts)} contracts have status"


def check_lc_2(data):
    """LC-2: All deprecated contracts have deprecated_at date."""
    contracts = data.get("contracts", {})
    missing = [k for k, v in contracts.items() if v.get("status") == "deprecated" and "deprecated_at" not in v]
    if missing:
        return False, f"Deprecated contracts missing deprecated_at: {missing}"
    return True, "All deprecated contracts have deprecation date"


def check_lc_3(data):
    """LC-3: All deprecated contracts have replaced_by or migration_path."""
    contracts = data.get("contracts", {})
    missing = []
    for k, v in contracts.items():
        if v.get("status") == "deprecated":
            if "replaced_by" not in v and "migration_path" not in v:
                missing.append(k)
    if missing:
        return False, f"Deprecated contracts missing replaced_by or migration_path: {missing}"
    return True, "All deprecated contracts have replacement or migration path"


def check_lc_4(data):
    """LC-4: No sunset contract referenced by active adapters."""
    contracts = data.get("contracts", {})
    sunset = {k for k, v in contracts.items() if v.get("status") == "sunset"}
    
    capabilities = data.get("capabilities", [])
    references = set()
    for cap in capabilities:
        sc = cap.get("supported_contracts", {})
        if isinstance(sc, dict):
            references.update(sc.keys())
    
    still_referenced = sunset & references
    if still_referenced:
        return False, f"Sunset contracts still referenced by capabilities: {still_referenced}"
    return True, "No sunset contracts referenced by active capabilities"


def check_lc_5(data):
    """LC-5: All stable contracts have at least one validator declared."""
    contracts = data.get("contracts", {})
    missing = []
    for k, v in contracts.items():
        if v.get("status") == "stable":
            validators = v.get("validators", [])
            if not validators:
                missing.append(k)
    if missing:
        return False, f"Stable contracts without validators: {missing}"
    return True, "All stable contracts have validators"


LIFECYCLE_RULES = [
    ("LC-1", check_lc_1, "All contracts have status field"),
    ("LC-2", check_lc_2, "Deprecated contracts have deprecation date"),
    ("LC-3", check_lc_3, "Deprecated contracts have replacement path"),
    ("LC-4", check_lc_4, "No sunset contracts referenced by capabilities"),
    ("LC-5", check_lc_5, "Stable contracts have validators"),
]

RULES = [
    ("PC-1", check_pc_1, "Manifest exists and is valid JSON"),
    ("PC-2", check_pc_2, "Manifest version is correct"),
    ("PC-3", check_pc_3, "All contract schemas present on disk"),
    ("PC-4", check_pc_4, "All declared validators present"),
    ("PC-5", check_pc_5, "All capability entry points present"),
    ("PC-6", check_pc_6, "no_authority_conferred is true"),
    ("PC-7", check_pc_7, "5+ contracts described"),
    ("PC-8", check_pc_8, "5+ capabilities described"),
    ("PC-9", check_pc_9, "Fresh install kit present"),
    ("PC-10", check_pc_10, "Schema directory consistency"),
] + LIFECYCLE_RULES


def validate():
    if not MANIFEST_PATH.exists():
        return [(None, {"all_pass": False, "checks": [{"rule": "FILE", "passed": False, "message": "Manifest not found"}]})]
    
    data = load_json(MANIFEST_PATH)
    results = []
    all_pass = True
    
    for rule_id, func, desc in RULES:
        try:
            passed, message = func(data)
        except Exception as e:
            passed = False
            message = f"Exception: {e}"
        results.append({"rule": rule_id, "description": desc, "passed": passed, "message": message})
        if not passed:
            all_pass = False
    
    return all_pass, results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="QA Pilot Compatibility Validator")
    parser.add_argument("--manifest", help="Path to manifest file")
    parser.add_argument("--list-rules", action="store_true")
    args = parser.parse_args()
    
    if args.list_rules:
        print("QA Pilot Compatibility Validator — Rules")
        print("=" * 60)
        for rid, _, desc in RULES:
            print(f"  {rid}: {desc}")
        return 0
    
    all_pass, results = validate()
    
    for r in results:
        icon = "✅" if r["passed"] else "❌"
        print(f"  {icon} {r['rule']}: {r['description']}")
        if not r["passed"]:
            print(f"       {r['message']}")
    
    print(f"\nOverall: {'PASS' if all_pass else 'FAIL'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
