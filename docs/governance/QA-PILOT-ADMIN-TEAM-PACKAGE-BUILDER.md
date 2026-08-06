# QA Pilot Admin Team Package Builder

**Sprint:** QA-PILOT-ADMIN-TEAM-PACKAGE-BUILDER-1 (Sprint 3/9)
**Epic:** EPIC-QA-PILOT-BROWSER-ONLY-DEPLOYMENT-AND-STARTUP-1
**Status:** complete_pending_owner_review

## Purpose

Build the admin/trainer workspace for creating local team workspaces, adding learners, assigning training packages, and exporting deployment-v1 JSON files.

## Delivered

| Path | Type | Purpose |
|------|------|---------|
| `docs/schemas/browser-assets/admin.html` | Static HTML | Admin workspace — 4-tab interface |

## Capabilities

| Feature | Implementation |
|---------|---------------|
| Workspace name | Text input → localStorage persistence |
| Team member creation | Add/remove members with display name + local ID |
| Package assignment | Checkbox selection from locally available training packs |
| Deployment JSON generation | Generates deployment-v1 schema, validates required fields, downloads as file |
| All localStorage | No server, no database, no auth |

## Contract Compliance

- ✅ No backend — static HTML only
- ✅ No password fields or login forms
- ✅ No server database — all localStorage
- ✅ Deployment JSON includes `advisory: true`
- ✅ Deployment JSON follows deployment-v1 schema
- ✅ Identity note on every page
- ✅ No cross-project write
- ✅ No Librarian mutation
