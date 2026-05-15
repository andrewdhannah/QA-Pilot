/**
 * =============================================================================
 * pdf-lib.js — Certificate and Email Template Generation
 * =============================================================================
 * QA Onboarding Training Platform
 *
 * PURPOSE:
 * Handles certificate PDF generation and email template building.
 * Used only by certificate.html.
 *
 * PDF APPROACH:
 * Uses window.print() — the browser's built-in print dialog.
 * This requires zero external dependencies, matching the project constraint.
 *
 * EMAIL TOKEN REFERENCE:
 * The congratsEmail template in content.js uses these tokens:
 *   [STUDENT NAME]  — replaced with the student's full name
 *   [COURSE NAME]   — replaced with the course name
 *   [ISSUER NAME]   — replaced with the issuer name from Admin settings
 *   [Issuing Manager Name] — left as-is for Admin to fill in manually
 *
 * LOAD ORDER:
 * Load AFTER content.js and app.js. Requires loadContent() to be available.
 * =============================================================================
 */

// ── SECTION 1: CERTIFICATE GENERATION ─────────────────────────────────────────

/**
 * generateCertificate()
 * Opens the browser print dialog so the student can save the certificate as PDF.
 * 
 * @returns {void}
 */
function generateCertificate() {
  // Delay ensures DOM is settled before the print snapshot is taken.
  setTimeout(function() {
    window.print();
  }, 100);
}

// ── SECTION 2: EMAIL TEMPLATE GENERATION ──────────────────────────────────────

/**
 * getEmailTemplate(studentName, issuerName, courseName)
 * Returns the congratulations email body with all tokens replaced.
 * 
 * @param {string} studentName - The student's full name.
 * @param {string} issuerName  - Issuing organisation.
 * @param {string} courseName  - Course name.
 * @returns {string} The complete email body.
 */
function getEmailTemplate(studentName, issuerName, courseName) {
  var content = loadContent();
  var template = content.certificate.congratsEmail;

  // Use regex /g to replace all occurrences of the tokens.
  template = template.replace(/\[STUDENT NAME\]/g, studentName);
  template = template.replace(/\[COURSE NAME\]/g,  courseName);
  template = template.replace(/\[ISSUER NAME\]/g,  issuerName);

  return template;
}
