# QA-PILOT-BROWSER-ONLY-STARTUP-AND-DEPLOYMENT-CONTRACT-1

**Generated:** 2026-07-08
**Epic:** EPIC-QA-PILOT-BROWSER-ONLY-DEPLOYMENT-AND-STARTUP-1 (Sprint 1/9)
**Status:** complete_pending_owner_review

---

## 1. Contract Overview

QA Pilot runs entirely in the browser from static hosting. No install, no backend, no server database, no required network after initial page load. Import/export JSON files are the team handoff mechanism. Local browser storage holds progress, identity selection, and resume state.

---

## 2. Startup Mode Matrix

| Mode | Trigger | Splash | Identity | Data Source | Network Required After Load? |
|------|---------|--------|----------|-------------|------------------------------|
| **Solo / No Login** | First visit or cleared storage | Show splash → Start training | Anonymous local learner profile created on first action | Browser local storage | No |
| **Returning User** | Visit with existing local state | Detect stored progress → Resume | Existing local learner profile | Browser local storage | No |
| **Team Deployment** | Import deployment JSON | Show splash → Import available | Local team identity selected from imported JSON | Browser local storage + imported JSON | No |
| **Admin / Trainer** | Visit with admin flag or local workspace | Show admin dashboard | Local admin identity (self-selected, not authenticated) | Browser local storage + local workspace JSON | No |

---

## 3. Deployment Mode Matrix

| Aspect | Solo | Returning | Team | Admin |
|--------|------|-----------|------|-------|
| **Start** | Splash → Start | Splash → Resume | Import JSON → Select identity | Admin dashboard |
| **Training** | Browse catalog → Enroll → Complete | Continue from checkpoint | Assigned package only | N/A |
| **Progress** | Local browser storage | Local (auto-resume) | Local (exportable) | View via imported results |
| **Export** | Optional backup JSON | Optional backup JSON | Result JSON (send to admin) | Deployment JSON, imported results |
| **Identity** | Anonymous local profile | Anonymous local profile | Selection from deployment JSON | Self-selected local admin |
| **Team handoff** | None | None | Deployment JSON → Result JSON | Creates deployment JSON, imports results |

---

## 4. JSON Custody Boundary Definition

### Deployment JSON (Admin → Learner)

Created by admin/trainer. Imported by learner. Contains:

```json
{
  "deployment_schema": "deployment-v1",
  "workspace_name": "Team Name",
  "generated_at": "ISO8601",
  "members": [
    {"local_id": "user-1", "display_name": "Alice"},
    {"local_id": "user-2", "display_name": "Bob"}
  ],
  "assigned_packages": [
    {"pack_id": "TP-...", "title": "Package Title", "assigned_to": ["user-1", "user-2"]}
  ],
  "advisory": true
}
```

### Result JSON (Learner → Admin)

Exported by learner. Imported by admin. Contains:

```json
{
  "result_schema": "result-v1",
  "learner_id": "user-1",
  "package_id": "TP-...",
  "completed_at": "ISO8601",
  "progress": {
    "sections_completed": ["s1", "s2"],
    "exercises_attempted": 3,
    "exercises_completed": 2
  },
  "evidence": {},
  "advisory": true
}
```

### Backup JSON (Learner → Local)

Optional backup of all local state:

```json
{
  "backup_schema": "backup-v1",
  "exported_at": "ISO8601",
  "local_profile": {},
  "progress": {},
  "imported_packages": [],
  "advisory": true
}
```

### Custody Rules

| Rule | Description |
|------|-------------|
| CR-1 | No JSON file is executable or authoritative |
| CR-2 | Every JSON carries `advisory: true` |
| CR-3 | Deployment JSON is a team assignment — not authentication |
| CR-4 | Result JSON is evidence — not approval |
| CR-5 | JSON files are the only cross-device handoff mechanism |
| CR-6 | No JSON file mutates Librarian |
| CR-7 | No JSON file grants authority |
| CR-8 | Owner/trainer review required before acting on result JSON |

---

## 5. Admin/Trainer Flow

```
1. Admin opens QA Pilot from static hosting
2. Sees splash with "Team Workspace" option (or auto-detect existing workspace)
3. Creates/manages local workspace:
   a. Add members (local_id + display_name)
   b. Assign training packages from available packs
   c. Generate deployment JSON
4. Sends deployment JSON to learners (email, share, USB, etc.)
5. Receives result JSON files from learners
6. Imports result JSON into admin portal
7. Views completion/progress per learner
8. No server, no authentication, no database
```

---

## 6. Learner Flow

```
1. Learner opens QA Pilot from static hosting (same URL as admin)
2. Sees splash screen
3. Imports deployment JSON file
4. Selects their local team identity from the imported member list
5. Sees assigned training packages
6. Completes training (browser-only runtime)
7. Progress auto-saves to browser storage
8. Exports result JSON
9. Sends result JSON to admin/trainer
10. No account, no password, no server
```

---

## 7. Returning User / Resume Flow

```
1. User opens QA Pilot on same browser/device
2. Splash screen detects existing local state:
   a. Local learner profile found
   b. In-progress training found
   c. Imported deployment JSON found
3. Shows: "Welcome back, [name]. Continue where you left off?"
4. User can:
   a. Resume training
   b. Start new training
   c. Import new deployment JSON
   d. Export backup
5. No login — identity from local storage
```

---

## 8. Terminology Rules

| Use | Do Not Use | Reason |
|-----|-----------|--------|
| local learner profile | account | No server-side identity |
| local team identity | user account | Identity is file-imported, not authenticated |
| deployment JSON | login credentials | JSON is assignment, not authentication |
| result JSON | submission | Result is evidence, not a server submission |
| local workspace | team server | Everything is local |
| browser storage | database | No server database |
| import/export custody boundary | auth boundary | JSON files are the handoff mechanism |
| resume state | session | No server session |
| identity selection | authentication | User picks from a list — no password |
| local admin | administrator | Self-selected, not provisioned |

---

## 9. Stop Conditions for Future Implementation Sprints

Stop and report to Owner if any sprint discovers a need for:

| # | Stop Condition | Why It Matters |
|---|---------------|----------------|
| SC-1 | Server authentication | Breaks browser-only model |
| SC-2 | Backend database | Requires install/server |
| SC-3 | Installed software | Breaks static-hosting deployment |
| SC-4 | Cloud account dependency | Requires network/signup |
| SC-5 | Cross-project write | Breaks QA Pilot boundary |
| SC-6 | Librarian mutation | Breaks authority model |
| SC-7 | Authority expansion | Training must remain advisory |
| SC-8 | Publication workflow | Owner decision bypass |
| SC-9 | Changing the training-system sealed architecture | Would reopen sealed #93–#109 |
| SC-10 | Replacing the browser-only model | Contract violation |
| SC-11 | Unclear distinction between local identity and real authentication | Security confusion |

---

## 10. Recommended Migration Sprint Sequence

| Priority | Sprint | Focus |
|----------|--------|-------|
| **P0** | QA-PILOT-BROWSER-SPLASH-AND-STARTUP-FLOW-1 | Splash screen, mode detection, solo/returning/admin entry points |
| **P1** | QA-PILOT-ADMIN-TEAM-PACKAGE-BUILDER-1 | Local workspace, member management, deployment JSON generation |
| **P2** | QA-PILOT-LEARNER-LOCAL-IDENTITY-IMPORT-1 | Import deployment JSON, select local identity, view assignments |
| **P3** | QA-PILOT-BROWSER-COURSE-RUNTIME-1 | Render training packs in browser (course-view equivalent) |
| **P4** | QA-PILOT-LOCAL-PROGRESS-TRACKING-1 | Auto-save progress, resume state, browser storage layer |
| **P5** | QA-PILOT-LEARNER-RESULT-EXPORT-1 | Export result JSON, custody boundary enforcement |
| **P6** | QA-PILOT-ADMIN-RESULT-IMPORT-1 | Import result JSON, completion dashboard |
| **P7** | QA-PILOT-BROWSER-ONLY-OPERATIONAL-BASELINE-1 | Lock completed system, regression tests, maintenance rules |

---

## 11. Validation Checklist

| # | Check | Result |
|---|-------|--------|
| V-1 | No server authentication required | ✅ Defined |
| V-2 | No backend database required | ✅ Defined |
| V-3 | No installed software required | ✅ Defined |
| V-4 | No cloud account dependency | ✅ Defined |
| V-5 | Runs from static hosting | ✅ Defined |
| V-6 | Import/export JSON is team handoff | ✅ Defined |
| V-7 | Browser storage is allowed | ✅ Defined |
| V-8 | Local identity ≠ authentication | ✅ Termed |
| V-9 | No autonomous publication | ✅ Defined |
| V-10 | No cross-project write | ✅ Defined |
| V-11 | No Librarian mutation | ✅ Defined |
| V-12 | All JSON files are advisory | ✅ Defined |
| V-13 | 4 startup modes defined | ✅ Solo, Returning, Team, Admin |
| V-14 | 4 deployment modes defined | ✅ Matrix complete |
| V-15 | 8 custody rules defined | ✅ CR-1 through CR-8 |
| V-16 | 11 stop conditions defined | ✅ SC-1 through SC-11 |
| V-17 | 8 future sprints proposed | ✅ P0–P7 |
| V-18 | Terminology rules documented | ✅ 12 term pairs |
| V-19 | No implementation performed | ✅ Contract only |
| V-20 | No UI rebuild, auth changes, data migration | ✅ Excluded |
