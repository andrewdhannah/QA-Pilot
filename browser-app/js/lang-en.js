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
  'page_title_index.html':          'QA Pilot Academy \u2014 Sign In',
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

  // Login page hero section
  'login_hero_tagline':         'Professional QA training that bridges the gap between theory and practice.',
  'login_feature_1_title':      'Industry-Relevant',
  'login_feature_1_desc':       'Real-world testing scenarios',
  'login_feature_2_title':      'Hands-On Labs',
  'login_feature_2_desc':       'Interactive simulators & tools',
  'login_feature_3_title':      'Credentials',
  'login_feature_3_desc':       'Professional certificates',
  'login_feature_4_title':      'Career Ready',
  'login_feature_4_desc':       'Job-focused curriculum',
  'login_info_cert':            'Professional Certificates',

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

  // Portal sidebar
  'portal_sidebar_quick_links': 'Quick Links',
  'portal_sidebar_certificates':'Certificates',
  'portal_sidebar_resources':   'Resources',
  'portal_stat_enrolled':       'Enrolled',
  'portal_stat_completed':      'Completed',
  'portal_btn_download_data':   'Download Student Data',
  'portal_footer_quick_start':  'Student Quick Start',

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


  // ── ADMIN DASHBOARD (admin/dashboard.html) ──────────────────────────────────

  'admin_onboarding_students':  'Students',
  'admin_onboarding_settings':  'Settings',
  'admin_onboarding_assign':    'Assign Lessons',
  'admin_stat_total_students':  'Total Students',
  'admin_topbar_role':          'Administrator',
  'admin_topbar_sign_out':      'Sign Out',

  // ── ADMIN ASSIGN (admin/assign.html) ───────────────────────────────────────

  'admin_assign_title':         'Assign Modules',
  'admin_assign_save':          'Save Assignment',
  'admin_assign_enrollments':   'Student Enrollments',
  'admin_assign_enrolled':      'Enrolled',
  'admin_assign_not_enrolled':  'Not Enrolled',
  'admin_assign_reset':         'Reset to All Modules',
  'admin_assign_action':        'Action',
  'admin_assign_case_id':       'Case ID',
  'admin_general_cancel':       'Cancel',


  // ── ADMIN BUG LAB (admin/bugs.html) ────────────────────────────────────────

  'admin_bug_lab':              'Bug Lab',
  'admin_save_bug_settings':    'Save Bug Settings',
  'admin_bug_config':           'Bug Config',


  // ── ADMIN CONTENT EDITOR (admin/editor.html) ───────────────────────────────

  'admin_content_editor':       'Content Editor',
  'admin_certificate_settings': 'Certificate Settings',
  'admin_save_changes':         'Save Changes',
  'admin_role_names':           'Role Names',
  'admin_junior_role':          'Junior role name',
  'admin_senior_role':          'Senior role name',
  'admin_reset_defaults':       'Reset to Defaults',


  // ── ADMIN TRAINER DASHBOARD (admin/simple.html) ────────────────────────────

  'admin_trainer_dashboard':    'Trainer Dashboard',
  'admin_full_dashboard':       'Full Dashboard',
  'admin_add_students':         'Add Students',
  'admin_default_password':     'Default Password',
  'admin_protect_download':     'Protect & Download Class File',
  'admin_share_team':           'Share with Your Team',
  'admin_download_class_file':  'Download Class File',
  'admin_email_students':       'Email to Students',

  // ── SIMPLE LOGIN (simple-login.html) ───────────────────────────────────────

  'simple_login_hero_desc':     'Your hands-on training platform for software testing, bug reporting, and quality assurance.',
  'simple_login_team_login':    'Team Login',
  'simple_login_subtitle':      'Upload your class file and enter your name to get started.',
  'simple_login_upload':        'Upload Class File',
  'simple_login_upload_hint':   'Click to select the .json file your trainer sent you',
  'simple_login_your_name':     'Your Name',
  'simple_login_name_placeholder': 'Type your name\u2026',
  'simple_login_scenarios':     'Scenarios',
  'simple_login_lessons':       'Lessons',
  'simple_login_unlock_code':   'Unlock Code',
  'simple_login_unlock_placeholder': 'Enter the unlock code from your trainer',
  'simple_login_unlock_hint':   'Your trainer shared this code separately (email, Teams, etc.)',
  'simple_login_login':         'Login',

  // ── QASIMULATOR OS (QASimulator.html / src/os-core.js) ─────────────────────

  'os_app_guide':               'App Guide',
  'os_settings':                'Settings',
  'os_help':                    'Help',
  'os_sign_out':                'Sign Out',
  'os_lock':                    'Lock',
  'os_about':                   'About',
  'os_profile':                 'Profile',
  'os_search':                  'Search',
  'os_apps':                    'Apps',
  'os_desktop':                 'Desktop',
  'os_files':                   'Files',
  'os_clock':                   'Clock',
  'os_notifications':           'Notifications',
  'os_tasks':                   'Tasks',
  'os_calendar':                'Calendar',
  'os_boot_loading':            'Loading\u2026',
  'os_boot_initializing':       'Initializing\u2026',
  'os_lock_hint':               'Click anywhere to unlock',
  'os_lock_enter':              'Enter',
};

// Auto-register: add LANG_EN to the global scope for i18n.js reference
