#!/usr/bin/env python3
"""
enforce-project-wide-write-custody.py — Preflight Write-Custody Enforcement

Evaluates a proposed write against the sealed PROJECT-WIDE-WRITE-CUSTODY-1 policy
and returns an enforcement decision.

Output codes:
  ALLOW                              — Write is permitted
  BLOCK_WRITE_SCOPE_VIOLATION        — Outside sprint allowlist without authority
  REQUIRES_OWNER_APPROVAL            — Authority file needs Owner OK + warning
  FORBIDDEN_SEALED_EVIDENCE          — Sealed evidence immutable
  FORBIDDEN_POST_RELEASE_ROUTINE_EDIT — Post-release file needs patch order
  GENERATED_WRITE_ONLY               — Generated files need deterministic tool

Usage:
  # Evaluate from JSON input
  python3 enforce-project-wide-write-custody.py < request.json

  # Evaluate from CLI arguments  
  python3 enforce-project-wide-write-custody.py \
    --project qa-pilot --sprint SPRINT-1 \
    --path "docs/foo.md" --action "Add section" \
    --allowlisted \
    --release-state pre_release

Authority source: docs/governance/PROJECT-WIDE-WRITE-CUSTODY.md (sealed)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

# ── Custody class determination rules ──────────────────────────────────────

# Path patterns → custody class (longest prefix wins)
CUSTODY_CLASS_PATTERNS = [
    # SEALED_EVIDENCE_IMMUTABLE (check first — highest priority)
    # Only receipt files and sealed/sprint-closeout paths
    (["receipts/"], "SEALED_EVIDENCE_IMMUTABLE"),

    # OWNER_APPROVAL_REQUIRED — authority/infrastructure/governance files
    ([".librarian/", "SessionStartup/",
      "PROJECT-STARTUP.md", "startup-contract.json", "CLAUDE.md",
      "PROJECT-IDENTITY.md", "PROJECT-PROFILE.json",
      "FEATURE-STATUS.md", "SESSION-HANDOFF.md",
      "docs/governance/", "docs/schemas/", "docs/rules/",
      "project-state/"], "OWNER_APPROVAL_REQUIRED"),

    # GENERATED_WRITE_ALLOWED
    (["STARTUP-STATE.md", "project-state/sprint-ledger.json",
      "project-state/project-index.json"], "GENERATED_WRITE_ALLOWED"),

    # POST_RELEASE_PATCH_ONLY
    (["release/", "dist/", "build/", "artifacts/"], "POST_RELEASE_PATCH_ONLY"),

    # FORBIDDEN
    (["secrets/", ".env", "credentials"], "FORBIDDEN"),
]

DEFAULT_CUSTODY_CLASS = "READ_ONLY_BY_DEFAULT"

# ── Enforcement rules ──────────────────────────────────────────────────────

ENFORCEMENT_RULES = {
    "EC-1": "Default decision is block unless write authority is proven",
    "EC-2": "Sprint allowlist permits only exact path or explicit pattern matches",
    "EC-3": "Active project membership does not grant write authority",
    "EC-4": "Writes outside allowlist return WRITE_SCOPE_VIOLATION",
    "EC-5": "Authority-file writes require warning plus explicit Owner approval",
    "EC-6": "Owner approval must name file, path pattern, or custody class",
    "EC-7": "Broad approval for entire project root is invalid",
    "EC-8": "Sealed receipts are immutable",
    "EC-9": "Sealed sprint records are immutable",
    "EC-10": "Post-release routine edits are forbidden",
    "EC-11": "Post-release changes require patch/change-order authority",
    "EC-12": "Generated files may be written only by deterministic tools",
    "EC-13": "Opportunistic cleanup is blocked",
    "EC-14": "Unrelated formatting edits are blocked",
    "EC-15": "If custody class is unknown, block",
}


def classify_path(path: str, release_state: str = "pre_release") -> str:
    """Determine custody class for a file path."""
    # POST_RELEASE_PATCH_ONLY if released
    if release_state in ("released", "patch_only"):
        for patterns, cls in CUSTODY_CLASS_PATTERNS:
            if cls == "POST_RELEASE_PATCH_ONLY":
                for pattern in patterns:
                    if pattern in path:
                        return "POST_RELEASE_PATCH_ONLY"
        # Released files default to POST_RELEASE_PATCH_ONLY
        return "POST_RELEASE_PATCH_ONLY"

    # Check patterns in order
    for patterns, cls in CUSTODY_CLASS_PATTERNS:
        for pattern in patterns:
            if pattern in path:
                return cls

    return DEFAULT_CUSTODY_CLASS


def is_sprint_allowlisted(path: str, allowlist: list = None) -> bool:
    """Check if path matches any sprint allowlist entry (exact or pattern)."""
    if not allowlist:
        return False
    for entry in allowlist:
        # Exact match
        if entry == path:
            return True
        # Directory prefix wildcard
        if entry.endswith("/") and path.startswith(entry):
            return True
        # Glob-like suffix
        if entry.endswith("/*") and path.startswith(entry[:-1]):
            return True
        # Pattern in path (for partial paths like "docs/")
        if entry in path:
            return True
    return False


def is_authority_file(path: str) -> bool:
    """Check if path is an authority/ownership file."""
    authority_patterns = [
        ".librarian/", "startup-contract.json", "CLAUDE.md",
        "PROJECT-STARTUP.md", "PROJECT-IDENTITY.md", "PROJECT-PROFILE.json",
    ]
    for p in authority_patterns:
        if p in path:
            return True
    return False


def generate_warning(file_path: str, custody_class: str,
                     reason: str, risk: str) -> str:
    """Generate a WRITE AUTHORITY WARNING."""
    return (
        "WRITE AUTHORITY WARNING\n"
        "\n"
        f"Requested file:\n"
        f"{file_path}\n"
        "\n"
        f"Current custody class:\n"
        f"{custody_class}\n"
        "\n"
        f"Reason for requested write:\n"
        f"{reason}\n"
        "\n"
        f"Risk:\n"
        f"{risk}\n"
        "\n"
        "Required action:\n"
        "Explicit Owner approval naming this file/path/class.\n"
    )


def enforce(request: dict) -> dict:
    """
    Evaluate a write request against the custody policy.

    Returns dict with keys:
      decision: ALLOW | BLOCK_WRITE_SCOPE_VIOLATION | REQUIRES_OWNER_APPROVAL
               | FORBIDDEN_SEALED_EVIDENCE | FORBIDDEN_POST_RELEASE_ROUTINE_EDIT
               | GENERATED_WRITE_ONLY
      decision_rationale: explanation
      warning: WRITE AUTHORITY WARNING text if applicable
    """
    project_id = request.get("project_id", "unknown")
    sprint_id = request.get("sprint_id", "unknown")
    file_path = request.get("file_path", "")
    requested_action = request.get("requested_action", "write")
    release_state = request.get("release_state", "pre_release")
    sealed_evidence = request.get("sealed_evidence", False)
    generated_by_tool = request.get("generated_by_tool", False)
    tool_is_deterministic = request.get("tool_is_deterministic", False)
    owner_approval_present = request.get("owner_approval_present", False)
    owner_approval_is_broad = request.get("owner_approval_is_broad", False)
    sprint_allowlisted = request.get("sprint_allowlisted", False)
    write_authority_source = request.get("write_authority_source", "none")
    is_cleanup = request.get("is_cleanup", False)
    is_formatting = request.get("is_formatting", False)

    # Determine custody class (if not explicitly provided)
    custody_class = request.get("custody_class", "")
    if not custody_class:
        custody_class = classify_path(file_path, release_state)

    # Track which enforcement rule triggered
    triggered_rules = []
    warning_text = ""

    # EC-1: Default is block
    # EC-15: Unknown class → block
    if custody_class == "READ_ONLY_BY_DEFAULT" and not sprint_allowlisted:
        triggered_rules.append("EC-1")
        # EC-3: Project membership alone does not grant write authority
        if write_authority_source == "none" and not owner_approval_present:
            triggered_rules.append("EC-3")
            return {
                "decision": "BLOCK_WRITE_SCOPE_VIOLATION",
                "blocker_code": "WRITE_SCOPE_VIOLATION",
                "decision_rationale": (
                    f"Default class READ_ONLY_BY_DEFAULT for '{file_path}'. "
                    f"Active project membership does not grant write authority. "
                    f"Sprint allowlisting or Owner approval required."
                ),
                "triggered_rules": triggered_rules,
                "custody_class": custody_class,
                "warning": "",
            }

    # EC-15: Unknown custody class
    if not custody_class or custody_class not in (
        "READ_ONLY_BY_DEFAULT", "SPRINT_WRITE_ALLOWED",
        "OWNER_APPROVAL_REQUIRED", "GENERATED_WRITE_ALLOWED",
        "SEALED_EVIDENCE_IMMUTABLE", "POST_RELEASE_PATCH_ONLY",
        "FORBIDDEN"
    ):
        triggered_rules.append("EC-15")
        return {
            "decision": "BLOCK_WRITE_SCOPE_VIOLATION",
            "blocker_code": "WRITE_SCOPE_VIOLATION",
            "decision_rationale": f"Unknown custody class '{custody_class}' for '{file_path}'.",
            "triggered_rules": triggered_rules,
            "custody_class": custody_class,
            "warning": "",
        }

    # ── FORBIDDEN ──────────────────────────────────────────────────────────
    if custody_class == "FORBIDDEN":
        triggered_rules.append("EC-1")
        return {
            "decision": "FORBIDDEN_SEALED_EVIDENCE",
            "blocker_code": "FORBIDDEN_CLASS",
            "decision_rationale": f"FORBIDDEN class file '{file_path}' cannot be modified.",
            "triggered_rules": triggered_rules,
            "custody_class": custody_class,
            "warning": "",
        }

    # ── SEALED_EVIDENCE_IMMUTABLE ──────────────────────────────────────────
    if custody_class == "SEALED_EVIDENCE_IMMUTABLE" or sealed_evidence:
        triggered_rules.extend(["EC-8", "EC-9"])
        return {
            "decision": "FORBIDDEN_SEALED_EVIDENCE",
            "blocker_code": "SEALED_EVIDENCE_IMMUTABLE",
            "decision_rationale": (
                f"Sealed evidence '{file_path}' is immutable. "
                f"Corrections require a new receipt or superseding record."
            ),
            "triggered_rules": triggered_rules,
            "custody_class": "SEALED_EVIDENCE_IMMUTABLE",
            "warning": "",
        }

    # ── POST_RELEASE_PATCH_ONLY ────────────────────────────────────────────
    if custody_class == "POST_RELEASE_PATCH_ONLY":
        if write_authority_source not in ("patch_work_order", "recovery_protocol"):
            triggered_rules.append("EC-10")
            return {
                "decision": "FORBIDDEN_POST_RELEASE_ROUTINE_EDIT",
                "blocker_code": "POST_RELEASE_NO_PATCH_ORDER",
                "decision_rationale": (
                    f"Post-release file '{file_path}' requires patch_work_order "
                    f"or recovery_protocol authority."
                ),
                "triggered_rules": triggered_rules,
                "custody_class": custody_class,
                "warning": "",
            }
        triggered_rules.append("EC-11")
        return {
            "decision": "ALLOW",
            "blocker_code": "",
            "decision_rationale": f"Post-release patch authorized via {write_authority_source}.",
            "triggered_rules": triggered_rules,
            "custody_class": custody_class,
            "warning": "",
        }

    # ── GENERATED_WRITE_ALLOWED ────────────────────────────────────────────
    if custody_class == "GENERATED_WRITE_ALLOWED":
        if not generated_by_tool:
            triggered_rules.append("EC-12")
            return {
                "decision": "GENERATED_WRITE_ONLY",
                "blocker_code": "NON_DETERMINISTIC_TOOL",
                "decision_rationale": (
                    f"Generated state file '{file_path}' must be written by "
                    f"a deterministic tool, not hand-edited."
                ),
                "triggered_rules": triggered_rules,
                "custody_class": custody_class,
                "warning": "",
            }
        if not tool_is_deterministic:
            triggered_rules.append("EC-12")
            return {
                "decision": "GENERATED_WRITE_ONLY",
                "blocker_code": "NON_DETERMINISTIC_TOOL",
                "decision_rationale": (
                    f"Tool writing '{file_path}' must be deterministic."
                ),
                "triggered_rules": triggered_rules,
                "custody_class": custody_class,
                "warning": "",
            }
        triggered_rules.append("EC-12")
        return {
            "decision": "ALLOW",
            "blocker_code": "",
            "decision_rationale": f"Generated state write by deterministic tool.",
            "triggered_rules": triggered_rules,
            "custody_class": custody_class,
            "warning": "",
        }

    # ── OWNER_APPROVAL_REQUIRED ────────────────────────────────────────────
    if custody_class == "OWNER_APPROVAL_REQUIRED":
        triggered_rules.append("EC-5")
        warning_text = generate_warning(
            file_path, custody_class,
            requested_action,
            "Authority/configuration file — unintended changes may affect project governance."
        )

        # Check if Owner approval is present
        if not owner_approval_present:
            return {
                "decision": "REQUIRES_OWNER_APPROVAL",
                "blocker_code": "OWNER_APPROVAL_MISSING",
                "decision_rationale": (
                    f"OWNER_APPROVAL_REQUIRED file '{file_path}' requires "
                    f"explicit Owner approval plus warning."
                ),
                "triggered_rules": triggered_rules,
                "custody_class": custody_class,
                "warning": warning_text,
            }

        # Check for broad approval (EC-6, EC-7)
        if owner_approval_is_broad:
            triggered_rules.extend(["EC-6", "EC-7"])
            return {
                "decision": "BLOCK_WRITE_SCOPE_VIOLATION",
                "blocker_code": "BROAD_PROJECT_ROOT_APPROVAL",
                "decision_rationale": (
                    f"Owner approval for '{file_path}' is broad/general and does not "
                    f"name the specific file, path pattern, or custody class."
                ),
                "triggered_rules": triggered_rules,
                "custody_class": custody_class,
                "warning": warning_text,
            }

        triggered_rules.append("EC-6")
        return {
            "decision": "ALLOW",
            "blocker_code": "",
            "decision_rationale": (
                f"OWNER_APPROVAL_REQUIRED file '{file_path}': "
                f"warning emitted and explicit Owner approval present."
            ),
            "triggered_rules": triggered_rules,
            "custody_class": custody_class,
            "warning": warning_text,
        }

    # ── SPRINT_WRITE_ALLOWED ───────────────────────────────────────────────
    if custody_class == "SPRINT_WRITE_ALLOWED" or sprint_allowlisted:
        # EC-13: No opportunistic cleanup
        if is_cleanup:
            triggered_rules.append("EC-13")
            return {
                "decision": "BLOCK_WRITE_SCOPE_VIOLATION",
                "blocker_code": "OPPORTUNISTIC_CLEANUP",
                "decision_rationale": "Opportunistic cleanup is blocked — cleanup is a governed change.",
                "triggered_rules": triggered_rules,
                "custody_class": custody_class,
                "warning": "",
            }

        # EC-14: No unrelated formatting
        if is_formatting:
            triggered_rules.append("EC-14")
            return {
                "decision": "BLOCK_WRITE_SCOPE_VIOLATION",
                "blocker_code": "OPPORTUNISTIC_CLEANUP",
                "decision_rationale": "Unrelated formatting edits are blocked — must be in sprint scope.",
                "triggered_rules": triggered_rules,
                "custody_class": custody_class,
                "warning": "",
            }

        triggered_rules.append("EC-2")
        return {
            "decision": "ALLOW",
            "blocker_code": "",
            "decision_rationale": f"Sprint-allowlisted write to '{file_path}'.",
            "triggered_rules": triggered_rules,
            "custody_class": custody_class,
            "warning": "",
        }

    # ── READ_ONLY_BY_DEFAULT with sprint allowlist ─────────────────────────
    if sprint_allowlisted:
        triggered_rules.append("EC-2")
        return {
            "decision": "ALLOW",
            "blocker_code": "",
            "decision_rationale": f"Sprint-allowlisted write to '{file_path}'.",
            "triggered_rules": triggered_rules,
            "custody_class": "READ_ONLY_BY_DEFAULT",
            "warning": "",
        }

    # Default: block (EC-1)
    triggered_rules.append("EC-1")
    return {
        "decision": "BLOCK_WRITE_SCOPE_VIOLATION",
        "blocker_code": "WRITE_SCOPE_VIOLATION",
        "decision_rationale": (
            f"No write authority proven for '{file_path}'. "
            f"Custody class: {custody_class}. "
            f"Authority source: {write_authority_source}."
        ),
        "triggered_rules": triggered_rules,
        "custody_class": custody_class,
        "warning": "",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Preflight write-custody enforcement")

    # JSON input mode
    parser.add_argument("--input", "-i", type=str,
                        help="JSON input file (default: stdin)")

    # CLI input mode
    parser.add_argument("--project", type=str, default="unknown",
                        help="Project ID")
    parser.add_argument("--sprint", type=str, default="unknown",
                        help="Sprint ID")
    parser.add_argument("--path", type=str, default="",
                        help="File path to evaluate")
    parser.add_argument("--action", type=str, default="write",
                        help="Requested action description")
    parser.add_argument("--custody-class", type=str, default="",
                        help="Override custody class")
    parser.add_argument("--release-state", type=str, default="pre_release",
                        choices=["pre_release", "released", "patch_only", "archived"])
    parser.add_argument("--allowlisted", action="store_true",
                        help="File is sprint-allowlisted")
    parser.add_argument("--owner-approved", action="store_true",
                        help="Owner approval present")
    parser.add_argument("--owner-broad", action="store_true",
                        help="Owner approval is broad (invalid)")
    parser.add_argument("--sealed", action="store_true",
                        help="File is sealed evidence")
    parser.add_argument("--generated", action="store_true",
                        help="Write by deterministic tool")
    parser.add_argument("--tool-deterministic", action="store_true",
                        help="Tool is deterministic")
    parser.add_argument("--write-source", type=str, default="none",
                        choices=["sprint_allowlist", "owner_approval",
                                 "generated_by_tool", "patch_work_order",
                                 "recovery_protocol", "none"],
                        help="Write authority source")
    parser.add_argument("--cleanup", action="store_true",
                        help="This write is cleanup")
    parser.add_argument("--formatting", action="store_true",
                        help="This write is formatting-only")
    parser.add_argument("--reason", type=str, default="",
                        help="Reason for write")
    parser.add_argument("--list-rules", action="store_true",
                        help="List all enforcement rules")

    args = parser.parse_args()

    if args.list_rules:
        print("Project-Wide Write Custody Enforcement Rules:")
        print("=" * 50)
        for rule_id, desc in sorted(ENFORCEMENT_RULES.items()):
            print(f"  {rule_id}: {desc}")
        return 0

    # Build request from CLI args or JSON input
    # JSON input mode if --input is explicitly provided
    if args.input:
        try:
            with open(args.input) as f:
                request = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading input: {e}", file=sys.stderr)
            return 1
    # JSON from stdin pipe (not TTY) AND no explicit CLI path args
    elif not sys.stdin.isatty() and not args.path:
        try:
            request = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error parsing stdin JSON: {e}", file=sys.stderr)
            return 1
    else:
        request = {
            "project_id": args.project,
            "sprint_id": args.sprint,
            "file_path": args.path,
            "requested_action": args.action,
            "custody_class": args.custody_class,
            "release_state": args.release_state,
            "sealed_evidence": args.sealed,
            "generated_by_tool": args.generated,
            "tool_is_deterministic": args.tool_deterministic,
            "owner_approval_present": args.owner_approved,
            "owner_approval_is_broad": args.owner_broad,
            "sprint_allowlisted": args.allowlisted,
            "write_authority_source": args.write_source,
            "is_cleanup": args.cleanup,
            "is_formatting": args.formatting,
        }

    result = enforce(request)

    # Pretty-print output
    output = {
        "enforcement_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "request": {
            "project_id": request.get("project_id"),
            "file_path": request.get("file_path"),
            "requested_action": request.get("requested_action"),
        },
        "decision": result["decision"],
        "blocker_code": result["blocker_code"],
        "decision_rationale": result["decision_rationale"],
        "custody_class": result["custody_class"],
        "triggered_rules": result["triggered_rules"],
    }

    print(json.dumps(output, indent=2))

    if result.get("warning"):
        print()
        print(result["warning"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
