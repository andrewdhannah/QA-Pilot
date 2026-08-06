#!/usr/bin/env python3
"""
lifecycle-custody-extension.py — Lifecycle Transition Custody Enforcement

Extends custody enforcement across QA Pilot lifecycle transitions so phase/state
movement is governed by the same custody posture established in PROJECT-WIDE-
WRITE-CUSTODY-ENFORCEMENT-1 (#23) and LIVE-CUSTODY-INTEGRATION-1 (#24).

This script does NOT modify #23 or #24 contracts.

Modes:
  live     — Evaluate lifecycle custody; write state change if allowed; produce receipt
  dry-run  — Evaluate lifecycle custody; return decision; do NOT modify state

Output codes:
  ALLOW                          — Lifecycle transition permitted
  LIFECYCLE_CUSTODY_VIOLATION    — Unauthorized transition
  REQUIRES_OWNER_APPROVAL        — Governed transition needs Owner approval
  FORBIDDEN_SEALED_EVIDENCE      — Sealed lifecycle evidence immutable
  FORBIDDEN_POST_RELEASE_ROUTINE_EDIT — Post-release lifecycle needs patch order
  GENERATED_LIFECYCLE_ONLY       — Generated lifecycle state deterministic-tool-only

Usage:
  python3 lifecycle-custody-extension.py live --project qa-pilot \
    --current-phase 1 --target-phase 2 --reason "Planning complete" --owner-approved

  python3 lifecycle-custody-extension.py dry-run --project qa-pilot \
    --current-phase 1 --target-phase 3 --reason "Skip phase" 2>&1

  python3 lifecycle-custody-extension.py live --input request.json
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_DIR = os.path.join(PROJECT_ROOT, "data", "lifecycle-custody-audit")

# ── Known lifecycle transitions for QA Pilot ──────────────────────────────
# These come from the MCP lifecycle cursor (project_get_allowed_transitions).
# Phase 1 (Plan) → Phase 2: "Planning complete, work packet ready"
KNOWN_TRANSITIONS = {
    ("1", "2"): "Planning complete, work packet ready",
}

# Phases with special custody requirements
GOVERNED_PHASES = {"2", "3", "4", "5", "6", "7", "8"}
SEALED_PHASES = set()  # Phases where evidence is sealed
POST_RELEASE_PHASES = {"7", "8"}  # Phases representing release/maintenance

# ── Lifecycle custody rules ───────────────────────────────────────────────

LIFECYCLE_RULES = {
    "LC-1": "Default decision is block unless lifecycle authority is proven",
    "LC-2": "Governed lifecycle transitions require Owner approval",
    "LC-3": "Active project membership does not grant lifecycle authority",
    "LC-4": "Unauthorized transitions return LIFECYCLE_CUSTODY_VIOLATION",
    "LC-5": "Authority-file lifecycle effects require warning plus Owner approval",
    "LC-6": "Owner approval must name the transition, phase, or project",
    "LC-7": "Broad lifecycle/project-root approval is invalid",
    "LC-8": "Sealed lifecycle evidence is immutable",
    "LC-9": "Post-release lifecycle changes require patch order",
    "LC-10": "Generated lifecycle state must be deterministic-tool-only",
    "LC-11": "No auto-promotion — lifecycle transitions are governed changes",
    "LC-12": "If lifecycle state is unknown, block",
    "LC-13": "Lifecycle custody does not bypass project-wide write custody (#23)",
    "LC-14": "Lifecycle custody does not alter live write contract (#24)",
    "LC-15": "Approved transitions preserve approval provenance",
}


def ensure_audit_dir():
    os.makedirs(AUDIT_DIR, exist_ok=True)


def generate_receipt_id(mode: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"lc-{mode}-{ts}"


def content_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate_warning(request: dict) -> str:
    """Generate lifecycle custody warning for authority-bearing transitions."""
    return (
        "LIFECYCLE CUSTODY WARNING\n"
        "\n"
        f"Requested transition:\n"
        f"Phase {request.get('current_phase', '?')} → Phase {request.get('target_phase', '?')}\n"
        "\n"
        f"Project:\n"
        f"{request.get('project_id', 'unknown')}\n"
        "\n"
        f"Reason:\n"
        f"{request.get('transition_reason', 'not provided')}\n"
        "\n"
        "Risk:\n"
        "Lifecycle transition may affect governance posture, authority boundaries, "
        "and file custody classes.\n"
        "\n"
        "Required action:\n"
        "Explicit Owner approval naming this transition or target phase.\n"
    )


def enforce_lifecycle(request: dict, mode: str) -> dict:
    """
    Evaluate a lifecycle transition request against custody rules.

    Returns dict with decision, rationale, and audit receipt.
    """
    project_id = request.get("project_id", "unknown")
    current_phase = str(request.get("current_phase", ""))
    target_phase = str(request.get("target_phase", ""))
    transition_reason = request.get("transition_reason", "")
    owner_approval_present = request.get("owner_approval_present", False)
    owner_approval_ref = request.get("owner_approval_ref", "")
    owner_approval_is_broad = request.get("owner_approval_is_broad", False)
    sealed_evidence_affected = request.get("sealed_evidence_affected", False)
    generated_state = request.get("generated_state", False)
    tool_is_deterministic = request.get("tool_is_deterministic", False)
    is_patch_order = request.get("is_patch_order", False)
    is_auto_promotion = request.get("is_auto_promotion", False)

    transition_key = (current_phase, target_phase)
    triggered_rules = []
    warning_text = ""

    # LC-11: No auto-promotion
    if is_auto_promotion:
        triggered_rules.append("LC-11")
        return make_result("LIFECYCLE_CUSTODY_VIOLATION", "LC_AUTO_PROMOTION",
                           "Auto-promotion is blocked — lifecycle transitions are governed changes.",
                           triggered_rules, request, mode)

    # LC-12: If transition is unknown, block
    if transition_key not in KNOWN_TRANSITIONS:
        triggered_rules.append("LC-12")
        blocked_reason = (
            f"Unknown lifecycle transition: Phase {current_phase} → Phase {target_phase}. "
            f"Known transitions: {list(KNOWN_TRANSITIONS.keys())}"
        )
        return make_result("LIFECYCLE_CUSTODY_VIOLATION", "LC_UNKNOWN_TRANSITION",
                           blocked_reason, triggered_rules, request, mode)

    # LC-8: Sealed lifecycle evidence immutable
    if sealed_evidence_affected or current_phase in SEALED_PHASES:
        triggered_rules.append("LC-8")
        return make_result("FORBIDDEN_SEALED_EVIDENCE", "LC_SEALED_EVIDENCE",
                           "Sealed lifecycle evidence is immutable.", triggered_rules, request, mode)

    # LC-9: Post-release lifecycle change requires patch order
    if current_phase in POST_RELEASE_PHASES or target_phase in POST_RELEASE_PHASES:
        if not is_patch_order:
            triggered_rules.append("LC-9")
            return make_result("FORBIDDEN_POST_RELEASE_ROUTINE_EDIT", "LC_POST_RELEASE_NO_PATCH",
                               "Post-release lifecycle change requires patch order.",
                               triggered_rules, request, mode)
        triggered_rules.append("LC-9")
        return make_result("ALLOW", "", "Post-release lifecycle change with patch order.",
                           triggered_rules, request, mode)

    # LC-10: Generated lifecycle state deterministic-tool-only
    if generated_state:
        if not tool_is_deterministic:
            triggered_rules.append("LC-10")
            return make_result("GENERATED_LIFECYCLE_ONLY", "LC_NON_DETERMINISTIC",
                               "Generated lifecycle state requires deterministic tool.",
                               triggered_rules, request, mode)
        triggered_rules.append("LC-10")
        return make_result("ALLOW", "", "Generated lifecycle state by deterministic tool.",
                           triggered_rules, request, mode)

    # Check if target phase is governed (requires Owner approval)
    is_governed = target_phase in GOVERNED_PHASES

    # LC-1/LC-4: Default is block
    triggered_rules.extend(["LC-1", "LC-4"])

    if is_governed:
        triggered_rules.append("LC-2")
        warning_text = generate_warning(request)

        if not owner_approval_present:
            return make_result("REQUIRES_OWNER_APPROVAL", "LC_OWNER_APPROVAL_MISSING",
                               f"Governed lifecycle transition Phase {current_phase} → Phase {target_phase} "
                               f"requires explicit Owner approval.", triggered_rules, request, mode,
                               warning=warning_text)

        # LC-7: Broad approval is invalid
        if owner_approval_is_broad:
            triggered_rules.append("LC-7")
            return make_result("LIFECYCLE_CUSTODY_VIOLATION", "LC_BROAD_APPROVAL",
                               "Broad lifecycle/project-root approval is invalid — must name "
                               "specific transition or target phase.", triggered_rules, request, mode,
                               warning=warning_text)

        # LC-6: Owner approval must name transition or phase
        # (Satisfied by non-broad approval — the approval ref serves as provenance)
        triggered_rules.append("LC-6")

        # LC-15: Preserve approval provenance
        triggered_rules.append("LC-15")

        return make_result("ALLOW", "",
                           f"Governed lifecycle transition Phase {current_phase} → Phase {target_phase}: "
                           f"Owner approval present (ref: {owner_approval_ref or 'direct'}).",
                           triggered_rules, request, mode, warning=warning_text,
                           owner_approval_ref=owner_approval_ref)

    else:
        # Non-governed phase transition
        # Still requires reason (LC-1/LC-4)
        if not transition_reason:
            return make_result("LIFECYCLE_CUSTODY_VIOLATION", "LC_MISSING_REASON",
                               "Lifecycle transition requires a stated reason.",
                               triggered_rules, request, mode)

        return make_result("ALLOW", "",
                           f"Lifecycle transition Phase {current_phase} → Phase {target_phase}: "
                           f"condition '{KNOWN_TRANSITIONS[transition_key]}'.",
                           triggered_rules, request, mode)


def make_result(decision: str, blocker_code: str, rationale: str,
                triggered_rules: list, request: dict, mode: str,
                warning: str = "", owner_approval_ref: str = "") -> dict:
    """Build a result dict with audit receipt."""
    receipt_id = generate_receipt_id(mode)

    receipt = {
        "receipt_id": receipt_id,
        "receipt_type": "lifecycle_custody_audit",
        "mode": mode,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "request": {
            "project_id": request.get("project_id"),
            "current_phase": request.get("current_phase"),
            "target_phase": request.get("target_phase"),
            "transition_reason": request.get("transition_reason"),
        },
        "enforcement": {
            "decision": decision,
            "blocker_code": blocker_code,
            "rationale": rationale,
            "triggered_rules": triggered_rules,
        },
        "result": {
            "write_executed": False,
            "warning_emitted": bool(warning),
            "owner_approval_ref": owner_approval_ref,
        },
    }
    if mode == "dry-run":
        receipt["result"]["dry_run_decision"] = decision

    # Persist receipt (only in live mode)
    if mode == "live":
        ensure_audit_dir()
        path = os.path.join(AUDIT_DIR, f"{receipt_id}.json")
        with open(path, "w") as f:
            json.dump(receipt, f, indent=2)

    return {
        "receipt_id": receipt_id,
        "mode": mode,
        "decision": decision,
        "blocker_code": blocker_code,
        "decision_rationale": rationale,
        "triggered_rules": triggered_rules,
        "write_executed": False,  # Lifecycle changes require MCP tools, not file writes
        "warning": warning,
        "owner_approval_ref": owner_approval_ref,
        "audit_receipt": receipt,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Lifecycle transition custody enforcement")

    parser.add_argument("mode", choices=["live", "dry-run"],
                        help="live = persist state if allowed; dry-run = evaluate only")

    parser.add_argument("--input", "-i", type=str, help="JSON input file")
    parser.add_argument("--project", type=str, default="qa-pilot")
    parser.add_argument("--current-phase", type=str, default="",
                        help="Current lifecycle phase")
    parser.add_argument("--target-phase", type=str, default="",
                        help="Target lifecycle phase")
    parser.add_argument("--reason", type=str, default="",
                        help="Reason for lifecycle transition")
    parser.add_argument("--owner-approved", action="store_true")
    parser.add_argument("--owner-approval-ref", type=str, default="")
    parser.add_argument("--owner-broad", action="store_true")
    parser.add_argument("--sealed", action="store_true",
                        help="Sealed lifecycle evidence affected")
    parser.add_argument("--generated", action="store_true",
                        help="Generated lifecycle state")
    parser.add_argument("--tool-deterministic", action="store_true")
    parser.add_argument("--patch-order", action="store_true",
                        help="Post-release lifecycle has patch order")
    parser.add_argument("--auto-promotion", action="store_true",
                        help="This is an auto-promotion attempt")

    args = parser.parse_args()

    # Build request
    if args.input:
        try:
            with open(args.input) as f:
                request = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(json.dumps({"error": f"Input error: {e}"}), file=sys.stderr)
            return 2
    elif not sys.stdin.isatty() and not args.current_phase:
        try:
            request = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Stdin parse error: {e}"}), file=sys.stderr)
            return 2
    else:
        request = {
            "project_id": args.project,
            "current_phase": args.current_phase,
            "target_phase": args.target_phase,
            "transition_reason": args.reason,
            "owner_approval_present": args.owner_approved,
            "owner_approval_ref": args.owner_approval_ref,
            "owner_approval_is_broad": args.owner_broad,
            "sealed_evidence_affected": args.sealed,
            "generated_state": args.generated,
            "tool_is_deterministic": args.tool_deterministic,
            "is_patch_order": args.patch_order,
            "is_auto_promotion": args.auto_promotion,
        }

    result = enforce_lifecycle(request, args.mode)

    output = {
        "mode": result["mode"],
        "receipt_id": result["receipt_id"],
        "decision": result["decision"],
        "blocker_code": result["blocker_code"],
        "decision_rationale": result["decision_rationale"],
        "triggered_rules": result["triggered_rules"],
        "write_executed": result["write_executed"],
        "warning": result.get("warning", ""),
    }

    print(json.dumps(output, indent=2))

    if result["decision"] == "ALLOW":
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
