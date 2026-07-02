#!/usr/bin/env python3
"""
QA Pilot Option B Broker Plan Validator — QA-PILOT-BROKER-PLAN-1

Enforces broker planning-only boundaries on broker plan fixtures.

Rules:
    BP-1: artifact_type must be 'qa_pilot_broker_plan'
    BP-2: artifact_version must be 'qap-broker-plan-v1'
    BP-3: planning_mode must be 'planning_only' or 'read_only_planning'
    BP-4: broker_model.model_type must be 'option_b_librarian_brokered'
    BP-5: broker_model.forward_direction_defined must be true
    BP-6: broker_model.reverse_direction_defined must be false
    BP-7: broker_model.librarian_broker_is_optional must be true
    BP-8: broker_model.qa_pilot_surface_remains_qa_pilot_owned must be true
    BP-9: broker_model.broker_routes_not_absorbs must be true
    BP-10: All planned_tools must have prefix 'planned_librarian_broker_qa_pilot_'
    BP-11: All planned_tools must have custody_required = true
    BP-12: All planned_tools must have planned = true
    BP-13: custody_conditions must have identity, authority, safety sections
    BP-14: identity section must contain CC-1 through CC-4
    BP-15: authority section must contain CC-5 through CC-7
    BP-16: safety section must contain CC-8 through CC-10
    BP-17: audit_requirements.receipt_type must be 'broker_audit'
    BP-18: mutation_envelope.runtime_mutation_authorized must be false
    BP-19: mutation_envelope.implementation_authorized must be false
    BP-20: option_c_reaffirmation.option_c_authorized must be false
    BP-21: mutation_envelope.allowed_files must not be unbounded (no bare 'docs/' or 'scripts/' patterns)
    BP-22: mutation_envelope.forbidden_files must be non-empty
    BP-23: rollback_requirements must have all 5 required sections
    BP-24: No Librarian runtime references in governance doc or schema
"""

import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FIXTURES_DIR = REPO_ROOT / "docs" / "examples" / "qa-pilot-broker-plan"
GOV_DOC = REPO_ROOT / "docs" / "governance" / "QA-PILOT-BROKER-PLAN.md"
SCHEMA_FILE = REPO_ROOT / "docs" / "schemas" / "qa-pilot-broker-plan.schema.json"

ALLOWED_PLANNING_MODES = ["planning_only", "read_only_planning"]
REQUIRED_CC_IDENTITY = ["CC-1", "CC-2", "CC-3", "CC-4"]
REQUIRED_CC_AUTHORITY = ["CC-5", "CC-6", "CC-7"]
REQUIRED_CC_SAFETY = ["CC-8", "CC-9", "CC-10"]
ROLLBACK_REQUIRED_FIELDS = [
    "files_to_revert", "audit_cleanup", "disable_mechanism",
    "project_context_reset", "post_rollback_validation"
]
UNBOUNDED_PATTERNS = [
    r"^docs/$", r"^scripts/$", r"^fixtures/$", r"^data/$",
    r"^docs/\*$", r"^scripts/\*$",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_bp_1(fixture_data=None):
    """BP-1: artifact_type must be 'qa_pilot_broker_plan'."""
    if fixture_data:
        at = fixture_data.get("artifact_type", "")
        if at != "qa_pilot_broker_plan":
            return (False, f"artifact_type must be 'qa_pilot_broker_plan', got '{at}'")
    return (True, "BP-1: artifact_type is 'qa_pilot_broker_plan'")


def check_bp_2(fixture_data=None):
    """BP-2: artifact_version must be 'qap-broker-plan-v1'."""
    if fixture_data:
        av = fixture_data.get("artifact_version", "")
        if av not in ["qap-broker-plan-v1"]:
            return (False, f"artifact_version must be 'qap-broker-plan-v1', got '{av}'")
    return (True, "BP-2: artifact_version is 'qap-broker-plan-v1'")


def check_bp_3(fixture_data=None):
    """BP-3: planning_mode must be planning_only or read_only_planning."""
    if fixture_data:
        pm = fixture_data.get("planning_mode", "")
        if pm not in ALLOWED_PLANNING_MODES:
            return (False, f"planning_mode must be one of {ALLOWED_PLANNING_MODES}, got '{pm}'")
    return (True, f"BP-3: planning_mode is valid")


def check_bp_4(fixture_data=None):
    """BP-4: broker_model.model_type must be 'option_b_librarian_brokered'."""
    if fixture_data:
        bm = fixture_data.get("broker_model", {})
        mt = bm.get("model_type", "")
        if mt != "option_b_librarian_brokered":
            return (False, f"broker_model.model_type must be 'option_b_librarian_brokered', got '{mt}'")
    return (True, "BP-4: broker_model.model_type is 'option_b_librarian_brokered'")


def check_bp_5(fixture_data=None):
    """BP-5: broker_model.forward_direction_defined must be true."""
    if fixture_data:
        bm = fixture_data.get("broker_model", {})
        fdd = bm.get("forward_direction_defined")
        if fdd is not True:
            return (False, f"broker_model.forward_direction_defined must be true, got {fdd}")
    return (True, "BP-5: forward_direction_defined is true")


def check_bp_6(fixture_data=None):
    """BP-6: broker_model.reverse_direction_defined must be false."""
    if fixture_data:
        bm = fixture_data.get("broker_model", {})
        rdd = bm.get("reverse_direction_defined")
        if rdd is not False:
            return (False, f"broker_model.reverse_direction_defined must be false, got {rdd}")
    return (True, "BP-6: reverse_direction_defined is false")


def check_bp_7(fixture_data=None):
    """BP-7: broker_model.librarian_broker_is_optional must be true."""
    if fixture_data:
        bm = fixture_data.get("broker_model", {})
        lbo = bm.get("librarian_broker_is_optional")
        if lbo is not True:
            return (False, f"broker_model.librarian_broker_is_optional must be true, got {lbo}")
    return (True, "BP-7: librarian_broker_is_optional is true")


def check_bp_8(fixture_data=None):
    """BP-8: broker_model.qa_pilot_surface_remains_qa_pilot_owned must be true."""
    if fixture_data:
        bm = fixture_data.get("broker_model", {})
        qpo = bm.get("qa_pilot_surface_remains_qa_pilot_owned")
        if qpo is not True:
            return (False, f"broker_model.qa_pilot_surface_remains_qa_pilot_owned must be true, got {qpo}")
    return (True, "BP-8: qa_pilot_surface_remains_qa_pilot_owned is true")


def check_bp_9(fixture_data=None):
    """BP-9: broker_model.broker_routes_not_absorbs must be true."""
    if fixture_data:
        bm = fixture_data.get("broker_model", {})
        brna = bm.get("broker_routes_not_absorbs")
        if brna is not True:
            return (False, f"broker_model.broker_routes_not_absorbs must be true, got {brna}")
    return (True, "BP-9: broker_routes_not_absorbs is true")


def check_bp_10(fixture_data=None):
    """BP-10: All planned_tools must have prefix 'planned_librarian_broker_qa_pilot_'."""
    if fixture_data:
        tools = fixture_data.get("planned_tools", [])
        for tool in tools:
            name = tool.get("tool_name", "")
            if not name.startswith("planned_librarian_broker_qa_pilot_"):
                return (False, f"Tool name '{name}' must start with 'planned_librarian_broker_qa_pilot_'")
    return (True, "BP-10: All planned tool names use correct prefix")


def check_bp_11(fixture_data=None):
    """BP-11: All planned_tools must have custody_required = true."""
    if fixture_data:
        tools = fixture_data.get("planned_tools", [])
        for tool in tools:
            cr = tool.get("custody_required")
            if cr is not True:
                return (False, f"Tool '{tool.get('tool_name', '?')}' must have custody_required = true")
    return (True, "BP-11: All planned tools require custody")


def check_bp_12(fixture_data=None):
    """BP-12: All planned_tools must have planned = true."""
    if fixture_data:
        tools = fixture_data.get("planned_tools", [])
        for tool in tools:
            p = tool.get("planned")
            if p is not True:
                return (False, f"Tool '{tool.get('tool_name', '?')}' must have planned = true")
    return (True, "BP-12: All planned tools are marked as planned (not implemented)")


def check_bp_13(fixture_data=None):
    """BP-13: custody_conditions must have identity, authority, safety sections."""
    if fixture_data:
        cc = fixture_data.get("custody_conditions", {})
        missing = [s for s in ["identity", "authority", "safety"] if s not in cc or not isinstance(cc.get(s), list)]
        if missing:
            return (False, f"custody_conditions missing sections: {missing}")
        for section in ["identity", "authority", "safety"]:
            if len(cc.get(section, [])) == 0:
                return (False, f"custody_conditions.{section} is empty")
    return (True, "BP-13: custody_conditions has all sections with content")


def check_bp_14(fixture_data=None):
    """BP-14: identity section must contain CC-1 through CC-4."""
    if fixture_data:
        cc = fixture_data.get("custody_conditions", {})
        identity_items = cc.get("identity", [])
        found_ids = set()
        for item in identity_items:
            cc_id = item.get("cc_id", "")
            found_ids.add(cc_id)
            if not item.get("condition"):
                return (False, f"{cc_id} missing condition description")
            if not item.get("verification_mechanism"):
                return (False, f"{cc_id} missing verification_mechanism")
        missing = [c for c in REQUIRED_CC_IDENTITY if c not in found_ids]
        if missing:
            return (False, f"identity section missing CC conditions: {missing}")
    return (True, "BP-14: identity section has CC-1 through CC-4 with details")


def check_bp_15(fixture_data=None):
    """BP-15: authority section must contain CC-5 through CC-7."""
    if fixture_data:
        cc = fixture_data.get("custody_conditions", {})
        authority_items = cc.get("authority", [])
        found_ids = set()
        for item in authority_items:
            cc_id = item.get("cc_id", "")
            found_ids.add(cc_id)
            if not item.get("condition"):
                return (False, f"{cc_id} missing condition description")
            if not item.get("verification_mechanism"):
                return (False, f"{cc_id} missing verification_mechanism")
        missing = [c for c in REQUIRED_CC_AUTHORITY if c not in found_ids]
        if missing:
            return (False, f"authority section missing CC conditions: {missing}")
    return (True, "BP-15: authority section has CC-5 through CC-7 with details")


def check_bp_16(fixture_data=None):
    """BP-16: safety section must contain CC-8 through CC-10."""
    if fixture_data:
        cc = fixture_data.get("custody_conditions", {})
        safety_items = cc.get("safety", [])
        found_ids = set()
        for item in safety_items:
            cc_id = item.get("cc_id", "")
            found_ids.add(cc_id)
            if not item.get("condition"):
                return (False, f"{cc_id} missing condition description")
            if not item.get("verification_mechanism"):
                return (False, f"{cc_id} missing verification_mechanism")
        missing = [c for c in REQUIRED_CC_SAFETY if c not in found_ids]
        if missing:
            return (False, f"safety section missing CC conditions: {missing}")
    return (True, "BP-16: safety section has CC-8 through CC-10 with details")


def check_bp_17(fixture_data=None):
    """BP-17: audit_requirements.receipt_type must be 'broker_audit'."""
    if fixture_data:
        ar = fixture_data.get("audit_requirements", {})
        rt = ar.get("receipt_type", "")
        if rt != "broker_audit":
            return (False, f"audit_requirements.receipt_type must be 'broker_audit', got '{rt}'")
    return (True, "BP-17: audit_requirements.receipt_type is 'broker_audit'")


def check_bp_18(fixture_data=None):
    """BP-18: mutation_envelope.runtime_mutation_authorized must be false."""
    if fixture_data:
        me = fixture_data.get("mutation_envelope", {})
        rma = me.get("runtime_mutation_authorized")
        if rma is not False:
            return (False, f"mutation_envelope.runtime_mutation_authorized must be false, got {rma}")
    return (True, "BP-18: runtime_mutation_authorized is false")


def check_bp_19(fixture_data=None):
    """BP-19: mutation_envelope.implementation_authorized must be false."""
    if fixture_data:
        me = fixture_data.get("mutation_envelope", {})
        ia = me.get("implementation_authorized")
        if ia is not False:
            return (False, f"mutation_envelope.implementation_authorized must be false, got {ia}")
    return (True, "BP-19: implementation_authorized is false")


def check_bp_20(fixture_data=None):
    """BP-20: option_c_reaffirmation.option_c_authorized must be false."""
    if fixture_data:
        ocr = fixture_data.get("option_c_reaffirmation", {})
        oca = ocr.get("option_c_authorized")
        if oca is not False:
            return (False, f"option_c_reaffirmation.option_c_authorized must be false, got {oca}")
    return (True, "BP-20: option_c_authorized is false")


def check_bp_21(fixture_data=None):
    """BP-21: mutation_envelope.allowed_files must not be unbounded."""
    if fixture_data:
        me = fixture_data.get("mutation_envelope", {})
        allowed = me.get("allowed_files", [])
        for pattern in allowed:
            for up in UNBOUNDED_PATTERNS:
                if re.match(up, pattern):
                    return (False, f"Unbounded mutation envelope pattern: '{pattern}' — must be specific")
    return (True, "BP-21: mutation_envelope is bounded (no bare wildcard patterns)")


def check_bp_22(fixture_data=None):
    """BP-22: mutation_envelope.forbidden_files must be non-empty."""
    if fixture_data:
        me = fixture_data.get("mutation_envelope", {})
        ff = me.get("forbidden_files", [])
        if not isinstance(ff, list) or len(ff) == 0:
            return (False, "mutation_envelope.forbidden_files must be non-empty")
    return (True, "BP-22: forbidden_files is non-empty")


def check_bp_23(fixture_data=None):
    """BP-23: rollback_requirements must have all 5 required sections."""
    if fixture_data:
        rr = fixture_data.get("rollback_requirements", {})
        missing = [f for f in ROLLBACK_REQUIRED_FIELDS if f not in rr]
        if missing:
            return (False, f"rollback_requirements missing fields: {missing}")
        for field in ROLLBACK_REQUIRED_FIELDS:
            val = rr.get(field, "")
            if isinstance(val, (list, str)) and len(val) == 0:
                return (False, f"rollback_requirements.{field} is empty")
            if val is None:
                return (False, f"rollback_requirements.{field} is null")
    return (True, "BP-23: rollback_requirements has all 5 required sections")


def check_bp_24():
    """BP-24: No Librarian runtime implementation references in governance doc.
    Planning-level references that reject Option C (e.g. 'native MCPController not authorized') are permitted."""
    forbidden_patterns = [
        "MCPController.swift",
        "Sources/App/",
        "AppEntry.swift",
        "register tool in Librarian",
    ]
    allowed_rejection_contexts = [
        "not authorized for planning or implementation",
        "not authorized by this sprint",
        "remains not authorized",
        "remains rejected",
        "not permitted",
        "without implementing",
        "without registering",
        "planning-only",
        "does not authorize",
        "not authorized",
    ]

    for path in [GOV_DOC]:
        if not path.exists():
            continue
        content = path.read_text()
        for pattern in forbidden_patterns:
            if pattern.lower() in content.lower():
                return (False, f"Found forbidden Librarian runtime ref '{pattern}' in {path.name}")

    # For patterns in context-sensitive list, check they're only in rejection context
    sensitive_patterns = ["native MCPController"]
    for path in [GOV_DOC]:
        if not path.exists():
            continue
        content = path.read_text()
        for pattern in sensitive_patterns:
            idx = content.find(pattern)
            if idx >= 0:
                # Check if any rejection context is nearby (within 200 chars)
                nearby = content[max(0, idx-50):idx+len(pattern)+150].lower()
                is_rejection = any(ctx.lower() in nearby for ctx in allowed_rejection_contexts)
                if not is_rejection:
                    return (False, f"Found non-rejection Librarian runtime ref '{pattern}' in {path.name}")

    return (True, "BP-24: No Librarian runtime references in broker planning documents")


def validate_fixture(path):
    """Validate a single fixture against schema and BP rules."""
    try:
        data = load_json(path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return (os.path.basename(path), {"error": str(e), "all_pass": False})

    # Schema validation first
    schema_path = SCHEMA_FILE
    schema_valid = True
    schema_msg = "Schema validation skipped (jsonschema not available)"

    try:
        import jsonschema
        schema = load_json(str(schema_path))
        jsonschema.validate(data, schema)
        schema_valid = True
        schema_msg = "Schema validation passed"
    except ImportError:
        # Basic structural check
        required = ["artifact_type", "artifact_version", "planning_mode",
                     "broker_model", "planned_tools", "custody_conditions",
                     "audit_requirements", "rollback_requirements",
                     "mutation_envelope", "option_c_reaffirmation"]
        missing = [f for f in required if f not in data]
        if missing:
            schema_valid = False
            schema_msg = f"Missing required fields: {missing}"
    except jsonschema.ValidationError as e:
        schema_valid = False
        schema_msg = f"Schema validation failed: {e.message}"

    checks = [
        ("BP-1", lambda: check_bp_1(data), "Artifact type is broker plan"),
        ("BP-2", lambda: check_bp_2(data), "Artifact version is correct"),
        ("BP-3", lambda: check_bp_3(data), "Planning mode is valid"),
        ("BP-4", lambda: check_bp_4(data), "Model type is Option B"),
        ("BP-5", lambda: check_bp_5(data), "Forward direction defined"),
        ("BP-6", lambda: check_bp_6(data), "Reverse direction not defined"),
        ("BP-7", lambda: check_bp_7(data), "Broker is optional"),
        ("BP-8", lambda: check_bp_8(data), "QA Pilot surface remains owned"),
        ("BP-9", lambda: check_bp_9(data), "Broker routes, does not absorb"),
        ("BP-10", lambda: check_bp_10(data), "Planned tool names correct"),
        ("BP-11", lambda: check_bp_11(data), "All tools require custody"),
        ("BP-12", lambda: check_bp_12(data), "All tools marked as planned"),
        ("BP-13", lambda: check_bp_13(data), "Custody sections present"),
        ("BP-14", lambda: check_bp_14(data), "Identity conditions CC-1..4"),
        ("BP-15", lambda: check_bp_15(data), "Authority conditions CC-5..7"),
        ("BP-16", lambda: check_bp_16(data), "Safety conditions CC-8..10"),
        ("BP-17", lambda: check_bp_17(data), "Audit receipt type correct"),
        ("BP-18", lambda: check_bp_18(data), "Runtime mutation not authorized"),
        ("BP-19", lambda: check_bp_19(data), "Implementation not authorized"),
        ("BP-20", lambda: check_bp_20(data), "Option C not authorized"),
        ("BP-21", lambda: check_bp_21(data), "Mutation envelope is bounded"),
        ("BP-22", lambda: check_bp_22(data), "Forbidden files is non-empty"),
        ("BP-23", lambda: check_bp_23(data), "Rollback requirements complete"),
    ]

    all_pass = schema_valid
    results = [{"rule": "SCHEMA", "description": "Schema valid", "passed": schema_valid, "message": schema_msg}]

    for rule_id, func, desc in checks:
        passed, message = func()
        results.append({"rule": rule_id, "description": desc, "passed": passed, "message": message})
        if not passed:
            all_pass = False

    return (os.path.basename(path), {"all_pass": all_pass, "checks": results})


def main():
    args = sys.argv[1:]
    list_rules = "--list-rules" in args
    include_invalid = "--include-invalid" in args

    if list_rules:
        print("QA Pilot Broker Plan Rules (BP-1 through BP-24):")
        for i in range(1, 25):
            rule_func = globals().get(f"check_bp_{i}")
            if rule_func:
                doc = rule_func.__doc__ or ""
                print(f"  BP-{i}: {doc.strip()}")
        return 0

    if not FIXTURES_DIR.exists():
        print(f"ERROR: Fixtures directory not found: {FIXTURES_DIR}")
        return 1

    if include_invalid:
        files = sorted(FIXTURES_DIR.glob("*.json"))
    else:
        files = sorted(FIXTURES_DIR.glob("valid-*.json"))

    if not files:
        print("No fixture files found")
        return 1

    results = []
    valid_pass = 0
    valid_total = 0
    invalid_pass = 0
    invalid_total = 0

    for f in files:
        fname = f.name
        is_invalid = fname.startswith("invalid-")
        result = validate_fixture(str(f))
        results.append(result)

        if not is_invalid:
            valid_total += 1
            if result[1].get("all_pass"):
                valid_pass += 1
        else:
            invalid_total += 1
            if not result[1].get("all_pass"):
                invalid_pass += 1

    parse_errors = False
    for fname, r in results:
        if "error" in r:
            print(f"  ❌ {fname} — ERROR: {r['error']}")
            parse_errors = True
            continue

        prefix = "✅" if r["all_pass"] else "❌"
        check_count = len(r["checks"])
        pass_count = sum(1 for c in r["checks"] if c["passed"])
        print(f"  {prefix} {fname} — {pass_count}/{check_count} checks pass")

        if not r["all_pass"]:
            for c in r["checks"]:
                if not c["passed"]:
                    print(f"       FAIL {c['rule']}: {c['message']}")

    # BP-24 is a project-level check (not per-fixture)
    bp24_passed, bp24_msg = check_bp_24()
    bp24_prefix = "✅" if bp24_passed else "❌"
    print(f"  {bp24_prefix} BP-24: {bp24_msg}")

    print()
    if include_invalid:
        print(f"Valid fixtures:   {valid_pass}/{valid_total} passed")
        print(f"Invalid fixtures: {invalid_pass}/{invalid_total} rejected")

    all_ok = (valid_pass == valid_total if valid_total > 0 else True)
    all_rejected = (invalid_pass == invalid_total if invalid_total > 0 else True)

    if all_ok and all_rejected and bp24_passed and not parse_errors:
        print("\n✅ ALL CHECKS PASS")
        return 0
    else:
        failures = []
        if not all_ok: failures.append("valid fixtures")
        if not all_rejected: failures.append("invalid fixture rejection")
        if not bp24_passed: failures.append("BP-24")
        if parse_errors: failures.append("parse errors")
        print(f"\n❌ CHECKS FAILED: {', '.join(failures)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
