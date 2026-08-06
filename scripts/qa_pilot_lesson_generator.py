#!/usr/bin/env python3
"""
QA Pilot Evidence-to-Lesson Generator — QA-PILOT-EVIDENCE-TO-LESSON-GENERATOR-1

Translates diagnostic findings from the Evidence Plane into governed Learning Objects
(learning-object-v1 schema). Proves the translation pipeline: Diagnostic Finding →
Learning Object → Lesson / Exercise / Assessment package.

This is a deterministic template-based generator. It does NOT use an LLM.
Educational content is constructed from finding metadata using governed templates.
All output validates against learning-object-v1.schema.json.

Usage:
    python3 scripts/qa_pilot_lesson_generator.py list-findings
    python3 scripts/qa_pilot_lesson_generator.py generate <finding-code>...
    python3 scripts/qa_pilot_lesson_generator.py generate-all
    python3 scripts/qa_pilot_lesson_generator.py generate-epic
    python3 scripts/qa_pilot_lesson_generator.py output <lo-id>

Authority: advisory-only. Learning objects reference evidence; they do not create evidence.
"""

import datetime
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
VALIDATOR_SCRIPT = SCRIPT_DIR / "validate-learning-object.py"

GENERATOR_VERSION = "evidence-to-lesson-generator-v1"

try:
    from qa_pilot_evidence_sdk import EvidenceProvider, SDK_VERSION
    SDK_AVAILABLE = True
except ImportError:
    EvidenceProvider = None
    SDK_VERSION = "unavailable"
    SDK_AVAILABLE = False


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_sdk():
    """Load evidence plane data via SDK."""
    if not SDK_AVAILABLE:
        return None, "SDK not available"
    try:
        provider = EvidenceProvider()
        findings_result = provider.getFindings()
        findings_data = findings_result.get("data", {})
        findings = findings_data.get("findings", [])
        
        snapshot_result = provider.getEvidenceSnapshot()
        snapshot_data = snapshot_result.get("data", {})
        
        provenance_result = provider.getProvenanceChain()
        provenance_data = provenance_result.get("data", {})
        
        return {
            "findings": findings,
            "snapshot": snapshot_data,
            "provenance": provenance_data,
            "run_id": findings_data.get("run_id") or snapshot_data.get("run_id"),
        }, None
    except Exception as e:
        return None, str(e)


# ── Educational Explanation Templates ────────────────────────────────────
# Each finding category gets a distinct teaching explanation.
# Templates are deterministic — same input always produces same output.

EXPLANATION_TEMPLATES = {
    "CURSOR": {
        "description": (
            "A lifecycle cursor is a project's governance bookmark. It records the current "
            "phase, cycle, and state within the Librarian governed development model. "
            "Think of it like the odometer reading on a car — it tells you where the project "
            "is in its journey, but not whether everything under the hood is working correctly."
        ),
        "stale": (
            "When a cursor is stale, it means the project has not reported its state within "
            "the expected freshness threshold. This is similar to a smoke alarm that was "
            "last tested 90 days ago — the alarm might still work, but you cannot be certain "
            "without a current test. Staleness does not mean the project is broken; it means "
            "the governance state is uncertain."
        ),
        "absent": (
            "When a cursor is absent, the project exists in the registry but has no lifecycle "
            "tracking at all. This is like a car that is registered with the DMV but has no "
            "license plate — it exists in the system but cannot legally operate. The project "
            "cannot participate in governed workflows until a lifecycle cursor is established."
        ),
    },
    "RECONCILIATION": {
        "description": (
            "Reconciliation is the process of comparing two sources of truth to ensure they "
            "agree. In the Librarian model, reconciliation checks that on-disk state matches "
            "the MCP store, that the project registry is consistent, and that evidence sources "
            "are producing expected output. Think of it like balancing a checkbook — both sides "
            "must match for the record to be trusted."
        ),
        "stale": (
            "A stale reconciliation report means the comparison has not been run recently. "
            "The two sides might still agree, but you cannot prove it without a current report."
        ),
        "absent": (
            "An absent reconciliation report means no comparison has ever been performed. "
            "The system has no evidence that on-disk and store state agree. This is a "
            "governance gap that must be resolved before lifecycle decisions can be trusted."
        ),
    },
    "EPIC": {
        "description": (
            "An epic registry tracks which epics have been registered, their status, and their "
            "lifecycle position. You can think of it like a library catalog — it tells you what "
            "capabilities exist, where they are in development, and what state they are in. "
            "Epics are the largest unit of governed work; they span multiple sprints and work orders."
        ),
        "stale": (
            "When the epic registry is stale, it means the catalog has not been updated recently. "
            "The epic entries might still be accurate, but you cannot be certain. This is similar "
            "to a library that has not recorded new books — the books might be on the shelf, "
            "but the catalog cannot confirm it."
        ),
        "absent": (
            "An absent epic registry means no epics have been registered at all. This is like "
            "a library with books on the shelves but no catalog system. The capability work may "
            "exist, but it cannot be tracked or verified through governed processes."
        ),
    },
    "RUNTIME_PROVENANCE": {
        "description": (
            "Runtime provenance traces evidence from source code through build, test, and "
            "deployment. It is the chain of custody for digital artifacts. Each link in the "
            "chain must be intact for the evidence to be trusted. Think of it like the "
            "evidence bag in a forensic investigation — if the seal is broken, the evidence "
            "cannot be used."
        ),
    },
    "PROJECTION_PROVENANCE": {
        "description": (
            "Projection provenance is the final validation layer. It checks that what a user "
            "sees (the surface) matches what the evidence says (the projection). A missing "
            "projection receipt means the surface might be displaying stale or incorrect state. "
            "This is like a dashboard gauge that is not connected to the actual sensor — the "
            "needle moves, but you cannot trust the reading."
        ),
    },
}

# Fallback for uncategorized findings
FALLBACK_EXPLANATION = (
    "This diagnostic finding represents a signal from the Librarian evidence plane. "
    "Understanding what each finding means, why it was generated, and what the appropriate "
    "response is, is a core skill in governed development."
)

# Quiz reference mappings: finding categories → relevant quiz questions
QUIZ_REF_MAP = {
    "CURSOR": ["l1-q1", "l1-q3", "l2-q1"],
    "RECONCILIATION": ["l1-q2", "l2-q2"],
    "EPIC": ["l1-q4", "l2-q3"],
    "RUNTIME_PROVENANCE": ["l2-q1", "l2-q2", "l3-q1"],
    "PROJECTION_PROVENANCE": ["l1-q4", "l2-q3", "l3-q2"],
}


def _generate_lo_id(finding):
    """Generate a deterministic learning object ID from a finding."""
    code = finding.get("code", "UNKNOWN")
    seq = finding.get("finding_id", "F-0000").replace("F-", "")
    return f"LO-{code}-{seq}"


def _get_finding_category(finding):
    """Get the category for a finding, falling back to first segment of code."""
    cat = finding.get("category", "")
    if cat and cat in EXPLANATION_TEMPLATES:
        return cat
    
    # Derive from code prefix
    code = finding.get("code", "")
    if code.startswith("EV-GOV"):
        return "CURSOR"
    elif code.startswith("EV-EVID"):
        return "RECONCILIATION"
    elif code.startswith("EV-SRC") or code.startswith("EV-RUNTIME"):
        return "RUNTIME_PROVENANCE"
    elif code.startswith("EV-PROJ"):
        return "PROJECTION_PROVENANCE"
    elif code.startswith("EV-CONFLICT"):
        return "RECONCILIATION"
    return "CURSOR"


def _generate_explanation(finding):
    """Generate an educational explanation from a finding."""
    category = _get_finding_category(finding)
    templates = EXPLANATION_TEMPLATES.get(category, {})
    
    evidence_status = finding.get("evidence_status", "")
    status = finding.get("status", "CONFIRMED")
    severity = finding.get("severity", "MEDIUM")
    finding_text = finding.get("finding", "")
    
    parts = []
    
    # Opening: what this finding is about
    desc = templates.get("description", FALLBACK_EXPLANATION)
    parts.append(desc)
    
    # Context from the actual finding
    if finding_text:
        parts.append(f"\n\nThe specific finding is: \"{finding_text}\"")
    
    # Category-specific elaboration based on status
    if status == "ABSENT" or evidence_status == "ABSENT":
        status_text = templates.get("absent")
        if status_text:
            parts.append(f"\n\n{status_text}")
    elif status in ("STALE", "CONFIRMED"):
        stale_text = templates.get("stale")
        if stale_text:
            parts.append(f"\n\n{stale_text}")
    
    # Severity context
    if severity == "HIGH":
        parts.append(
            "\n\nThe evidence plane classifies this finding as HIGH severity, which means "
            "it affects critical governance processes. Understanding this finding is "
            "important before making lifecycle decisions."
        )
    elif severity == "MEDIUM":
        parts.append(
            "\n\nThis finding is classified as MEDIUM severity. It represents a standard "
            "governance signal that should be understood and monitored."
        )
    
    # Category-specific teaching
    if category == "CURSOR":
        parts.append(
            "\n\nAs a training technician, your role is to identify cursor state, "
            "understand what it means for governance, and communicate the status to "
            "the appropriate team. You do not resolve cursor issues yourself — that is "
            "a governed workflow action."
        )
    elif category in ("RUNTIME_PROVENANCE", "PROJECTION_PROVENANCE"):
        parts.append(
            "\n\nProvenance analysis is a diagnostic skill. You identify where the chain "
            "is broken and explain the implications. Repairing provenance is a separate "
            "governed action performed by authorized workflows."
        )
    elif category == "RECONCILIATION":
        parts.append(
            "\n\nReconciliation gaps are governance signals. They tell you that verification "
            "has not been completed. Your role is to detect and report the gap, not to "
            "perform the reconciliation yourself."
        )
    
    return "".join(parts)


def _generate_learning_object(finding, seq_num=1):
    """Generate a complete learning object from a diagnostic finding."""
    code = finding.get("code", "UNKNOWN")
    category = _get_finding_category(finding)
    lo_id = _generate_lo_id(finding)
    severity = finding.get("severity", "MEDIUM")
    
    # Title
    code_desc = code.replace("EV-", "").replace("-", " ")
    title = f"Understanding {code_desc.title()}"
    
    # Objective
    objective = (
        f"The learner will understand what finding {code} means, why it was generated "
        f"by the evidence plane, and how to interpret its severity ({severity}) and "
        f"category ({category}) in a governed development context."
    )
    
    # Explanation
    explanation = _generate_explanation(finding)
    
    # Evidence refs
    evidence_refs = []
    for ref in finding.get("evidence_refs", []):
        evidence_refs.append({
            "type": ref.get("type", "evidence_snapshot"),
            "ref": ref.get("ref", ""),
            "description": ref.get("description", ""),
        })
    if not evidence_refs:
        evidence_refs.append({
            "type": "evidence_snapshot",
            "ref": finding.get("run_id", "unknown"),
            "description": f"Evidence plane evaluation containing finding {finding.get('finding_id', 'unknown')}",
        })
    
    # Quiz refs
    quiz_refs = QUIZ_REF_MAP.get(category, ["l1-q1", "l1-q3"])
    
    # Certification criteria
    cert_criteria = [
        {
            "id": f"LO-CERT-{seq_num:03d}-001",
            "description": f"Learner can explain what finding {code} means in the context of governed development",
            "required": True,
        },
        {
            "id": f"LO-CERT-{seq_num:03d}-002",
            "description": f"Learner can identify the finding's severity ({severity}) and category ({category}) from evidence plane output",
            "required": True,
        },
        {
            "id": f"LO-CERT-{seq_num:03d}-003",
            "description": "Learner can describe the appropriate response to this finding without attempting to unilaterally resolve it",
            "required": True,
        },
    ]
    
    learning_object = {
        "schema": "learning-object-v1",
        "id": lo_id,
        "title": title,
        "source": {
            "finding_code": code,
            "finding_id": finding.get("finding_id", ""),
            "evidence_refs": evidence_refs,
            "confidence": finding.get("confidence", "DERIVED"),
        },
        "learning": {
            "objective": objective,
            "explanation": explanation,
            "tags": [category.lower(), code.lower(), severity.lower()],
        },
        "exercise": {
            "scenario_id": f"{code.lower()}-scenario",
            "setup": (
                f"You are reviewing evidence plane output for a governed project. "
                f"The evaluation reports finding {finding.get('finding_id', 'unknown')} "
                f"({code}) with {severity} severity in the {category} category. "
                f"Your task: interpret the finding, understand what it means for "
                f"governance posture, and explain it to a team member."
            ),
            "expected_observations": [
                {
                    "observation": f"Identify that the finding code is {code} and category is {category}",
                    "evidence_link": f"finding_id={finding.get('finding_id', 'unknown')}",
                },
                {
                    "observation": f"Determine the severity ({severity}) and what it implies for governance decisions",
                    "evidence_link": "severity field in diagnostic-finding-v1",
                },
            ],
        },
        "assessment": {
            "quiz_refs": quiz_refs,
            "scoring_model": "composite",
        },
        "certification": {
            "criteria": cert_criteria,
            "passing_score": 80,
        },
        "advisory_only": True,
        "no_seal_authority": True,
        "metadata": {
            "generated_at": now_utc(),
            "version": GENERATOR_VERSION,
            "author": "evidence-to-lesson-generator",
        },
    }
    
    return learning_object


def _validate_learning_object(lo):
    """Validate a learning object against the schema using the validator script."""
    import subprocess
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(lo, f, indent=2)
        tmp_path = f.name
    
    try:
        result = subprocess.run(
            ["python3", str(VALIDATOR_SCRIPT), tmp_path],
            capture_output=True, text=True, timeout=10,
        )
        valid = result.returncode == 0
        return valid, result.stdout
    finally:
        os.unlink(tmp_path)


# ── Commands ─────────────────────────────────────────────────────────────

def cmd_list_findings(args):
    """List all available diagnostic findings from the evidence plane."""
    data, error = _load_sdk()
    if error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    
    findings = data["findings"]
    print(f"Evidence Plane: {data.get('run_id', 'unknown')}")
    print(f"Total findings: {len(findings)}")
    print()
    print(f"{'ID':<12} {'Code':<20} {'Severity':<10} {'Category':<22} Finding")
    print("-" * 100)
    for f in findings:
        fid = f.get("finding_id", "??")
        code = f.get("code", "??")
        sev = f.get("severity", "??")
        cat = f.get("category", "??")
        finding = f.get("finding", "")[:45]
        print(f"{fid:<12} {code:<20} {sev:<10} {cat:<22} {finding}")
    return 0


def cmd_generate(args):
    """Generate learning objects for specific findings or codes."""
    if not args:
        print("Usage: lesson_generator.py generate <finding-code> [<finding-code> ...]")
        print("       lesson_generator.py generate-all")
        print("       lesson_generator.py generate-epic")
        return 1
    
    data, error = _load_sdk()
    if error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    
    findings = data["findings"]
    
    # Filter findings by requested codes or IDs
    targets = set(args)
    matched = []
    
    for f in findings:
        fid = f.get("finding_id", "")
        code = f.get("code", "")
        if fid in targets or code in targets:
            matched.append(f)
        # Also match by category for generate-epic
        if "epic" in targets and f.get("category") in ("CURSOR", "RECONCILIATION", "EPIC",
                                                         "RUNTIME_PROVENANCE", "PROJECTION_PROVENANCE"):
            if f not in matched:
                matched.append(f)
    
    if not matched:
        print(f"No findings matched: {targets}", file=sys.stderr)
        print("Use 'list-findings' to see available findings.", file=sys.stderr)
        return 1
    
    # Generate learning objects
    learning_objects = []
    for i, finding in enumerate(matched):
        lo = _generate_learning_object(finding, i + 1)
        # Validate
        valid, validation_output = _validate_learning_object(lo)
        lo["_validation"] = {
            "valid": valid,
            "output": validation_output.strip() if validation_output else "",
        }
        learning_objects.append(lo)
    
    # Output
    output = {
        "generator_version": GENERATOR_VERSION,
        "sdk_version": SDK_VERSION,
        "generated_at": now_utc(),
        "run_id": data.get("run_id", "unknown"),
        "findings_processed": len(matched),
        "learning_objects_generated": len(learning_objects),
        "all_validated": all(lo["_validation"]["valid"] for lo in learning_objects),
        "learning_objects": learning_objects,
        "advisory_only": True,
    }
    
    print(json.dumps(output, indent=2, default=str))
    return 0 if output["all_validated"] else 1


def cmd_generate_all(args):
    """Generate learning objects for all available findings."""
    data, error = _load_sdk()
    if error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    
    findings = data["findings"]
    all_codes = [f.get("code") for f in findings if f.get("code")]
    return cmd_generate(all_codes)


def cmd_generate_epic(args):
    """Generate learning objects for all Evidence Plane categories."""
    return cmd_generate(["epic"])


def cmd_output(args):
    """Write a generated learning object to a JSON file."""
    if not args:
        print("Usage: lesson_generator.py output <lo-id>")
        return 1
    
    lo_id = args[0]
    data, error = _load_sdk()
    if error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    
    findings = data["findings"]
    for i, finding in enumerate(findings):
        candidate_id = _generate_lo_id(finding)
        if candidate_id == lo_id:
            lo = _generate_learning_object(finding, i + 1)
            output_dir = REPO_ROOT / "data" / "learning-objects"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{lo_id}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(lo, f, indent=2, default=str)
            print(f"Written: {output_path}")
            valid, val_out = _validate_learning_object(lo)
            print(f"Validates: {'PASS' if valid else 'FAIL'}")
            return 0
    
    print(f"Learning object not found: {lo_id}", file=sys.stderr)
    return 1


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("QA Pilot Evidence-to-Lesson Generator — QA-PILOT-EVIDENCE-TO-LESSON-GENERATOR-1")
        print()
        print("Usage:")
        print("  list-findings              — List available diagnostic findings")
        print("  generate <code>...         — Generate LO for specific finding codes")
        print("  generate-all               — Generate LOs for all findings")
        print("  generate-epic              — Generate LOs for Evidence Plane categories")
        print("  output <lo-id>             — Write a LO to disk")
        print()
        print("Authority: advisory-only. Learning objects reference evidence; they do not create evidence.")
        return 0

    command = sys.argv[1]
    cmd_args = sys.argv[2:]

    commands = {
        "list-findings": cmd_list_findings,
        "generate": cmd_generate,
        "generate-all": cmd_generate_all,
        "generate-epic": cmd_generate_epic,
        "output": cmd_output,
    }

    if command not in commands:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(f"Valid: {', '.join(commands.keys())}", file=sys.stderr)
        return 1

    return commands[command](cmd_args)


if __name__ == "__main__":
    sys.exit(main())
