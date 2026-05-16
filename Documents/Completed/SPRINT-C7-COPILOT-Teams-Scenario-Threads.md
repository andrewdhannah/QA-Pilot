# Sprint C-7 — Teams Scenario Threads + Scenario-002 Data
## Copilot Prompt — GitHub repo: andrewdhannah/QA-Pilot

You are working in the QA Pilot repository.
No CDN links, no external imports, no fetch(). File:// safe architecture.
Run `node build.js` from the `desktop/` folder after making changes.

**Prerequisite:** Sprint C-6 (Teams Shell) must be merged and built before this sprint.

---

## Context

The Teams app (added in C-6) currently shows static placeholder messages.
This sprint wires Teams into the scenario system: when a scenario is loaded,
Teams displays a scripted conversation thread — the manager assigns the case,
a colleague adds context, and the trainee receives their brief via Teams chat
rather than a bare text notice.

This sprint also adds `scenario-002` — a more complex case with three hidden bugs
for use in the advanced training module.

---

## Part 1: Scenario data — `scenario-002`

### File to create: `desktop/scenarios/case-002.js`

```javascript
// scenarios/case-002.js — Advanced scenario: Customer Portal Access Failure
// Three deliberate bugs hidden in the CRM case for the trainee to discover.
// This scenario is used by the advanced capstone (capstone-2.html).

window.SCENARIOS = window.SCENARIOS || {};

window.SCENARIOS["case-002"] = {

  // ── Scenario metadata ────────────────────────────────────────────────────
  id:          "case-002",
  title:       "Customer Portal Access Failure",
  difficulty:  "advanced",
  description: "A business customer cannot access the self-service portal. " +
               "Three AC violations are present in the CRM case data.",

  // ── CRM state — loaded into Dynamics CRM on boot ─────────────────────────
  crmState: {
    caseId:       "CASE-00189",
    caseTitle:    "Business Portal — Login Failure After Password Reset",
    customerName: "Raj Patel",
    company:      "Northgate Logistics Ltd.",
    priority:     "High",
    status:       "Escalated",         // BUG-A: Junior role has Status set to "Escalated" — Junior cannot set this
    escalationReason: "",              // BUG-B: Escalation Reason is blank despite status being Escalated — AC-4.1 violation
    assignedTo:   "Junior Investigator",
    dateOpened:   "2026-07-15",        // BUG-C: Future date (today is May 2026) — AC-3.2 violation
    product:      "Customer Self-Service Portal",
    summary:      "Customer reports they are unable to log in to the portal after completing " +
                  "a password reset. Reset email was received and link was clicked, but login " +
                  "page shows 'Invalid credentials' error. Issue began 2026-07-14.",
    environment:  "Production",
    version:      "Portal v4.2.1",
  },

  // ── Acceptance criteria for this scenario ────────────────────────────────
  // The trainee must reference these IDs in their ADO bug reports.
  acceptanceCriteria: [
    { id: "AC-2.1", text: "Junior Investigators cannot set case Status to Escalated or Closed." },
    { id: "AC-3.2", text: "Date Opened must not be a future date." },
    { id: "AC-4.1", text: "Escalation Reason is mandatory when Status is set to Escalated." },
  ],

  // ── Bugs the trainee must discover ───────────────────────────────────────
  // bugId must match what is posted via BUG_FOUND / BUG_LOGGED from app iframes.
  expectedBugs: [
    {
      bugId:           "status-junior-escalated",
      description:     "Case Status is set to 'Escalated' but assigned role is Junior Investigator",
      acRef:           "AC-2.1",
      expectedSeverity: "2 - High",
      hint:            "Check who this case is assigned to, and whether they should be able to set this status.",
    },
    {
      bugId:           "escalation-reason-blank",
      description:     "Escalation Reason field is blank even though Status is Escalated",
      acRef:           "AC-4.1",
      expectedSeverity: "3 - Medium",
      hint:            "When a case is escalated, what information must always be recorded?",
    },
    {
      bugId:           "future-date-allowed",
      description:     "Date Opened is set to a future date (2026-07-15 is after today)",
      acRef:           "AC-3.2",
      expectedSeverity: "3 - Medium",
      hint:            "Can a case be opened on a date that hasn't happened yet?",
    },
  ],

  // ── Teams thread — loaded into Teams app when scenario starts ─────────────
  // Each message is displayed in chronological order in the #General channel.
  // "sender" is shown as the message author. "avatar" is 2-char initials or emoji.
  // "time" is a display string (shown as-is). "isBot" renders the message in a
  // slightly different style (subtle left border, bot avatar colour).
  teamsThread: [
    {
      sender:    "Elyse Hannah",
      avatar:    "EH",
      avatarBg:  "#0078d4",
      time:      "Today at 8:47 AM",
      body:      "Morning team. New priority case in the queue — CASE-00189. " +
                 "Raj Patel from Northgate Logistics can't access the portal after a password reset. " +
                 "Priority: **High**. Can someone pick this up first thing?",
    },
    {
      sender:    "QA Bot",
      avatar:    "🤖",
      avatarBg:  "#5b5fc7",
      time:      "Today at 8:47 AM",
      isBot:     true,
      body:      "📋 Case CASE-00189 assigned to **Andrew Hannah**. Scenario loaded. Good luck!",
    },
    {
      sender:    "Sam (Senior QA)",
      avatar:    "SQ",
      avatarBg:  "#107c10",
      time:      "Today at 8:51 AM",
      body:      "Heads up — I glanced at the case before it was reassigned. " +
                 "Something looked off with the metadata. Worth checking the AC checklist carefully before you start filing. 🧐",
    },
    {
      sender:    "Elyse Hannah",
      avatar:    "EH",
      avatarBg:  "#0078d4",
      time:      "Today at 9:02 AM",
      body:      "Andrew — reminder that the AC for this product version is in the AC Panel app. " +
                 "Check each field against the acceptance criteria before concluding your review. " +
                 "Sprint review is at end of day.",
    },
  ],
};
```

---

## Part 2: Wire Teams to scenario data

### File to modify: `apps/teams.html`

When Teams receives `APP_BOOT` with a `scenarioId`, load that scenario's `teamsThread`
and render it in the main message area, replacing the static placeholder messages.

#### 2a — Update the APP_BOOT handler

```javascript
window.addEventListener("message", function(event) {
  var msg = event.data;
  if (!msg) return;

  if (msg.type === "APP_BOOT" && msg.appId === "teams") {
    applyTheme(msg.theme || "light");

    // Load scripted thread if a scenario is active
    if (msg.scenarioId) {
      loadScenarioThread(msg.scenarioId);
    }
  }

  if (msg.type === "SCENARIO_LOADED") {
    // Fired by the OS if the scenario changes after boot
    if (msg.scenarioId) loadScenarioThread(msg.scenarioId);
  }

  if (msg.type === "THEME_CHANGE") {
    if (msg.theme) applyTheme(msg.theme);
  }
});
```

#### 2b — `loadScenarioThread(scenarioId)`

```javascript
function loadScenarioThread(scenarioId) {
  // Access SCENARIOS via parent window (same-origin: Teams iframe → OS shell)
  var scenarios = (window.parent && window.parent.SCENARIOS) || window.SCENARIOS || {};
  var scenario  = scenarios[scenarioId];

  if (!scenario || !scenario.teamsThread || !scenario.teamsThread.length) return;

  renderThread(scenario.teamsThread);
}
```

#### 2c — `renderThread(messages)`

Replace the static messages in the `#teams-messages` container with the scripted thread.
Render each message using the same visual style as the static messages in C-6.

```javascript
function renderThread(messages) {
  var container = document.getElementById("teams-messages");
  if (!container) return;

  container.innerHTML = "";  // clear static placeholders

  messages.forEach(function(msg) {
    var el = document.createElement("div");
    el.className = "teams-msg" + (msg.isBot ? " teams-msg--bot" : "");

    // Avatar
    var avatar = document.createElement("div");
    avatar.className = "teams-avatar";
    avatar.textContent = msg.avatar || "??";
    avatar.style.background = msg.avatarBg || "#5b5fc7";

    // Body column
    var body = document.createElement("div");
    body.className = "teams-msg-body";

    // Header row: sender name + timestamp
    var header = document.createElement("div");
    header.className = "teams-msg-header";
    header.innerHTML =
      '<span class="teams-msg-sender">' + escapeHtml(msg.sender) + '</span>' +
      '<span class="teams-msg-time">' + escapeHtml(msg.time) + '</span>';

    // Message text — support **bold** markdown shorthand
    var text = document.createElement("div");
    text.className = "teams-msg-text";
    text.innerHTML = parseSimpleMd(msg.body);

    body.appendChild(header);
    body.appendChild(text);
    el.appendChild(avatar);
    el.appendChild(body);
    container.appendChild(el);
  });

  // Scroll to bottom
  container.scrollTop = container.scrollHeight;
}

// Parse **bold** → <strong>bold</strong> only. No other markdown.
function parseSimpleMd(str) {
  return escapeHtml(str).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}

function escapeHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
```

Give the `#teams-messages` div an `id` attribute if it doesn't have one already.
The container must already exist in the C-6 HTML structure — do not restructure the layout.

---

## Part 3: Broadcast SCENARIO_LOADED from os-core.js

When a scenario is started, the OS should notify all open app iframes — including Teams —
so they can update their content. Use the existing EventBus.

### File to modify: `src/os-core.js`

Find the `startCapstoneScenario(scenarioId)` function and add a broadcast at the end:

```javascript
function startCapstoneScenario(scenarioId) {
  // ... existing code ...

  // Notify all open app iframes so they can react to the new scenario
  var bus = window.QA_OS && window.QA_OS.EventBus;
  if (bus && bus.postToAllApps) {
    bus.postToAllApps({ type: "SCENARIO_LOADED", scenarioId: scenarioId });
  }
}
```

Add this broadcast call at the END of the existing `startCapstoneScenario` function,
after all existing logic. Do not remove or reorder any existing code in that function.

---

## What NOT to Change

- Do not touch `build.js`
- Do not touch `os.css`
- Do not touch any app files other than `apps/teams.html`
- Do not modify the `APPS` constant (already done in C-6)
- Do not add CDN links or external dependencies

---

## Definition of Done

- [ ] `desktop/scenarios/case-002.js` created with `crmState`, `acceptanceCriteria`, `expectedBugs`, and `teamsThread`
- [ ] Teams `APP_BOOT` handler updated to call `loadScenarioThread(msg.scenarioId)` when `scenarioId` is present
- [ ] `loadScenarioThread()` reads from `window.parent.SCENARIOS` and calls `renderThread()`
- [ ] `renderThread()` clears static messages and renders the scripted thread with correct sender, avatar, timestamp, body
- [ ] `**bold**` text in message bodies renders as `<strong>` in the output
- [ ] Messages container scrolls to bottom after render
- [ ] `SCENARIO_LOADED` broadcast added to `startCapstoneScenario()` in `src/os-core.js`
- [ ] Static placeholder messages from C-6 still appear when no `scenarioId` is present
- [ ] `node build.js` runs without errors
- [ ] Opening Teams when a scenario is active shows the scripted thread; opening without a scenario shows the static placeholders
