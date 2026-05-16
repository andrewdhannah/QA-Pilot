# Sprint G9 — Lesson 4 Quiz Layout Fix
## Gemma Build Prompt

Read GEMMA-STYLE-GUIDE.md before writing any code.
This sprint fixes a single confirmed layout bug in `lesson-4.html`.
No other files need to be changed.

---

## Context

`lesson-4.html` has four display phases, each controlled by JavaScript:

| Phase div | Shown when |
|-----------|-----------|
| `#phase-content` | Lesson chapters (default) |
| `#phase-mock` | Chapter 4 ADO mock exercise |
| `#phase-quiz` | Quiz |
| `#phase-results` | Quiz results |

There is also a **root-level** `<nav class="topbar">` element at the top of `<body>`,
OUTSIDE all phase divs. It is always visible.

The bug: `#phase-quiz` and `#phase-results` each contain their own `<nav class="topbar">`.
When the quiz phase is shown, the root topbar is NOT hidden — so TWO topbars stack at the
top of the page. This pushes all quiz content down, breaks the layout, and makes the
quiz unusable.

The same issue affects `#phase-results`.

`#phase-mock` uses a completely different header (`<header class="ado-header">`),
so it is not affected.

---

## The fix (three small changes)

### Change 1 — Add an `id` to the root topbar

Find the root-level `<nav class="topbar">` (the first one in `<body>`, outside all
phase divs). Add `id="topbar-initial"`:

```html
<!-- BEFORE -->
<nav class="topbar flex justify-between items-center">

<!-- AFTER -->
<nav id="topbar-initial" class="topbar flex justify-between items-center">
```

**Do not change anything else on this element or inside it.**

---

### Change 2 — Hide the root topbar when entering quiz or results

Find the JavaScript function that switches to the quiz phase. It looks like this:

```javascript
document.getElementById('phase-content').style.display = 'none';
document.getElementById('phase-quiz').style.display = 'block';
startQuiz();
```

Add one line to hide the root topbar before showing the quiz:

```javascript
var rootTopbar = document.getElementById('topbar-initial');
if (rootTopbar) rootTopbar.style.display = 'none';

document.getElementById('phase-content').style.display = 'none';
document.getElementById('phase-quiz').style.display = 'block';
startQuiz();
```

Find the function that switches to the results phase (it shows `#phase-results`).
Apply the same fix — hide the root topbar there too:

```javascript
var rootTopbar = document.getElementById('topbar-initial');
if (rootTopbar) rootTopbar.style.display = 'none';

document.getElementById('phase-quiz').style.display = 'none';
document.getElementById('phase-results').style.display = 'block';
```

---

### Change 3 — Restore the root topbar if the user navigates back to lesson content

If there is any "Back to lesson" or navigation that returns to `#phase-content`, restore
the root topbar visibility:

```javascript
var rootTopbar = document.getElementById('topbar-initial');
if (rootTopbar) rootTopbar.style.display = '';

document.getElementById('phase-quiz').style.display = 'none';
document.getElementById('phase-content').style.display = 'block';
```

Only add this if a back-navigation function exists. Do not create new navigation
that wasn't there before.

---

## How to find the right JavaScript

Search for these strings in the `<script>` block at the bottom of `lesson-4.html`:

- `phase-quiz` — finds the quiz transition
- `phase-results` — finds the results transition
- `phase-content` — finds content transitions (to find back-navigation if it exists)
- `startQuiz` — the quiz initialisation function

Read the surrounding code before editing. Understand what each function does.
Make only the three targeted changes above — do not refactor or restructure any logic.

---

## What NOT to Change

- Do not modify any other lesson files
- Do not modify `course.html`, `index.html`, or `capstone.html`
- Do not change the quiz logic, questions, scoring, or results rendering
- Do not change any CSS
- Do not add CDN links or external assets

---

## After the fix is applied

Update `FEATURE-STATUS.md` in the repo root — change this row:

| Row | New status |
|-----|-----------|
| Lesson 4 — Azure DevOps | ✅ |

---

## Definition of Done

- [ ] `id="topbar-initial"` added to the root-level `<nav class="topbar">` in `lesson-4.html`
- [ ] Root topbar is hidden (`display: none`) before `#phase-quiz` is shown
- [ ] Root topbar is hidden (`display: none`) before `#phase-results` is shown
- [ ] Root topbar is restored (`display: ''`) if navigation back to lesson content exists
- [ ] Opening `lesson-4.html`, advancing to the quiz — only ONE topbar is visible
- [ ] Quiz layout is correctly positioned (quiz content not displaced by double-topbar)
- [ ] Proceeding to results — layout remains correct, single topbar from `#phase-results`
- [ ] No other phase is broken — lesson chapters, mock ADO screen unaffected
