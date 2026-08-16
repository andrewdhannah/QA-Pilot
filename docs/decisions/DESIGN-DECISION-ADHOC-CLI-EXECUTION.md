# Design Decision: Ad-Hoc CLI Execution Path

**Decision:** Option 1 — `librarian execute` without a Work Packet auto-generates a minimal one.
**Date:** 2026-08-16
**Status:** Closed
**Source:** Claude/GPT chat synthesis, Owner review

---

## Context

The governed CLI requires a Work Packet: `librarian execute WP-482`. This closes the "skip project shaping" hole. But a power user may want to run something in 30 seconds without opening a planning room.

## Options

**Option 1:** `librarian execute` with no WP auto-generates a minimal Work Packet behind the scenes (global default budget, no scope-specific planning). There is still a governed artifact and an evidence trail — just a thin one.

**Option 2:** No ungoverned path, full stop. The CLI's job is to make creating a minimal WP fast enough that this isn't friction.

## Decision

Option 1. Every execution has a Work Packet — absolute invariant. A thin WP is still governed: it has an authority envelope, constraints, provenance.

## Rationale

- "Every execution has a Work Packet" is a cleaner invariant than "every execution usually has one"
- A thin WP is still governed: authority envelope, constraints, provenance all present
- Provenance marks it `auto_generated: true` so the owner can distinguish LINK-planned from ad-hoc
- Token budget for auto-generated WPs falls back to the CostEstimate's p80 (informed by historical data, not arbitrary)
- This is the `git commit -m "quick fix"` pattern: the governed path is preferred, but the system doesn't block you — it just makes the governance visible

## Auto-Generated Work Packet Structure

```json
{
  "packet_id": "WP-AUTO-<timestamp>",
  "queue_item_ref": "adhoc-cli",
  "status": "authorized",
  "failure_context": null,
  "constraints": {
    "must_not_modify": [],
    "required_validation": [],
    "token_budget": {
      "planned": "<p80 from CostEstimate>",
      "tolerance": 1.25,
      "checkpoint_at_pct": 90,
      "action_on_exceed": { "type": "checkpoint" },
      "estimate_ref": "<CostEstimate observation_id>"
    }
  },
  "verification_required": [],
  "authority": {
    "authorized_by": "cli-auto-generate",
    "authorized_at": "<timestamp>",
    "scope": "adhoc-execution"
  },
  "provenance": {
    "advisory": true,
    "no_authority_conferred": true,
    "generated_from": "cli-adhoc",
    "auto_generated": true,
    "authority_granted_by": "cli-defaults"
  }
}
```

## Consequence

The intelligence is not in the command. The intelligence is in the governed context behind the command. `librarian execute "build auth"` is syntactic sugar for "auto-generate a WP, then execute it." The governance is thinner but not absent.
