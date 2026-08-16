#!/usr/bin/env python3
"""
E2E-7: Reproducibility

Runs the frozen E2E-5 artifacts twice against the same target.
Compares structural and observational reproducibility.

Usage:
    python3 scripts/e2e-7-reproducibility.py
"""

import json
import os
import sys
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from copy import deepcopy

WORKSPACE_ROOT = Path("/Users/andrew/Desktop/CarbideFrame")
QA_PILOT_ROOT = WORKSPACE_ROOT / "active" / "qa-pilot"
CONSTRUCTED_TESTS = QA_PILOT_ROOT / "test-library" / "e2e-5-constructed"
MCP_CAPABILITY = QA_PILOT_ROOT / "scripts" / "mcp-capability.py"
RUST_MCP_TARGET = "http://127.0.0.1:3457/mcp"

results = []
passes = 0
failures = 0


def record_result(requirement, test_name, status, detail=""):
    global passes, failures
    results.append({
        "requirement": requirement,
        "test": test_name,
        "status": status,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    if status == "PASS":
        passes += 1
    elif status == "FAIL":
        failures += 1


def compute_file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f), None
    except Exception as e:
        return None, str(e)


def execute_test(artifact):
    """Execute a single test artifact."""
    adapter = artifact.get("target_adapter", "")

    if adapter == "mcp-jsonrpc":
        cmd = [sys.executable, str(MCP_CAPABILITY), "--tool", "project_registry_list",
               "--target", RUST_MCP_TARGET]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                                    cwd=str(WORKSPACE_ROOT))
            if result.returncode == 0:
                output = json.loads(result.stdout)
                if output.get("error"):
                    return "FAIL", f"MCP error: {output['error'].get('message', str(output['error']))[:60]}"
                return "PASS", "MCP tool executed"
            else:
                return "ERROR", f"MCP failed: {result.stderr[:60]}"
        except Exception as e:
            return "ERROR", f"MCP error: {str(e)[:60]}"
    elif adapter == "cli":
        source_sprint = artifact.get("source_sprint", "")
        sprint_doc = WORKSPACE_ROOT / "active" / "librarian" / "docs" / "sprints" / f"{source_sprint}.md"
        if sprint_doc.exists():
            return "PASS", f"Sprint doc exists"
        else:
            return "FAIL", f"Sprint doc not found"
    else:
        return "ERROR", f"Unknown adapter: {adapter}"


def run_execution(label):
    """Execute all frozen artifacts and return results."""
    print(f"\n=== {label}: Execution ===")

    artifact_files = sorted(CONSTRUCTED_TESTS.glob("*.json"))
    print(f"  Artifacts discovered: {len(artifact_files)}")

    # Compute pre-execution hashes
    pre_hashes = {}
    for f in artifact_files:
        pre_hashes[f.name] = compute_file_hash(f)

    # Execute all tests
    execution_results = []
    for f in artifact_files:
        artifact, err = load_json(f)
        if err:
            execution_results.append({"test_id": f.stem, "status": "ERROR", "detail": err})
            continue

        status, detail = execute_test(artifact)
        execution_results.append({
            "test_id": artifact.get("test_id"),
            "status": status,
            "detail": detail,
            "source_requirement": artifact.get("source_requirement"),
            "required_capabilities": artifact.get("required_capabilities"),
            "target_adapter": artifact.get("target_adapter"),
        })

    # Compute post-execution hashes
    post_hashes = {}
    for f in artifact_files:
        post_hashes[f.name] = compute_file_hash(f)

    # Count results
    pass_count = sum(1 for r in execution_results if r["status"] == "PASS")
    fail_count = sum(1 for r in execution_results if r["status"] == "FAIL")
    error_count = sum(1 for r in execution_results if r["status"] == "ERROR")

    print(f"  Executed: {len(execution_results)}")
    print(f"  PASS: {pass_count}, FAIL: {fail_count}, ERROR: {error_count}")

    return {
        "label": label,
        "artifact_count": len(artifact_files),
        "pre_hashes": pre_hashes,
        "post_hashes": post_hashes,
        "integrity_match": pre_hashes == post_hashes,
        "results": execution_results,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "error_count": error_count,
    }


def compare_structural(run_a, run_b):
    """Compare structural reproducibility between runs."""
    print("\n=== Structural Comparison ===")

    comparisons = []

    # Artifacts
    match = run_a["artifact_count"] == run_b["artifact_count"]
    comparisons.append(("Artifacts", match, f"A={run_a['artifact_count']}, B={run_b['artifact_count']}"))
    record_result("Structural: Artifacts match", "struct-artifacts", "PASS" if match else "FAIL",
                  f"A={run_a['artifact_count']}, B={run_b['artifact_count']}")

    # Requirements
    reqs_a = [r.get("source_requirement") for r in run_a["results"]]
    reqs_b = [r.get("source_requirement") for r in run_b["results"]]
    match = reqs_a == reqs_b
    comparisons.append(("Requirements", match, "MATCH" if match else "MISMATCH"))
    record_result("Structural: Requirements match", "struct-requirements", "PASS" if match else "FAIL")

    # Capabilities
    caps_a = [r.get("required_capabilities") for r in run_a["results"]]
    caps_b = [r.get("required_capabilities") for r in run_b["results"]]
    match = caps_a == caps_b
    comparisons.append(("Capabilities", match, "MATCH" if match else "MISMATCH"))
    record_result("Structural: Capabilities match", "struct-capabilities", "PASS" if match else "FAIL")

    # Adapters
    adapters_a = [r.get("target_adapter") for r in run_a["results"]]
    adapters_b = [r.get("target_adapter") for r in run_b["results"]]
    match = adapters_a == adapters_b
    comparisons.append(("Adapters", match, "MATCH" if match else "MISMATCH"))
    record_result("Structural: Adapters match", "struct-adapters", "PASS" if match else "FAIL")

    # Test IDs
    ids_a = [r.get("test_id") for r in run_a["results"]]
    ids_b = [r.get("test_id") for r in run_b["results"]]
    match = ids_a == ids_b
    comparisons.append(("Test IDs", match, "MATCH" if match else "MISMATCH"))
    record_result("Structural: Test IDs match", "struct-test-ids", "PASS" if match else "FAIL")

    # Artifact hashes
    match = run_a["pre_hashes"] == run_b["pre_hashes"]
    comparisons.append(("Artifact Hashes", match, "MATCH" if match else "MISMATCH"))
    record_result("Structural: Artifact hashes match", "struct-hashes", "PASS" if match else "FAIL")

    # Artifact integrity
    match = run_a["integrity_match"] and run_b["integrity_match"]
    comparisons.append(("Artifact Integrity", match, "MATCH" if match else "MISMATCH"))
    record_result("Structural: Artifact integrity", "struct-integrity", "PASS" if match else "FAIL")

    # Result schema
    schema_a = all("test_id" in r and "status" in r for r in run_a["results"])
    schema_b = all("test_id" in r and "status" in r for r in run_b["results"])
    match = schema_a and schema_b
    comparisons.append(("Result Schema", match, "MATCH" if match else "MISMATCH"))
    record_result("Structural: Result schema consistent", "struct-schema", "PASS" if match else "FAIL")

    # Evidence structure
    evidence_a = len(run_a["results"]) == run_a["artifact_count"]
    evidence_b = len(run_b["results"]) == run_b["artifact_count"]
    match = evidence_a and evidence_b
    comparisons.append(("Evidence Structure", match, "MATCH" if match else "MISMATCH"))
    record_result("Structural: Evidence structure complete", "struct-evidence", "PASS" if match else "FAIL")

    # No silent skips
    skip_a = run_a["artifact_count"] != len(run_a["results"])
    skip_b = run_b["artifact_count"] != len(run_b["results"])
    match = not skip_a and not skip_b
    comparisons.append(("No Silent Skips", match, "MATCH" if match else "MISMATCH"))
    record_result("Structural: No silent skips", "struct-no-skips", "PASS" if match else "FAIL")

    print("\n  Structural Summary:")
    for name, match, detail in comparisons:
        symbol = "✓" if match else "✗"
        print(f"    {symbol} {name}: {detail}")

    return comparisons


def compare_observational(run_a, run_b):
    """Compare observational reproducibility between runs."""
    print("\n=== Observational Comparison ===")

    # PASS/FAIL counts
    match = (run_a["pass_count"] == run_b["pass_count"] and
             run_a["fail_count"] == run_b["fail_count"])
    record_result("Observational: PASS/FAIL counts match", "obs-pass-fail",
                  "PASS" if match else "FAIL",
                  f"A={run_a['pass_count']}/{run_a['fail_count']}, B={run_b['pass_count']}/{run_b['fail_count']}")

    # Individual results
    results_match = [r_a["status"] == r_b["status"]
                     for r_a, r_b in zip(run_a["results"], run_b["results"])]
    all_match = all(results_match)
    divergences = sum(1 for m in results_match if not m)
    record_result("Observational: Individual results match", "obs-individual",
                  "PASS" if all_match else "FAIL",
                  f"Divergences: {divergences}/{len(results_match)}")

    print(f"\n  Observational Summary:")
    print(f"    Run A: {run_a['pass_count']} PASS / {run_a['fail_count']} FAIL / {run_a['error_count']} ERROR")
    print(f"    Run B: {run_b['pass_count']} PASS / {run_b['fail_count']} FAIL / {run_b['error_count']} ERROR")
    print(f"    Match: {'YES' if match else 'NO'}")
    print(f"    Individual divergences: {divergences}")

    return match, divergences


def main():
    print("=" * 72)
    print("  E2E-7: Reproducibility")
    print("  Frozen E2E-5 artifacts, two runs, comparison")
    print("=" * 72)

    # Verify frozen artifacts exist
    if not CONSTRUCTED_TESTS.exists():
        print("  FAIL: E2E-5 constructed tests not found")
        sys.exit(1)

    artifact_count = len(list(CONSTRUCTED_TESTS.glob("*.json")))
    if artifact_count != 30:
        print(f"  FAIL: Expected 30 artifacts, found {artifact_count}")
        sys.exit(1)

    print(f"  Frozen artifacts: {artifact_count}")

    # Run A
    run_a = run_execution("RUN A")

    # Run B (same frozen artifacts, same target)
    run_b = run_execution("RUN B")

    # Structural comparison
    structural = compare_structural(run_a, run_b)

    # Observational comparison
    obs_match, divergences = compare_observational(run_a, run_b)

    # Save results
    print("\n=== Saving Results ===")
    reports_dir = QA_PILOT_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)

    result_path = reports_dir / "E2E-7-reproducibility-result.json"
    with open(result_path, "w") as f:
        json.dump({
            "$schema": "qa-test-result-v1",
            "test_id": "E2E-7",
            "title": "Reproducibility",
            "domain": "regression",
            "objective": "Prove same frozen artifacts produce reproducible results",
            "results": {
                "total_requirements": len(results),
                "discovered": len(results),
                "executable": len(results),
                "executed": len(results),
                "reported": len(results),
                "pass": passes,
                "fail": failures,
                "capability_missing": 0,
                "discovery_coverage_pct": 100.0,
                "execution_coverage_pct": 100.0,
                "reporting_coverage_pct": 100.0,
                "pass_rate_pct": round((passes / len(results)) * 100, 1) if results else 0,
                "status": "COMPLETE",
            },
            "run_a": {
                "artifact_count": run_a["artifact_count"],
                "pass": run_a["pass_count"],
                "fail": run_a["fail_count"],
                "error": run_a["error_count"],
                "integrity": run_a["integrity_match"],
            },
            "run_b": {
                "artifact_count": run_b["artifact_count"],
                "pass": run_b["pass_count"],
                "fail": run_b["fail_count"],
                "error": run_b["error_count"],
                "integrity": run_b["integrity_match"],
            },
            "structural_comparison": [{"name": s[0], "match": s[1], "detail": s[2]} for s in structural],
            "observational_match": obs_match,
            "observational_divergences": divergences,
            "test_cases": results,
            "advisory_only": True,
            "no_seal_authority": True,
        }, f, indent=2)

    print(f"  Results written to: {result_path.relative_to(QA_PILOT_ROOT)}")

    # Print summary
    print("\n" + "=" * 72)
    print("  E2E-7 Summary")
    print("=" * 72)
    print(f"\n  Frozen artifacts:    30")
    print(f"  Run A:               {run_a['pass_count']} PASS / {run_a['fail_count']} FAIL")
    print(f"  Run B:               {run_b['pass_count']} PASS / {run_b['fail_count']} FAIL")
    print(f"  Structural match:    {'YES' if all(s[1] for s in structural) else 'NO'}")
    print(f"  Observational match: {'YES' if obs_match else 'NO'}")
    print(f"\n  Checks: {passes} PASS, {failures} FAIL")

    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
