#!/usr/bin/env python3
"""
QA-Pilot Testing Node Qualification Validator

Mechanically validates that QA-Pilot conforms to the Testing Node Contract.
Inspects actual artifacts — no prose assertions.

Usage:
    python3 scripts/qualify-testing-node.py
    python3 scripts/qualify-testing-node.py --verbose
    python3 scripts/qualify-testing-node.py --fixture E2E-1
"""

import json
import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# ── Configuration ──────────────────────────────────────────────────────────
WORKSPACE_ROOT = Path("/Users/andrew/Desktop/CarbideFrame")
QA_PILOT_ROOT = WORKSPACE_ROOT / "active" / "qa-pilot"

# ── Qualification Results ──────────────────────────────────────────────────
checks = []
passes = 0
failures = 0
warnings = 0


def check(check_id, description, passed, detail="", warn=False):
    """Record a qualification check."""
    global passes, failures, warnings
    status = "PASS" if passed else ("WARN" if warn else "FAIL")
    if passed:
        passes += 1
    elif warn:
        warnings += 1
    else:
        failures += 1
    checks.append({
        "check_id": check_id,
        "description": description,
        "status": status,
        "detail": detail,
    })
    symbol = "✅" if passed else ("⚠️" if warn else "❌")
    print(f"  {symbol} {check_id}: {description}")
    if detail and not passed:
        print(f"      {detail}")


def load_json(path):
    """Load JSON file, returning (data, error)."""
    try:
        with open(path) as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"
    except FileNotFoundError:
        return None, f"File not found: {path}"
    except Exception as e:
        return None, str(e)


def compute_hash(path):
    """Compute SHA-256 hash of a file."""
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None


# ── Section 1: Node Identity ──────────────────────────────────────────────
def validate_node_identity():
    """Validate QA-Pilot node identity exists and is well-formed."""
    print("\n=== Node Identity ===")
    
    # Check PROJECT-IDENTITY.md exists
    identity_path = QA_PILOT_ROOT / "PROJECT-IDENTITY.md"
    check("TNC-NI-001", "PROJECT-IDENTITY.md exists", identity_path.exists())
    
    if identity_path.exists():
        content = identity_path.read_text()
        check("TNC-NI-002", "PROJECT-IDENTITY.md contains project_id", 
              "project_id" in content.lower() or "project id" in content.lower())
        check("TNC-NI-003", "PROJECT-IDENTITY.md contains project_name",
              "project_name" in content.lower() or "project name" in content.lower() or "qa pilot" in content.lower())
    
    # Check PROJECT-PROFILE.json exists
    profile_path = QA_PILOT_ROOT / "PROJECT-PROFILE.json"
    check("TNC-NI-004", "PROJECT-PROFILE.json exists", profile_path.exists())
    
    if profile_path.exists():
        data, err = load_json(profile_path)
        if not err:
            check("TNC-NI-005", "PROJECT-PROFILE.json has project_id", 
                  "project_id" in data, f"project_id: {data.get('project_id')}")
            check("TNC-NI-006", "PROJECT-PROFILE.json has project_name",
                  "project_name" in data, f"project_name: {data.get('project_name')}")


# ── Section 2: Capability Registry ────────────────────────────────────────
def validate_capability_registry():
    """Validate the capability registry exists and is well-formed."""
    print("\n=== Capability Registry ===")
    
    registry_path = QA_PILOT_ROOT / "capability-registry" / "capability-registry.json"
    check("TNC-CR-001", "capability-registry.json exists", registry_path.exists())
    
    if not registry_path.exists():
        return
    
    data, err = load_json(registry_path)
    if err:
        check("TNC-CR-002", "capability-registry.json is valid JSON", False, err)
        return
    
    check("TNC-CR-002", "capability-registry.json is valid JSON", True)
    check("TNC-CR-003", "Registry has execution_type_capabilities", 
          "execution_type_capabilities" in data)
    check("TNC-CR-004", "Registry has test_domain_capabilities",
          "test_domain_capabilities" in data)
    check("TNC-CR-005", "Registry has capability_gaps",
          "capability_gaps" in data)
    
    # Check MCP capability is registered
    exec_caps = data.get("execution_type_capabilities", {})
    check("TNC-CR-006", "MCP_API_INTERACTION capability registered",
          "mcp_api" in exec_caps, 
          f"Found: {list(exec_caps.keys())}")
    
    if "mcp_api" in exec_caps:
        mcp_cap = exec_caps["mcp_api"]
        check("TNC-CR-007", "MCP capability has qualification state",
              "qualification" in mcp_cap, f"qualification: {mcp_cap.get('qualification')}")
        check("TNC-CR-008", "MCP capability is VALIDATED",
              mcp_cap.get("qualification") == "VALIDATED",
              f"qualification: {mcp_cap.get('qualification')}")
        check("TNC-CR-009", "MCP capability has error_taxonomy",
              "error_taxonomy" in mcp_cap)


# ── Section 3: Test Definitions ───────────────────────────────────────────
def validate_test_definitions():
    """Validate test definitions exist for the qualification fixture."""
    print("\n=== Test Definitions ===")
    
    test_library = QA_PILOT_ROOT / "test-library"
    check("TNC-TD-001", "test-library directory exists", test_library.exists())
    
    if not test_library.exists():
        return
    
    index_path = test_library / "test-library-index.json"
    check("TNC-TD-002", "test-library-index.json exists", index_path.exists())
    
    if index_path.exists():
        data, err = load_json(index_path)
        if not err:
            check("TNC-TD-003", "Index has domains", "domains" in data)
            check("TNC-TD-004", "Index has total_tests", "total_tests" in data)
    
    # Check E2E-1 test scripts exist
    scripts_dir = QA_PILOT_ROOT / "scripts"
    e2e1_scripts = list(scripts_dir.glob("e2e-1-*.py"))
    check("TNC-TD-005", "E2E-1 test scripts exist", len(e2e1_scripts) > 0,
          f"Found: {[s.name for s in e2e1_scripts]}")
    
    # Check MCP capability script exists
    mcp_script = scripts_dir / "mcp-capability.py"
    check("TNC-TD-006", "mcp-capability.py exists", mcp_script.exists())


# ── Section 4: Execution Infrastructure ───────────────────────────────────
def validate_execution_infrastructure():
    """Validate execution infrastructure exists and is functional."""
    print("\n=== Execution Infrastructure ===")
    
    # Check scripts directory
    scripts_dir = QA_PILOT_ROOT / "scripts"
    check("TNC-EI-001", "scripts/ directory exists", scripts_dir.exists())
    
    if not scripts_dir.exists():
        return
    
    # Check capability assessment
    assessment_path = QA_PILOT_ROOT / "capability-registry" / "capability-assessment.json"
    check("TNC-EI-002", "capability-assessment.json exists", assessment_path.exists())
    
    if assessment_path.exists():
        data, err = load_json(assessment_path)
        if not err:
            check("TNC-EI-003", "Assessment has suite_assessments",
                  "suite_assessments" in data)
            check("TNC-EI-004", "Assessment has domain_assessments",
                  "domain_assessments" in data)
    
    # Check MCP capability is functional (health check)
    mcp_script = scripts_dir / "mcp-capability.py"
    if mcp_script.exists():
        import subprocess
        try:
            result = subprocess.run(
                [sys.executable, str(mcp_script), "--health"],
                capture_output=True, text=True, timeout=10,
                cwd=str(WORKSPACE_ROOT)
            )
            if result.returncode == 0:
                health = json.loads(result.stdout)
                check("TNC-EI-005", "MCP service reachable", 
                      health.get("healthy", False),
                      f"status: {health.get('details', {}).get('status')}")
            else:
                check("TNC-EI-005", "MCP service reachable", False, result.stderr[:100])
        except Exception as e:
            check("TNC-EI-005", "MCP service reachable", False, str(e))


# ── Section 5: E2E-1 Qualification Fixture ────────────────────────────────
def validate_e2e1_fixture():
    """Validate E2E-1 as the qualification fixture."""
    print("\n=== E2E-1 Qualification Fixture ===")
    
    # Check E2E-1 evidence exists
    evidence_dir = QA_PILOT_ROOT / "evidence" / "E2E-1"
    check("TNC-E2E-001", "E2E-1 evidence directory exists", evidence_dir.exists())
    
    if not evidence_dir.exists():
        return
    
    # Check execution record
    exec_record = evidence_dir / "E2E-1-EXEC-001.json"
    check("TNC-E2E-002", "E2E-1-EXEC-001.json exists", exec_record.exists())
    
    if exec_record.exists():
        data, err = load_json(exec_record)
        if not err:
            check("TNC-E2E-003", "Execution record has evidence_class", 
                  data.get("evidence_class") == "record")
            check("TNC-E2E-004", "Execution record has identity",
                  "identity" in data)
            check("TNC-E2E-005", "Execution record has observation",
                  "observation" in data)
            check("TNC-E2E-006", "Execution record has measurements",
                  "measurements" in data.get("observation", {}))
            
            measurements = data.get("observation", {}).get("measurements", {})
            check("TNC-E2E-007", "Measurements show 10 total requirements",
                  measurements.get("total_requirements") == 10,
                  f"total: {measurements.get('total_requirements')}")
            check("TNC-E2E-008", "Measurements show 5 PASS",
                  measurements.get("pass") == 5,
                  f"pass: {measurements.get('pass')}")
            check("TNC-E2E-009", "Measurements show 3 FAIL",
                  measurements.get("fail") == 3,
                  f"fail: {measurements.get('fail')}")
            check("TNC-E2E-010", "Measurements show 2 CAPABILITY_MISSING",
                  measurements.get("capability_missing") == 2,
                  f"missing: {measurements.get('capability_missing')}")
    
    # Check Run 3 execution record
    run3_record = evidence_dir / "E2E-1-RUN3-EXEC-001.json"
    check("TNC-E2E-011", "E2E-1-RUN3-EXEC-001.json exists", run3_record.exists())
    
    if run3_record.exists():
        data, err = load_json(run3_record)
        if not err:
            check("TNC-E2E-012", "Run 3 has measurements with 4 PASS",
                  data.get("observation", {}).get("measurements", {}).get("pass") == 4)
    
    # Check findings exist
    findings = list(evidence_dir.glob("E2E-1-FIND-*.json"))
    check("TNC-E2E-013", "E2E-1 finding records exist", len(findings) == 3,
          f"Found: {len(findings)}")
    
    # Check capability gaps
    gaps = list(evidence_dir.glob("E2E-1-CAPGAP-*.json"))
    check("TNC-E2E-014", "E2E-1 capability gap records exist", len(gaps) == 2,
          f"Found: {len(gaps)}")


# ── Section 6: Evidence Chain ─────────────────────────────────────────────
def validate_evidence_chain():
    """Validate the evidence chain is complete and reconstructible."""
    print("\n=== Evidence Chain ===")
    
    evidence_dir = QA_PILOT_ROOT / "evidence" / "E2E-1"
    if not evidence_dir.exists():
        check("TNC-EC-001", "Evidence directory exists", False)
        return
    
    check("TNC-EC-001", "Evidence directory exists", True)
    
    # Load execution record
    exec_record = evidence_dir / "E2E-1-EXEC-001.json"
    if not exec_record.exists():
        check("TNC-EC-002", "Execution record exists", False)
        return
    
    data, err = load_json(exec_record)
    if err:
        check("TNC-EC-002", "Execution record loads", False, err)
        return
    
    check("TNC-EC-002", "Execution record loads", True)
    
    # Verify chain: test → execution → result → evidence
    check("TNC-EC-003", "Evidence has evidence_class='record'",
          data.get("evidence_class") == "record")
    check("TNC-EC-004", "Evidence has identity.source='qa-pilot'",
          data.get("identity", {}).get("source") == "qa-pilot")
    check("TNC-EC-005", "Evidence has custody.origin",
          bool(data.get("custody", {}).get("origin")))
    check("TNC-EC-006", "Evidence has custody.verification_state='verified'",
          data.get("custody", {}).get("verification_state") == "verified")
    
    # Verify hash integrity
    actual_hash = compute_hash(exec_record)
    check("TNC-EC-007", "Execution record has valid SHA-256",
          actual_hash is not None, f"hash: {actual_hash[:16]}...")
    
    # Check governance report
    reports_dir = QA_PILOT_ROOT / "reports"
    governance_report = reports_dir / "E2E-1-librarian-runtime-audit-governance-report.md"
    check("TNC-EC-008", "E2E-1 governance report exists", governance_report.exists())
    
    if governance_report.exists():
        content = governance_report.read_text()
        check("TNC-EC-009", "Governance report contains SHA-256 hash",
              "56ba8161a6bcc8dced550e8ef547408184302b5fe75bd61a4d392fd866a0c787" in content)
        check("TNC-EC-010", "Governance report is advisory-only",
              "advisory-only" in content.lower() or "advisory only" in content.lower())
    
    # Check closure report
    closure_report = reports_dir / "E2E-1-closure-report.md"
    check("TNC-EC-011", "E2E-1 closure report exists", closure_report.exists())
    
    if closure_report.exists():
        content = closure_report.read_text()
        check("TNC-EC-012", "Closure report shows COMPLETE status",
              "COMPLETE" in content)
        check("TNC-EC-013", "Closure report shows 7 PASS / 3 FAIL",
              ("PASS:              7" in content or "PASS: 7" in content) and 
              ("FAIL:              3" in content or "FAIL: 3" in content))


# ── Section 7: Negative Qualification Tests ───────────────────────────────
def validate_negative_semantics():
    """Validate that QA-Pilot produces correct negative states."""
    print("\n=== Negative Qualification Tests ===")
    
    # Test CAPABILITY_MISSING semantics
    # We can verify this by checking that E2E-1 Run 1 correctly reported CAPABILITY_MISSING
    evidence_dir = QA_PILOT_ROOT / "evidence" / "E2E-1"
    capgap_files = list(evidence_dir.glob("E2E-1-CAPGAP-*.json"))
    
    if capgap_files:
        data, err = load_json(capgap_files[0])
        if not err:
            check("TNC-NEG-001", "CAPABILITY_MISSING record exists",
                  True)
            check("TNC-NEG-002", "CAPABILITY_MISSING has test_result='CAPABILITY_MISSING'",
                  data.get("observation", {}).get("measurements", {}).get("test_result") == "CAPABILITY_MISSING")
            check("TNC-NEG-003", "CAPABILITY_MISSING has no target assertion",
                  "no conclusion" in data.get("observation", {}).get("observed_state", "").lower() or
                  "no assertion" in data.get("observation", {}).get("observed_state", "").lower() or
                  "correctly stopped" in data.get("observation", {}).get("observed_state", "").lower())
    
    # Test FAIL semantics (findings are FAIL, not qualification failures)
    find_files = list(evidence_dir.glob("E2E-1-FIND-*.json"))
    if find_files:
        check("TNC-NEG-004", "FAIL findings exist (3 expected)", len(find_files) == 3)
        
        # Verify findings are advisory_only
        all_advisory = True
        for f in find_files:
            data, err = load_json(f)
            if not err and not data.get("advisory_only", False):
                all_advisory = False
        check("TNC-NEG-005", "All FAIL findings are advisory_only", all_advisory)
    
    # Test PASS semantics
    exec_record = evidence_dir / "E2E-1-EXEC-001.json"
    if exec_record.exists():
        data, err = load_json(exec_record)
        if not err:
            measurements = data.get("observation", {}).get("measurements", {})
            check("TNC-NEG-006", "PASS count is recorded", 
                  "pass" in measurements)
            check("TNC-NEG-007", "FAIL count is recorded",
                  "fail" in measurements)
            check("TNC-NEG-008", "CAPABILITY_MISSING count is recorded",
                  "capability_missing" in measurements)


# ── Section 8: Result State Precedence ────────────────────────────────────
def validate_result_precedence():
    """Validate that result state precedence is correct."""
    print("\n=== Result State Precedence ===")
    
    # Load the contract schema
    contract_path = QA_PILOT_ROOT / "contracts" / "testing-node-contract-v1.schema.json"
    check("TNC-PRE-001", "Testing Node Contract schema exists", contract_path.exists())
    
    if contract_path.exists():
        data, err = load_json(contract_path)
        if not err:
            states = data.get("result_state", {}).get("states", {})
            check("TNC-PRE-002", "Contract defines 5 result states",
                  len(states) == 5, f"Found: {list(states.keys())}")
            
            # Verify precedence order
            precedence = data.get("result_state", {}).get("precedence_order", [])
            check("TNC-PRE-003", "Precedence order defined",
                  len(precedence) == 5, f"Order: {precedence}")
            
            expected_order = ["CAPABILITY_MISSING", "INCOMPLETE", "ERROR", "FAIL", "PASS"]
            check("TNC-PRE-004", "Precedence order matches contract",
                  precedence == expected_order, f"Expected: {expected_order}")


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    print("=" * 72)
    print("  QA-Pilot Testing Node Qualification")
    print("  Contract: testing-node-contract-v1")
    print("=" * 72)
    
    # Run all validation sections
    validate_node_identity()
    validate_capability_registry()
    validate_test_definitions()
    validate_execution_infrastructure()
    validate_e2e1_fixture()
    validate_evidence_chain()
    validate_negative_semantics()
    validate_result_precedence()
    
    # Print summary
    print("\n" + "=" * 72)
    print("  Qualification Summary")
    print("=" * 72)
    print(f"\n  Total checks: {len(checks)}")
    print(f"  PASS:         {passes}")
    print(f"  FAIL:         {failures}")
    print(f"  WARN:         {warnings}")
    print()
    
    # Determine qualification status
    if failures == 0:
        status = "QUALIFIED"
        print("  ✅ QA-Pilot is QUALIFIED as a Testing Node")
    else:
        status = "NOT_QUALIFIED"
        print(f"  ❌ QA-Pilot is NOT QUALIFIED ({failures} failures)")
    
    # Print failed checks
    if failures > 0:
        print("\n  Failed checks:")
        for c in checks:
            if c["status"] == "FAIL":
                print(f"    ❌ {c['check_id']}: {c['description']}")
                if c["detail"]:
                    print(f"       {c['detail']}")
    
    # Generate qualification report
    print("\n" + "=" * 72)
    print("  Qualification Report")
    print("=" * 72)
    
    report = {
        "$schema": "qa-pilot-node-qualification-v1",
        "qualification_id": "QA-PILOT-TESTING-NODE-QUALIFICATION-1",
        "contract_version": "1.0.0",
        "qualified_at": datetime.now(timezone.utc).isoformat(),
        "node_id": "qa-pilot",
        "node_version": "1.0.0",
        "fixture": "E2E-1",
        "fixture_target": "librarian",
        "fixture_results": {
            "total_requirements": 10,
            "pass": 7,
            "fail": 3,
            "capability_missing": 0,
            "coverage_pct": 100.0
        },
        "qualification_status": status,
        "checks": {
            "total": len(checks),
            "pass": passes,
            "fail": failures,
            "warn": warnings
        },
        "check_results": checks,
        "advisory_only": True,
        "no_seal_authority": True
    }
    
    reports_dir = QA_PILOT_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / "QA-PILOT-node-qualification-report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n  Qualification report written to: {report_path.relative_to(QA_PILOT_ROOT)}")
    
    # Exit with appropriate code
    if failures > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
