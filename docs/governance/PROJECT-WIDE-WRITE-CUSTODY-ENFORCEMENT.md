# PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT.md — Preflight Enforcement

**Status:** 🔍 Pending (not sealed)
**Authority:** Enforcement governance. Implements preflight checks for PROJECT-WIDE-WRITE-CUSTODY-1 (sealed).
**Sprint:** PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT-1

---

## 1. Purpose

Implement live or preflight write-custody enforcement so agents cannot modify project files outside the active sprint write allowlist without triggering a governed block, warning, or explicit Owner approval requirement.

**Core invariant:**
> No file is writable merely because it is inside the active project.

**Post-release invariant:**
> After release, every modification is a governed change, not routine agent work.

## 2. Enforcement Architecture

The enforcement layer operates as a **preflight validator** — it evaluates a proposed write and returns an enforcement decision before the write is performed.

### Input

A write request containing:
```
project_id, sprint_id, file_path, requested_action, custody_class,
sprint_allowlisted, owner_approval_present, owner_approval_is_broad,
generated_by_tool, tool_is_deterministic, sealed_evidence,
release_state, write_authority_source, is_cleanup, is_formatting
```

Input may be provided via:
- **JSON file** (--input <file>)
- **stdin pipe** (echo '{"file_path":"...",...}' | python3 enforce-...)
- **CLI arguments** (--path, --allowlisted, --owner-approved, etc.)

### Output

```json
{
  "decision": "ALLOW | BLOCK_WRITE_SCOPE_VIOLATION | ...",
  "blocker_code": "...",
  "decision_rationale": "...",
  "custody_class": "...",
  "triggered_rules": ["EC-1", "EC-2", ...],
  "warning": "WRITE AUTHORITY WARNING\\n..."
}
```

### Decisions

| Decision | Meaning |
|----------|---------|
| ALLOW | Write is permitted |
| BLOCK_WRITE_SCOPE_VIOLATION | Outside sprint allowlist without authority |
| REQUIRES_OWNER_APPROVAL | Authority file needs Owner OK + warning |
| FORBIDDEN_SEALED_EVIDENCE | Sealed evidence is immutable |
| FORBIDDEN_POST_RELEASE_ROUTINE_EDIT | Post-release file needs patch order |
| GENERATED_WRITE_ONLY | Generated files need deterministic tool |

## 3. Enforcement Rules

| Rule | Description |
|------|-------------|
| EC-1 | Default decision is block unless write authority is proven |
| EC-2 | Sprint allowlist permits only exact path or explicit pattern matches |
| EC-3 | Active project membership does not grant write authority |
| EC-4 | Writes outside allowlist return WRITE_SCOPE_VIOLATION |
| EC-5 | Authority-file writes require warning plus explicit Owner approval |
| EC-6 | Owner approval must name file, path pattern, or custody class |
| EC-7 | Broad approval for entire project root is invalid |
| EC-8 | Sealed receipts are immutable |
| EC-9 | Sealed sprint records are immutable |
| EC-10 | Post-release routine edits are forbidden |
| EC-11 | Post-release changes require patch/change-order authority |
| EC-12 | Generated files may be written only by deterministic tools |
| EC-13 | Opportunistic cleanup is blocked |
| EC-14 | Unrelated formatting edits are blocked |
| EC-15 | If custody class is unknown, block |

## 4. Custody Class Classification

The enforcement script classifies file paths into custody classes using path pattern matching:

| Class | Example Paths |
|-------|--------------|
| SEALED_EVIDENCE_IMMUTABLE | `receipts/` |
| OWNER_APPROVAL_REQUIRED | `.librarian/`, `SessionStartup/`, `PROJECT-STARTUP.md`, `startup-contract.json`, `CLAUDE.md`, `PROJECT-IDENTITY.md`, `PROJECT-PROFILE.json`, `FEATURE-STATUS.md`, `SESSION-HANDOFF.md`, `docs/governance/`, `docs/schemas/`, `docs/rules/`, `project-state/` |
| GENERATED_WRITE_ALLOWED | `STARTUP-STATE.md`, `project-state/sprint-ledger.json`, `project-state/project-index.json` |
| POST_RELEASE_PATCH_ONLY | `release/`, `dist/`, `build/`, `artifacts/` (and all released-state files) |
| FORBIDDEN | `secrets/`, `.env`, credentials files |
| READ_ONLY_BY_DEFAULT | Everything else |

## 5. Warning Format

Before blocking an authority-file write, the enforcement layer emits:

```
WRITE AUTHORITY WARNING

Requested file:
<path>

Current custody class:
<custody_class>

Reason for requested write:
<reason>

Risk:
<risk summary>

Required action:
Explicit Owner approval naming this file/path/class.
```

## 6. Relationship to Sealed Policy

This enforcement layer implements the governance rules from `PROJECT-WIDE-WRITE-CUSTODY.md` (sealed at Librarian ledger #339). It does **not** modify or override the sealed policy — it provides the preflight enforcement that the policy called for.

## 7. Non-Goals

- No irreversible live hooks
- No runtime MCP registration
- No filesystem interceptors
- No cross-project enforcement (single workspace)
- No performance optimization

## 8. Boundary Invariants

1. Enforcement script must not modify any files — it is a read-only validator
2. All decisions must be deterministic (same inputs → same output)
3. Default decision is always block unless authority is proven
4. Sealed evidence immutability is absolute — no override path
5. Broad Owner approval is never valid write authority
