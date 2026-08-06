# LIVE-CUSTODY-INTEGRATION.md — Live Write-Custody Integration

**Status:** 🔍 Pending (not sealed)
**Authority:** Integration governance. Wraps PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT-1 (sealed #23) into a live write path.
**Sprint:** LIVE-CUSTODY-INTEGRATION-1

---

## 1. Purpose

Integrate the sealed PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT-1 contract into QA Pilot's live write path so that project-wide write custody is enforced before any mutation.

**Core invariant:**
> Every live write attempt must pass through project-wide write custody before mutation.

## 2. Architecture

The live custody integration wraps the enforcement engine with write execution logic:

```
Write Request → LIVE-CUSTODY-INTEGRATION → enforce-project-wide-write-custody
                                                  ↓
                                          [Enforcement Decision]
                                                  ↓
                       ┌──────────────────────────┼──────────────────────────┐
                       ↓                          ↓                          ↓
                    ALLOW                    BLOCK_*                   REQUIRES_OWNER...
                       ↓                          ↓                          ↓
                 Execute write           Deny write, produce         Check approval;
                 Produce receipt         denial receipt              if missing → deny
                                                                     if present → allow
```

### Modes

| Mode | Behavior |
|------|----------|
| `live` | Evaluate custody; write file if ALLOWed; produce audit receipt |
| `dry-run` | Evaluate custody; return decision without writing; produce advisory receipt |

### Input

Via CLI arguments, JSON file, or stdin:
- `file_path` — relative path within project
- `content` — file content to write
- `project_id`, `sprint_id` — identity context
- `sprint_allowlisted`, `owner_approval_present`, etc. — custody parameters
- `owner_approval_ref` — reference to approval decision for provenance

### Output

```json
{
  "mode": "live|dry-run",
  "receipt_id": "ci-<mode>-<timestamp>",
  "decision": "ALLOW|BLOCK_WRITE_SCOPE_VIOLATION|...",
  "write_executed": true|false,
  "write_error": "...",
  "warning": "WRITE AUTHORITY WARNING\n...",
  "audit_receipt": { ... }
}
```

## 3. Acceptance Gates

| # | Gate | Mechanism | Status |
|---|------|-----------|--------|
| AG-1 | Live write invokes custody before mutation | `live-custody-integration.py` wraps enforcement + write | ✅ |
| AG-2 | WRITE_SCOPE_VIOLATION blocks mutation | Enforcement returns BLOCK; integration does not write | ✅ |
| AG-3 | Authority file emits warning + requires Owner approval | Ownership warning generated; write blocked without approval | ✅ |
| AG-4 | Sealed evidence immutable in live path | FORBIDDEN_SEALED_EVIDENCE returned | ✅ |
| AG-5 | Post-release requires patch order | FORBIDDEN_POST_RELEASE_ROUTINE_EDIT returned | ✅ |
| AG-6 | Generated state deterministic-tool-only | GENERATED_WRITE_ONLY returned unless tool is deterministic | ✅ |
| AG-7 | Broad project-root approval rejected | BROAD_PROJECT_ROOT_APPROVAL returned | ✅ |
| AG-8 | Dry-run produces decision without writing | Decision returned; write_executed=false | ✅ |
| AG-9 | Denied writes produce evidence receipts | Audit receipt persisted to `data/custody-audit/` | ✅ |
| AG-10 | Approved writes preserve approval provenance | `owner_approval_ref` stored in audit receipt | ✅ |
| AG-11 | Existing #23 enforcement fixtures still pass | Test runner validates 16/16 | ✅ |
| AG-12 | Startup regression remains green | Validated in full sweep | ✅ |
| AG-13 | Parity matrix remains green | Validated in full sweep | ✅ |
| AG-14 | No unrelated files modified | Verified by test runner scope | ✅ |
| AG-15 | No Librarian files modified | No Librarian paths touched | ✅ |

## 4. Audit Trail

All write attempts (allowed and denied) produce audit receipts stored at:

```
data/custody-audit/<receipt_id>.json
```

Each receipt contains:
- `receipt_id` — unique identifier
- `mode` — live or dry-run
- `request` — file_path, content_hash
- `enforcement` — decision, blocker_code, rationale, custody_class, triggered_rules
- `result` — write_executed, warning_emitted, owner_approval_ref

## 5. Non-Goals

- No lifecycle phase rules
- No Librarian mutation
- No cross-project write authority
- No auto-seal, auto-approval, or auto-execution
- No relaxation of PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT-1 rules

## 6. Boundary Invariants

1. Every write passes through enforcement before mutation
2. Dry-run never writes files — always returns decision only
3. All denied writes produce audit receipts
4. Approved writes record approval provenance
5. No file outside `active/qa-pilot/` is written
6. The #23 enforcement contract is not weakened or bypassed
