# QA-PILOT-CORE-I18N-WIRING-1 — Core Page I18N Wiring

**Type:** implementation / i18n wiring
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** implementation
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Dependencies:** #169 reassessment complete (VISUAL-PARITY-REASSESSMENT.md, I18N-REASSESSMENT.md)

---

## Purpose

Wire remaining hardcoded English strings in core pages to the `__('key')` translation function. This is the highest-priority implementation sprint identified by the reassessment.

**Why first:** The translation foundation is solid (103/103 EN/FR keys). The gap is HTML wiring, not translation content. This sprint closes the most visible i18n seam.

---

## Scope

### Pages In Scope

| Page | Hardcoded Strings | Priority |
|------|-------------------|----------|
| `index.html` | ~10 strings | High |
| `portal.html` | ~15 strings | High |
| `admin/dashboard.html` | ~10 strings | Medium |

### Strings to Wire (index.html)

| String | Proposed Key | Location |
|--------|-------------|----------|
| "Professional QA training that bridges the gap..." | `login_hero_tagline` | Hero section |
| "Industry-Relevant" | `login_feature_1_title` | Hero features |
| "Real-world testing scenarios" | `login_feature_1_desc` | Hero features |
| "Hands-On Labs" | `login_feature_2_title` | Hero features |
| "Interactive simulators & tools" | `login_feature_2_desc` | Hero features |
| "Credentials" | `login_feature_3_title` | Hero features |
| "Professional certificates" | `login_feature_3_desc` | Hero features |
| "Career Ready" | `login_feature_4_title` | Hero features |
| "Job-focused curriculum" | `login_feature_4_desc` | Hero features |
| "About QA Pilot Academy" | `login_info_heading` | Info section |
| "Professional Certificates" | `login_info_cert` | Info section |

### Strings to Wire (portal.html)

| String | Proposed Key | Location |
|--------|-------------|----------|
| "Quick Links" | `portal_sidebar_quick_links` | Sidebar |
| "Certificates" | `portal_sidebar_certificates` | Sidebar |
| "Resources" | `portal_sidebar_resources` | Sidebar |
| "My Learning" | `portal_section_my_learning` | Section header |
| "Available Courses" | `portal_section_available_courses` | Section header |
| "Enrolled" | `portal_stat_enrolled` | Profile stats |
| "Completed" | `portal_stat_completed` | Profile stats |
| "Download Student Data" | `portal_btn_download_data` | Button |
| "Sign Out" | `portal_btn_sign_out` | Button |
| "Student Quick Start" | `portal_footer_quick_start` | Footer |

### Strings to Wire (admin/dashboard.html)

| String | Proposed Key | Location |
|--------|-------------|----------|
| "Students" | `admin_onboarding_students` | Onboarding |
| "Settings" | `admin_onboarding_settings` | Onboarding |
| "Assign Lessons" | `admin_onboarding_assign` | Onboarding |
| "Total Students" | `admin_stat_total_students` | Stats |
| "Administrator" | `admin_topbar_role` | Topbar |
| "Sign Out" | `admin_topbar_sign_out` | Topbar |

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| I18N-1 | All identified hardcoded strings replaced |
| I18N-2 | Existing behavior preserved |
| I18N-3 | Translation keys registered |
| I18N-4 | Missing key checks pass |
| I18N-5 | No unrelated pages modified |
| I18N-6 | Evidence produced |

---

## Non-Scope

This sprint must not:

- Add new UI components
- Modify design tokens
- Change page layout
- Add language toggle to other pages
- Modify governance validators
- Change canonical identity

---

## Evidence Contract

This sprint produces exactly:

```
docs/sprints/QA-PILOT-CORE-I18N-WIRING-1-EVIDENCE.md
```

Containing:
- Keys added to language files
- Strings replaced per page
- Language toggle verification
- Visual regression check

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Authorized by:** Andrew Hannah
**Ledger entry:** #170 (authorized)
