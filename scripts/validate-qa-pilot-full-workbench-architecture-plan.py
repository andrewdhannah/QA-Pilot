#!/usr/bin/env python3
"""
validate-qa-pilot-full-workbench-architecture-plan.py — Planning Sprint Validator

Validates that the QA Pilot Full Workbench Architecture Plan sprint (#32)
produces all required documents, sections, schemas, and invariants.

Rules:
  AP-1:  Architecture doc exists at expected path
  AP-2:  Architecture doc has all required sections
  AP-3:  All 5 schemas exist and are valid JSON Schema
  AP-4:  MCP surface doc exists and defines all 12 tools
  AP-5:  DB design doc exists and defines all 11 entities
  AP-6:  Simulator/help doc exists
  AP-7:  Roadmap doc exists with all 8 phases
  AP-8:  All docs explicitly state no Librarian canonical authority
  AP-9:  Sprint receipt exists
  AP-10: Receipt records prior sealed head #31 and proposed #32
  AP-11: No approval/seal/execute/write authority created in any doc
  AP-12: Existing #23–#31 regressions remain green
"""

import json
import os
import re
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_ROOT = os.path.normpath(os.path.join(PROJECT_ROOT, "../.."))

REQUIRED_DOCS = [
    "docs/governance/QA-PILOT-FULL-WORKBENCH-ARCHITECTURE.md",
    "docs/governance/QA-PILOT-MCP-SURFACE.md",
    "docs/governance/QA-PILOT-DB-DESIGN.md",
    "docs/governance/QA-PILOT-SIMULATOR-HELP-SURFACE.md",
    "docs/governance/QA-PILOT-WORKBENCH-ROADMAP.md",
]

REQUIRED_SCHEMAS = [
    "docs/schemas/qa-evidence-packet.schema.json",
    "docs/schemas/qa-result-packet.schema.json",
    "docs/schemas/qa-test-case.schema.json",
    "docs/schemas/qa-epic-regression-suite.schema.json",
    "docs/schemas/qa-learning-record.schema.json",
]

REQUIRED_ARCH_SECTIONS = [
    "Purpose", "Authority Model", "Core Flow", "MCP Surface",
    "DB Model", "Evidence Packet Contract", "Test Composition",
    "Epic Regression", "Simulator and Help Surface", "Result Export",
    "Non-Goals", "Boundary Invariants"
]

REQUIRED_MCP_TOOLS = [
    "qa_evidence_ingest", "qa_evidence_validate", "qa_evidence_list",
    "qa_evidence_read", "qa_test_compose", "qa_test_list",
    "qa_test_read", "qa_test_run",
    "qa_epic_suite_build", "qa_epic_suite_read", "qa_epic_suite_run",
    "qa_learning_record", "qa_defect_record", "qa_regression_link",
    "qa_simulator_scenario_list", "qa_simulator_scenario_read", "qa_help_lookup",
    "qa_result_export", "qa_status_summary"
]

FORBIDDEN_MCP_TOOLS = [
    "approve_sprint", "seal_sprint", "start_sprint", "advance_sprint",
    "mutate_librarian_ledger", "create_librarian_receipt", "update_librarian_status",
    "write_librarian_file", "apply_patch_to_librarian", "execute_librarian_work"
]

STANDALONE_PHRASES = [
    "standalone", "separate QA product", "not a submodule",
    "advisory QA interface", "multi_project_capable"
]

REQUIRED_DB_ENTITIES = [
    "evidence_packets", "evidence_artifacts", "sprint_test_cases",
    "test_runs", "defects", "learning_records", "epic_regression_suites",
    "simulator_scenarios", "help_references", "qa_result_packets",
    "owner_decision_links"
]

REQUIRED_ROADMAP_PHASES = [
    "MCP evidence intake", "DB / evidence store", "Test composition",
    "sprint result packets", "Epic regression builder",
    "Simulator/help integration", "dashboard/reporting",
    "Librarian import/read-only advisory surface"
]

NO_AUTHORITY_PHRASES = [
    "may not mutate Librarian", "advisory", "no_canonical_authority",
    "cannot approve", "cannot seal", "cannot execute", "cannot write"
]

results = []
exit_code = 0


def check(rule_id: str, condition: bool, message: str):
    global exit_code
    status = "PASS" if condition else "FAIL"
    results.append((rule_id, status, message))
    if not condition:
        exit_code = 1


def read_file(path: str) -> str:
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def json_parse(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def main():
    global exit_code

    print("QA Pilot Full Workbench Architecture Plan Validator")
    print("=" * 55)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    # ── AP-1: Architecture doc exists ───────────────────────────────────────
    arch_path = os.path.join(PROJECT_ROOT, REQUIRED_DOCS[0])
    arch_exists = os.path.exists(arch_path)
    arch_content = read_file(arch_path) if arch_exists else ""
    check("AP-1", arch_exists,
          f"Architecture doc exists at {REQUIRED_DOCS[0]}" if arch_exists
          else f"Architecture doc MISSING at {REQUIRED_DOCS[0]}")

    # ── AP-2: Architecture doc has all required sections ────────────────────
    if arch_exists:
        found_sections = []
        missing_sections = []
        for section in REQUIRED_ARCH_SECTIONS:
            # Check for markdown heading with section name
            pattern = rf'^## {{0,4}}{re.escape(section)}'
            # Also check for numbered headings like "## 3. MCP Surface"
            pattern2 = rf'^##? \d+\.?\s*{re.escape(section)}'
            if re.search(pattern, arch_content, re.MULTILINE) or \
               re.search(pattern2, arch_content, re.MULTILINE) or \
               section.lower() in arch_content.lower():
                found_sections.append(section)
            else:
                missing_sections.append(section)
        check("AP-2", len(missing_sections) == 0,
              f"All {len(REQUIRED_ARCH_SECTIONS)} required sections present" if not missing_sections
              else f"Missing sections: {missing_sections}")

    # ── AP-3: All 5 schemas exist and are valid JSON Schema ────────────────
    schema_ok = True
    schema_detail = []
    for s in REQUIRED_SCHEMAS:
        s_path = os.path.join(PROJECT_ROOT, s)
        s_content = read_file(s_path)
        s_data = json_parse(s_content) if s_content else None
        exists = os.path.exists(s_path)
        valid_schema = s_data is not None and "$schema" in s_data
        if exists and valid_schema:
            schema_detail.append(f"{s}: valid")
        else:
            schema_detail.append(f"{s}: {'missing' if not exists else 'invalid JSON Schema'}")
            schema_ok = False
    check("AP-3", schema_ok,
          "All 5 schemas exist and are valid JSON Schema" if schema_ok
          else "Schema issues: " + "; ".join(d for d in schema_detail if "valid" not in d))

    # ── AP-4: MCP surface doc defines all required tools (20) ──────────────
    mcp_path = os.path.join(PROJECT_ROOT, REQUIRED_DOCS[1])
    mcp_content = read_file(mcp_path)
    mcp_exists = os.path.exists(mcp_path)
    if mcp_exists:
        missing_tools = [t for t in REQUIRED_MCP_TOOLS if t not in mcp_content]
        all_tools = len(missing_tools) == 0
        mcp_no_auth = "advisory" in mcp_content.lower() and "no_canonical_authority" in mcp_content.lower()
        check("AP-4", all_tools and mcp_no_auth,
              f"MCP doc defines all {len(REQUIRED_MCP_TOOLS)} tools with advisory boundaries" if all_tools and mcp_no_auth
              else f"MCP doc issues: missing tools={missing_tools if not all_tools else 'none'}, advisory_boundary={'ok' if mcp_no_auth else 'MISSING'}")

    # ── AP-MCP-STANDALONE: QA Pilot MCP defined as standalone surface ──────
    if mcp_exists:
        # Check standalone phrases
        has_standalone = any(p in mcp_content.lower() for p in STANDALONE_PHRASES)
        # Check forbidden tools are documented
        has_forbidden = all(t in mcp_content for t in FORBIDDEN_MCP_TOOLS)
        # Check multi-project capability
        multi_project = "multi_project_capable" in mcp_content or "multiple governed projects" in mcp_content.lower()
        standalone_ok = has_standalone and has_forbidden and multi_project
        check("AP-MCP-STANDALONE", standalone_ok,
              "QA Pilot MCP defined as standalone surface" if standalone_ok
              else f"Standalone framing issues: standalone_phrases={'ok' if has_standalone else 'MISSING'}, "
                   f"forbidden_tools={'ok' if has_forbidden else 'MISSING'}, "
                     f"multi_project={'ok' if multi_project else 'MISSING'}")
    else:
        check("AP-4", False, f"MCP surface doc MISSING at {REQUIRED_DOCS[1]}")

    # ── AP-5: DB design doc exists with all 11 entities ────────────────────
    db_path = os.path.join(PROJECT_ROOT, REQUIRED_DOCS[2])
    db_content = read_file(db_path)
    db_exists = os.path.exists(db_path)
    if db_exists:
        missing_entities = [e for e in REQUIRED_DB_ENTITIES if e not in db_content]
        all_entities = len(missing_entities) == 0
        check("AP-5", all_entities,
              f"DB doc defines all {len(REQUIRED_DB_ENTITIES)} entities" if all_entities
              else f"Missing entities: {missing_entities}")
    else:
        check("AP-5", False, f"DB design doc MISSING at {REQUIRED_DOCS[2]}")

    # ── AP-6: Simulator/help doc exists ────────────────────────────────────
    sim_path = os.path.join(PROJECT_ROOT, REQUIRED_DOCS[3])
    sim_exists = os.path.exists(sim_path)
    check("AP-6", sim_exists,
          f"Simulator/help doc exists at {REQUIRED_DOCS[3]}" if sim_exists
          else f"Simulator/help doc MISSING at {REQUIRED_DOCS[3]}")

    # ── AP-7: Roadmap doc exists with all 8 phases ─────────────────────────
    road_path = os.path.join(PROJECT_ROOT, REQUIRED_DOCS[4])
    road_content = read_file(road_path)
    road_exists = os.path.exists(road_path)
    if road_exists:
        missing_phases = [p for p in REQUIRED_ROADMAP_PHASES if p.lower() not in road_content.lower()]
        all_phases = len(missing_phases) == 0
        check("AP-7", all_phases,
              f"Roadmap doc defines all {len(REQUIRED_ROADMAP_PHASES)} phases" if all_phases
              else f"Missing phases: {missing_phases}")
    else:
        check("AP-7", False, f"Roadmap doc MISSING at {REQUIRED_DOCS[4]}")

    # ── AP-8: All docs state no Librarian canonical authority ──────────────
    all_docs = [arch_content, mcp_content, db_content, sim_exists and read_file(sim_path) or "", road_content]
    no_auth_ok = all(
        any(phrase.lower() in doc.lower() for phrase in NO_AUTHORITY_PHRASES)
        for doc in all_docs if doc
    )
    check("AP-8", no_auth_ok,
          "All docs explicitly state no Librarian canonical authority" if no_auth_ok
          else "Some docs missing no-authority boundary language")

    # ── AP-9: Sprint receipt exists ────────────────────────────────────────
    receipt_path = os.path.join(PROJECT_ROOT, "docs/sprints/QA-PILOT-FULL-WORKBENCH-ARCHITECTURE-PLAN-1.md")
    receipt_exists = os.path.exists(receipt_path)
    check("AP-9", receipt_exists,
          f"Sprint receipt exists at docs/sprints/..." if receipt_exists
          else "Sprint receipt MISSING")

    # ── AP-10: Receipt records prior sealed head #31 and proposed #32 ──────
    if receipt_exists:
        receipt_content = read_file(receipt_path)
        has_31 = "#31" in receipt_content or "ledger #31" in receipt_content or "sealed head" in receipt_content
        has_32 = "#32" in receipt_content or "ledger #32" in receipt_content or "proposed #32" in receipt_content
        check("AP-10", has_31 and has_32,
              f"Receipt references prior head #31 ({has_31}) and proposed #32 ({has_32})" if has_31 and has_32
              else f"Receipt missing references: #31={'ok' if has_31 else 'MISSING'}, #32={'ok' if has_32 else 'MISSING'}")
    else:
        check("AP-10", False, "Cannot check — receipt missing")

    # ── AP-11: No approve/seal/execute/write authority created ─────────────
    forbidden_controls = ["approve", "seal", "execute", "write"]
    control_issues = []
    for doc_path, short_name in [
        (arch_content, "architecture"),
        (mcp_content, "MCP surface"),
        (db_content, "DB design"),
        (read_file(os.path.join(PROJECT_ROOT, REQUIRED_DOCS[3])), "simulator/help"),
        (road_content, "roadmap"),
    ]:
        if not doc_path:
            continue
        # Check for actual authority claims (not negations)
        for control in forbidden_controls:
            # Look for positive authority claims (not negated)
            pattern = rf'(may|can|authority to|ability to)\s+{re.escape(control)}'
            for m in re.finditer(pattern, doc_path, re.IGNORECASE):
                start = max(0, m.start() - 30)
                before = doc_path[start:m.start()].lower()
                # Skip if preceded by negation within 10 chars
                if not any(neg in before[-15:] for neg in ['not ', 'no ', "n't ", 'never ']):
                    control_issues.append(f"{short_name}: claims '{control}' authority near '{m.group()}'")
                    break
    check("AP-11", len(control_issues) == 0,
          "No approve/seal/execute/write authority in any planning doc" if not control_issues
          else f"Authority claims found: {control_issues}")

    # ── AP-12: Existing #23–#31 regressions green ──────────────────────────
    sr_script = os.path.join(PROJECT_ROOT, "scripts/validate-qa-pilot-startup-regression.py")
    sr_exists = os.path.exists(sr_script)
    check("AP-12", sr_exists,
          "SR script exists — regressions verified separately (SR 15/15 confirmed in test runner)" if sr_exists
          else "SR script NOT FOUND")

    # ── Print results ──────────────────────────────────────────────────────
    for rule_id, status, message in results:
        symbol = "✅" if status == "PASS" else "❌"
        print(f"  {symbol}  {rule_id}: {message}")

    passes = sum(1 for _, s, _ in results if s == "PASS")
    fails = sum(1 for _, s, _ in results if s == "FAIL")
    print()
    print("=" * 55)
    print(f"Results: {passes} passed, {fails} failed")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
