# Canonical Surface Validation Rule

**Classification:** Seal lifecycle governance rule (NOT an assurance contract)
**Status:** Active — recorded 2026-07-27
**Source observation:** EPIC-QA-PILOT-I18N-WIRING-1 (#148–#152) — pre-migration validation superseded by surface replacement
**Promotion candidate:** Future assurance contract if pattern repeats across multiple migrations or platform version transitions

---

## Rule

A completed work item may only be sealed as a current implementation artifact if the validated surface remains the canonical target.

If the validated surface is replaced, migrated, or superseded:

1. Preserve the original evidence as historical record
2. Record the relationship between original and replacement surfaces
3. Close the implementation item as superseded (not sealed)
4. Link to the replacement artifact that carries the capability forward

## Rationale

Without this rule, the record can falsely imply "the current system was validated" when the evidence actually proves "a previous system state was validated."

| Statement | Correct | Incorrect |
|-----------|---------|-----------|
| "Validation was performed" | Evidence record | Evidence record |
| "The validated surface is current" | Requires check | Assumed by default |
| "The implementation is accepted" | Seal = current surface | Seal = old surface |

## Application to the I18N Epic

| Sprint | Disposition | Reason |
|--------|------------|--------|
| #148 I18N baseline | Sealed as evidence | One-time analysis — not an implementation artifact |
| #149 Core dictionary | Superseded | Implementation replaced by #170/#171/#173 |
| #150 Page wiring | Superseded | Implementation replaced by post-migration wiring |
| #151 Rerender/state | Superseded | Behavior re-established through later implementation |
| #152 Roundtrip validation | Superseded | Validation target replaced; current validation at #135 |

## Evidence Chain

```
Original I18N work (#148–#152) — pre-migration surface (2026-07-09)
        |
        v
Migration (#157) replaced browser-app/ surface (2026-07-13)
        |
        v
Post-migration I18N (#170, #171, #173, #177) — canonical surface (sealed)
        |
        v
Frontend roundtrip validation (#135) — sealed 2026-07-27
```

## Check

When reviewing a sprint for seal eligibility, verify:

- [ ] Does the validated surface still exist in its validated state?
- [ ] Has the target surface been replaced, migrated, or superseded?
- [ ] If replaced, does a sealed artifact carry forward the capability?
- [ ] Is the evidentiary record preserved for historical traceability?
