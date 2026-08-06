#!/usr/bin/env python3
"""
QA Pilot Scenario Adapter — QA-PILOT-SCENARIO-ADAPTER-1

Bridges governed Learning Objects to the V1.5 scoring engine (scoring.js).
Converts between:
  Learning Object (exercise scenario, certification criteria)
      ↓
  V1.5 Scenario Format (expected bugs, AC refs, pass mode)
      ↓
  scoring.js input/output
      ↓
  Governed validation result

The scoring logic is a Python reimplementation of src/scoring.js (pure function).
No DOM, no browser, no persistence. Deterministic evaluation.

Usage:
    python3 scripts/qa_pilot_scenario_adapter.py evaluate <scenario-id> <bugs-found> <bugs-logged>
    python3 scripts/qa_pilot_scenario_adapter.py list-scenarios
    python3 scripts/qa_pilot_scenario_adapter.py load <scenario-id>

Authority: advisory-only. Evaluates understanding, not system correctness.
"""

import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

ADAPTER_VERSION = "qa-pilot-scenario-adapter-v1"

# Path to V1.5 scenario files (preserved as reference definitions)
V15_ROOT = Path("/Users/andrew/Desktop/OpenWork/QA Pilot")
V15_SCENARIOS = V15_ROOT / "scenarios"
V15_BUG_KEYS = V15_ROOT / "data" / "bug-keys.js"
V15_SCORING = V15_ROOT / "src" / "scoring.js"

# Learning objects generated directory
LO_DIR = REPO_ROOT / "data" / "learning-objects"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def now_utc():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Known Scenario Definitions (from V1.5) ──────────────────────────────
# Preserved as governed scenario definitions adapted from V1.5's scenario files.
# See active/qa-pilot/docs/governance/SCENARIO-ADAPTATION-NOTES.md for provenance.

SCENARIO_DEFINITIONS = {
    "capstone-001": {
        "title": "Payment Processing — Live Investigation",
        "expected_bugs": [
            "status-junior-closed",
            "priority-mismatch",
            "future-date-allowed",
            "owner-unassigned",
        ],
        "ac_refs": {
            "status-junior-closed": "AC-2.1",
            "priority-mismatch": "AC-3.1",
            "future-date-allowed": "AC-3.2",
            "owner-unassigned": "AC-1.4",
        },
        "passing_score": 80,
        "max_score_per_bug": 3,
    },
    "case-002": {
        "title": "Escalation Handling — Case Investigation",
        "expected_bugs": [
            "escalation-reason-blank",
            "status-junior-close",
        ],
        "ac_refs": {
            "escalation-reason-blank": "AC-4.1",
            "status-junior-close": "AC-2.1",
        },
        "passing_score": 70,
        "max_score_per_bug": 3,
    },
    "scenario-case-003": {
        "title": "Role-Based Access — Junior Investigator",
        "expected_bugs": [
            "status-junior-closed",
            "priority-mismatch",
            "future-date-allowed",
            "owner-unassigned",
        ],
        "ac_refs": {
            "status-junior-closed": "AC-2.1",
            "priority-mismatch": "AC-3.1",
            "future-date-allowed": "AC-3.2",
            "owner-unassigned": "AC-1.4",
        },
        "passing_score": 75,
        "max_score_per_bug": 3,
    },
    "scenarios-bug-001": {
        "title": "Bug Hunting — CRM Field Validation",
        "expected_bugs": [
            "outcome-resolution-visible-junior",
            "outcome-resolution-editable-junior",
            "case-title-blank-allowed",
            "resolved-without-outcome",
            "last-updated-stale",
        ],
        "ac_refs": {
            "outcome-resolution-visible-junior": "AC-5.1",
            "outcome-resolution-editable-junior": "AC-5.2",
            "case-title-blank-allowed": "AC-5.3",
            "resolved-without-outcome": "AC-6.1",
            "last-updated-stale": "AC-7.1",
        },
        "passing_score": 60,
        "max_score_per_bug": 3,
    },
    "capstone-002": {
        "title": "Sprint G — End-to-End QA Assessment",
        "expected_bugs": [
            "BUG-C2-01",
            "BUG-C2-02",
            "BUG-C2-03",
        ],
        "ac_refs": {
            "BUG-C2-01": "AC-C2-1",
            "BUG-C2-02": "AC-C2-2",
            "BUG-C2-03": "AC-C2-3",
        },
        "passing_score": 70,
        "max_score_per_bug": 3,
    },
}

# ── Scoring Engine (Python port of V1.5 scoring.js) ────────────────────

def evaluate_submission(scenario_id, bugs_found, bugs_logged):
    """Evaluate a scenario submission.
    
    Pure function. No side effects. No persistence.
    Port of V1.5's window.evaluateSubmission().
    
    Args:
        scenario_id: Scenario identifier (e.g. 'capstone-001')
        bugs_found: List of bug IDs the student triggered/found
        bugs_logged: List of bug report dicts with title, severity, acRef, hasSteps
    
    Returns:
        dict with score, max_score, percentage, passed, missed_bugs, bad_reports, summary
    """
    scenario = SCENARIO_DEFINITIONS.get(scenario_id)
    if not scenario:
        return {
            "score": 0, "max_score": 0, "percentage": 0, "passed": False,
            "missed_bugs": [], "bad_reports": [], "summary": "Scenario not found.",
        }
    
    expected = scenario.get("expected_bugs", [])
    ac_refs = scenario.get("ac_refs", {})
    max_score_per = scenario.get("max_score_per_bug", 3)
    max_score = len(expected) * max_score_per
    passing_score = scenario.get("passing_score", 80)
    
    score = 0
    missed_bugs = []
    bad_reports = []
    
    # 1 point for each expected bug found in dynamics
    for bug_id in expected:
        if bug_id in bugs_found:
            score += 1
        else:
            missed_bugs.append(bug_id)
    
    # 1 point for complete ADO report + 1 for correct AC ref
    for report in bugs_logged:
        title = report.get("title", "").strip()
        severity = report.get("severity", "").strip()
        ac_ref = report.get("acRef", "").strip()
        has_steps = report.get("hasSteps", False)
        
        is_complete = bool(title and severity and ac_ref and has_steps)
        
        if is_complete:
            score += 1
            # Check if AC ref matches expected
            ref_matches = False
            for bug_id in expected:
                expected_ref = ac_refs.get(bug_id, "")
                if expected_ref.lower() == ac_ref.lower():
                    ref_matches = True
                    break
            if ref_matches:
                score += 1
        else:
            bad_reports.append(title or "(untitled)")
    
    percentage = round((score / max_score) * 100) if max_score > 0 else 0
    passed = percentage >= passing_score
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": percentage,
        "passed": passed,
        "missed_bugs": missed_bugs,
        "bad_reports": bad_reports,
        "summary": _build_summary(score, max_score, percentage, missed_bugs, bad_reports),
    }


def _build_summary(score, max_score, percentage, missed_bugs, bad_reports):
    """Build a human-readable summary string (port of scoring.js buildSummary)."""
    lines = [f"Score: {score} / {max_score} ({percentage}%)"]
    
    if not missed_bugs:
        lines.append("✓ All defects found in the CRM.")
    else:
        lines.append(f"✗ Defects not found: {', '.join(missed_bugs)}")
    
    if not bad_reports and score > 0:
        lines.append("✓ All ADO reports were complete.")
    elif bad_reports:
        lines.append(f"✗ Incomplete ADO reports: {', '.join(bad_reports)}")
    
    return "\n".join(lines)


# ── Learning Object Bridge ───────────────────────────────────────────────

def load_learning_object(lo_id):
    """Load a generated learning object from disk."""
    lo_path = LO_DIR / f"{lo_id}.json"
    if lo_path.exists():
        return load_json(lo_path)
    return None


def learning_object_to_scenario(learning_object):
    """Convert a learning object's exercise section to a scenario definition.
    
    This is the bridge: a learning object's exercise describes what the
    learner should observe, and we map that to an evaluatable scenario.
    """
    exercise = learning_object.get("exercise", {})
    source = learning_object.get("source", {})
    cert = learning_object.get("certification", {})
    
    scenario_id = exercise.get("scenario_id", "lo-derived-scenario")
    expected_obs = exercise.get("expected_observations", [])
    
    # Convert expected observations to evaluation criteria
    expected_bugs = []
    ac_refs = {}
    for i, obs in enumerate(expected_obs):
        bug_id = f"OBS-{i+1:03d}"
        expected_bugs.append(bug_id)
        ac_refs[bug_id] = obs.get("evidence_link", f"EXPECTED-{i+1:03d}")
    
    passing_score = cert.get("passing_score", 80)
    
    return {
        "title": learning_object.get("title", "Derived Scenario"),
        "expected_bugs": expected_bugs,
        "ac_refs": ac_refs,
        "passing_score": passing_score,
        "max_score_per_bug": 3,
        "source_learning_object": learning_object.get("id", ""),
        "source_finding": source.get("finding_code", ""),
        "advisory_only": True,
        "no_seal_authority": True,
    }


# ── Commands ─────────────────────────────────────────────────────────────

def cmd_list_scenarios(args):
    """List all available scenario definitions."""
    print("QA Pilot Scenario Adapter — Known Scenarios")
    print("=" * 60)
    for sid, sdef in sorted(SCENARIO_DEFINITIONS.items()):
        print(f"  {sid}: {sdef['title']}")
        print(f"       Bugs: {len(sdef['expected_bugs'])} expected, pass={sdef['passing_score']}%")
    print()
    print(f"Total: {len(SCENARIO_DEFINITIONS)} scenario definitions")
    return 0


def cmd_load(args):
    """Load and display a scenario definition."""
    if not args:
        print("Usage: scenario_adapter.py load <scenario-id>", file=sys.stderr)
        return 1
    
    sid = args[0]
    sdef = SCENARIO_DEFINITIONS.get(sid)
    if not sdef:
        print(f"Scenario not found: {sid}", file=sys.stderr)
        return 1
    
    output = {
        "adapter_version": ADAPTER_VERSION,
        "scenario_id": sid,
        "definition": sdef,
        "provenance": {
            "source": "V1.5 scenario files (active/librarian/qa-pilot reference)",
            "adapted_by": ADAPTER_VERSION,
            "advisory": True,
            "no_authority_conferred": True,
        },
    }
    print(json.dumps(output, indent=2))
    return 0


def cmd_evaluate(args):
    """Evaluate a scenario submission.
    
    Usage: scenario_adapter.py evaluate <scenario-id> <bugs-found-json> <bugs-logged-json>
    
    <bugs-found-json>: JSON array of bug ID strings
    <bugs-logged-json>: JSON array of bug report objects with title, severity, acRef, hasSteps
    """
    if len(args) < 3:
        print("Usage: scenario_adapter.py evaluate <scenario-id> <bugs-found-json> <bugs-logged-json>",
              file=sys.stderr)
        return 1
    
    sid = args[0]
    
    try:
        bugs_found = json.loads(args[1])
    except json.JSONDecodeError:
        print("ERROR: bugs-found must be a JSON array", file=sys.stderr)
        return 1
    
    try:
        bugs_logged = json.loads(args[2])
    except json.JSONDecodeError:
        print("ERROR: bugs-logged must be a JSON array", file=sys.stderr)
        return 1
    
    result = evaluate_submission(sid, bugs_found, bugs_logged)
    
    output = {
        "adapter_version": ADAPTER_VERSION,
        "scenario_id": sid,
        "result": result,
        "provenance": {
            "advisory": True,
            "no_authority_conferred": True,
            "evaluates_understanding": True,
            "not_system_correctness": True,
        },
    }
    
    print(json.dumps(output, indent=2))
    return 0 if result["passed"] else 2


def cmd_evaluate_from_lo(args):
    """Evaluate using a learning object's exercise definition.
    
    Usage: scenario_adapter.py evaluate-from-lo <lo-id> <bugs-found-json> <bugs-logged-json>
    """
    if len(args) < 3:
        print("Usage: scenario_adapter.py evaluate-from-lo <lo-id> <bugs-found-json> <bugs-logged-json>",
              file=sys.stderr)
        return 1
    
    lo_id = args[0]
    lo = load_learning_object(lo_id)
    if not lo:
        print(f"Learning object not found: {lo_id}", file=sys.stderr)
        return 1
    
    sdef = learning_object_to_scenario(lo)
    scenario_id = sdef.get("title", "lo-derived").lower().replace(" ", "-")
    
    try:
        bugs_found = json.loads(args[1])
    except json.JSONDecodeError:
        print("ERROR: bugs-found must be a JSON array", file=sys.stderr)
        return 1
    
    try:
        bugs_logged = json.loads(args[2])
    except json.JSONDecodeError:
        print("ERROR: bugs-logged must be a JSON array", file=sys.stderr)
        return 1
    
    # Use the same scoring engine with the learning-object-derived definition
    # Override to use our derived scenario as a temp definition
    original = SCENARIO_DEFINITIONS.get(scenario_id)
    SCENARIO_DEFINITIONS[scenario_id] = sdef
    
    try:
        result = evaluate_submission(scenario_id, bugs_found, bugs_logged)
    finally:
        if original is None:
            SCENARIO_DEFINITIONS.pop(scenario_id, None)
        else:
            SCENARIO_DEFINITIONS[scenario_id] = original
    
    output = {
        "adapter_version": ADAPTER_VERSION,
        "source_learning_object": lo_id,
        "source_finding": lo.get("source", {}).get("finding_code", ""),
        "scenario_id": sdef.get("title", "derived"),
        "result": result,
        "provenance": {
            "advisory": True,
            "no_authority_conferred": True,
            "evaluates_understanding": True,
            "not_system_correctness": True,
            "certification_criteria": lo.get("certification", {}).get("criteria", []),
        },
    }
    
    print(json.dumps(output, indent=2))
    return 0 if result["passed"] else 2


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("QA Pilot Scenario Adapter — QA-PILOT-SCENARIO-ADAPTER-1")
        print()
        print("Usage:")
        print("  list-scenarios                        — List available scenarios")
        print("  load <scenario-id>                    — Load scenario definition")
        print("  evaluate <id> <bugs> <logs>           — Evaluate submission")
        print("  evaluate-from-lo <lo-id> <bugs> <logs> — Evaluate from learning object")
        print()
        print("Authority: advisory-only. Evaluates understanding, not system correctness.")
        return 0

    command = sys.argv[1]
    cmd_args = sys.argv[2:]

    commands = {
        "list-scenarios": cmd_list_scenarios,
        "load": cmd_load,
        "evaluate": cmd_evaluate,
        "evaluate-from-lo": cmd_evaluate_from_lo,
    }

    if command not in commands:
        print(f"Unknown command: {command}", file=sys.stderr)
        return 1

    return commands[command](cmd_args)


if __name__ == "__main__":
    sys.exit(main())
