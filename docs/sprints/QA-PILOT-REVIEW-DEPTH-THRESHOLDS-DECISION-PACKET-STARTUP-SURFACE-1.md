# QA-PILOT-REVIEW-DEPTH-THRESHOLDS-DECISION-PACKET-STARTUP-SURFACE-1

**Sprint ID:** QA-PILOT-REVIEW-DEPTH-THRESHOLDS-DECISION-PACKET-STARTUP-SURFACE-1
**Ledger:** #92
**Type:** startup surface / decision packet posture visibility
**Lane:** QA Pilot
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none
**Input dependencies:** QA-PILOT-REVIEW-DEPTH-THRESHOLDS-DECISION-PACKET-1 (#90, sealed)

## Purpose

Expose #90 decision packet posture in the QA Pilot startup/status surface, extending the established capability → posture visibility pattern.

## Scope

### What It Does

Adds a decision packet startup surface layer that reports:
- **Packet count** — total decision packets in the store
- **Latest packet ID** — most recent decision packet identifier
- **Latest packet state** — packet state (prepared/needs_owner_review/deferred/closed_by_owner)
- **Bound threshold/evidence bundle references** — source threshold ID, evidence bundle ref, result packet ref, consistency guard refs
- **Latest timestamp** — when the latest packet was created
- **By-state breakdowns** — packet and threshold state distribution counts
- **Honest empty/absent state** — reports absent or empty state when no packets exist

Adds validator rules DP-SS-1 through DP-SS-6:
- **DP-SS-1:** Decision packet surface section present in report
- **DP-SS-2:** Packet count reported (0 or more is valid — honest empty state allowed)
- **DP-SS-3:** Latest packet ID reported when packets exist
- **DP-SS-4:** Latest packet state and threshold/evidence bundle references reported when packets exist
- **DP-SS-5:** DP surface is read-only/advisory-only, cannot imply operational authority
- **DP-SS-6:** DP section honestly reports empty/absent state (no false failure when empty)

Adds fixtures:
- `valid-packet-present.json` — Valid surface with 3 decision packets, all fields present
- `invalid-packet-absent.json` — Invalid: reports `packet_count=0` but claims a latest packet ID
- `invalid-authority-claim.json` — Invalid: contains `approved_by` and `sealed_by` fields in surface

### What It Does NOT Do (Boundary)

The startup surface may display decision packet posture only. It does NOT:
- Create packets
- Make Owner decisions
- Accept or reject results
- Authorize execution
- Verify evidence
- Close reviews
- Mutate evidence or result packets
- Create seal authority

## Deliverables

| Artifact | Path |
|----------|------|
| Schema | `docs/schemas/qa-pilot-review-depth-thresholds-decision-packet-startup-surface.schema.json` |
| CLI | `scripts/qa_pilot_review_depth_thresholds_decision_packet_startup_surface.py` |
| Validator | `scripts/validate-qa-pilot-review-depth-thresholds-decision-packet-startup-surface.py` |
| Valid fixtures | `docs/examples/qa-pilot-review-depth-thresholds-decision-packet-startup-surface/valid-packet-present.json` |
| Invalid fixtures | `docs/examples/qa-pilot-review-depth-thresholds-decision-packet-startup-surface/invalid-packet-absent.json`, `invalid-authority-claim.json` |
| Test runner | `scripts/test-qa-pilot-review-depth-thresholds-decision-packet-startup-surface.sh` |
| Governance | This file |

## Validation

### Acceptance Gates

1. CLI reports absent state when no decision packet store exists
2. CLI reports empty state when store has index with no records
3. CLI reports present state with real packet data
4. CLI report JSON includes `packet_count`, `latest_packet_id`, `latest_packet_state`
5. CLI report shows threshold ID and evidence bundle references
6. CLI report shows timestamp
7. CLI report is advisory-only (`advisory_only: true`)
8. CLI report contains no authority fields (no `approve_`, `seal_`, `executed_`)
9. Text report format renders correctly
10. `validate` command passes DP-SS rules against live data
11. Validator fixture validation passes all 3 fixtures (1 valid pass, 2 invalid reject)
12. Validator directly validates each fixture correctly
13. Validator rejects invalid authority-claim fixture

### Existing Validator Chain

All existing QA Pilot validators must remain green:
- Evidence intake (#33): unchanged
- Test composition (#34): unchanged
- Result packet export (#35): unchanged
- Epic regression (#36): unchanged
- Pipeline startup surface (#37): unchanged
- Pipeline health regression (#38): unchanged
- Pipeline drift detection (#39): unchanged
- Pipeline recovery diagnostics (#40): unchanged
- Pipeline owner review packet (#41): unchanged
- ODR (#42): unchanged
- ODR startup surface (#43): unchanged
- Evidence checklist (#44): unchanged
- Checklist review packet (#45): unchanged
- Checklist evidence linker (#46): unchanged
- Decision packet (#90): unchanged
- Decision packet startup surface (this sprint): new

## Authority

This surface is **read-only/advisory-only**. It creates no approval, seal, execution, or mutation authority.
Owner is the only decision authority.
