#!/usr/bin/env python3
"""
ASSURANCE-CORPUS-CLASSIFICATION-1: Extract FAIL Details

Re-runs the E2E-8 execution to extract the full 79 FAIL details
for classification pilot.

Usage:
    python3 scripts/classification-pilot-extract-fails.py
"""

import json
import os
import sys
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

WORKSPACE_ROOT = Path("/Users/andrew/Desktop/CarbideFrame")
QA_PILOT_ROOT = WORKSPACE_ROOT / "active" / "qa-pilot"
LIBRARIAN_ROOT = WORKSPACE_ROOT / "active" / "librarian"
SPRINT_LEDGER = LIBRARIAN_ROOT / "project-state" / "sprint-ledger.json"
CAPABILITY_REGISTRY = QA_PILOT_ROOT / "capability-registry" / "capability-registry.json"
MCP_CAPABILITY = QA_PILOT_ROOT / "scripts" / "mcp-capability.py"
RUST_MCP_TARGET = "http://127.0.0.1:3457/mcp"


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f), None
    except Exception as e:
        return None, str(e)


def classify_sprint(sprint):
    has_acceptance = bool(sprint.get("harness"))
    has_implementation = bool(sprint.get("commit"))
    has_evidence = bool(sprint.get("evidence_note"))
    has_doc = bool(sprint.get("doc"))

    if has_acceptance and has_implementation and has_evidence and has_doc:
        return "ASSURANCE_READY"
    elif has_acceptance and has_implementation:
        return "ASSURANCE_PARTIAL"
    elif has_implementation and not has_acceptance:
        return "NON_EXECUTABLE"
    else:
        return "INSUFFICIENT_SOURCE"


def extract_claims(sprint):
    claims = []
    harness = sprint.get("harness", "")
    if "/" in harness:
        try:
            parts = harness.split("/")
            passed = int(parts[0])
            total = int(parts[1].split()[0])
            claims.append({
                "type": "harness_pass",
                "claim": f"All {total} tests passed ({harness})",
                "testable": True,
                "requirement": f"Sprint {sprint['id']} harness tests must pass"
            })
        except:
            pass

    commit = sprint.get("commit", "")
    if commit:
        claims.append({
            "type": "implementation_exists",
            "claim": f"Implementation exists: {commit}",
            "testable": True,
            "requirement": f"Sprint {sprint['id']} must have implementing artifacts"
        })

    evidence = sprint.get("evidence_note", "")
    if evidence:
        claims.append({
            "type": "evidence_recorded",
            "claim": f"Evidence recorded: {evidence[:80]}...",
            "testable": True,
            "requirement": f"Sprint {sprint['id']} must have verifiable evidence"
        })

    return claims


def derive_test_requirements(claims, sprint):
    test_requirements = []
    for claim in claims:
        if claim["type"] == "harness_pass":
            test_requirements.append({
                "id": f"{sprint['id']}-T001",
                "requirement": claim["requirement"],
                "test_type": "regression",
                "required_capability": "SCRIPT_EXECUTION",
                "description": f"Verify harness test results for {sprint['id']}"
            })
        elif claim["type"] == "implementation_exists":
            test_requirements.append({
                "id": f"{sprint['id']}-T002",
                "requirement": claim["requirement"],
                "test_type": "existence",
                "required_capability": "SCRIPT_EXECUTION",
                "description": f"Verify implementation artifacts exist for {sprint['id']}"
            })
        elif claim["type"] == "evidence_recorded":
            test_requirements.append({
                "id": f"{sprint['id']}-T003",
                "requirement": claim["requirement"],
                "test_type": "evidence_verification",
                "required_capability": "SCRIPT_EXECUTION",
                "description": f"Verify evidence references for {sprint['id']}"
            })

    return test_requirements


def resolve_capability(required_capability, cap_registry):
    exec_caps = cap_registry.get("execution_type_capabilities", {})
    if required_capability == "SCRIPT_EXECUTION" and "validator" in exec_caps:
        return "validator"
    elif required_capability == "MCP_API_INTERACTION" and "mcp_api" in exec_caps:
        return "mcp_api"
    return None


def construct_test_artifact(req, sprint, cap_registry):
    cap_id = resolve_capability(req.get("required_capability", "SCRIPT_EXECUTION"), cap_registry)

    return {
        "test_id": f"{req['id']}-CONSTRUCTED",
        "source_requirement": req.get("requirement", ""),
        "source_sprint": sprint.get("id", ""),
        "source_claim": sprint.get("commit", ""),
        "source_evidence": sprint.get("evidence_note", ""),
        "required_capabilities": [req.get("required_capability", "SCRIPT_EXECUTION")],
        "matched_capability": cap_id,
        "target_adapter": "mcp-jsonrpc" if cap_id == "mcp_api" else "cli",
        "test_type": req.get("test_type", "regression"),
        "description": req.get("description", ""),
    }


def execute_test(artifact, sprint_data):
    """Execute a test and return detailed result."""
    adapter = artifact.get("target_adapter", "")
    test_type = artifact.get("test_type", "")
    source_sprint = artifact.get("source_sprint", "")

    if adapter == "mcp-jsonrpc":
        cmd = [sys.executable, str(MCP_CAPABILITY), "--tool", "project_registry_list",
               "--target", RUST_MCP_TARGET]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                                    cwd=str(WORKSPACE_ROOT))
            if result.returncode == 0:
                output = json.loads(result.stdout)
                if output.get("error"):
                    return "FAIL", "MCP returned error", {
                        "observed": f"MCP error: {output['error'].get('message', str(output['error']))}",
                        "expected": "MCP tool executes successfully"
                    }
                return "PASS", "MCP tool executed", {
                    "observed": "MCP tool returned result",
                    "expected": "MCP tool executes successfully"
                }
            else:
                return "ERROR", "MCP execution failed", {
                    "observed": f"Subprocess failed: {result.stderr[:100]}",
                    "expected": "MCP tool executes successfully"
                }
        except Exception as e:
            return "ERROR", "MCP execution error", {
                "observed": f"Exception: {str(e)[:100]}",
                "expected": "MCP tool executes successfully"
            }

    elif adapter == "cli":
        # For CLI tests, check different conditions based on test_type
        sprint_doc = LIBRARIAN_ROOT / "docs" / "sprints" / f"{source_sprint}.md"

        if test_type == "regression":
            # Check if harness claims exist
            harness = sprint_data.get("harness", "")
            if harness and "/" in harness:
                try:
                    parts = harness.split("/")
                    total = int(parts[1].split()[0])
                    if total > 0:
                        return "PASS", f"Harness claims {total} tests", {
                            "observed": f"Harness: {harness}",
                            "expected": "Non-zero test count claimed"
                        }
                except:
                    pass
            return "FAIL", "No harness test count found", {
                "observed": f"Harness: {sprint_data.get('harness', 'null')}",
                "expected": "Non-zero test count claimed"
            }

        elif test_type == "existence":
            # Check if authoritative evidence exists
            # Multiple valid locations: sprint doc, evidence_note, or commit
            has_sprint_doc = sprint_doc.exists()
            has_evidence_note = bool(sprint_data.get("evidence_note", ""))
            has_commit = bool(sprint_data.get("commit", ""))

            if has_sprint_doc or has_evidence_note or has_commit:
                evidence_locations = []
                if has_sprint_doc:
                    evidence_locations.append(f"doc:{sprint_doc.name}")
                if has_evidence_note:
                    evidence_locations.append("evidence_note")
                if has_commit:
                    evidence_locations.append("commit")
                return "PASS", "Authoritative evidence exists", {
                    "observed": f"Evidence locations: {', '.join(evidence_locations)}",
                    "expected": "Authoritative evidence exists"
                }
            else:
                return "FAIL", "No authoritative evidence found", {
                    "observed": f"No doc, no evidence_note, no commit for {source_sprint}",
                    "expected": "Authoritative evidence exists"
                }

        elif test_type == "evidence_verification":
            # Check if evidence note exists
            evidence = sprint_data.get("evidence_note", "")
            if evidence:
                return "PASS", "Evidence note exists", {
                    "observed": f"Evidence: {evidence[:80]}...",
                    "expected": "Evidence note recorded"
                }
            else:
                return "FAIL", "No evidence note", {
                    "observed": "evidence_note is empty/null",
                    "expected": "Evidence note recorded"
                }

    return "ERROR", "Unknown adapter/test type", {
        "observed": f"adapter={adapter}, test_type={test_type}",
        "expected": "Recognized adapter and test type"
    }


def main():
    print("=" * 72)
    print("  ASSURANCE-CORPUS-CLASSIFICATION-1: Extract FAIL Details")
    print("=" * 72)

    # Load sprint ledger
    print("\n=== Loading Sprint Ledger ===")
    ledger, err = load_json(SPRINT_LEDGER)
    if err:
        print(f"  FAIL: {err}")
        sys.exit(1)

    sprints = ledger.get("sprints", [])
    sealed = [s for s in sprints if s.get("status") == "sealed"]
    print(f"  Sealed sprints: {len(sealed)}")

    # Load capability registry
    cap_registry, _ = load_json(CAPABILITY_REGISTRY)

    # Build corpus and execute
    print("\n=== Building and Executing Corpus ===")
    all_results = []
    for sprint in sealed:
        classification = classify_sprint(sprint)
        if classification == "ASSURANCE_READY":
            claims = extract_claims(sprint)
            test_reqs = derive_test_requirements(claims, sprint)
            for req in test_reqs:
                artifact = construct_test_artifact(req, sprint, cap_registry)
                status, detail, evidence = execute_test(artifact, sprint)
                all_results.append({
                    "test_id": artifact["test_id"],
                    "source_sprint": sprint["id"],
                    "source_sprint_title": sprint.get("title", ""),
                    "source_requirement": artifact["source_requirement"],
                    "source_claim": artifact["source_claim"],
                    "source_evidence": artifact["source_evidence"],
                    "test_type": artifact["test_type"],
                    "status": status,
                    "detail": detail,
                    "evidence": evidence,
                })

    # Count results
    pass_count = sum(1 for r in all_results if r["status"] == "PASS")
    fail_count = sum(1 for r in all_results if r["status"] == "FAIL")
    error_count = sum(1 for r in all_results if r["status"] == "ERROR")

    print(f"\n  Total: {len(all_results)}")
    print(f"  PASS: {pass_count}, FAIL: {fail_count}, ERROR: {error_count}")

    # Extract all FAILs
    fails = [r for r in all_results if r["status"] == "FAIL"]
    print(f"\n=== All {len(fails)} FAILs ===")

    # Group by sprint
    by_sprint = defaultdict(list)
    for f in fails:
        by_sprint[f["source_sprint"]].append(f)

    print(f"  Sprints with FAILs: {len(by_sprint)}")

    # Save full results
    reports_dir = QA_PILOT_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Save all results
    with open(reports_dir / "classification-pilot-all-results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    # Save only FAILs
    with open(reports_dir / "classification-pilot-fails.json", "w") as f:
        json.dump(fails, f, indent=2)

    # Save summary
    with open(reports_dir / "classification-pilot-summary.json", "w") as f:
        json.dump({
            "total": len(all_results),
            "pass": pass_count,
            "fail": fail_count,
            "error": error_count,
            "sprints_with_fails": len(by_sprint),
            "fails_by_sprint": {k: len(v) for k, v in by_sprint.items()},
        }, f, indent=2)

    print(f"\n  Results saved to: reports/classification-pilot-*.json")

    # Print first 15 FAILs for classification pilot
    print("\n=== Classification Pilot: First 15 FAILs ===")
    for i, f in enumerate(fails[:15]):
        print(f"\n--- FAIL {i+1} ---")
        print(f"  Test ID: {f['test_id']}")
        print(f"  Sprint: {f['source_sprint']} ({f['source_sprint_title']})")
        print(f"  Test Type: {f['test_type']}")
        print(f"  Requirement: {f['source_requirement'][:100]}")
        print(f"  Claim: {f['source_claim'][:100]}")
        print(f"  Observed: {f['evidence']['observed'][:100]}")
        print(f"  Expected: {f['evidence']['expected'][:100]}")

    sys.exit(0)


if __name__ == "__main__":
    main()
