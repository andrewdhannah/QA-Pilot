#!/usr/bin/env python3
"""
QA Pilot Training Content Model Validator — QA-PILOT-TRAINING-CONTENT-MODEL-1

Validates training content artifacts against schema and governance rules.

Rules:
    CM-1:  schema_version must be 'training-content-v1'
    CM-2:  artifact_type must be one of 7 known types
    CM-3:  intended_audience must be a valid audience
    CM-4:  governance.authority_posture must be 'advisory'
    CM-5:  governance.owner_decision_required_for_publish must be true
    CM-6:  governance.validation_status must be a valid status
    CM-7:  provenance.librarian_sources must have at least 1 entry
    CM-8:  provenance.source_hash must be valid SHA-256
    CM-9:  Every content section must have at least 1 source reference
    CM-10: validation_exercise and workflow_tutorial must have exercises in all sections
    CM-11: content.sections must have at least 1 section
    CM-12: No authority expansion patterns in content body
    CM-13: No Librarian mutation paths in content
    CM-14: pack_id must match TC- pattern
"""

import json, os, re, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-training-content-model"
SCHEMA_FILE = REPO_ROOT / "docs" / "schemas" / "qa-pilot-training-content-model.schema.json"
GOV_DOC = REPO_ROOT / "docs" / "governance" / "QA-PILOT-TRAINING-CONTENT-MODEL.md"

VALID_ARTIFACT_TYPES = [
    "onboarding_guide", "operator_guide", "developer_guide",
    "troubleshooting_guide", "architecture_explanation",
    "workflow_tutorial", "validation_exercise"
]
VALID_AUDIENCES = ["onboarding", "operator", "developer", "architect", "all"]
VALID_VALIDATION_STATUSES = ["draft", "validated", "failed", "owner_approved"]
EXERCISE_REQUIRED_TYPES = ["validation_exercise", "workflow_tutorial"]
FORBIDDEN_AUTHORITY_PATTERNS = [
    "this is authoritative", "canonical truth", "binding requirement",
    "must be followed by all", "automatically applies"
]


def load_json(path):
    with open(path) as f:
        return json.load(f)


def check_cm_1(data):
    val = data.get("schema_version", "")
    passed = val == "training-content-v1"
    return (passed, f"schema_version = '{val}'" if not passed else "schema_version is training-content-v1")

def check_cm_2(data):
    val = data.get("artifact_type", "")
    passed = val in VALID_ARTIFACT_TYPES
    return (passed, f"artifact_type = '{val}'" if not passed else f"artifact_type is '{val}'")

def check_cm_3(data):
    val = data.get("intended_audience", "")
    passed = val in VALID_AUDIENCES
    return (passed, f"intended_audience = '{val}'" if not passed else f"audience is '{val}'")

def check_cm_4(data):
    gov = data.get("governance", {})
    val = gov.get("authority_posture", "")
    passed = val == "advisory"
    return (passed, f"authority_posture = '{val}'" if not passed else "authority_posture is advisory")

def check_cm_5(data):
    gov = data.get("governance", {})
    val = gov.get("owner_decision_required_for_publish")
    passed = val is True
    return (passed, f"owner_decision_required = {val}" if not passed else "owner_decision_required is true")

def check_cm_6(data):
    gov = data.get("governance", {})
    val = gov.get("validation_status", "")
    passed = val in VALID_VALIDATION_STATUSES
    return (passed, f"validation_status = '{val}'" if not passed else f"status is '{val}'")

def check_cm_7(data):
    prov = data.get("provenance", {})
    sources = prov.get("librarian_sources", [])
    passed = len(sources) >= 1
    return (passed, "No librarian_sources" if not passed else f"{len(sources)} source(s)")

def check_cm_8(data):
    prov = data.get("provenance", {})
    val = prov.get("source_hash", "")
    passed = bool(re.match(r"^[a-f0-9]{64}$", val))
    return (passed, f"source_hash invalid" if not passed else "source_hash valid")

def check_cm_9(data):
    content = data.get("content", {})
    sections = content.get("sections", [])
    for s in sections:
        srcs = s.get("sources", [])
        if len(srcs) < 1:
            return (False, f"Section '{s.get('id','?')}' has no source references")
    return (True, "All sections have source references")

def check_cm_10(data):
    atype = data.get("artifact_type", "")
    if atype not in EXERCISE_REQUIRED_TYPES:
        return (True, f"Not {atype} — skip")
    content = data.get("content", {})
    sections = content.get("sections", [])
    for s in sections:
        exercises = s.get("exercises", [])
        if len(exercises) < 1:
            return (False, f"Section '{s.get('id','?')}' missing exercises (required for {atype})")
    return (True, f"All sections have exercises ({atype})")

def check_cm_11(data):
    content = data.get("content", {})
    sections = content.get("sections", [])
    passed = len(sections) >= 1
    return (passed, "No content sections" if not passed else f"{len(sections)} section(s)")

def check_cm_12(data):
    content = data.get("content", {})
    body_text = json.dumps(content).lower()
    for pat in FORBIDDEN_AUTHORITY_PATTERNS:
        if pat.lower() in body_text:
            return (False, f"Contains authority claim: '{pat}'")
    return (True, "No authority expansion in content")

def check_cm_13(data):
    body_text = json.dumps(data).lower()
    forbidden = ["seal_action", "approve_action", "merge_action", "librarian db write",
                 "librarian mcp register", "sources/app/", "mcpcontroller.swift"]
    for pat in forbidden:
        if pat in body_text:
            return (False, f"Contains mutation path: '{pat}'")
    return (True, "No Librarian mutation paths")

def check_cm_14(data):
    pid = data.get("pack_id", "")
    passed = bool(re.match(r"^TC-[A-Z0-9-]+$", pid))
    return (passed, f"pack_id = '{pid}'" if not passed else "pack_id matches TC- pattern")


ALL_CHECKS = [
    ("CM-1", check_cm_1, "Schema version correct"),
    ("CM-2", check_cm_2, "Artifact type known"),
    ("CM-3", check_cm_3, "Audience valid"),
    ("CM-4", check_cm_4, "Authority posture advisory"),
    ("CM-5", check_cm_5, "Owner decision required"),
    ("CM-6", check_cm_6, "Validation status valid"),
    ("CM-7", check_cm_7, "Provenance has sources"),
    ("CM-8", check_cm_8, "Source hash valid"),
    ("CM-9", check_cm_9, "Sections have source refs"),
    ("CM-10", check_cm_10, "Exercise requirement met"),
    ("CM-11", check_cm_11, "Sections present"),
    ("CM-12", check_cm_12, "No authority expansion"),
    ("CM-13", check_cm_13, "No mutation paths"),
    ("CM-14", check_cm_14, "Pack ID format"),
]


def validate_fixture(path):
    try:
        data = load_json(path)
    except Exception as e:
        return (os.path.basename(path), {"all_pass": False, "error": str(e)})
    results = []
    all_pass = True
    for rule_id, func, desc in ALL_CHECKS:
        try:
            passed, msg = func(data)
        except Exception as e:
            passed, msg = False, str(e)
        results.append({"rule": rule_id, "description": desc, "passed": passed, "message": msg})
        if not passed:
            all_pass = False
    return (os.path.basename(path), {"all_pass": all_pass, "checks": results})


def main():
    args = sys.argv[1:]
    if "--list-rules" in args:
        for rid, _, desc in ALL_CHECKS:
            print(f"  {rid}: {desc}")
        return 0

    include_invalid = "--include-invalid" in args
    if not FIXTURES_DIR.exists():
        print(f"ERROR: Fixtures not found: {FIXTURES_DIR}")
        return 1

    files = sorted(FIXTURES_DIR.glob("*.json" if include_invalid else "valid-*.json"))
    if not files:
        print("No fixture files found")
        return 1

    valid_pass = valid_total = invalid_pass = invalid_total = 0
    for f in files:
        is_invalid = f.name.startswith("invalid-")
        fname, r = validate_fixture(str(f))
        if not is_invalid:
            valid_total += 1
            if r.get("all_pass"): valid_pass += 1
        else:
            invalid_total += 1
            if not r.get("all_pass"): invalid_pass += 1
        prefix = "✅" if r.get("all_pass") else "❌"
        cc = len(r.get("checks", []))
        pc = sum(1 for c in r.get("checks", []) if c["passed"])
        print(f"  {prefix} {fname} — {pc}/{cc} checks pass")
        if not r.get("all_pass"):
            for c in r.get("checks", []):
                if not c["passed"]:
                    print(f"       FAIL {c['rule']}: {c['message']}")

    print()
    if include_invalid:
        print(f"Valid fixtures:   {valid_pass}/{valid_total} passed")
        print(f"Invalid fixtures: {invalid_pass}/{invalid_total} rejected")

    all_ok = (valid_pass == valid_total if valid_total > 0 else True)
    all_rejected = (invalid_pass == invalid_total if invalid_total > 0 else True)

    if all_ok and all_rejected:
        print("\n✅ ALL CHECKS PASS")
        return 0
    failures = []
    if not all_ok: failures.append("valid fixtures")
    if not all_rejected: failures.append("invalid rejection")
    print(f"\n❌ FAILED: {', '.join(failures)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
