# QA Pilot Owner Review Decision Receipt — Governance

**Status:** Agent work complete — pending Owner review
**Sprint:** QA-PILOT-OWNER-REVIEW-DECISION-RECEIPT-1
**Boundary:** QA Pilot-local advisory receipt store only
**Librarian impact:** none
**Authority:** advisory-only

## Commands

```
record accept/authorize/defer/reject [--note "text"]  Record Owner decision
list [--limit N]                                       List receipts
read <receipt_id>                                      Read a receipt
status                                                  Store status
clear                                                   Clear all receipts
```

## Forbidden

- Creating seal, repair, or mutation authority
- Auto-executing decisions
- Librarian mutation
