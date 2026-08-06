#!/usr/bin/env python3
"""
QA Pilot Training Sim Advisory Review CLI — QA-PILOT-TRAINING-SIM-ADVISORY-REVIEW-1

Generates, lists, validates, and manages advisory review summaries for training sim cases.

Commands:
    list                           — List generated advisory reviews
    show <review_id>               — Show details of a specific review
    summary <review_id>            — Show summary of a specific review
    validate <path>                — Validate a review file against schema
    status                         — Show review store status
    clear                          — Clear all reviews

Authority: advisory-only. No apply path, no training behavior, no MCP bridge.
"""

import json
import os
import sys
import datetime
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
REVIEWS_DIR = REPO_ROOT / "data" / "reviews"
REVIEW_INDEX_FILE = REPO_ROOT / "data" / "reviews" / "review-index.json"
REVIEW_SCHEMA = REPO_ROOT / "docs" / "schemas" / "qa-pilot-advisory-review.schema.json"


def ensure_dirs():
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)


def load_index():
    if REVIEW_INDEX_FILE.exists():
        with open(REVIEW_INDEX_FILE, "r") as f:
            return json.load(f)
    return {"reviews": [], "review_count": 0, "last_generated_at": None}


def save_index(index):
    with open(REVIEW_INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)


def load_json(path):
    path = Path(path)
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_list(args):
    """List generated advisory reviews."""
    review_index = load_index()
    reviews = review_index.get("reviews", [])
    if not reviews:
        print("No advisory reviews generated.")
        return 0

    print(f"Advisory reviews ({len(reviews)} total):")
    print()
    for r in reviews:
        print(f"  {r['review_id']}")
        print(f"    Type:      {r.get('review_type', 'unknown')}")
        print(f"    Source:    {r.get('source_sim_id', 'unknown')}")
        print(f"    Generated: {r.get('generated_at', 'unknown')}")
        print(f"    Advisory:  {r.get('advisory', 'unknown')}")
        print()
    return 0


def cmd_show(args):
    """Show details of a specific review."""
    if len(args) < 1:
        print("Usage: qa_pilot_advisory_review.py show <review_id>")
        return 1

    review_id = args[0]
    review_path = REVIEWS_DIR / f"{review_id}.json"
    if not review_path.exists():
        print(f"Review not found: {review_id}")
        return 1

    review = load_json(str(review_path))
    if not review:
        print(f"Failed to load review: {review_id}")
        return 1

    print(f"Advisory Review: {review_id}")
    print("=" * 50)
    print(f"Source Sim:     {review.get('source_sim_id', 'unknown')}")
    print(f"Review Type:    {review.get('review_type', 'unknown')}")
    print(f"Generated:      {review.get('generated_at', 'unknown')}")
    print(f"Advisory:        {review.get('advisory', 'unknown')}")
    print(f"Owner Required: {review.get('owner_decision_required', 'unknown')}")
    print()
    print("Summary:")
    print(review.get('summary', 'No summary available'))
    print()
    print("Review ID:      ", review.get('review_id', 'unknown'))
    print("Review Type:    ", review.get('review_type', 'unknown'))
    print("Source Sim:     ", review.get('source_sim_id', 'unknown'))
    print("Generated:      ", review.get('generated_at', 'unknown'))
    print("Advisory:        ", review.get('advisory', 'unknown'))
    print("Owner Required: ", review.get('owner_decision_required', 'unknown'))
    if 'notes' in review:
        print("Notes:          ", review['notes'])
    return 0


def cmd_summary(args):
    """Show summary of a specific review."""
    if len(args) < 1:
        print("Usage: qa_pilot_advisory_review.py summary <review_id>")
        return 1

    review_id = args[0]
    review_path = REVIEWS_DIR / f"{review_id}.json"
    if not review_path.exists():
        print(f"Review not found: {review_id}")
        return 1

    review = load_json(str(review_path))
    if not review:
        print(f"Failed to load review: {review_id}")
        return 1

    print(f"Summary for {review_id}")
    print("=" * 50)
    print(f"Type:           {review.get('review_type', 'unknown')}")
    print(f"Source Sim:     {review.get('source_sim_id', 'unknown')}")
    print(f"Generated:      {review.get('generated_at', 'unknown')}")
    print(f"Advisory:        {review.get('advisory', 'unknown')}")
    print(f"Owner Required: {review.get('owner_decision_required', 'unknown')}")
    print()
    print("Summary:")
    print(review.get('summary', 'No summary available'))
    return 0


def cmd_validate(args):
    """Validate a review file against schema."""
    if len(args) < 1:
        print("Usage: qa_pilot_advisory_review.py validate <path>")
        return 1

    path = args[0]
    result = subprocess.run(
        [sys.executable, str(REVIEW_SCHEMA)],
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    print(result.stdout)
    return result.returncode


def cmd_status(args):
    """Show review store status."""
    review_index = load_index()
    reviews = review_index.get("reviews", [])

    counts = {}
    for r in reviews:
        t = r.get("review_type", "unknown")
        counts[t] = counts.get(t, 0) + 1

    print("QA Pilot Advisory Review Store")
    print("=================================")
    print(f"Total reviews:     {len(reviews)}")
    print(f"Review path:       {REVIEWS_DIR}")
    print(f"Index path:        {REVIEW_INDEX_FILE}")
    print(f"Last generated:    {review_index.get('last_generated_at', 'never')}")
    print()
    if counts:
        print("By type:")
        for t, c in sorted(counts.items()):
            print(f"  {t}: {c}")
    print()
    print("Authority: advisory-only")
    print("No apply path, no training behavior, no MCP bridge")
    print("Status: advisory-only — no authority, no application")
    return 0


def cmd_clear(args):
    """Clear all advisory reviews."""
    review_index = load_index()
    count = len(review_index.get("reviews", []))

    # Remove review files
    for r in review_index.get("reviews", []):
        rp = Path(r.get("review_path", ""))
        if rp.exists():
            rp.unlink()

    # Reset index
    review_index["reviews"] = []
    review_index["review_count"] = 0
    review_index["last_generated_at"] = None
    save_index(review_index)

    print(f"Cleared {count} advisory reviews.")
    return 0


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("QA Pilot Advisory Review CLI — QA-PILOT-TRAINING-SIM-ADVISORY-REVIEW-1")
        print()
        print("Usage:")
        print("  list                           — List generated advisory reviews")
        print("  show <review_id>               — Show details of a specific review")
        print("  summary <review_id>            — Show summary of a specific review")
        print("  validate <path>                — Validate a review file against schema")
        print("  status                         — Show review store status")
        print("  clear                          — Clear all reviews")
        print()
        print("Authority: advisory-only. No apply path, no training behavior, no MCP bridge.")
        return 0

    command = sys.argv[1]
    cmd_args = sys.argv[2:]

    commands = {
        "list": cmd_list,
        "show": cmd_show,
        "summary": cmd_summary,
        "validate": cmd_validate,
        "status": cmd_status,
        "clear": cmd_clear,
    }

    if command not in commands:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(f"Valid commands: {', '.join(commands.keys())}", file=sys.stderr)
        return 1

    return commands[command](cmd_args)


if __name__ == "__main__":
    sys.exit(main())
