# Sprint G4 — Certificate Redesign + Score Breakdown
## Gemma Build Prompt

Read GEMMA-STYLE-GUIDE.md before writing any code.
Sprint G3 (Academy Visual Refresh) should be complete before this sprint
so the shared CSS tokens are available.

---

## Context

This is the QA Onboarding Training Platform.
Stack: pure HTML/CSS/JS, no frameworks, no CDN links, no canvas.
CSS tokens: css/main.css. Data layer: IndexedDB via js/db.js.

`certificate.html` currently shows a simple text layout with the student
name, score, and a print button. It works but looks nothing like a real
training certificate.

This sprint replaces it with:
1. A printable certificate panel styled like a professional document
2. A score breakdown card showing bugs found, reports filed, and points scored
3. A "What's Next" panel (links back to dashboard, suggests re-take if failed)

The page must remain file:// safe — no external fonts, no images, no canvas.
All visual richness comes from CSS and inline SVG.

---

## What NOT to Change

- js/db.js — do not modify
- js/app.js — do not modify
- css/main.css — only ADD rules at the end, do not remove any
- The `requireLogin()`, `initDB()`, `getProgress()`, `getStudent()` calls in
  the existing `<script>` — keep the data loading logic intact
- The `currentProgress.certificateAwarded` check — keep the security gate

---

## Page Layout

Replace the body content with this three-section layout:

```html
<body class="cert-page">

  <!-- Topbar (same pattern as lesson pages) -->
  <header class="topbar">
    <div class="topbar-left">
      <span class="topbar-brand">QA Pilot Academy</span>
    </div>
    <div class="topbar-right">
      <span id="cert-student-name" class="text-sm"></span>
      <button onclick="handleLogout()" class="btn btn-ghost text-xs">Sign Out</button>
    </div>
  </header>

  <div class="cert-layout">

    <!-- LEFT: The certificate document -->
    <div class="cert-document-wrap">
      <div class="cert-document" id="cert-print-area">

        <div class="cert-watermark">QA PILOT</div>

        <div class="cert-header">
          <!-- QA Pilot logo mark (inline SVG) -->
          <div class="cert-logo">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none"
                 xmlns="http://www.w3.org/2000/svg">
              <rect width="48" height="48" rx="10" fill="#2563eb"/>
              <path d="M14 24 L20 30 L34 16" stroke="white" stroke-width="4"
                    stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="24" cy="24" r="10" stroke="white" stroke-width="2"
                      fill="none" opacity="0.3"/>
            </svg>
          </div>
          <div class="cert-org">QA Pilot Academy</div>
          <div class="cert-document-title">Certificate of Completion</div>
        </div>

        <div class="cert-body">
          <p class="cert-presented">This certifies that</p>
          <p class="cert-name" id="cert-name">Student Name</p>
          <p class="cert-presented">has successfully completed the</p>
          <p class="cert-course" id="cert-course">QA Onboarding Program</p>

          <div class="cert-divider"></div>

          <div class="cert-meta-row">
            <div class="cert-meta-item">
              <span class="cert-meta-label">Score</span>
              <span class="cert-meta-value" id="cert-score-display">--</span>
            </div>
            <div class="cert-meta-sep"></div>
            <div class="cert-meta-item">
              <span class="cert-meta-label">Date</span>
              <span class="cert-meta-value" id="cert-date">--</span>
            </div>
            <div class="cert-meta-sep"></div>
            <div class="cert-meta-item">
              <span class="cert-meta-label">Credential ID</span>
              <span class="cert-meta-value" id="cert-credential">--</span>
            </div>
          </div>
        </div>

        <div class="cert-footer">
          <div class="cert-seal">
            <!-- Seal SVG — rendered in CSS ring pattern -->
            <svg width="64" height="64" viewBox="0 0 64 64" fill="none"
                 xmlns="http://www.w3.org/2000/svg">
              <circle cx="32" cy="32" r="30" stroke="#2563eb" stroke-width="2"
                      stroke-dasharray="4 3"/>
              <circle cx="32" cy="32" r="22" stroke="#2563eb" stroke-width="1.5"
                      fill="#eff6ff"/>
              <path d="M22 32 L28 38 L42 24" stroke="#2563eb" stroke-width="3"
                    stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="cert-issuer" id="cert-issuer">QA Pilot Training Program</div>
        </div>

      </div><!-- /cert-document -->

      <!-- Print button sits outside the print area -->
      <div class="cert-actions">
        <button class="btn btn-primary" onclick="window.print()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" stroke-width="2">
            <polyline points="6 9 6 2 18 2 18 9"/>
            <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1
                     2 2v5a2 2 0 0 1-2 2h-2"/>
            <rect x="6" y="14" width="12" height="8"/>
          </svg>
          Print Certificate
        </button>
        <a href="course.html" class="btn btn-ghost">← Back to Dashboard</a>
      </div>
    </div><!-- /cert-document-wrap -->

    <!-- RIGHT: Score breakdown + What's Next -->
    <div class="cert-sidebar">

      <!-- Score card -->
      <div class="cert-score-card" id="cert-score-card">
        <div class="cert-score-header">
          <span class="cert-score-label">Assessment Score</span>
          <span class="cert-score-badge" id="cert-badge">--</span>
        </div>
        <div class="cert-score-ring-wrap">
          <svg class="cert-score-ring" viewBox="0 0 80 80">
            <circle cx="40" cy="40" r="34" stroke="var(--color-border)"
                    stroke-width="6" fill="none"/>
            <circle cx="40" cy="40" r="34" stroke="var(--color-primary)"
                    stroke-width="6" fill="none"
                    stroke-dasharray="213.6"
                    stroke-dashoffset="213.6"
                    stroke-linecap="round"
                    transform="rotate(-90 40 40)"
                    id="cert-ring-fill"/>
          </svg>
          <div class="cert-score-pct" id="cert-pct">--%</div>
        </div>
        <div class="cert-score-detail" id="cert-score-detail">-- of -- points</div>
      </div>

      <!-- Breakdown rows -->
      <div class="cert-breakdown" id="cert-breakdown" style="display:none;">
        <div class="cert-breakdown-title">Score Breakdown</div>
        <div class="cert-breakdown-row">
          <span>Bugs discovered in CRM</span>
          <span class="cert-breakdown-val" id="bd-bugs-found">--</span>
        </div>
        <div class="cert-breakdown-row">
          <span>ADO reports filed</span>
          <span class="cert-breakdown-val" id="bd-reports">--</span>
        </div>
        <div class="cert-breakdown-row">
          <span>Correct AC references</span>
          <span class="cert-breakdown-val" id="bd-refs">--</span>
        </div>
      </div>

      <!-- What's Next -->
      <div class="cert-next">
        <div class="cert-next-title" id="cert-next-title">What's Next</div>
        <p class="cert-next-body" id="cert-next-body"></p>
        <a href="course.html" class="btn btn-primary cert-next-btn"
           id="cert-next-btn" style="display:none;">View Dashboard</a>
      </div>

    </div><!-- /cert-sidebar -->

  </div><!-- /cert-layout -->

</body>
```

---

## CSS — Add to end of css/main.css

```css
/* ── CERTIFICATE PAGE ────────────────────────────────────────────────── */

.cert-page { background: var(--color-bg); min-height: 100vh; }

.cert-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: var(--space-8);
  max-width: 1000px;
  margin: var(--space-8) auto;
  padding: 0 var(--space-6);
  align-items: start;
}

/* Certificate document */
.cert-document-wrap { display: flex; flex-direction: column; gap: var(--space-4); }

.cert-document {
  background: #fff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-12) var(--space-10);
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.07);
}

.cert-watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-30deg);
  font-size: 80px;
  font-weight: var(--weight-bold);
  color: var(--color-primary);
  opacity: 0.03;
  letter-spacing: 0.1em;
  white-space: nowrap;
  pointer-events: none;
  user-select: none;
}

.cert-header { text-align: center; margin-bottom: var(--space-8); }
.cert-logo   { display: flex; justify-content: center; margin-bottom: var(--space-3); }
.cert-org    { font-size: var(--text-xs); font-weight: var(--weight-bold);
               text-transform: uppercase; letter-spacing: 0.12em;
               color: var(--color-ink-muted); margin-bottom: var(--space-2); }
.cert-document-title { font-size: var(--text-xl); font-weight: var(--weight-bold);
                        color: var(--color-ink); letter-spacing: -0.01em; }

.cert-body { text-align: center; }
.cert-presented { font-size: var(--text-sm); color: var(--color-ink-muted);
                   margin: 0 0 var(--space-1); }
.cert-name  { font-size: var(--text-2xl); font-weight: var(--weight-bold);
               color: var(--color-primary); margin: var(--space-2) 0; }
.cert-course { font-size: var(--text-md); font-weight: var(--weight-medium);
                color: var(--color-ink); margin: var(--space-1) 0 var(--space-6); }

.cert-divider {
  width: 60px; height: 2px; background: var(--color-primary);
  margin: var(--space-6) auto; border-radius: var(--radius-full);
  opacity: 0.3;
}

.cert-meta-row {
  display: flex; justify-content: center; align-items: center;
  gap: var(--space-6); flex-wrap: wrap;
}
.cert-meta-item { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.cert-meta-label { font-size: var(--text-xs); color: var(--color-ink-muted);
                    text-transform: uppercase; letter-spacing: 0.06em; }
.cert-meta-value { font-size: var(--text-sm); font-weight: var(--weight-bold);
                    color: var(--color-ink); }
.cert-meta-sep   { width: 1px; height: 28px; background: var(--color-border); }

.cert-footer {
  display: flex; flex-direction: column; align-items: center;
  gap: var(--space-3); margin-top: var(--space-10);
}
.cert-issuer { font-size: var(--text-xs); color: var(--color-ink-muted); }

.cert-actions {
  display: flex; gap: var(--space-3); justify-content: center; flex-wrap: wrap;
}

/* Score sidebar */
.cert-sidebar { display: flex; flex-direction: column; gap: var(--space-4); }

.cert-score-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
}

.cert-score-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: var(--space-4);
}
.cert-score-label { font-size: var(--text-sm); font-weight: var(--weight-bold);
                     color: var(--color-ink); }
.cert-score-badge {
  font-size: var(--text-xs); font-weight: var(--weight-bold);
  padding: 2px 8px; border-radius: var(--radius-full);
  background: var(--color-success-light); color: var(--color-success);
}
.cert-score-badge.failed { background: var(--color-error-light); color: var(--color-error); }

.cert-score-ring-wrap {
  position: relative; width: 80px; height: 80px; margin: 0 auto var(--space-3);
}
.cert-score-ring { width: 80px; height: 80px; }
.cert-score-pct {
  position: absolute; inset: 0; display: flex; align-items: center;
  justify-content: center; font-size: var(--text-md);
  font-weight: var(--weight-bold); color: var(--color-ink);
}
.cert-score-detail {
  text-align: center; font-size: var(--text-xs); color: var(--color-ink-muted);
}

.cert-breakdown {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-5);
}
.cert-breakdown-title {
  font-size: var(--text-sm); font-weight: var(--weight-bold);
  color: var(--color-ink); margin-bottom: var(--space-3);
}
.cert-breakdown-row {
  display: flex; justify-content: space-between; align-items: center;
  font-size: var(--text-sm); color: var(--color-ink-muted);
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--color-border);
}
.cert-breakdown-row:last-child { border-bottom: none; }
.cert-breakdown-val { font-weight: var(--weight-bold); color: var(--color-ink); }

.cert-next {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
}
.cert-next-title { font-size: var(--text-sm); font-weight: var(--weight-bold);
                    color: var(--color-ink); margin-bottom: var(--space-2); }
.cert-next-body  { font-size: var(--text-sm); color: var(--color-ink-muted);
                    margin: 0 0 var(--space-4); line-height: var(--leading-base); }
.cert-next-btn   { width: 100%; justify-content: center; }

/* Print styles */
@media print {
  .topbar, .cert-sidebar, .cert-actions { display: none !important; }
  .cert-layout { grid-template-columns: 1fr; max-width: 100%; margin: 0; padding: 0; }
  .cert-document { box-shadow: none; border: none; border-radius: 0; }
  .cert-watermark { opacity: 0.05; }
}

@media (max-width: 700px) {
  .cert-layout { grid-template-columns: 1fr; }
}
```

---

## Script — renderCertificate() updates

Update `renderCertificate()` to:

1. **Animate the score ring** — set `stroke-dashoffset` to
   `213.6 - (213.6 * percentage / 100)` on `#cert-ring-fill`

2. **Populate score breakdown** — if `capstoneResult` has `missedBugs` and
   `badReports` fields (from scoring.js), show `#cert-breakdown` and fill
   `#bd-bugs-found`, `#bd-reports`, `#bd-refs`

3. **What's Next messaging**:
   - If passed: "Outstanding work! You've earned your QA Pilot certificate.
     Share it with your team lead or add it to your profile."
     Show "View Dashboard" button.
   - If failed (score < 70%): "You scored below the pass threshold this time.
     Review the lessons and retry the capstone when you're ready."
     Show "Retry Capstone" button linking to capstone.html.

4. **Credential ID** — generate a deterministic ID from caseId + date:
   ```javascript
   var credId = 'QAP-' + currentSession.caseId.replace('CASE-', '') +
                '-' + new Date(certDate).getFullYear();
   ```

---

## Definition of Done

- [ ] Certificate document renders with watermark, logo, student name, course name, score, date, credential ID
- [ ] Score ring animates to the correct percentage on page load
- [ ] Score breakdown card shows if `capstoneResult` data is available
- [ ] What's Next panel shows appropriate message + button for pass and fail states
- [ ] Print button hides sidebar and actions, prints only the certificate document
- [ ] Page is responsive — single column on mobile
- [ ] All existing data loading logic (requireLogin, initDB, getStudent, getProgress) is untouched
- [ ] No external fonts, images, or CDN links
