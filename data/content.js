/**
 * =============================================================================
 * content.js — Single Source of Truth for All Editable Text
 * =============================================================================
 * QA Onboarding Training Platform
 *
 * PURPOSE:
 * Provides a central configuration object for all text labels, messages, and
 * course metadata. This allows Admins to customize the platform terminology
 * and templates without modifying the core logic.
 *
 * HOW TO USE:
 * call loadContent() to get the current configuration (merged with any local
 * Admin overrides).
 *
 * READS FROM:   localStorage ('qa_content')
 * WRITES TO:    localStorage ('qa_content')
 * =============================================================================
 */

// ── SECTION 1: DEFAULT CONTENT ────────────────────────────────────────────────

const DEFAULT_CONTENT = {
  fieldLabels: {
    caseTitle: "Case Title",
    status: "Status",
    priority: "Priority",
    dateOpened: "Date Opened",
    investigationNotes: "Investigation Notes",
    escalated: "Escalated",
    escalationReason: "Escalation Reason",
    outcome: "Outcome / Resolution",
    assignedTo: "Assigned To",
  },
  dropdownOptions: {
    status: ["Open", "In Progress", "Pending Review", "Resolved", "Closed"],
    priority: ["Critical", "High", "Medium", "Low"],
    escalationReason: ["Policy Breach", "Senior Review Required", "Client Complaint", "Regulatory"],
  },
  validationMessages: {
    caseTitleRequired: "Case title is required.",
    caseTitleMaxLength: "Case title cannot exceed 120 characters.",
    dateOpenedRequired: "Date opened is required.",
    dateOpenedFuture: "Date opened cannot be a future date.",
    escalationReasonRequired: "Escalation reason is required when a case is marked as escalated.",
    outcomeRequired: "Outcome is required before a case can be marked as Resolved or Closed.",
    juniorCannotClose: "You do not have permission to resolve or close cases.",
    assignedToNotFound: "No investigators found.",
  },
  toastMessages: {
    caseSaved: "Case saved successfully.",
    autoSaved: "Saved",
  },
  sidebarLabels: {
    caseId: "Case ID",
    assignedTo: "Assigned To",
    role: "Role",
    dateOpened: "Date Opened",
    lastUpdated: "Last Updated",
    status: "Status",
    timeline: "Timeline",
  },
  roleNames: {
    senior: "Senior Investigator",
    junior: "Junior Investigator",
  },
  certificate: {
    issuerName: "Agile Testing Team",
    congratsEmail: `Subject: Congratulations on Completing the QA Onboarding Training

Dear [STUDENT NAME],

We are pleased to confirm that you have successfully completed all required
lessons and assessments in the [COURSE NAME].

Your certificate of completion is attached to this email.

This achievement reflects your commitment to quality and your readiness to
contribute to the team's testing practice. We look forward to working with you.

Congratulations and welcome to the team.

[Issuing Manager Name]
[ISSUER NAME]`,
  },
  courseMetadata: {
    courseName: "QA Onboarding Training",
    lessons: [
      { id: "lesson-1", title: "Testing 101",            type: "true-false" },
      { id: "lesson-2", title: "Acceptance Criteria",    type: "multiple-choice" },
      { id: "lesson-3", title: "Dynamics 365 CRM",       type: "multiple-choice" },
      { id: "lesson-4", title: "Azure DevOps",           type: "scenario" },
      { id: "lesson-5", title: "Test Planning & Triage", type: "multiple-choice" },
      { id: "capstone", title: "Capstone Assessment",    type: "capstone" },
    ],
  },
};

// ── SECTION 2: CONTENT LOADER ─────────────────────────────────────────────────

function loadContent() {
  const saved = localStorage.getItem('qa_content');
  if (!saved) return DEFAULT_CONTENT;
  try {
    const parsed = JSON.parse(saved);
    return deepMerge(DEFAULT_CONTENT, parsed);
  } catch (error) {
    return DEFAULT_CONTENT;
  }
}

function saveContent(contentObject) {
  try {
    localStorage.setItem('qa_content', JSON.stringify(contentObject));
    return true;
  } catch (error) { return false; }
}

function resetContent() {
  localStorage.removeItem('qa_content');
}

// ── SECTION 3: UTILITIES ──────────────────────────────────────────────────────

function deepMerge(target, source) {
  const result = Object.assign({}, target);
  for (const key in source) {
    if (source.hasOwnProperty(key)) {
      if (source[key] !== null && typeof source[key] === 'object' && !Array.isArray(source[key]) && typeof target[key] === 'object' && !Array.isArray(target[key])) {
        result[key] = deepMerge(target[key], source[key]);
      } else {
        result[key] = source[key];
      }
    }
  }
  return result;
}
