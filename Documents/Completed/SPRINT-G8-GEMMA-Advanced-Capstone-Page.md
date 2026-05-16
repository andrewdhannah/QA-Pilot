# Sprint G8 — Advanced Capstone Page
## Gemma Build Prompt

Read GEMMA-STYLE-GUIDE.md before writing any code.
**Prerequisites:** G-7 (Lesson 5) must be merged. Sprints C-6, C-7, C-8, C-9 must be merged
and the desktop build must be current (`node build.js` run after all OS sprints).

---

## Context

The QA Pilot Academy has a capstone page (`capstone.html`) that embeds the OS simulator
as a full-screen iframe for the standard (beginner) scenario (`case-001`).

This sprint creates `capstone-2.html` — the **Advanced Capstone** for the new advanced track.
It uses `case-002` (three hidden bugs, Teams-delivered scenario brief, stricter ADO validation).

`capstone-2.html` follows the same pattern as `capstone.html`:
- Read `capstone.html` carefully before writing a single line.
- The OS is embedded via `getOSContent()` which returns the built `dist.html` as a template literal.
- Communication between the Academy page and the OS uses postMessage.

**Important:** The `getOSContent()` function and its BUILD:OS_START / BUILD:OS_END markers
must be copied from `capstone.html` exactly. The build script auto-syncs this content.

---

## Deliverable 1: `capstone-2.html`

Create `capstone-2.html` in the project root.

### Key differences from `capstone.html`

| Property | capstone.html (beginner) | capstone-2.html (advanced) |
|--|--|--|
| Scenario ID | `capstone-001` | `case-002` |
| Page title | "QA Pilot Academy — Capstone" | "QA Pilot Academy — Advanced Capstone" |
| Intro text | Beginner brief | Advanced brief (see below) |
| Access gate | None | Requires `qa-lesson5-complete` in localStorage |
| Bug target | 2 bugs | 3 bugs |

### Access gate

At the top of the page's `<script>` block (before anything else runs), check the prerequisite:

```javascript
(function() {
  var ready = false;
  try { ready = localStorage.getItem("qa-lesson5-complete") === "1"; } catch(e) {}
  if (!ready) {
    // Redirect to course page with a message
    window.location.href = "course.html?locked=lesson5";
  }
})();
```

### Advanced Capstone brief (shown before the OS loads)

Display a brief introduction panel above (or overlaying) the OS iframe on first load.
The panel disappears once the trainee clicks "Begin Assessment".

Content:

```
Advanced QA Capstone — Case-002

You are a Junior QA Analyst at Northgate Logistics.
A new high-priority case has arrived: CASE-00189 — Customer Portal Login Failure.

Your QA Lead has assigned it to you via Teams. Open the Teams app first
to read your briefing, then investigate the case in Dynamics CRM and
reference the Acceptance Criteria panel.

Your task:
  • Find all defects in the case data
  • File a detailed ADO bug report for each defect
  • Reference the correct AC for each bug
  • Submit when you are confident you have found everything

Target: 3 bugs · Pass mark: 2/3 accepted reports

The QA Lead will review your work in Teams when you submit.
Good luck.
```

Style the intro panel to match the Academy's existing design language.
Include: case ID badge, bullet list of task steps, a target/pass-mark line, and a CTA button.

### Session initialisation

When the trainee clicks "Begin Assessment", the page writes the capstone session to localStorage
(same pattern as `capstone.html`) then embeds the OS:

```javascript
function beginAssessment() {
  var session = {
    scenarioId:  "case-002",
    caseId:      "capstone-2-" + Date.now(),
    role:        "junior",
    startedAt:   new Date().toISOString(),
    bugToggles: {
      "status-junior-escalated":  true,
      "escalation-reason-blank":  true,
      "future-date-allowed":      true,
    },
  };

  try {
    localStorage.setItem("qa-capstone-session", JSON.stringify(session));
  } catch(e) {}

  // Hide the intro panel and show the OS iframe
  document.getElementById("capstone2-intro").style.display = "none";
  document.getElementById("capstone2-frame-wrap").style.display = "block";
  loadOSFrame();
}
```

### `loadOSFrame()` — same pattern as `capstone.html`

Read `capstone.html` for the exact iframe setup, srcdoc loading, and postMessage listener.
The OS iframe should fill the remaining viewport height after the Academy header.

Copy the following from `capstone.html` exactly (do not paraphrase or rewrite):
- The `getOSContent()` function with its `/* BUILD:OS_START */` and `/* BUILD:OS_END */` markers
- The `window.addEventListener("message", ...)` handler that listens for `CAPSTONE_COMPLETE`
  and redirects to the result/certificate page
- The iframe `srcdoc` loading pattern

The only change: the event listener should redirect to `certificate.html?scenario=case-002`
(or however `capstone.html` handles completion — match its pattern and adapt the scenario ID).

### Result handling

When the OS posts `CAPSTONE_COMPLETE`, record the result to IndexedDB (same as capstone.html)
and redirect to the certificate page. Read `capstone.html` for the exact implementation.

---

## Deliverable 2: Update `course.html` for the Advanced Capstone entry

Add the Advanced Capstone entry to the "Advanced Track" section added in G-7.

The entry should:
- Be visually locked (greyed out, lock icon) if `qa-lesson5-complete` is NOT in localStorage
- Be visually unlocked and clickable if the flag IS set
- Link to `capstone-2.html` when unlocked
- Show: "Advanced Capstone — Case-002: Customer Portal Access Failure"
- Subtitle: "3 bugs · Teams-delivered brief · Strict ADO validation"

Check the lock state with JavaScript on page load (same try/catch pattern as the lesson).

```javascript
(function() {
  var lesson5Done = false;
  try { lesson5Done = localStorage.getItem("qa-lesson5-complete") === "1"; } catch(e) {}

  var advCapstone = document.getElementById("course-adv-capstone");
  if (advCapstone) {
    if (lesson5Done) {
      advCapstone.classList.remove("course-item--locked");
      advCapstone.querySelector("a").href = "capstone-2.html";
    }
    // If not done, the item stays locked — link href remains "#" or is absent
  }
})();
```

---

## Deliverable 3: Handle `?locked=lesson5` in `course.html`

When `capstone-2.html` redirects a gated trainee to `course.html?locked=lesson5`,
show a brief notice at the top of the course page:

```javascript
(function() {
  var params = new URLSearchParams(window.location.search);
  if (params.get("locked") === "lesson5") {
    var notice = document.getElementById("course-locked-notice");
    if (notice) {
      notice.textContent = "Complete Lesson 5 to unlock the Advanced Capstone.";
      notice.style.display = "block";
    }
  }
})();
```

Add the notice element near the top of the course page content area:

```html
<div id="course-locked-notice"
     style="display:none; background:#fff4ce; border:1px solid #f0c000; border-radius:4px;
            padding:10px 14px; font-size:13px; color:#6b4c00; margin-bottom:16px;">
</div>
```

---

## What NOT to Change

- Do not modify `capstone.html` — `capstone-2.html` is a new file
- Do not modify any lesson files (lesson-1 through lesson-5)
- Do not modify `index.html` (login page)
- Do not change the `getOSContent()` function — copy it exactly from `capstone.html`
- Do not add CDN links or external assets

---

## Definition of Done

- [ ] `capstone-2.html` exists in the project root
- [ ] Access gate redirects to `course.html?locked=lesson5` if `qa-lesson5-complete` is not set
- [ ] Intro panel shows the advanced brief with case ID, task steps, target/pass-mark, and Begin button
- [ ] "Begin Assessment" writes the correct session to localStorage (scenarioId: "case-002", 3 active bugs)
- [ ] Intro panel hides and OS iframe shows after Begin is clicked
- [ ] `getOSContent()` and BUILD:OS_START/OS_END markers are present and identical to `capstone.html`
- [ ] OS iframe loads the simulator with `case-002` session active
- [ ] `CAPSTONE_COMPLETE` message triggers result recording and redirect to certificate
- [ ] `course.html` shows the Advanced Capstone entry in the Advanced Track section
- [ ] Entry is visually locked when `qa-lesson5-complete` is not set; unlocked and linked when it is
- [ ] `course.html` shows the locked notice when redirected from `capstone-2.html` with `?locked=lesson5`
- [ ] No CDN links, no external assets, fully self-contained
