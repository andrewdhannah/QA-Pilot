# Scenario Expansion — LLM Prompt Templates
*Feed these prompts to a local LLM to generate rich training content for QA Pilot Academy.*

---

## How to Use

1. Copy the **System Prompt** block at the top into your LLM's system/context window.
2. Copy the **User Prompt** for whichever scenario you want to expand.
3. Paste the output back into the relevant `trainingSteps` array in `capstone-2.html`.
4. Step `body` fields should be plain text (no markdown — the app renders `\n` as line breaks).
5. Keep each step to roughly 60–120 words in the `body`. Hints should be 1–2 sentences.

---

## System Prompt (use for all scenarios)

```
You are a training content writer for a QA analyst onboarding platform.

The platform is a simulated Windows desktop (called QA Pilot OS) running in a browser.
Students are new or junior QA analysts learning to investigate CRM cases and file bug reports.
The OS contains these apps: Dynamics CRM, Azure DevOps (ADO), Teams, AC Panel (Acceptance Criteria), QOutlook.

Your job is to write guided training steps — NOT quiz questions, NOT multiple choice.
Each step walks the student through one action in the scenario.

Rules for each step:
- title: "Step N of N — [Short verb phrase describing the action]"
- body: 2–5 short paragraphs. Explain WHAT to do, WHERE to look, and WHY it matters.
  Use plain text. Line breaks with \n. No markdown.
- hint: 1–2 sentences. Point to the relevant AC reference or explain the key insight.

Write in a friendly, teacher tone — encouraging but professional.
Assume the student is competent but new to formal QA methodology.
Do NOT reveal the answer directly — guide the student to notice the issue themselves.
```

---

## Scenario Prompts

---

### Scenario 1: case-001 — Beginner Case Investigation

**Goal:** Teach a student to open a CRM case, check fields against Acceptance Criteria, and file bugs.
**Bugs to find:** STATUS_JUNIOR_CLOSED, FUTURE_DATE_ALLOWED
**Key ACs:** AC-2.1 (junior cannot close), AC-1.3 (no future dates)
**Apps used:** Dynamics CRM, AC Panel, ADO
**Target steps:** 6

```
Write 6 training steps for the following scenario in QA Pilot Academy:

SCENARIO: case-001 — Junior Case Investigation (Beginner)

CONTEXT:
The student has just opened the QA Pilot OS. Their role is Junior Analyst.
A CRM case (CASE-00247) is pre-loaded in Dynamics. The case has two defects:
1. Status is set to "Closed" — Junior analysts cannot close cases (AC-2.1)
2. Date Opened is set 3 days in the future (AC-1.3)

APPS AVAILABLE: Dynamics CRM, AC Panel, Azure DevOps (ADO)

STEPS TO COVER:
1. Orient the student — what is their goal, what apps will they use
2. Open Dynamics CRM — what to look at first (header fields)
3. Check the Status field — guide them to notice the violation without stating it
4. Open the AC Panel — how to use it to validate what they found
5. Check the Date Opened field — guide them to compare with today's date
6. File ADO reports — how to structure each bug report with title, severity, AC ref

Write each step as:
{
  title: "Step N of 6 — [verb phrase]",
  body: "[plain text, \n for line breaks, 50-100 words]",
  hint: "[1-2 sentence insight pointing to AC ref]"
}
```

---

### Scenario 2: bug-001 — Beginner Bug Report Practice

**Goal:** Teach a student the structure of a good ADO bug report from scratch.
**Type:** Practice filing — no investigation needed, scenario data is pre-loaded.
**Key concepts:** Bug title format, Severity levels, Repro steps, Expected vs Actual
**Apps used:** ADO only
**Target steps:** 6

```
Write 6 training steps for the following scenario in QA Pilot Academy:

SCENARIO: bug-001 — Bug Report Filing Practice (Beginner)

CONTEXT:
The student does NOT need to investigate — the bug scenario is given to them:
  - Issue: A customer cannot complete an online payment. Checkout fails at confirmation.
  - Severity: 2 - High (major feature broken, no workaround)
  - App: ADO (Azure DevOps)

STEPS TO COVER:
1. Explain what a bug report is and why it needs to be structured
2. Write a clear title using [Area] format — give examples of good and bad titles
3. Choose the correct Severity — explain the 4 levels, ask student to pick one
4. Write numbered Repro Steps — explain what makes steps good vs bad
5. Fill in Expected vs Actual — explain the purpose and give example text
6. Review checklist and submit — summarise what a complete report looks like

Write each step as:
{
  title: "Step N of 6 — [verb phrase]",
  body: "[plain text, \n for line breaks, 60-120 words]",
  hint: "[1-2 sentence teaching insight]"
}

Style: Friendly teacher. Don't give away the answers — guide the student to arrive at them.
```

---

### Scenario 3: case-002 — Advanced Case Investigation

**Goal:** Teach a student to investigate a more complex case with 3 AC violations.
**Bugs to find:** STATUS_ESCALATED_BY_JUNIOR, ESCALATION_REASON_BLANK, FUTURE_DATE_ALLOWED
**Key ACs:** AC-2.1 (escalated by junior), AC-4.1 (escalation reason required), AC-3.2 (no future dates)
**Apps used:** Teams, Dynamics CRM, ADO
**Target steps:** 7

```
Write 7 training steps for the following scenario in QA Pilot Academy:

SCENARIO: case-002 — Customer Portal Access Failure (Advanced)

CONTEXT:
Student role: Junior QA Analyst.
They receive a Teams message from Elyse Hannah (QA Lead) assigning CASE-00189.
The case has 3 defects in Dynamics CRM:
1. Status = "Escalated" — Junior analysts cannot set Escalated status (AC-2.1)
2. Escalation Reason field is blank — Required when status is Escalated (AC-4.1)
3. Date Opened = future date (AC-3.2)

APPS AVAILABLE: Teams, Dynamics CRM, ADO

STEPS TO COVER:
1. Read the Teams briefing — what does the QA Lead tell them?
2. Open Dynamics CRM — what are the first fields to examine?
3. Check the Status field — is this status allowed for a Junior? Why?
4. Check the Escalation Reason — what rule applies when Status = Escalated?
5. Check the Date Opened — same defect class as Beginner case, reinforce the pattern
6. File all 3 ADO reports — what severity for each? (reference AC numbers)
7. Review and submit — self-review checklist before submitting

Write each step as:
{
  title: "Step N of 7 — [verb phrase]",
  body: "[plain text, \n for line breaks, 60-120 words]",
  hint: "[1-2 sentence insight with AC reference]"
}

Style: This is an Advanced scenario — the student has already done the Beginner case.
Refer back to what they learned in case-001 to reinforce pattern recognition.
```

---

### Scenario 4: case-003 — Expert Case Investigation

**Goal:** Teach a student to find 4 defects using Teams + AC Panel + Dynamics, without being hand-held.
**Bugs to find:** OWNER_UNASSIGNED, STATUS_JUNIOR_CLOSED, PRIORITY_MISMATCH, FUTURE_DATE_ALLOWED
**Key ACs:** AC-1.1 (owner required), AC-2.1 (junior cannot close), AC-3.2 (priority vs financial impact), AC-1.3 (no future dates)
**Apps used:** Teams, Dynamics CRM, AC Panel, ADO
**Target steps:** 7

```
Write 7 training steps for the following scenario in QA Pilot Academy:

SCENARIO: case-003 — Invoice Processing Failure, Northgate Logistics (Expert)

CONTEXT:
Student role: Junior QA Analyst.
They receive a Teams message from Sarah Chen (QA Lead) assigning CASE-00247.
This is an expert-level scenario — 4 defects, one of which requires reading the case
description to notice a mismatch (priority vs financial value).
Defects:
1. Case Owner = blank — Required field (AC-1.1)
2. Status = "Closed" — Junior analysts cannot close cases (AC-2.1)
3. Priority = "Low" — Case involves £42,000 invoice, should be Critical (AC-3.2)
4. Created Date = future date (AC-1.3)

APPS AVAILABLE: Teams, AC Panel, Dynamics CRM, ADO

STEPS TO COVER:
1. Read the Teams briefing — note the AC references Sarah flagged
2. Open the AC Panel alongside Dynamics — how to use snap layout
3. Check Case Owner — first field to verify (AC-1.1)
4. Check Status — same pattern as case-001, reinforce it
5. Read the case description + check Priority — this is the non-obvious bug
6. Check Created Date — reinforce date validation pattern
7. File all 4 ADO reports with correct severity, title, and AC refs

Write each step as:
{
  title: "Step N of 7 — [verb phrase]",
  body: "[plain text, \n for line breaks, 60-120 words]",
  hint: "[1-2 sentence insight with AC reference]"
}

Style: Expert level — the student has completed Beginner and Advanced scenarios.
Minimal hand-holding. Teach them to form their own methodology.
For the Priority step, ask questions rather than telling them — guide them to read the
case description and apply the AC rule themselves.
```

---

## Output Format Reminder

Paste LLM output as a JavaScript array into the `trainingSteps` field of the relevant scenario object in `capstone-2.html`:

```javascript
trainingSteps: [
  {
    title: "Step 1 of 7 — Read your Teams briefing",
    body:  "Open Teams...",
    hint:  "Sarah flagged AC-1.1...",
  },
  // ... more steps
],
```

Escape any backslashes in the `body` string: use `\\n` not `\n` since the file is JS inside HTML.

---

## Notes for Future Scenarios

When adding a new scenario, the minimum required fields in `trainingMeta` are:

```javascript
trainingMeta: {
  title:         "Short display title for the card",
  difficulty:    "Beginner" | "Advanced",
  description:   "1-2 sentence card description",
  estimatedMins: 10,
}
```

And `trainingSteps` must be an array of `{ title, body, hint }` objects.
If `trainingSteps` is missing, the training app falls back to `case-001`'s steps — wrong content!
