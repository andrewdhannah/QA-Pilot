# QA Pilot Pipeline Owner Review Packet — Governance

**Status:** Agent work complete — pending Owner review
**Sprint:** QA-PILOT-PIPELINE-OWNER-REVIEW-PACKET-1
**Boundary:** QA Pilot-local advisory review packet only
**Librarian impact:** none
**Authority:** advisory-only

## Purpose

Consolidate pipeline health, drift state, and recovery diagnostics into a single bounded Owner-facing review artifact.

## Commands

```
python3 scripts/qa_pilot_pipeline_owner_review_packet.py              # JSON
python3 scripts/qa_pilot_pipeline_owner_review_packet.py --report     # formatted
python3 scripts/qa_pilot_pipeline_owner_review_packet.py --fixture <p> # fixture
```

## Forbidden

- Auto-repair 
- Seal authority
- Librarian mutation
- New packet layer authority
