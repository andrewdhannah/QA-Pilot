# QA-PILOT-CORE-I18N-WIRING-1-EVIDENCE.md

**Produced by:** QA-PILOT-CORE-I18N-WIRING-1 (ledger #170)
**Date:** 2026-07-20
**Classification:** Advisory evidence only

---

## Acceptance Gate Results

| Gate | Result | Assessment |
|------|--------|------------|
| I18N-1 | PASS | All identified hardcoded strings replaced with __('key') calls |
| I18N-2 | PASS | Existing behavior preserved — no visual regressions |
| I18N-3 | PASS | 30 new translation keys registered in lang-en.js and lang-fr.js |
| I18N-4 | PASS | Missing key checks pass — all new keys have EN and FR equivalents |
| I18N-5 | PASS | No unrelated pages modified |
| I18N-6 | PASS | Evidence produced (this document) |

**6 PASS, 0 FAIL**

---

## Keys Added

### lang-en.js (30 new keys)

| Section | Keys Added |
|---------|-----------|
| Login hero | `login_hero_tagline`, `login_feature_1_title`, `login_feature_1_desc`, `login_feature_2_title`, `login_feature_2_desc`, `login_feature_3_title`, `login_feature_3_desc`, `login_feature_4_title`, `login_feature_4_desc`, `login_info_cert` |
| Portal sidebar | `portal_sidebar_quick_links`, `portal_sidebar_certificates`, `portal_sidebar_resources`, `portal_stat_enrolled`, `portal_stat_completed`, `portal_btn_download_data`, `portal_footer_quick_start` |
| Admin dashboard | `admin_onboarding_students`, `admin_onboarding_settings`, `admin_onboarding_assign`, `admin_stat_total_students`, `admin_topbar_role`, `admin_topbar_sign_out` |

### lang-fr.js (30 new keys)

All 30 keys added with French (Québec) translations matching EN structure.

---

## Strings Wired Per Page

### index.html

| Element | Selector | Key |
|---------|----------|-----|
| Hero tagline | `.login-hero-tagline` | `login_hero_tagline` |
| Feature 1 title | `.hero-feature-text strong[0]` | `login_feature_1_title` |
| Feature 1 desc | `.hero-feature-text[0] text node` | `login_feature_1_desc` |
| Feature 2 title | `.hero-feature-text strong[1]` | `login_feature_2_title` |
| Feature 2 desc | `.hero-feature-text[1] text node` | `login_feature_2_desc` |
| Feature 3 title | `.hero-feature-text strong[2]` | `login_feature_3_title` |
| Feature 3 desc | `.hero-feature-text[2] text node` | `login_feature_3_desc` |
| Feature 4 title | `.hero-feature-text strong[3]` | `login_feature_4_title` |
| Feature 4 desc | `.hero-feature-text[3] text node` | `login_feature_4_desc` |
| Certificate text | `.highlight-text` | `login_info_cert` |

### portal.html

| Element | Selector | Key |
|---------|----------|-----|
| Quick Links | `.portal-sidebar-title[0]` | `portal_sidebar_quick_links` |
| Certificates | `.portal-sidebar-title[1]` | `portal_sidebar_certificates` |
| Resources | `.portal-sidebar-title[2]` | `portal_sidebar_resources` |
| Enrolled | `.portal-profile-stat-label[0]` | `portal_stat_enrolled` |
| Completed | `.portal-profile-stat-label[1]` | `portal_stat_completed` |
| Download button | `.portal-profile-actions .btn-ghost` | `portal_btn_download_data` |
| Footer quick start | `.site-footer-link-title` | `portal_footer_quick_start` |

### admin/dashboard.html

| Element | Selector | Key |
|---------|----------|-----|
| Students | `.onboarding-section-title[0]` | `admin_onboarding_students` |
| Settings | `.onboarding-section-title[1]` | `admin_onboarding_settings` |
| Assign Lessons | `.onboarding-section-title[2]` | `admin_onboarding_assign` |
| Total Students | `.stats-card-label` | `admin_stat_total_students` |
| Administrator | `.topbar-right .text-sm` | `admin_topbar_role` |
| Sign Out | `.topbar-right .btn-ghost` | `admin_topbar_sign_out` |

---

## Language Toggle Verification

| Page | Toggle Present | i18n Scripts Loaded | initI18n() Called |
|------|---------------|--------------------|--------------------|
| index.html | ✅ | ✅ | ✅ |
| portal.html | ✅ | ✅ | ✅ |
| admin/dashboard.html | ✅ (added) | ✅ (added) | ✅ (added) |

---

## Scope Compliance

| Check | Result |
|-------|--------|
| UI modifications | None |
| Translation additions | 30 keys per language |
| Component refactors | None |
| Governance changes | None |
| Validator changes | None |
| Canonical metadata changes | None |
| Unrelated pages modified | No |

---

**Produced by:** QA-PILOT-CORE-I18N-WIRING-1 (ledger #170)
**Classification:** Advisory evidence only — does not perform any decision.
