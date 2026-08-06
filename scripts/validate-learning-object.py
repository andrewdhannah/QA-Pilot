#!/usr/bin/env python3
"""
Learning Object v1 Validator — QA-PILOT-LEARNING-OBJECT-CONTRACT-1

Validates learning objects against the learning-object-v1.schema.json contract.
Enforces the invariant: learning objects REFERENCE evidence — they do not CREATE, duplicate, or replace evidence.

Rules:
  LO-1:  schema is learning-object-v1
  LO-2:  id matches pattern LO-[A-Z]+-[0-9]{3,}
  LO-3:  title is present and non-empty
  LO-4:  source block is present with finding_code, evidence_refs, confidence
  LO-5:  finding_code matches valid diagnostic pattern
  LO-6:  evidence_refs is non-empty array
  LO-7:  learning block present with objective and explanation
  LO-8:  learning.explanation is distinct from finding (>=20 chars, educational context)
  LO-9:  assessment block present with quiz_refs and scoring_model
  LO-10: scoring_model is valid enum value
  LO-11: certification block present with criteria and passing_score
  LO-12: certification.criteria descriptions do not contain seal/approve/merge/authorize keywords
  LO-13: no top-level evidence creation fields (findings, evidence, seal, approve)
  LO-14: advisory_only is true
  LO-15: no_seal_authority is true

Usage:
    python3 scripts/validate-learning-object.py <fixture-path>...
    python3 scripts/validate-learning-object.py --all
    python3 scripts/validate-learning-object.py --list-rules
    python3 scripts/validate-learning-object.py --include-invalid
"""

import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "learning-object-v1"
SCHEMA_FILE = REPO_ROOT / "docs" / "schemas" / "learning-object-v1.schema.json"

VALID_SCORING_MODELS = {"evaluateSubmission", "quiz_only", "exercise_only", "composite"}
FORBIDDEN_CERT_KEYWORDS = {"seal", "approve", "merge", "authorize"}
EVIDENCE_CREATION_FIELDS = {"findings", "evidence", "seal", "approve"}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_lo_1(data):
    """LO-1: schema is learning-object-v1."""
    s = data.get("schema")
    if s == "learning-object-v1":
        return True, f"schema correct: {s}"
    return False, f"schema mismatch: expected learning-object-v1, got {s}"


def check_lo_2(data):
    """LO-2: id matches pattern LO-<CODE>...-<SEQ>."""
    lid = data.get("id", "")
    # Pattern: LO- (one or more uppercase/digit segments separated by -) then -NNN
    if re.match(r"^LO-[A-Z0-9]+(-[A-Z0-9]+)*-[0-9]{3,}$", lid):
        return True, f"id valid: {lid}"
    return False, f"id invalid: {lid}"


def check_lo_3(data):
    """LO-3: title is present and non-empty."""
    title = data.get("title", "")
    if title and isinstance(title, str) and len(title.strip()) >= 3:
        return True, f"title present: {title[:60]}..."
    return False, "title missing or too short (<3 chars)"


def check_lo_4(data):
    """LO-4: source block present with required fields."""
    source = data.get("source")
    if not source or not isinstance(source, dict):
        return False, "source block missing or not an object"
    required = ["finding_code", "evidence_refs", "confidence"]
    missing = [r for r in required if r not in source]
    if missing:
        return False, f"source missing required fields: {missing}"
    return True, "source block present with all required fields"


def check_lo_5(data):
    """LO-5: finding_code matches valid diagnostic pattern."""
    fc = data.get("source", {}).get("finding_code", "")
    if re.match(r"^(EV-[A-Z]+-[0-9]{3,}|F-[0-9]{4,})$", fc):
        return True, f"finding_code valid: {fc}"
    return False, f"finding_code invalid: {fc}"


def check_lo_6(data):
    """LO-6: evidence_refs is non-empty array."""
    refs = data.get("source", {}).get("evidence_refs", [])
    if not isinstance(refs, list) or len(refs) == 0:
        return False, f"evidence_refs is not a non-empty array: {type(refs).__name__} len={len(refs) if isinstance(refs, list) else 'N/A'}"
    for i, ref in enumerate(refs):
        if not isinstance(ref, dict) or "type" not in ref or "ref" not in ref:
            return False, f"evidence_refs[{i}] missing type or ref"
    return True, f"evidence_refs: {len(refs)} valid references"


def check_lo_7(data):
    """LO-7: learning block present with objective and explanation."""
    learning = data.get("learning")
    if not learning or not isinstance(learning, dict):
        return False, "learning block missing or not an object"
    if "objective" not in learning:
        return False, "learning.objective missing"
    if "explanation" not in learning:
        return False, "learning.explanation missing"
    return True, "learning block present with objective and explanation"


def check_lo_8(data):
    """LO-8: learning.explanation is distinct from finding (>=20 chars, educational context)."""
    explanation = data.get("learning", {}).get("explanation", "")
    if not isinstance(explanation, str) or len(explanation) < 20:
        return False, f"learning.explanation too short ({len(explanation)} chars, min 20)"
    # Check for educational context keywords as heuristic
    edu_keywords = ["you will", "learner will", "understand", "think of", "like a", "similar to", "means"]
    has_context = any(kw in explanation.lower() for kw in edu_keywords)
    if not has_context:
        return False, "learning.explanation lacks educational context markers (heuristic)"
    return True, f"explanation distinct and educational ({len(explanation)} chars)"


def check_lo_9(data):
    """LO-9: assessment block present with quiz_refs and scoring_model."""
    assessment = data.get("assessment")
    if not assessment or not isinstance(assessment, dict):
        return False, "assessment block missing or not an object"
    if "quiz_refs" not in assessment:
        return False, "assessment.quiz_refs missing"
    if "scoring_model" not in assessment:
        return False, "assessment.scoring_model missing"
    quiz_refs = assessment.get("quiz_refs", [])
    if not isinstance(quiz_refs, list) or len(quiz_refs) == 0:
        return False, "assessment.quiz_refs must be non-empty array"
    return True, "assessment block present with quiz_refs and scoring_model"


def check_lo_10(data):
    """LO-10: scoring_model is valid enum value."""
    sm = data.get("assessment", {}).get("scoring_model", "")
    if sm in VALID_SCORING_MODELS:
        return True, f"scoring_model valid: {sm}"
    return False, f"scoring_model invalid: {sm} (must be one of {VALID_SCORING_MODELS})"


def check_lo_11(data):
    """LO-11: certification block present with criteria and passing_score."""
    cert = data.get("certification")
    if not cert or not isinstance(cert, dict):
        return False, "certification block missing or not an object"
    if "criteria" not in cert:
        return False, "certification.criteria missing"
    if "passing_score" not in cert:
        return False, "certification.passing_score missing"
    criteria = cert.get("criteria", [])
    if not isinstance(criteria, list) or len(criteria) == 0:
        return False, "certification.criteria must be non-empty array"
    ps = cert.get("passing_score", 0)
    if not isinstance(ps, (int, float)) or ps < 1 or ps > 100:
        return False, f"certification.passing_score invalid: {ps}"
    return True, "certification block present and valid"


def check_lo_12(data):
    """LO-12: certification.criteria descriptions do not contain forbidden keywords."""
    cert = data.get("certification", {})
    criteria = cert.get("criteria", [])
    for i, c in enumerate(criteria):
        desc = c.get("description", "").lower()
        for kw in FORBIDDEN_CERT_KEYWORDS:
            if kw in desc:
                return False, f"certification.criteria[{i}] contains forbidden keyword '{kw}': {c.get('description', '')[:80]}..."
    return True, "No forbidden seal/approve/merge/authorize keywords in certification criteria"


def check_lo_13(data):
    """LO-13: no top-level evidence creation fields."""
    found_fields = []
    for field in EVIDENCE_CREATION_FIELDS:
        if field in data:
            found_fields.append(field)
    if found_fields:
        return False, f"Evidence creation fields found at top level: {found_fields}"
    return True, "No evidence creation fields at top level"


def check_lo_14(data):
    """LO-14: advisory_only is true."""
    ao = data.get("advisory_only")
    if ao is True:
        return True, "advisory_only is True"
    return False, f"advisory_only is {ao}, expected True"


def check_lo_15(data):
    """LO-15: no_seal_authority is true."""
    nsa = data.get("no_seal_authority")
    if nsa is True:
        return True, "no_seal_authority is True"
    return False, f"no_seal_authority is {nsa}, expected True"


RULES = [
    ("LO-1", check_lo_1, "schema is learning-object-v1"),
    ("LO-2", check_lo_2, "id matches pattern"),
    ("LO-3", check_lo_3, "title present and non-empty"),
    ("LO-4", check_lo_4, "source block present with required fields"),
    ("LO-5", check_lo_5, "finding_code matches diagnostic pattern"),
    ("LO-6", check_lo_6, "evidence_refs is non-empty array"),
    ("LO-7", check_lo_7, "learning block present"),
    ("LO-8", check_lo_8, "explanation distinct and educational"),
    ("LO-9", check_lo_9, "assessment block present"),
    ("LO-10", check_lo_10, "scoring_model valid"),
    ("LO-11", check_lo_11, "certification block present"),
    ("LO-12", check_lo_12, "no forbidden keywords in certification criteria"),
    ("LO-13", check_lo_13, "no evidence creation fields"),
    ("LO-14", check_lo_14, "advisory_only is true"),
    ("LO-15", check_lo_15, "no_seal_authority is true"),
]


def validate_fixture(path, allow_invalid=False):
    try:
        data = load_json(path)
    except (json.JSONDecodeError, IOError) as e:
        return (os.path.basename(path), {
            "all_pass": False,
            "checks": [{"rule": "PARSE", "passed": False, "message": str(e)}],
        })

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

    fn = os.path.basename(path)
    is_invalid = fn.startswith("invalid-")
    if allow_invalid and is_invalid:
        expected_pass = not all_pass
    else:
        expected_pass = all_pass

    return (fn, {"all_pass": all_pass, "expected_pass": expected_pass, "checks": results})


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Learning Object v1 Validator")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--include-invalid", action="store_true")
    parser.add_argument("--list-rules", action="store_true")
    args = parser.parse_args()

    if args.list_rules:
        print("Learning Object v1 Validator — Rules")
        print("=" * 60)
        for rid, _, desc in RULES:
            print(f"  {rid}: {desc}")
        return 0

    fixtures = []
    if args.paths:
        fixtures = args.paths
    else:
        pattern = "valid-*.json" if not args.include_invalid else "*.json"
        if FIXTURES_DIR.exists():
            for f in sorted(FIXTURES_DIR.glob(pattern)):
                fixtures.append(str(f))

    if not fixtures:
        if FIXTURES_DIR.exists():
            for f in sorted(FIXTURES_DIR.glob("valid-*.json")):
                fixtures.append(str(f))

    all_passed = True
    vp, vt, ip, it = 0, 0, 0, 0

    for path in fixtures:
        fn = os.path.basename(path)
        is_inv = fn.startswith("invalid-")
        if not os.path.exists(path):
            print(f"  SKIP  {fn} — not found")
            continue
        name, result = validate_fixture(path, args.include_invalid)
        if is_inv:
            it += 1
            if result["expected_pass"]:
                ip += 1
                print(f"  ✅  {name} — correctly rejected")
            else:
                all_passed = False
                print(f"  ❌  {name} — expected rejection but passed")
        else:
            vt += 1
            if result["all_pass"]:
                vp += 1
                print(f"  ✅  {name} — all rules pass")
            else:
                all_passed = False
                print(f"  ❌  {name} — FAILED")
                for c in result["checks"]:
                    if not c["passed"]:
                        print(f"       {c['rule']}: {c['message']}")

    print()
    print(f"Valid fixtures:   {vp}/{vt} passed")
    if args.include_invalid:
        print(f"Invalid fixtures: {ip}/{it} correctly rejected")
    print(f"Overall: {'PASS' if all_passed else 'FAIL'}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
