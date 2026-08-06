/**
 * =============================================================================
 * lang-en.js — English (EN) UI Strings
 * =============================================================================
 * QA Pilot — Bilingual English Dictionary
 *
 * PURPOSE:
 * Defines the LANG_EN object containing all user-facing English strings.
 * Used by the __() translation function in i18n.js to render UI text.
 *
 * KEYS:
 * - Keys are organised by page/feature prefix for clarity.
 * - Use {0}, {1} placeholders for dynamic values.
 * - Keep all UI text here — no hardcoded English strings in HTML or JS.
 *
 * NOTE:
 * This file must be loaded AFTER i18n.js in every page's script tag sequence.
 * =============================================================================
 */

var LANG_EN = {

  // ── GLOBAL / SHARED ─────────────────────────────────────────────────────────

  // Language toggle
  'lang_en': 'EN',
  'lang_fr': 'FR',

  // Page titles
  'page_title_index.html':          'QA Pilot Academy',
  'page_title_portal.html':         'QA Pilot Academy \u2014 Training Portal',
  'page_title_course-view.html':    'QA Pilot \u2014 Course Viewer',

  // App branding
  'app_name':             'QA Pilot Academy',
  'app_name_short':       'QA Pilot',
  'app_brand_training':   'QA Pilot Academy',


  // ── LOGIN PAGE (index.html) ─────────────────────────────────────────────────

  'login_subtitle':             'Sign in to continue your training.',
  'login_email_label':          'Email address',
  'login_email_placeholder':    'your.name@example.com',
  'login_password_label':       'Password',
  'login_password_placeholder': 'Enter your password',
  'login_sign_in':              'Sign in',
  'login_signing_in':           'Signing in\u2026',
  'login_admin_link':           'Administrator sign in',
  'login_password_reset_note':  'Password resets are managed by your training coordinator.',
  'login_caps_warning':         'Caps Lock is on.',
  'login_demo_btn':             '\u{1F6E0}\uFE0F Demo Login',
  'login_demo_email':           'demo@qapilot.com',

  // Login page product description
  'login_info_heading':         'What is QA Pilot Academy?',
  'login_info_desc':            'A fully offline, hands-on training platform for Quality Assurance professionals. Learn testing methodology, bug reporting, CRM tools, Azure DevOps, and test planning through realistic simulations and guided exercises.',

  // Privacy notice
  'login_privacy':              'Your training data is stored locally on this device and is not transmitted anywhere.',

  // Login errors
  'login_error_empty':          'Please enter your email address and password.',
  'login_error_email_not_found':'Email address not found. Please check and try again.',
  'login_error_deactivated':    'This account has been deactivated. Please contact your administrator.',
  'login_error_wrong_password': 'Incorrect password. Please try again.',
  'login_error_db':             'Unable to connect to the database. Please try refreshing the page.',
  'login_error_generic':        'An error occurred. Please refresh the page and try again.',




  // ── PORTAL PAGE (portal.html) ───────────────────────────────────────────────

  'portal_welcome':             'Welcome, {0}!',
  'portal_welcome_sub':         'Pick up where you left off or explore a new course.',
  'portal_welcome_sub_first':   'Ready to start your QA training journey? Browse a course below and enroll to get started.',
  'portal_my_learning':         'My Learning',
  'portal_my_learning_empty':   'You are not enrolled in any courses yet. Browse the catalog below and click a course to get started!',
  'portal_available_courses':   'Available Courses',
  'portal_sign_out':            'Sign Out',
  'portal_loading':             'Loading your courses\u2026',
  'portal_no_courses':          'No additional courses available at this time.',
  'portal_error':               'Something went wrong loading the portal. Please refresh the page.',
  'portal_admin_dashboard':     'Go to Admin Dashboard \u2192',

  // Course card labels
  'portal_modules':             '{0} modules',
  'portal_lessons':             '{0} lessons',
  'portal_estimated_min':       '~{0} min',
  'portal_progress':            'Progress',
  'portal_completed':           '\u2713 Completed',
  'portal_continue_hint':       'Continue',
  'portal_view_certificate':    'View Certificate \u2192',
  'portal_start_course':        'Start Course \u2192',
  'portal_enroll_free':         'Enroll \u2014 Free',
  'portal_enrolling':           'Enrolling\u2026',
  'portal_enrolled_success':    'Successfully enrolled!',
  'portal_enrolled_fail':       'Failed to enroll. Please try again.',
  'portal_course_not_found':    'Course not found.',

  // Portal category fallback
  'portal_category_general':    'General',

   // Portal category headings (shown above grouped course sections)
   'portal_cat_QA_title':        'QA Fundamentals',
   'portal_cat_QA_desc':         'Courses focused on quality assurance testing skills and best practices.',
   'portal_cat_Fundamentals_title': 'Fundamentals',
   'portal_cat_Fundamentals_desc':  'Core QA skills including acceptance criteria, CRM, and DevOps basics.',
    'portal_cat_Tools & Process_title': 'Tools & Process',
    'portal_cat_Tools & Process_desc':  'Training on specific tools and processes used in QA workflows.',
   'portal_cat_Development_title': 'Development & Collaboration',
   'portal_cat_Development_desc':  'Courses covering development methodologies and team collaboration practices.',
   'portal_cat_Scenarios_title':   'Scenarios',
   'portal_cat_Scenarios_desc':    'Real-world scenario-based courses for practical QA experience.',


  // ── COURSE VIEWER (course-view.html) ────────────────────────────────────────

  'cv_back':                    '\u2190 Back',
  'cv_percent_done':            '{0}% done',
  'cv_loading':                 'Loading\u2026',

  // Welcome screen
  'cv_welcome_title':           'Select a lesson to begin',
  'cv_welcome_desc':            'Choose a module from the sidebar and click a lesson to start learning. Your progress is saved automatically.',

  // Sidebar
  'cv_module':                  'Module {0}',
  'cv_no_modules':              'No modules found.',
  'cv_read':                    'Read',
  'cv_quiz':                    'Quiz',
  'cv_practice':                'Practice',
  'cv_exam':                    'Exam',

  // Navigation
  'cv_previous':                '\u2190 Previous',
  'cv_mark_complete':           'Mark Complete \u2192',
  'cv_completed':               '\u2713 Completed',
  '__prev__':                   '\u2190 Previous',
  '__next__':                   'Next \u2192',
  'cv_saving':                  'Saving\u2026',

  // Errors
  'cv_error_not_found':         'Course not found. It may have been removed or the link may be incorrect.',
  'cv_error_load':              'Unable to load course data. Please refresh.',
  'cv_error_save':              'Error saving progress.',
  'cv_error_module_locked':     'Complete the previous module first.',

  // Quiz
  'cv_quiz_intro':              '{0} questions \u2014 you\'ll see the correct answer after each one.',
  'cv_quiz_question_of':        'Question {0} of {1}',
  'cv_quiz_correct':            '\u2705 Correct!',
  'cv_quiz_incorrect':          '\u274C Incorrect.',
  'cv_quiz_correct_answer':     'The correct answer is:',
  'cv_quiz_next':               'Next question \u2192',
  'cv_quiz_see_results':        '\U0001F4CA See results \u2192',
  'cv_quiz_complete':           '\U0001F4CA Quiz Complete!',
  'cv_quiz_score':              'You got {0} out of {1} ({2}%)',
  'cv_quiz_reset_confirm':      'Reset this quiz? All your current answers will be cleared.',
  'cv_quiz_reset_btn':          '\\U0001F504 Reset Quiz',
  'cv_quiz_retake':             '\\U0001F504 Retake Test',
  'cv_quiz_continue':           'Continue \u2192',
  'cv_quiz_not_available':      'Quiz questions not yet available',
  'cv_quiz_not_available_desc': 'The questions for this module are being prepared.',

  // Placeholder content
  'cv_placeholder_title':       'Lesson content coming soon',
  'cv_placeholder_desc':        'This lesson is being prepared. Check back later for the full content.',

  // Exercise / capstone labels
  'cv_launch_lab':              'Launch {0} \u2192',
  'cv_launch_capstone':         'Open Capstone \u2192',
  'cv_lab_complete_hint':       'Once you complete the lab, return here to proceed to the module quiz.',

  // Course complete
  'cv_course_complete':         'Course complete! \U0001F389',


  // ── SPLASH PAGE (index.html — browser-only) ────────────────────────────────

  'splash_title':               'QA Pilot Academy',
  'splash_hero_heading':        'Browser-Based Training',
  'splash_hero_sub':            'No install \u00B7 No login \u00B7 No server. Complete your training directly in the browser.',
  'splash_solo':                'Start Solo Training',
  'splash_solo_desc':           'Begin immediately \u2014 no account, no team. Progress saved locally.',
  'splash_import':              'Import Team Deployment',
  'splash_import_desc':         'Join a team session. Import the JSON file from your trainer.',
  'splash_admin':               'Admin / Trainer Workspace',
  'splash_admin_desc':          'Create deployments, manage members, import learner results.',
  'splash_import_heading':      'Import Deployment JSON',
  'splash_import_help':         'Select the deployment JSON file sent by your trainer.',
  'splash_import_note':         'Deployment files contain your team roster and assigned training. This is not authentication \u2014 it is local identity selection.',
  'splash_identity_note':       'Local identity, not authentication. QA Pilot does not use passwords, accounts, or servers. Your profile is stored in this browser only. Team identity comes from the deployment file \u2014 not from a login system.',
  'splash_resume_welcome':      'Welcome back{0}',
  'splash_resume_desc':         'You have training in progress. Continue where you left off?',
  'splash_resume_btn':          'Resume',
  'splash_footer':              'QA Pilot Academy \u00B7 Advisory-only training',
  'splash_footer_custody':      'Static browser deployment',
  'splash_footer_no_server':    'No server \u00B7 No install \u00B7 No auth',


  // ── ADMIN PAGE (admin.html) ────────────────────────────────────────────────

  'admin_title':                'QA Pilot Academy \u2014 Admin Dashboard',
  'admin_brand':                'QA Pilot Academy \u2014 Admin',
  'admin_back':                 '\u2190 Back',
  'admin_no_workspace':         'No workspace',
  'admin_dashboard':            'Dashboard',
  'admin_workspace':            'Workspace',
  'admin_members':              'Members',
  'admin_packages':             'Packages',
  'admin_deploy':               'Deploy',
  'admin_results':              'Results',

  // Dashboard
  'admin_dash_label':           'ADMIN DASHBOARD',
  'admin_dash_overview':        'Overview',
  'admin_dash_workspace_label': 'WORKSPACE',
  'admin_dash_activity_label':  'ACTIVITY',
  'admin_dash_recent_label':    'RECENT RESULTS',
  'admin_dash_ws_desc':         'Current admin workspace status and quick actions.',
  'admin_dash_activity_desc':   'Team and package summary. Use the tabs above to manage each area.',
  'admin_dash_manage_members':  'Manage Members',
  'admin_dash_create_deploy':   'Create Deployment',
  'admin_dash_view_results':    'View All Results \u2192',
  'admin_dash_no_results':      'No results imported yet. Deploy training, collect learner results, then import them here.',
  'admin_dash_last_import':     'Last import: {0} file(s), {1} result(s), {2} learner(s).',

  // Workspace tab
  'admin_ws_heading':           'Workspace Setup',
  'admin_ws_desc':              'Name your team workspace. This appears in deployment JSON files sent to learners.',
  'admin_ws_label':             'Workspace Name',
  'admin_ws_placeholder':       'e.g., Q1 Training Team',
  'admin_ws_save':              'Save Workspace',
  'admin_ws_saved':             '\u2705 Saved',

  // Members tab
  'admin_member_heading':       'Team Members',
  'admin_member_desc':          'Add learners who will receive this deployment. Each member selects their identity locally \u2014 no accounts or passwords needed.',
  'admin_member_name_label':    'Display Name',
  'admin_member_name_placeholder': 'e.g., Alice',
  'admin_member_id_label':      'Local ID',
  'admin_member_id_placeholder': 'auto-generated',
  'admin_member_add':           'Add Member',
  'admin_member_none':          'No members yet.',

  // Packages tab
  'admin_pkg_heading':          'Assign Training Packages',
  'admin_pkg_desc':             'Select packages to include in the deployment. Only training packs loaded in browser storage are shown.',
  'admin_pkg_none':             'No packages in browser storage. Load content first.',

  // Deploy tab
  'admin_deploy_heading':       'Deploy',
  'admin_deploy_desc':          'Generate a deployment JSON file to share with your learners.',
  'admin_deploy_members':       'Members',
  'admin_deploy_packages':      'Packages',
  'admin_deploy_workspace':     'Workspace',
  'admin_deploy_generate':      'Generate & Download Deployment JSON',
  'admin_deploy_preview_empty': 'Configure workspace, members, and packages above, then generate the deployment.',

  // Results tab
  'admin_results_heading':      'Learner Results',
  'admin_results_desc':         'Import result JSON files returned by learners to track completion.',
  'admin_results_import_label': 'Import Result File',
  'admin_results_none':         'No results imported. Import a learner result JSON file above.',
  'admin_results_imported':     'Imported {0} result(s) from {1}',
  'admin_results_advisory':     'All results advisory. Trainer/Owner review required before use.',

  // Admin identity note
  'admin_identity_note':        'Local admin workspace only. This workspace exists in your browser. Team identities are exported via deployment JSON. No accounts, no passwords, no server.',

  // Admin data footer
  'admin_footer_source':        'Data source: local browser',
  'admin_footer_identity':      'Identity: admin workspace',
  'admin_footer_advisory':      'All data advisory',


  // ── IDENTITY PAGE (identity.html) ──────────────────────────────────────────

  'identity_title':             'QA Pilot Academy \u2014 Select Identity',
  'identity_heading':           'Select Your Identity',
  'identity_loading':           'Loading deployment information...',
  'identity_no_deployment':     'No deployment found. Import a team deployment JSON from the home screen first.',
  'identity_no_members':        'No members in this deployment.',
  'identity_workspace_info':    'Workspace: {0} \u00B7 {1} members',
  'identity_member_heading':    'Team Members',
  'identity_member_desc':       'Choose your name from the deployment roster to begin training.',
  'identity_confirm':           'Confirm Identity \u2192',
  'identity_note':              'Local identity only. You are selecting from a pre-loaded roster. No password, no account, no server. This selection is stored locally in your browser.',
  'identity_footer_source':     'Data source: local browser',
  'identity_footer_identity':   'Identity: learner roster',
  'identity_footer_advisory':   'All data advisory',


  // ── CATALOG / TRAINING PORTAL (catalog.html) ─────────────────────────────

  'catalog_title':              'QA Pilot Academy \u2014 Training Portal',
  'catalog_heading':            'My Training',
  'catalog_hero_desc':          'Complete your assigned training packages. Progress is saved automatically in your browser.',
  'catalog_learner_loading':    'Loading...',
  'catalog_not_signed_in':      'Not signed in',
  'catalog_no_profile':         'No profile found. Start from the home screen first.',
  'catalog_in_progress':        'In Progress',
  'catalog_completed':          'Completed',
  'catalog_completed_count':    'Completed ({0})',
  'catalog_no_packages':        'No training packages assigned yet. If you joined via team deployment, ensure the file included packages.',
  'catalog_all_complete':       'All training complete! Check the completed section above.',
  'catalog_assigned':           'Assigned',
  'catalog_in_progress_label':  'In Progress',
  'catalog_complete_label':     'Complete',
  'catalog_continue':           'Continue working through this training package.',
  'catalog_completed_text':     'Completed successfully.',
  'catalog_home':               '\u2190 Home',
  'catalog_footer_source':      'Data source: local browser',
  'catalog_footer_identity':    'Identity: learner profile',
  'catalog_footer_advisory':    'All data advisory',
  'catalog_identity_note':      'Local learner identity. You are {0}. Your progress is stored in this browser only. No accounts, no passwords, no server.',


  // ── COURSE RUNTIME (course-view.html) ─────────────────────────────────────

  'course_title':               'QA Pilot Academy \u2014 Course View',
  'course_catalog_link':        '\u2190 Catalog',
  'course_welcome_title':       'Select a section to begin',
  'course_welcome_desc':        'Choose a section from the sidebar to start learning. Your progress is saved automatically.',
  'course_package_not_found':   'Package not found',
  'course_no_content':          'Run the content sync tool first, then reload this page.',
  'course_no_sections':         'No sections',
  'course_breadcrumb':          'Section {0} of {1}',
  'course_percent_done':        '{0}% done',
  'course_previous':            '\u2190 Previous',
  'course_next':                'Next \u2192',
  'course_mark_complete':       'Mark Complete \u2713',
  'course_finish':              'Finish \u2713',
  'course_no_sources':          'No sources listed',
  'course_exercise_title':      'Exercise {0}',
  'course_exercise_placeholder':  'Type your answer here...',
  'course_exercise_expected':   'Expected: {0}',
  'course_exercise_submit':     'Submit',
  'course_exercise_correct':    '\u2705 Recorded. Compare your answer against the expected outcome above.',
  'course_exercise_incorrect':  '\u274C Please provide a more detailed answer before submitting.',
  'course_footer_source':       'Data source: local browser',
  'course_footer_advisory':     'Training content advisory',
  'course_footer_progress':     'Progress saved locally',


  // ── CERTIFICATE PAGE (certificate.html) ───────────────────────────────────

  'cert_title':                 'QA Pilot Academy \u2014 Certificate',
  'cert_badge':                 'Certificate of Completion',
  'cert_awarded_to':            'Awarded to: {0}',
  'cert_package':               'Package',
  'cert_completed':             'Completed',
  'cert_learner':               'Learner',
  'cert_deployment':            'Deployment',
  'cert_type':                  'Type',
  'cert_advisory':              'Advisory completion',
  'cert_print':                 '\uD83D\uDDD0\uFE0F Print',
  'cert_back':                  '\u2190 Back to Training',
  'cert_advisory_note':         'Advisory completion record. This certificate is generated from local browser data and is not an official certification. Trainer/Owner review required for any formal use.',
  'cert_footer_source':         'Data source: local browser',
  'cert_footer_type':           'Type: advisory completion',
  'cert_footer_note':           'Not an official certification',


  // ── EXPORT PAGE (export.html) ─────────────────────────────────────────────

  'export_title':               'QA Pilot Academy \u2014 Export Results',
  'export_heading':             'Export Results',
  'export_desc':                'Export your completed training as a result JSON file to send to your trainer.',
  'export_none':                'No completed training to export yet.',
  'export_download':            'Download Result JSON',
  'export_note':                'Result JSON. This file contains your training evidence. It is advisory only \u2014 not an approval, not a certification. Your trainer must review it.',
  'export_back':                '\u2190 Back to Training',
  'export_footer_source':       'Data source: local browser',
  'export_footer_schema':       'Schema: result-v1',
  'export_footer_advisory':     'Advisory only',


  // ── IMPORT PAGE (import.html) ─────────────────────────────────────────────

  'import_title':               'QA Pilot Academy \u2014 Import Results',
  'import_heading':             'Import Results',
  'import_desc':                'Import result JSON files returned by learners.',
  'import_files':               'Import Files',
  'import_results':             'Results',
  'import_learners':            'Learners',
  'import_upload_label':        'Import Result File',
  'import_none':                'No results imported. Import a learner result JSON file above.',
  'import_note':                'All results are advisory. Trainer/Owner review required before acting on any result.',
  'import_back':                '\u2190 Admin Workspace',
  'import_footer_source':       'Data source: local browser',
  'import_footer_schema':       'Schema: result-v1',
  'import_footer_advisory':     'Advisory only',


  // ── SHARED / MISC ──────────────────────────────────────────────────────────

  'shared_skip_link':           'Skip to main content',
  'shared_data_source':         'Data source: local browser',
  'shared_build':               'Build: dev',
};

// Auto-register: add LANG_EN to the global scope for i18n.js reference
