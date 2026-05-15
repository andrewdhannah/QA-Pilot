# Sprint G-2 — Certificate Page
## Gemma Build Prompt

Read GEMMA-STYLE-GUIDE.md before writing any code.
Sprint Capstone-1 (capstone.html) must be complete before this sprint.
The db.js data layer must have awardCertificate() and saveQuizResults() implemented.

---

## Context

This is the QA Pilot training platform.
Stack: pure HTML/CSS/JS, no frameworks, no CDN links.
Data layer: IndexedDB via `js/db.js` — the ONLY file that touches IndexedDB.
CSS tokens: `css/main.css`.

`certificate.html` is the final destination in the student journey:
  Login → Lessons 1-4 → Capstone Assessment → **Certificate**

The page is reached by a redirect from `capstone.html` after the OS posts
`CAPSTONE_COMPLETE` and the result is saved to IndexedDB. At this point:
- The student's score is saved in IndexedDB via `saveQuizResults()`
- The certificate has been awarded via `awardCertificate()`
- `sessionStorage` still holds the active session (caseId, role)

The certificate page must read these results, display them, and offer a
printable certificate layout.

---

## What to Build

### HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Certificate of Completion | QA Pilot Academy</title>
    <link rel="stylesheet" href="css/main.css">
    <style>
        /* Certificate page specific styles */

        .certificate-page {
            min-height: 100vh;
            background: var(--color-surface-alt, #f8f7f6);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
            box-sizing: border-box;
        }

        /* Score summary card */
        .cert-score-card {
            background: white;
            border: 1px solid var(--color-border);
            border-radius: 12px;
            padding: 24px 32px;
            margin-bottom: 32px;
            text-align: center;
            max-width: 480px;
            width: 100%;
        }

        .cert-score-pct {
            font-size: 56px;
            font-weight: 700;
            color: var(--color-primary, #0078d4);
            line-height: 1;
            margin-bottom: 8px;
        }

        .cert-score-pct.passed  { color: #107c10; }
        .cert-score-pct.failed  { color: #a4262c; }

        .cert-score-label {
            font-size: 14px;
            color: var(--color-ink-soft);
            margin-bottom: 16px;
        }

        .cert-score-detail {
            font-size: 13px;
            color: var(--color-ink-soft);
        }

        /* The printable certificate */
        .certificate {
            background: white;
            border: 2px solid #0078d4;
            border-radius: 12px;
            padding: 48px 56px;
            max-width: 680px;
            width: 100%;
            text-align: center;
            position: relative;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        }

        .certificate::before {
            content: "";
            position: absolute;
            inset: 8px;
            border: 1px solid #c7e0f4;
            border-radius: 8px;
            pointer-events: none;
        }

        .cert-issuer {
            font-size: 11px;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #0078d4;
            font-weight: 600;
            margin-bottom: 20px;
        }

        .cert-headline {
            font-size: 28px;
            font-weight: 700;
            color: #201f1e;
            margin-bottom: 8px;
        }

        .cert-subheadline {
            font-size: 14px;
            color: var(--color-ink-soft);
            margin-bottom: 32px;
        }

        .cert-recipient-label {
            font-size: 12px;
            color: var(--color-ink-soft);
            margin-bottom: 6px;
        }

        .cert-recipient-name {
            font-size: 32px;
            font-weight: 300;
            font-style: italic;
            color: #0078d4;
            border-bottom: 1px solid #c7e0f4;
            display: inline-block;
            padding-bottom: 8px;
            margin-bottom: 24px;
            min-width: 280px;
        }

        .cert-body {
            font-size: 13px;
            color: #605e5c;
            line-height: 1.7;
            margin-bottom: 32px;
            max-width: 460px;
            margin-left: auto;
            margin-right: auto;
        }

        .cert-score-badge {
            display: inline-block;
            background: #107c10;
            color: white;
            border-radius: 999px;
            padding: 6px 20px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 32px;
        }

        .cert-score-badge.failed {
            background: #a4262c;
        }

        .cert-date {
            font-size: 12px;
            color: var(--color-ink-soft);
            margin-top: 24px;
        }

        .cert-actions {
            margin-top: 28px;
            display: flex;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
        }

        @media print {
            .topbar, .cert-score-card, .cert-actions { display: none !important; }
            .certificate-page { padding: 0; background: white; }
            .certificate { box-shadow: none; border-color: #ccc; }
        }
    </style>
</head>
<body>
    <!-- Topbar (not printed) -->
    <header class="topbar">
        <div class="topbar-left">
            <a href="course.html" class="topbar-back"
               style="color: var(--color-ink-soft); text-decoration: none; margin-right: 12px;">
                ← Dashboard
            </a>
            <span class="topbar-title font-bold">Certificate</span>
        </div>
        <div class="topbar-right flex items-center gap-4">
            <span id="user-name-display" class="text-sm"></span>
            <button onclick="signOut()" class="btn btn-ghost text-xs">Sign Out</button>
        </div>
    </header>

    <div class="certificate-page">

        <!-- Score summary (not printed) -->
        <div class="cert-score-card" id="cert-score-card">
            <div class="cert-score-pct" id="cert-score-pct">—</div>
            <div class="cert-score-label" id="cert-score-label">Loading your results…</div>
            <div class="cert-score-detail" id="cert-score-detail"></div>
        </div>

        <!-- The certificate -->
        <div class="certificate" id="cert-document">
            <div class="cert-issuer">QA Pilot Academy</div>
            <div class="cert-headline">Certificate of Completion</div>
            <div class="cert-subheadline">QA Analyst Onboarding Programme</div>

            <div class="cert-recipient-label">This certifies that</div>
            <div class="cert-recipient-name" id="cert-name">—</div>

            <div class="cert-body">
                has successfully completed the QA Pilot Academy onboarding programme,
                including all lesson modules and the live Capstone Assessment —
                demonstrating proficiency in case investigation using Dynamics 365,
                defect identification against Acceptance Criteria, and bug reporting
                in Azure DevOps.
            </div>

            <div class="cert-score-badge" id="cert-badge">Loading…</div>

            <div class="cert-date" id="cert-date"></div>
        </div>

        <!-- Actions (not printed) -->
        <div class="cert-actions">
            <button onclick="window.print()" class="btn btn-primary">Print Certificate</button>
            <a href="course.html" class="btn btn-ghost">Back to Dashboard</a>
        </div>

    </div>

    <div id="toast" class="toast"></div>

    <script src="data/content.js"></script>
    <script src="js/db.js"></script>
    <script src="js/app.js"></script>
    <script>
        /**
         * certificate.html — Certificate of Completion
         * =============================================
         * WHAT THIS PAGE DOES:
         * - Verifies the student session via requireLogin()
         * - Reads the capstone score from IndexedDB via getProgress()
         * - Renders the score summary card and printable certificate
         *
         * FLOW:
         * 1. initDB() opens the database
         * 2. requireLogin() checks for a valid session (redirects if none)
         * 3. getProgress() fetches the student's progress record
         * 4. renderCertificate() populates the page from the progress data
         *
         * READS FROM:   IndexedDB via db.js (progress store)
         * WRITES TO:    nothing
         * REDIRECTS TO: login if no session
         */


        // ── SECTION 1: PAGE STATE ──────────────────────────────────────────────

        var currentSession  = null;
        var currentProgress = null;


        // ── SECTION 2: INITIALISE ─────────────────────────────────────────────

        initDB()
            .then(function() {
                currentSession = requireLogin();
                if (!currentSession) return null;

                var nameEl = document.getElementById('user-name-display');
                if (nameEl) nameEl.textContent = currentSession.caseId;

                return getProgress(currentSession.caseId);
            })
            .then(function(progress) {
                if (!progress) return;
                currentProgress = progress;
                renderCertificate(currentProgress, currentSession);
            })
            .catch(function(err) {
                console.error('Certificate load failed:', err);
                showToast('Could not load results. Please return to the dashboard.', 'error');
            });


        // ── SECTION 3: RENDER ─────────────────────────────────────────────────

        /**
         * renderCertificate(progress, session)
         * Populates the score card and certificate document from IndexedDB data.
         *
         * @param {Object} progress - The student progress record from getProgress()
         * @param {Object} session  - The active session from requireLogin()
         */
        function renderCertificate(progress, session) {

            // Extract capstone quiz results (saved by capstone.html on CAPSTONE_COMPLETE)
            var results    = (progress.quizResults && progress.quizResults.capstone) || {};
            var score      = results.score      || 0;
            var maxScore   = results.maxScore   || 0;
            var percentage = results.percentage || 0;
            var passed     = results.passed     || false;
            var completedAt = results.completedAt
                             ? new Date(results.completedAt).toLocaleDateString(undefined, {
                                 year: 'month', month: 'long', day: 'numeric'
                               })
                             : new Date().toLocaleDateString(undefined, {
                                 year: 'numeric', month: 'long', day: 'numeric'
                               });

            var name = session.caseId || 'Student';

            // ── Score summary card ─────────────────────────────────────────────
            var pctEl    = document.getElementById('cert-score-pct');
            var labelEl  = document.getElementById('cert-score-label');
            var detailEl = document.getElementById('cert-score-detail');

            if (pctEl) {
                pctEl.textContent = percentage + '%';
                pctEl.classList.add(passed ? 'passed' : 'failed');
            }
            if (labelEl) {
                labelEl.textContent = passed
                    ? '✓ Assessment Passed'
                    : '✗ Assessment Not Passed — Please review with your supervisor.';
            }
            if (detailEl) {
                detailEl.textContent = maxScore > 0
                    ? score + ' of ' + maxScore + ' points'
                    : 'Score data not available.';
            }

            // ── Certificate document ───────────────────────────────────────────
            var nameEl   = document.getElementById('cert-name');
            var badgeEl  = document.getElementById('cert-badge');
            var dateEl   = document.getElementById('cert-date');

            if (nameEl)  nameEl.textContent  = name;
            if (dateEl)  dateEl.textContent  = 'Completed ' + completedAt;

            if (badgeEl) {
                badgeEl.textContent = passed
                    ? 'Passed — ' + percentage + '%'
                    : 'Needs Review — ' + percentage + '%';
                if (!passed) badgeEl.classList.add('failed');
            }
        }
    </script>
</body>
</html>
```

---

## What NOT to Change

- Do not touch lesson-1.html through lesson-4.html
- Do not touch admin files
- Do not modify js/db.js — only call functions that already exist there
- Do not change CSS variables in main.css
- Do not add CDN links or external dependencies
- Do not use fetch() — this is a file:// safe platform

---

## After This Sprint

Open `certificate.html` directly in a browser after completing the capstone.
The session must still be active in sessionStorage.
Confirm: score percentage displays, certificate shows the student name,
passed/failed badge is correct, print button triggers browser print dialog.

---

## Definition of Done

- [ ] `certificate.html` reads session from `requireLogin()` and redirects if none
- [ ] `getProgress(caseId)` is called and capstone quiz results are extracted
- [ ] Score percentage displayed in the summary card with pass/fail colour
- [ ] Score detail shows "X of Y points"
- [ ] Certificate document shows student name, passed/failed badge, and completion date
- [ ] Print button triggers `window.print()` — topbar and score card are hidden via `@media print`
- [ ] Page handles missing score data gracefully (shows fallback text, no JS errors)
- [ ] All code commented to GEMMA-STYLE-GUIDE standard
