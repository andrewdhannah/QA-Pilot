# QA-PILOT-BROKER-AUDIT-STORE-HARDEN-1 — Broker Audit Store Hardening

**Type:** Hardening / negative coverage
**Mode:** QA Pilot-local broker audit store — path safety, status transitions, immutability, corruption handling, deterministic listing
**Predecessor:** QA-PILOT-BROKER-AUDIT-STORE-IMPLEMENTATION-1 (sealed #11)

---

## Summary

Hardened the QA Pilot-local broker audit store with stronger negative coverage, path safety, immutable field protection, status-transition validation, corruption handling, and deterministic listing.

## What Changed

### Store Module (`scripts/qa_pilot_broker_audit_store.py`)

| Feature | Change |
|---------|--------|
| Path safety | `is_safe_audit_id()` — rejects `/`, `\`, `..`, null bytes, dots, and paths that normalize outside `data/audit/broker/` |
| Schema enforcement | `register()` now blocks persistence on schema validation failure (was advisory-only) |
| Status model | `VALID_STATUSES`, `ALLOWED_TRANSITIONS`, `IMMUTABLE_FIELDS` constants |
| `update-status` | New command — validates transitions, protects immutable fields, returns structured result |
| Corruption handling | `get()` wraps JSON parse in try/except, returns `corruption_notice` on failure |
| Deterministic listing | `list_audits()` sorts by `stored_at` ascending (then audit_id as tiebreaker) |

### Status Transition Rules

```
registered -> running
registered -> failed
running -> completed
running -> failed
completed -> (terminal)
failed -> (terminal)
```

### Immutable Fields (after registration)

`audit_id`, `receipt_type`, `active_project_id`, `target_project_id`, `requested_tool`, `custody_record_id`, `handler_path`, `authority_level`, `advisory_only`, `output_effects`, `audit_timestamp`, `rollback_reference`, `validation_result`

### Validator (`scripts/validate-qa-pilot-broker-audit-store.py`)

| Rule | Coverage |
|------|----------|
| AS-13 | Path traversal audit ids rejected |
| AS-14 | Duplicate audit ids rejected |
| AS-15 | Invalid statuses rejected |
| AS-16 | Invalid status transitions rejected |
| AS-17 | Immutable fields protected |
| AS-18 | Corruption handling in get/list/status |
| AS-19 | Deterministic listing order |

### Test Runner (`scripts/test-qa-pilot-broker-audit-store.sh`)

44 tests total (was 29). 16 new hardening tests covering path traversal, duplicates, missing fields, bad timestamps, project ID mismatches, all status transitions, corruption handling, deterministic listing, and immutable field protection.

### Fixtures Added (16 total in `docs/examples/qa-pilot-broker-audit-store/`)

| Fixture | Type |
|---------|------|
| `invalid-path-traversal-audit-id.json` | Invalid — `../` in audit_id |
| `invalid-absolute-path-audit-id.json` | Invalid — `/` in audit_id |
| `invalid-duplicate-audit-id.json` | Invalid — duplicate audit_id |
| `invalid-missing-required-field.json` | Invalid — missing audit_id |
| `invalid-bad-status.json` | Invalid — wrong type for advisory_only |
| `invalid-bad-timestamp.json` | Invalid — malformed timestamp |
| `invalid-project-id-mismatch.json` | Invalid — wrong active_project_id |
| `invalid-status-transition-completed-to-running.json` | Invalid — terminal transition |
| `invalid-status-transition-failed-to-running.json` | Invalid — terminal transition |
| `invalid-mutates-immutable-field.json` | Invalid — immutable field mutation ref |
| `invalid-corrupted-store-record.json` | Invalid — corrupted JSON |
| `valid-status-transition-registered-to-running.json` | Valid transition |
| `valid-status-transition-running-to-completed.json` | Valid transition |
| `valid-status-transition-running-to-failed.json` | Valid transition |
| `valid-deterministic-listing-a.json` | Ordering test (older) |
| `valid-deterministic-listing-b.json` | Ordering test (newer) |

## Verification

### Audit Store Validator (19 rules)

```
✅ ALL CHECKS PASS
AS-1 through AS-19: all pass
```

### Audit Store Test Runner (44 tests)

```
44/44 passed. All tests pass.
```

### Regression: Broader QA Pilot Validators

| Validator | Result |
|-----------|--------|
| Broker plan validator | ✅ PASS |
| Implementation validator | ✅ PASS |
| Advisory surface validator | ✅ PASS |
| Audit receipt validator | ✅ PASS |
| Receipt validator | ✅ PASS |
| MCP surface validator | ✅ PASS |
| Receipt store validator | ✅ PASS |
| Handler validator | ✅ PASS |
| Custody validator | ✅ PASS |

### Startup Substrate (unchanged)

| Validator | Result |
|-----------|--------|
| Startup boundary validator | ✅ PASS |
| Contract fixture validator (12/12) | ✅ PASS |
| Registry selection (fixtures, 14/14 test + 1 helper) | ✅ PASS — 4/4 valid, 10/10 invalid; `fixture-contract-mismatch.json` correctly skipped as helper |
| QA Pilot startup checks | ✅ managed |

### Git Status

Working tree: dirty with intentional sprint files (new fixtures, modified store/validator/test runner, new sprint receipt).

## Files Changed

```
Modified:
  scripts/qa_pilot_broker_audit_store.py (path safety, schema enforcement, status model, update-status command, corruption handling, deterministic sort)
  scripts/validate-qa-pilot-broker-audit-store.py (AS-13 through AS-19 added)
  scripts/test-qa-pilot-broker-audit-store.sh (44 tests, 16 new)

Created:
  docs/examples/qa-pilot-broker-audit-store/invalid-path-traversal-audit-id.json
  docs/examples/qa-pilot-broker-audit-store/invalid-absolute-path-audit-id.json
  docs/examples/qa-pilot-broker-audit-store/invalid-duplicate-audit-id.json
  docs/examples/qa-pilot-broker-audit-store/invalid-missing-required-field.json
  docs/examples/qa-pilot-broker-audit-store/invalid-bad-status.json
  docs/examples/qa-pilot-broker-audit-store/invalid-bad-timestamp.json
  docs/examples/qa-pilot-broker-audit-store/invalid-project-id-mismatch.json
  docs/examples/qa-pilot-broker-audit-store/invalid-status-transition-completed-to-running.json
  docs/examples/qa-pilot-broker-audit-store/invalid-status-transition-failed-to-running.json
  docs/examples/qa-pilot-broker-audit-store/invalid-mutates-immutable-field.json
  docs/examples/qa-pilot-broker-audit-store/invalid-corrupted-store-record.json
  docs/examples/qa-pilot-broker-audit-store/valid-status-transition-registered-to-running.json
  docs/examples/qa-pilot-broker-audit-store/valid-status-transition-running-to-completed.json
  docs/examples/qa-pilot-broker-audit-store/valid-status-transition-running-to-failed.json
  docs/examples/qa-pilot-broker-audit-store/valid-deterministic-listing-a.json
  docs/examples/qa-pilot-broker-audit-store/valid-deterministic-listing-b.json
  active/qa-pilot/docs/sprints/QA-PILOT-BROKER-AUDIT-STORE-HARDEN-1.md

Not modified:
  SessionStartup/ (unchanged)
  docs/startup/ (unchanged)
  .librarian/current-project.json (unchanged)
  active/librarian/ (unchanged)
  startup-contract.json (unchanged)
  project-index.json (unchanged)
```

## Acceptance Gates

| Gate | Status |
|------|--------|
| Path traversal audit ids rejected | ✅ |
| Absolute-path audit ids rejected | ✅ |
| Duplicate audit ids rejected | ✅ |
| Missing required fields rejected | ✅ |
| Invalid statuses rejected | ✅ |
| Invalid status transitions rejected | ✅ |
| Immutable fields protected | ✅ |
| Corrupted stored records don't produce false success | ✅ |
| Listing order deterministic | ✅ |
| Existing valid broker audit store behavior intact | ✅ |
| QA Pilot startup checks still pass | ✅ |
| No Librarian files changed | ✅ |
| No startup substrate files changed | ✅ |
| No MCP tools added | ✅ |
| No runtime integration | ✅ |
