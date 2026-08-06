#!/usr/bin/env python3
"""
QA Pilot Qualification Review Surface CLI.

Provides Owner-facing review surfaces for qualification results:
  - Decision packet generation (following existing QA Pilot CLI pattern)
  - Reviewer view of qualification results
  - Qualification status visibility
  - Startup surface extension
  - Owner review workflow

Commands:
  decision    Generate qualification decision packet
  review      Show reviewer-facing qualification summary
  status      Show qualification status visibility
  startup     Generate startup surface extension block
  list        List qualification decisions
  read        Read a specific decision packet

Pipeline:
  Qualification Results → Review Surface → Decision Artifact → Owner Review
"""
import argparse, json, os, sys, datetime, glob, textwrap

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "qualification-records")
STORE_INDEX = os.path.join(STORE_DIR, "qualification-index.json")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "data", "qualification-results")
RESULTS_INDEX = os.path.join(RESULTS_DIR, "results-index.json")
DECISIONS_DIR = os.path.join(PROJECT_ROOT, "docs", "decisions")
DECISIONS_INDEX = os.path.join(DECISIONS_DIR, "decisions-index.json")
EXECUTION_LOG_DIR = os.path.join(PROJECT_ROOT, "data", "qualification-execution-logs")
EXECUTION_LOG_INDEX = os.path.join(EXECUTION_LOG_DIR, "execution-log.json")

ADVISORY_DISCLAIMER = (
    "This decision packet connects qualification posture to Owner review. "
    "It does not authorize implementation, seal, ledger mutation, "
    "or cross-project writes. Custody is qa-pilot-local. "
    "Librarian impact is none."
)


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _today():
    return datetime.date.today().isoformat()


def _ensure_dirs():
    os.makedirs(DECISIONS_DIR, exist_ok=True)
    if not os.path.exists(DECISIONS_INDEX):
        with open(DECISIONS_INDEX, "w") as f:
            json.dump({"decisions": [], "last_updated": _now()}, f, indent=2)


def _load_index(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"records": [], "last_updated": _now()}


def _save_index(index, path):
    index["last_updated"] = _now()
    with open(path, "w") as f:
        json.dump(index, f, indent=2)


def _load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def _load_qr_record(rid):
    path = os.path.join(STORE_DIR, f"{rid}.json")
    return _load_json(path)


def _load_result(rid):
    # rid can be either QR-XXXX or QRX-XXXX — handle both
    if rid.startswith("QR-"):
        rid = f"QRX-{rid[3:]}"
    path = os.path.join(RESULTS_DIR, f"{rid}.json")
    return _load_json(path)


def _next_decision_id():
    """Generate next sequential decision ID."""
    _ensure_dirs()
    idx = _load_index(DECISIONS_INDEX)
    existing = idx.get("decisions", [])
    nums = []
    for d in existing:
        try:
            n = int(d.split("-")[-1])
            nums.append(n)
        except (ValueError, IndexError):
            pass
    next_num = max(nums) + 1 if nums else 1
    return f"QUALIFICATION-DECISION-{next_num:04d}"


def _write_decision_markdown(decision):
    """Write a decision packet as a Markdown document."""
    _ensure_dirs()
    md = f"""# Qualification Decision — {decision['decision_id']}

**Target:** {decision.get('target_id', 'N/A')}
**Type:** {decision.get('target_type', 'N/A')}
**Qualification Level:** {decision.get('qualification_level', 'N/A')}
**Assessment:** {decision.get('assessment', 'N/A')}
**Overall Score:** {decision.get('overall_score', 0):.4f}
**Decision:** {decision.get('decision', 'N/A')}
**Date:** {decision.get('generated_at', _now())[:10]}
**Source:** {decision.get('source_record', 'N/A')}

---

## Rationale

{decision.get('rationale', 'No rationale provided.')}

## Sub-dimension Scores

| Dimension | Score | Weight |
|-----------|-------|--------|
"""
    for dim, score in sorted(decision.get('sub_dimension_scores', {}).items()):
        md += f"| {dim} | {score:.4f} | {decision.get('score_weights', {}).get(dim, 'N/A')} |\n"

    md += f"""
## Evidence Refs

| Evidence ID | Type | Status |
|-------------|------|--------|
"""
    for ref in decision.get('evidence_refs', []):
        md += f"| {ref.get('evidence_id', 'N/A')} | {ref.get('evidence_type', 'N/A')} | {ref.get('verification_status', 'N/A')} |\n"

    md += f"""
## Authority Disclaimer

{ADVISORY_DISCLAIMER}
"""
    return md


def cmd_decision(args):
    """Generate a qualification decision packet."""
    _ensure_dirs()

    # Load source result
    result = _load_result(args.source)
    if result is None:
        print(f"Result for '{args.source}' not found.")
        return 1

    # Load source QR- record
    record = _load_qr_record(args.source)
    if record is None:
        print(f"Record '{args.source}' not found.")
        return 1

    decision_id = _next_decision_id()
    evidence_refs = record.get("evidence_refs", [])

    decision = {
        "decision_id": decision_id,
        "source_record": args.source,
        "target_id": record.get("target_id", "unknown"),
        "target_type": record.get("target_type", "unknown"),
        "qualification_type": record.get("qualification_type", "unknown"),
        "qualification_level": result.get("qualification_level", "unqualified"),
        "assessment": result.get("assessment", "fail"),
        "overall_score": result.get("overall_score", 0.0),
        "sub_dimension_scores": result.get("sub_dimension_scores", {}),
        "score_weights": {"schema_compliance": 0.25, "evidence_freshness": 0.20,
                          "evidence_diversity": 0.15, "authority_boundary": 0.25,
                          "provenance_quality": 0.15},
        "evidence_refs": evidence_refs,
        "violations": result.get("violations", []),
        "decision": args.decision,
        "rationale": args.rationale or f"Qualification assessment: {result.get('assessment', 'fail')} at level {result.get('qualification_level', 'unqualified')}",
        "advisory_only": True,
        "custody": "qa-pilot-local",
        "librarian_impact": "none",
        "generated_at": _now(),
        "generated_by": "qa-pilot-qualification-review-surface"
    }

    # Write JSON
    json_path = os.path.join(DECISIONS_DIR, f"{decision_id}.json")
    with open(json_path, "w") as f:
        json.dump(decision, f, indent=2)

    # Write Markdown
    md = _write_decision_markdown(decision)
    md_path = os.path.join(DECISIONS_DIR, f"{decision_id}.md")
    with open(md_path, "w") as f:
        f.write(md)

    # Update index
    idx = _load_index(DECISIONS_INDEX)
    if decision_id not in idx.get("decisions", []):
        idx.setdefault("decisions", []).append(decision_id)
        _save_index(idx, DECISIONS_INDEX)

    print(f"Decision packet generated:")
    print(f"  ID:      {decision_id}")
    print(f"  Target:  {decision['target_id']} ({decision['target_type']})")
    print(f"  Level:   {decision['qualification_level']}")
    print(f"  Assess:  {decision['assessment']}")
    print(f"  JSON:    {json_path}")
    print(f"  MD:      {md_path}")
    return 0


def cmd_review(args):
    """Show reviewer-facing qualification summary."""
    _ensure_dirs()

    idx = _load_index(RESULTS_INDEX)
    results = idx.get("results", [])

    if not results:
        print("No qualification results to review.")
        return 0

    # Level distribution
    by_level = {}
    by_type = {}
    by_assessment = {}
    target_info = []

    for rid in results:
        result = _load_result(rid)
        if not result:
            continue
        lv = result.get("qualification_level", "unknown")
        at = result.get("assessment", "unknown")
        tt = result.get("target_type", "unknown")
        by_level[lv] = by_level.get(lv, 0) + 1
        by_type[tt] = by_type.get(tt, 0) + 1
        by_assessment[at] = by_assessment.get(at, 0) + 1

        if args.detail:
            target_info.append({
                "id": rid,
                "target": result.get("target_id", "?"),
                "type": tt,
                "level": lv,
                "score": result.get("overall_score", 0),
                "assessment": at
            })

    print("=== Qualification Review Surface ===")
    print(f"\nSummary: {len(results)} qualified targets\n")

    print("By Assessment:")
    for at in ["pass", "advisory", "fail"]:
        count = by_assessment.get(at, 0)
        bar = "█" * min(count, 40)
        print(f"  {at:10s} {count:3d} {bar}")

    print(f"\nBy Level:")
    for lv in ["audited", "peer_reviewed", "spot_checked", "unqualified", "exempt"]:
        count = by_level.get(lv, 0)
        bar = "█" * min(count, 40)
        print(f"  {lv:16s} {count:3d} {bar}")

    print(f"\nBy Target Type:")
    for tt, count in sorted(by_type.items(), key=lambda x: -x[1]):
        bar = "█" * min(count, 40)
        print(f"  {tt:20s} {count:3d} {bar}")

    if args.detail and target_info:
        print(f"\nDetail ({len(target_info)} entries):")
        for t in target_info[:int(args.detail)]:
            print(f"  {t['id']:25s} {t['level']:16s} {t['score']:.4f}  {t['assessment']:8s}  {t['target'][:30]}")

    print(f"\n{ADVISORY_DISCLAIMER}")
    return 0


def cmd_status(args):
    """Show qualification status visibility."""
    _ensure_dirs()

    idx = _load_index(RESULTS_INDEX)
    store_idx = _load_index(STORE_INDEX)
    exec_idx = _load_index(EXECUTION_LOG_INDEX)

    results = idx.get("results", [])
    qr_records = store_idx.get("records", [])
    executions = exec_idx.get("executions", [])

    by_level = {}
    expired = 0
    for rid in results:
        result = _load_result(rid)
        lv = result.get("qualification_level", "unknown") if result else "unknown"
        by_level[lv] = by_level.get(lv, 0) + 1

    # Count expired
    for rid in qr_records:
        rec = _load_qr_record(rid)
        if rec and rec.get("lifecycle_state") == "expired":
            expired += 1

    last_run = executions[-1]["evaluated_at"][:10] if executions else "never"
    covered = len(results)
    total = len(qr_records)
    coverage_pct = round(covered / total * 100, 1) if total > 0 else 0

    print("=== Qualification Status ===")
    print(f"  Records:         {total}")
    print(f"  Evaluated:       {covered}")
    print(f"  Coverage:        {coverage_pct}%")
    print(f"  Expired:         {expired}")
    print(f"  Last evaluation: {last_run}")
    print(f"\n  Level Distribution:")
    for lv in ["audited", "peer_reviewed", "spot_checked", "unqualified", "exempt"]:
        count = by_level.get(lv, 0)
        bar = "█" * min(count, 40)
        print(f"    {lv:16s} {count:3d} {bar}")
    print(f"\n  Decisions:       {len(_load_index(DECISIONS_INDEX).get('decisions', []))}")
    print(f"\n  Results store:   {RESULTS_DIR}")
    print(f"  Decision store:  {DECISIONS_DIR}")
    return 0


def cmd_startup(args):
    """Generate startup surface extension block."""
    _ensure_dirs()

    results_idx = _load_index(RESULTS_INDEX)
    store_idx = _load_index(STORE_INDEX)
    decisions_idx = _load_index(DECISIONS_INDEX)
    exec_idx = _load_index(EXECUTION_LOG_INDEX)

    results = results_idx.get("results", [])
    qr_records = store_idx.get("records", [])

    by_level = {}
    by_type = {}
    for rid in results:
        result = _load_result(rid)
        if result:
            lv = result.get("qualification_level", "unknown")
            tt = result.get("target_type", "unknown")
            by_level[lv] = by_level.get(lv, 0) + 1
            by_type[tt] = by_type.get(tt, 0) + 1

    expired = sum(1 for rid in qr_records
                  if (_load_qr_record(rid) or {}).get("lifecycle_state") == "expired")

    last_exec = exec_idx.get("executions", [])
    last_date = last_exec[-1]["evaluated_at"][:10] if last_exec else "never"

    if args.format == "block":
        # Generate startup-ready text block
        block = f"""--- Qualification Posture ---
Qualified targets:     {len(results)}
By level:
  audited:             {by_level.get('audited', 0)}
  peer_reviewed:       {by_level.get('peer_reviewed', 0)}
  spot_checked:        {by_level.get('spot_checked', 0)}
  unqualified:         {by_level.get('unqualified', 0)}
  exempt:              {by_level.get('exempt', 0)}
By type:
"""
        for tt, count in sorted(by_type.items(), key=lambda x: -x[1]):
            block += f"  {tt:22s} {count}\n"
        block += f"Coverage:             {len(results)}/{len(qr_records)} ({round(len(results)/max(len(qr_records),1)*100,1)}%)\n"
        block += f"Expired:              {expired}\n"
        block += f"Decisions:            {len(decisions_idx.get('decisions', []))}\n"
        block += f"Latest qualification: {last_date}\n"
        print(block)
    else:
        # JSON format
        out = {
            "qualified_targets": len(results),
            "total_records": len(qr_records),
            "coverage_pct": round(len(results) / max(len(qr_records), 1) * 100, 1),
            "by_level": by_level,
            "by_type": by_type,
            "expired": expired,
            "decisions": len(decisions_idx.get("decisions", [])),
            "latest_qualification": last_date
        }
        print(json.dumps(out, indent=2))

    return 0


def cmd_list(args):
    """List qualification decisions."""
    _ensure_dirs()
    idx = _load_index(DECISIONS_INDEX)
    decisions = idx.get("decisions", [])

    if not decisions:
        print("No decisions recorded.")
        return 0

    print(f"{'Decision ID':30s} {'Target':25s} {'Level':16s} {'Decision':10s}")
    print("-" * 85)
    for did in decisions:
        d = _load_json(os.path.join(DECISIONS_DIR, f"{did}.json"))
        if d:
            print(f"{did:30s} {d.get('target_id','?'):25s} {d.get('qualification_level','?'):16s} {d.get('decision','?'):10s}")
    return 0


def cmd_read(args):
    """Read a specific decision packet."""
    _ensure_dirs()

    # Try JSON first
    d = _load_json(os.path.join(DECISIONS_DIR, f"{args.decision_id}.json"))
    if d is None:
        print(f"Decision '{args.decision_id}' not found.")
        return 1

    if args.format == "json":
        print(json.dumps(d, indent=2))
    else:
        md_path = os.path.join(DECISIONS_DIR, f"{args.decision_id}.md")
        if os.path.exists(md_path):
            with open(md_path) as f:
                print(f.read())
        else:
            print(json.dumps(d, indent=2))

    return 0


def main():
    parser = argparse.ArgumentParser(description="QA Pilot Qualification Review Surface CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # decision
    p = sub.add_parser("decision", help="Generate qualification decision packet")
    p.add_argument("--source", required=True, help="Source QR- record ID")
    p.add_argument("--decision", required=True, choices=["accept", "defer", "reject", "modify"],
                   help="Owner decision")
    p.add_argument("--rationale", help="Decision rationale")

    # review
    p = sub.add_parser("review", help="Show reviewer-facing qualification summary")
    p.add_argument("--detail", nargs="?", const="20", help="Show detail rows (default: 20)")

    # status
    sub.add_parser("status", help="Show qualification status visibility")

    # startup
    p = sub.add_parser("startup", help="Generate startup surface extension block")
    p.add_argument("--format", choices=["block", "json"], default="block",
                   help="Output format (default: block)")

    # list
    sub.add_parser("list", help="List qualification decisions")

    # read
    p = sub.add_parser("read", help="Read a specific decision packet")
    p.add_argument("decision_id", help="Decision ID")
    p.add_argument("--format", choices=["text", "json"], default="text",
                   help="Output format (default: text)")

    args = parser.parse_args()

    if args.command == "decision":
        return cmd_decision(args)
    elif args.command == "review":
        return cmd_review(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "startup":
        return cmd_startup(args)
    elif args.command == "list":
        return cmd_list(args)
    elif args.command == "read":
        return cmd_read(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
