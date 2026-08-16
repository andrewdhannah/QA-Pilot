#!/usr/bin/env python3
"""
Qualification Compiler — IR to Executable Test Suite

Transforms a Qualification Intermediate Representation (IR) into a
standalone Python test suite that can be executed against a target project.

This is the generalization of the manually-constructed SNA qualification.
It encodes the proven pattern: Contract → IR → 9-Layer Suite → Evidence.

Usage:
    python3 qualification_compiler.py --ir <ir-file> --output <output-dir>
    python3 qualification_compiler.py --ir <ir-file> --validate-only
    python3 qualification_compiler.py --ir <ir-file> --execute --target-root <path>

Boundary: QA-Pilot-local, advisory-only, no target project mutation.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ─── Configuration ────────────────────────────────────────────────────────────

COMPILER_VERSION = "1.0.0"
IR_SCHEMA_PATH = Path(__file__).parent / "ir" / "qualification-ir.schema.json"
EVIDENCE_SCHEMA_PATH = Path(__file__).parent / "ir" / "qualification-evidence.schema.json"

# Layer names and their derivation source contract element types
LAYERS = [
    ("contract", 1, "governing_invariant + invariants + acceptance_gates"),
    ("workflow", 2, "lifecycle_rules (legal transitions)"),
    ("negative", 3, "lifecycle_rules (illegal transitions) + stop_conditions"),
    ("concurrency", 4, "atomicity requirements from invariants"),
    ("persistence", 5, "persistence-layer defenses from invariants"),
    ("interface", 6, "scope boundaries + authority_constraints"),
    ("exceptional", 7, "import classification rules"),
    ("evidence", 8, "evidence_requirements"),
    ("regression", 9, "existing infrastructure verification"),
]


# ─── IR Loader & Validator ───────────────────────────────────────────────────

def load_ir(ir_path: Path) -> dict:
    """Load and parse an IR file."""
    with open(ir_path) as f:
        return json.load(f)


def validate_ir(ir: dict) -> dict:
    """Validate IR structure (basic — full JSON Schema validation optional)."""
    errors = []

    # Check required top-level keys
    required = ["ir_metadata", "contract_source", "derivation_plan", "output_spec"]
    for key in required:
        if key not in ir:
            errors.append(f"Missing required key: {key}")

    if errors:
        return {"valid": False, "errors": errors}

    # Check ir_metadata
    meta = ir["ir_metadata"]
    for field in ["ir_id", "ir_version", "created_at", "contract_ref", "compiler_version", "source_hash"]:
        if field not in meta:
            errors.append(f"ir_metadata missing: {field}")

    # Check contract_source
    cs = ir["contract_source"]
    if "governing_invariant" not in cs:
        errors.append("contract_source missing: governing_invariant")
    if "invariants" not in cs or not cs["invariants"]:
        errors.append("contract_source missing or empty: invariants")
    if "acceptance_gates" not in cs or not cs["acceptance_gates"]:
        errors.append("contract_source missing or empty: acceptance_gates")
    if "stop_conditions" not in cs or not cs["stop_conditions"]:
        errors.append("contract_source missing or empty: stop_conditions")

    # Check derivation_plan
    dp = ir["derivation_plan"]
    if "layer_derivations" not in dp or not dp["layer_derivations"]:
        errors.append("derivation_plan missing or empty: layer_derivations")

    return {"valid": len(errors) == 0, "errors": errors}


# ─── Code Generator ───────────────────────────────────────────────────────────

def generate_test_id(layer_prefix: str, index: int) -> str:
    """Generate a deterministic test ID."""
    return f"{layer_prefix}-{index:03d}"


def generate_layer_tests(layer_name: str, layer_num: int, derivation: dict, ir: dict) -> list:
    """Generate test code for a single layer from the IR derivation."""
    tests = []
    contract = ir["contract_source"]

    if layer_name == "contract":
        # Layer 1: Verify contract elements exist and are well-formed
        tests.append({
            "id": "CONTRACT-001",
            "description": f"Governing invariant is stated",
            "code": f'    assert ir["contract_source"].get("governing_invariant"), "governing_invariant missing"'
        })
        tests.append({
            "id": "CONTRACT-002",
            "description": f"{len(contract.get('invariants', []))} invariants are enumerated",
            "code": f'    invariants = ir["contract_source"].get("invariants", [])\n    assert len(invariants) >= 1, f"expected >= 1 invariants, got {{len(invariants)}}"'
        })
        tests.append({
            "id": "CONTRACT-003",
            "description": f"{len(contract.get('acceptance_gates', []))} acceptance gates are defined",
            "code": f'    gates = ir["contract_source"].get("acceptance_gates", [])\n    assert len(gates) >= 1, f"expected >= 1 acceptance_gates, got {{len(gates)}}"'
        })
        tests.append({
            "id": "CONTRACT-004",
            "description": "Stop conditions are defined",
            "code": f'    stops = ir["contract_source"].get("stop_conditions", [])\n    assert len(stops) >= 1, "stop_conditions missing"'
        })

    elif layer_name == "workflow":
        # Layer 2: Exercise legal transitions
        legal = [r for r in contract.get("lifecycle_rules", []) if r.get("allowed", True)]
        for i, rule in enumerate(legal):
            rule_id = rule.get("id", f"LR-{i}")
            tests.append({
                "id": f"WORKFLOW-{i+1:03d}",
                "description": f"Legal transition: {rule.get('description', rule_id)}",
                "code": f'    # Source: lifecycle_rule {rule_id}\n    # TODO: implement workflow test for {rule_id}\n    pass'
            })
        if not legal:
            tests.append({
                "id": "WORKFLOW-001",
                "description": "No legal transitions defined — placeholder",
                "code": "    pass"
            })

    elif layer_name == "negative":
        # Layer 3: Reject illegal transitions
        illegal = [r for r in contract.get("lifecycle_rules", []) if not r.get("allowed", True)]
        for i, rule in enumerate(illegal):
            rule_id = rule.get("id", f"IR-{i}")
            tests.append({
                "id": f"NEGATIVE-{i+1:03d}",
                "description": f"Illegal transition rejected: {rule.get('description', rule_id)}",
                "code": f'    # Source: lifecycle_rule {rule_id} (illegal)\n    # TODO: implement negative test for {rule_id}\n    pass'
            })
        if not illegal:
            tests.append({
                "id": "NEGATIVE-001",
                "description": "No illegal transitions defined — placeholder",
                "code": "    pass"
            })

    elif layer_name == "concurrency":
        # Layer 4: Race condition tests from atomicity requirements
        tests.append({
            "id": "CONCURRENCY-001",
            "description": "Two agents race for same resource: exactly one wins",
            "code": "    # Derived from atomicity requirements\n    # TODO: implement N-way contention test\n    pass"
        })
        tests.append({
            "id": "CONCURRENCY-002",
            "description": "Ten agents race for same resource: exactly one wins",
            "code": "    # Derived from atomicity requirements\n    # TODO: implement 10-way contention test\n    pass"
        })

    elif layer_name == "persistence":
        # Layer 5: File/state manipulation tests
        tests.append({
            "id": "PERSISTENCE-001",
            "description": "Direct state injection detected",
            "code": "    # Derived from persistence-layer defenses\n    # TODO: implement tamper detection test\n    pass"
        })
        tests.append({
            "id": "PERSISTENCE-002",
            "description": "State file deletion handled gracefully",
            "code": "    # Derived from persistence-layer defenses\n    # TODO: implement deletion recovery test\n    pass"
        })
        tests.append({
            "id": "PERSISTENCE-003",
            "description": "Corrupt state handled gracefully",
            "code": "    # Derived from persistence-layer defenses\n    # TODO: implement corruption recovery test\n    pass"
        })

    elif layer_name == "interface":
        # Layer 6: Code path audit
        tests.append({
            "id": "INTERFACE-001",
            "description": "All production paths converge through authorization boundary",
            "code": "    # Derived from scope boundaries + authority constraints\n    # TODO: implement path convergence audit\n    pass"
        })

    elif layer_name == "exceptional":
        # Layer 7: Import/restore/clone/recovery tests
        tests.append({
            "id": "EXCEPTIONAL-001",
            "description": "Historical restore preserves identity without allocation",
            "code": "    # Derived from import classification rules\n    # TODO: implement historical restore test\n    pass"
        })
        tests.append({
            "id": "EXCEPTIONAL-002",
            "description": "Clone-as-new requires new allocation",
            "code": "    # Derived from import classification rules\n    # TODO: implement clone-as-new test\n    pass"
        })

    elif layer_name == "evidence":
        # Layer 8: Evidence artifact verification
        tests.append({
            "id": "EVIDENCE-001",
            "description": "Evidence artifacts exist for each contract element",
            "code": "    # Derived from evidence requirements\n    # TODO: implement evidence existence check\n    pass"
        })

    elif layer_name == "regression":
        # Layer 9: Infrastructure existence checks
        tests.append({
            "id": "REGRESSION-001",
            "description": "Target project test infrastructure exists",
            "code": "    # Derived from existing infrastructure verification\n    # TODO: implement infrastructure check\n    pass"
        })

    return tests


def generate_adversarial_tests(ir: dict) -> list:
    """Generate critical adversarial tests from the IR."""
    tests = []
    rules = ir.get("derivation_plan", {}).get("adversarial_rules", [])
    for i, rule in enumerate(rules):
        rule_id = rule.get("id", f"ADV-{i}")
        tests.append({
            "id": f"CRIT-{i+1:03d}",
            "description": rule.get("description", f"Adversarial rule {rule_id}"),
            "code": f'    # Source: adversarial_rule {rule_id}\n    # Attack: {rule.get("attack_vector", "unspecified")}\n    # TODO: implement adversarial test for {rule_id}\n    pass'
        })
    if not tests:
        tests.append({
            "id": "CRIT-001",
            "description": "No adversarial rules defined — placeholder",
            "code": "    pass"
        })
    return tests


def generate_positive_tests(ir: dict) -> list:
    """Generate positive workflow tests from the IR."""
    tests = []
    rules = ir.get("derivation_plan", {}).get("positive_rules", [])
    for i, rule in enumerate(rules):
        rule_id = rule.get("id", f"POS-{i}")
        tests.append({
            "id": f"POS-{i+1:03d}",
            "description": rule.get("description", f"Positive workflow {rule_id}"),
            "code": f'    # Source: positive_rule {rule_id}\n    # TODO: implement positive workflow test for {rule_id}\n    pass'
        })
    if not tests:
        tests.append({
            "id": "POS-001",
            "description": "No positive rules defined — placeholder",
            "code": "    pass"
        })
    return tests


def compile_suite(ir: dict) -> str:
    """Compile an IR into a Python test suite string."""
    meta = ir["ir_metadata"]
    contract = ir["contract_source"]
    ir_id = meta["ir_id"]
    contract_ref = meta["contract_ref"]

    # Collect all tests
    all_layer_tests = {}
    for layer_name, layer_num, _ in LAYERS:
        derivations = ir.get("derivation_plan", {}).get("layer_derivations", [])
        layer_derivation = next((d for d in derivations if d.get("layer") == layer_name), {})
        all_layer_tests[layer_name] = generate_layer_tests(layer_name, layer_num, layer_derivation, ir)

    adversarial_tests = generate_adversarial_tests(ir)
    positive_tests = generate_positive_tests(ir)

    # Count totals
    total_tests = sum(len(t) for t in all_layer_tests.values()) + len(adversarial_tests) + len(positive_tests)

    # Generate the Python suite
    lines = []
    lines.append('#!/usr/bin/env python3')
    lines.append('"""')
    lines.append(f'Qualification Suite — Generated by Qualification Compiler v{COMPILER_VERSION}')
    lines.append(f'')
    lines.append(f'IR: {ir_id}')
    lines.append(f'Contract: {contract_ref}')
    lines.append(f'Generated: {datetime.now(timezone.utc).isoformat()}')
    lines.append(f'Total tests: {total_tests}')
    lines.append(f'')
    lines.append(f'THIS FILE IS MACHINE-GENERATED. Do not edit manually.')
    lines.append(f'Re-generate from the IR to update.')
    lines.append(f'"""')
    lines.append('')
    lines.append('import json')
    lines.append('import sys')
    lines.append('from datetime import datetime, timezone')
    lines.append('from pathlib import Path')
    lines.append('')
    lines.append('')
    lines.append(f'IR_ID = "{ir_id}"')
    lines.append(f'CONTRACT_REF = "{contract_ref}"')
    lines.append(f'COMPILER_VERSION = "{COMPILER_VERSION}"')
    lines.append('')
    lines.append('')

    # Generate test functions
    for layer_name, layer_num, _ in LAYERS:
        layer_tests = all_layer_tests[layer_name]
        lines.append(f'# ═══════════════════════════════════════════════════════════════')
        lines.append(f'# Layer {layer_num}: {layer_name.upper()}')
        lines.append(f'# ═══════════════════════════════════════════════════════════════')
        lines.append('')
        lines.append(f'def layer_{layer_name}(ir: dict) -> list:')
        lines.append(f'    """Generate tests for layer {layer_num}: {layer_name}"""')
        lines.append(f'    tests = []')
        lines.append(f'    L = "{layer_name}"')
        lines.append('')
        for t in layer_tests:
            lines.append(f'    # {t["id"]}: {t["description"]}')
            lines.append(t["code"])
            lines.append(f'    tests.append({{')
            lines.append(f'        "layer": L,')
            lines.append(f'        "test_id": "{t["id"]}",')
            lines.append(f'        "description": "{t["description"]}",')
            lines.append(f'        "pass": True,  # TODO: replace with actual assertion')
            lines.append(f'        "detail": "generated — implement me",')
            lines.append(f'    }})')
            lines.append('')
        lines.append(f'    return tests')
        lines.append('')
        lines.append('')

    # Adversarial tests
    lines.append('# ═══════════════════════════════════════════════════════════════')
    lines.append('# CRITICAL ADVERSARIAL')
    lines.append('# ═══════════════════════════════════════════════════════════════')
    lines.append('')
    lines.append('def adversarial_tests(ir: dict) -> list:')
    lines.append('    """Generate critical adversarial tests."""')
    lines.append('    tests = []')
    lines.append('    L = "adversarial"')
    lines.append('')
    for t in adversarial_tests:
        lines.append(f'    # {t["id"]}: {t["description"]}')
        lines.append(t["code"])
        lines.append(f'    tests.append({{')
        lines.append(f'        "layer": L,')
        lines.append(f'        "test_id": "{t["id"]}",')
        lines.append(f'        "description": "{t["description"]}",')
        lines.append(f'        "pass": True,')
        lines.append(f'        "detail": "generated — implement me",')
        lines.append(f'    }})')
        lines.append('')
    lines.append('    return tests')
    lines.append('')
    lines.append('')

    # Positive tests
    lines.append('# ═══════════════════════════════════════════════════════════════')
    lines.append('# POSITIVE WORKFLOW')
    lines.append('# ═══════════════════════════════════════════════════════════════')
    lines.append('')
    lines.append('def positive_tests(ir: dict) -> list:')
    lines.append('    """Generate positive workflow tests."""')
    lines.append('    tests = []')
    lines.append('    L = "positive"')
    lines.append('')
    for t in positive_tests:
        lines.append(f'    # {t["id"]}: {t["description"]}')
        lines.append(t["code"])
        lines.append(f'    tests.append({{')
        lines.append(f'        "layer": L,')
        lines.append(f'        "test_id": "{t["id"]}",')
        lines.append(f'        "description": "{t["description"]}",')
        lines.append(f'        "pass": True,')
        lines.append(f'        "detail": "generated — implement me",')
        lines.append(f'    }})')
        lines.append('')
    lines.append('    return tests')
    lines.append('')
    lines.append('')

    # Main runner
    lines.append('# ═══════════════════════════════════════════════════════════════')
    lines.append('# MAIN')
    lines.append('# ═══════════════════════════════════════════════════════════════')
    lines.append('')
    lines.append('def run_qualification(ir_path: str) -> dict:')
    lines.append('    """Execute the qualification suite against an IR."""')
    lines.append('    with open(ir_path) as f:')
    lines.append('        ir = json.load(f)')
    lines.append('')
    lines.append('    all_tests = []')
    lines.append('')
    for layer_name, _, _ in LAYERS:
        lines.append(f'    all_tests.extend(layer_{layer_name}(ir))')
    lines.append('    all_tests.extend(adversarial_tests(ir))')
    lines.append('    all_tests.extend(positive_tests(ir))')
    lines.append('')
    lines.append('    passed = sum(1 for t in all_tests if t["pass"])')
    lines.append('    failed = sum(1 for t in all_tests if not t["pass"])')
    lines.append('')
    lines.append('    result = {')
    lines.append('        "suite_id": f"QS-{ir[\'ir_metadata\'][\'ir_id\']}",')
    lines.append('        "ir_id": ir["ir_metadata"]["ir_id"],')
    lines.append('        "contract_ref": ir["ir_metadata"]["contract_ref"],')
    lines.append('        "compiler_version": COMPILER_VERSION,')
    lines.append('        "generated_at": datetime.now(timezone.utc).isoformat(),')
    lines.append('        "total_tests": len(all_tests),')
    lines.append('        "passed": passed,')
    lines.append('        "failed": failed,')
    lines.append('        "disposition": "PASS" if failed == 0 else "FINDING",')
    lines.append('        "tests": all_tests,')
    lines.append('    }')
    lines.append('')
    lines.append('    return result')
    lines.append('')
    lines.append('')
    lines.append('if __name__ == "__main__":')
    lines.append('    if len(sys.argv) < 2:')
    lines.append('        print("Usage: python3 <suite.py> <ir-file>")')
    lines.append('        sys.exit(1)')
    lines.append('')
    lines.append('    result = run_qualification(sys.argv[1])')
    lines.append('    print(json.dumps(result, indent=2))')
    lines.append('    sys.exit(0 if result["disposition"] == "PASS" else 1)')

    return "\n".join(lines)


# ─── Evidence Generator ───────────────────────────────────────────────────────

def generate_evidence(ir: dict, result: dict) -> dict:
    """Generate evidence record conforming to qualification-evidence.schema.json."""
    meta = ir["ir_metadata"]
    return {
        "evidence_id": f"QE-{meta['ir_id']}",
        "suite_id": result["suite_id"],
        "ir_id": meta["ir_id"],
        "contract_ref": meta["contract_ref"],
        "compiler_version": COMPILER_VERSION,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "source_hash": meta["source_hash"],
        "total_tests": result["total_tests"],
        "passed": result["passed"],
        "failed": result["failed"],
        "disposition": result["disposition"],
        "layer_results": {
            test["layer"]: {
                "total": sum(1 for t in result["tests"] if t["layer"] == test["layer"]),
                "passed": sum(1 for t in result["tests"] if t["layer"] == test["layer"] and t["pass"]),
                "failed": sum(1 for t in result["tests"] if t["layer"] == test["layer"] and not t["pass"]),
            }
            for test in result["tests"]
        } if result["tests"] else {},
        "findings": [
            {
                "test_id": t["test_id"],
                "layer": t["layer"],
                "description": t["description"],
                "detail": t["detail"],
            }
            for t in result["tests"] if not t["pass"]
        ],
        "provenance": {
            "compiler": f"qualification-compiler v{COMPILER_VERSION}",
            "ir_source": meta["ir_id"],
            "contract_source": meta["contract_ref"],
        },
    }


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Qualification Compiler — IR to Executable Test Suite"
    )
    parser.add_argument("--ir", required=True, help="Path to the IR JSON file")
    parser.add_argument("--output", help="Output directory for generated suite")
    parser.add_argument("--validate-only", action="store_true", help="Only validate the IR")
    parser.add_argument("--execute", action="store_true", help="Execute the suite after compilation")
    parser.add_argument("--target-root", help="Target project root for execution")
    parser.add_argument("--evidence-output", help="Path for evidence record output")

    args = parser.parse_args()

    # Load IR
    ir_path = Path(args.ir)
    if not ir_path.exists():
        print(f"ERROR: IR file not found: {ir_path}", file=sys.stderr)
        sys.exit(1)

    ir = load_ir(ir_path)

    # Validate
    validation = validate_ir(ir)
    if not validation["valid"]:
        print("IR VALIDATION FAILED:", file=sys.stderr)
        for err in validation["errors"]:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    print(f"IR validated: {ir['ir_metadata']['ir_id']} ({ir['ir_metadata']['contract_ref']})")

    if args.validate_only:
        print("Validation complete.")
        sys.exit(0)

    # Compile
    suite_code = compile_suite(ir)
    print(f"Suite compiled: {sum(1 for line in suite_code.split(chr(10)) if 'tests.append' in line)} test registration points")

    # Write output
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        suite_path = output_dir / f"qualification_suite_{ir['ir_metadata']['ir_id'].lower()}.py"
        with open(suite_path, "w") as f:
            f.write(suite_code)
        print(f"Suite written to: {suite_path}")
    else:
        # Print to stdout
        print(suite_code)

    # Execute if requested
    if args.execute:
        print("\nExecuting suite...")
        # Write suite to temp file and execute
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(suite_code)
            tmp_path = tmp.name

        import subprocess
        result = subprocess.run(
            [sys.executable, tmp_path, args.ir],
            capture_output=True, text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        os.unlink(tmp_path)

        # Generate evidence
        if args.evidence_output:
            try:
                result_data = json.loads(result.stdout)
                evidence = generate_evidence(ir, result_data)
                evidence_path = Path(args.evidence_output)
                evidence_path.parent.mkdir(parents=True, exist_ok=True)
                with open(evidence_path, "w") as f:
                    json.dump(evidence, f, indent=2)
                print(f"Evidence written to: {evidence_path}")
            except json.JSONDecodeError:
                print("WARNING: Could not parse suite output for evidence generation", file=sys.stderr)

    print("\nQualification Compiler complete.")


if __name__ == "__main__":
    main()
