# DERIVATION-FIX-1: Existence Check Fix

**Date:** 2026-08-11
**Status:** APPLIED
**Change Type:** Bug fix in requirement derivation logic

---

## Change

The existence-check for "Sprint X must have implementing artifacts" was updated to recognize multiple authoritative evidence locations.

### Before (Defective)

```python
# Only checked for sprint doc file
sprint_doc = LIBRARIAN_ROOT / "docs" / "sprints" / f"{source_sprint}.md"
if sprint_doc.exists():
    return "PASS"
else:
    return "FAIL"
```

### After (Fixed)

```python
# Checks multiple authoritative evidence locations
has_sprint_doc = sprint_doc.exists()
has_evidence_note = bool(sprint_data.get("evidence_note", ""))
has_commit = bool(sprint_data.get("commit", ""))

if has_sprint_doc or has_evidence_note or has_commit:
    return "PASS"
else:
    return "FAIL"
```

---

## Reason

27/27 pilot FAILs traced to this gap. UI sprints and other sprint types record evidence in the ledger's `evidence_note` field rather than in separate doc files at `docs/sprints/<ID>.md`. The derivation logic only checked for the doc file, missing the other valid evidence locations.

---

## Effect

| Metric | Before | After |
|---|---|---|
| Total tests | 307 | 307 |
| PASS | 280 | 307 |
| FAIL | 27 | 0 |
| ERROR | 0 | 0 |

All 27 FAILs were REQUIREMENT_DERIVATION_ERROR — the requirement was incorrectly derived due to incomplete evidence discovery, not a target defect.

---

## Evidence Locations Recognized

| Location | Source | Authority |
|---|---|---|
| `docs/sprints/<ID>.md` | Sprint documentation file | Direct |
| `evidence_note` | Sprint ledger field | Direct |
| `commit` | Sprint ledger field | Direct |

---

## Changelog Entry

```
DERIVATION-FIX-1
Change: existence-check now recognizes evidence_note and commit as
        valid evidence locations, in addition to docs/sprints/<ID>.md
Reason: 27/27 pilot FAILs traced to this gap (UI sprints record
        evidence in ledger, not separate doc files)
Effect: re-derive against full 307-requirement corpus — 0 FAILs remain
Date:   2026-08-11
```

---

*Fix applied as governed change. Original E2E-8 corpus preserved as pre-fix evidence.*
