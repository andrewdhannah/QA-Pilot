# Sprint G5 — Admin Dashboard Polish
## Gemma Build Prompt

Read GEMMA-STYLE-GUIDE.md before writing any code.
Sprint G3 (Academy Visual Refresh) should be complete before this sprint.

---

## Context

This is the QA Onboarding Training Platform.
Stack: pure HTML/CSS/JS, no frameworks, no CDN links.
CSS tokens: css/main.css. Data layer: IndexedDB via js/db.js.

`admin/dashboard.html` was recently consolidated to a single page with five
in-page tabs. It is functional but visually inconsistent with the student-
facing pages. This sprint brings it up to the same quality bar.

Key admin sections to polish:
1. **Students tab** — expandable rows with progress data, quiz scores, time
   spent, and Reset Password. Add colour-coded progress indicators.
2. **Bug Lab tab** — bug toggle checkboxes. Add live preview of which bugs
   are active, make the save state more obvious.
3. **Overall layout** — consistent topbar, sidebar nav, tab design.

Do NOT touch: js/db.js, js/app.js, data/ files.
Do NOT change CSS tokens in css/main.css — only add rules at end.

---

## Deliverable 1: Bug Lab tab — Save state + active bug preview

### Problem
When an admin toggles bugs and hits Save, the page just shows a generic toast.
There is no visual indicator of which bugs are "live" vs "off".

### Solution
After saving, each toggle row should show a coloured status chip:

```javascript
// After saveSetting('activeBugs', JSON.stringify(checked)) resolves:
// Re-render each bug row with a status chip
Object.keys(bugConfig).forEach(function(bugId) {
  var row = document.querySelector('[data-bug-id="' + bugId + '"]');
  if (!row) return;
  var isOn = checked[bugId] === true;
  var chip = row.querySelector('.bug-status-chip');
  if (chip) {
    chip.textContent = isOn ? 'Active' : 'Off';
    chip.className   = 'bug-status-chip ' + (isOn ? 'chip-active' : 'chip-off');
  }
});
```

Add to `css/main.css`:
```css
/* Bug Lab status chips */
.bug-status-chip {
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 999px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.bug-status-chip.chip-active { background: #fef3c7; color: #92400e; }
.bug-status-chip.chip-off    { background: var(--color-bg); color: var(--color-ink-muted); }
```

Also add a summary banner at the top of the Bug Lab tab showing how many
bugs are currently active:

```html
<div class="bug-lab-summary" id="bug-lab-summary">
  <span id="bug-active-count">0</span> bugs currently active
</div>
```

### Bug fix: saving uses correct key
Confirm the Save button calls:
```javascript
saveSetting('activeBugs', JSON.stringify(checked))
```
NOT `saveSetting('bugToggles', ...)` — the key must be `'activeBugs'` to
match what `getBugToggles()` in db.js reads. (This was fixed in a prior
sprint but verify it is consistent throughout the tab.)

---

## Deliverable 2: Students tab — Progress indicators

Each expandable student row shows:
- Overall course progress as a percentage pill
- Quiz scores per lesson (small badge per lesson)
- Certificate status with a green check or grey dash

Add progress calculation:
```javascript
function calcProgress(progress) {
  if (!progress) return 0;
  var lessons = ['lesson-1', 'lesson-2', 'lesson-3', 'lesson-4'];
  var done = (progress.lessonsComplete || []).filter(function(id) {
    return lessons.includes(id);
  }).length;
  return Math.round((done / lessons.length) * 100);
}
```

Lesson quiz score badges: show `progress.quizResults['lesson-N'].percentage`
or `--` if not attempted. Use colour coding: ≥70% = green, <70% = orange,
not attempted = grey.

Certificate status: check `progress.certificateAwarded || progress.certificateEarned`.

---

## Deliverable 3: Topbar + tab design consistency

The admin topbar should match the student pages:
```html
<header class="topbar">
  <div class="topbar-left">
    <span class="topbar-brand">QA Pilot Admin</span>
  </div>
  <div class="topbar-right">
    <span class="text-sm" style="color: var(--color-ink-muted);">Administrator</span>
    <a href="index.html" class="btn btn-ghost text-xs">Sign Out</a>
  </div>
</header>
```

The tab buttons should use a consistent style — active tab has a bottom
border in `--color-primary` and `font-weight: bold`. This is likely already
present but verify it matches the student-side tab pattern.

---

## Definition of Done

- [ ] Bug Lab shows status chips (Active/Off) for each bug after save
- [ ] Bug Lab summary banner shows count of active bugs and updates on save
- [ ] `saveSetting('activeBugs', ...)` is confirmed as the save key (not 'bugToggles')
- [ ] Student rows show overall progress % and per-lesson quiz scores
- [ ] Certificate status shows correctly using `certificateAwarded || certificateEarned`
- [ ] Admin topbar is consistent with student-facing topbar style
- [ ] No regressions — all 5 tabs still load and save data correctly
- [ ] db.js and app.js untouched
