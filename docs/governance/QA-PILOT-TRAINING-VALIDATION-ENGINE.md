# QA Pilot Training Validation Engine

**Sprint:** QA-PILOT-TRAINING-VALIDATION-ENGINE-1 (Sprint 6/11)
**Epic:** EPIC-QA-PILOT-TRAINING-SYSTEM-1

## Purpose

Deterministic validation of generated training packages. Training can fail validation deterministically.

## Commands

| Command | Purpose |
|---------|---------|
| `check <pack-id>` | Run all 10 validation checks |
| `check --all` | Validate all generated packages |
| `sources <pack-id>` | Validate source coverage per-section |
| `authority <pack-id>` | Validate authority posture |
| `status` | Show validation engine state |

## Checks (VE-1 to VE-10)

| Rule | What It Checks | Outcome |
|------|---------------|---------|
| VE-1 | Schema validity — required fields present | PASS/FAIL |
| VE-2 | Source coverage — provenance and section sources | PASS/FAIL |
| VE-3 | Stale references — referenced sources still exist | PASS/WARN |
| VE-4 | Missing sections — content has ≥1 section | PASS/FAIL |
| VE-5 | Authority violations — no forbidden authority claims | PASS/FAIL |
| VE-6 | Mutation paths — no Librarian mutation patterns | PASS/FAIL |
| VE-7 | Advisory posture — governance fields correct | PASS/FAIL |
| VE-8 | Exercise requirement — mandatory for appropriate types | PASS/FAIL |
| VE-9 | Provenance hash validity — SHA-256 format | PASS/FAIL |
| VE-10 | Pack ID format — TP- pattern | PASS/FAIL |

## Hard Boundaries

- Deterministic pass/fail/warn outcomes
- Training can fail validation (fail-closed)
- No auto-repair of failed packages
- No authority expansion
- No Librarian mutation
