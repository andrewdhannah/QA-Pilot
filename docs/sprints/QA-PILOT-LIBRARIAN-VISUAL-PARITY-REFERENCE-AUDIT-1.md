# QA Pilot Librarian Visual Parity Reference Audit

**Sprint:** QA-PILOT-LIBRARIAN-VISUAL-PARITY-REFERENCE-AUDIT-1 (Ledger #153)
**Lane:** visual_parity
**Epic:** EPIC-QA-PILOT-LIBRARIAN-VISUAL-PARITY-CORRECTION-1 (Sprint 1/5)
**Status:** authorized — 2026-07-09

## Purpose
Inspect current CarbideFrame Librarian reference files. Extract design primitives. Produce page-by-page mismatch matrix. Do not redesign.

## Completion Report

### Reference Files Accessed (CarbideFrame Librarian)

| File | Path | Size | Notes |
|------|------|------|-------|
| index.html | `active/librarian/Public/index.html` | 2440 lines | Current bento layout with Overview, Review, External Actions, Plan views |
| styles.css | `active/librarian/Public/styles.css` | ~270KB | Bentos, elevation, motion, shell, cards, status pills, inline stats, state badges |
| theme.css | `active/librarian/Public/theme.css` | ~20KB | Design tokens: colors, spacing, typography, shadows, density, elevation |
| V1X-DESIGN-LANGUAGE.md | `active/librarian/docs/governance/V1X-DESIGN-LANGUAGE.md` | 225 lines | Official V1X design language reference: card anatomy, density, typography, layout |
| BENTO-ELEVATION-MOTION-SPEC | `CarbideFrame/docs/governance/UI-OVERVIEW-BENTO-ELEVATION-MOTION-SPEC.md` | 594 lines | Bento layout, elevation hierarchy, motion rules spec |

### Concrete Design Primitives Extracted from Current Librarian

| Primitive | Current Librarian | QA Pilot (Current) |
|-----------|------------------|-------------------|
| **Shell** | `.app-shell` — fixed grid: toolbar/sidebar+main+inspector/status-strip | Single-scroll, no shell grid |
| **Toolbar** | `.app-toolbar` — flat bg, brand icon+name, workspace label, command palette, mode toggle, status indicators, owner queue | `.topbar`/`.portal-topbar` — gradient bg, brand+lang toggle only |
| **Bento cards** | 3-tier hierarchy: `card-attention` (elevated shadow+border+blur) > `card-active` (subtle shadow) > `card-flat` (no shadow) | `.card` (uniform) — all same level, no hierarchy |
| **Card anatomy** | Eyebrow `.panel-purpose-label` + Title row + Body + Basis/TrustSpine footer | Heading `h2` + description `p` + content |
| **Status chips** | `.status-pill` with ok/warn/bad/neutral variants; `.view-state-badge` | `.status-badge` with limited variants |
| **Color palette** | Dark theme (warm graphite + antique gold) + Light theme (warm paper + blue accent) | Light theme only (blue primary #2563eb) |
| **Typography** | `--font-ui`: -apple-system + BlinkMacSystemFont; `--font-mono`: SF Mono; `--font-display`: Georgia | `--font-sans`: similar; `--font-mono`: Courier New |
| **Spacing** | 4px grid; `--space-1` through `--space-7`, density-responsive | 4px grid; `--space-1` through `--space-16`, static |
| **Elevation** | Shadow-based hierarchy with 3 levels; warm paper backgrounds | Border-based differentiation; uniform `--shadow-sm` |
| **Motion** | `--motion-card-entrance: 250ms`, `--motion-card-stagger: 40ms`, `fade-up` animation, reduced-motion support | `--motion-card-entrance` exists but not applied to all pages |
| **Data footer** | `.view-data-footer` — mono, source tag, data source/build info (every page) | `.view-data-footer` — added in prior epic, present on all pages |
| **Source chips** | `.view-source-tag` — inline mono tag showing data source | Not present |
| **Workbench layout** | Asymmetrical bento: attention card (largest) + active work (medium) + flat cards | Uniform card grid; admin tabs |

### QA Pilot Pages Inspected

All 8 pages inspected against current Librarian reference.

### Exact Visual Mismatches Found

| Mismatch | Severity | QA Pilot | Librarian Reference |
|----------|----------|----------|-------------------|
| **M1 — Blue marketing hero** | Critical | `index.html`: blue gradient hero (#1e3a8a→#2563eb→#3b82f6) with centered CTA cards and emoji icons | No hero page — app opens directly to Overview bento/workbench with warm paper background |
| **M2 — Emoji CTA iconography** | High | All pages use emoji icons (🚀, 📦, 🛠️, 👥, 📚, 📥) | No emoji icons anywhere in the current Librarian UI |
| **M3 — Uniform card level** | High | All cards `.card`, `.admin-card`, `.card-attention`/`active`/`flat` exist in CSS but not all pages use them in bento layout | 3-tier bento hierarchy: attention (elevated shadow, warm bg) > active (subtle shadow) > flat (no shadow) |
| **M4 — Gradient topbar** | Medium | `admin.html` topbar uses `linear-gradient(90deg,#fff,#f9fafb)` border-bottom `2px solid #e5e7eb` | Flat toolbar with `--color-bg-secondary`, `--border-width-thin` border |
| **M5 — No warm paper ambient** | Medium | White/blue-gray background (`#f4f6fb`) | Warm light background gradient (`--bg-gradient-warm` radial) |
| **M6 — Header lacks structure** | Medium | No `.panel-purpose-label` eyebrow on most pages | Every card/view has an eyebrow label + title |
| **M7 — Source-chip absent** | Low | No source/tag labels on data areas | `view-source-tag` inline mono chip showing data origin |
| **M8 — Font-mono stack** | Low | `--font-mono: 'Courier New', Courier, monospace` | `--font-mono: SF Mono, Menlo, Monaco, "Cascadia Code", Consolas, monospace` |
| **M9 — Identity note style** | Low | Yellow warning border (`#fffbeb` + `#fde68a`) | No equivalent — local identity conveyed via data-footer source chips |
| **M10 — Status-indicator style** | Low | `.status-pill` added but not used on all pages | Consistent `.status-pill` + dot indicators across toolbar |

### Unsupported Prior Design Claims

| Claim from prior epic | Evaluation |
|----------------------|------------|
| "Design tokens merged from Librarian" | Partially correct — some tokens added but the **visual result** does not match the current Librarian. The current Librarian uses warm paper/amber instead of blue/white-gray. |
| "Bento card hierarchy added" | CSS classes exist but the actual page layout is still uniform — not asymmetrical bento. |
| "All pages refreshed with data footers" | ✅ Correct — `.view-data-footer` present on all pages. |
| "Panel-purpose-labels added" | ✅ CSS exists — not yet applied to all pages. |
| "Status pill components added" | ✅ CSS exists — `.status-pill`, `.view-state-badge` present. |

### Recommended Remediation Order

1. **Landing page shell** (Sprint 2): Replace the blue gradient hero with a Librarian-aligned bento workbench surface. Remove emoji icons. Apply warm paper background. Add source chips.
2. **Admin dashboard** (Sprint 3): Apply bento tier hierarchy to admin cards. Use `.card-attention` for workspace overview, `.card-active` for activity, `.card-flat` for recent results.
3. **Learner pages** (Sprint 3): Apply same bento primitives to catalog and identity.
4. **Course runtime** (Sprint 3): Keep two-column layout but apply elevation and section rhythm.
5. **Export/import/certificate** (Sprint 4): Apply data footers (already done), section rhythm, and source chips.

### Validation Evidence

All 8 QA Pilot pages inspected and compared against current Librarian reference. Mismatch matrix covers 10 findings (M1-M10).

### Unresolved Issues

| Issue | Impact | Sprint |
|-------|--------|--------|
| QA Pilot's blue primary may need alignment to Librarian light-theme blue | Visual consistency | Sprint 2 |
| Font-mono stack still uses Courier New | Minor visual | Sprint 2 |
| I18N epic (#148-#152) paused — not sealed | I18N deferred | After visual parity |
