# QA Pilot Browser Splash and Startup Flow

**Sprint:** QA-PILOT-BROWSER-SPLASH-AND-STARTUP-FLOW-1 (Sprint 2/9)
**Epic:** EPIC-QA-PILOT-BROWSER-ONLY-DEPLOYMENT-AND-STARTUP-1
**Status:** complete_pending_owner_review

## Purpose

Implement the startup entry surface defined by the sealed browser-only contract. Splash screen, mode detection, solo/returning/admin/import flows.

## Files

| Path | Type | Purpose |
|------|------|---------|
| `docs/schemas/browser-assets/index.html` | Static HTML | Splash page — single file, no dependencies |

## Startup Modes Detected

| Mode | Trigger | Action |
|------|---------|--------|
| Solo | First visit or cleared state | Create anonymous local profile → route to catalog |
| Returning User | Existing `qapilot_state` in localStorage with in-progress items | Show resume banner → route to last URL |
| Import Team Deployment | "Import Team Deployment" button | File picker → validate deployment-v1 JSON → route to identity |
| Admin / Trainer | "Admin / Trainer Workspace" button | Route to admin.html |

## Contract Compliance

| Requirement | Status |
|-------------|--------|
| Single static HTML, no backend | ✅ index.html is standalone |
| No server authentication | ✅ No password field, no login API |
| No install required | ✅ Open in browser |
| Local browser storage allowed | ✅ localStorage for state |
| Import/export JSON is handoff | ✅ Deployment JSON import validated |
| Local identity ≠ authentication | ✅ Banner on every page |
| Advisory-only | ✅ All stored state advisory |
