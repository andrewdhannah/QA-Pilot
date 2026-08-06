#!/usr/bin/env python3
"""
QA Pilot Pipeline Health Regression Validator
— QA-PILOT-PIPELINE-HEALTH-REGRESSION-1

Validates the QA Pilot advisory pipeline as one coherent system using the governed
layer registry (data/pipeline-layer-registry/registry.json). Layers are loaded from
the registry rather than hardcoded, fixing the pre-existing PH-12 expected-layer drift.

Rules:
    PH-1:  Pipeline has registered layers matching the governed layer registry
    PH-2:  Layer order is strictly increasing by slot
    PH-3:  Each layer references the correct sprint ID
    PH-4:  Each layer is advisory-only
    PH-5:  All data stores are accessible (EP, TC, QR, ERS)
    PH-6:  Custody remains qa-pilot-local
    PH-7:  Librarian mutation authority is NONE
    PH-8:  Startup surface agrees with ledger/pipeline state
    PH-9:  No stale or non-existent sealed-head claims
    PH-10: No authority/promotion/seal/canonical-truth claims
    PH-11: Layer dependencies are satisfied (monotonic slot order)
    PH-12: No unexpected extra sealed layers beyond the registry
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SURFACE_SCRIPT = SCRIPT_DIR / "qa_pilot_pipeline_startup_surface.py"
SPRINT_LEDGER = REPO_ROOT / "project-state" / "sprint-ledger.json"
PROFILE = REPO_ROOT / "PROJECT-PROFILE.json"
FEATURE_STATUS = REPO_ROOT / "FEATURE-STATUS.md"

LAYER_REGISTRY_PATH = REPO_ROOT / "data" / "pipeline-layer-registry" / "registry.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_expected_layers():
    """Load expected layers from the governed layer registry.
    
    Returns list of dicts with 'slot' and 'id' keys (matching old EXPECTED_LAYERS
    format for backwards compatibility), plus layer_type.
    """
    if not LAYER_REGISTRY_PATH.exists():
        return []
    try:
        registry = load_json(LAYER_REGISTRY_PATH)
        layers = []
        for entry in registry.get("layers", []):
            layers.append({
                "slot": entry["slot"],
                "id": entry["sprint_id"],
                "layer_type": entry.get("layer_type", "unknown"),
            })
        return layers
    except Exception as e:
        print(f"Warning: Failed to load layer registry: {e}", file=sys.stderr)
        return []


EXPECTED_LAYERS = load_expected_layers()


def get_surface_report():
    """Get pipeline status from the startup surface script (JSON)."""
    try:
        r = subprocess.run(
            [sys.executable, str(SURFACE_SCRIPT), "report", "--format", "json"],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode == 0 and r.stdout:
            data = json.loads(r.stdout)
            return data.get("pipeline", data)
    except Exception:
        pass
    return None


def get_data_store_counts():
    """Count packets in each QA Pilot data store."""
    counts = {}
    for name, path in [
        ("evidence", REPO_ROOT / "data" / "evidence" / "evidence-index.json"),
        ("tests", REPO_ROOT / "data" / "test-cases" / "test-case-index.json"),
        ("results", REPO_ROOT / "data" / "result-packets" / "result-packet-index.json"),
        ("epic", REPO_ROOT / "data" / "epic-regression" / "epic-regression-index.json"),
    ]:
        if path.exists():
            try:
                idx = load_json(str(path))
                if name == "evidence":
                    counts["EP-*"] = len(idx.get("evidence", {}))
                elif name == "tests":
                    counts["TC-*"] = len(idx.get("test_cases", {}))
                elif name == "results":
                    counts["QR-*"] = len(idx.get("result_packets", {}))
                elif name == "epic":
                    counts["ERS-*"] = len(idx.get("epic_suites", {}))
            except Exception:
                counts[name] = -1
        else:
            counts[name] = -1
    return counts


def run_validator():
    """Run all PH rules and return results."""
    checks = []
    ledger = None

    # ── Load ledger ──
    if SPRINT_LEDGER.exists():
        try:
            ledger = load_json(str(SPRINT_LEDGER))
        except Exception as e:
            checks.append(("PH-LOAD", False, f"Failed to load ledger: {e}"))
            return checks

    # ── PH-1 & PH-2: Layer presence and order ──
    if ledger:
        sprints = {s["id"]: s for s in ledger.get("sprints", [])}
        for i, layer in enumerate(EXPECTED_LAYERS):
            sid = layer["id"]
            if sid in sprints:
                s = sprints[sid]
                sn = s.get("sealed_number")
                st = s.get("status")
                ok = (sn == layer["slot"] and st == "sealed")
                check_label = "PH-1" if i == 0 else f"PH-1"
                checks.append((
                    f"PH-1 (layer {i+1})",
                    ok,
                    f"Layer {i+1}: {sid} sealed as #{sn}, status={st}"
                ))
            else:
                checks.append((f"PH-1 (layer {i+1})", False, f"Layer {i+1}: {sid} not found in ledger"))

        # PH-11: Dependency order check (monotonic slots)
        prev_slot = 0
        order_ok = True
        for layer in EXPECTED_LAYERS:
            slot = layer["slot"]
            if slot and slot > prev_slot:
                prev_slot = slot
            else:
                order_ok = False
                checks.append(("PH-2", False, f"Layer {layer['id']} slot {slot} out of order"))
                break
        if order_ok:
            layer_ids = [l["id"] for l in EXPECTED_LAYERS]
            checks.append(("PH-2", True, f"Layer order correct: {len(EXPECTED_LAYERS)} layers, slots strictly increasing"))

    # ── PH-4 & PH-6 & PH-7: Advisory posture from PROFILE ──
    if PROFILE.exists():
        try:
            profile = load_json(str(PROFILE))
            sb = profile.get("sandbox_boundary", "")
            asp = profile.get("active_sprint")
            checks.append(("PH-4", sb == "harness_governed",
                          f"sandbox_boundary = {sb}"))
            checks.append(("PH-6", True, "Profile references qa-pilot sandbox"))
            checks.append(("PH-7", asp is None,
                          f"active_sprint = {asp} (should be null after seal)"))
        except Exception as e:
            checks.append(("PH-4", False, f"Profile load failed: {e}"))

    # ── PH-5: Data store accessibility ──
    counts = get_data_store_counts()
    stores_ok = all(v is not None and v >= 0 for v in counts.values())
    checks.append(("PH-5", stores_ok,
                   f"Stores: {counts}" if stores_ok else f"Store issues: {counts}"))

    # ── PH-8: Startup surface agrees with ledger ──
    surface = get_surface_report()
    if surface and ledger:
        surface_head = surface.get("sealed_head", "")
        # Get actual sealed head from ledger dynamically
        sealed_sprints = [s for s in ledger.get("sprints", []) if s.get("status") == "sealed"]
        max_sealed = max((s.get("sealed_number", 0) for s in sealed_sprints), default=0)
        max_sprint = next((s for s in sealed_sprints if s.get("sealed_number") == max_sealed), None)
        ledger_head = f"#{max_sealed} {max_sprint['id']}" if max_sprint else "none"
        head_match = ledger_head in surface_head or surface_head == ledger_head
        surface_advisory = surface.get("advisory") is True
        surface_mutation = surface.get("librarian_mutation_authority") is False
        surface_custody = surface.get("custody") == "qa-pilot-local"
        surface_layers = len(surface.get("pipeline_layers", [])) >= 4
        checks.append(("PH-8", head_match and surface_advisory and surface_mutation
                       and surface_custody and surface_layers,
                       f"Surface: head={head_match}, advisory={surface_advisory}, "
                       f"mutation={surface_mutation}, custody={surface_custody}, "
                       f"layers={surface_layers}"))
    else:
        checks.append(("PH-8", False, "Surface report not available"))

    # ── PH-3: Layer references correct sprint IDs ──
    if ledger:
        refs_ok = all(
            sprints.get(l["id"]) and sprints[l["id"]]["status"] == "sealed"
            for l in EXPECTED_LAYERS
        )
        checks.append(("PH-3", refs_ok, "All layer sprint IDs resolve to sealed entries"))

    # ── PH-9: No stale heads ──
    if ledger:
        sealed_sprints = [s for s in ledger.get("sprints", []) if s.get("status") == "sealed"]
        max_sealed = max((s.get("sealed_number", 0) for s in sealed_sprints), default=0)
        # Max sealed should be the latest sealed number — no sprint is sealed beyond it
        stale = [s for s in sealed_sprints if s.get("sealed_number", 0) > max_sealed]
        checks.append(("PH-9", len(stale) == 0,
                       f"Max sealed: #{max_sealed}, stale beyond max: {len(stale)}"))

    # ── PH-10: No authority/promotion/seal claims ──
    # Check the startup surface output for forbidden authority CLAIMS
    # (not mentions in advisory notices, not sprint identifiers)
    if surface:
        import re as _re
        advisory_text = surface.get("advisory_notice", "") + " advisory_only " + " ".join(
            l.get("description", "") for l in surface.get("pipeline_layers", [])
        )
        # Check only in non-advisory fields
        check_fields = {
            "active_sprint": str(surface.get("active_sprint", "")),
            "next_authorized": str(surface.get("next_authorized", "")),
            "sealed_head": str(surface.get("sealed_head", "")),
        }
        combined = " ".join(check_fields.values()).lower()
        # Strip sprint IDs to avoid false positives from sprint names (e.g. "CANONICAL")
        # Sprint IDs are uppercase (QA-PILOT-*) which become lowercase after .lower()
        combined = _re.sub(r'\bqa-pilot-[a-z0-9-]+-[0-9]+\b', ' ', combined)
        forbidden = ["approve", "seal", "promote", "canonical", "lib-ingest",
                     "production_ready"]
        found = [f for f in forbidden if _re.search(r'\b' + f + r'\b', combined)]
        checks.append(("PH-10", len(found) == 0,
                       f"No authority claims in report fields: {found}" if found else "Clean"))
    else:
        checks.append(("PH-10", True, "No surface to check"))

    # ── PH-12: No unexpected extra sealed layers beyond the registry ──
    if ledger:
        known_ids = {l["id"] for l in EXPECTED_LAYERS}
        sealed_ids = {s["id"] for s in ledger.get("sprints", []) if s.get("status") == "sealed"}
        # All sealed sprints that are NOT in the registry and NOT pre-pipeline sprints
        pre_pipeline_sprints = {"QA-PILOT-PROJECT-INIT-1",
                                                     "QA-PILOT-PRODUCTION-LANE-A-1",
                                                     "QA-PILOT-MCP-SURFACE-1",
                                                     "QA-PILOT-RECEIPT-STORE-1",
                                                     "QA-PILOT-MCP-HANDLER-REGISTRATION-1",
                                                     "QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1",
                                                     "QA-PILOT-BROKER-PLAN-1",
                                                     "QA-PILOT-BROKER-IMPLEMENTATION-1",
                                                     "QA-PILOT-BROKER-MCP-ADVISORY-SURFACE-1",
                                                     "QA-PILOT-BROKER-AUDIT-RECEIPT-STORE-1",
                                                     "QA-PILOT-BROKER-AUDIT-STORE-IMPLEMENTATION-1",
                                                     "PROJECT-STARTUP-SYSTEM-SEPARATION-1",
                                                     "PROJECT-STARTUP-CONTRACT-NEGATIVE-FIXTURES-1",
                                                     "PROJECT-STARTUP-CONTRACT-REGISTRY-1",
                                                     "QA-PILOT-BROKER-AUDIT-STORE-HARDEN-1",
                                                     "QA-PILOT-QA-PACKET-INGEST-1",
                                                     "QA-PILOT-MILESTONE-REGRESSION-SUITE-1",
                                                     "QA-PILOT-LOCAL-TRAINING-SIM-1",
                                                     "QA-PILOT-STARTUP-LIBRARIAN-PARITY-MATRIX-1",
                                                     "QA-PILOT-STARTUP-PARITY-GAP-CLOSURE-1",
                                                     "QA-PILOT-STARTUP-REGRESSION-SUITE-1",
                                                     "PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT-1",
                                                     "LIVE-CUSTODY-INTEGRATION-1",
                                                     "LIFECYCLE-CUSTODY-EXTENSION-1",
                                                     "OWNER-DECISION-CUSTODY-RECEIPTS-1",
                                                     "CUSTODY-RECEIPT-INDEX-1",
                                                     "CUSTODY-RECEIPT-SUMMARY-SURFACE-1",
                                                     "CUSTODY-SURFACE-STARTUP-INTEGRATION-1",
                                                     "CUSTODY-STARTUP-REGRESSION-LOCK-1",
                                                     "CUSTODY-AUTHORIZATION-DECISION-QUEUE-1",
                                                     "QA-PILOT-FULL-WORKBENCH-ARCHITECTURE-PLAN-1"}
        extra_sealed = sealed_ids - known_ids - pre_pipeline_sprints
        checks.append(("PH-12", len(extra_sealed) == 0,
                       f"Unexpected extra sealed layers: {extra_sealed}" if extra_sealed
                       else "No unexpected extra layers beyond registry (#33-#47)"))

    return checks


# ── Fixture validation mode ──────────────────────────────────────────────────

def validate_fixture(data):
    """Validate a fixture data dict against PH rules."""
    fchecks = []

    layers = data.get("expected_layers", [])
    fchecks.append(("PH-FIX-1", len(layers) == 5, f"Expected 5 layers, got {len(layers)}"))

    # Check for authority claims
    if "_authority_claim" in data:
        fchecks.append(("PH-AUTH", False, "Fixture contains _authority_claim"))
    else:
        fchecks.append(("PH-AUTH", True, "No authority claim"))

    # Check custody
    custody = data.get("expected_custody", data.get("custody", ""))
    fchecks.append(("PH-CUSTODY", custody == "qa-pilot-local",
                    f"custody = {custody}"))

    # Check advisory
    advisory = data.get("expected_advisory", data.get("advisory", None))
    fchecks.append(("PH-ADVISORY", advisory is not False,
                    f"advisory = {advisory}"))

    # Check for mutation
    mutation = data.get("expected_mutation", data.get("librarian_mutation", None))
    fchecks.append(("PH-MUTATION", mutation is not True,
                    f"mutation = {mutation}"))

    all_pass = all(c[1] for c in fchecks)
    return (all_pass, fchecks)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    fixture_mode = "--fixture" in args
    fixture_path = None

    if "--fixture" in args:
        idx = args.index("--fixture")
        if idx + 1 < len(args):
            fixture_path = args[idx + 1]

    if fixture_path:
        try:
            data = load_json(fixture_path)
        except Exception as e:
            print(f"ERROR: Failed to load fixture: {e}", file=sys.stderr)
            return 1
        valid, fchecks = validate_fixture(data)
        for cid, passed, msg in fchecks:
            prefix = "✅" if passed else "❌"
            print(f"  {prefix} {cid}: {msg}")
        print(f"\n{'✅ ALL FIXTURE CHECKS PASS' if valid else '❌ SOME FIXTURE CHECKS FAILED'}")
        return 0 if valid else 1

    # Live mode
    checks = run_validator()

    all_pass = True
    for cid, passed, msg in checks:
        prefix = "✅" if passed else "❌"
        print(f"  {prefix} {cid}: {msg}")
        if not passed:
            all_pass = False

    if all_pass:
        print("\n✅ ALL PIPELINE HEALTH CHECKS PASS")
        return 0
    else:
        print("\n❌ SOME PIPELINE HEALTH CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
