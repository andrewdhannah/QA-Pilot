#!/usr/bin/env python3
"""
validate-qa-pilot-assurance-governance-maturity.py — Governance Maturity Validator

Validates that the governance maturity institutionalization is complete:
  GM-1: Governance policy documented
  GM-2: Maturity model defined
  GM-3: Operating cadence established
  GM-4: All 5 maturity stages assessable
  GM-5: Drift detection criteria defined
  GM-6: Governance documents consistent with existing invariants
  GM-7: No new authority paths introduced
  GM-8: Calibration baseline preserved
"""

import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs", "governance")


def check_file_exists(path, name):
    exists = os.path.exists(path)
    if not exists:
        return (name, False, "File not found")
    with open(path) as f:
        content = f.read()
    return (name, True, f"Present ({len(content)} chars)")


def check_content_contains(path, term, name):
    if not os.path.exists(path):
        return (name, False, "File not found")
    with open(path) as f:
        content = f.read()
    found = term in content
    return (name, found, f"Contains '{term}': {'yes' if found else 'no'}")


def main():
    policy_path = os.path.join(DOCS_DIR, "QA-PILOT-ASSURANCE-GOVERNANCE-POLICY.md")
    maturity_path = os.path.join(DOCS_DIR, "QA-PILOT-ASSURANCE-MATURITY-MODEL.md")
    cadence_path = os.path.join(DOCS_DIR, "QA-PILOT-ASSURANCE-OPERATING-CADENCE.md")

    checks = []

    # GM-1: Governance policy documented
    checks.append(check_file_exists(policy_path, "GM-1: Governance policy"))
    if os.path.exists(policy_path):
        checks.append(check_content_contains(policy_path, "Projection, Not Decision",
                     "GM-1a: Projection principle"))
        checks.append(check_content_contains(policy_path, "Owner Decision Authority",
                     "GM-1b: Owner authority principle"))

    # GM-2: Maturity model defined
    checks.append(check_file_exists(maturity_path, "GM-2: Maturity model"))
    if os.path.exists(maturity_path):
        for stage in ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5"]:
            checks.append(check_content_contains(maturity_path, stage,
                         f"GM-2a: {stage} defined"))

    # GM-3: Operating cadence established
    checks.append(check_file_exists(cadence_path, "GM-3: Operating cadence"))
    if os.path.exists(cadence_path):
        checks.append(check_content_contains(cadence_path, "Daily",
                     "GM-3a: Daily rhythm"))
        checks.append(check_content_contains(cadence_path, "Weekly",
                     "GM-3b: Weekly rhythm"))
        checks.append(check_content_contains(cadence_path, "Per-Sprint",
                     "GM-3c: Per-sprint rhythm"))
        checks.append(check_content_contains(cadence_path, "Drift Detection",
                     "GM-3d: Drift detection"))

    # GM-4: All stages assessable
    if os.path.exists(maturity_path):
        checks.append(check_content_contains(maturity_path, "Maturity Assessment",
                     "GM-4: Maturity assessment summary"))

    # GM-5: Drift criteria defined
    if os.path.exists(cadence_path):
        checks.append(check_content_contains(cadence_path, "What It Indicates",
                     "GM-5: Drift signal definitions"))

    # GM-6: Consistent with invariants
    if os.path.exists(policy_path):
        checks.append(check_content_contains(policy_path, "not auto-resolve",
                     "GM-6: Projection invariant preserved"))

    # GM-7: No new authority paths
    for path, name in [(policy_path, "policy"), (maturity_path, "maturity"), (cadence_path, "cadence")]:
        if os.path.exists(path):
            with open(path) as f:
                content = f.read().lower()
            for term in ["auto-approve", "auto-seal", "bypass owner", "automated decision"]:
                if term in content:
                    checks.append((f"GM-7: Authority check in {name}", False,
                                   f"Contains: {term}"))
                    break
            else:
                checks.append((f"GM-7: No authority leakage in {name}", True,
                               "Clean"))

    # GM-8: Calibration baseline preserved
    cal_path = os.path.join(PROJECT_ROOT, "data", "assurance-baseline-2026-07-20.json")
    if os.path.exists(cal_path):
        checks.append(("GM-8: Calibration baseline preserved", True,
                       "Baseline file present"))
    else:
        checks.append(("GM-8: Calibration baseline", False, "Not found"))

    # Print results
    all_pass = all(c[1] for c in checks)
    print("=== Governance Maturity Validation (GM-1 through GM-8) ===")
    for name, passed, detail in checks:
        icon = "✅" if passed else "❌"
        print(f"  {icon} {name}: {detail}")

    print(f"\n{'✅ ALL CHECKS PASS' if all_pass else '❌ SOME FAILED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
