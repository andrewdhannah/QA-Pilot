# QA-PILOT-BROKER-AUDIT-STORE-HARDEN-1 — Progress Report

## Status: In progress — 3 test failures being resolved

### What's done

- **Store module:** Path safety (`is_safe_audit_id`), status transitions (`update_status` with `ALLOWED_TRANSITIONS`), immutable field protection (`IMMUTABLE_FIELDS` list), deterministic listing (sort by stored_at), corruption handling (try/except in get)
- **Validator:** AS-13 through AS-19 added (19/19 checks pass)
- **Fixtures:** 16 new fixtures written to `docs/examples/qa-pilot-broker-audit-store/`

### Test runner: 41/45 pass — 3 failures to fix

| # | Test | Issue | Root cause |
|---|------|-------|------------|
| 34 | Invalid status rejected | Fixture has `status` field — not in schema | Schema doesn't constrain the `status` property; fixture needs different approach |
| 35 | Bad timestamp rejected | Fixture passes schema but store continues | **Bug: register() records schema failure but doesn't block registration** — only advisory enforcement errors prevent persistence |
| 36 | Project ID mismatch rejected | Same as above | Same bug: schema failure recorded but not enforced |

### Fix plan

1. **Fix register() schema enforcement:** Schema validation failures must add errors that block persistence, just like advisory enforcement failures do
2. **Fix bad-status fixture:** Change to test what the schema actually constrains (empty strings, wrong types, etc.) or test via `update-status` command
3. **Re-run full suite** after fixes

### What works (41 tests)

Path traversal, absolute path, duplicate, missing required fields, all valid transitions, all invalid transitions, immutable field protection, corruption handling in get, deterministic listing, all 19 AS validator rules, all 9 regression validators.
