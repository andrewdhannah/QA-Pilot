# EPIC-QA-PILOT-DESIGN-LANGUAGE-REFRESH-1 — Design Language Convergence

**Status:** ✅ Sealed — Owner-approved 2026-07-09 per OD-EPIC-QA-PILOT-DESIGN-LANGUAGE-REFRESH-1-BATCH-SEAL
**Decision ID:** `OD-EPIC-QA-PILOT-DESIGN-LANGUAGE-REFRESH-1-AUTHORIZATION`
**Receipt:** `receipts/decision-resolutions/od-epic-qa-pilot-design-language-refresh-1-authorization.json`
**Authorization type:** Bounded continuation (7 sprints)

---

## Purpose

Bring QA Pilot's browser-only frontend up to the same design quality standard as the current Librarian dashboard, while preserving QA Pilot's Academy/training identity and sealed browser-only workflow.

## Design Direction

Use the current Librarian dashboard design language as the quality reference:

| Principle | Description |
|-----------|-------------|
| **Bento card hierarchy** | Elevated attention cards (Owner Queue) > standard cards (Active Work) > flat cards (system health, recent changes) |
| **Calmer spacing** | Consistent vertical rhythm, generous padding, separation between sections |
| **Native-feeling panels** | OS-native feel using -apple-system font, frosted glass where appropriate, restrained borders |
| **Readiness/status strips** | Compact horizontal strips with pill indicators for system state |
| **Restrained motion** | Subtle entrance animations, card stagger, pulse only for attention items |
| **Readable typography** | Clear hierarchy (eyebrow > title > body > meta), comfortable line height |
| **Strong action hierarchy** | Primary actions clearly distinguished from secondary, tertiary |
| **Consistent light theme** | QA Pilot is light-theme-native — white/cream backgrounds, subtle warm borders |
| **Polished workflows** | Owner/Admin action surfaces, learner portal, course runtime all at same quality level |

## What QA Pilot Must Retain

- ✅ Browser-only static deployment (open file:// in browser)
- ✅ Academy/training product identity ("QA Pilot Academy")
- ✅ JSON import/export custody model (deployment-v1, result-v1 schemas)
- ✅ Local learner identity only
- ✅ No backend
- ✅ No install
- ✅ No server authentication
- ✅ No password/account system
- ✅ No Librarian mutation
- ✅ No cross-project write
- ✅ No autonomous publication

## Sprint Sequence

| # | Sprint | Purpose |
|---|--------|---------|
| 1 | QA-PILOT-DESIGN-LANGUAGE-BASELINE-1 | Design-language baseline: compare against Librarian, define QA Pilot-specific rules, fix two known defects |
| 2 | QA-PILOT-DESIGN-TOKEN-AND-SHELL-REFRESH-1 | Update shared CSS tokens, page shell, typography, spacing, header, cards |
| 3 | QA-PILOT-ADMIN-DASHBOARD-DESIGN-REFRESH-1 | Redesign admin.html around dashboard/bento layout |
| 4 | QA-PILOT-LEARNER-PORTAL-DESIGN-REFRESH-1 | Refresh catalog.html and identity.html |
| 5 | QA-PILOT-COURSE-RUNTIME-DESIGN-REFRESH-1 | Refresh course-view.html with better lesson nav, sources, progress |
| 6 | QA-PILOT-EXPORT-IMPORT-CERTIFICATE-DESIGN-REFRESH-1 | Refresh export.html, import.html, certificate.html |
| 7 | QA-PILOT-DESIGN-LANGUAGE-ROUNDTRIP-VALIDATION-1 | Re-run full roundtrip + design/i18n validation |

## Known Defects to Repair

1. **Defect #1 (medium):** EN/FR language toggle does not render because `renderLangToggle()` is called with a DOM element object instead of the expected string container ID. Affects all 8 pages.
2. **Defect #2 (low):** `export.html` and `import.html` are missing "QA Pilot Academy" title branding and favicon references.

## Design Reference: Librarian Dashboard

The Librarian dashboard (`Public/index.html`, `theme.css`, `styles.css`) provides the quality reference:

- Theme: warm light (gold/cream palette with blue accent for QA Pilot's light-native context)
- Cards: bento hierarchy with elevation tokens (`--elev-bg-owner-queue`, `--elev-shadow-*`)
- Status: pill-based readiness strip (`os-pill os-pill-ok`, `os-pill os-pill-info`)
- Typography: -apple-system, clear size scale, letter-spacing tokens
- Motion: entrance animations, card stagger, pulse for attention items
- Spacing: 4px grid scale, CSS custom properties for all dimensions

## Stop Conditions

Stop and report immediately if:
- the design refresh breaks the 22-step browser-only roundtrip
- any page requires backend/server/auth
- JSON custody is bypassed
- local identity is presented as real authentication
- the design replaces QA Pilot's training identity instead of refining it
- Librarian canonical files must be mutated
- sprint order or scope needs to change
