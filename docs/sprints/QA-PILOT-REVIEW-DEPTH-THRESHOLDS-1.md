# Sprint Receipt — QA-PILOT-REVIEW-DEPTH-THRESHOLDS-1

**Ledger #88**
**Lane:** QA Pilot
**Type:** substantive capability / review depth thresholds
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none
**Input dependencies:** E4 evidence chain (sealed)
**Seal status:** 🔍 complete_pending_owner_review — NOT self-sealed

## Deliverables

### Schema
- `docs/schemas/qa-pilot-review-depth-threshold.schema.json` — 9 required fields
- Advisory states: sufficient, needs_more_context, blocked
- Bound to evidence bundle context (consistency guard refs, item counts, pass counts)

### CLI (5 commands)
- `threshold-evaluate` — Evaluate depth against evidence posture
- `threshold-read <id>` — Read stored threshold
- `threshold-list` — List stored thresholds
- `threshold-validate [id]` — Validate against schema + TD-1–TD-8
- `threshold-status` — Show aggregate threshold state

### Validator
- `scripts/validate-qa-pilot-review-depth-thresholds.py` — TD-1 through TD-8
- TD-6 rejects auto-accept/auto-reject/execution/seal/approval/verification/closure/mutation fields
- TD-7 rejects authority-claiming rationale

### Fixtures (6)
- 3 valid: sufficient, needs_more_context, blocked
- 3 invalid: auto-accept claim, execution/seal claim, verify/close/mutate claim

### Tests (14/14 pass)
### Store: `data/review-depth-thresholds/`

## Authority Boundaries
- Classifies evidence depth for Owner review guidance only
- No auto-acceptance, no auto-rejection, no execution authority
- Owner remains final decision point
