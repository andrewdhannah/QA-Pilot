# QA Pilot Design Language Baseline

**Epic:** EPIC-QA-PILOT-DESIGN-LANGUAGE-REFRESH-1
**Sprint:** QA-PILOT-DESIGN-LANGUAGE-BASELINE-1 (Ledger #136, sealed)
**Epic:** EPIC-QA-PILOT-DESIGN-LANGUAGE-REFRESH-1 (sealed 2026-07-09)
**Reference:** The Librarian `Public/index.html`, `theme.css`, `styles.css` (light mode)
**Date:** 2026-07-09

---

## 1. Comparison: QA Pilot vs Librarian Design Language

### 1.1 Design Tokens

| Token | QA Pilot (Current) | Librarian Light Theme | Recommendation |
|-------|-------------------|----------------------|----------------|
| `--color-primary` | `#2563eb` (blue) | `#0066cc` (blue) | Keep QA Pilot blue but align brightness |
| `--color-accent` | — | `#0066cc` | Add `--color-accent` alias |
| `--color-bg` | `#f4f6fb` | `#ffffff` / `#f5f5f5` | Keep current — cleaner for static pages |
| `--color-ink` | `#1a1f2e` | `#1a1a1a` | Keep — virtually identical |
| `--color-ink-muted` | `#8892a4` | `#888888` | Keep — virtually identical |
| `--color-border` | `#e2e6f0` | `rgba(0,0,0,0.14)` | Keep QA Pilot — cleaner blue-gray |
| `--font-sans` | `-apple-system, ...` | `-apple-system, ...` | **Inherit Librarian** — add `BlinkMacSystemFont`, `Helvetica` |
| `--font-mono` | `'Courier New'` | `SF Mono, Menlo...` | **Inherit Librarian** — better monospace stack |
| Spacing scale | 4px grid (1-16) | 4px grid (1-7) | **Inherit Librarian** `--space-*` naming (1-7) |
| Radius scale | sm=4, md=8, lg=12, full=9999 | sm=4, md=8, lg=12, xl=16, full=9999 | **Inherit Librarian** — add `--radius-xl: 16px` |
| Shadow scale | sm, md, lg | xs, sm, md, lg, xl | **Inherit Librarian** — add `--shadow-xs` and `--shadow-xl` |
| Typography scale | xs=11, sm=13, base=14, md=16, lg=20, xl=24, 2xl=30 | caption=11, small=12, body=13, subhead=14, heading=16, heading-lg=20, hero=clamp | **Inherit Librarian** naming + add `--text-hero` |
| Weight scale | normal=400, medium=500, bold=700 | regular=400, medium=500, semibold=600, bold=700 | **Inherit Librarian** — add `--weight-semibold` |
| Letter spacing | inline only | `--ls-tight`, `--ls-normal`, `--ls-wide`, `--ls-wider`, `--ls-widest` | **Inherit Librarian** — add letter-spacing tokens |
| Line height | tight=1.3, base=1.6, loose=1.8 | tight=1.1, normal=1.4, relaxed=1.6 | **Inherit Librarian** — tighter heading leading |
| Motion | fast=0.1s, base=0.2s, slow=0.3s | instant=0ms, fast=100ms, normal=200ms, slow=300ms | **Inherit Librarian** naming + `--motion-ease-out` for entrances |

### 1.2 Layout Patterns

| Pattern | QA Pilot | Librarian | Recommendation |
|---------|----------|-----------|----------------|
| Page shell | Single scroll | Fixed shell with sidebar/rail | Keep QA Pilot single-scroll (browser-only) |
| Topbar | `linear-gradient(90deg,#fff,#f9fafb)`, sticky | Fixed toolbar with brand, command, indicators | **Inherit Librarian** — flat white, remove gradient |
| Brand display | SVG + "QA Pilot Academy" | SVG + "The Librarian" + workspace label | Keep QA Pilot identity, add data-source footer |
| Sidebar | None | `--sidebar-width: 232px` | Not applicable — QA Pilot is single-page |
| Status display | Inline identity notes | Status strip with dot indicators | **Inherit Librarian** — add status strip with pill indicators |
| Content width | `max-width: 960px` (container), 640px (splash), 1200px (catalog) | `--content-readable-width: 1180px` | Standardize on 960px/1180px per page type |
| Card hierarchy | Single level (`.card`) | Three levels (owner-queue > active-work > flat) | **Inherit Librarian** — add bento elevation system |

### 1.3 Page-Specific Patterns

| Page | QA Pilot | Librarian Equivalent | Recommendation |
|------|----------|---------------------|----------------|
| `index.html` (Splash) | Hero with 3 mode cards | — | Keep splash/portal identity, Librarian card styling |
| `admin.html` | 5 tabs with card panels | Overview Command Center (bento cards) | **Inherit Librarian bento layout** — attention card, work card, stats |
| `identity.html` | Single card with member list | — | Keep simple, apply Librarian card styling |
| `catalog.html` | Course card grid | Library view | **Inherit Librarian** document card pattern |
| `course-view.html` | Two-column sidebar + content | — | Keep layout, refine with Librarian section rhythm |
| `certificate.html` | Full certificate page | — | Keep distinctive certificate, apply tokens |
| `export.html` | Single card page | — | Apply Librarian section rhythm, data footer |
| `import.html` | Single card page | — | Apply Librarian section rhythm, data footer |

## 2. Design Tokens to Inherit from Librarian

The following tokens should be added to QA Pilot's `main.css` before any page redesigns:

```css
/* Letter Spacing */
--ls-tight:       -0.01em;
--ls-normal:      0;
--ls-wide:        0.05em;
--ls-wider:       0.08em;
--ls-widest:      0.12em;

/* Font Stacks */
--font-sans:      -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
--font-mono:      SF Mono, Menlo, Monaco, "Cascadia Code", Consolas, monospace;

/* Typography additions */
--weight-semibold: 600;
--text-caption:   11px;
--text-small:     12px;
--text-hero:      clamp(22px, 2.4vw, 34px);
--lh-tight:       1.1;
--lh-relaxed:     1.6;

/* Border Radius */
--radius-xl:      16px;

/* Shadows */
--shadow-xs:      0 1px 2px rgba(0, 0, 0, 0.30);
--shadow-xl:      0 20px 48px rgba(0, 0, 0, 0.50);

/* Motion */
--motion-instant:   0ms;
--motion-ease-out:  ease-out;
--motion-spring:    cubic-bezier(0.34, 1.56, 0.64, 1);
--motion-card-entrance:     250ms;
--motion-card-stagger:      40ms;
--motion-pulse:             600ms;
--motion-button-press:      100ms;

/* Elevation Backgrounds (light mode) */
--elev-bg-owner-queue:    rgba(250, 245, 235, 0.85);
--elev-bg-active-work:    rgba(248, 243, 233, 0.70);
--elev-bg-flat:           rgba(242, 237, 227, 0.50);

/* Elevation Shadows (light mode) */
--elev-shadow-owner-queue: 0 20px 40px -12px rgba(180, 150, 100, 0.15),
                            0 4px 12px rgba(0, 0, 0, 0.08);
--elev-shadow-active-work: 0 12px 24px -10px rgba(180, 150, 100, 0.08);
--elev-shadow-flat:        none;

/* Elevation Borders (light mode) */
--elev-border-owner-queue:     1px solid rgba(180, 150, 100, 0.20);
--elev-border-active-work:     1px solid rgba(180, 150, 100, 0.12);
--elev-border-flat:            1px solid rgba(0, 0, 0, 0.06);

/* Section Rhythm */
--section-gap:               var(--space-4);
--section-inner-gap:         var(--space-3);
--section-padding:           var(--space-4);
--section-radius:            var(--radius-lg);
```

## 3. QA Pilot-Specific Design Rules

### 3.1 Identity Rules

| Rule | Description |
|------|-------------|
| R1 | All pages must say "QA Pilot Academy" in title and visible branding |
| R2 | QA Pilot Academy brand mark (SVG badge icon) on every page |
| R3 | Product identity is Academy/training — not a governance dashboard |
| R4 | Language toggle must appear on every page (Defect #1 fix verified) |
| R5 | Favicon must be referenced on every page |

### 3.2 Browser-Only Constraints

| Rule | Description |
|------|-------------|
| B1 | All pages open from `file://` — no server rendering, no build step |
| B2 | All state uses `localStorage` — no network requests |
| B3 | JSON schema enforcement for deployment-v1 and result-v1 |
| B4 | Local identity only — no auth, no passwords |
| B5 | No Librarian file paths must be referenced or written |

### 3.3 Light Theme Rules

| Rule | Description |
|------|-------------|
| L1 | QA Pilot is light-theme-only — no dark theme, no `prefers-color-scheme` queries |
| L2 | Background: `--color-bg: #f4f6fb` (warm light) |
| L3 | Cards: `--color-surface: #ffffff` with subtle border |
| L4 | Blue primary accent: `--color-primary: #2563eb` |
| L5 | Warm neutrals for text, not pure gray (#8892a4 > #888888) |

### 3.4 Page Layout Rules

| Rule | Description |
|------|-------------|
| P1 | Single-scroll layout — no fixed shell, no sidebar, no right rail |
| P2 | Topbar: flat white background (remove blue gradient for admin, keep portal gradient for splash) |
| P3 | Content: centered max-width container per page type |
| P4 | Data source/identity footer on every non-trivial page (see Librarian `view-data-footer`) |
| P5 | Card hierarchy: elevate admin cards with bento-style elevation (owner/active/flat) |

## 4. Page-by-Page Redesign Rules

### 4.1 index.html (Splash Page)

**Keep:** QA Pilot Academy branding, 3 mode cards, identity note
**Change:** Librarian-style card styling for mode cards, status strip for identity/authenticity, data-footer for build version
**Token alignment:** Apply `--lh-tight`, `--radius-xl` to hero, Librarian-style headings

### 4.2 admin.html (Admin Workspace)

**Keep:** 5-tab structure, localStorage-based state
**Change:** Adopt Librarian bento layout for the default "dashboard" view — attention card (Owner Queue style) for recent activity, flat cards for stats (learners, packages, deployments), active-work card for current deployment status, Recent Changes style card for result imports
**Token alignment:** Apply `--elev-bg-*`, `--elev-shadow-*`, `--elev-border-*` for card hierarchy

### 4.3 identity.html (Learner Identity)

**Keep:** Deployment roster display, local identity note
**Change:** Librarian-style card with section rhythm (header > body > footer), status-strip style for deployment info
**Token alignment:** Apply `--section-gap`, `--view-section-*` patterns

### 4.4 catalog.html (Training Portal)

**Keep:** Course card grid, progress tracking, completed/in-progress sections
**Change:** Librarian-style document cards (cleaner borders, consistent metadata), inline stats for totals
**Token alignment:** Apply `--inline-stat-*` patterns, `--view-state-badge` for status

### 4.5 course-view.html (Course Runtime)

**Keep:** Two-column layout, sidebar navigation, progress bar
**Change:** Refine lesson cards with Librarian section rhythm, add breadcrumb/subtle motion for section transitions, consistent exercise area styling
**Token alignment:** Apply `--view-section-*`, `--lh-relaxed` for body text, `--motion-card-entrance` for section transitions

### 4.6 certificate.html (Certificate)

**Keep:** Certificate layout, print-to-PDF, advisory notice
**Change:** Apply updated design tokens, consistent typography scale, Librarian-style data source footer
**Token alignment:** Apply all token updates, keep distinctive double-border certificate styling

### 4.7 export.html (Result Export)

**Keep:** Completed items list, result JSON preview, download functionality
**Change:** Apply Librarian section rhythm (panel-purpose-label > header > body > footer), show result schema info and data source tag
**Token alignment:** Apply `--view-section-*`, `--panel-purpose-label`, `--view-data-footer`

### 4.8 import.html (Admin Import)

**Keep:** File import, results dashboard, stats grid
**Change:** Apply Librarian section rhythm, inline stats for dashboard counters, status strip for import validation
**Token alignment:** Apply `--inline-stats-row`, `--view-state-badge`, `--view-data-footer`

## 5. Components to Add from Librarian

| Component | Source | QA Pilot Target |
|-----------|--------|-----------------|
| `panel-purpose-label` | `styles.css` .panel-purpose-label | All page headers |
| `view-data-footer` | `styles.css` .view-data-footer | All pages (identity/source info) |
| `inline-stats-row` | `styles.css` .inline-stats-row | admin.html, import.html |
| `status-pill` | `styles.css` .status-pill | admin.html status indicators |
| `view-state-badge` | `styles.css` .view-state-badge | admin.html, catalog.html |
| `card-enter` animation | `styles.css` @keyframes fade-up | Admin cards, catalog cards |
| `status-strip` | `styles.css` .app-status-strip | All pages as persistent footer |
| `elevation cards` | `theme.css` --elev-* | admin.html bento layout |

## 6. Components to Keep as QA Pilot-Specific

| Component | Reason |
|-----------|--------|
| Course sidebar (`cv-sidebar`) | Unique to learner runtime — no Librarian equivalent |
| Certificate styling | Distinctive double-border, watermark — Academy identity |
| Splash hero (blue gradient) | Academy brand portal feel |
| Language toggle | QA Pilot is bilingual (EN/FR) — unique requirement |
| Mode cards (splash) | No Librarian equivalent for solo/import/admin |

## 7. Sprint Sequence Guidance

### Sprint 2: QA-PILOT-DESIGN-TOKEN-AND-SHELL-REFRESH-1
- Merge Librarian tokens into `main.css` (see §2 above)
- Add component classes: `.panel-purpose-label`, `.view-data-footer`, `.inline-stats-row`, `.status-pill`, `.view-state-badge`
- Add card-entrance animation
- Update typography scale, font stacks, letter-spacing tokens
- Update button system to match Librarian (secondary-button, primary-button patterns)

### Sprint 3: QA-PILOT-ADMIN-DASHBOARD-DESIGN-REFRESH-1
- Redesign admin.html tab contents with bento card hierarchy
- Default landing tab as dashboard with attention/work/stats cards
- Apply elevation tokens

### Sprint 4: QA-PILOT-LEARNER-PORTAL-DESIGN-REFRESH-1
- Refresh catalog.html with Librarian-style document cards
- Refresh identity.html with section rhythm
- Apply consistent card, status, and stat patterns

### Sprint 5: QA-PILOT-COURSE-RUNTIME-DESIGN-REFRESH-1
- Refine course-view.html layout, navigation, progress
- Add motion for section transitions
- Apply refreshed typography

### Sprint 6: QA-PILOT-EXPORT-IMPORT-CERTIFICATE-DESIGN-REFRESH-1
- Apply section rhythm to export.html, import.html
- Apply updated tokens to certificate.html
- Add data footers to all three pages

### Sprint 7: QA-PILOT-DESIGN-LANGUAGE-ROUNDTRIP-VALIDATION-1
- Re-run full 22-step validation workflow
- Confirm all design parity checklist items pass
- Verify no backend/auth/install introduced
