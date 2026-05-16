# Sprint C-8 — Teams Sprint Review Scoring
## Copilot Prompt — GitHub repo: andrewdhannah/QA-Pilot

You are working in the QA Pilot repository.
No CDN links, no external imports, no fetch(). File:// safe architecture.
Run `node build.js` from the `desktop/` folder after making changes.

**Prerequisites:** Sprints C-6 (Teams Shell) and C-7 (Scenario Threads) must be merged first.

---

## Context

When the trainee clicks "Submit for Certification" in the OS taskbar, `runSubmit()` in
`src/os-core.js` fires. Currently it calls `window.evaluateSubmission()` and shows a
result modal. This sprint replaces the generic modal with a **Teams Sprint Review thread**
— a QA Lead scores each filed bug report inline, exactly like a real sprint review meeting.

This is the payoff of the Teams wrapper: the trainee gets specific, per-bug feedback
from a simulated colleague, not just a score out of 10.

The OS already tracks logged bugs in `state.bugsLogged` (each entry is the `data` object
from a `BUG_LOGGED` postMessage: `{ title, severity, acRef, hasSteps }`).
The active scenario's `expectedBugs` array is the reference for scoring.

---

## Deliverable 1: Scoring function in `src/os-core.js`

Add a new function `scoreSubmission(scenarioId, bugsLogged)` to `os-core.js`.
This function evaluates each filed bug against four criteria and returns a structured result.

```javascript
// ── SPRINT REVIEW SCORING ────────────────────────────────────────────────────
// Evaluates each BUG_LOGGED entry against the active scenario's expectedBugs.
// Returns a result object consumed by both the Teams review thread and the
// existing result modal.
//
// Scoring criteria per bug report:
//   1. Title quality   — length > 10 chars, not a generic placeholder
//   2. Severity format — matches "N - Label" pattern (e.g. "2 - High")
//   3. AC Reference    — matches "AC-N.N" or "AC-N" format
//   4. Steps to repro  — hasSteps is true
//
// Bonus: if the AC reference matches an expected bug's acRef, the report is
// flagged as "matched" (found the right bug, not just any bug).

function scoreSubmission(scenarioId, bugsLogged) {
  var scenario     = window.SCENARIOS && window.SCENARIOS[scenarioId];
  var expected     = (scenario && scenario.expectedBugs) || [];
  var acPattern    = /^AC-\d+(\.\d+)?$/i;
  var sevPattern   = /^\d\s*-\s*.+$/;

  var scored = bugsLogged.map(function(bug, idx) {
    var title    = (bug.title    || "").trim();
    var severity = (bug.severity || "").trim();
    var acRef    = (bug.acRef    || "").trim();
    var hasSteps = !!bug.hasSteps;

    var checks = {
      title:    title.length > 10 && !/^(bug|issue|test|untitled|defect)$/i.test(title),
      severity: sevPattern.test(severity),
      acRef:    acPattern.test(acRef),
      steps:    hasSteps,
    };

    // Check if this report targets a real expected bug
    var match = expected.find(function(e) {
      return e.acRef && acRef.toLowerCase() === e.acRef.toLowerCase();
    });

    var passed = checks.title && checks.severity && checks.acRef && checks.steps;

    return {
      index:    idx + 1,
      title:    title || "(no title)",
      severity: severity || "(none)",
      acRef:    acRef || "(none)",
      hasSteps: hasSteps,
      checks:   checks,
      matched:  !!match,
      expected: match || null,
      passed:   passed,
    };
  });

  var passCount  = scored.filter(function(b) { return b.passed; }).length;
  var matchCount = scored.filter(function(b) { return b.matched; }).length;
  var total      = scored.length;

  return {
    scored:     scored,
    passCount:  passCount,
    matchCount: matchCount,
    total:      total,
    expectedTotal: expected.length,
  };
}
```

---

## Deliverable 2: Update `runSubmit()` to post the Sprint Review to Teams

Find the existing `runSubmit()` function in `src/os-core.js`.
After the existing `showResultModal(result)` call, add code to post the sprint review
to the Teams app window via EventBus.

```javascript
function runSubmit() {
  // ... existing scoring and modal code (keep it as-is) ...

  // NEW: also post the Sprint Review to the Teams app window
  var reviewResult = scoreSubmission(
    state.capstoneScenarioId || "capstone-001",
    state.bugsLogged
  );

  var bus = window.QA_OS && window.QA_OS.EventBus;
  if (bus && bus.postToAllApps) {
    bus.postToAllApps({
      type:   "SPRINT_REVIEW",
      result: reviewResult,
    });
  }
}
```

Place this addition at the END of the existing `runSubmit()` function.
Do not remove or reorder any existing code.

---

## Deliverable 3: Sprint Review thread renderer in `apps/teams.html`

In `apps/teams.html`, add a handler for the `SPRINT_REVIEW` message type
inside the existing `window.addEventListener("message", ...)` block.

```javascript
if (msg.type === "SPRINT_REVIEW" && msg.result) {
  renderSprintReview(msg.result);
}
```

Implement `renderSprintReview(result)`:

```javascript
function renderSprintReview(result) {
  var container = document.getElementById("teams-messages");
  if (!container) return;

  // ── Divider ──────────────────────────────────────────────────────────────
  var divider = document.createElement("div");
  divider.className = "teams-divider";
  divider.innerHTML = '<span>Sprint Review — started now</span>';
  container.appendChild(divider);

  // ── QA Lead opening message ───────────────────────────────────────────────
  appendTeamsMessage(container, {
    sender:   "Elyse Hannah (QA Lead)",
    avatar:   "EH",
    avatarBg: "#0078d4",
    time:     "Just now",
    body:     "Alright, let's do the sprint review. You submitted **" + result.total +
              " bug report" + (result.total !== 1 ? "s" : "") + "**. I'll go through each one.",
  });

  // ── Per-bug review messages ───────────────────────────────────────────────
  if (result.total === 0) {
    appendTeamsMessage(container, {
      sender:   "Elyse Hannah (QA Lead)",
      avatar:   "EH",
      avatarBg: "#0078d4",
      time:     "Just now",
      body:     "❓ No bug reports were filed. Use the ADO app to log defects before submitting.",
    });
  }

  result.scored.forEach(function(bug) {
    var lines = [];

    // Bug heading
    lines.push("**Bug Report " + bug.index + ": \"" + bug.title + "\"**");

    // Per-criterion feedback
    lines.push(
      (bug.checks.title    ? "✅" : "❌") + " Title: " +
      (bug.checks.title    ? "Clear and descriptive" : "Too vague — describe the specific defect, not just the area")
    );
    lines.push(
      (bug.checks.severity ? "✅" : "❌") + " Severity: " +
      (bug.checks.severity ? bug.severity : "Must be in format '1 - Critical', '2 - High', etc.")
    );
    lines.push(
      (bug.checks.acRef    ? "✅" : "❌") + " AC Reference: " +
      (bug.checks.acRef    ? bug.acRef + (bug.matched ? " ✔ matches known defect" : " (format correct)") : "Must reference a specific AC, e.g. 'AC-2.1'")
    );
    lines.push(
      (bug.checks.steps    ? "✅" : "❌") + " Steps to Reproduce: " +
      (bug.checks.steps    ? "Provided" : "Missing — the developer needs numbered steps to reproduce this")
    );

    // Verdict
    lines.push(bug.passed ? "→ **Accepted ✅**" : "→ **Needs revision ⚠️** — address the issues above and resubmit");

    appendTeamsMessage(container, {
      sender:   "Elyse Hannah (QA Lead)",
      avatar:   "EH",
      avatarBg: "#0078d4",
      time:     "Just now",
      isBot:    false,
      body:     lines.join("\n"),
    });
  });

  // ── Summary message ───────────────────────────────────────────────────────
  var summaryLines = [];
  summaryLines.push(
    "**Summary:** " + result.passCount + " of " + result.total +
    " report" + (result.total !== 1 ? "s" : "") + " accepted."
  );
  if (result.matchCount > 0) {
    summaryLines.push(
      "You identified **" + result.matchCount + " of " + result.expectedTotal +
      "** known defects in this scenario."
    );
  }
  if (result.passCount === result.total && result.total > 0) {
    summaryLines.push("Great work! Your reports are publication-ready. 🎉");
  } else if (result.passCount === 0 && result.total > 0) {
    summaryLines.push(
      "Don't be discouraged — review the AC Panel and try the scenario again. " +
      "Quality bug reports are a skill that takes practice."
    );
  } else {
    summaryLines.push("Good effort. Refine the flagged reports and you'll be there.");
  }
  summaryLines.push("Check the result screen for your full score and certificate status.");

  appendTeamsMessage(container, {
    sender:   "Elyse Hannah (QA Lead)",
    avatar:   "EH",
    avatarBg: "#0078d4",
    time:     "Just now",
    body:     summaryLines.join("\n"),
  });

  // Scroll to bottom
  container.scrollTop = container.scrollHeight;

  // Switch sidebar to show #sprint-review channel selected (optional visual touch)
  var generalItem = document.querySelector(".teams-channel-item.active");
  if (generalItem) generalItem.classList.remove("active");
  var reviewItem = document.getElementById("teams-channel-sprint-review");
  if (reviewItem) reviewItem.classList.add("active");
}
```

#### Helper: `appendTeamsMessage(container, msg)`

Re-use or refactor the `renderThread()` single-message logic from C-7 into a shared helper:

```javascript
function appendTeamsMessage(container, msg) {
  var el = document.createElement("div");
  el.className = "teams-msg" + (msg.isBot ? " teams-msg--bot" : "");

  var avatar = document.createElement("div");
  avatar.className = "teams-avatar";
  avatar.textContent = msg.avatar || "??";
  avatar.style.background = msg.avatarBg || "#5b5fc7";

  var body = document.createElement("div");
  body.className = "teams-msg-body";

  var header = document.createElement("div");
  header.className = "teams-msg-header";
  header.innerHTML =
    '<span class="teams-msg-sender">' + escapeHtml(msg.sender) + '</span>' +
    '<span class="teams-msg-time">' + escapeHtml(msg.time) + '</span>';

  var text = document.createElement("div");
  text.className = "teams-msg-text";
  // Support newlines in body: split on \n and wrap each in <p>
  var lines = (msg.body || "").split("\n");
  text.innerHTML = lines.map(function(line) {
    return "<p>" + parseSimpleMd(line.trim()) + "</p>";
  }).join("");

  body.appendChild(header);
  body.appendChild(text);
  el.appendChild(avatar);
  el.appendChild(body);
  container.appendChild(el);
}
```

#### Divider CSS

Add this to the `<style>` block in `apps/teams.html`:

```css
.teams-divider {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px 4px;
  font-size: 11px;
  color: var(--teams-timestamp, #8e8ea0);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.teams-divider::before,
.teams-divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--teams-border, #3d3c52);
}

/* Multi-line message body */
.teams-msg-text p {
  margin: 0 0 4px;
}
.teams-msg-text p:last-child {
  margin-bottom: 0;
}
```

#### Optional: Add `#sprint-review` channel to sidebar

In the Teams sidebar HTML (from C-6), add a second channel item below `#General`:

```html
<div class="teams-channel-item" id="teams-channel-sprint-review">
  # sprint-review
</div>
```

This channel is not clickable — it appears when the review is posted.
You may leave it hidden initially (`display:none`) and show it when `renderSprintReview()` runs.

---

## What NOT to Change

- Do not modify `build.js`
- Do not modify `os.css`
- Do not touch the Academy files (`capstone.html`, lesson HTML files)
- Do not remove the existing `showResultModal()` call in `runSubmit()` — keep both the modal AND the Teams review
- Do not add CDN links or external dependencies

---

## Definition of Done

- [ ] `scoreSubmission(scenarioId, bugsLogged)` function added to `src/os-core.js`
- [ ] `runSubmit()` calls `scoreSubmission()` and posts `SPRINT_REVIEW` to all apps via EventBus
- [ ] Teams `message` listener handles `SPRINT_REVIEW` and calls `renderSprintReview(result)`
- [ ] `renderSprintReview()` appends: divider, opening message, one message per bug, summary message
- [ ] Each bug message shows ✅/❌ for title quality, severity format, AC reference format, and steps
- [ ] `appendTeamsMessage()` helper supports multi-line body (split on `\n`, wrapped in `<p>` tags)
- [ ] `**bold**` shorthand renders as `<strong>` in message bodies
- [ ] Summary message reflects total bugs filed and pass/fail count
- [ ] Result modal from `showResultModal()` still appears as before (Teams review is additive)
- [ ] `node build.js` runs without errors
- [ ] Submitting with 0 bugs shows "No bug reports were filed" message in Teams
- [ ] Submitting with bugs shows per-bug review and final summary in Teams
