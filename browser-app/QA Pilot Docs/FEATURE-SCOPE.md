# QA Pilot — Feature Scope & Improvement Plan
*Generated 2026-05-25 after full cross-app audit*

---

## The honest answer to "can a student just go in and train?"

**Right now: mostly no.** The UI looks right, the content is there, but four bugs in the plumbing prevent the training loop from closing properly. Once those four are fixed (all specced in SESSION-HANDOFF.md), the answer becomes **yes for Capstone 1 and 2**. For the Training module, it becomes yes after BUG-T1/T2/T3 are fixed.

**If a student "just screws around"** — they can open apps freely, change fields, trigger validation errors, and the OS will react. But two things currently break the experiment: (1) Dynamics doesn't show the future-date defect because relative dates aren't resolved, and (2) the Owner field doesn't exist in the Dynamics form even though case-003 has a blank-owner bug.

**Does it start fresh?** No. Apps stay open with stale data between scenario changes. That's BUG-T2.

---

## Current App Inventory

### Dynamics CRM — What exists
| Field | Type | Notes |
|-------|------|-------|
| Case ID | readonly text | Set from crmState |
| Linked Bug | readonly text | Set from scenario |
| Title | text input | Required, validated on save |
| Priority | select | Options: Low / Medium / High — **Critical missing** |
| Status | select | Junior-gated: Active/Resolved only; Senior: full set |
| Customer | text input | |
| Escalation Reason | select | Required when Status=Escalated (validated) |
| Date Opened | date input | **Relative "+3d" dates not rendered — BUG-T3** |
| Last Updated | readonly text | Intentionally stale for bug scenarios |
| Summary | textarea | |
| Resolution Date | date | Senior-only (lock card for juniors) |
| Resolution Notes | textarea | Senior-only (lock card for juniors) |
| Timeline | add notes | Student can add notes manually |

**Live reactions in Dynamics:**
- BUG_FOUND fires when Status set to restricted value for Junior
- BUG_FOUND fires when date validation fails
- OS.notify() shows toast on save + field violations
- BPF stage bar present (visual only, not interactive)

### Azure DevOps — What exists
| Field | Type | Notes |
|-------|------|-------|
| Title | text | Required |
| Area | text | Pre-filled "Contoso\Web - Azure DevOps" |
| Linked Case | readonly | From scenario |
| Repro Steps | textarea | |
| Expected | textarea | |
| Actual | textarea | |
| Severity | select | 1-Critical / 2-High / 3-Medium / 4-Low |
| Assigned To | text | Hardcoded "Senior Investigator" |
| AC Reference | text | Validated against scenario acRefs |
| State | select | New / Active / Resolved / Closed |
| Tags | text | |

**Live reactions in ADO:**
- BUG_LOGGED fires on save with full bug data → OS counts it, Clip reacts
- AC ref validated against scenario's acRefs array; error shown if invalid
- AC hints panel shows valid refs for current scenario
- Confirmation toast on save
- **No filed bugs list** — after saving, form clears; student has no record of what they submitted

### Teams — What exists
| Channel | Content | Interactivity |
|---------|---------|---------------|
| #qa-team | Scenario teamsThread messages | Read only during training |
| #standup | Standup update form (stage 4+ Capstone 2 only) | 3-field form → fires STANDUP_POSTED |
| #sprint-review | Sprint review content (stage 6+ Capstone 2 only) | Partially interactive |
| Compose bar | Present in all channels | Sends message to current channel DOM only |

**Live reactions in Teams:**
- Scenario teamsThread rendered on APP_BOOT
- Student can type and "send" messages (appear in channel but no server response)
- Standup form at stage 4 — validates 3 fields, fires STANDUP_POSTED to advance stage
- **For training scenarios (non-C2): compose sends to DOM only. No scripted QA Lead response. No Acknowledge button.**

### QOutlook — What exists
- Left rail: Inbox / Sent / Drafts / Deleted
- Static emails: 5–6 generic workplace emails (IT maintenance, team calendar, etc.)
- Scenario emails: **only for Capstone 2** (reads `scenario.stages`); stage-gated
- Compose: button exists, opens compose pane — messages go nowhere
- **For all training scenarios (case-001, 002, 003): no scenario-specific emails at all**

### AC Panel — What exists
- Four cards: Scenario header, Global criteria (hardcoded), Case-specific criteria, Bug-specific criteria, Relationship criteria
- Read-only reference panel
- Loaded from scenario.acceptanceCriteriaGlobal / acceptanceCriteriaScenario on APP_BOOT
- **No highlighting, no search, no "you just violated this AC" feedback**

---

## Critical Bugs (must fix before training works)

These are fully specced with code in SESSION-HANDOFF.md.

| ID | Impact | File | Fix |
|----|--------|------|-----|
| BUG-T1 | Apps get wrong scenario data in Training mode | apps/training.html | Add `OS.setActiveScenarioId(id)` call in `beginScenario()` |
| BUG-T2 | Stale app state between scenario changes | apps/training.html + src/os-core.js | Close working apps on scenario change |
| BUG-T3 | Future-date defect invisible in Dynamics | apps/dynamics.html + inline in capstone-2.html | `resolveRelativeDate()` helper for "+Nd" strings |
| BUG-T4 | QOutlook generic for all training scenarios | apps/qoutlook.html + scenario files | Add `qoutlookEmails` to scenarios + QOutlook reader |

**Plus two Dynamics form gaps that block specific bug scenarios:**
| Gap | Impact | Fix |
|----|--------|-----|
| Priority dropdown missing "Critical" | case-003 priority mismatch bug is unfindable | Add Critical option to `<select id="d365-priority">` |
| Owner field missing entirely | case-003 blank-owner bug is unfindable | Add `<input id="d365-owner">` field + populate from `crmState.owner` |

---

## Feature Improvements — Prioritised

### Tier 1 — Makes training genuinely work (small effort, high impact)

**F1. Dynamics: Add "Critical" priority option**
- Add `<option value="Critical">Critical</option>` to `d365-priority` select (first position)
- Update `applyRole()` / `checkPriorityMismatch()` to detect Low when case description implies Critical
- Needed for case-003 scenario to be completable

**F2. Dynamics: Add Owner field**
- Add `<div class="d365-field required">` with `<input id="d365-owner" />` to the form grid
- Populate from `crmState.owner` in `populateCaseForm()`
- Fire `BUG_FOUND("owner-unassigned")` if owner is blank on save
- Needed for case-003's blank-owner bug

**F3. ADO: Filed bugs sidebar**
- After each successful save, append the bug title + severity + AC ref to a collapsible "Filed Bugs" panel at the bottom
- Persists in sessionStorage so student can review what they've submitted
- Critical for self-checking: "Have I filed all 3 bugs?"

**F4. Teams: Acknowledge button on kickoff messages**
- If a teamsThread message has `type: "kickoff"`, render it with an Acknowledge button
- On click: button becomes "✓ Acknowledged", fires `OS_NOTIFICATION` with "Acknowledged sprint briefing"
- Simple, makes it feel interactive, teaches the team communication loop

**F5. Scenario reset on training start**
- When `beginScenario()` fires, call `OS.closeApp('dynamics')`, `OS.closeApp('ado')`, `OS.closeApp('teams')` (if open)
- Then open them fresh via `OS.openApp(...)` — they'll pick up the new `activeScenarioId`
- This is BUG-T2 fix but framed as a feature: "fresh workspace for each scenario"

### Tier 2 — Significantly improves realism (medium effort)

**F6. AC Panel: Dynamic violation highlight**
- When Dynamics fires `BUG_FOUND`, broadcast `AC_VIOLATED` with the AC ref (e.g. "AC-2.1")
- AC Panel listens and highlights the matching criterion in yellow
- Teaches the student to connect what they observed to the rule that defines it

**F7. Teams: Scripted QA Lead response to student messages**
- When student sends a message in #qa-team, after 1–2 seconds render a scripted reply from "Sarah Chen / Elyse Hannah" based on simple keyword matching
- e.g. student types "found 2 bugs" → QA Lead replies "Great work — make sure you've checked all the AC refs before submitting! 💪"
- Canned responses are fine; even 4–5 makes it feel alive

**F8. QOutlook: Scenario inbox for training scenarios**
- Add `qoutlookEmails` array to case-001, case-002, case-003 scenario data
- Update QOutlook `buildScenarioEmails()` to read from it when `scenario.stages` doesn't exist
- Minimum: one email per scenario from the QA Lead assigning the case, matching the Teams briefing

**F9. Dynamics: Business Process Flow (BPF) stages become interactive**
- Currently the BPF bar (Qualify → Research → Resolve) is visual-only
- Make clicking a stage advance the marker and update a "current stage" label
- Fire `OS_NOTIFICATION` when student moves from Research → Resolve ("Case moved to Resolution stage")
- Reinforces the real CRM workflow concept

**F10. ADO: Student name in "Assigned To" field**
- Currently hardcoded "Senior Investigator"
- Read student name from `window.__capstoneStudentInfo.name` or `APP_BOOT` session data
- Small but makes it feel personal

### Tier 3 — Polish that elevates the experience (low-medium effort)

**F11. Clip: React to BUG_FOUND (Dynamics violation) not just BUG_LOGGED**
- Currently Clip only counts BUG_LOGGED (ADO save)
- When `BUG_FOUND` fires from Dynamics, Clip says "Nice catch — that's a real defect! Now file it in ADO. 🔍"
- Closes the loop between noticing a bug and filing it

**F12. Dynamics: Save button feedback**
- After save: button shows "✓ Saved" in green for 2 seconds, then resets
- Timeline auto-adds a "Case updated by [student name]" entry with timestamp
- Last Updated field actually updates (it's intentionally stale for one bug scenario, but normal saves should update it)

**F13. Training module: Scenario brief overlay**
- When student clicks "Start Training" in the training app, show the same OS scenario brief overlay that Capstone uses
- Gives context before apps open: "You've been assigned CASE-00189. Here's what you need to know..."
- Currently students jump straight into the training steps with no scene-setting

**F14. Training module: "Open Apps" button in step panel**
- Each step has a position reference ("Open Dynamics..."). Add a small "Open →" chip next to app names
- Clicking it posts `openApp("dynamics")` to the OS parent
- Removes friction: student doesn't have to find the app themselves while reading the step

**F15. Clip: "Start Over" / reset button**
- Clip's `?` help panel gets a "Start Over" option
- Calls `OS.setActiveScenarioId(currentId)` and closes/reopens the working apps
- Lets students reset without leaving the scenario

**F16. AC Panel: Searchable criteria list**
- Add a search input at the top of the AC Panel
- Filter criteria in real time by AC number (type "AC-2" → shows only AC-2.x entries)
- Students often need to look up a specific AC quickly while working

**F17. QOutlook: Unread count badge on app icon**
- When new scenario emails arrive (or are present and unread), show a red badge on the QOutlook taskbar icon
- Requires OS support: OS sends `APP_BADGE_UPDATE` → taskbar button shows count
- Mirrors real Outlook behaviour; trains students to check email as part of workflow

---

## App Interaction Map — Current vs Target

```
CURRENT STATE:
OS ──(APP_BOOT + scenario data)──→ Teams, ADO, Dynamics, AC, QOutlook
ADO ──(BUG_LOGGED)──→ OS → Clip counts
Dynamics ──(BUG_FOUND)──→ OS (logs it, no Clip reaction)
Teams ──(STANDUP_POSTED)──→ OS → advances Capstone 2 stage only

GAPS:
Training.html ──(beginScenario)──→ OS [NOT CALLING setActiveScenarioId]
Dynamics ──(BUG_FOUND)──→ AC Panel [no highlight]
ADO save ──→ Filed Bugs panel [doesn't exist]
QOutlook ──→ scenario emails for training [not wired]

TARGET STATE (after all tiers):
Training.html ──(beginScenario)──→ OS.setActiveScenarioId → apps reboot with correct data
OS ──(APP_BOOT)──→ all apps get scenario, role, student name
Dynamics ──(BUG_FOUND "AC-2.1")──→ OS ──(AC_VIOLATED "AC-2.1")──→ AC Panel highlights row
ADO ──(BUG_LOGGED)──→ OS → Clip "X of N filed!" + Filed Bugs sidebar updates
Teams student message ──→ scripted QA Lead response after 1.5s delay
QOutlook ──scenario emails──→ student reads briefing, mark as read
Training step ──(Open → chip)──→ OS.openApp("dynamics")
Clip ──(BUG_FOUND)──→ "Nice catch! Now file it in ADO →"
```

---

## Realism Assessment vs Real Tools

| Feature | Real Tool | Current Sim | Gap |
|---------|-----------|-------------|-----|
| CRM Priority | Low/Medium/High/**Critical** | Low/Medium/High | Missing Critical |
| CRM Owner field | Always required | Field not in form | Field missing entirely |
| CRM BPF | Interactive stage progression | Visual only | No click interaction |
| CRM timeline | Auto-adds entries on save | Manual only | Save doesn't add entry |
| ADO filed bugs list | Full backlog list | Single form, no list | No history view |
| ADO assigned to | Student's name | "Senior Investigator" | Not personalised |
| Teams replies | Real-time from colleagues | No scripted replies | No response to student |
| Teams acknowledge | Read receipts / reactions | No acknowledge mechanic | Missing |
| Outlook inbox | Scenario-specific emails | Generic static only | Not wired to scenarios |
| Outlook unread badge | Unread count on icon | Not present | Feature gap |
| AC Panel | Interactive checklist | Static read-only | No check-off or highlight |

---

## Recommended Build Order

```
Sprint A — Make training work (critical bugs)
  1. BUG-T3: resolveRelativeDate in Dynamics (20 min)
  2. F1 + F2: Add Critical priority + Owner field to Dynamics (30 min)
  3. BUG-T1: OS.setActiveScenarioId API + training.html call (30 min)
  4. BUG-T2: Close stale apps on scenario change (20 min)
  → Build + test

Sprint B — Make apps feel connected (high-value realism)
  5. F3: ADO filed bugs sidebar (45 min)
  6. F4: Teams acknowledge button (20 min)
  7. BUG-T4 + F8: QOutlook scenario emails (45 min)
  8. F11: Clip reacts to BUG_FOUND from Dynamics (15 min)
  → Build + test

Sprint C — Polish + immersion
  9. F6: AC Panel violation highlight (30 min)
  10. F7: Teams scripted QA Lead replies (30 min)
  11. F13: Training scenario brief overlay (20 min)
  12. F14: Training "Open →" app launch chips (20 min)
  13. F15: Clip "Start Over" button (15 min)
  → Build + test

Sprint D — Nice-to-haves
  14. F9: BPF interactive stages in Dynamics
  15. F10: Student name in ADO assigned-to
  16. F12: Dynamics save confirmation + timeline entry
  17. F16: AC Panel search
  18. F17: QOutlook unread badge
```

---

## LLM Prompt Templates Needed

In addition to scenario step expansion (already in SCENARIO-LLM-PROMPTS.md), the following content needs writing and could be LLM-generated:

1. **Teams scripted QA Lead replies** (F7) — keyword→response map for each scenario
2. **QOutlook scenario emails** (F8) — one kickoff email per training scenario from QA Lead
3. **Clip BUG_FOUND reactions** (F11) — per-bugId encouraging messages ("You spotted the closed status — that's AC-2.1!")
4. **Timeline auto-entries** (F12) — templated timeline note text for each save action
5. **Scenario brief overlay text** (F13) — the "here's your assignment" brief for each training scenario

---

*Next agent: Read SESSION-HANDOFF.md for the 4 critical bugs with exact code. Then start Sprint A above.*
