# Sprint G3 — Academy Visual Refresh
## Gemma Build Prompt

Read GEMMA-STYLE-GUIDE.md before writing any code.
Sprint C4 (IndexedDB Bridge) does not need to be complete before this sprint.

---

## Context

This is the QA Onboarding Training Platform.
Stack: pure HTML/CSS/JS, no frameworks, no CDN links.
CSS tokens: css/main.css (read this file before writing any CSS).
Data layer: IndexedDB via js/db.js.

The platform has two visual worlds that need to feel like one product:
- The **Academy** (index.html, course.html, lesson-1 to lesson-4, capstone.html)
  — currently clean and functional but flat and generic
- The **OS Desktop** (dist.html embedded in capstone.html)
  — polished, Windows 11-inspired, with Fluent icons and clear visual hierarchy

This sprint upgrades the Academy to match the quality bar of the OS:
- Each lesson gets a distinct color identity
- Lesson pages get chapter hero sections with inline SVG illustrations
- course.html gets richer lesson cards with live progress indicators
- All pages get a consistent, professional topbar

Do NOT touch: js/db.js, js/app.js, data/, admin/, desktop/, certificate.html.
Do NOT add CDN links or external fonts.
Do NOT change CSS variable names or values in css/main.css.
Only ADD new CSS — do not remove existing rules.

---

## Lesson Color System

Add these four lesson-specific accent tokens to the `:root` block in
`css/main.css`. Place them directly after the existing status color block:

```css
/* ── LESSON ACCENT COLOURS ── */
/* Each lesson has a unique hue so students can orient instantly.        */
/* These are used for sidebar borders, chapter hero fills, and badges.   */
--lesson-1-color:        #2563eb;   /* Blue   — Testing 101              */
--lesson-1-light:        #eff6ff;
--lesson-1-border:       #bfdbfe;

--lesson-2-color:        #ea580c;   /* Orange — Bug Reporting            */
--lesson-2-light:        #fff7ed;
--lesson-2-border:       #fed7aa;

--lesson-3-color:        #0891b2;   /* Teal   — CRM Tools                */
--lesson-3-light:        #ecfeff;
--lesson-3-border:       #a5f3fc;

--lesson-4-color:        #7c3aed;   /* Purple — QA Process               */
--lesson-4-light:        #faf5ff;
--lesson-4-border:       #e9d5ff;
```

---

## Deliverable 1: css/main.css — Shared lesson component styles

Add the following new rule blocks to the END of main.css.
Do not modify any existing rules.

```css
/* ── LESSON PAGE COMPONENTS ──────────────────────────────────────────── */

/* Topbar — consistent across all lesson pages and course.html */
.topbar-progress-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--color-ink-muted);
}

.topbar-progress-pip {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-border);
  transition: background 0.2s;
}
.topbar-progress-pip.done { background: var(--color-success); }
.topbar-progress-pip.active { background: var(--color-primary); }

/* Chapter hero — the illustrated header at the top of each chapter */
.chapter-hero {
  display: flex;
  align-items: center;
  gap: var(--space-6);
  padding: var(--space-6) var(--space-8);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-8);
  border: 1px solid var(--color-border);
  position: relative;
  overflow: hidden;
}

.chapter-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.06;
  background: linear-gradient(135deg, currentColor 0%, transparent 70%);
  pointer-events: none;
}

.chapter-hero-icon {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.chapter-hero-icon svg {
  width: 32px;
  height: 32px;
}

.chapter-hero-text { flex: 1; }

.chapter-hero-eyebrow {
  font-size: var(--text-xs);
  font-weight: var(--weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: var(--space-1);
  opacity: 0.75;
}

.chapter-hero-title {
  font-size: var(--text-lg);
  font-weight: var(--weight-bold);
  color: var(--color-ink);
  line-height: var(--leading-tight);
  margin-bottom: var(--space-1);
}

.chapter-hero-sub {
  font-size: var(--text-sm);
  color: var(--color-ink-muted);
  line-height: var(--leading-base);
}

/* Chapter content callout boxes */
.callout {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-md);
  border-left: 3px solid;
  margin: var(--space-6) 0;
}

.callout-icon { font-size: 18px; flex-shrink: 0; line-height: 1.6; }
.callout-body { font-size: var(--text-sm); line-height: var(--leading-base); }
.callout-body strong { display: block; margin-bottom: 2px; }

.callout.tip    { background: var(--color-primary-light); border-color: var(--color-primary); color: #1e40af; }
.callout.warn   { background: var(--color-warning-light); border-color: var(--color-warning); color: #92400e; }
.callout.good   { background: var(--color-success-light); border-color: var(--color-success); color: #14532d; }

/* Quiz UI improvements */
.quiz-option {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-2);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  font-size: var(--text-sm);
}
.quiz-option:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}
.quiz-option.selected {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
  font-weight: var(--weight-medium);
}
.quiz-option.correct  { border-color: var(--color-success); background: var(--color-success-light); }
.quiz-option.incorrect { border-color: var(--color-error);  background: var(--color-error-light); }

/* ── COURSE DASHBOARD — LESSON CARDS ─────────────────────────────────── */

.lesson-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-6);
  display: flex;
  align-items: center;
  gap: var(--space-5);
  margin-bottom: var(--space-3);
  transition: box-shadow 0.15s, border-color 0.15s;
  text-decoration: none;
  color: inherit;
  position: relative;
  overflow: hidden;
}

.lesson-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  border-radius: var(--radius-sm) 0 0 var(--radius-sm);
  background: var(--lesson-accent, var(--color-border));
  transition: width 0.2s;
}

.lesson-card.available:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  border-color: var(--lesson-accent, var(--color-primary));
}

.lesson-card.complete { background: var(--color-bg); }
.lesson-card.locked   { opacity: 0.55; pointer-events: none; }

.lesson-card-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--lesson-accent-light, var(--color-bg));
}

.lesson-card-icon svg { width: 24px; height: 24px; }

.lesson-card-body { flex: 1; min-width: 0; }

.lesson-card-title {
  font-size: var(--text-base);
  font-weight: var(--weight-bold);
  color: var(--color-ink);
  margin-bottom: 2px;
}

.lesson-card-meta {
  font-size: var(--text-xs);
  color: var(--color-ink-muted);
}

.lesson-card-progress {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--space-1);
  flex-shrink: 0;
}

.lesson-card-pct {
  font-size: var(--text-xs);
  font-weight: var(--weight-bold);
  color: var(--color-ink-muted);
}

.lesson-card-bar {
  width: 80px;
  height: 4px;
  background: var(--color-border);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.lesson-card-bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
  background: var(--lesson-accent, var(--color-primary));
  transition: width 0.4s ease;
}

.lesson-card-badge {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  padding: 3px 8px;
  border-radius: var(--radius-full);
}

.lesson-card-badge.complete { background: var(--color-success-light); color: var(--color-success); }
.lesson-card-badge.available { background: var(--color-primary-light); color: var(--color-primary); }
.lesson-card-badge.locked   { background: var(--color-bg); color: var(--color-ink-muted); }
.lesson-card-badge.capstone { background: #faf5ff; color: #7c3aed; }
```

---

## Deliverable 2: course.html — Richer lesson cards

Replace the lesson list rendering inside `showLessonList()` to use the new
`.lesson-card` design. The lesson card for each lesson should:

- Use `--lesson-accent` and `--lesson-accent-light` CSS custom properties set
  as inline styles so the color system applies automatically
- Show an inline SVG icon matching the lesson topic
- Show a progress bar filled to `chaptersRead / totalChapters` percent
- Show a badge: "Complete", "Start", "Continue", or "Locked"

Map lesson IDs to their accent colors and icons:

```javascript
var LESSON_META = {
  'lesson-1': {
    accent:      'var(--lesson-1-color)',
    accentLight: 'var(--lesson-1-light)',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>',
    label: 'Testing 101',
    chapters: 5
  },
  'lesson-2': {
    accent:      'var(--lesson-2-color)',
    accentLight: 'var(--lesson-2-light)',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/><path d="M11 8v3l2 2"/></svg>',
    label: 'Bug Reporting',
    chapters: 4
  },
  'lesson-3': {
    accent:      'var(--lesson-3-color)',
    accentLight: 'var(--lesson-3-light)',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8m-4-4v4"/></svg>',
    label: 'CRM Tools',
    chapters: 5
  },
  'lesson-4': {
    accent:      'var(--lesson-4-color)',
    accentLight: 'var(--lesson-4-light)',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    label: 'QA Process',
    chapters: 4
  },
  'capstone': {
    accent:      '#7c3aed',
    accentLight: '#faf5ff',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
    label: 'Capstone Assessment',
    chapters: 0
  }
};
```

Calculate chapter progress from `progress.chaptersRead[lessonId]` (array of
completed chapter IDs) vs the `chapters` count in LESSON_META.

The card HTML structure should match the `.lesson-card` CSS defined in
Deliverable 1, with inline style for `--lesson-accent` and
`--lesson-accent-light`.

---

## Deliverable 3: lesson-1.html through lesson-4.html — Chapter hero sections

At the top of each chapter's content area (inside `.chapter-main`), add a
`.chapter-hero` block before the chapter prose begins.

Each lesson file should define a `CHAPTER_HEROES` map at the top of its
`<script>` block:

**lesson-1.html** (Testing 101 — Blue):
```javascript
var CHAPTER_HEROES = {
  'chapter-1': {
    eyebrow: 'Lesson 1 · Chapter 1',
    title: 'What is Software Testing?',
    sub: 'Learn the purpose of QA and why it exists in every software team.',
    bg: 'var(--lesson-1-light)',
    color: 'var(--lesson-1-color)',
    border: 'var(--lesson-1-border)',
    icon: '<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="4" y="4" width="24" height="24" rx="5" fill="var(--lesson-1-color)" opacity="0.15"/><path d="M10 16 L14 20 L22 10" stroke="var(--lesson-1-color)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
  }
  // ... add entries for each chapter in lesson 1
};
```

**lesson-2.html** (Bug Reporting — Orange), **lesson-3.html** (CRM Tools — Teal),
**lesson-4.html** (QA Process — Purple): follow the same pattern with their
respective color variables.

When rendering a chapter, inject the hero at the top of `.chapter-main`:
```javascript
function renderChapterHero(chapterId) {
  var hero = CHAPTER_HEROES[chapterId];
  if (!hero) return '';
  return '<div class="chapter-hero" style="background:' + hero.bg +
         '; border-color:' + hero.border + '; color:' + hero.color + '">' +
         '<div class="chapter-hero-icon" style="background:' + hero.color +
         '20">' + hero.icon + '</div>' +
         '<div class="chapter-hero-text">' +
         '<div class="chapter-hero-eyebrow">' + hero.eyebrow + '</div>' +
         '<div class="chapter-hero-title">' + hero.title + '</div>' +
         '<div class="chapter-hero-sub">' + hero.sub + '</div>' +
         '</div></div>';
}
```

---

## Deliverable 4: lesson pages — Topbar chapter pips

In each lesson page's topbar, add a row of chapter completion pips so
students can see at a glance how far through the lesson they are:

```html
<div class="topbar-progress-indicator" id="topbar-pips">
  <!-- filled dynamically by JS -->
</div>
```

Populate via JS using the `topbar-progress-pip` classes (done / active / default).

---

## Definition of Done

- [ ] `css/main.css` has 4 lesson accent colour sets + all new component CSS
- [ ] `course.html` lesson cards show lesson icon, title, chapter progress bar, and correct badge
- [ ] Lesson 1–4 each have `CHAPTER_HEROES` map with chapter title + sub for every chapter
- [ ] Chapter hero renders at the top of each chapter with the correct lesson accent colour
- [ ] Topbar pips update as student moves through chapters
- [ ] All pages still function identically — no regressions in progress saving or navigation
- [ ] No CDN links or external image references added
- [ ] Admin pages and db.js are untouched
