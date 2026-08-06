# Sprint Receipt — QA-PILOT-RISK-BASED-REVIEW-DEPTH-1

**Ledger #91**
**Lane:** QA Pilot
**Type:** substantive capability / risk-based review depth implementation
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none
**Input dependencies:** QA-PILOT-REVIEW-DEPTH-THRESHOLDS-1 (#88, sealed), QA-PILOT-REVIEW-DEPTH-THRESHOLDS-DECISION-PACKET-1 (#90, sealed), RC result packet consistency framework, E4 evidence bundle framework
**Seal status:** ✅ Sealed — Owner-approved 2026-07-08

## Deliverables

### Schemas (4)
- `docs/schemas/qa-pilot-risk-based-review-depth.schema.json` — 14 required fields, RD-EVAL- ID pattern
- `docs/schemas/qa-pilot-risk-based-review-card.schema.json` — Light review card, RC- ID pattern
- `docs/schemas/qa-pilot-risk-based-review-packet.schema.json` — Standard review packet, RP- ID pattern
- `docs/schemas/qa-pilot-risk-based-heavy-packet.schema.json` — Heavy evidence review packet, HP- ID pattern

### CLI (8 commands)
- `depth-evaluate` — Evaluate result packet against 9 risk inputs, assign review depth
- `depth-read <id>` — Read stored depth evaluation
- `depth-list` — List stored depth evaluations
- `depth-validate [id|file]` — Validate against schema + RD rules
- `depth-status` — Show aggregate depth state
- `card-create <eval-id>` — Generate light review card
- `packet-create <eval-id>` — Generate standard review packet
- `packet-heavy-create <eval-id>` — Generate heavy evidence review packet

### Validator
- `scripts/validate-qa-pilot-risk-based-review-depth.py` — RD-1 through RD-15 evaluations, C-1–C-3 cards, P-1–P-2 packets, H-1–H-2 heavy packets

### Fixtures (9)
- 6 valid: low-risk-lightweight, authority-change-heavy, partial-completion-standard, failed-rc-escalated, standard-packet-example, heavy-packet-example
- 3 invalid: authority-claim, depth-too-low, seal-claim

### Tests (19/19 pass)
- 6 validation scenarios covering all risk profiles
- 11 CLI/validator/regression checks

### Store
- `data/risk-based-review-depths/` — depth evaluations, review cards, review packets, heavy packets

### Governance
- `docs/governance/QA-PILOT-RISK-BASED-REVIEW-DEPTH.md`

## Review Depth Model

| Level | Score Range | Escalation Floor | Output |
|-------|-------------|------------------|--------|
| none | 0–3 | ER-9 (lightweight+all pass) | No artifact |
| light | 4–10 | — | Light review card |
| standard | 11–20 | ER-2/3/4/5/6 (ledger/prod/cross-node/partial/incomplete) | Standard review packet |
| heavy | 21+ | ER-1 (authority change) | Heavy evidence review packet |

## Escalation Rules (ER-1 through ER-10)

| Rule | Trigger | Effect |
|------|---------|--------|
| ER-1 | Authority change | Floor = heavy |
| ER-2 | Ledger/registry change | Floor = standard |
| ER-3 | Production-path impact | Floor = standard |
| ER-4 | Cross-node involvement | Floor = standard |
| ER-5 | Partial completion | Floor = standard |
| ER-6 | Incomplete requirements | Floor = standard |
| ER-7 | RC failures | Escalate +1 level |
| ER-8 | E4 failures | Escalate +1 level |
| ER-9 | Lightweight + all pass + no triggers | Floor = none |
| ER-10 | Multiple rules fire | Highest depth wins |

## Authority Boundaries
- Advisory-only: no approval, no seal, no production mutation
- QA Pilot never replaces Owner decision authority
- Sealed #88, #89, #90 artifacts unchanged
- Existing QA Pilot validators unaffected
- Windows Router remains deferred_not_wired
