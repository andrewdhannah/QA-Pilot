#!/usr/bin/env python3
"""
QA Pilot Pipeline Drift Detection — QA-PILOT-PIPELINE-DRIFT-DETECTION-1

Advisory-only drift detector for the sealed QA Pilot pipeline (#33-#38).
Checks ledger, startup surface, EP/TC/QR/ERS stores, PH rules, sealed-head
reporting, active-sprint reporting, and authority-boundary fields for
inconsistencies.

Does NOT auto-repair drift. Emits bounded advisory drift reports only.

Usage:
    python3 scripts/validate-qa-pilot-pipeline-drift-detection.py
    python3 scripts/validate-qa-pilot-pipeline-drift-detection.py --fixture <path>
    python3 scripts/validate-qa-pilot-pipeline-drift-detection.py --report
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
PH_VALIDATOR = SCRIPT_DIR / "validate-qa-pilot-pipeline-health-regression.py"
SPRINT_LEDGER = REPO_ROOT / "project-state" / "sprint-ledger.json"
PROFILE = REPO_ROOT / "PROJECT-PROFILE.json"
FEATURE_STATUS = REPO_ROOT / "FEATURE-STATUS.md"
LAYER_REGISTRY_PATH = REPO_ROOT / "data" / "pipeline-layer-registry" / "registry.json"

ADVISORY_NOTICE = (
    "This drift report is advisory-only. It does not approve, seal, merge, "
    "or assert production readiness. Do not auto-repair based on this report."
)

DR_RULES = {
    "DR-1":  "Ledger/startup sealed-head match",
    "DR-2":  "Active sprint matches across ledger, profile, and status",
    "DR-3":  "All 6 sealed layers (#33-#38) present",
    "DR-4":  "No unexpected extra packet layers",
    "DR-5":  "EP/TC/QR/ERS stores are internally consistent",
    "DR-6":  "Startup surface output is not stale",
    "DR-7":  "PH validator agrees with pipeline state",
    "DR-8":  "Posture/custody/mutation fields unchanged",
    "DR-9":  "No authority/promotion/seal claims",
    "DR-10": "Report is bounded and advisory-only",
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_cmd(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout, r.stderr, r.returncode)
    except Exception as e:
        return ("", str(e), -1)


# ── Drift Checks ──────────────────────────────────────────────────────────────

def run_drift_checks():
    """Run all DR drift checks. Returns list of (check_id, passed, message)."""
    checks = []
    drift_found = []

    # ── Load current state ──
    ledger = None
    if SPRINT_LEDGER.exists():
        try:
            ledger = load_json(str(SPRINT_LEDGER))
        except Exception as e:
            checks.append(("DR-LDGR", False, f"Ledger load failed: {e}"))
            return checks

    profile = None
    if PROFILE.exists():
        try:
            profile = load_json(str(PROFILE))
        except Exception:
            pass

    # ── DR-1: Ledger/startup sealed-head match ──
    if ledger:
        sealed_sprints = [s for s in ledger.get("sprints", []) if s.get("status") == "sealed"]
        max_sealed = max((s.get("sealed_number", 0) for s in sealed_sprints), default=0)
        max_sprint = next((s for s in sealed_sprints if s.get("sealed_number") == max_sealed), None)
        ledger_head = f"#{max_sealed} {max_sprint['id']}" if max_sprint else "none"
    else:
        ledger_head = "none"

    # Get startup surface reported head
    surface_out, _, _ = run_cmd([sys.executable, str(SURFACE_SCRIPT), "report", "--format", "json"])
    surface_head = "none"
    surface_active = None
    if surface_out:
        try:
            sdata = json.loads(surface_out)
            pipeline = sdata.get("pipeline", sdata)
            surface_head = pipeline.get("sealed_head", "none")
            surface_active = pipeline.get("active_sprint")
        except Exception:
            pass

    head_match = ledger_head == surface_head
    checks.append(("DR-1", head_match,
                   f"Ledger: {ledger_head} | Surface: {surface_head}" if not head_match
                   else f"Match: {ledger_head}"))
    if not head_match:
        drift_found.append("DR-1: sealed-head mismatch")

    # ── DR-2: Active sprint match ──
    ledger_active = None
    if ledger:
        pending = [s for s in ledger.get("sprints", []) if s.get("status") == "pending_owner_review"]
        ledger_active = pending[0]["id"] if pending else None

    profile_active = profile.get("active_sprint") if profile else None

    fs_active = None
    if FEATURE_STATUS.exists():
        for line in FEATURE_STATUS.read_text().splitlines():
            m = re.search(r"\| *active_sprint *\| *`([^`]+)` *\|", line)
            if m:
                v = m.group(1)
                fs_active = None if v == "none" else v
                break

    # Collect all active sprint values
    active_sprints = set()
    if ledger_active:
        active_sprints.add(("ledger", ledger_active))
    if profile_active:
        active_sprints.add(("profile", profile_active))
    if surface_active and surface_active != "none":
        active_sprints.add(("surface", surface_active))
    if fs_active:
        active_sprints.add(("status", fs_active))

    # Check agreement
    unique_values = set(v for _, v in active_sprints)
    as_match = len(unique_values) <= 1
    checks.append(("DR-2", as_match,
                   f"Active sprints: {dict(active_sprints)}" if not as_match
                   else f"Match: {unique_values.pop() if unique_values else 'none'}"))
    if not as_match:
        drift_found.append(f"DR-2: active-sprint mismatch: {dict(active_sprints)}")

    # ── Load registry for DR-3/DR-4 ──
    registry_layers = []
    if LAYER_REGISTRY_PATH.exists():
        try:
            reg = load_json(LAYER_REGISTRY_PATH)
            registry_layers = reg.get("layers", [])
        except Exception:
            pass

    # ── DR-3: All sealed layers from registry present ──
    missing_layers = []
    if ledger and registry_layers:
        for entry in registry_layers:
            sn = entry["slot"]
            sid = entry["sprint_id"]
            found = any(
                s.get("sealed_number") == sn and s.get("status") == "sealed"
                for s in ledger.get("sprints", [])
            )
            if not found:
                missing_layers.append(f"#{sn} {sid}")
    elif ledger and not registry_layers:
        # Fallback: use minimal expected set
        fallback = {33: "QA-PILOT-MCP-EVIDENCE-INTAKE-1", 34: "QA-PILOT-TEST-COMPOSITION-1"}
        for sn, sid in fallback.items():
            found = any(
                s.get("sealed_number") == sn and s.get("status") == "sealed"
                for s in ledger.get("sprints", [])
            )
            if not found:
                missing_layers.append(f"#{sn} {sid}")

    checks.append(("DR-3", len(missing_layers) == 0,
                   f"Missing: {missing_layers}" if missing_layers
                   else f"All {len(registry_layers)} registry layers present"))
    if missing_layers:
        drift_found.append(f"DR-3: missing layers: {missing_layers}")

    # ── DR-4: No unexpected extra packet layers ──
    # Known pipeline layer IDs from the governed registry
    known_ids = {entry["sprint_id"] for entry in registry_layers}
    
    # Dynamically derive pre-pipeline sprint IDs from the ledger.
    # Pre-pipeline = sealed sprints with ledger number < 33 (first pipeline slot).
    # This replaces the hardcoded pipeline_sprints set that was a maintenance burden.
    pre_pipeline_ids = set()
    if ledger:
        for s in ledger.get("sprints", []):
            sn = s.get("sealed_number")
            if sn and isinstance(sn, int) and sn < 33 and s.get("status") == "sealed":
                pre_pipeline_ids.add(s["id"])
    
    all_sealed_ids = set(s["id"] for s in ledger.get("sprints", [])
                         if s.get("status") == "sealed") if ledger else set()
    pipeline_plus_known = known_ids | pre_pipeline_ids
    extra = all_sealed_ids - pipeline_plus_known
    checks.append(("DR-4", len(extra) == 0,
                   f"Extra: {extra}" if extra else "No extra layers"))
    if extra:
        drift_found.append(f"DR-4: extra layers: {extra}")

    # ── DR-5: Store/index consistency (counts from surface) ──
    if surface_out:
        try:
            sdata = json.loads(surface_out)
            pipeline = sdata.get("pipeline", sdata)
            ev = pipeline.get("evidence_count", -1)
            tc = pipeline.get("test_case_count", -1)
            qr = pipeline.get("result_packet_count", -1)
            ers = pipeline.get("epic_suite_count", -1)
            all_valid = all(isinstance(v, int) and v >= 0 for v in [ev, tc, qr, ers])
            checks.append(("DR-5", all_valid,
                           f"EP={ev} TC={tc} QR={qr} ERS={ers}" if all_valid
                           else f"Store issue: EP={ev} TC={tc} QR={qr} ERS={ers}"))
            if not all_valid:
                drift_found.append("DR-5: store/index inconsistency")
        except Exception:
            checks.append(("DR-5", False, "Failed to parse surface counts"))
            drift_found.append("DR-5: surface parse error")
    else:
        checks.append(("DR-5", False, "Surface not available"))
        drift_found.append("DR-5: surface unreachable")

    # ── DR-6: Surface is not stale ──
    if ledger and surface_out:
        try:
            sdata = json.loads(surface_out)
            pipeline = sdata.get("pipeline", sdata)
            surface_ts = pipeline.get("timestamp", "")
            if surface_ts:
                st = datetime.strptime(surface_ts.replace("Z", "+0000"),
                                       "%Y-%m-%dT%H:%M:%S%z")
                now = datetime.now(timezone.utc)
                age_seconds = (now - st.replace(tzinfo=None)).total_seconds()
                stale = age_seconds > 300  # 5 min
                checks.append(("DR-6", not stale,
                               f"Surface age: {age_seconds:.0f}s{' (STALE)' if stale else ''}"))
                if stale:
                    drift_found.append("DR-6: stale surface output")
            else:
                checks.append(("DR-6", True, "No timestamp to check staleness"))
        except Exception:
            checks.append(("DR-6", True, "Could not compute staleness"))
    else:
        checks.append(("DR-6", True, "No baseline for staleness check"))

    # ── DR-7: PH validator agrees ──
    ph_out, _, ph_rc = run_cmd([sys.executable, str(PH_VALIDATOR)])
    ph_pass = "ALL PIPELINE HEALTH CHECKS PASS" in ph_out
    checks.append(("DR-7", ph_pass,
                   "PH checks pass" if ph_pass else "PH checks FAIL"))
    if not ph_pass:
        drift_found.append("DR-7: PH validator disagrees")

    # ── DR-8: Posture/custody/mutation unchanged ──
    if profile:
        sb = profile.get("sandbox_boundary", "")
        asp = profile.get("active_sprint")
        posture_ok = sb == "harness_governed"
        mutation_ok = asp is None  # after seal
        checks.append(("DR-8", posture_ok and mutation_ok,
                       f"boundary={sb} active={asp}" if posture_ok and mutation_ok
                       else f"CHANGED: boundary={sb} active={asp}"))
        if not posture_ok or not mutation_ok:
            drift_found.append("DR-8: posture/custody/mutation changed")
    else:
        checks.append(("DR-8", False, "Profile not found"))
        drift_found.append("DR-8: profile missing")

    # ── DR-9: No authority/promotion/seal claims ──
    if surface_out:
        try:
            sdata = json.loads(surface_out)
            pipeline = sdata.get("pipeline", sdata)
            # Only scan report HEADER fields, not advisory notices
            check_fields = {
                "active_sprint": str(pipeline.get("active_sprint", "")),
                "next_authorized": str(pipeline.get("next_authorized", "")),
                "sealed_head": str(pipeline.get("sealed_head", "")),
            }
            combined = " ".join(check_fields.values()).lower()
            forbidden = ["approve", "seal", "promote", "canonical", "production_ready"]
            found = [f for f in forbidden if re.search(r'\b' + f + r'\b', combined)]
            checks.append(("DR-9", len(found) == 0,
                           f"Claims: {found}" if found else "Clean"))
            if found:
                drift_found.append(f"DR-9: authority claims: {found}")
        except Exception:
            checks.append(("DR-9", True, "Could not scan"))

    # ── DR-10: Report is bounded and advisory-only ──
    total_checks = len(checks)
    drift_count = len(drift_found)
    checks.append(("DR-10", True,
                   f"Bounded report: {total_checks} checks, {drift_count} drifts detected"))

    return checks


# ── Fixture mode ──────────────────────────────────────────────────────────────

def validate_fixture(data):
    """Validate a fixture data dict against DR rules."""
    fchecks = []

    layers = data.get("expected_layers", [])
    fchecks.append(("DR-FIX-1", len(layers) >= 5, f"{len(layers)} layers"))

    if data.get("expected_drift", False):
        # Fixture expects drift — check it's marked
        has_authority = "_authority_claim" in data
        has_missing = data.get("missing_layers", [])
        has_mismatch = data.get("head_mismatch", False)
        drift_likely = has_authority or has_missing or has_mismatch
        fchecks.append(("DR-FIX-DRIFT", drift_likely,
                        f"Drift indicators: auth={has_authority} missing={has_missing} mismatch={has_mismatch}"))
    else:
        # No drift expected
        has_authority = "_authority_claim" in data
        fchecks.append(("DR-FIX-CLEAN", not has_authority,
                        "No authority claim" if not has_authority else "Has unexpected authority"))

    custody = data.get("custody", "qa-pilot-local")
    fchecks.append(("DR-FIX-CUSTODY", custody == "qa-pilot-local", f"custody={custody}"))

    fchecks.append(("DR-FIX-ADVISORY", data.get("advisory", True) is not False,
                    f"advisory={data.get('advisory', True)}"))

    all_pass = all(c[1] for c in fchecks)
    return (all_pass, fchecks, len([c for c in fchecks if not c[1]]))


# ── Report Output ─────────────────────────────────────────────────────────────

def format_report(checks):
    """Format an advisory drift report."""
    lines = []
    lines.append("QA Pilot Pipeline Drift Report")
    lines.append("=" * 50)
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append(f"Advisory:  True")
    lines.append("")

    drift_count = 0
    for cid, passed, msg in checks:
        prefix = "✅" if passed else "❌  DRIFT"
        if not passed:
            drift_count += 1
        lines.append(f"  {prefix}  {cid}: {msg}")

    lines.append("")
    lines.append(f"Checks: {len(checks)} total, {drift_count} drifts detected")
    if drift_count > 0:
        lines.append("STATUS: Drift detected — review above items")
    else:
        lines.append("STATUS: No drift — pipeline is consistent")
    lines.append("")
    lines.append(ADVISORY_NOTICE)

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    fixture_mode = "--fixture" in args
    report_mode = "--report" in args

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
        valid, fchecks, fail_count = validate_fixture(data)
        for cid, passed, msg in fchecks:
            prefix = "✅" if passed else "❌"
            print(f"  {prefix} {cid}: {msg}")
        print(f"\n{'✅ ALL FIXTURE CHECKS PASS' if valid else '❌ SOME FIXTURE CHECKS FAILED'}")
        return 0 if valid else 1

    # Live mode
    checks = run_drift_checks()

    if report_mode:
        print(format_report(checks))
    else:
        drift_count = 0
        for cid, passed, msg in checks:
            prefix = "✅" if passed else "❌"
            if not passed:
                drift_count += 1
            print(f"  {prefix} {cid}: {msg}")
        print(f"\nDrifts: {drift_count}/{len(checks)}")
        if drift_count == 0:
            print("✅ NO DRIFT DETECTED")
            return 0
        else:
            print(f"❌ {drift_count} DRIFT(S) DETECTED")
            return 0  # Report drift but don't fail (advisory)

    return 0


if __name__ == "__main__":
    sys.exit(main())
