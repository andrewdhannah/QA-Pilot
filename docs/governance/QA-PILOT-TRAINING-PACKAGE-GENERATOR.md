# QA Pilot Training Package Generator

**Sprint:** QA-PILOT-TRAINING-PACKAGE-GENERATOR-1 (Sprint 5/11)
**Epic:** EPIC-QA-PILOT-TRAINING-SYSTEM-1

## Purpose

Generate governed training packages from approved Librarian source material. Select source set, generate package, attach provenance, validate structure.

## Commands

| Command | Purpose |
|---------|---------|
| `init <pack-id> <type>` | Initialize new training package skeleton |
| `generate <pack-id>` | Generate full package from sources + content model |
| `provenance <pack-id> <paths>` | Attach/recompute source provenance |
| `validate <pack-id>` | Validate package against content model |
| `list` | List all generated packages |
| `status` | Show generator state |

## Hard Boundaries

- No generated artifact without source lineage
- All packages advisory-only
- No cross-project write
- No automatic publication
- No learning paths (Sprint 7)
- No simulation changes (Sprint 8)
- No MCP surface (Sprint 10)
