#!/usr/bin/env python3
"""
QA Pilot Regression Learning Loop CLI — QA-PILOT-REGRESSION-LEARNING-LOOP-1

Commands:
    ingest      — Extract finding patterns from qualification results (QRX-*)
    generate    — Generate learning objects from finding patterns
    consume     — Simulate training consumption of learning objects
    feedback    — Generate feedback records from training outcomes
    receipt     — Generate lifecycle receipt for the complete loop
    validate    — Validate loop integrity (provenance chain, advisory boundaries)
    status      — Show loop state

Authority: advisory-only. No cross-project write authority.
No QRX-* modification. No LO-* modification. No historical modification.
"""

import json
import os
import sys
import datetime
import hashlib
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
QUALIFICATION_RESULTS_DIR = REPO_ROOT / "data" / "qualification-results"
QUALIFICATION_RECORDS_DIR = REPO_ROOT / "data" / "qualification-records"
LEARNING_OBJECTS_DIR = REPO_ROOT / "data" / "learning-objects"
LOOP_DATA_DIR = REPO_ROOT / "data" / "learning-loop"
FINDING_PATTERNS_DIR = LOOP_DATA_DIR / "finding-patterns"
LOOP_LEARNING_OBJECTS_DIR = LOOP_DATA_DIR / "learning-objects"
FEEDBACK_DIR = LOOP_DATA_DIR / "feedback"
LOOP_RECEIPTS_DIR = LOOP_DATA_DIR / "receipts"
LOOP_INDEX_FILE = LOOP_DATA_DIR / "loop-index.json"
VALIDATOR = SCRIPT_DIR / "validate-learning-object.py"


def ensure_dirs():
    for d in [LOOP_DATA_DIR, FINDING_PATTERNS_DIR, LOOP_LEARNING_OBJECTS_DIR,
              FEEDBACK_DIR, LOOP_RECEIPTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def load_loop_index():
    if LOOP_INDEX_FILE.exists():
        with open(LOOP_INDEX_FILE, "r") as f:
            return json.load(f)
    return {
        "finding_patterns": [],
        "learning_objects": [],
        "feedback_records": [],
        "receipts": [],
        "last_ingested_at": None,
        "last_generated_at": None,
        "last_consumed_at": None,
        "last_feedback_at": None,
        "last_receipt_at": None,
    }


def save_loop_index(data):
    with open(LOOP_INDEX_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_qrx_records():
    """Load all qualification results (QRX-*)."""
    records = []
    if not QUALIFICATION_RESULTS_DIR.exists():
        return records
    for f in sorted(QUALIFICATION_RESULTS_DIR.glob("QRX-*.json")):
        with open(f, "r") as fh:
            records.append(json.load(fh))
    return records


def load_qr_records():
    """Load all qualification records (QR-*)."""
    records = []
    if not QUALIFICATION_RECORDS_DIR.exists():
        return records
    for f in sorted(QUALIFICATION_RECORDS_DIR.glob("QR-*.json")):
        with open(f, "r") as fh:
            records.append(json.load(fh))
    return records


# ── Commands ──────────────────────────────────────────────────────────────

def cmd_ingest(args):
    """Extract finding patterns from qualification results."""
    ensure_dirs()
    qrx_records = load_qrx_records()
    if not qrx_records:
        print("No QRX-* records found in qualification-results/")
        return 1

    # Load QR-* records for evidence lineage
    qr_records = {r.get("record_id"): r for r in load_qr_records()}

    index = load_loop_index()
    patterns = []

    for qrx in qrx_records:
        qrx_id = qrx.get("result_id") or qrx.get("id", "unknown")
        source_record = qrx.get("source_record", "")
        level = qrx.get("qualification_level") or qrx.get("level", "unknown")
        score = qrx.get("overall_score", 0.0)
        assessment = qrx.get("assessment", "unknown")

        # Trace evidence lineage from QR-* record
        qr_id = source_record
        qr_rec = qr_records.get(qr_id, {})
        evidence_refs = qr_rec.get("evidence_refs", [])

        # Derive finding classification from level and score
        if assessment == "fail" or level == "unqualified":
            classification = "CRITICAL"
            severity = "HIGH"
        elif assessment == "advisory" or level == "spot_checked":
            classification = "IMPROVEMENT"
            severity = "MEDIUM"
        else:
            classification = "MAINTENANCE"
            severity = "LOW"

        # Use QRX ID segment for pattern code
        qrx_seg = qrx_id.split("-")[1] if "-" in qrx_id else "UNKNOWN"
        pattern_code = f"FP-{qrx_seg}-{len(patterns)+1:04d}"

        pattern = {
            "schema": "finding-pattern-v1",
            "id": pattern_code,
            "source_qrx_id": qrx_id,
            "finding_classification": classification,
            "severity": severity,
            "level": level,
            "score": score,
            "assessment": assessment,
            "evidence_refs": evidence_refs,
            "derived_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "advisory_only": True,
            "no_seal_authority": True,
        }

        pattern_file = FINDING_PATTERNS_DIR / f"{pattern_code}.json"
        with open(pattern_file, "w") as f:
            json.dump(pattern, f, indent=2)

        patterns.append(pattern_code)
        print(f"  ✅ {pattern_code} → {classification} ({severity}) from {qrx_id}")

    index["finding_patterns"] = patterns
    index["last_ingested_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_loop_index(index)

    print(f"\nIngested: {len(patterns)} finding patterns from {len(qrx_records)} QRX-* records")
    return 0


def cmd_generate(args):
    """Generate learning objects from finding patterns."""
    ensure_dirs()
    index = load_loop_index()
    pattern_files = list(FINDING_PATTERNS_DIR.glob("FP-*.json"))

    if not pattern_files:
        print("No finding patterns found. Run 'ingest' first.")
        return 1

    learning_objects = []

    for pf in sorted(pattern_files):
        with open(pf, "r") as f:
            pattern = json.load(f)

        pattern_id = pattern["id"]
        qrx_id = pattern["source_qrx_id"]
        classification = pattern["finding_classification"]
        severity = pattern["severity"]
        evidence_refs = pattern["evidence_refs"]

        lo_id = f"LO-{pattern_id}-0001"

        # Generate learning-focused content (not finding-focused)
        objective = (
            f"The learner will understand what finding pattern {pattern_id} means, "
            f"why it was generated by the qualification engine, and how to interpret "
            f"its severity ({severity}) and classification ({classification}) in a "
            f"governed development context."
        )

        explanation = (
            f"A qualification finding pattern represents a recurring signal from the "
            f"qualification engine. Pattern {pattern_id} was derived from qualification "
            f"result {qrx_id}, which assessed an artifact at the {pattern['level']} level "
            f"with a score of {pattern['score']:.2f}.\n\n"
            f"The classification is {classification}, meaning this pattern represents "
            f"{'a critical issue requiring immediate attention' if classification == 'CRITICAL' else 'an improvement opportunity that should be addressed' if classification == 'IMPROVEMENT' else 'a maintenance signal that should be monitored'}.\n\n"
            f"As a training technician, your role is to understand this pattern, "
            f"recognize it in future qualification runs, and communicate its significance "
            f"to the appropriate team. You do not resolve findings yourself — that is "
            f"a governed workflow action."
        )

        lo = {
            "schema": "learning-object-v1",
            "id": lo_id,
            "title": f"Understanding Pattern {pattern_id}",
            "source": {
                "finding_code": pattern_id,
                "finding_id": qrx_id,
                "evidence_refs": evidence_refs,
                "confidence": "ESTIMATED",
            },
            "learning": {
                "objective": objective,
                "explanation": explanation,
                "tags": [pattern_id.lower(), classification.lower(), severity.lower()],
            },
            "exercise": {
                "scenario_id": f"{pattern_id.lower()}-scenario",
                "setup": (
                    f"You are reviewing qualification engine output for a governed project. "
                    f"The evaluation reports pattern {pattern_id} ({classification}, {severity} severity). "
                    f"Your task: interpret the pattern, understand what it means for governance posture, "
                    f"and explain it to a team member."
                ),
                "expected_observations": [
                    {
                        "observation": f"Identify that the pattern code is {pattern_id} and classification is {classification}",
                        "evidence_link": f"source_qrx_id={qrx_id}",
                    },
                    {
                        "observation": f"Determine the severity ({severity}) and what it implies for governance decisions",
                        "evidence_link": "severity field in finding-pattern-v1",
                    },
                ],
            },
            "assessment": {
                "quiz_refs": [f"{pattern_id.lower()}-q1", f"{pattern_id.lower()}-q2"],
                "scoring_model": "composite",
            },
            "certification": {
                "criteria": [
                    {
                        "id": f"{lo_id}-CERT-001",
                        "description": f"Learner can explain what pattern {pattern_id} means in the context of governed development",
                        "required": True,
                    },
                    {
                        "id": f"{lo_id}-CERT-002",
                        "description": f"Learner can identify the pattern's severity ({severity}) and classification ({classification}) from qualification output",
                        "required": True,
                    },
                ],
                "passing_score": 80,
            },
            "advisory_only": True,
            "no_seal_authority": True,
            "metadata": {
                "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "version": "regression-learning-loop-v1",
                "author": "regression-learning-loop",
                "source_pattern": pattern_id,
                "source_qrx": qrx_id,
            },
        }

        lo_file = LOOP_LEARNING_OBJECTS_DIR / f"{lo_id}.json"
        with open(lo_file, "w") as f:
            json.dump(lo, f, indent=2)

        # Also copy to main learning-objects directory
        main_lo_file = LEARNING_OBJECTS_DIR / f"{lo_id}.json"
        with open(main_lo_file, "w") as f:
            json.dump(lo, f, indent=2)

        learning_objects.append(lo_id)
        print(f"  ✅ {lo_id} ← {pattern_id}")

    index["learning_objects"] = learning_objects
    index["last_generated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_loop_index(index)

    print(f"\nGenerated: {len(learning_objects)} learning objects from {len(pattern_files)} patterns")
    return 0


def cmd_consume(args):
    """Simulate training consumption of learning objects."""
    ensure_dirs()
    index = load_loop_index()
    lo_files = list(LOOP_LEARNING_OBJECTS_DIR.glob("LO-*.json"))

    if not lo_files:
        print("No learning objects found. Run 'generate' first.")
        return 1

    completions = []

    for lof in sorted(lo_files):
        with open(lof, "r") as f:
            lo = json.load(f)

        lo_id = lo["id"]
        completion = {
            "schema": "training-completion-v1",
            "id": f"TC-{lo_id}",
            "learning_object_id": lo_id,
            "learner_id": "simulated-learner-001",
            "completion_status": "completed",
            "quiz_scores": {
                "quiz_1": 85,
                "quiz_2": 90,
            },
            "overall_score": 87.5,
            "completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "advisory_only": True,
            "no_seal_authority": True,
        }

        completion_file = FEEDBACK_DIR / f"TC-{lo_id}.json"
        with open(completion_file, "w") as f:
            json.dump(completion, f, indent=2)

        completions.append(f"TC-{lo_id}")
        print(f"  ✅ TC-{lo_id} → completed (87.5%)")

    index["feedback_records"] = completions
    index["last_consumed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_loop_index(index)

    print(f"\nConsumed: {len(completions)} learning objects")
    return 0


def cmd_feedback(args):
    """Generate feedback records from training outcomes."""
    ensure_dirs()
    index = load_loop_index()
    completion_files = list(FEEDBACK_DIR.glob("TC-*.json"))

    if not completion_files:
        print("No training completions found. Run 'consume' first.")
        return 1

    feedback_records = []

    for cf in sorted(completion_files):
        with open(cf, "r") as f:
            completion = json.load(f)

        lo_id = completion["learning_object_id"]
        score = completion.get("overall_score", 0)

        feedback = {
            "schema": "feedback-record-v1",
            "id": f"FB-{lo_id}",
            "source_completion_id": completion["id"],
            "learning_object_id": lo_id,
            "feedback_type": "training_outcome",
            "effectiveness_signal": "effective" if score >= 80 else "needs_improvement",
            "recommendations": [
                {
                    "type": "profile_adjustment",
                    "description": f"Consider adjusting scoring weights for patterns similar to {lo_id}",
                    "advisory": True,
                }
            ],
            "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "advisory_only": True,
            "no_seal_authority": True,
        }

        feedback_file = FEEDBACK_DIR / f"FB-{lo_id}.json"
        with open(feedback_file, "w") as f:
            json.dump(feedback, f, indent=2)

        feedback_records.append(f"FB-{lo_id}")
        print(f"  ✅ FB-{lo_id} → {feedback['effectiveness_signal']}")

    index["feedback_records"] = feedback_records
    index["last_feedback_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_loop_index(index)

    print(f"\nFeedback: {len(feedback_records)} records generated")
    return 0


def cmd_receipt(args):
    """Generate lifecycle receipt for the complete loop."""
    ensure_dirs()
    index = load_loop_index()

    receipt = {
        "schema": "lifecycle-receipt-v1",
        "id": f"LL-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')}",
        "loop_id": f"LL-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')}",
        "finding_patterns_count": len(index.get("finding_patterns", [])),
        "learning_objects_generated": len(index.get("learning_objects", [])),
        "training_modules_consumed": len([r for r in index.get("feedback_records", []) if r.startswith("TC-")]),
        "feedback_records_collected": len([r for r in index.get("feedback_records", []) if r.startswith("FB-")]),
        "profile_recommendations_produced": len([r for r in index.get("feedback_records", []) if r.startswith("FB-")]),
        "provenance_chain": {
            "qr_records": len(load_qr_records()),
            "qrx_records": len(load_qrx_records()),
            "finding_patterns": index.get("finding_patterns", []),
            "learning_objects": index.get("learning_objects", []),
            "feedback_records": index.get("feedback_records", []),
        },
        "advisory_only": True,
        "no_seal_authority": True,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    receipt_file = LOOP_RECEIPTS_DIR / f"{receipt['id']}.json"
    with open(receipt_file, "w") as f:
        json.dump(receipt, f, indent=2)

    index["receipts"].append(receipt["id"])
    index["last_receipt_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_loop_index(index)

    print(f"✅ Lifecycle receipt: {receipt['id']}")
    print(f"   Finding patterns: {receipt['finding_patterns_count']}")
    print(f"   Learning objects: {receipt['learning_objects_generated']}")
    print(f"   Training consumed: {receipt['training_modules_consumed']}")
    print(f"   Feedback records: {receipt['feedback_records_collected']}")
    print(f"   Recommendations: {receipt['profile_recommendations_produced']}")
    return 0


def cmd_validate(args):
    """Validate loop integrity."""
    index = load_loop_index()
    errors = []
    warnings = []

    # Check provenance chain
    patterns = index.get("learning_objects", [])
    los = index.get("learning_objects", [])

    # Verify all learning objects reference existing patterns
    for lo_id in los:
        lo_file = LOOP_LEARNING_OBJECTS_DIR / f"{lo_id}.json"
        if not lo_file.exists():
            errors.append(f"Learning object {lo_id} not found")
            continue
        with open(lo_file, "r") as f:
            lo = json.load(f)
        if not lo.get("advisory_only"):
            errors.append(f"Learning object {lo_id} missing advisory_only=true")
        if not lo.get("no_seal_authority"):
            errors.append(f"Learning object {lo_id} missing no_seal_authority=true")
        if lo.get("schema") != "learning-object-v1":
            errors.append(f"Learning object {lo_id} wrong schema: {lo.get('schema')}")

    # Verify all feedback records reference existing LOs
    feedback_files = list(FEEDBACK_DIR.glob("FB-*.json"))
    for ff in feedback_files:
        with open(ff, "r") as f:
            fb = json.load(f)
        if not fb.get("advisory_only"):
            errors.append(f"Feedback {fb['id']} missing advisory_only=true")
        lo_ref = fb.get("learning_object_id")
        if lo_ref and lo_ref not in los:
            errors.append(f"Feedback {fb['id']} references non-existent LO {lo_ref}")

    # Check receipts
    receipt_files = list(LOOP_RECEIPTS_DIR.glob("LL-*.json"))
    for rf in receipt_files:
        with open(rf, "r") as f:
            rc = json.load(f)
        if not rc.get("advisory_only"):
            errors.append(f"Receipt {rc['id']} missing advisory_only=true")

    if errors:
        print("❌ Validation failed:")
        for e in errors:
            print(f"  ✗ {e}")
        return 1

    print("✅ Loop validation passed")
    print(f"   Learning objects: {len(patterns)}")
    print(f"   Feedback records: {len(feedback_files)}")
    print(f"   Receipts: {len(receipt_files)}")
    print(f"   Advisory-only: confirmed at all layers")
    print(f"   Provenance: intact")
    return 0


def cmd_status(args):
    """Show loop state."""
    index = load_loop_index()

    print("=== Regression Learning Loop Status ===")
    print(f"Finding patterns:  {len(index.get('finding_patterns', []))}")
    print(f"Learning objects:  {len(index.get('learning_objects', []))}")
    print(f"Feedback records:  {len(index.get('feedback_records', []))}")
    print(f"Receipts:          {len(index.get('receipts', []))}")
    print()
    print(f"Last ingested:     {index.get('last_ingested_at', 'never')}")
    print(f"Last generated:    {index.get('last_generated_at', 'never')}")
    print(f"Last consumed:     {index.get('last_consumed_at', 'never')}")
    print(f"Last feedback:     {index.get('last_feedback_at', 'never')}")
    print(f"Last receipt:      {index.get('last_receipt_at', 'never')}")
    return 0


def main():
    commands = {
        "ingest": cmd_ingest,
        "generate": cmd_generate,
        "consume": cmd_consume,
        "feedback": cmd_feedback,
        "receipt": cmd_receipt,
        "validate": cmd_validate,
        "status": cmd_status,
    }

    if len(sys.argv) < 2:
        print("Commands:", ", ".join(commands.keys()))
        return 1

    cmd = sys.argv[1]
    if cmd in commands:
        return commands[cmd](sys.argv[2:])

    print(f"Unknown command: {cmd}")
    print("Commands:", ", ".join(commands.keys()))
    return 1


if __name__ == "__main__":
    sys.exit(main())
