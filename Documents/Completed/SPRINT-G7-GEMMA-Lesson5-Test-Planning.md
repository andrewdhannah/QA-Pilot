# Sprint G7 — Lesson 5: Test Planning & Triage
## Gemma Build Prompt

Read GEMMA-STYLE-GUIDE.md before writing any code.
All previous sprints can be complete or in progress — this sprint only creates new files.

---

## Context

This is the QA Pilot Academy — an offline lesson platform for new QA analysts.
Stack: pure HTML/CSS/JS. No frameworks, no CDN links. Fully self-contained.
The Academy lives in the project root (`index.html`, `course.html`, `lesson-1.html` … `lesson-4.html`).

This sprint adds **Lesson 5** — the gateway to advanced QA training. It teaches three concepts
that underpin the harder capstone scenario (`case-002`):

1. Planned testing vs exploratory testing — when to use each
2. Bug triage and severity — what makes a defect Sev 1 vs Sev 4
3. Traceability — why every bug must reference a specific acceptance criterion

The lesson must feel practical, not like a Microsoft marketing page.
Real talk, concrete examples, slight humour where it fits. Elyse (Lead QA Tester) is the audience.

---

## Deliverable 1: `lesson-5.html`

Create `lesson-5.html` in the project root (same folder as `lesson-1.html` to `lesson-4.html`).
Match the visual style of the existing lesson pages exactly — same header, nav, progress bar pattern.

Read `lesson-1.html` or `lesson-4.html` first to identify:
- The CSS classes used for section headings, callout boxes, tips, and quizzes
- The HTML structure for the lesson header (title, progress indicator, lesson number)
- The footer/navigation buttons (Previous / Next / Back to Course)

Match those patterns exactly. Do not invent new class names when existing ones cover the need.

---

## Lesson content

### Page title and header

```
Lesson 5 — Test Planning & Bug Triage
"Writing bugs that actually get fixed."
```

---

### Section 1: Two ways to test

**Heading:** Exploratory Testing vs Planned Testing

Explain the difference conversationally:

- **Exploratory testing**: You open the app, poke around, and look for things that feel wrong.
  No script, no checklist. You're using your instincts and domain knowledge.
  Good for: early stages, new features, "does this even work?" checks.

- **Planned testing (test cases)**: You have a list of specific steps and expected outcomes.
  You follow them in order and record pass/fail for each step.
  Good for: regression testing, acceptance criteria validation, repeatable proof of quality.

Use a two-column comparison card (or styled table) showing:

| | Exploratory | Planned |
|--|--|--|
| Prep time | Low | Higher |
| Coverage | Broad, intuitive | Specific, documented |
| Repeatability | Variable | Consistent |
| When to use | Discovery, new features | Regression, sign-off |
| Risk | May miss edge cases | May miss unexpected behaviour |

Add a callout box (tip style):
> "In practice, good QA analysts do both. You explore first to understand the system,
> then you write test cases to prove it works for every scenario that matters."

---

### Section 2: Writing a test case

**Heading:** What's in a test case?

Explain the three parts: preconditions, steps, expected result.

Show a concrete example using the QA Pilot training scenario:

**Test Case: Junior Investigator — Status restrictions**

| Field | Value |
|--|--|
| Precondition | User is logged in with Junior Investigator role |
| Step 1 | Open Dynamics CRM and navigate to Case CASE-00142 |
| Step 2 | Click the Status dropdown |
| Step 3 | Attempt to select "Escalated" from the options |
| Expected result | "Escalated" option is not available — the field is restricted to Active and Pending for Junior role |
| Actual result | (fill in during testing) |
| Pass / Fail | (fill in during testing) |

Add a callout box:
> "Notice 'Actual result' is blank when you write the test case.
> You fill it in during testing. If actual ≠ expected, you've found a bug."

---

### Section 3: Bug triage and severity

**Heading:** Not all bugs are created equal

Explain severity levels 1–4. Keep it punchy, not a textbook:

| Severity | Label | Plain English |
|--|--|--|
| 1 — Critical | 🔴 | System is down or data is lost. Stops everything. Fix NOW. |
| 2 — High | 🟠 | Major feature broken, no workaround. Most users affected. |
| 3 — Medium | 🟡 | Feature partially works, or a workaround exists. |
| 4 — Low | 🟢 | Cosmetic issue, spelling error, minor annoyance. |

Add a **triage exercise**: show three bug descriptions and ask the trainee to mentally
assign a severity before revealing the answer. Use a styled reveal (click to show answer).

**Bug A:** "The Date Opened field accepts future dates — a case can be 'opened' on 1 January 2099."
→ Answer: Severity 3 — Medium. Data integrity issue, workaround is careful manual entry.

**Bug B:** "Case notes are deleted when the page is refreshed — all entered text is lost."
→ Answer: Severity 2 — High. Major data loss, no workaround, affects every user.

**Bug C:** "The Dynamics CRM logo appears slightly blurry on high-DPI screens."
→ Answer: Severity 4 — Low. Cosmetic, no functional impact.

Implement the reveal as a `<details><summary>` element (no JavaScript needed):
```html
<details>
  <summary>Reveal answer</summary>
  <p>Severity 3 — Medium. ...</p>
</details>
```

---

### Section 4: Traceability — the "so what?" of bug reports

**Heading:** Why every bug needs an AC reference

Explain in plain language:

- An acceptance criterion (AC) defines what "correct" looks like.
- Without an AC reference, a bug report is just an opinion: "I don't like this."
- With an AC reference, it's evidence: "This violates AC-2.1 which says Junior users cannot escalate cases."
- Developers prioritise bugs with clear AC references because they know exactly what 'fixed' looks like.
- QA leads accept bug reports that are traceable. They reject ones that aren't.

Show a **bad vs. good** example pair using the `good`/`bad` styled boxes from the existing lesson pages:

❌ **Bad:** "Status is broken"
✅ **Good:** "Junior Investigator can set case Status to Escalated — AC-2.1 violation"

❌ **Bad:** "Date field issue"
✅ **Good:** "Date Opened accepts future dates — should be blocked per AC-3.2"

Add a tip callout:
> "When in doubt: [what happened] + [what should have happened] + [which AC it violates].
> That's a complete bug title."

---

### Section 5: Quick reference card

**Heading:** Triage checklist — before you file a bug

A styled checklist box the trainee can use as a mental model:

- [ ] Does the title describe the specific defect (not just the area)?
- [ ] Have I assigned a severity level using the 1–4 scale?
- [ ] Have I referenced the specific AC that is violated?
- [ ] Have I written numbered steps that any developer can follow to reproduce this?
- [ ] Is this actually a defect — or is it working as intended?

Style this as a visual checklist (not a form — just styled `<ul>` with checkbox-style bullets).

---

### Quiz (end of lesson)

3-question quiz, matching the quiz style from existing lesson pages:

**Q1:** A new feature has just been built and no one has tested it yet. What type of testing should you start with?
- A) Planned testing with detailed test cases
- B) Exploratory testing ← correct
- C) Automated regression testing
- D) User acceptance testing

**Q2:** A bug is filed: "The Submit button does not respond when clicked — no error message, no action taken. Reproduces 100% of the time." What severity is this?
- A) 4 — Low
- B) 3 — Medium
- C) 2 — High ← correct
- D) 1 — Critical

**Q3:** Which bug title is most useful to a developer?
- A) "Status is wrong"
- B) "The dropdown is broken again"
- C) "Dynamics form doesn't save"
- D) "Junior Investigator can set Status to Closed — AC-2.1 violation" ← correct

On 3/3 correct: show a success message and unlock the "Advanced Capstone" button in the course.
On < 3/3: show which answers were wrong and allow retry. Do not reveal correct answers until 3/3 is achieved.

**Unlock mechanism:** On quiz completion (3/3), set a localStorage flag:
```javascript
try { localStorage.setItem("qa-lesson5-complete", "1"); } catch(e) {}
```

---

## Deliverable 2: Update `course.html`

Add Lesson 5 to the lesson list in `course.html`. Read the existing lesson list markup first
and match the pattern exactly. The Lesson 5 entry should:
- Show lesson number, title, and a brief subtitle: "Test Planning & Bug Triage"
- Link to `lesson-5.html`
- Display a lock icon if `qa-lesson5-complete` is not set in localStorage — wait, no:
  Lesson 5 should be accessible immediately (it's a prerequisite for the advanced capstone, not a reward).
  The **Advanced Capstone** entry (added later in G-8) will be the locked one.

Add a visual section divider between Lesson 4 and Lesson 5 labelled:
`Advanced Track — Prerequisites required`

---

## What NOT to Change

- Do not modify any existing lesson files (lesson-1 through lesson-4)
- Do not touch `index.html` (login page) or `capstone.html`
- Do not add CDN links, external fonts, or external images
- Do not change the Academy's colour palette or typography

---

## Definition of Done

- [ ] `lesson-5.html` created — matches the visual style of existing lesson pages exactly
- [ ] All four content sections present: exploratory vs planned, test case anatomy, severity triage, traceability
- [ ] Comparison table renders correctly for both sections that use one
- [ ] Three triage exercises use `<details>`/`<summary>` for reveal — no JavaScript required for reveal
- [ ] Bad/good example pairs use the existing `.bad` and `.good` CSS classes from the lesson styles
- [ ] Quick reference checklist is visually distinct and readable
- [ ] 3-question quiz is functional — correct answer tracking, retry on failure, no answer reveal until 3/3
- [ ] On 3/3 quiz pass, `qa-lesson5-complete` is written to localStorage (wrapped in try/catch)
- [ ] `course.html` updated with Lesson 5 entry and "Advanced Track" section divider
- [ ] Lesson 5 is immediately accessible from the course page (not locked)
- [ ] No CDN links, no external assets, fully self-contained
