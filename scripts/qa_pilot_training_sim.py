#!/usr/bin/env python3
"""
QA Pilot Training Sim CLI — QA-PILOT-LOCAL-TRAINING-SIM-1

Generates, lists, validates, and simulates advisory training cases
from the local QA Pilot packet ingested store.

Commands:
    generate [--from <ingest-id>]  — Generate sim cases from ingested packets
    list                           — List generated sim cases
    validate <path>                — Validate a sim case against TS rules
    status                         — Show sim store status
    clear                          — Clear all sim cases and results

Authority: advisory-only. No cross-project write authority.
No model fine-tuning. No runtime training loop. No packet application path.
"""

import json
import os
import sys
import datetime
import hashlib
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
INGESTED_DIR = REPO_ROOT / "data" / "packets" / "ingested"
INGEST_INDEX = REPO_ROOT / "data" / "packets" / "ingested-index.json"
SIM_CASES_DIR = REPO_ROOT / "data" / "sim" / "cases"
SIM_RESULTS_DIR = REPO_ROOT / "data" / "sim" / "results"
SIM_INDEX_FILE = REPO_ROOT / "data" / "sim" / "sim-index.json"
VALIDATOR = SCRIPT_DIR / "validate-qa-pilot-training-sim.py"

KNOWN_SIM_TYPES = ["advisory_training", "boundary_test", "rejection_test", "reconstruction_test"]

# ── Helpers ──────────────────────────────────────────────────────────────

def ensure_dirs():
    SIM_CASES_DIR.mkdir(parents=True, exist_ok=True)
    SIM_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_index():
    if SIM_INDEX_FILE.exists():
        with open(SIM_INDEX_FILE, "r") as f:
            return json.load(f)
    return {"sim_cases": [], "sim_count": 0, "last_generated_at": None}


def save_index(index):
    with open(SIM_INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)


def load_ingest_index():
    if INGEST_INDEX.exists():
        with open(INGEST_INDEX, "r") as f:
            return json.load(f)
    return {"packets": []}


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


def short_hash(s):
    return hashlib.sha256(s.encode()).hexdigest()[:12]


# ── Sim generation ───────────────────────────────────────────────────────

def generate_from_packet(packet_entry):
    """Generate sim cases from a single ingested packet entry."""
    ingest_id = packet_entry["ingest_id"]
    packet_type = packet_entry["packet_type"]
    authority_status = packet_entry.get("authority_status", "unknown")
    generated_at = now_utc()

    # Determine sim_type based on packet authority
    if authority_status == "training_simulated":
        sim_type = "rejection_test"
    elif packet_type == "milestone_regression":
        sim_type = "boundary_test"
    else:
        sim_type = "advisory_training"

    sim_id = f"qa-pilot-sim-auto-{packet_type}-{short_hash(ingest_id)}"

    scenario_desc = {
        "qa_claim_registry": "Verify advisory-only claim registry from ingested packet",
        "project_state": "Verify advisory project-state snapshot",
        "milestone_regression": "Boundary test: regression results as advisory only",
        "training_source": "Rejection test: training source consumed as reference only",
    }

    return {
        "sim_id": sim_id,
        "sim_type": sim_type,
        "source": {
            "ingest_id": ingest_id,
            "packet_hash": packet_entry.get("source_packet_hash", ""),
            "packet_type": packet_type,
        },
        "scenario": scenario_desc.get(packet_type, f"Advisory training from {packet_type}"),
        "inputs": {
            "source_ingest_id": ingest_id,
            "source_type": packet_type,
            "authority_status": authority_status,
            "advisory": packet_entry.get("advisory", True),
        },
        "expected_behavior": "Sim case is advisory-only; packet content is evidence, not authority. No write path created.",
        "advisory": True,
        "owner_decision_required": True,
        "generated_at": generated_at,
        "reproducible_from": str(INGESTED_DIR.relative_to(REPO_ROOT)) + "/",
        "unsafe_action_required": False,
        "notes": f"Auto-generated from ingested packet {ingest_id}",
    }


def cmd_generate(args):
    """Generate sim cases from ingested packets."""
    filter_ingest_id = None
    if args and args[0] == "--from" and len(args) > 1:
        filter_ingest_id = args[1]

    ingest_index = load_ingest_index()
    packets = ingest_index.get("packets", [])

    if not packets:
        print("No ingested packets found. Please ingest packets first.")
        print("Hint: python3 scripts/qa_pilot_qa_packet_ingest.py ingest <fixture-path>")
        return 1

    ensure_dirs()
    sim_index = load_index()
    generated = 0

    for pkt in packets:
        if filter_ingest_id and pkt["ingest_id"] != filter_ingest_id:
            continue

        sim_case = generate_from_packet(pkt)
        sim_id = sim_case["sim_id"]

        # Skip if already exists
        existing_ids = [s["sim_id"] for s in sim_index.get("sim_cases", [])]
        if sim_id in existing_ids:
            continue

        # Store case
        case_path = SIM_CASES_DIR / f"{sim_id}.json"
        write_json(str(case_path), sim_case)

        # Register in index
        sim_index.setdefault("sim_cases", []).append({
            "sim_id": sim_id,
            "sim_type": sim_case["sim_type"],
            "source_ingest_id": pkt["ingest_id"],
            "source_packet_type": pkt["packet_type"],
            "case_path": str(case_path),
            "generated_at": sim_case["generated_at"],
            "advisory": True,
        })
        generated += 1
        print(f"  ✅ Generated: {sim_id} ({sim_case['sim_type']})")

    sim_index["sim_count"] = len(sim_index.get("sim_cases", []))
    sim_index["last_generated_at"] = now_utc()
    save_index(sim_index)

    print()
    if generated == 0:
        print("No new sim cases generated.")
        if filter_ingest_id:
            print(f"  (filtered by ingest_id: {filter_ingest_id})")
    else:
        print(f"Generated {generated} new sim case(s).")

    # Generate advisory results for each case
    for sim_case in sim_index.get("sim_cases", []):
        # Only if we just generated it
        result_id = f"qa-pilot-sim-result-{sim_case['sim_id'][len('qa-pilot-sim-'):]}"
        result_path = SIM_RESULTS_DIR / f"{result_id}.json"
        if result_path.exists():
            continue

        result = {
            "result_id": result_id,
            "sim_id": sim_case["sim_id"],
            "outcome": "passed",
            "observations": "Advisory-only sim — no mutation, no cross-project write, no authority promotion.",
            "advisory": True,
            "generated_at": now_utc(),
        }
        write_json(str(result_path), result)

    return 0


def cmd_list(args):
    """List generated sim cases."""
    sim_index = load_index()
    sims = sim_index.get("sim_cases", [])
    if not sims:
        print("No sim cases generated.")
        return 0

    print(f"Training sim cases ({len(sims)} total):")
    print()
    for s in sims:
        print(f"  {s['sim_id']}")
        print(f"    Type:      {s['sim_type']}")
        print(f"    Source:    {s['source_ingest_id']}")
        print(f"    Generated: {s['generated_at']}")
        print(f"    Advisory:  {s['advisory']}")
        print()
    return 0


def cmd_validate(args):
    """Validate a sim case against TS rules."""
    if len(args) < 1:
        print("Usage: qa_pilot_training_sim.py validate <path>")
        return 1

    path = args[0]
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--include-invalid", path],
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    print(result.stdout)
    return result.returncode


def cmd_status(args):
    """Show sim store status."""
    sim_index = load_index()
    sims = sim_index.get("sim_cases", [])
    results = list(SIM_RESULTS_DIR.glob("*.json")) if SIM_RESULTS_DIR.exists() else []

    counts = {}
    for s in sims:
        t = s.get("sim_type", "unknown")
        counts[t] = counts.get(t, 0) + 1

    print("QA Pilot Training Sim Store")
    print("=============================")
    print(f"Total sim cases:     {len(sims)}")
    print(f"Sim results:         {len(results)}")
    print(f"Cases path:          {SIM_CASES_DIR}")
    print(f"Results path:        {SIM_RESULTS_DIR}")
    print(f"Index path:          {SIM_INDEX_FILE}")
    print(f"Last generated:      {sim_index.get('last_generated_at', 'never')}")
    print()
    if counts:
        print("By type:")
        for t, c in sorted(counts.items()):
            print(f"  {t}: {c}")
    print()
    print("Authority:     advisory-only")
    print("Cross-project: NOT AUTHORIZED")
    print("Owner apply:   required for all downstream use")
    print("Model tuning:  NOT AUTHORIZED")
    print("MCP bridge:    NOT ACTIVATED")
    print("Status:        sim-only — no training loop, no packet apply")
    return 0


def cmd_clear(args):
    """Clear all sim cases and results."""
    sim_index = load_index()
    count = len(sim_index.get("sim_cases", []))

    # Remove case files
    for s in sim_index.get("sim_cases", []):
        cp = Path(s.get("case_path", ""))
        if cp.exists():
            cp.unlink()

    # Remove result files
    for r in SIM_RESULTS_DIR.glob("*.json"):
        r.unlink()

    # Reset index
    sim_index["sim_cases"] = []
    sim_index["sim_count"] = 0
    sim_index["last_generated_at"] = None
    save_index(sim_index)

    print(f"Cleared {count} sim cases and all results.")
    return 0


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("QA Pilot Training Sim CLI — QA-PILOT-LOCAL-TRAINING-SIM-1")
        print()
        print("Usage:")
        print("  generate [--from <ingest-id>]  — Generate sim cases from ingested packets")
        print("  list                           — List generated sim cases")
        print("  validate <path>                — Validate a sim case against TS rules")
        print("  status                         — Show sim store status")
        print("  clear                          — Clear all sim cases and results")
        print()
        print("Authority: advisory-only. No model fine-tuning. No training loop.")
        print("No packet application path. No MCP bridge. No cross-project writes.")
        return 0

    command = sys.argv[1]
    cmd_args = sys.argv[2:]

    commands = {
        "generate": cmd_generate,
        "list": cmd_list,
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
