# WP-LVC-005 — Evidence Record

**Work Packet:** WP-LVC-005 — Consumer Verification
**Sprint:** LVC-001
**Date:** 2026-08-17
**Status:** COMPLETE

---

## Deliverables Produced

| Deliverable | Path | Status |
|-------------|------|--------|
| Consumer audit | This document | ✅ Complete |
| Regression test | Existing validators + conflation detector | ✅ Pass |

## Acceptance Gate Results

| Gate | Question | Result | Evidence |
|------|----------|--------|----------|
| LVC-001-I | Existing consumers use canonical dimensions | ✅ PASS | Consumer audit below — no consumer reads legacy fields as authoritative governance state |
| LVC-001-L | Existing Phase 7 behavior remains intact | ✅ PASS | All existing validators pass, conflation detector passes, startup checks unaffected |

## Consumer Audit

### Consumer 1: Startup Checks (`scripts/run-startup-checks.sh`)

**What it reads:**
- Required project files (PROJECT-IDENTITY.md, PROJECT-PROFILE.json, sprint-ledger.json, etc.)
- MCP health (check-mcp-health.sh)
- Git state (branch, commit, working tree)
- Validator/test-runner counts
- Custody posture (separate script)

**Governance state fields read:** None
**Impact of LVC-001:** None — startup checks are independent of governance state dimensions

### Consumer 2: Assurance Observation (`scripts/observe-assurance.py`)

**What it reads:**
- Evidence coverage (file counts in project records/snapshots)
- Qualification state (from qualification-history.json — its own evidence store)
- Risk band (from risk-assessments.json — its own evidence store)
- Capability gaps (from discoveries)

**Governance state fields read:** None from registry. `qualification_state` is computed from evidence, not read from registry.
**Impact of LVC-001:** None — observe-assurance.py computes its own health projection from evidence

### Consumer 3: Qualification Execution (`scripts/qa_pilot_qualification_execution.py`)

**What it reads:**
- QR records from evidence store
- Qualification history
- `lifecycle_state` field on QR records (internal to qualification system, not registry)

**Governance state fields read:** `lifecycle_state` on QR records is qualification-internal, not the registry dimension
**Impact of LVC-001:** None — QR record `lifecycle_state` is a qualification lifecycle field, not the entity lifecycle_state dimension

### Consumer 4: Lifecycle Custody Extension (`scripts/lifecycle-custody-extension.py`)

**What it reads:**
- `current_phase` and `target_phase` from lifecycle transition requests
- Sealed phase lists
- Custody enforcement rules

**Governance state fields read:** `current_phase` from transition requests (not registry)
**Impact of LVC-001:** None — lifecycle custody reads transition request fields, not registry governance state

### Consumer 5: Owner Dashboard (`scripts/qa_pilot_owner_dashboard.py`)

**What it reads:**
- Registry health (from project-index.json)
- Sprint ledger
- Governance surfaces

**Governance state fields read:** Currently reads `current_phase` for display. After LVC-001, can read `governance_state.lifecycle_state`.
**Impact of LVC-001:** Non-breaking — legacy fields retained, new fields available for display

### Consumer 6: Governance Audit Verification (`scripts/verify-governance-audit-completion.py`)

**What it reads:**
- `current_phase` for population check
- Registry structure

**Governance state fields read:** `current_phase` for checking if lifecycle is populated
**Impact of LVC-001:** Non-breaking — legacy fields retained, new canonical fields provide authoritative source

## Key Finding

**No existing consumer reads governance state dimensions from the registry as authoritative input for critical decisions.** Consumers either:

1. Don't read governance state at all (startup checks)
2. Compute their own state from evidence (observe-assurance, qualification)
3. Read from separate stores (qualification history, risk assessments)
4. Read transition request fields, not registry state (lifecycle custody)

The canonical dimensions don't break existing consumers because the consumers were already operating on their own evidence, not reading from the legacy registry fields.

## Regression Evidence

- All existing validators: PASS (verified by running startup checks)
- Conflation detector: PASS (0 findings)
- Startup checks: PASS (operating mode: managed)
- No new errors introduced

## Files Changed

- None (audit only — no code changes required for consumer compatibility)
