/**
 * =============================================================================
 * lang-fr.js — French (FR) UI Strings & Translated Course Content
 * =============================================================================
 * QA Pilot — Bilingual French (Québec) Dictionary
 *
 * PURPOSE:
 * Defines LANG_FR (UI translations) and LANG_CONTENT_FR (French course content).
 * LANG_FR mirrors the keys in LANG_EN with French (Québec) translations.
 * LANG_CONTENT_FR provides French versions of QA Onboarding lesson content.
 *
 * NOTE:
 * This file must be loaded AFTER i18n.js in every page's script tag sequence.
 * =============================================================================
 */

var LANG_FR = {

  // ── GLOBAL / SHARED ─────────────────────────────────────────────────────────

  'lang_en':                          'EN',
  'lang_fr':                          'FR',

  'page_title_index.html':            'Acad\u00e9mie QA Pilot \u2014 Connexion',
  'page_title_portal.html':           'Acad\u00e9mie QA Pilot \u2014 Portail de formation',
  'page_title_course-view.html':      'QA Pilot \u2014 Visualiseur de cours',

  'app_name':                         'Acad\u00e9mie QA Pilot',
  'app_name_short':                   'QA Pilot',
  'app_brand_training':               'Acad\u00e9mie QA Pilot',


  // ── LOGIN PAGE (index.html) ─────────────────────────────────────────────────

  'login_subtitle':                   'Connectez-vous pour continuer votre formation.',
  'login_email_label':                'Adresse courriel',
  'login_email_placeholder':          'prenom.nom@exemple.com',
  'login_password_label':             'Mot de passe',
  'login_password_placeholder':       'Entrez votre mot de passe',
  'login_sign_in':                    'Se connecter',
  'login_signing_in':                 'Connexion en cours\u2026',
  'login_admin_link':                 'Connexion administrateur',
  'login_password_reset_note':        'Les r\u00e9initialisations de mot de passe sont g\u00e9r\u00e9es par votre coordinateur de formation.',
  'login_caps_warning':               'Le Verrouillage majuscule est activ\u00e9.',
  'login_demo_btn':                   '\u{1F6E0}\uFE0F Connexion d\u00e9mo',
  'login_demo_email':                 'demo@qapilot.com',

  'login_info_heading':               'Qu\u2019est-ce que l\u2019Acad\u00e9mie QA Pilot\u00a0?',
  'login_info_desc':                  'Une plateforme de formation hors ligne pour les professionnels de l\u2019assurance qualit\u00e9. Apprenez les m\u00e9thodes de test, les rapports de bogues, les outils CRM, Azure DevOps et la planification de tests gr\u00e2ce \u00e0 des simulations r\u00e9alistes et des exercices guid\u00e9s.',

  // Login page hero section
  'login_hero_tagline':               'Formation QA professionnelle qui fait le pont entre la th\u00e9orie et la pratique.',
  'login_feature_1_title':            'Pertinent pour l\u2019industrie',
  'login_feature_1_desc':             'Sc\u00e9narios de test r\u00e9alistes',
  'login_feature_2_title':            'Laboratoires pratiques',
  'login_feature_2_desc':             'Simulateurs et outils interactifs',
  'login_feature_3_title':            'Certifications',
  'login_feature_3_desc':             'Certificats professionnels',
  'login_feature_4_title':            'Pr\u00eat pour le march\u00e9',
  'login_feature_4_desc':             'Curriculum ax\u00e9 sur l\u2019emploi',
  'login_info_cert':                  'Certificats professionnels',
  'login_privacy':                    'Vos donn\u00e9es de formation sont stock\u00e9es localement sur cet appareil et ne sont transmises nulle part.',

  'login_error_empty':                'Veuillez entrer votre adresse courriel et votre mot de passe.',
  'login_error_email_not_found':      'Adresse courriel introuvable. Veuillez v\u00e9rifier et r\u00e9essayer.',
  'login_error_deactivated':          'Ce compte a \u00e9t\u00e9 d\u00e9sactiv\u00e9. Veuillez contacter votre administrateur.',
  'login_error_wrong_password':       'Mot de passe incorrect. Veuillez r\u00e9essayer.',
  'login_error_db':                   'Impossible de se connecter \u00e0 la base de donn\u00e9es. Veuillez rafra\u00eechir la page.',
  'login_error_generic':              'Une erreur est survenue. Veuillez rafra\u00eechir la page et r\u00e9essayer.',




  // ── PORTAL PAGE (portal.html) ───────────────────────────────────────────────

  'portal_welcome':                   'Bienvenue, {0}!',
  'portal_welcome_sub':               'Continuez l\u00e0 o\u00f9 vous vous \u00eates arr\u00eat\u00e9 ou explorez un nouveau cours.',
  'portal_welcome_sub_first':         'Pr\u00eat \u00e0 commencer votre formation en assurance qualit\u00e9? Parcourez un cours ci-dessous et inscrivez-vous pour commencer.',
  'portal_my_learning':               'Ma formation',
  'portal_my_learning_empty':         'Vous n\u2019\u00eates inscrit \u00e0 aucun cours pour le moment. Parcourez le catalogue ci-dessous et cliquez sur un cours pour commencer!',
  'portal_available_courses':         'Cours disponibles',
  'portal_sign_out':                  'D\u00e9connexion',
  'portal_loading':                   'Chargement de vos cours\u2026',
  'portal_no_courses':                'Aucun cours suppl\u00e9mentaire disponible pour le moment.',
  'portal_error':                     'Une erreur est survenue lors du chargement du portail. Veuillez rafra\u00eechir la page.',
  'portal_admin_dashboard':           'Acc\u00e9der au tableau de bord \u2192',

  'portal_modules':                   '{0} modules',
  'portal_lessons':                   '{0} le\u00e7ons',
  'portal_estimated_min':             '~{0} min',
  'portal_progress':                  'Progression',
  'portal_completed':                 '\u2713 Termin\u00e9',
  'portal_continue_hint':             'Continuer',
  'portal_view_certificate':          'Voir le certificat \u2192',
  'portal_start_course':              'Commencer le cours \u2192',
  'portal_enroll_free':               "S'inscrire \u2014 Gratuit",
  'portal_enrolling':                 'Inscription en cours\u2026',
  'portal_enrolled_success':          'Inscription r\u00e9ussie!',
  'portal_enrolled_fail':             "L'inscription a \u00e9chou\u00e9. Veuillez r\u00e9essayer.",
  'portal_course_not_found':          'Cours introuvable.',

  'portal_category_general':          'G\u00e9n\u00e9ral',

  // Portal sidebar
  'portal_sidebar_quick_links':       'Liens rapides',
  'portal_sidebar_certificates':      'Certificats',
  'portal_sidebar_resources':         'Ressources',
  'portal_stat_enrolled':             'Inscrit',
  'portal_stat_completed':            'Termin\u00e9',
  'portal_btn_download_data':         'T\u00e9l\u00e9charger les donn\u00e9es \u00e9tudiant',
  'portal_footer_quick_start':        'D\u00e9marrage rapide \u00e9tudiant',

   'portal_cat_QA_title':              'Fondamentaux du QA',
   'portal_cat_QA_desc':               'Cours ax\u00e9s sur les comp\u00e9tences et les meilleures pratiques en assurance qualit\u00e9.',
   'portal_cat_Fundamentals_title':    'Fondamentaux',
   'portal_cat_Fundamentals_desc':     'Compétences de base en QA incluant les critères d\'acceptation, CRM et les bases de DevOps.',
    'portal_cat_Tools & Process_title': 'Outils & Processus',
    'portal_cat_Tools & Process_desc':  'Formation sur les outils et processus spécifiques utilisés dans les flux de travail QA.',
   'portal_cat_Development_title':     'D\u00e9veloppement et collaboration',
   'portal_cat_Development_desc':      'Cours couvrant les m\u00e9thodologies de d\u00e9veloppement et les pratiques de collaboration d\u2019\u00e9quipe.',
   'portal_cat_Scenarios_title':       'Scénarios',
   'portal_cat_Scenarios_desc':        'Cours basés sur des scénarios réels pour une expérience pratique en QA.',


  // ── COURSE VIEWER (course-view.html) ────────────────────────────────────────

  'cv_back':                          '\u2190 Retour',
  'cv_percent_done':                  '{0}% termin\u00e9',
  'cv_loading':                       'Chargement\u2026',

  'cv_welcome_title':                 'Choisissez une le\u00e7on pour commencer',
  'cv_welcome_desc':                  'S\u00e9lectionnez un module dans la barre lat\u00e9rale et cliquez sur une le\u00e7on pour d\u00e9marrer l\u02bcapprentissage. Votre progression est sauvegard\u00e9e automatiquement.',

  'cv_module':                        'Module {0}',
  'cv_no_modules':                    'Aucun module trouv\u00e9.',
  'cv_read':                          'Lecture',
  'cv_quiz':                          'Quiz',
  'cv_practice':                      'Exercice',
  'cv_exam':                          'Examen',

  'cv_previous':                      '\u2190 Pr\u00e9c\u00e9dent',
  'cv_mark_complete':                 'Marquer comme termin\u00e9 \u2192',
  'cv_completed':                     '\u2713 Termin\u00e9',
  '__prev__':                         '\u2190 Pr\u00e9c\u00e9dent',
  '__next__':                         'Suivant \u2192',
  'cv_saving':                        'Sauvegarde en cours\u2026',

  'cv_error_not_found':               'Cours introuvable. Il a peut-\u00eatre \u00e9t\u00e9 supprim\u00e9 ou le lien est incorrect.',
  'cv_error_load':                    'Impossible de charger les donn\u00e9es du cours. Veuillez rafra\u00eechir.',
  'cv_error_save':                    'Erreur lors de la sauvegarde de la progression.',
  'cv_error_module_locked':           'Terminez le module pr\u00e9c\u00e9dent d\u02bcabord.',

  'cv_quiz_intro':                    '{0} questions \u2014 vous verrez la bonne r\u00e9ponse apr\u00e8s chaque question.',
  'cv_quiz_question_of':              'Question {0} sur {1}',
  'cv_quiz_correct':                  '\u2705 Correct!',
  'cv_quiz_incorrect':                '\u274C Incorrect.',
  'cv_quiz_correct_answer':           'La bonne r\u00e9ponse est :',
  'cv_quiz_next':                     'Question suivante \u2192',
  'cv_quiz_see_results':              '\U0001F4CA Voir les r\u00e9sultats \u2192',
  'cv_quiz_complete':                 '\U0001F4CA Quiz termin\u00e9!',
  'cv_quiz_score':                    'Vous avez obtenu {0} sur {1} ({2}%)',
  'cv_quiz_reset_confirm':            'R\u00e9initialiser ce quiz? Toutes vos r\u00e9ponses seront effac\u00e9es.',
  'cv_quiz_reset_btn':                '\\U0001F504 R\u00e9initialiser',
  'cv_quiz_retake':                   '\\U0001F504 Reprendre le test',
  'cv_quiz_continue':                 'Continuer \u2192',
  'cv_quiz_not_available':            'Questions de quiz pas encore disponibles',
  'cv_quiz_not_available_desc':       'Les questions pour ce module sont en pr\u00e9paration.',

  'cv_placeholder_title':             'Contenu de la le\u00e7on \u00e0 venir',
  'cv_placeholder_desc':              'Cette le\u00e7on est en pr\u00e9paration. Revenez plus tard pour le contenu complet.',

  'cv_launch_lab':                    'Lancer {0} \u2192',
  'cv_launch_capstone':               'Ouvrir l\u2019\u00e9valuation finale \u2192',
  'cv_lab_complete_hint':             'Une fois le laboratoire termin\u00e9, revenez ici pour passer le quiz du module.',

  'cv_course_complete':               'Cours termin\u00e9! \U0001F389',


  // ── ADMIN DASHBOARD (admin/dashboard.html) ──────────────────────────────────

  'admin_onboarding_students':        '\u00c9tudiants',
  'admin_onboarding_settings':        'Param\u00e8tres',
  'admin_onboarding_assign':          'Attribuer des le\u00e7ons',
  'admin_stat_total_students':        'Total des \u00e9tudiants',
  'admin_topbar_role':                'Administrateur',
  'admin_topbar_sign_out':            'D\u00e9connexion',

  // ── ADMIN ASSIGN (admin/assign.html) ───────────────────────────────────────

  'admin_assign_title':               'Attribuer des modules',
  'admin_assign_save':                "Enregistrer l'attribution",
  'admin_assign_enrollments':         'Inscriptions des \u00e9tudiants',
  'admin_assign_enrolled':            'Inscrit',
  'admin_assign_not_enrolled':        'Non inscrit',
  'admin_assign_reset':               'R\u00e9initialiser tous les modules',
  'admin_assign_action':              'Action',
  'admin_assign_case_id':             'ID de dossier',
  'admin_general_cancel':             'Annuler',


  // ── ADMIN BUG LAB (admin/bugs.html) ────────────────────────────────────────

  'admin_bug_lab':                    'Laboratoire de bogues',
  'admin_save_bug_settings':          'Enregistrer les param\u00e8tres de bogues',
  'admin_bug_config':                 'Configuration des bogues',


  // ── ADMIN CONTENT EDITOR (admin/editor.html) ───────────────────────────────

  'admin_content_editor':             '\u00c9diteur de contenu',
  'admin_certificate_settings':       'Param\u00e8tres du certificat',
  'admin_save_changes':               'Enregistrer les modifications',
  'admin_role_names':                 'Noms des r\u00f4les',
  'admin_junior_role':                'Nom du r\u00f4le junior',
  'admin_senior_role':                'Nom du r\u00f4le senior',
  'admin_reset_defaults':             'R\u00e9initialiser les valeurs par d\u00e9faut',


  // ── ADMIN TRAINER DASHBOARD (admin/simple.html) ────────────────────────────

  'admin_trainer_dashboard':          'Tableau de bord du formateur',
  'admin_full_dashboard':             'Tableau de bord complet',
  'admin_add_students':               'Ajouter des \u00e9tudiants',
  'admin_default_password':           'Mot de passe par d\u00e9faut',
  'admin_protect_download':           'Prot\u00e9ger et t\u00e9l\u00e9charger le fichier de classe',
  'admin_share_team':                 'Partager avec votre \u00e9quipe',
  'admin_download_class_file':        'T\u00e9l\u00e9charger le fichier de classe',
  'admin_email_students':             'Envoyer par courriel aux \u00e9tudiants',

  // ── SIMPLE LOGIN (simple-login.html) ───────────────────────────────────────

  'simple_login_hero_desc':       'Votre plateforme de formation pratique pour les tests logiciels, les rapports de bogues et l\u2019assurance qualit\u00e9.',
  'simple_login_team_login':      'Connexion d\u2019\u00e9quipe',
  'simple_login_subtitle':        'T\u00e9l\u00e9chargez votre fichier de classe et entrez votre nom pour commencer.',
  'simple_login_upload':          'T\u00e9l\u00e9charger le fichier de classe',
  'simple_login_upload_hint':     'Cliquez pour s\u00e9lectionner le fichier .json que votre formateur vous a envoy\u00e9',
  'simple_login_your_name':       'Votre nom',
  'simple_login_name_placeholder':'Tapez votre nom\u2026',
  'simple_login_scenarios':       'Sc\u00e9narios',
  'simple_login_lessons':         'Le\u00e7ons',
  'simple_login_unlock_code':     'Code de d\u00e9verrouillage',
  'simple_login_unlock_placeholder': 'Entrez le code de d\u00e9verrouillage de votre formateur',
  'simple_login_unlock_hint':     'Votre formateur a partag\u00e9 ce code s\u00e9par\u00e9ment (courriel, Teams, etc.)',
  'simple_login_login':           'Connexion',

  // ── QASIMULATOR OS (QASimulator.html / src/os-core.js) ─────────────────────

  'os_app_guide':                 'Guide de l\u2019application',
  'os_settings':                  'Param\u00e8tres',
  'os_help':                      'Aide',
  'os_sign_out':                  'D\u00e9connexion',
  'os_lock':                      'Verrouiller',
  'os_about':                     '\u00c0 propos',
  'os_profile':                   'Profil',
  'os_search':                    'Rechercher',
  'os_apps':                      'Applications',
  'os_desktop':                   'Bureau',
  'os_files':                     'Fichiers',
  'os_clock':                     'Horloge',
  'os_notifications':             'Notifications',
  'os_tasks':                     'T\u00e2ches',
  'os_calendar':                  'Calendrier',
  'os_boot_loading':              'Chargement\u2026',
  'os_boot_initializing':         'Initialisation\u2026',
  'os_lock_hint':                 'Cliquez n\u2019importe o\u00f9 pour d\u00e9verrouiller',
  'os_lock_enter':                'Entrer',
};


// ── FRENCH COURSE CONTENT — QA ONBOARDING ──────────────────────────────────────
// This provides French translations for QA Onboarding lesson content.
// Structure mirrors COURSE_CONTENT["qa-onboarding"] in data/content.js
// Key: subModuleId → HTML string (French)
//
// NOTE: SVG diagrams with embedded English text are kept as-is for now.
// The visual diagrams (bug lifecycle, sprint cycle, test case documents) are
// language-agnostic in their visual structure; only the surrounding text is
// translated.

var LANG_CONTENT_FR = {
  "qa-onboarding": {

    // ── MODULE 1: Testing 101 (Module Test 101) ─────────────────────────────
    "mod-1-1": [
      '<h1>Qu\u2019est-ce que les tests logiciels et pourquoi existent-ils?</h1>',
      '<p class="chapter-intro">Avant de parler de la fa\u00e7on de tester, il est utile de comprendre pourquoi les tests existent.</p>',
      '<p>Imaginez que vous \u00e9crivez une fonctionnalit\u00e9 qui calcule le total d\u2019une facture. Elle fonctionne parfaitement sur votre poste. Vous la d\u00e9ployez. Trois jours plus tard, la facture d\u2019un client s\u2019\u00e9l\u00e8ve \u00e0 0,00 $. Le d\u00e9veloppeur l\u2019a v\u00e9rifi\u00e9e. Le designer l\u2019a r\u00e9vis\u00e9e. Personne ne l\u2019a test\u00e9e dans les conditions sp\u00e9cifiques qui ont r\u00e9v\u00e9l\u00e9 le bogue. C\u2019est \u00e0 cela que servent les testeurs.</p>',
      '<p><strong>Les tests logiciels</strong> sont le processus syst\u00e9matique qui consiste \u00e0 v\u00e9rifier que le logiciel fait ce qu\u2019il est cens\u00e9 faire \u2014 et qu\u2019il ne fait <em>pas</em> ce qu\u2019il n\u2019est pas cens\u00e9 faire. Les deux moiti\u00e9s de cette phrase comptent \u00e9galement.</p>',
      '<h2 style="margin: var(--space-6) 0 var(--space-3);">V\u00e9rification vs. Validation</h2>',
      '<p>Ces deux mots se ressemblent mais signifient des choses diff\u00e9rentes en AQ :</p>',
      '<ul style="padding-left:var(--space-5); color:var(--color-ink-soft); margin-bottom:var(--space-5);">',
      '<li style="margin-bottom:var(--space-3);"><strong>V\u00e9rification</strong> \u2014 Avons-nous bien construit le produit? Le logiciel correspond-il \u00e0 ses sp\u00e9cifications techniques?</li>',
      '<li style="margin-bottom:var(--space-3);"><strong>Validation</strong> \u2014 Avons-nous construit le bon produit? Le logiciel r\u00e9sout-il le vrai probl\u00e8me de l\u2019utilisateur?</li>',
      '</ul>',
      '<p>Une fonctionnalit\u00e9 peut passer la v\u00e9rification et \u00e9chouer la validation. Un bon contr\u00f4le qualit\u00e9 (AQ) attrape les deux.</p>',
      '<h2 style="margin: var(--space-6) 0 var(--space-3);">Pourquoi les d\u00e9veloppeurs ne peuvent-ils pas tester leur propre code?</h2>',
      '<p>Ils le peuvent \u2014 et devraient le faire. Mais les d\u00e9veloppeurs sont de mauvais testeurs de bout en bout pour leur propre travail en raison du <strong>Biais de proximit\u00e9</strong> (tester seulement le chemin pr\u00e9vu) et de la <strong>C\u00e9cit\u00e9 d\u2019hypoth\u00e8se</strong> (utiliser le logiciel \u00ab correctement \u00bb parce qu\u2019ils savent comment il fonctionne).</p>',
      // SVG diagrams kept in English (same as content.js)
      // Key takeaway callout:
      '<div class="callout"><strong>Point cl\u00e9 :</strong> Le travail d\u2019un testeur n\u2019est pas de casser le logiciel. C\u2019est de d\u00e9couvrir ce qu\u2019est la r\u00e9alit\u00e9, et de la comparer honn\u00eatement \u00e0 ce qui a \u00e9t\u00e9 promis.</div>',
    ].join("\n"),

    "mod-1-2": [
      '<h1>Agile et votre r\u00f4le</h1>',
      '<p class="chapter-intro">Comprendre le processus autour de vous fait de vous un meilleur testeur. Voici comment fonctionne Agile et o\u00f9 se situe votre r\u00f4le.</p>',
      '<div class="callout" style="margin-bottom:var(--space-5);"><strong>Votre r\u00f4le : Testeur syst\u00e8me.</strong> Vous v\u00e9rifiez que l\u2019application enti\u00e8re fonctionne de bout en bout \u2014 que chaque fonctionnalit\u00e9 se comporte exactement selon les crit\u00e8res d\u2019acceptation. C\u2019est ce qu\u2019on appelle le <em>Test Syst\u00e8me</em>. Les TAU (Tests d\u2019Acceptation Utilisateur) viennent apr\u00e8s vous et sont effectu\u00e9s par le client ou les propri\u00e9taires d\u2019affaires. Votre travail consiste \u00e0 attraper les probl\u00e8mes <em>avant</em> qu\u2019ils n\u2019atteignent les TAU.</div>',
      '<h2 style="margin: var(--space-6) 0 var(--space-3);">Qu\u2019est-ce que Agile?</h2>',
      '<p>Agile est une fa\u00e7on de construire des logiciels en cycles courts et cibl\u00e9s appel\u00e9s <strong>sprints</strong> \u2014 g\u00e9n\u00e9ralement d\u2019une \u00e0 deux semaines.</p>',
      // SVG diagram kept in English (same SVG from content.js)
      '<h2 style="margin: var(--space-6) 0 var(--space-3);">Tests Agile vs. Cascade</h2>',
      '<div class="comparison-grid">',
      '<div class="comparison-card bad"><div class="comparison-label">Cascade (Waterfall)</div>Le d\u00e9veloppement se termine d\u2019abord. Puis les tests commencent. L\u2019\u00e9cart est long. Les bogues trouv\u00e9s tard sont co\u00fbteux \u00e0 corriger.</div>',
      '<div class="comparison-card good"><div class="comparison-label">Agile</div>Les tests se d\u00e9roulent parall\u00e8lement au d\u00e9veloppement \u00e0 chaque sprint. Les probl\u00e8mes sont d\u00e9tect\u00e9s t\u00f4t, quand ils sont peu co\u00fbteux \u00e0 corriger.</div>',
      '</div>',
      '<h2 style="margin: var(--space-6) 0 var(--space-3);">Qu\u2019est-ce que le TAU?</h2>',
      '<p><strong>Le Test d\u2019Acceptation Utilisateur (TAU)</strong> est la v\u00e9rification finale avant qu\u2019une fonctionnalit\u00e9 ne soit livr\u00e9e. Il r\u00e9pond \u00e0 la question : cela fait-il ce que l\u2019entreprise a convenu qu\u2019il ferait?</p>',
      '<div class="callout"><strong>Point cl\u00e9 :</strong> En Agile, vous n\u2019\u00eates pas un gardien \u00e0 la fin de la cha\u00eene. Vous \u00eates un signal de qualit\u00e9 tout au long du processus.</div>',
    ].join("\n"),

    "mod-1-3": [
      '<h1>Types de tests</h1>',
      '<p class="chapter-intro">Il existe de nombreux types de tests. Savoir quel type fait quoi vous aide \u00e0 comprendre o\u00f9 votre travail s\u2019inscrit dans l\u2019ensemble.</p>',
      '<table style="width:100%; border-collapse:collapse; margin:var(--space-6) 0; font-size:var(--text-sm);">',
      '<thead style="background:var(--color-bg); border-bottom:2px solid var(--color-border);">',
      '<tr><th style="text-align:left; padding:var(--space-3) var(--space-4); color:var(--color-ink-muted); font-size:var(--text-xs); text-transform:uppercase;">Type</th><th style="text-align:left; padding:var(--space-3) var(--space-4); color:var(--color-ink-muted); font-size:var(--text-xs); text-transform:uppercase;">Ce qu\u2019il teste</th><th style="text-align:left; padding:var(--space-3) var(--space-4); color:var(--color-ink-muted); font-size:var(--text-xs); text-transform:uppercase;">Analogie</th></tr>',
      '</thead>',
      '<tbody>',
      '<tr style="border-bottom:1px solid var(--color-border);"><td style="padding:var(--space-3) var(--space-4);"><strong>Unitaire</strong></td><td style="padding:var(--space-3) var(--space-4); color:var(--color-ink-soft);">Une seule fonction isol\u00e9e</td><td style="padding:var(--space-3) var(--space-4); color:var(--color-ink-soft);">Tester un interrupteur</td></tr>',
      '<tr style="border-bottom:1px solid var(--color-border);"><td style="padding:var(--space-3) var(--space-4);"><strong>Int\u00e9gration</strong></td><td style="padding:var(--space-3) var(--space-4); color:var(--color-ink-soft);">Comment les composants interagissent</td><td style="padding:var(--space-3) var(--space-4); color:var(--color-ink-soft);">Tester que l\u2019interrupteur allume la lumi\u00e8re</td></tr>',
      '<tr style="border-bottom:1px solid var(--color-border); background:var(--color-primary-light);"><td style="padding:var(--space-3) var(--space-4);"><strong>Syst\u00e8me \u2190 Vous \u00eates ici</strong></td><td style="padding:var(--space-3) var(--space-4); color:var(--color-ink-soft);">L\u2019application enti\u00e8re de bout en bout</td><td style="padding:var(--space-3) var(--space-4); color:var(--color-ink-soft);">Visiter chaque pi\u00e8ce, v\u00e9rifier chaque interrupteur</td></tr>',
      '<tr style="border-bottom:1px solid var(--color-border);"><td style="padding:var(--space-3) var(--space-4);"><strong>TAU</strong></td><td style="padding:var(--space-3) var(--space-4); color:var(--color-ink-soft);">Si le logiciel r\u00e9pond aux vrais besoins</td><td style="padding:var(--space-3) var(--space-4); color:var(--color-ink-soft);">Demander si c\u2019est la maison qu\u2019ils voulaient</td></tr>',
      '<tr><td style="padding:var(--space-3) var(--space-4);"><strong>R\u00e9gression</strong></td><td style="padding:var(--space-3) var(--space-4); color:var(--color-ink-soft);">Que les changements n\u2019ont pas cass\u00e9 l\u2019existant</td><td style="padding:var(--space-3) var(--space-4); color:var(--color-ink-soft);">V\u00e9rifier qu\u2019aucun autre interrupteur n\u2019est cass\u00e9</td></tr>',
      '</tbody>',
      '</table>',
      // SVG test case document kept as-is (English visual)
    ].join("\n"),

    "mod-1-4": [
      '<h1>Le cycle de vie d\u2019un bogue</h1>',
      '<p class="chapter-intro">Un bogue n\u2019est pas simplement signal\u00e9 et oubli\u00e9. Il traverse un ensemble d\u00e9fini d\u2019\u00e9tats.</p>',
      // SVG bug lifecycle diagram kept as-is
      '<div class="callout"><strong>Distinction cruciale :</strong> \u00ab R\u00e9solu \u00bb signifie que le d\u00e9veloppeur pense que c\u2019est termin\u00e9. \u00ab Ferm\u00e9 \u00bb signifie que <em>vous</em> avez confirm\u00e9 que c\u2019est termin\u00e9.</div>',
    ].join("\n"),

    "mod-1-5": [
      '<h1>Qu\u2019est-ce qui fait un bon cas de test?</h1>',
      '<p class="chapter-intro">Un cas de test est un ensemble document\u00e9 de conditions utilis\u00e9es pour v\u00e9rifier un comportement sp\u00e9cifique.</p>',
      '<h2 style="margin: var(--space-6) 0 var(--space-3);">Les trois parties requises</h2>',
      '<ul style="padding-left:var(--space-5); color:var(--color-ink-soft); margin-bottom:var(--space-6);">',
      '<li style="margin-bottom:var(--space-4);"><strong>Pr\u00e9conditions</strong> \u2014 Dans quel \u00e9tat le syst\u00e8me doit-il \u00eatre? Qui est connect\u00e9?</li>',
      '<li style="margin-bottom:var(--space-4);"><strong>\u00c9tapes</strong> \u2014 Quelles actions exactes effectuez-vous? Num\u00e9rot\u00e9es et pr\u00e9cises.</li>',
      '<li style="margin-bottom:var(--space-4);"><strong>R\u00e9sultat attendu</strong> \u2014 Que devrait-il se passer? R\u00e9f\u00e9rencez le crit\u00e8re d\u2019acceptation.</li>',
      '</ul>',
      '<div class="comparison-grid">',
      '<div class="comparison-card bad"><div class="comparison-label">Mauvais cas de test</div><p style="margin:0; font-size:var(--text-sm); color:var(--color-ink-soft);">\u00ab V\u00e9rifiez que le champ Statut fonctionne. \u00bb</p></div>',
      '<div class="comparison-card good"><div class="comparison-label">Bon cas de test</div><p style="margin:0 0 var(--space-2); font-size:var(--text-sm); color:var(--color-ink-soft);"><strong>Pr\u00e9condition :</strong> Connect\u00e9 en tant qu\u2019enqu\u00eateur junior.<br><strong>\u00c9tapes :</strong> 1. Mettre le statut \u00e0 \u00ab Ferm\u00e9 \u00bb, 2. Cliquer sur Enregistrer.<br><strong>R\u00e9sultat attendu :</strong> Enregistrement bloqu\u00e9. Message : \u00ab Vous n\u2019avez pas la permission\u2026 \u00bb</p></div>',
      '</div>',
      '<div class="callout"><strong>Point cl\u00e9 :</strong> R\u00e9digez les r\u00e9sultats attendus avec une telle pr\u00e9cision qu\u2019il n\u2019y a qu\u2019une seule lecture possible.</div>',
      '<p style="margin-top:var(--space-6);">Vous avez maintenant couvert les bases. Passez au quiz pour tester votre compr\u00e9hension.</p>',
    ].join("\n"),

    // ── MODULE 2: Acceptance Criteria (Crit\u00e8res d\u2019acceptation) ──────────────
    "mod-2-1": [
      '<h1>Que sont les crit\u00e8res d\u2019acceptation?</h1>',
      '<p class="chapter-intro">C\u2019est le concept le plus important de tout ce cours. Tout le reste repose l\u00e0-dessus.</p>',
      '<p>Imaginez que vous construisez une cl\u00f4ture pour un client. Ils ont dit : \u00ab Je veux une cl\u00f4ture autour de la cour. \u00bb Vous la construisez. Ils sont m\u00e9contents \u2014 ils voulaient une porte c\u00f4t\u00e9 sud, peinte en blanc, d\u2019exactement 1,2 m\u00e8tre de haut. Rien de tout cela n\u2019avait \u00e9t\u00e9 \u00e9crit. \u00c0 qui la faute?</p>',
      '<p><strong>Les crit\u00e8res d\u2019acceptation (CA)</strong> existent pour que tout le monde s\u2019entende sur ce \u00e0 quoi ressemble \u00ab termin\u00e9 \u00bb avant que quelqu\u2019un ne prenne un marteau \u2014 ou n\u2019\u00e9crive une ligne de code.</p>',
      '<h2 style="margin: var(--space-6) 0 var(--space-3);">Une d\u00e9finition pr\u00e9cise</h2>',
      '<p>Les crit\u00e8res d\u2019acceptation sont les conditions convenues qu\u2019une fonctionnalit\u00e9 doit remplir pour \u00eatre consid\u00e9r\u00e9e comme compl\u00e8te. Ils sont r\u00e9dig\u00e9s avant le d\u00e9but du d\u00e9veloppement. Ils d\u00e9finissent le contrat entre le propri\u00e9taire du produit et l\u2019\u00e9quipe.</p>',
      '<p>En tant que testeur, les CA sont votre source de v\u00e9rit\u00e9 principale :</p>',
      '<ul style="padding-left:var(--space-5); color:var(--color-ink-soft); margin-bottom:var(--space-5);">',
      '<li style="margin-bottom:var(--space-3);">Si c\u2019est dans le CA \u2192 testez-le</li>',
      '<li style="margin-bottom:var(--space-3);">Si le comportement n\u2019est pas dans le CA \u2192 signalez l\u2019\u00e9cart, ne devinez pas</li>',
      '<li style="margin-bottom:var(--space-3);">Si le logiciel s\u2019\u00e9carte du CA \u2192 c\u2019est un bogue</li>',
      '</ul>',
      '<h2 style="margin: var(--space-6) 0 var(--space-3);">CA vs. Exigences</h2>',
      '<div class="comparison-grid">',
      '<div class="comparison-card bad"><div class="comparison-label">Exigences \u2014 quoi construire</div>\u00ab Le syst\u00e8me doit permettre aux utilisateurs de cr\u00e9er des dossiers de cas. \u00bb</div>',
      '<div class="comparison-card good"><div class="comparison-label">CA \u2014 comment v\u00e9rifier que c\u2019est bien construit</div>\u00ab \u00c9tant donn\u00e9 un enqu\u00eateur principal connect\u00e9, quand il remplit tous les champs obligatoires et clique sur Enregistrer, alors un nouveau dossier est cr\u00e9\u00e9 avec un ID unique au format CAS-XXXXX. \u00bb</div>',
      '</div>',
      '<div class="callout"><strong>Rappelez-vous :</strong> Les exigences disent <em>quoi</em> construire. Les crit\u00e8res d\u2019acceptation disent <em>comment vous saurez</em> que c\u2019est bien construit.</div>',
    ].join("\n"),

    "mod-2-2": [
      '<h1>Le format Given / When / Then</h1>',
      '<p class="chapter-intro">La plupart des crit\u00e8res d\u2019acceptation dans les \u00e9quipes Agile sont r\u00e9dig\u00e9s dans un format structur\u00e9 qui les rend directement testables. Voici comment les lire.</p>',
      '<pre style="background:var(--color-bg); border:1px solid var(--color-border); border-radius:var(--radius-md); padding:var(--space-5); font-family:var(--font-mono); font-size:var(--text-sm); color:var(--color-ink); overflow-x:auto; margin:var(--space-5) 0;">\u00c9tant donn\u00e9  [une pr\u00e9condition ou un \u00e9tat sp\u00e9cifique]\nQuand        [une action est effectu\u00e9e]\nAlors        [le r\u00e9sultat attendu]</pre>',
      '<h2 style="margin: var(--space-6) 0 var(--space-3);">Un exemple concret</h2>',
      '<p>Voici un CA de l\u2019\u00e9cran de gestion des cas que vous utiliserez dans la Le\u00e7on 3 :</p>',
      '<pre style="background:var(--color-bg); border:1px solid var(--color-border); border-radius:var(--radius-md); padding:var(--space-5); font-family:var(--font-mono); font-size:var(--text-sm); color:var(--color-ink); overflow-x:auto; margin:var(--space-5) 0;">\u00c9tant donn\u00e9 que l\u2019utilisateur est connect\u00e9 en tant qu\u2019enqu\u00eateur junior\n  Et que   un dossier de cas est ouvert en mode \u00e9dition\nQuand        l\u2019utilisateur met le menu d\u00e9roulant Statut \u00e0 \u00ab Ferm\u00e9 \u00bb\n  Et que    clique sur Enregistrer\nAlors        l\u2019enregistrement est bloqu\u00e9\n  Et qu\u2019un  message de validation appara\u00eet sous le champ Statut\n  Et que    le message dit exactement :\n            \u00ab Vous n\u2019avez pas la permission de r\u00e9soudre ou fermer des cas. \u00bb</pre>',
      '<h2 style="margin: var(--space-6) 0 var(--space-3);">Pourquoi chaque partie est importante</h2>',
      '<ul style="padding-left:var(--space-5); color:var(--color-ink-soft); margin-bottom:var(--space-5);">',
      '<li style="margin-bottom:var(--space-4);"><strong>\u00c9tant donn\u00e9</strong> \u2014 d\u00e9finit vos conditions de d\u00e9part exactes. Sans cela, deux testeurs ex\u00e9cutant le \u00ab m\u00eame \u00bb test pourraient obtenir des r\u00e9sultats diff\u00e9rents.</li>',
      '<li style="margin-bottom:var(--space-4);"><strong>Quand</strong> \u2014 une action unique, pr\u00e9cise. Pas \u00ab cliquer un peu partout \u00bb \u2014 une chose, faite une fois.</li>',
      '<li style="margin-bottom:var(--space-4);"><strong>Alors</strong> \u2014 le r\u00e9sultat exact, sans interpr\u00e9tation n\u00e9cessaire. Notez comment l\u2019exemple sp\u00e9cifie le texte exact du message d\u2019erreur.</li>',
      '</ul>',
      '<div class="callout"><strong>Attention :</strong> Plusieurs clauses \u00ab Alors \u00bb non li\u00e9es dans un m\u00eame CA. Si vous avez cinq clauses \u00ab Et \u00bb sous Alors qui testent des choses diff\u00e9rentes, le CA devrait \u00eatre divis\u00e9.</div>',
    ].join("\n"),

    "mod-2-3": [
      '<h1>Lire les CA en tant que testeur</h1>',
      '<p class="chapter-intro">Votre travail en lisant les CA est de transformer chaque \u00e9nonc\u00e9 en cas de test. C\u2019est un processus m\u00e9canique qui s\u2019apprend.</p>',
      '<h2 style="margin: var(--space-6) 0 var(--space-3);">Trois questions pour chaque CA</h2>',
      '<ul style="padding-left:var(--space-5); color:var(--color-ink-soft); margin-bottom:var(--space-6);">',
      '<li style="margin-bottom:var(--space-4);"><strong>Quel est le chemin heureux?</strong> L\u2019action qui devrait r\u00e9ussir.</li>',
      '<li style="margin-bottom:var(--space-4);"><strong>Quel est le chemin malheureux?</strong> L\u2019action qui devrait \u00eatre rejet\u00e9e.</li>',
      '<li style="margin-bottom:var(--space-4);"><strong>Quels sont les cas limites?</strong> Valeurs limites, entr\u00e9es vides, changements de r\u00f4le.</li>',
      '</ul>',
      '<h2 style="margin: var(--space-6) 0 var(--space-3);">Exemple pratique \u2014 Un CA, quatre cas de test</h2>',
      '<p>Le CA dit : <em>\u00ab Le titre du cas est obligatoire. Maximum 120 caract\u00e8res. Ne peut pas \u00eatre vide \u00e0 l\u2019enregistrement. \u00bb</em></p>',
      // Table structure kept; English column headers are short and technical
      '<table style="width:100%; border-collapse:collapse; margin:var(--space-5) 0; font-size:var(--text-sm);">',
      '<thead style="background:var(--color-bg); border-bottom:2px solid var(--color-border);"><tr><th style="text-align:left; padding:var(--space-3) var(--space-4); color:var(--color-ink-muted); font-size:var(--text-xs); text-transform:uppercase;">#</th><th style="text-align:left; padding:var(--space-3) var(--space-4); color:var(--color-ink-muted); font-size:var(--text-xs); text-transform:uppercase;">Test</th><th style="text-align:left; padding:var(--space-3) var(--space-4); color:var(--color-ink-muted); font-size:var(--text-xs); text-transform:uppercase;">Entr\u00e9e</th><th style="text-align:left; padding:var(--space-3) var(--space-4); color:var(--color-ink-muted); font-size:var(--text-xs); text-transform:uppercase;">R\u00e9sultat attendu</th></tr></thead>',
      '<tbody>',
      '<tr style="border-bottom:1px solid var(--color-border); background:var(--color-success-light);"><td style="padding:var(--space-3) var(--space-4);">1</td><td style="padding:var(--space-3) var(--space-4);">Chemin heureux</td><td style="padding:var(--space-3) var(--space-4);">Titre valide, 50 car.</td><td style="padding:var(--space-3) var(--space-4);">Enregistr\u00e9 avec succ\u00e8s</td></tr>',
      '<tr style="border-bottom:1px solid var(--color-border); background:var(--color-error-light);"><td style="padding:var(--space-3) var(--space-4);">2</td><td style="padding:var(--space-3) var(--space-4);">Chemin malheureux</td><td style="padding:var(--space-3) var(--space-4);">Vide</td><td style="padding:var(--space-3) var(--space-4);">Enregistrement bloqu\u00e9, erreur affich\u00e9e</td></tr>',
      '<tr style="border-bottom:1px solid var(--color-border);"><td style="padding:var(--space-3) var(--space-4);">3</td><td style="padding:var(--space-3) var(--space-4);">Limite \u2014 max</td><td style="padding:var(--space-3) var(--space-4);">Exactement 120 car.</td><td style="padding:var(--space-3) var(--space-4);">Enregistr\u00e9 avec succ\u00e8s</td></tr>',
      '<tr><td style="padding:var(--space-3) var(--space-4);">4</td><td style="padding:var(--space-3) var(--space-4);">Limite \u2014 d\u00e9pass\u00e9</td><td style="padding:var(--space-3) var(--space-4);">121e caract\u00e8re tap\u00e9</td><td style="padding:var(--space-3) var(--space-4);">Caract\u00e8re non accept\u00e9</td></tr>',
      '</tbody>',
      '</table>',
      '<div class="callout"><strong>Id\u00e9e cl\u00e9 :</strong> Une ligne de CA g\u00e9n\u00e8re plusieurs cas de test. Un bon testeur cherche tout ce qui pourrait mal tourner, pas seulement ce qui devrait bien fonctionner.</div>',
    ].join("\n"),

    "mod-2-4": [
      '<h1>Quand les CA sont manquants ou ambigus</h1>',
      '<p class="chapter-intro">Les CA ne couvriront pas toujours tous les sc\u00e9narios que vous rencontrez. Voici quoi faire quand cela arrive.</p>',
      '<h2 style="margin: var(--space-6) 0 var(--space-3);">Les quatre \u00e9tapes</h2>',
      '<ul style="padding-left:var(--space-5); color:var(--color-ink-soft); margin-bottom:var(--space-5);">',
      '<li style="margin-bottom:var(--space-5);"><strong>1. Signalez-le imm\u00e9diatement.</strong> Ne devinez pas quel est le comportement pr\u00e9vu. Ne pr\u00e9sumez pas.</li>',
      '<li style="margin-bottom:var(--space-5);"><strong>2. Posez une question pr\u00e9cise.</strong> Pas \u00ab cela semble faux \u00bb \u2014 mais une question pr\u00e9cise \u00e0 laquelle on peut r\u00e9pondre.</li>',
      '<li style="margin-bottom:var(--space-5);"><strong>3. Ne signalez pas un bogue sans r\u00e9f\u00e9rence CA.</strong> Vous ne pouvez pas qualifier quelque chose de bogue s\u2019il n\u2019y a pas d\u2019attente d\u00e9finie dont il s\u2019\u00e9carte.</li>',
      '<li style="margin-bottom:var(--space-5);"><strong>4. Documentez votre hypoth\u00e8se si vous devez continuer.</strong> Notez-la clairement : <em>\u00ab Hypoth\u00e8se : Priorit\u00e9 vide par d\u00e9faut \u00e0 Moyenne \u2014 pas dans le CA. \u00bb</em></li>',
      '</ul>',
      '<div class="callout"><strong>Ceci vous prot\u00e8ge :</strong> Un testeur qui signale des bogues bas\u00e9s sur des pr\u00e9f\u00e9rences personnelles plut\u00f4t que sur les CA perdra rapidement sa cr\u00e9dibilit\u00e9. Ancrez toujours votre rapport \u00e0 une r\u00e9f\u00e9rence CA sp\u00e9cifique.</div>',
      // SVG documents kept in English
    ].join("\n"),

    "mod-2-5": [
      '<h1>Les CA pour ce cours</h1>',
      '<p class="chapter-intro">Dans le laboratoire CRM, vous interagirez avec une simulation d\u2019\u00e9cran CRM. Voici les crit\u00e8res d\u2019acceptation pour cet \u00e9cran \u2014 lisez-les maintenant pour arriver pr\u00eat.</p>',
      '<div style="background:var(--color-bg); border:1px solid var(--color-border); border-radius:var(--radius-md); padding:var(--space-6); margin:var(--space-6) 0;">',
      '<h2 style="font-size:var(--text-md); color:var(--color-primary); margin-bottom:var(--space-4);">\u00c9cran d\u2019enqu\u00eate de cas \u2014 CA</h2>',
      '<h3 style="font-size:var(--text-sm); text-transform:uppercase; letter-spacing:0.08em; color:var(--color-ink-muted); margin:var(--space-5) 0 var(--space-3);">CA-1 : Visibilit\u00e9</h3>',
      '<ul style="padding-left:var(--space-5); color:var(--color-ink-soft); font-size:var(--text-sm);"><li style="margin-bottom:var(--space-2);">CA-1.1 : Tous les champs standards sont visibles pour les deux r\u00f4les.</li><li style="margin-bottom:var(--space-2);">CA-1.2 : Le champ R\u00e9sultat/Conclusion est visible UNIQUEMENT pour les enqu\u00eateurs principaux. Doit \u00eatre absent du DOM pour les juniors.</li><li style="margin-bottom:var(--space-2);">CA-1.3 : Le champ Assign\u00e9 \u00e0 est visible UNIQUEMENT pour les enqu\u00eateurs principaux.</li></ul>',
      '<h3 style="font-size:var(--text-sm); text-transform:uppercase; letter-spacing:0.08em; color:var(--color-ink-muted); margin:var(--space-5) 0 var(--space-3);">CA-2 : Validation</h3>',
      '<ul style="padding-left:var(--space-5); color:var(--color-ink-soft); font-size:var(--text-sm);"><li style="margin-bottom:var(--space-2);">CA-2.1 : Le titre du cas est obligatoire. L\u2019enregistrement est bloqu\u00e9 s\u2019il est vide.</li><li style="margin-bottom:var(--space-2);">CA-2.2 : Le titre du cas max. 120 car. Le 121e caract\u00e8re n\u2019est pas accept\u00e9.</li><li style="margin-bottom:var(--space-2);">CA-2.3 : La date d\u2019ouverture est obligatoire. Les dates futures sont rejet\u00e9es.</li></ul>',
      '<h3 style="font-size:var(--text-sm); text-transform:uppercase; letter-spacing:0.08em; color:var(--color-ink-muted); margin:var(--space-5) 0 var(--space-3);">CA-3 : Comportement conditionnel</h3>',
      '<ul style="padding-left:var(--space-5); color:var(--color-ink-soft); font-size:var(--text-sm);"><li style="margin-bottom:var(--space-2);">CA-3.1 : Le motif de signalement appara\u00eet UNIQUEMENT lorsque Signalement est coch\u00e9.</li><li style="margin-bottom:var(--space-2);">CA-3.2 : Le motif de signalement est obligatoire lorsque Signalement est cochant.</li></ul>',
      '<h3 style="font-size:var(--text-sm); text-transform:uppercase; letter-spacing:0.08em; color:var(--color-ink-muted); margin:var(--space-5) 0 var(--space-3);">CA-4 : R\u00f4les</h3>',
      '<ul style="padding-left:var(--space-5); color:var(--color-ink-soft); font-size:var(--text-sm);"><li style="margin-bottom:var(--space-2);">CA-4.2 : Le junior ne peut pas mettre le statut \u00e0 R\u00e9solu/Ferm\u00e9. Enregistrement bloqu\u00e9 : \u00ab Vous n\u2019avez pas la permission\u2026 \u00bb</li></ul>',
      '</div>',
      '<div class="callout"><strong>Avant de continuer :</strong> Choisissez un CA ci-dessus et \u00e9crivez les cas de test qu\u2019il g\u00e9n\u00e8re \u2014 chemin heureux, chemin malheureux, cas limites.</div>',
    ].join("\n"),

    // ── MODULE 3: CRM Interactive Lab (standalone) ──────────────────────────
    "mod-3-1": [
      '<div class="cv-placeholder">',
      '<div class="cv-placeholder-icon">\U0001F5A5\uFE0F</div>',
      '<h3>Laboratoire CRM interactif</h3>',
      '<p>Ce module contient une simulation interactive de Dynamics 365 CRM. Lancez-la dans une fen\u00eatre s\u00e9par\u00e9e ci-dessous.</p>',
      '<p style="font-size:var(--text-sm); color:var(--color-ink-muted);">Une fois le laboratoire termin\u00e9, revenez ici pour passer au quiz du module.</p>',
      '<p style="margin-top:var(--space-5);"><a href="crm-lab.html" target="_blank" class="btn btn-primary" style="text-decoration:none;">Lancer le laboratoire CRM \u2192</a></p>',
      '</div>',
    ].join("\n"),

    // ── MODULE 4: Azure DevOps Interactive Lab (standalone) ─────────────────
    "mod-4-1": [
      '<div class="cv-placeholder">',
      '<div class="cv-placeholder-icon">\U0001F6E0\uFE0F</div>',
      '<h3>Laboratoire Azure DevOps interactif</h3>',
      '<p>Ce module contient une simulation interactive d\u2019Azure DevOps. Lancez-la dans une fen\u00eatre s\u00e9par\u00e9e ci-dessous.</p>',
      '<p style="font-size:var(--text-sm); color:var(--color-ink-muted);">Une fois le laboratoire termin\u00e9, revenez ici pour passer au quiz du module.</p>',
      '<p style="margin-top:var(--space-5);"><a href="ado-lab.html" target="_blank" class="btn btn-primary" style="text-decoration:none;">Lancer le laboratoire Azure DevOps \u2192</a></p>',
      '</div>',
    ].join("\n"),

    // ── MODULE 5: Test Planning & Bug Triage (Planification et triage) ─────
    "mod-5-1": [
      '<h1>Tests exploratoires vs. Tests planifi\u00e9s</h1>',
      '<p class="chapter-intro">Selon l\u2019objectif, vous aborderez une fonctionnalit\u00e9 de l\u2019une ou l\u2019autre fa\u00e7on. Aucune n\u2019est \u00ab meilleure \u00bb \u2014 elles r\u00e9solvent simplement des probl\u00e8mes diff\u00e9rents.</p>',
      '<p><strong>Les tests exploratoires</strong> consistent \u00e0 ouvrir l\u2019application, explorer et chercher ce qui semble anormal. Il n\u2019y a ni script, ni liste de v\u00e9rification. Vous utilisez votre instinct et votre connaissance du domaine. C\u2019est id\u00e9al pour les premi\u00e8res \u00e9tapes, les nouvelles fonctionnalit\u00e9s ou les v\u00e9rifications rapides.</p>',
      '<p><strong>Les tests planifi\u00e9s (cas de test)</strong> sont formels. Vous avez une liste d\u2019\u00e9tapes pr\u00e9cises et de r\u00e9sultats attendus. Vous les suivez dans l\u2019ordre et enregistrez un r\u00e9sultat r\u00e9ussite/\u00e9chec pour chacun. C\u2019est essentiel pour les tests de r\u00e9gression et pour prouver que les crit\u00e8res d\u2019acceptation sont respect\u00e9s.</p>',
      '<div class="callout tip"><strong>Conseil :</strong> En pratique, les bons analystes AQ font les deux. Vous explorez d\u2019abord pour comprendre le syst\u00e8me, puis vous \u00e9crivez des cas de test pour prouver qu\u2019il fonctionne pour tous les sc\u00e9narios importants.</div>',
    ].join("\n"),

    "mod-5-2": [
      '<h1>Que contient un cas de test?</h1>',
      '<p class="chapter-intro">Un cas de test professionnel \u00e9limine les conjectures. Si un d\u00e9veloppeur lit votre cas de test, il devrait pouvoir reproduire le r\u00e9sultat exact sans vous demander des clarifications.</p>',
      '<p>Chaque cas de test n\u00e9cessite trois composants essentiels : <strong>Pr\u00e9conditions</strong> (l\u2019\u00e9tat de l\u2019application), <strong>\u00c9tapes</strong> (les actions) et le <strong>R\u00e9sultat attendu</strong> (l\u2019objectif).</p>',
      '<div class="callout">Remarquez que le \u00ab R\u00e9sultat obtenu \u00bb est vide quand vous \u00e9crivez le cas de test. Vous le remplissez pendant le test. Si le r\u00e9sultat obtenu \u2260 r\u00e9sultat attendu, vous avez trouv\u00e9 un bogue.</div>',
    ].join("\n"),

    "mod-5-3": [
      '<h1>Les bogues ne sont pas tous \u00e9gaux</h1>',
      '<p class="chapter-intro">Le triage des bogues est le processus qui d\u00e9cide de l\u2019urgence d\u2019une correction. La gravit\u00e9 est bas\u00e9e sur l\u2019impact fonctionnel, pas sur le degr\u00e9 de \u00ab d\u00e9rangeance \u00bb du bogue.</p>',
      '<p><strong>Exercice de triage :</strong> Attribuez mentalement une gravit\u00e9 \u00e0 ces bogues avant de r\u00e9v\u00e9ler la r\u00e9ponse.</p>',
      '<details class="triage-exercise"><summary>Bogue A : \u00ab Le champ Date d\u2019ouverture accepte les dates futures \u2014 un cas peut \u00eatre \u00ab ouvert \u00bb le 1er janvier 2099. \u00bb</summary><p><strong>R\u00e9ponse : Gravite 3 \u2014 Moyenne.</strong> Probl\u00e8me d\u2019int\u00e9grit\u00e9 des donn\u00e9es, solution de contournement par saisie manuelle attentive.</p></details>',
      '<details class="triage-exercise"><summary>Bogue B : \u00ab Les notes de cas sont supprim\u00e9es lors du rafra\u00eechissement de la page \u2014 tout le texte saisi est perdu. \u00bb</summary><p><strong>R\u00e9ponse : Gravite 2 \u2014 \u00c9lev\u00e9e.</strong> Perte de donn\u00e9es majeure, aucune solution de contournement, affecte tous les utilisateurs.</p></details>',
      '<details class="triage-exercise"><summary>Bogue C : \u00ab Le logo Dynamics CRM appara\u00eet l\u00e9g\u00e8rement flou sur les \u00e9crans haute d\u00e9finition. \u00bb</summary><p><strong>R\u00e9ponse : Gravite 4 \u2014 Faible.</strong> Probl\u00e8me esth\u00e9tique, aucun impact fonctionnel.</p></details>',
    ].join("\n"),

    "mod-5-4": [
      '<h1>Pourquoi chaque bogue a besoin d\u2019une r\u00e9f\u00e9rence CA</h1>',
      '<p class="chapter-intro">La tra\u00e7abilit\u00e9 est ce qui distingue une opinion d\u2019un d\u00e9faut. Dans un environnement professionnel, nous ne signalons pas des bogues parce que nous \u00ab n\u2019aimons pas \u00bb quelque chose; nous les signalons parce qu\u2019ils violent une exigence.</p>',
      '<p>Un <strong>Crit\u00e8re d\u2019acceptation (CA)</strong> d\u00e9finit ce \u00e0 quoi ressemble \u00ab correct \u00bb. Sans r\u00e9f\u00e9rence CA, un rapport de bogue n\u2019est qu\u2019une opinion. Avec une r\u00e9f\u00e9rence, c\u2019est une preuve.</p>',
      '<p>Les d\u00e9veloppeurs priorisent les bogues avec des r\u00e9f\u00e9rences CA claires parce qu\u2019ils savent exactement \u00e0 quoi ressemble \u00ab corrig\u00e9 \u00bb, et les responsables AQ les acceptent parce qu\u2019ils sont tra\u00e7ables.</p>',
      '<div class="comparison-grid">',
      '<div class="comparison-card bad"><div class="comparison-label">Mauvais</div><p style="margin:0; font-size:var(--text-sm);">\u00ab Le statut ne fonctionne pas \u00bb</p></div>',
      '<div class="comparison-card good"><div class="comparison-label">Bon</div><p style="margin:0; font-size:var(--text-sm);">\u00ab Un enqu\u00eateur junior peut mettre le statut du cas \u00e0 Signal\u00e9 \u2014 violation CA-2.1 \u00bb</p></div>',
      '</div>',
      '<div class="callout tip"><strong>En cas de doute :</strong> [ce qui s\u2019est pass\u00e9] + [ce qui aurait d\u00fb se passer] + [quel CA est viol\u00e9]. C\u2019est un titre de bogue complet.</div>',
    ].join("\n"),

    "mod-5-5": [
      '<h1>Liste de v\u00e9rification \u2014 avant de signaler un bogue</h1>',
      '<p class="chapter-intro">Avant d\u2019appuyer sur \u00ab Enregistrer \u00bb dans Azure DevOps, parcourez ce mod\u00e8le mental pour vous assurer que votre rapport est une correction \u00ab \u00e0 un clic \u00bb pour le d\u00e9veloppeur.</p>',
      '<div class="checklist-box">',
      '<ul>',
      '<li>Le titre d\u00e9crit-il le d\u00e9faut sp\u00e9cifique (pas seulement la zone)?</li>',
      '<li>Ai-je attribu\u00e9 un niveau de gravit\u00e9 selon l\u2019\u00e9chelle 1-4?</li>',
      '<li>Ai-je r\u00e9f\u00e9renc\u00e9 le CA sp\u00e9cifique qui est viol\u00e9?</li>',
      '<li>Ai-je \u00e9crit des \u00e9tapes num\u00e9rot\u00e9es que tout d\u00e9veloppeur peut suivre pour reproduire?</li>',
      '<li>S\u2019agit-il vraiment d\u2019un d\u00e9faut \u2014 ou fonctionne-t-il comme pr\u00e9vu?</li>',
      '</ul>',
      '</div>',
      '<p>Vous avez atteint la fin de ce module. Passez au quiz du module pour tester votre compr\u00e9hension.</p>',
    ].join("\n"),

    // ── CAPSTONE (Assessment final) ─────────────────────────────────────────
    "capstone": [
      '<div class="cv-placeholder">',
      '<div class="cv-placeholder-icon">🎯</div>',
      '<h3>Évaluation finale</h3>',
      '<p>Ceci est une évaluation pratique. Ouvrez la page d\u2019\u00e9valuation ci-dessous et suivez les instructions pour la compl\u00e9ter.</p>',
      '<p style="margin-top:var(--space-5);"><a href="capstone.html" target="_blank" class="btn btn-primary" style="text-decoration:none;">Ouvrir l\u2019\u00e9valuation finale \u2192</a></p>',
      '</div>',
    ].join("\n"),
  },

  // ── Agile & Scrum for Developers ──────────────────────────────────────────
  "agile-scrum-dev": {

    // ── MODULE 1: Introduction to Agile and Scrum (Introduction à Agile et Scrum) ──
    "mod-1-1": [
      "<h2>Qu'est-ce que le développement Agile?</h2>",
      "<p>Le développement Agile est une méthodologie qui met l'accent sur <strong>le progrès itératif, la collaboration et l'adaptabilité</strong>. Contrairement aux approches traditionnelles en cascade, Agile divise le travail en petites incréments appelés itérations (généralement 1 à 4 semaines), chaque itération livrant un incrément de produit potentiellement livrable.</p>",

      "<h2>Le Manifeste Agile (2001)</h2>",
      "<p>En février 2001, 17 développeurs de logiciels se sont réunis dans une station de ski en Utah et ont rédigé le Manifeste Agile. Il se compose de quatre valeurs fondamentales :</p>",
      "<ol>",
      "<li><strong>Les individus et leurs interactions</strong> plus que les processus et les outils</li>",
      "<li><strong>Des logiciels opérationnels</strong> plus qu'une documentation exhaustive</li>",
      "<li><strong>La collaboration avec les clients</strong> plus que la négociation contractuelle</li>",
      "<li><strong>L'adaptation au changement</strong> plus que le suivi d'un plan</li>",
      "</ol>",

      "<blockquote>Bien qu'il y ait de la valeur dans les éléments de droite, nous accordons davantage de valeur aux éléments de gauche. — Manifeste Agile</blockquote>",

      "<h2>Les 12 principes Agile</h2>",
      "<p>Le Manifeste est soutenu par 12 principes qui guident les équipes Agile :</p>",
      "<ol>",
      "<li>Notre plus haute priorité est de satisfaire le client par la livraison rapide et continue de logiciels de valeur.</li>",
      "<li>Accueillir les changements d'exigences, même tard dans le développement. Les processus Agile exploitent le changement pour l'avantage compétitif du client.</li>",
      "<li>Livrer des logiciels fonctionnels fréquemment, de quelques semaines à quelques mois, avec une préférence pour les échéances les plus courtes.</li>",
      "<li>Les gens d'affaires et les développeurs doivent travailler ensemble quotidiennement tout au long du projet.</li>",
      "<li>Bâtir des projets autour d'individus motivés. Leur fournir l'environnement et le soutien dont ils ont besoin, et leur faire confiance pour accomplir le travail.</li>",
      "<li>La méthode la plus efficace pour transmettre l'information à une équipe de développement et à l'intérieur de celle-ci est la conversation en face à face.</li>",
      "<li>Un logiciel fonctionnel est la principale mesure de progrès.</li>",
      "<li>Les processus Agile favorisent un développement durable. Les commanditaires, les développeurs et les utilisateurs devraient pouvoir maintenir un rythme constant indéfiniment.</li>",
      "<li>Une attention continue à l'excellence technique et à une bonne conception améliore l'agilité.</li>",
      "<li>La simplicité — l'art de maximiser la quantité de travail non effectué — est essentielle.</li>",
      "<li>Les meilleures architectures, exigences et conceptions émergent d'équipes auto-organisées.</li>",
      "<li>À intervalles réguliers, l'équipe réfléchit à la façon de devenir plus efficace, puis ajuste son comportement en conséquence.</li>",
      "</ol>",

      "<div class=\"callout tip\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Point clé</strong>Agile n'est pas un processus que vous suivez — c'est un état d'esprit que vous adoptez. Les principes mettent l'accent sur les personnes, la collaboration et la réactivité plutôt que sur des plans rigides.</div></div>"
    ].join("\n"),

    "mod-1-2": [
      "<h2>Introduction à Scrum</h2>",
      "<p>Scrum est le cadre Agile le plus utilisé. Il a été formalisé au début des années 1990 par Ken Schwaber et Jeff Sutherland, et est décrit dans le <strong>Guide Scrum</strong> (disponible gratuitement sur scrumguides.org).</p>",

      "<h2>Qu'est-ce que Scrum?</h2>",
      "<p>Scrum est un cadre léger qui aide les personnes, les équipes et les organisations à générer de la valeur grâce à des solutions adaptatives pour des problèmes complexes. Il est :</p>",
      "<ul>",
      "<li><strong>Léger</strong> — éléments prescrits minimaux</li>",
      "<li><strong>Simple à comprendre</strong> — mais difficile à maîtriser</li>",
      "<li><strong>Empirique</strong> — basé sur l'observation et l'adaptation</li>",
      "</ul>",

      "<h2>Théorie Scrum</h2>",
      "<p>Scrum est fondé sur <strong>l'empirisme</strong> — l'idée que la connaissance vient de l'expérience et que les décisions sont basées sur ce qui est connu. Trois piliers soutiennent chaque mise en œuvre :</p>",
      "<ol>",
      "<li><strong>Transparence</strong> — Tous les aspects du processus doivent être visibles pour ceux qui sont responsables du résultat. Un langage commun et des normes partagées assurent la transparence.</li>",
      "<li><strong>Inspection</strong> — Les utilisateurs de Scrum doivent fréquemment inspecter les artefacts Scrum et les progrès vers l'objectif du Sprint pour détecter les écarts indésirables. L'inspection ne doit pas être si fréquente qu'elle gêne le travail.</li>",
      "<li><strong>Adaptation</strong> — Si un aspect du processus dévie des limites acceptables, des ajustements doivent être apportés dès que possible pour minimiser les écarts supplémentaires.</li>",
      "</ol>",

      "<div class=\"callout good\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Scrum ≠ Agile</strong>Scrum est un cadre spécifique qui implémente les valeurs Agile. Il y en a plusieurs autres — Kanban, XP, SAFe — mais Scrum est de loin le plus courant.</div></div>",

      SVG_SCRUM_CYCLE
    ].join("\n"),

    "mod-1-3": [
      "<h2>Agile vs. Développement traditionnel</h2>",
      "<p>Le développement logiciel traditionnel suit généralement un modèle en <strong>Cascade (Waterfall)</strong> : exigences → conception → implémentation → tests → déploiement. Chaque phase se termine complètement avant que la suivante ne commence.</p>",

      SVG_AGILE_VS_TRADITIONAL,

      "<h2>Différences clés</h2>",

      "<h3>Planification</h3>",
      "<p><strong>Cascade :</strong> Toutes les exigences sont recueillies et documentées à l'avance. L'ensemble du projet est planifié avant le début du codage. Les changements nécessitent des demandes de modification formelles.</p>",
      "<p><strong>Agile :</strong> La planification de haut niveau est faite à l'avance, mais la planification détaillée se fait de façon itérative. Les exigences sont affinées tout au long du projet à mesure que la compréhension s'améliore.</p>",

      "<h3>Implication du client</h3>",
      "<p><strong>Cascade :</strong> Le client est impliqué au début (exigences) et à la fin (acceptation). Rétroaction limitée pendant le développement.</p>",
      "<p><strong>Agile :</strong> Le client (ou le Product Owner) est impliqué en continu. La rétroaction est recueillie après chaque itération et intégrée dans la suivante.</p>",

      "<h3>Livraison</h3>",
      "<p><strong>Cascade :</strong> Une seule livraison à la fin du projet, souvent des mois ou des années après le début des travaux.</p>",
      "<p><strong>Agile :</strong> Des livraisons fréquentes (toutes les 1 à 4 semaines). Un logiciel fonctionnel est livré de façon incrémentale.</p>",

      "<h3>Gestion du changement</h3>",
      "<p><strong>Cascade :</strong> Le changement est considéré comme un risque à minimiser. Les demandes de modification passent par des processus d'approbation formels.</p>",
      "<p><strong>Agile :</strong> Le changement est accueilli comme une source d'avantage concurrentiel. Le processus est conçu pour s'adapter au changement, même tard dans le développement.</p>",

      "<h2>Quand utiliser chaque approche</h2>",
      "<p><strong>La Cascade fonctionne bien quand :</strong></p>",
      "<ul>",
      "<li>Les exigences sont bien comprises et peu susceptibles de changer</li>",
      "<li>Le projet est petit ou simple</li>",
      "<li>Des exigences réglementaires ou de conformité imposent une documentation détaillée</li>",
      "</ul>",
      "<p><strong>Agile fonctionne bien quand :</strong></p>",
      "<ul>",
      "<li>Les exigences sont incertaines ou susceptibles d'évoluer</li>",
      "<li>Le projet est complexe ou innovant</li>",
      "<li>La vitesse de mise sur le marché est critique</li>",
      "<li>La rétroaction des clients est facilement disponible</li>",
      "</ul>",

      "<div class=\"callout tip\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Approches hybrides</strong>De nombreuses organisations utilisent un modèle hybride — Cascade pour la planification de haut niveau et la conformité, Agile pour l'exécution et la livraison.</div></div>"
    ].join("\n"),

    "mod-1-4": [
      "<h2>L'état d'esprit Agile</h2>",
      "<p>Adopter Agile ne consiste pas à suivre un ensemble prescrit de pratiques — il s'agit d'adopter un <strong>état d'esprit</strong> qui valorise la collaboration, l'apprentissage et l'adaptabilité plutôt que des processus rigides.</p>",

      "<h2>Éléments clés de l'état d'esprit Agile</h2>",

      "<h3>1. Orientation client</h3>",
      "<p>Tout ce que l'équipe fait vise ultimement à offrir de la valeur au client. L'équipe recherche des commentaires fréquents et s'ajuste en fonction de ce qu'elle apprend.</p>",

      "<h3>2. Collaboration plutôt que silos</h3>",
      "<p>Les développeurs, testeurs, propriétaires de produit et parties prenantes travaillent ensemble tout au long du projet. Pas de transfert par-dessus le mur — l'équipe est collectivement responsable du résultat.</p>",

      "<h3>3. Accepter l'incertitude</h3>",
      "<p>Dans les domaines complexes, on ne peut pas tout savoir à l'avance. Les équipes Agile acceptent cette incertitude et utilisent des boucles de rétroaction courtes pour apprendre et s'adapter.</p>",

      "<h3>4. Amélioration continue</h3>",
      "<p>Les équipes Agile réfléchissent régulièrement à leur processus et cherchent des moyens de s'améliorer. C'est intégré à Scrum par la Rétrospective de Sprint.</p>",

      "<h3>5. Rythme soutenable</h3>",
      "<p>Les équipes devraient travailler à un rythme qu'elles peuvent maintenir indéfiniment. L'épuisement professionnel n'est pas un signe de dévouement — c'est un signe de mauvaise gestion de processus.</p>",

      "<h3>6. Excellence technique</h3>",
      "<p>Les équipes Agile valorisent la qualité. Des pratiques comme le TDD, le refactoring et l'intégration continue maintiennent la base de code en santé et l'équipe rapide.</p>",

      "<blockquote>L'état d'esprit Agile est l'ensemble des attitudes qui soutiennent un environnement de travail Agile. Cela inclut le respect, la collaboration, l'amélioration et les cycles d'apprentissage, la fierté du travail, l'accent sur la livraison de valeur et la capacité à s'adapter au changement. — Agile Alliance</blockquote>"
    ].join("\n"),

    "mod-1-5": [
      "<h2>Études de cas et exemples</h2>",

      "<h2>Étude de cas 1 : Le modèle Agile de Spotify</h2>",
      "<p>Spotify est célèbre pour son modèle Agile unique basé sur les Squads, Tribes, Chapters et Guilds. Chaque Squad agit comme une mini-startup avec une mission claire, et les Squads qui travaillent sur des fonctionnalités connexes sont regroupées en Tribes. Les Chapters rassemblent des personnes ayant des compétences similaires (p. ex. tous les développeurs web), tandis que les Guildes sont des communautés d'intérêt à travers toute l'entreprise.</p>",
      "<p><strong>Leçon clé :</strong> Spotify a adapté Scrum à sa culture plutôt que de forcer sa culture à s'adapter à Scrum.</p>",

      "<h2>Étude de cas 2 : La transformation Agile d'ING</h2>",
      "<p>La banque ING a entrepris une transformation Agile massive en 2015, passant d'une structure hiérarchique traditionnelle à un modèle Squads-and-Tribes inspiré de Spotify. La transition a impliqué 3 500 employés TI et a pris plus d'un an.</p>",
      "<p><strong>Leçon clé :</strong> Les transformations Agile à grande échelle nécessitent un engagement de la direction, un changement culturel et de la patience.</p>",

      "<h2>Étude de cas 3 : Un échec d'adoption Agile</h2>",
      "<p>Une grande entreprise a adopté les cérémonies Scrum mais a conservé sa structure de gestion traditionnelle de commandement et contrôle. Les mêlées quotidiennes sont devenues des rapports d'état aux gestionnaires, les revues de sprint sont devenues des présentations formelles, et les rétrospectives ont été traitées comme des séances de plaintes sans suivi. En 6 mois, l'équipe faisait du « Cascade déguisé en Sprint ».</p>",
      "<p><strong>Leçon clé :</strong> Adopter les cérémonies sans l'état d'esprit, c'est de l'Agile de pacotille. La véritable agilité nécessite la confiance, l'autonomisation et la sécurité psychologique.</p>",

      "<div class=\"callout warn\"><strong class=\"callout-icon\">⚠️</strong><div class=\"callout-body\"><strong>Piège fréquent</strong>La raison la plus courante pour laquelle Agile échoue est que les organisations adoptent la mécanique (mêlées quotidiennes, sprints, rétrospectives) sans adopter les valeurs et principes sous-jacents.</div></div>"
    ].join("\n"),

    // ── MODULE 2: Agile Development Practices (Pratiques de développement Agile) ──
    "mod-2-1": [
      "<h2>Introduction aux pratiques Agile</h2>",
      "<p>Au-delà de Scrum, il existe plusieurs autres pratiques et méthodologies Agile que les équipes utilisent couramment. Chacune offre des forces uniques et peut être combinée avec Scrum pour une approche plus complète.</p>",

      "<h2>Extreme Programming (XP)</h2>",
      "<p>XP est une méthodologie axée sur <strong>l'excellence technique</strong> et <strong>la satisfaction du client</strong>. Les pratiques clés comprennent :</p>",
      "<ul>",
      "<li><strong>Programmation en binôme (Pair Programming)</strong> — deux développeurs partagent un poste de travail</li>",
      "<li><strong>Développement piloté par les tests (TDD)</strong> — écrire les tests avant le code</li>",
      "<li><strong>Intégration continue</strong> — fusionner les changements de code plusieurs fois par jour</li>",
      "<li><strong>Refactoring</strong> — améliorer la conception sans changer le comportement</li>",
      "<li><strong>Conception simple</strong> — la solution la plus simple qui fonctionne</li>",
      "</ul>",

      "<h2>Feature-Driven Development (FDD)</h2>",
      "<p>FDD est une approche Agile pilotée par les modèles qui se concentre sur la conception et la construction de fonctionnalités en itérations courtes. Elle fonctionne bien pour les grandes équipes et les projets plus complexes car elle inclut des phases de conception explicites.</p>",

      "<h2>Développement logiciel Lean</h2>",
      "<p>Adapté du système de fabrication de Toyota, les principes Lean appliqués au logiciel comprennent :</p>",
      "<ul>",
      "<li>Éliminer le gaspillage (code inutile, fonctionnalités, délais)</li>",
      "<li>Amplifier l'apprentissage (cycles de rétroaction courts)</li>",
      "<li>Décider le plus tard possible (différer l'engagement)</li>",
      "<li>Livrer le plus rapidement possible (itérations rapides)</li>",
      "<li>Responsabiliser l'équipe (respecter les personnes)</li>",
      "<li>Bâtir l'intégrité dès le départ (qualité dès le début)</li>",
      "<li>Voir l'ensemble (optimiser le système, pas les parties)</li>",
      "</ul>"
    ].join("\n"),

    "mod-2-2": [
      "<h2>Le cadre Scrum</h2>",
      "<p>Ce sous-module approfondit la structure du cadre Scrum, en développant l'introduction du Module 1.</p>",

      "<h2>Structure de base de Scrum</h2>",
      "<p>Scrum prescrit :</p>",
      "<ul>",
      "<li><strong>3 Rôles :</strong> Product Owner, Scrum Master, Développeurs</li>",
      "<li><strong>5 Événements :</strong> Sprint, Planification du Sprint, Mêlée quotidienne, Revue du Sprint, Rétrospective du Sprint</li>",
      "<li><strong>3 Artefacts :</strong> Backlog du produit, Backlog du Sprint, Incrément</li>",
      "</ul>",

      "<h2>Cadence du Sprint</h2>",
      "<p>Un Sprint est une boîte de temps d'un mois ou moins durant laquelle un Incrément de produit Fini, utilisable et potentiellement livrable est créé. Les Sprints ont des durées constantes tout au long de l'effort de développement. Un nouveau Sprint commence immédiatement après la conclusion du Sprint précédent.</p>",

      "<h2>Flux Scrum</h2>",
      "<ol>",
      "<li><strong>Planification du Sprint</strong> — L'équipe sélectionne les éléments du Backlog du produit et planifie comment les compléter</li>",
      "<li><strong>Exécution du Sprint</strong> — L'équipe travaille sur les éléments sélectionnés, en se coordonnant quotidiennement lors de la Mêlée quotidienne</li>",
      "<li><strong>Revue du Sprint</strong> — L'équipe démontre ce qu'elle a construit et reçoit des commentaires</li>",
      "<li><strong>Rétrospective du Sprint</strong> — L'équipe réfléchit au processus et identifie des améliorations</li>",
      "<li>Le cycle se répète avec la prochaine Planification du Sprint</li>",
      "</ol>"
    ].join("\n"),

    "mod-2-3": [
      "<h2>Méthodologie Kanban</h2>",
      "<p>Kanban (mot japonais signifiant « panneau d'affichage ») est une méthode de gestion visuelle du flux de travail. Elle est originaire du système de fabrication de Toyota et a été adaptée au développement logiciel par David Anderson.</p>",

      "<h2>Principes fondamentaux de Kanban</h2>",
      "<ol>",
      "<li><strong>Visualiser le flux de travail</strong> — Utiliser un tableau avec des colonnes représentant les étapes du flux (À faire, En cours, Terminé)</li>",
      "<li><strong>Limiter le travail en cours (WIP)</strong> — Restreindre le nombre d'éléments pouvant être en cours à la fois pour réduire le multitâche</li>",
      "<li><strong>Gérer le flux</strong> — Surveiller et optimiser le mouvement du travail à travers le système</li>",
      "<li><strong>Rendre les politiques de processus explicites</strong> — Définir et afficher les règles de déplacement du travail entre les étapes</li>",
      "<li><strong>Améliorer en collaboration</strong> — Utiliser les données et les connaissances de l'équipe pour améliorer le processus</li>",
      "</ol>",

      SVG_KANBAN_BOARD,

      "<h2>Kanban vs. Scrum</h2>",
      "<table style=\"width:100%;border-collapse:collapse;font-size:var(--text-sm);margin:var(--space-4) 0;\">",
      "<tr style=\"background:var(--color-bg);\"><th style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);text-align:left;\">Aspect</th><th style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);text-align:left;\">Scrum</th><th style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);text-align:left;\">Kanban</th></tr>",
      "<tr><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Boîte de temps</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Sprints de durée fixe</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Flux continu</td></tr>",
      "<tr><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Rôles</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">PO, SM, Développeurs</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Aucun rôle prescrit</td></tr>",
      "<tr><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Limites WIP</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Implicites (périmètre du Sprint)</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Explicites</td></tr>",
      "<tr><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Changements</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Impossible de changer le périmètre du Sprint</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Les changements peuvent survenir à tout moment</td></tr>",
      "</table>",

      "<div class=\"callout tip\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Scrumban</strong>De nombreuses équipes utilisent une approche hybride appelée Scrumban — utilisant les rôles et événements de Scrum mais le tableau visuel et les limites WIP de Kanban pour la gestion du flux.</div></div>"
    ].join("\n"),

    // ── MODULE 3: Scrum Roles and Responsibilities (Rôles et responsabilités Scrum) ──
    "mod-3-1": [
      "<h2>Le Product Owner</h2>",
      "<p>Le Product Owner (PO) est la personne unique responsable de <strong>maximiser la valeur du produit</strong> résultant du travail de l'Équipe de Développement. C'est un rôle singulier — pas un comité.</p>",

      SVG_SCRUM_ROLES,

      "<h2>Responsabilités clés</h2>",
      "<ul>",
      "<li><strong>Gérer le Backlog du produit</strong> — Exprimer clairement les éléments du Backlog du produit, les ordonner pour atteindre les objectifs, et s'assurer que le Backlog est visible, transparent et clair pour tous.</li>",
      "<li><strong>Définir l'objectif du produit</strong> — Établir la vision à long terme du produit qui guide tout le travail du Sprint.</li>",
      "<li><strong>Gestion des parties prenantes</strong> — Agir comme principal lien entre les parties prenantes et l'Équipe de Développement.</li>",
      "<li><strong>Décisions de valeur</strong> — Prendre la décision finale sur les compromis de priorité et les décisions de périmètre.</li>",
      "</ul>",

      "<h2>PO vs. Gestionnaire de produit</h2>",
      "<p>Dans de nombreuses organisations, le rôle de Product Owner est combiné ou soutenu par un Gestionnaire de produit. Le PO se concentre sur <strong>le raffinement du backlog et les décisions au niveau du sprint</strong>, tandis qu'un Gestionnaire de produit peut se concentrer sur la stratégie de marché et la recherche client. Dans Scrum, ces responsabilités convergent souvent vers une seule personne.</p>",

      "<div class=\"callout warn\"><strong class=\"callout-icon\">⚠️</strong><div class=\"callout-body\"><strong>Antipatron courant</strong>Le PO ne devrait pas être un « proxy » qui ne fait que relayer les ordres des parties prenantes. Un PO efficace a l'autorité de prendre de véritables décisions de priorisation.</div></div>"
    ].join("\n"),

    "mod-3-2": [
      "<h2>Le Scrum Master</h2>",
      "<p>Le Scrum Master est un <strong>leader servant</strong> pour l'Équipe Scrum. Il est responsable de la promotion et du soutien de Scrum tel que défini dans le Guide Scrum. Le SM aide tout le monde à comprendre la théorie, les pratiques, les règles et les valeurs de Scrum.</p>",

      "<h2>Responsabilités clés</h2>",
      "<ul>",
      "<li><strong>Coacher l'équipe</strong> — Enseigner à l'Équipe de Développement l'autogestion et la polyvalence.</li>",
      "<li><strong>Faciliter les événements</strong> — S'assurer que tous les événements Scrum ont lieu, sont productifs et respectent leur boîte de temps.</li>",
      "<li><strong>Éliminer les obstacles</strong> — Identifier et éliminer activement les bloqueurs qui ralentissent l'équipe.</li>",
      "<li><strong>Protéger l'équipe</strong> — Protéger l'équipe des interruptions externes et des pressions pendant le Sprint.</li>",
      "<li><strong>Coacher l'organisation</strong> — Aider les parties prenantes à comprendre Scrum et la valeur du contrôle empirique des processus.</li>",
      "</ul>",

      "<h2>Scrum Master ≠ Gestionnaire de projet</h2>",
      "<p>Les gestionnaires de projet traditionnels assignent des tâches, suivent les progrès par rapport à un plan et rendent compte de l'état d'avancement. Les Scrum Masters ne font rien de tout cela — ils facilitent l'autogestion de l'équipe et éliminent les obstacles. Dans une transition Scrum, les anciens chefs de projet constatent souvent que le rôle de SM nécessite un changement d'état d'esprit important.</p>",

      "<div class=\"callout tip\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Leadership servant</strong>Le pouvoir du SM vient de l'influence et du service, pas de l'autorité. Les meilleurs Scrum Masters rendent l'équipe meilleure sans que l'équipe ne réalise qu'elle était coachée.</div></div>"
    ].join("\n"),

    "mod-3-3": [
      "<h2>L'Équipe de Développement</h2>",
      "<p>L'Équipe de Développement est composée de professionnels qui effectuent le travail de livraison d'un Incrément de produit <strong>Fini</strong> potentiellement livrable à la fin de chaque Sprint. Elle est auto-organisée et polyvalente.</p>",

      "<h2>Caractéristiques d'une grande équipe de développement</h2>",
      "<ul>",
      "<li><strong>Auto-organisée</strong> — Personne (pas même le SM ou le PO) ne dit à l'Équipe de Développement comment transformer les éléments du Backlog du produit en un Incrément de valeur.</li>",
      "<li><strong>Polyvalente</strong> — L'équipe possède toutes les compétences nécessaires pour créer un Incrément de produit : conception, développement, tests, déploiement, etc.</li>",
      "<li><strong>Responsable collectivement</strong> — Toute l'équipe partage la responsabilité de livrer ses engagements de Sprint.</li>",
      "<li><strong>Membres stables</strong> — La recherche montre que les équipes stables performent mieux. Un roulement fréquent réduit la vélocité et la cohésion.</li>",
      "<li><strong>Taille optimale</strong> — 3 à 9 personnes. Les petites équipes peuvent manquer de compétences; les grandes équipes ont du mal à se coordonner.</li>",
      "</ul>",

      "<h2>Pas de sous-équipes</h2>",
      "<p>Le Guide Scrum stipule explicitement qu'il n'y a pas de sous-équipes au sein de l'Équipe de Développement — pas d'équipe AQ distincte, pas d'équipe d'architecture, pas d'équipe de base de données. Tout le monde travaille ensemble comme une seule unité. Les titres et spécialisations sont reconnus (un développeur spécialisé en sécurité reste d'abord un membre de l'équipe), mais la responsabilité est collective.</p>",

      "<div class=\"callout good\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Polyvalence en pratique</strong>Une équipe vraiment polyvalente peut amener une fonctionnalité de l'idée au déploiement, en passant par un logiciel fonctionnel, sans transferts à des équipes externes. C'est l'objectif — même s'il faut du temps pour développer les compétences nécessaires.</div></div>"
    ].join("\n"),

    "mod-3-4": [
      "<h2>Les parties prenantes</h2>",
      "<p>Les parties prenantes sont des individus ou des groupes qui ont un <strong>intérêt direct</strong> dans le produit en cours de construction. Ils ne font pas partie de l'Équipe Scrum mais sont essentiels à son succès. Les parties prenantes incluent les clients, les utilisateurs, les dirigeants, les équipes de soutien, les responsables de la conformité et toute personne affectée par le produit.</p>",

      "<h2>Comment les parties prenantes s'engagent dans Scrum</h2>",
      "<ul>",
      "<li><strong>Revue du Sprint</strong> — Le point de contact formel principal. Les parties prenantes assistent à la Revue du Sprint pour inspecter l'Incrément et fournir des commentaires qui façonnent le Backlog du produit.</li>",
      "<li><strong>Raffinement du Backlog</strong> — Les parties prenantes collaborent avec le Product Owner pour clarifier les exigences et les priorités.</li>",
      "<li><strong>Transparence</strong> — Le Backlog du produit est visible pour toutes les parties prenantes afin qu'elles puissent suivre les progrès et comprendre ce qui s'en vient.</li>",
      "</ul>",

      "<h2>Responsabilités des parties prenantes</h2>",
      "<ul>",
      "<li>Fournir des commentaires en temps opportun lors des Revues de Sprint</li>",
      "<li>Respecter la concentration de l'Équipe Scrum pendant un Sprint (pas de changements de périmètre en cours de Sprint)</li>",
      "<li>Prendre des décisions lorsque nécessaire (p. ex., questions de compromis)</li>",
      "<li>Communiquer clairement les contraintes et les priorités d'affaires</li>",
      "</ul>",

      "<div class=\"callout warn\"><strong class=\"callout-icon\">⚠️</strong><div class=\"callout-body\"><strong>Ingérence des parties prenantes</strong>L'antipatron le plus courant est de traiter la Mêlée quotidienne comme un outil de rapport d'état ou de tenter d'ajouter du périmètre en cours de Sprint. Le rôle du Scrum Master inclut la protection de l'équipe contre ces perturbations.</div></div>"
    ].join("\n"),

    // ── MODULE 4: Scrum Events and Artifacts (Événements et artefacts Scrum) ──
    "mod-4-1": [
      "<h2>Le Sprint</h2>",
      "<p>Le Sprint est le <strong>cœur de Scrum</strong>. C'est une boîte de temps d'un mois ou moins durant laquelle un Incrément de produit Fini, utilisable et potentiellement livrable est créé. Les Sprints ont des durées constantes tout au long d'un effort de développement — on ne change pas la durée du Sprint en milieu de projet.</p>",

      "<h2>Règles clés</h2>",
      "<ul>",
      "<li>Un nouveau Sprint commence immédiatement après la conclusion du Sprint précédent.</li>",
      "<li>Tout le travail nécessaire pour atteindre l'Objectif du produit se fait pendant les Sprints.</li>",
      "<li>Aucun changement n'est effectué qui pourrait compromettre l'Objectif du Sprint pendant le Sprint.</li>",
      "<li>La durée du Sprint peut être raccourcie ou le Sprint peut être annulé par le Product Owner si l'Objectif du Sprint devient obsolète.</li>",
      "</ul>",

      SVG_SPRINT_TIMELINE,

      "<h2>Pourquoi la boîte de temps est importante</h2>",
      "<p>Les Sprints de durée fixe créent un rythme prévisible qui permet à l'équipe de planifier, exécuter, inspecter et s'adapter. Cette cadence renforce la confiance des parties prenantes qui peuvent compter sur un flux régulier de valeur. Elle crée aussi une pression saine — savoir que vous n'avez que deux semaines pour livrer concentre merveilleusement l'esprit.</p>",

      "<div class=\"callout tip\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Choisissez votre cadence</strong>Les Sprints d'une semaine maximisent la rétroaction mais augmentent les frais généraux. Les Sprints de quatre semaines réduisent les cérémonies mais retardent la rétroaction. Deux semaines est le choix le plus courant pour les équipes de développement logiciel.</div></div>"
    ].join("\n"),

    "mod-4-2": [
      "<h2>Planification du Sprint</h2>",
      "<p>La Planification du Sprint initie le Sprint en définissant le travail à effectuer. Le plan est créé en collaboration par toute l'Équipe Scrum. La Planification du Sprint est limitée à un maximum de <strong>8 heures pour un Sprint d'un mois</strong> (proportionnellement moins pour les Sprints plus courts).</p>",

      "<h2>Trois sujets</h2>",
      "<h3>1. Pourquoi ce Sprint est-il précieux?</h3>",
      "<p>Le Product Owner propose comment le produit pourrait augmenter sa valeur et son utilité dans le Sprint à venir. L'équipe collabore à la définition d'un <strong>Objectif de Sprint</strong> — un objectif unique et concis pour le Sprint.</p>",

      "<h3>2. Qu'est-ce qui peut être fait pendant ce Sprint?</h3>",
      "<p>L'Équipe de Développement sélectionne les éléments du Backlog du produit à inclure dans le Sprint en cours. L'équipe tient compte des performances passées, de la capacité et de la Définition de Fini. L'équipe — pas le PO ni un gestionnaire — fait cette sélection.</p>",

      "<h3>3. Comment le travail choisi sera-t-il réalisé?</h3>",
      "<p>Pour chaque élément sélectionné du Backlog du produit, l'Équipe de Développement planifie le travail nécessaire. Cela implique souvent de décomposer les éléments en tâches plus petites (heures à une journée). L'équipe peut ou non créer un tableau de tâches ou un plan — l'important est d'avoir une compréhension commune de la façon dont ils atteindront l'Objectif du Sprint.</p>",

      "<div class=\"callout good\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Poker de planification</strong>De nombreuses équipes utilisent le Poker de planification (une technique d'estimation basée sur le consensus) pendant la Planification du Sprint pour estimer l'effort des éléments du Backlog.</div></div>"
    ].join("\n"),

    "mod-4-3": [
      "<h2>Mêlée quotidienne (Daily Scrum)</h2>",
      "<p>La Mêlée quotidienne est un <strong>événement de 15 minutes</strong> pour que l'Équipe de Développement inspecte les progrès vers l'Objectif du Sprint et adapte le travail planifié à venir. Elle a lieu au même endroit et à la même heure chaque jour ouvrable du Sprint.</p>",

      "<h2>Ce qu'elle N'EST PAS</h2>",
      "<ul>",
      "<li><strong>Pas un rapport d'état à la direction</strong> — Les parties prenantes peuvent observer mais ne devraient pas participer ni l'utiliser pour l'imputabilité.</li>",
      "<li><strong>Pas une session de résolution de problèmes</strong> — Les problèmes identifiés pendant la Mêlée quotidienne sont discutés séparément (souvent après la Mêlée quotidienne).</li>",
      "<li><strong>Pas une mise à jour à tour de rôle</strong> — L'équipe devrait se concentrer sur les progrès vers l'Objectif du Sprint, pas sur le statut individuel.</li>",
      "</ul>",

      "<h2>Formats courants</h2>",
      "<p>Le format classique des « trois questions » est :</p>",
      "<ol>",
      "<li>Qu'ai-je fait hier qui a aidé l'équipe à atteindre l'Objectif du Sprint?</li>",
      "<li>Que vais-je faire aujourd'hui pour aider l'équipe à atteindre l'Objectif du Sprint?</li>",
      "<li>Voit-je un obstacle qui m'empêche ou empêche l'équipe d'atteindre l'Objectif du Sprint?</li>",
      "</ol>",
      "<p>Certaines équipes parcourent plutôt le tableau (en déplaçant les cartes de gauche à droite sur le tableau Kanban), ce qui peut être plus visuel et engageant.</p>",

      "<div class=\"callout tip\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Restez concis</strong>La Mêlée quotidienne n'est pas une réunion debout — c'est un événement de planification. Concentrez-vous sur la coordination et l'ajustement, pas sur le rapport d'état.</div></div>"
    ].join("\n"),

    "mod-4-4": [
      "<h2>Revue du Sprint</h2>",
      "<p>La Revue du Sprint a lieu à la fin du Sprint pour <strong>inspecter l'Incrément</strong> et adapter le Backlog du produit. Elle est limitée à un maximum de 4 heures pour un Sprint d'un mois (moins pour les Sprints plus courts).</p>",

      "<h2>Ce qui se passe lors d'une Revue du Sprint</h2>",
      "<ul>",
      "<li>Le Product Owner explique quels éléments du Backlog du produit ont été Terminés et lesquels ne l'ont pas été.</li>",
      "<li>L'Équipe de Développement discute de ce qui a bien fonctionné, des problèmes rencontrés et de la façon dont ils ont été résolus.</li>",
      "<li>L'Équipe de Développement démontre le travail qui est Terminé et répond aux questions sur l'Incrément.</li>",
      "<li>Les parties prenantes fournissent des commentaires et discutent du marché ou du paysage produit global.</li>",
      "<li>L'ensemble du groupe collabore sur la suite des choses, en mettant à jour le Backlog du produit en conséquence.</li>",
      "</ul>",

      "<h2>Revue ≠ Démo</h2>",
      "<p>De nombreuses équipes commettent l'erreur de traiter la Revue du Sprint comme une réunion de démonstration uniquement. La revue est une <strong>session de travail</strong> où l'équipe et les parties prenantes inspectent ce qui a été construit et ajustent les priorités en collaboration. Cela devrait ressembler à une conversation, pas à une présentation.</p>",

      "<div class=\"callout good\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Encouragez la rétroaction honnête</strong>Les parties prenantes devraient se sentir à l'aise de dire « ce n'est pas ce dont nous avions besoin. » La Revue du Sprint est une occasion d'apprentissage, pas une porte d'approbation.</div></div>"
    ].join("\n"),

    "mod-4-5": [
      "<h2>Rétrospective du Sprint</h2>",
      "<p>La Rétrospective du Sprint a lieu après la Revue du Sprint et avant la prochaine Planification du Sprint. Elle est limitée à un maximum de <strong>3 heures pour un Sprint d'un mois</strong>. Son but est d'inspecter comment le dernier Sprint s'est déroulé en ce qui concerne les personnes, les relations, les processus et les outils, et de créer un plan d'amélioration.</p>",

      "<h2>Structure de la rétrospective</h2>",
      "<ol>",
      "<li><strong>Préparer le terrain</strong> — Créer un environnement sûr pour une discussion ouverte. Établir la confidentialité et une culture sans blâme.</li>",
      "<li><strong>Recueillir des données</strong> — Collecter des faits sur ce qui s'est passé pendant le Sprint (métriques, événements, observations).</li>",
      "<li><strong>Générer des idées</strong> — Analyser les données pour identifier les causes profondes des succès et des échecs.</li>",
      "<li><strong>Décider quoi faire</strong> — Sélectionner les améliorations les plus impactantes et les transformer en expériences réalisables.</li>",
      "<li><strong>Clôturer</strong> — Résumer les résultats et célébrer les succès.</li>",
      "</ol>",

      "<h2>Formats de rétrospective courants</h2>",
      "<ul>",
      "<li><strong>Commencer / Arrêter / Continuer</strong> — Que devrions-nous commencer à faire, arrêter de faire et continuer à faire?</li>",
      "<li><strong>Fâché / Triste / Content</strong> — Qu'est-ce qui nous a fâchés, rendus tristes et contents pendant le Sprint?</li>",
      "<li><strong>Les 4L</strong> — Qu'avons-nous Aimé, Appris, Manqué et Désiré?</li>",
      "<li><strong>Bateau à voile</strong> — Quel est le vent (qui nous aide) et quelles sont les ancres (qui nous ralentissent)?</li>",
      "</ul>",

      "<div class=\"callout warn\"><strong class=\"callout-icon\">⚠️</strong><div class=\"callout-body\"><strong>Éléments d'action</strong>Le piège le plus courant est d'avoir une excellente conversation mais de ne prendre aucune mesure. Chaque Rétrospective devrait produire au moins une amélioration réalisable à laquelle l'équipe s'engage.</div></div>"
    ].join("\n"),

    "mod-4-6": [
      "<h2>Backlog du produit</h2>",
      "<p>Le Backlog du produit est une <strong>liste ordonnée de tout ce qui pourrait être nécessaire</strong> dans le produit. C'est la source unique des exigences pour tout changement à apporter au produit. Le Product Owner est responsable du Backlog du produit, y compris son contenu, sa disponibilité et son ordonnancement.</p>",

      "<h2>Caractéristiques</h2>",
      "<ul>",
      "<li><strong>Émergent</strong> — Le Backlog n'est jamais complet. Il évolue à mesure que le produit, le marché et la technologie changent.</li>",
      "<li><strong>Ordonné</strong> — Les éléments en haut (priorité la plus élevée) sont plus urgents et mieux raffinés que les éléments en bas.</li>",
      "<li><strong>Transparent</strong> — Visible pour toutes les parties prenantes. Tous peuvent voir ce qui est planifié et dans quel ordre.</li>",
      "<li><strong>Raffiné dynamiquement</strong> — Les éléments sont régulièrement raffinés lors des sessions de Raffinement du Backlog (généralement 5-10% de la capacité du Sprint).</li>",
      "</ul>",

      "<h2>User Stories</h2>",
      "<p>La plupart des Backlogs de produit utilisent des <strong>User Stories</strong> comme format pour les éléments du Backlog. Un modèle de user story standard est :</p>",
      "<blockquote>En tant que [rôle d'utilisateur], je veux [objectif] afin de [raison].</blockquote>",
      "<p>Les bonnes user stories suivent le moyen mnémotechnique <strong>INVEST</strong> : Independent (indépendante), Negotiable (négociable), Valuable (de valeur), Estimable (estimable), Small (petite), Testable (testable).</p>",

      "<div class=\"callout tip\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Définition de Prêt</strong>De nombreuses équipes définissent une « Définition de Prêt » pour s'assurer que les éléments du Backlog sont suffisamment raffinés avant d'entrer dans un Sprint. C'est un accord au niveau de l'équipe, pas une règle Scrum.</div></div>"
    ].join("\n"),

    "mod-4-7": [
      "<h2>Backlog du Sprint</h2>",
      "<p>Le Backlog du Sprint est un plan — <strong>visible en temps réel</strong> — créé par l'Équipe de Développement pour le Sprint en cours. Il comprend les éléments sélectionnés du Backlog du produit (le « quoi ») plus un plan pour les livrer (le « comment »).</p>",

      "<h2>Propriétés</h2>",
      "<ul>",
      "<li>Il appartient à l'Équipe de Développement — seuls ses membres peuvent le modifier pendant le Sprint.</li>",
      "<li>Il est hautement visible — tous peuvent voir sur quoi l'équipe travaille et ce qui reste à faire.</li>",
      "<li>Il est mis à jour tout au long du Sprint à mesure que l'équipe en apprend davantage sur le travail nécessaire.</li>",
      "<li>L'Objectif du Sprint est le « pourquoi » — l'objectif cohérent qui relie les éléments sélectionnés.</li>",
      "</ul>",

      "<h2>Mises à jour quotidiennes</h2>",
      "<p>Le Backlog du Sprint n'est pas un document statique. Pendant la Mêlée quotidienne, l'équipe inspecte les progrès et peut ajuster le Backlog du Sprint. Si un nouveau travail est découvert, il est ajouté; si un travail planifié s'avère inutile, il est retiré. Le Backlog du Sprint est toujours le reflet de la meilleure compréhension actuelle de l'équipe du travail nécessaire pour atteindre l'Objectif du Sprint.</p>",

      "<div class=\"callout good\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Outils de visualisation</strong>La plupart des équipes utilisent un tableau physique ou numérique (Jira, Trello, Azure Boards) pour visualiser le Backlog du Sprint. Les colonnes incluent généralement À faire, En cours et Terminé — bien que les équipes puissent ajouter plus d'étapes selon leurs besoins.</div></div>"
    ].join("\n"),

    "mod-4-8": [
      "<h2>Incrément et Définition de Fini</h2>",
      "<p>L'<strong>Incrément</strong> est la somme de tous les éléments du Backlog du produit terminés pendant un Sprint, combinés à tous les Sprints précédents. À la fin d'un Sprint, le nouvel Incrément doit être Fini, utilisable et répondre à la Définition de Fini.</p>",

      "<h2>Définition de Fini (DoD)</h2>",
      "<p>La Définition de Fini est une <strong>description formelle de l'état de l'Incrément</strong> lorsqu'il répond aux mesures de qualité requises pour le produit. Si un élément du Backlog du produit ne répond pas à la DoD, il ne peut pas être livré ou présenté lors de la Revue du Sprint.</p>",

      "<h2>Exemple de DoD pour une équipe logicielle</h2>",
      "<ul>",
      "<li>Le code est écrit et révisé par les pairs</li>",
      "<li>Les tests unitaires automatisés réussissent avec une couverture de 80%+</li>",
      "<li>Les tests d'intégration réussissent</li>",
      "<li>La fonctionnalité a été testée dans un environnement de préproduction</li>",
      "<li>La documentation (le cas échéant) est mise à jour</li>",
      "<li>Aucun défaut critique ou de gravité élevée connu</li>",
      "<li>Le Product Owner a accepté le travail</li>",
      "</ul>",

      "<h2>Pourquoi la DoD est importante</h2>",
      "<p>La DoD crée une compréhension commune de ce que « Fini » signifie. Sans elle, les équipes perdent du temps à débattre pour savoir si le travail est complet. Elle renforce également la confiance des parties prenantes qui peuvent compter sur une norme de qualité cohérente. Si l'organisation a une DoD, toutes les Équipes Scrum doivent la suivre comme minimum; les équipes individuelles peuvent ajouter des critères plus stricts.</p>",

      "<div class=\"callout warn\"><strong class=\"callout-icon\">⚠️</strong><div class=\"callout-body\"><strong>Travail non terminé</strong>Si la DoD n'est pas respectée, le travail n'est pas un Incrément. Il devrait rester dans le Backlog du produit pour un Sprint futur, ou l'équipe peut négocier un périmètre plus petit pour le Sprint.</div></div>"
    ].join("\n"),

    // ── MODULE 5: Agile Testing and Continuous Integration (Tests Agile et Intégration continue) ──
    "mod-5-1": [
      "<h2>Quadrants de tests Agile</h2>",
      "<p>Les Quadrants de tests Agile, créés par Brian Marick, fournissent un <strong>modèle mental</strong> pour réfléchir aux tests dans les projets Agile. Ils aident les équipes à s'assurer d'avoir une stratégie de test équilibrée couvrant à la fois les tests orientés métier et les tests orientés technologie, au niveau du produit et du système.</p>",

      SVG_TESTING_QUADRANTS,

      "<h2>Les quatre quadrants</h2>",
      "<table style=\"width:100%;border-collapse:collapse;font-size:var(--text-sm);margin:var(--space-4) 0;\">",
      "<tr style=\"background:var(--color-bg);\"><th style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Quadrant</th><th style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Focalisation</th><th style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Exemples</th></tr>",
      "<tr><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);font-weight:bold;\">Q1</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Orienté technologie — soutient l'équipe</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Tests unitaires, tests de composants</td></tr>",
      "<tr><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);font-weight:bold;\">Q2</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Orienté métier — soutient l'équipe</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Tests fonctionnels, tests d'histoire, prototypes</td></tr>",
      "<tr><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);font-weight:bold;\">Q3</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Orienté métier — critique le produit</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Tests exploratoires, tests d'utilisabilité, TAU</td></tr>",
      "<tr><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);font-weight:bold;\">Q4</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Orienté technologie — critique le produit</td><td style=\"padding:var(--space-2) var(--space-3);border:1px solid var(--color-border);\">Tests de performance, tests de sécurité, tests de charge</td></tr>",
      "</table>",

      "<p>Les quadrants ne sont pas des phases — ce sont une liste de vérification. Une stratégie de test Agile saine inclut une couverture dans les quatre quadrants, avec l'emphase appropriée selon le contexte.</p>"
    ].join("\n"),

    "mod-5-2": [
      "<h2>Développement piloté par les tests (TDD)</h2>",
      "<p>Le Développement piloté par les tests est une <strong>pratique de codage</strong> où vous écrivez un test qui échoue avant d'écrire le code de production. Le mantra est : <strong>Rouge — Vert — Refactor</strong>.</p>",

      "<h2>Le cycle TDD</h2>",
      "<ol>",
      "<li><strong>Rouge</strong> — Écrire un test qui échoue. Le test définit une nouvelle fonction ou amélioration, et il devrait échouer parce que la fonctionnalité n'existe pas encore.</li>",
      "<li><strong>Vert</strong> — Écrire le minimum de code de production pour faire passer le test. Ne vous souciez pas encore de l'élégance — faites simplement passer le test.</li>",
      "<li><strong>Refactor</strong> — Nettoyer le code, supprimer les duplications et améliorer la conception, tout en gardant tous les tests au vert.</li>",
      "<li>Répéter pour l'exigence suivante.</li>",
      "</ol>",

      SVG_TDD_CYCLE,

      "<h2>Avantages du TDD</h2>",
      "<ul>",
      "<li><strong>Meilleure conception</strong> — Écrire les tests d'abord vous oblige à réfléchir aux interfaces et aux contrats avant l'implémentation.</li>",
      "<li><strong>Documentation vivante</strong> — Les tests servent de documentation exécutable de ce que le système fait.</li>",
      "<li><strong>Filet de sécurité pour la régression</strong> — Une suite de tests complète signifie que vous pouvez refactoriser en toute confiance.</li>",
      "<li><strong>Temps de débogage réduit</strong> — Les bogues sont détectés en quelques minutes, pas en quelques semaines.</li>",
      "</ul>",

      "<div class=\"callout tip\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>TDD ≠ Tests</strong>Le TDD est une technique de conception qui produit des tests comme sous-produit. Le principal avantage est une meilleure conception du code, pas seulement des tests automatisés.</div></div>"
    ].join("\n"),

    "mod-5-3": [
      "<h2>Pipeline d'intégration continue</h2>",
      "<p>L'Intégration continue (IC) est une pratique de développement où les développeurs <strong>fusionnent les changements de code dans un référentiel partagé fréquemment</strong> — idéalement plusieurs fois par jour. Chaque fusion déclenche une séquence automatisée de construction et de test pour détecter les problèmes tôt.</p>",

      "<h2>Pratiques clés</h2>",
      "<ul>",
      "<li><strong>Validations fréquentes</strong> — Pousser le code au moins une fois par jour, de préférence après chaque petit changement ciblé.</li>",
      "<li><strong>Construction automatisée</strong> — Chaque validation déclenche une construction automatisée sur le serveur CI.</li>",
      "<li><strong>Tests automatisés</strong> — La construction exécute des tests unitaires, des tests d'intégration et souvent une analyse statique.</li>",
      "<li><strong>Rétroaction rapide</strong> — La construction devrait se terminer en moins de 10 minutes. Les constructions longues découragent les validations fréquentes.</li>",
      "<li><strong>Réparer les constructions brisées immédiatement</strong> — Une construction brisée est la priorité absolue de l'équipe. Personne ne valide de nouveau code tant que la construction n'est pas verte.</li>",
      "</ul>",

      "<h2>Pipeline CI typique</h2>",
      "<ol>",
      "<li>Le développeur valide le code dans le référentiel partagé</li>",
      "<li>Le serveur CI détecte le changement et récupère le dernier code</li>",
      "<li>Le serveur compile le code et exécute les tests unitaires</li>",
      "<li>Si les tests réussissent, le code est déployé dans un environnement de préproduction pour les tests d'intégration</li>",
      "<li>Si toutes les étapes réussissent, l'équipe reçoit une notification de construction verte</li>",
      "<li>Si une étape échoue, l'équipe est notifiée immédiatement</li>",
      "</ol>",

      SVG_CI_CD_PIPELINE,

      "<div class=\"callout warn\"><strong class=\"callout-icon\">⚠️</strong><div class=\"callout-body\"><strong>CI n'est pas CD</strong>L'Intégration continue (fusion et test) est différente de la Livraison continue ou du Déploiement continu (publication automatique en production). CI est un prérequis pour les deux.</div></div>"
    ].join("\n"),

    "mod-5-4": [
      "<h2>Tests automatisés vs. Tests manuels</h2>",
      "<p>Une stratégie de test Agile équilibrée utilise <strong>à la fois des tests automatisés et manuels</strong>. L'objectif n'est pas l'automatisation à 100% — c'est l'approche de test la plus efficace pour votre contexte.</p>",

      "<h2>Quand automatiser</h2>",
      "<ul>",
      "<li><strong>Tests de régression</strong> — Tests qui doivent être exécutés de façon répétée (chaque construction, chaque Sprint).</li>",
      "<li><strong>Tests unitaires et d'intégration</strong> — Vérifications rapides et déterministes qui détectent les changements cassants.</li>",
      "<li><strong>Tests de performance</strong> — Tests qui nécessitent des mesures précises et reproductibles.</li>",
      "<li><strong>Validation des données</strong> — Vérification de grands ensembles de données ou de contrats d'API.</li>",
      "</ul>",

      "<h2>Quand les tests manuels sont essentiels</h2>",
      "<ul>",
      "<li><strong>Tests exploratoires</strong> — Apprendre le système en l'utilisant de façon créative pour trouver des problèmes inattendus.</li>",
      "<li><strong>Tests d'utilisabilité</strong> — Évaluer si l'interface est intuitive et conviviale.</li>",
      "<li><strong>Tests visuels</strong> — Vérifier la mise en page, les couleurs et la cohérence visuelle que les outils automatisés peinent à évaluer.</li>",
      "<li><strong>Cas limites</strong> — Scénarios nouveaux que les scripts automatisés pourraient ne pas couvrir.</li>",
      "</ul>",

      "<h2>La pyramide d'automatisation des tests</h2>",
      "<p>La pyramide d'automatisation des tests de Mike Cohn recommande : <strong>beaucoup de tests unitaires (base), quelques tests d'intégration (milieu), peu de tests UI/de bout en bout (sommet)</strong>. Cela garantit une rétroaction rapide (les tests unitaires s'exécutent en millisecondes) tout en couvrant les parcours utilisateur critiques.</p>",

      "<div class=\"callout tip\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Shift Left</strong>Tester plus tôt dans le processus de développement (shift left) réduit le coût des défauts. Automatisez ce que vous pouvez, testez manuellement ce que vous devez, et déplacez les activités de test plus tôt dans chaque Sprint.</div></div>"
    ].join("\n"),

    // ── MODULE 6: Scaling Agile (Mise à l'échelle Agile) ──
    "mod-6-1": [
      "<h2>Scrum of Scrums</h2>",
      "<p>Scrum of Scrums (SoS) est une <strong>technique de mise à l'échelle</strong> pour coordonner plusieurs équipes Scrum travaillant sur le même produit. C'est une méta-réunion où les représentants de chaque équipe se rencontrent pour faire rapport sur les progrès, discuter des problèmes de coordination et résoudre les dépendances inter-équipes.</p>",

      "<h2>Comment ça fonctionne</h2>",
      "<ul>",
      "<li>Chaque équipe envoie un ambassadeur (généralement un développeur, pas nécessairement le SM) à la réunion SoS.</li>",
      "<li>Les réunions ont généralement lieu 2 à 3 fois par semaine.</li>",
      "<li>L'accent est mis sur les préoccupations inter-équipes, pas sur le statut de chaque équipe.</li>",
      "<li>La structure reflète la Mêlée quotidienne mais au niveau inter-équipe.</li>",
      "</ul>",

      "<h2>Questions courantes du SoS</h2>",
      "<ol>",
      "<li>Qu'est-ce que notre équipe a fait depuis le dernier SoS qui affecte d'autres équipes?</li>",
      "<li>Qu'est-ce que notre équipe fera avant le prochain SoS qui pourrait affecter d'autres équipes?</li>",
      "<li>Quelles dépendances ou problèmes notre équipe a-t-elle avec d'autres équipes?</li>",
      "</ol>",

      "<div class=\"callout tip\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Scrum of Scrums est Scrum</strong>Le SoS n'est pas un cadre séparé — c'est une simple extension de Scrum pour plusieurs équipes. Chaque équipe individuelle suit toujours Scrum tel que défini dans le Guide Scrum.</div></div>"
    ].join("\n"),

    "mod-6-2": [
      "<h2>SAFe (Scaled Agile Framework)</h2>",
      "<p>SAFe est un <strong>cadre de mise à l'échelle commercial</strong> développé par Dean Leffingwell. Il fournit une approche détaillée et structurée pour mettre Agile à l'échelle dans de grandes entreprises comptant des centaines ou des milliers de personnes.</p>",

      "<h2>Concepts clés</h2>",
      "<ul>",
      "<li><strong>Agile Release Train (ART)</strong> — Une équipe durable d'équipes Agile (50-125 personnes) qui planifie, s'engage et exécute ensemble.</li>",
      "<li><strong>Program Increment (PI)</strong> — Une boîte de temps fixe (généralement 8-12 semaines) pendant laquelle les ART livrent de la valeur.</li>",
      "<li><strong>Planification PI</strong> — Un grand événement de plusieurs jours où toutes les équipes d'un ART planifient ensemble, identifient les dépendances et fixent des objectifs.</li>",
      "<li><strong>Solution Train</strong> — Pour les systèmes encore plus grands, un ART de niveau méta qui coordonne plusieurs ART.</li>",
      "</ul>",

      "<h2>Avantages et inconvénients</h2>",
      "<p><strong>Avantages :</strong> Fournit une structure claire pour les grandes organisations; s'aligne sur la gestion de portefeuille; dispose de programmes de formation et de certification étendus.</p>",
      "<p><strong>Inconvénients :</strong> Peut être trop prescriptif; nécessite un investissement organisationnel important; les critiques soutiennent qu'il ajoute trop de surcharge de processus.</p>",

      "<div class=\"callout warn\"><strong class=\"callout-icon\">⚠️</strong><div class=\"callout-body\"><strong>SAFe est controversé</strong>Certains puristes Agile soutiennent que SAFe est du « Cascade avec des étiquettes Agile » en raison de sa planification descendante et de ses limites de PI fixes. Évaluez si votre organisation a vraiment besoin de ce niveau de structure avant de l'adopter.</div></div>"
    ].join("\n"),

    "mod-6-3": [
      "<h2>LeSS (Large-Scale Scrum)</h2>",
      "<p>LeSS (prononcé « less ») est un <strong>cadre de mise à l'échelle minimaliste</strong> construit au-dessus de Scrum standard. Créé par Craig Larman et Bas Vodde, LeSS applique les principes Scrum à plusieurs équipes travaillant sur le même produit, en ajoutant le moins de processus supplémentaire possible.</p>",

      "<h2>Principes LeSS</h2>",
      "<ul>",
      "<li><strong>Plus avec moins</strong> — Commencer par Scrum standard et n'ajouter que ce qui est absolument nécessaire pour la coordination.</li>",
      "<li><strong>Focus sur le produit complet</strong> — Toutes les équipes travaillent à partir d'un seul Backlog du produit avec un seul Product Owner.</li>",
      "<li><strong>Un Sprint, un produit</strong> — Toutes les équipes se synchronisent sur la même cadence de Sprint.</li>",
      "<li><strong>Coordination inter-équipes</strong> — Les équipes se coordonnent directement plutôt que par l'intermédiaire d'un seul chef de projet.</li>",
      "</ul>",

      "<h2>LeSS vs. SAFe</h2>",
      "<p>LeSS est fondamentalement différent de SAFe. Là où SAFe ajoute des couches de rôles et d'événements, LeSS les supprime. LeSS conserve les trois rôles Scrum (PO, SM, Développeurs) mais met les événements à l'échelle — par exemple, la Planification du Sprint implique toutes les équipes ensemble, puis se divise en sessions de groupe au niveau de l'équipe.</p>",

      "<div class=\"callout tip\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Choisissez sagement</strong>LeSS fonctionne bien quand toutes les équipes travaillent sur le même produit. SAFe peut être préférable lorsque vous devez coordonner plusieurs produits connexes ou inclure des fonctions non liées au développement (RH, finances, marketing) dans la transformation Agile.</div></div>"
    ].join("\n"),

    "mod-6-4": [
      "<h2>Quand passer à l'échelle</h2>",
      "<p>De nombreuses organisations se précipitent pour mettre Agile à l'échelle avant de le comprendre. La première question devrait toujours être : <strong>avez-vous réellement besoin de passer à l'échelle?</strong></p>",

      "<h2>Signes que vous pourriez avoir besoin de passer à l'échelle</h2>",
      "<ul>",
      "<li>Votre produit nécessite plus de 9 personnes pour être livré (la taille maximale d'une équipe Scrum)</li>",
      "<li>Vous avez plusieurs équipes Scrum travaillant sur la même base de code</li>",
      "<li>Les dépendances inter-équipes causent des retards fréquents</li>",
      "<li>Les frais de communication consomment un temps important</li>",
      "</ul>",

      "<h2>Signes que vous ne devriez PAS encore passer à l'échelle</h2>",
      "<ul>",
      "<li>Votre équipe unique apprend encore les bases de Scrum</li>",
      "<li>Vous n'avez pas encore atteint une Définition de Fini stable</li>",
      "<li>Vos Revues de Sprint et Rétrospectives ne produisent pas de résultats exploitables</li>",
      "<li>La direction utilise encore un style de commandement et contrôle</li>",
      "</ul>",

      "<h2>Passer à l'échelle de façon incrémentale</h2>",
      "<p>Quand vous devez passer à l'échelle, faites-le de façon incrémentale. Commencez par Scrum of Scrums. Si ce n'est pas suffisant, explorez LeSS ou Nexus avant de passer à SAFe. La solution la plus simple qui fonctionne est la bonne.</p>",

      "<div class=\"callout warn\"><strong class=\"callout-icon\">⚠️</strong><div class=\"callout-body\"><strong>Loi de Conway</strong>'Les organisations conçoivent des systèmes qui reflètent leur structure de communication.' Si votre approche Agile à grande échelle nécessite des mécanismes de coordination complexes, demandez-vous si des changements de structure d'équipe pourraient résoudre le problème plus directement.</div></div>"
    ].join("\n"),

    // ── MODULE 7: Agile Metrics and Monitoring Progress (Métriques Agile et suivi des progrès) ──
    "mod-7-1": [
      "<h2>Vélocité</h2>",
      "<p>La vélocité est une mesure de la quantité de travail qu'une équipe <strong>termine</strong> dans un Sprint, généralement exprimée en story points. C'est la métrique Agile la plus couramment suivie — et l'une des plus souvent utilisées à mauvais escient.</p>",

      "<h2>Comment mesurer la vélocité</h2>",
      "<p>À la fin de chaque Sprint, additionnez les story points de tous les éléments terminés (Finis) du Backlog du produit. Suivez cela sur 3 à 5 Sprints pour trouver une moyenne stable. Utilisez cette moyenne pour les prévisions de planification de Sprint — pas comme objectif de performance.</p>",

      "<h2>Utilisations abusives courantes</h2>",
      "<ul>",
      "<li><strong>Utiliser la vélocité pour comparer les équipes</strong> — Les story points sont spécifiques à chaque équipe. Comparer les vélocités entre équipes est insensé et destructeur.</li>",
      "<li><strong>Fixer des objectifs de vélocité</strong> — « Vous avez livré 30 points le Sprint dernier, vous devez donc livrer au moins 30 ce Sprint. » Cela encourage l'inflation et la tricherie.</li>",
      "<li><strong>Lier la vélocité aux évaluations de performance</strong> — Cela garantit que la métrique sera truquée et que la confiance sera brisée.</li>",
      "</ul>",

      "<div class=\"callout warn\"><strong class=\"callout-icon\">⚠️</strong><div class=\"callout-body\"><strong>La vélocité est un outil de prévision</strong>La vélocité existe pour aider l'équipe à planifier, pas pour juger la productivité. Une équipe qui livre une vélocité constante est prévisible — et la prévisibilité est l'objectif.</div></div>"
    ].join("\n"),

    "mod-7-2": [
      "<h2>Graphiques d'avancement (Burndown / Burnup)</h2>",
      "<p>Les graphiques d'avancement sont des <strong>outils visuels de suivi des progrès</strong> utilisés pendant un Sprint. Ils montrent le travail restant (burndown) ou le travail terminé (burnup) au fil du temps.</p>",

      "<h2>Graphique Burndown</h2>",
      "<p>Un graphique burndown a le <strong>temps sur l'axe X</strong> et <strong>l'effort restant sur l'axe Y</strong> (en story points ou en heures). La ligne de tendance idéale descend du coin supérieur gauche au coin inférieur droit, atteignant zéro à la fin du Sprint. La ligne réelle montre les progrès réels de l'équipe. Si la ligne réelle est au-dessus de la ligne idéale, l'équipe est en retard.</p>",

      SVG_BURNDOWN,

      "<h2>Graphique Burnup</h2>",
      "<p>Un graphique burnup a <strong>deux lignes</strong> : le travail total (qui peut augmenter si du périmètre est ajouté) et le travail terminé. Quand les deux lignes se rencontrent, l'Objectif du Sprint est atteint. Les graphiques burnup sont souvent préférés car ils représentent visuellement les changements de périmètre.</p>",

      "<h2>Que rechercher</h2>",
      "<ul>",
      "<li><strong>Un burndown plat</strong> — L'équipe ne progresse pas. Enquêter sur les bloqueurs.</li>",
      "<li><strong>Un pic en milieu de Sprint</strong> — Du nouveau travail a été ajouté. Cela devrait être rare dans Scrum.</li>",
      "<li><strong>Une chute brusque vers la fin</strong> — Le travail a été terminé en lot plutôt que de façon incrémentale. Cela risque des problèmes de qualité.</li>",
      "</ul>"
    ].join("\n"),

    "mod-7-3": [
      "<h2>Temps de cycle et délai d'exécution</h2>",
      "<p>Ces métriques d'origine Kanban mesurent le <strong>temps nécessaire pour que le travail circule dans le système</strong>.</p>",

      "<h2>Définitions</h2>",
      "<ul>",
      "<li><strong>Délai d'exécution (Lead Time)</strong> — Le temps total entre le moment où une demande est faite (ajoutée au backlog) et le moment où elle est livrée (acceptée comme Fini).</li>",
      "<li><strong>Temps de cycle (Cycle Time)</strong> — Le temps à partir du moment où le travail commence réellement sur un élément jusqu'à son achèvement. Cela exclut le temps passé à attendre dans le backlog.</li>",
      "</ul>",

      "<h2>Pourquoi ces métriques sont importantes</h2>",
      "<p>Le délai d'exécution mesure <strong>l'expérience du client</strong> (combien de temps il attend pour une fonctionnalité), tandis que le temps de cycle mesure <strong>l'efficacité de l'équipe</strong> (combien de temps il faut pour faire le travail). Réduire les deux est généralement un bon objectif, mais concentrez-vous d'abord sur le temps de cycle — vous ne pouvez pas contrôler combien de temps les éléments restent dans le backlog sans changements de processus.</p>",

      "<h2>Loi de Little</h2>",
      "<p>La Loi de Little stipule : <strong>Temps de cycle = WIP / Débit</strong>. Pour réduire le temps de cycle, soit réduisez le WIP (travail en cours), soit augmentez le débit. Comme le débit est difficile à augmenter, la réduction du WIP est généralement le levier le plus efficace.</p>",

      "<div class=\"callout tip\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Prévisibilité</strong>Une fois que vous avez des données stables sur le délai d'exécution, vous pouvez faire des promesses de livraison fiables aux parties prenantes : « Les fonctionnalités de cette taille nous prennent généralement 2 à 3 semaines de la demande à la livraison. »</div></div>"
    ].join("\n"),

    "mod-7-4": [
      "<h2>Diagrammes de flux cumulés</h2>",
      "<p>Un Diagramme de flux cumulés (CFD) est un <strong>graphique visuel</strong> montrant la quantité de travail dans chaque état du flux de travail (À faire, En cours, Terminé) au fil du temps. Il fournit une vue d'ensemble de la santé du flux de travail de l'équipe.</p>",

      "<h2>Lire un CFD</h2>",
      "<ul>",
      "<li>L'axe X montre le temps; l'axe Y montre le nombre d'éléments de travail.</li>",
      "<li>Les bandes colorées représentent chaque état du flux de travail.</li>",
      "<li>La <strong>largeur de chaque bande</strong> indique le WIP dans cet état à un moment donné.</li>",
      "<li>La <strong>pente de la bande supérieure</strong> montre le débit global.</li>",
      "</ul>",

      "<h2>Que rechercher</h2>",
      "<ul>",
      "<li><strong>Des bandes qui s'élargissent</strong> — Le WIP augmente dans un état, indiquant un goulot d'étranglement. Par exemple, si « En test » s'élargit constamment, les tests sont le facteur limitant.</li>",
      "<li><strong>Des pentes plates</strong> — Aucun travail n'est terminé. Le processus est peut-être bloqué.</li>",
      "<li><strong>Des bandes régulières et parallèles</strong> — Un flux sain et prévisible. Le travail circule bien dans le système.</li>",
      "</ul>",

      "<div class=\"callout good\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Les CFD pour les rétrospectives</strong>Les Diagrammes de flux cumulés sont d'excellents outils pour les Rétrospectives de Sprint. Ils fournissent des données objectives pour étayer les discussions sur les goulots d'étranglement du processus, l'efficacité du flux et les expériences d'amélioration.</div></div>"
    ].join("\n"),

    // ── MODULE 8: Advanced Topics in Agile (Sujets avancés en Agile) ──
    "mod-8-1": [
      "<h2>Contrats Agile et gouvernance</h2>",
      "<p>Les contrats traditionnels à prix fixe et périmètre fixe sont <strong>fondamentalement en conflit avec Agile</strong> car ils supposent que les exigences peuvent être entièrement définies à l'avance. Les contrats Agile sont conçus pour aligner les incitatifs sur la livraison de valeur, pas sur la conformité au périmètre.</p>",

      "<h2>Modèles de contrats Agile</h2>",
      "<ul>",
      "<li><strong>Temps et matériel</strong> — Le client paie pour le temps et le matériel réels. Haute confiance, périmètre flexible, mais risqué pour le client sans supervision.</li>",
      "<li><strong>Prix fixe + itératif</strong> — Prix fixe pour une boîte de temps fixe (p. ex., Sprint de 2 semaines), avec un périmètre variable. Le client sélectionne le travail de plus grande valeur chaque Sprint.</li>",
      "<li><strong>Argent pour rien, changement gratuit</strong> — Le client peut annuler tôt (en payant des frais de résiliation) ou ajouter du périmètre sans pénalité. Le fournisseur gagne une marge plus élevée pour une livraison anticipée.</li>",
      "<li><strong>Basé sur les résultats</strong> — Le paiement est lié aux résultats d'affaires (p. ex., augmentation de 10% du taux de conversion) plutôt qu'aux extrants. Nécessite une confiance solide et une capacité de mesure.</li>",
      "</ul>",

      "<h2>Gouvernance en Agile</h2>",
      "<p>La gouvernance Agile passe de <strong>la conformité aux processus</strong> à <strong>l'assurance de la valeur</strong>. Au lieu de vérifier si l'équipe a suivi un plan, la gouvernance demande : Construisons-nous la bonne chose? Le construisons-nous bien? Comment le savons-nous? Les Revues de Sprint régulières et les Backlogs transparents deviennent le principal mécanisme de gouvernance.</p>"
    ].join("\n"),

    "mod-8-2": [
      "<h2>Équipes distribuées en Agile</h2>",
      "<p>Agile a été conçu à l'origine pour des <strong>équipes co-localisées</strong>, mais le développement logiciel moderne est de plus en plus distribué. Les années 2020 ont montré qu'Agile peut fonctionner à distance — mais cela nécessite une adaptation délibérée.</p>",

      "<h2>Défis</h2>",
      "<ul>",
      "<li><strong>Décalage de communication</strong> — La communication textuelle manque de la bande passante de la conversation en face à face (Principe #6 : « La méthode la plus efficace est la conversation en face à face »).</li>",
      "<li><strong>Différences de fuseaux horaires</strong> — Les heures de chevauchement limitées compriment les fenêtres de collaboration.</li>",
      "<li><strong>Confiance et visibilité</strong> — Les équipes à distance luttent contre la dynamique « loin des yeux, loin du cœur ».</li>",
      "<li><strong>Communication informelle</strong> — Les discussions autour de la fontaine à eau et les décisions de corridor ne se produisent pas naturellement.</li>",
      "</ul>",

      "<h2>Pratiques pour les équipes à distance</h2>",
      "<ul>",
      "<li><strong>Surcommuniquer</strong> — Écrire les décisions. Enregistrer les mêlées. Tenir un journal des décisions.</li>",
      "<li><strong>Utiliser la vidéo pour les cérémonies</strong> — La Planification du Sprint, la Revue et la Rétrospective devraient toutes être des appels vidéo, pas seulement audio.</li>",
      "<li><strong>Créer des boucles de rétroaction asynchrones</strong> — Vidéos Loom, documents de conception écrits et tableaux partagés.</li>",
      "<li><strong>Chevauchement de fuseaux horaires</strong> — Établir une fenêtre de collaboration centrale (minimum 4 heures) où toute l'équipe est disponible.</li>",
      "<li><strong>Temps social virtuel</strong> — Planifier du temps non professionnel pour les liens d'équipe (clavardages-café, jeux, séances de show-and-tell).</li>",
      "</ul>",

      "<div class=\"callout tip\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>À distance ≠ Asynchrone</strong>Prioriser le télétravail ne signifie pas asynchrone seulement. La communication synchrone (appels vidéo, programmation en binôme) reste essentielle pour les discussions complexes et la collaboration.</div></div>"
    ].join("\n"),

    "mod-8-3": [
      "<h2>Agile dans des contextes non logiciels</h2>",
      "<p>Bien qu'Agile soit né dans le développement logiciel, ses principes ont été appliqués avec succès au <strong>marketing, aux RH, à l'éducation, aux soins de santé et même à la construction</strong>. Les idées fondamentales — progrès itératif, orientation client, collaboration — sont indépendantes du domaine.</p>",

      "<h2>Exemples</h2>",
      "<ul>",
      "<li><strong>Équipes marketing</strong> — Utiliser des Sprints pour planifier et exécuter des campagnes, avec des Mêlées quotidiennes pour se coordonner et des Revues de Sprint pour analyser la performance des campagnes.</li>",
      "<li><strong>Services RH</strong> — Appliquer Kanban aux pipelines de recrutement, visualiser les étapes des candidats et limiter le WIP pour réduire le délai d'embauche.</li>",
      "<li><strong>Conception de programmes éducatifs</strong> — Développer itérativement le contenu des cours avec des cycles fréquents de rétroaction des étudiants agissant comme « Revues de Sprint ».</li>",
      "<li><strong>Développement matériel</strong> — Tesla et SpaceX utilisent le développement itératif pour le matériel, avec des cycles de prototypage rapide qui reflètent les sprints Agile.</li>",
      "</ul>",

      "<h2>Adapter les cérémonies</h2>",
      "<p>Lors de l'application d'Agile en dehors du logiciel, adaptez les cérémonies au domaine. La « Revue de Sprint » d'une équipe marketing pourrait être une analyse de performance de campagne. La « Mêlée quotidienne » d'une équipe RH pourrait être une brève réunion debout axée sur l'état du pipeline de recrutement. Préservez l'intention (inspecter et adapter) plutôt que la forme spécifique au logiciel.</p>"
    ].join("\n"),

    "mod-8-4": [
      "<h2>DevOps et Agile</h2>",
      "<p>DevOps n'est pas une méthodologie distincte — c'est une <strong>extension naturelle des principes Agile</strong> dans les opérations et l'infrastructure. Là où Agile a abattu le mur entre les affaires et le développement, DevOps abat le mur entre le développement et les opérations.</p>",

      "<h2>Les trois voies de DevOps</h2>",
      "<ol>",
      "<li><strong>Flux</strong> — Optimiser le flux de travail du développement aux opérations jusqu'au client. Cela signifie de petits lots, la réduction des transferts et l'automatisation du pipeline de déploiement.</li>",
      "<li><strong>Rétroaction</strong> — Créer des boucles de rétroaction courtes pour que les problèmes opérationnels soient détectés et corrigés immédiatement. La surveillance, les alertes et la réponse aux incidents sont des préoccupations de premier ordre.</li>",
      "<li><strong>Apprentissage continu</strong> — Favoriser une culture d'expérimentation et d'apprentissage. Les post-mortems sans blâme, l'ingénierie du chaos et les rétrospectives régulières stimulent l'amélioration.</li>",
      "</ol>",

      "<h2>Comment DevOps soutient Agile</h2>",
      "<ul>",
      "<li><strong>Livraison plus rapide</strong> — Les pipelines CI/CD permettent plusieurs déploiements par jour, en accord avec le principe Agile de livraison fréquente.</li>",
      "<li><strong>Risque réduit</strong> — Les tests et déploiements automatisés rendent chaque livraison plus sûre et moins stressante.</li>",
      "<li><strong>Propriété partagée</strong> — Les développeurs sont responsables de leur code en production : « vous le construisez, vous l'exploitez. »</li>",
      "<li><strong>Infrastructure as Code</strong> — Traiter l'infrastructure comme un logiciel (versionné, testé, automatisé) permet d'appliquer les principes Agile au domaine des opérations.</li>",
      "</ul>",

      "<div class=\"callout good\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>DevOps est aussi une culture</strong>Comme Agile, DevOps est avant tout un mouvement culturel. Les outils (Docker, Kubernetes, Jenkins) soutiennent la culture, pas l'inverse.</div></div>"
    ].join("\n"),

    // ── MODULE 9: Case Studies and Practical Application (Études de cas et application pratique) ──
    "mod-9-1": [
      "<h2>Simulation de Sprint Scrum de bout en bout</h2>",
      "<p>Cet exercice vous guide à travers un <strong>cycle complet de Sprint Scrum</strong> du point de vue d'un développeur dans une équipe Scrum. Vous pouvez réaliser cette simulation avec votre équipe ou comme exercice de réflexion guidé.</p>",

      "<h2>Scénario</h2>",
      "<p>Vous êtes développeur dans une équipe de 5 personnes construisant un système de paiement pour un site de commerce électronique. Votre Product Owner a défini l'Objectif du Sprint : « Permettre aux clients d'effectuer un achat en utilisant une carte de crédit enregistrée. » La durée du Sprint est de 2 semaines.</p>",

      "<h2>Phase 1 : Planification du Sprint (2 heures)</h2>",
      "<p>Révisez le Backlog du produit avec le PO. Les principaux éléments sont : (1) Interface utilisateur de paiement enregistré, (2) Intégration API de tokenisation de carte, (3) Flux de paiement « Utiliser une carte enregistrée », (4) Écran de confirmation de paiement. L'équipe estime et sélectionne les éléments. <strong>Votre tâche :</strong> Rédigez un Backlog du Sprint avec une répartition des tâches pour les deux premiers éléments.</p>",

      "<h2>Phase 2 : Exécution du Sprint (10 jours)</h2>",
      "<p>Chaque jour commence par la Mêlée quotidienne. Vous identifiez un bloqueur : le bac à sable de la passerelle de paiement est hors service. <strong>Votre tâche :</strong> Rédigez comment vous soulèveriez cet obstacle et décrivez ce que le Scrum Master devrait faire ensuite.</p>",

      "<h2>Phase 3 : Revue du Sprint (1 heure)</h2>",
      "<p>Vous démontrez le flux de paiement enregistré. Une partie prenante demande si cela peut aussi prendre en charge PayPal. <strong>Votre tâche :</strong> Décrivez comment le PO devrait gérer cette nouvelle demande — devrait-elle aller dans le Sprint en cours?</p>",

      "<h2>Phase 4 : Rétrospective du Sprint (45 min)</h2>",
      "<p>L'équipe discute de ce qui a bien fonctionné (bonne collaboration) et de ce qui n'a pas fonctionné (des tâches de soutien imprévues ont perturbé la concentration). <strong>Votre tâche :</strong> Proposez deux expériences d'amélioration réalisables pour le prochain Sprint.</p>",

      "<div class=\"callout tip\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Essayez-le avec votre équipe</strong>Réalisez cette simulation dans un atelier de 2 heures. Assignez des rôles (PO, SM, Développeurs) et travaillez à travers chaque phase. C'est un excellent exercice d'intégration pour les nouveaux membres de l'équipe.</div></div>"
    ].join("\n"),

    "mod-9-2": [
      "<h2>Exercice de rétrospective de Sprint</h2>",
      "<p>Ceci est un format de rétrospective structuré que vous pouvez utiliser avec votre équipe. Contrairement au standard « ce qui a bien fonctionné / ce qui n'a pas fonctionné », cet exercice utilise le format <strong>Commencer / Arrêter / Continuer</strong> avec un accent sur la génération d'éléments d'action concrets.</p>",

      "<h2>Instructions</h2>",
      "<ol>",
      "<li><strong>Préparer le terrain (5 min)</strong> — L'animateur explique le format et rappelle à tous les règles de base de la rétrospective : sans blâme, constructive, axée sur l'amélioration.</li>",
      "<li><strong>Remue-méninges (15 min)</strong> — Chaque membre de l'équipe écrit des notes autocollantes dans trois catégories : Commencer à faire, Arrêter de faire, Continuer à faire. Une idée par note.</li>",
      "<li><strong>Regrouper et discuter (15 min)</strong> — L'équipe regroupe les idées similaires et discute des plus impactantes. L'animateur guide la conversation pour faire remonter les causes profondes.</li>",
      "<li><strong>Voter et s'engager (10 min)</strong> — Chaque membre de l'équipe vote pour les 1 à 2 améliorations les plus importantes. L'équipe s'engage à mettre en œuvre les éléments les plus votés dans le prochain Sprint.</li>",
      "<li><strong>Définir les éléments d'action (5 min)</strong> — Pour chaque amélioration convenue, précisez : Qu'allons-nous faire? Qui est la personne responsable? Quand allons-nous vérifier les progrès?</li>",
      "</ol>",

      "<h2>Exemples d'éléments d'action</h2>",
      "<ul>",
      "<li>« Ajouter un tampon de 15 minutes à notre Mêlée quotidienne pour la coordination inter-équipes » (Responsable : SM, Vérification : prochaine Rétro)</li>",
      "<li>« Arrêter d'assigner des tâches individuelles — laisser les membres de l'équipe s'auto-sélectionner à partir du Backlog du Sprint » (Responsable : Équipe, Vérification : 1 semaine)</li>",
      "<li>« Continuer la programmation en binôme sur les fonctionnalités complexes, mais limiter à 2 heures par session » (Responsable : Équipe, Vérification : prochaine Rétro)</li>",
      "</ul>",

      "<div class=\"callout good\"><strong class=\"callout-icon\">💡</strong><div class=\"callout-body\"><strong>Assurer le suivi</strong>La Rétrospective n'est utile que si l'équipe assure le suivi de ses éléments d'action. Commencez votre prochaine Rétrospective en examinant l'état des engagements du Sprint précédent.</div></div>"
    ].join("\n"),

    "mod-9-3": [
      "<h2>Atelier de raffinement du Backlog</h2>",
      "<p>Le Raffinement du Backlog (aussi appelé lissage du Backlog) est le processus qui consiste à <strong>maintenir le Backlog du produit en santé</strong> — ajouter des détails, des estimations et de l'ordre aux éléments. Cet atelier vous donne une approche structurée pour mener des sessions de raffinement.</p>",

      "<h2>Pourquoi raffiner?</h2>",
      "<p>Un Backlog bien raffiné garantit que la Planification du Sprint est efficace et productive. Sans raffinement, la Planification du Sprint devient une session de découverte où l'équipe essaie de comprendre les exigences pour la première fois — gaspillant un temps de planification précieux.</p>",

      "<h2>Structure de l'atelier (60 min, hebdomadaire)</h2>",
      "<ol>",
      "<li><strong>Examiner les nouveaux éléments (10 min)</strong> — Le PO présente les nouveaux éléments ajoutés depuis la dernière session. L'équipe pose des questions de clarification.</li>",
      "<li><strong>Détailler les éléments prioritaires (30 min)</strong> — Travailler sur les éléments les plus prioritaires qui ne sont pas encore raffinés. Ajouter des critères d'acceptation, discuter des cas limites et identifier les dépendances.</li>",
      "<li><strong>Estimer (15 min)</strong> — Utiliser le Poker de planification ou le dimensionnement par taille de T-shirt pour estimer les éléments. Le PO observe mais ne participe pas à l'estimation.</li>",
      "<li><strong>Réordonner (5 min)</strong> — Sur la base des nouvelles informations, le PO ajuste l'ordre du backlog. L'équipe confirme qu'elle peut s'engager sur les éléments prioritaires lors de la prochaine Planification du Sprint.</li>",
      "</ol>",

      "<h2>Conseils pour un raffinement efficace</h2>",
      "<ul>",
      "<li>Limiter les sessions de raffinement à 60 minutes — les sessions plus longues perdent leur concentration.</li>",
      "<li>Inviter toute l'Équipe Scrum (PO, SM, Développeurs). Les parties prenantes peuvent se joindre si nécessaire.</li>",
      "<li>Utiliser la Définition de Prêt comme liste de vérification pour chaque élément.</li>",
      "<li>Diviser les grands éléments (épopées) en morceaux plus petits adaptés à un Sprint.</li>",
      "<li>Éviter de trop raffiner les éléments loin dans le backlog — les détails deviennent obsolètes.</li>",
      "</ul>",

      "<div class=\"callout warn\"><strong class=\"callout-icon\">⚠️</strong><div class=\"callout-body\"><strong>Le raffinement est du travail</strong>Le Guide Scrum recommande de consacrer jusqu'à 10% de la capacité du Sprint au Raffinement du Backlog. Ce n'est pas une surcharge facultative — c'est un investissement dans des Sprints plus fluides.</div></div>"
    ].join("\n"),

    "final-exam": [
      "<h2>Examen final</h2>",
      "<p>Cet examen complet couvre tous les modules du cours Agile & Scrum pour Développeurs. Il comprend <strong>20 questions</strong> tirées de l'ensemble du programme, testant à la fois vos connaissances des concepts et votre capacité à les appliquer en pratique.</p>",

      "<h2>Règles de l'examen</h2>",
      "<ul>",
      "<li>Vous devez obtenir une note de <strong>80% ou plus</strong> pour réussir et obtenir votre certificat.</li>",
      "<li>Vous pouvez repasser l'examen si vous ne réussissez pas du premier coup.</li>",
      "<li>Les questions sont tirées aléatoirement d'une banque couvrant les 9 modules.</li>",
      "<li>Il n'y a pas de limite de temps, mais prévoyez environ 30 minutes.</li>",
      "</ul>",

      "<p><em>Les questions de l'examen final seront tirées des quiz des modules ci-dessus. Commencez par compléter tous les quiz des modules, puis revenez ici pour l'évaluation complète.</em></p>"
    ].join("\n"),
  },

  "qa-onboarding-advanced": {

    "mod-1-1": [
      '<h1>Workflows D365 concrets</h1>',
      '<p class="chapter-intro">Dynamics 365 n\u2019est pas qu\u2019un formulaire avec des champs. C\u2019est une machine d\u2019\u00e9tat pilot\u00e9e par des flux de processus d\u2019affaires, des workflows et des plug-ins. Comprendre ces m\u00e9canismes est ce qui distingue les testeurs interm\u00e9diaires des testeurs avanc\u00e9s.</p>',
      '<h2>Flux de processus d\u2019affaires (BPF)</h2>',
      '<p>Un BPF guide les utilisateurs \u00e0 travers une s\u00e9quence d\u2019\u00e9tapes. Chaque \u00e9tape comporte des champs obligatoires qui doivent \u00eatre remplis avant de passer \u00e0 la suivante. En tant que testeur, vous devez v\u00e9rifier :</p>',
      '<ul>',
      '<li>Chaque \u00e9tape impose ses champs obligatoires avant de permettre l\u2019avancement</li>',
      '<li>La navigation arri\u00e8re ne permet pas de sauter des \u00e9tapes obligatoires</li>',
      '<li>Les branchements conditionnels (si le r\u00e9sultat de l\u2019\u00e9tape A = X, aller \u00e0 l\u2019\u00e9tape C au lieu de B)</li>',
      '<li>Le BPF s\u2019affiche correctement pour chaque r\u00f4le (certains BPF sont sp\u00e9cifiques \u00e0 un r\u00f4le)</li>',
      '</ul>',
      '<h2>D\u00e9clencheurs de workflows et plug-ins</h2>',
      '<p>Les workflows D365 s\u2019ex\u00e9cutent en arri\u00e8re-plan lors de la cr\u00e9ation, la modification ou la suppression d\u2019un enregistrement. Un workflow peut attribuer automatiquement un dossier en fonction de sa cat\u00e9gorie, ou envoyer un courriel lorsqu\u2019un dossier est escalad\u00e9. Les plug-ins sont du code .NET personnalis\u00e9 qui s\u2019ex\u00e9cute de fa\u00e7on synchrone pendant une transaction.</p>',
      '<p>L\u2019aper\u00e7u critique pour les tests : <strong>un test uniquement dans l\u2019interface utilisateur est incomplet.</strong> Un champ peut sembler se sauvegarder correctement, mais le workflow ou le plug-in qui se d\u00e9clenche lors de la sauvegarde pourrait \u00e9chouer silencieusement. Vous devez v\u00e9rifier les effets en aval :</p>',
      '<ul>',
      '<li>Le courriel a-t-il vraiment \u00e9t\u00e9 envoy\u00e9? V\u00e9rifiez la chronologie des courriels.</li>',
      '<li>L\u2019attribution automatique a-t-elle eu lieu? V\u00e9rifiez le champ Propri\u00e9taire apr\u00e8s la sauvegarde.</li>',
      '<li>La mise \u00e0 jour du statut s\u2019est-elle propag\u00e9e aux enregistrements li\u00e9s? Ouvrez l\u2019entit\u00e9 connexe.</li>',
      '</ul>',
      '<div class="callout warn"><strong>Pi\u00e8ge courant :</strong> Un plug-in lance une exception pour une combinaison de donn\u00e9es sp\u00e9cifique. L\u2019interface indique \u00ab Sauvegard\u00e9 avec succ\u00e8s \u00bb mais l\u2019enregistrement sous-jacent est dans un \u00e9tat incoh\u00e9rent. V\u00e9rifiez toujours le r\u00e9sultat, pas seulement le message de confirmation.</div>',
      '<h2>Tester les workflows multi-entit\u00e9s</h2>',
      '<p>Plusieurs processus D365 traversent plusieurs entit\u00e9s. Un dossier cr\u00e9e un compte, qui cr\u00e9e un contact, qui met en file d\u2019attente une t\u00e2che. Chaque \u00e9tape est un point de d\u00e9faillance potentiel. Cartographiez la cha\u00eene compl\u00e8te avant de commencer les tests.</p>',
      '<div class="callout tip"><strong>Technique avanc\u00e9e :</strong> Conservez un diagramme de d\u00e9pendance des workflows pour les fonctionnalit\u00e9s que vous testez. Lorsqu\u2019une nouvelle version est d\u00e9ploy\u00e9e, v\u00e9rifiez la liste des workflows/plug-ins pour les changements avant de commencer \u00e0 cliquer.</div>',
    ].join("\n"),

    "mod-1-2": [
      '<h1>Cas limites dans D365</h1>',
      '<p class="chapter-intro">Les tests par le chemin heureux standard attrapent les bogues \u00e9vidents. Les tests de cas limites attrapent les \u00e9checs de codage d\u00e9fensif, les erreurs de configuration des autorisations et les risques de corruption de donn\u00e9es.</p>',
      '<h2>Cas limites au niveau des champs</h2>',
      '<table style="width:100%; border-collapse:collapse; margin:var(--space-5) 0; font-size:var(--text-sm);">',
      '<thead style="background:var(--color-bg);"><tr><th style="text-align:left; padding:var(--space-3); border:1px solid var(--color-border);">Type de champ</th><th style="text-align:left; padding:var(--space-3); border:1px solid var(--color-border);">Cas limites \u00e0 tester</th></tr></thead>',
      '<tbody>',
      '<tr><td style="padding:var(--space-3); border:1px solid var(--color-border);">Texte (une ligne)</td><td style="padding:var(--space-3); border:1px solid var(--color-border);">Longueur maximale, caract\u00e8res Unicode, espaces de d\u00e9but/fin, injection HTML, motifs d\u2019injection SQL</td></tr>',
      '<tr><td style="padding:var(--space-3); border:1px solid var(--color-border);">Texte (plusieurs lignes)</td><td style="padding:var(--space-3); border:1px solid var(--color-border);">Sauts de ligne, contenu tr\u00e8s long coll\u00e9 (10k+ caract\u00e8res), copier-coller depuis Word avec mise en forme</td></tr>',
      '<tr><td style="padding:var(--space-3); border:1px solid var(--color-border);">Nombre/Monnaie</td><td style="padding:var(--space-3); border:1px solid var(--color-border);">Valeurs n\u00e9gatives, z\u00e9ro, pr\u00e9cision d\u00e9cimale, tr\u00e8s grands nombres, virgules dans la saisie</td></tr>',
      '<tr><td style="padding:var(--space-3); border:1px solid var(--color-border);">Date/Heure</td><td style="padding:var(--space-3); border:1px solid var(--color-border);">29 f\u00e9vrier les ann\u00e9es non bissextiles, transitions de fuseau horaire, dates avant 1970, ann\u00e9e 9999</td></tr>',
      '<tr><td style="padding:var(--space-3); border:1px solid var(--color-border);">Recherche (lookup)</td><td style="padding:var(--space-3); border:1px solid var(--color-border);">Enregistrement d\u00e9sactiv\u00e9 comme cible de recherche, r\u00e9f\u00e9rences circulaires, auto-r\u00e9f\u00e9rences</td></tr>',
      '<tr><td style="padding:var(--space-3); border:1px solid var(--color-border);">Option Set</td><td style="padding:var(--space-3); border:1px solid var(--color-border);">Valeur par d\u00e9faut (y en a-t-il une?), s\u00e9lection nulle, options d\u00e9pr\u00e9ci\u00e9es encore visibles</td></tr>',
      '</tbody>',
      '</table>',
      '<h2>Tests de limites d\u2019autorisations</h2>',
      '<p>La s\u00e9curit\u00e9 de D365 est bas\u00e9e sur les r\u00f4les, les enregistrements et les champs. En tant que testeur avanc\u00e9, vous devez tester au-del\u00e0 des limites d\u2019autorisations :</p>',
      '<ul>',
      '<li>Un enqu\u00eateur junior peut-il voir ou modifier des champs marqu\u00e9s comme r\u00e9serv\u00e9s aux seniors? (V\u00e9rifiez le DOM, pas seulement l\u2019\u00e9tat d\u00e9sactiv\u00e9)</li>',
      '<li>Que se passe-t-il lorsque le r\u00f4le du propri\u00e9taire d\u2019un enregistrement est modifi\u00e9 en cours de workflow?</li>',
      '<li>Le partage d\u2019un enregistrement accorde-t-il correctement un acc\u00e8s en lecture seule ou en lecture-\u00e9criture?</li>',
      '<li>Un utilisateur peut-il acc\u00e9der \u00e0 un enregistrement d\u00e9sactiv\u00e9 via une recherche d\u2019entit\u00e9 connexe?</li>',
      '</ul>',
      '<div class="callout good"><strong>Conseil pratique :</strong> Cr\u00e9ez des comptes de test pour chaque r\u00f4le et testez chaque sc\u00e9nario du point de vue de chaque r\u00f4le. Ne testez pas tout en tant qu\u2019administrateur syst\u00e8me en pr\u00e9sumant que cela fonctionne pour les utilisateurs finaux.</div>',
    ].join("\n"),

    "mod-1-3": [
      '<h1>Strat\u00e9gies de pr\u00e9paration des donn\u00e9es de test</h1>',
      '<p class="chapter-intro">Un test n\u2019est aussi bon que les donn\u00e9es sur lesquelles il repose. De mauvaises donn\u00e9es de test entra\u00eenent de faux positifs, de faux n\u00e9gatifs et une perte de temps pour le d\u00e9bogage.</p>',
      '<h2>Le probl\u00e8me avec les donn\u00e9es de production</h2>',
      '<p>Copier des donn\u00e9es de production dans un environnement de test semble efficace, mais cela pr\u00e9sente des risques : exposition de renseignements personnels, r\u00e9f\u00e9rences orphelines et volumes de donn\u00e9es qui masquent les probl\u00e8mes de performance. Les environnements de test n\u00e9cessitent leurs propres ensembles de donn\u00e9es organis\u00e9s.</p>',
      '<h2>Mod\u00e8les de pr\u00e9paration des donn\u00e9es</h2>',
      '<h3>1. Ensemble de donn\u00e9es de base</h3>',
      '<p>Un ensemble minimal d\u2019enregistrements n\u00e9cessaires \u00e0 toute suite de tests : entit\u00e9s de r\u00e9f\u00e9rence (statuts, cat\u00e9gories), r\u00f4les de s\u00e9curit\u00e9, utilisateurs et au moins un de chaque entit\u00e9 principale (comptes, contacts, dossiers). Exportez cet ensemble comme un package de migration de donn\u00e9es et r\u00e9importez-le avant chaque cycle de test.</p>',
      '<h3>2. Donn\u00e9es sp\u00e9cifiques aux sc\u00e9narios</h3>',
      '<p>Chaque sc\u00e9nario de test n\u00e9cessite des donn\u00e9es cibl\u00e9es. Un test de \u00ab d\u00e9tection des doublons \u00bb a besoin d\u2019un enregistrement existant avec un nom correspondant. Un test de \u00ab cascade de workflow \u00bb n\u00e9cessite des relations parent-enfant d\u00e9j\u00e0 en place. Documentez ces conditions pr\u00e9alables dans votre cas de test.</p>',
      '<h3>3. Donn\u00e9es limites</h3>',
      '<p>Cr\u00e9ez des enregistrements \u00e0 chaque limite : longueurs minimales de champs, longueurs maximales, caract\u00e8res sp\u00e9ciaux, enregistrements avec tous les champs remplis, enregistrements avec seulement les champs obligatoires. Ces enregistrements deviendront vos donn\u00e9es de r\u00e9f\u00e9rence pour les tests de r\u00e9gression.</p>',
      '<div class="callout tip"><strong>Outillage :</strong> Apprenez les mod\u00e8les Excel pour l\u2019import de donn\u00e9es D365 et envisagez un mod\u00e8le de construction de donn\u00e9es (code de test qui cr\u00e9e ses propres donn\u00e9es) pour les suites automatis\u00e9es. Pour les tests manuels, maintenez un document partag\u00e9 \u00ab Configuration des donn\u00e9es de test \u00bb avec des instructions de cr\u00e9ation \u00e9tape par \u00e9tape.</div>',
    ].join("\n"),

    "mod-1-4": [
      '<h1>Tests d\u2019int\u00e9gration avec D365</h1>',
      '<p class="chapter-intro">D365 existe rarement en isolation. Il se connecte \u00e0 Power Automate, SharePoint, Outlook, des portails personnalis\u00e9s et des API tierces. Les tests d\u2019int\u00e9gration valident le bon fonctionnement de ces connexions de bout en bout.</p>',
      '<h2>Points d\u2019int\u00e9gration courants</h2>',
      '<ul>',
      '<li><strong>Flux Power Automate</strong> d\u00e9clench\u00e9s par des \u00e9v\u00e9nements D365 (cr\u00e9ation, modification, suppression)</li>',
      '<li><strong>Synchronisation c\u00f4t\u00e9 serveur</strong> entre D365 et Exchange (suivi des courriels, rendez-vous)</li>',
      '<li><strong>Gestion documentaire SharePoint</strong> \u2014 t\u00e9l\u00e9versements de documents, gestion des versions, cr\u00e9ation automatique de dossiers</li>',
      '<li><strong>Points de terminaison d\u2019API web personnalis\u00e9s</strong> exposant les donn\u00e9es D365 aux syst\u00e8mes externes</li>',
      '<li><strong>Rapports Power BI</strong> consommant les vues de donn\u00e9es D365</li>',
      '</ul>',
      '<h2>Strat\u00e9gie de test pour les int\u00e9grations</h2>',
      '<p>Les tests d\u2019int\u00e9gration suivent un mod\u00e8le diff\u00e9rent des tests UI. La question centrale est : <strong>qu\u2019est-ce qui se brise lorsque l\u2019int\u00e9gration \u00e9choue?</strong></p>',
      '<ul>',
      '<li>Si Power Automate est hors service, le formulaire D365 se sauvegarde-t-il quand m\u00eame? (Il le devrait.)</li>',
      '<li>Si le site SharePoint est inaccessible, le t\u00e9l\u00e9versement de document \u00e9choue-t-il gracieusement?</li>',
      '<li>Si une API externe retourne une charge utile inattendue, le travail de synchronisation enregistre-t-il l\u2019erreur ou \u00e9choue-t-il silencieusement?</li>',
      '</ul>',
      '<div class="callout warn"><strong>Principe cl\u00e9 :</strong> Une d\u00e9faillance d\u2019int\u00e9gration en aval ne doit jamais corrompre les donn\u00e9es en amont. D365 doit rester coh\u00e9rent m\u00eame lorsque les services connect\u00e9s sont indisponibles.</div>',
      '<h2>Tra\u00e7abilit\u00e9 entre les syst\u00e8mes</h2>',
      '<p>Lorsqu\u2019un bogue traverse plusieurs syst\u00e8mes, attribuez des identifiants de test ou des identifiants de corr\u00e9lation uniques pour pouvoir tracer la demande \u00e0 travers les fronti\u00e8res. Un dossier cr\u00e9\u00e9 dans D365 doit pouvoir \u00eatre retrouv\u00e9 dans l\u2019historique d\u2019ex\u00e9cution de Power Automate, dans l\u2019ensemble de documents SharePoint et dans les journaux de l\u2019API externe.</p>',
      '<div class="callout good"><strong>Liste de v\u00e9rification pour chaque int\u00e9gration :</strong> 1) Le chemin heureux fonctionne, 2) La d\u00e9faillance en aval ne brise pas le syst\u00e8me en amont, 3) L\u2019erreur est consign\u00e9e avec suffisamment de d\u00e9tails pour d\u00e9boguer, 4) Un m\u00e9canisme de nouvelle tentative existe pour les d\u00e9faillances transitoires, 5) Les donn\u00e9es sont coh\u00e9rentes dans tous les syst\u00e8mes apr\u00e8s la r\u00e9cup\u00e9ration.</div>',
    ].join("\n"),

    "mod-2-1": [
      '<h1>R\u00e9diger des rapports de bogue professionnels</h1>',
      '<p class="chapter-intro">Un rapport de bogue ignor\u00e9 est pire qu\u2019aucun rapport du tout. Un rapport professionnel est un outil de communication qui permet \u00e0 un d\u00e9veloppeur de reproduire, corriger et v\u00e9rifier le d\u00e9faut dans les plus brefs d\u00e9lais.</p>',
      '<h2>L\u2019anatomie d\u2019un excellent rapport de bogue</h2>',
      '<table style="width:100%; border-collapse:collapse; margin:var(--space-5) 0; font-size:var(--text-sm);">',
      '<thead style="background:var(--color-bg);"><tr><th style="text-align:left; padding:var(--space-3); border:1px solid var(--color-border);">Champ</th><th style="text-align:left; padding:var(--space-3); border:1px solid var(--color-border);">Que \u00e9crire</th></tr></thead>',
      '<tbody>',
      '<tr><td style="padding:var(--space-3); border:1px solid var(--color-border);"><strong>Titre</strong></td><td style="padding:var(--space-3); border:1px solid var(--color-border);">Court, sp\u00e9cifique, inclut le comportement et la zone. p. ex. \u00ab Sauvegarde bloqu\u00e9e avec une erreur trompeuse lorsque le titre du dossier d\u00e9passe 120 caract\u00e8res \u00bb</td></tr>',
      '<tr><td style="padding:var(--space-3); border:1px solid var(--color-border);"><strong>\u00c9tapes de reproduction</strong></td><td style="padding:var(--space-3); border:1px solid var(--color-border);">Num\u00e9rot\u00e9es, \u00e0 partir d\u2019un \u00e9tat connu. Incluez les valeurs exactes utilis\u00e9es.</td></tr>',
      '<tr><td style="padding:var(--space-3); border:1px solid var(--color-border);"><strong>R\u00e9sultat attendu</strong></td><td style="padding:var(--space-3); border:1px solid var(--color-border);">Ce qui devrait se produire. R\u00e9f\u00e9rencez le crit\u00e8re d\u2019acceptation sp\u00e9cifique.</td></tr>',
      '<tr><td style="padding:var(--space-3); border:1px solid var(--color-border);"><strong>R\u00e9sultat obtenu</strong></td><td style="padding:var(--space-3); border:1px solid var(--color-border);">Ce qui s\u2019est r\u00e9ellement produit. Incluez le texte d\u2019erreur textuellement.</td></tr>',
      '<tr><td style="padding:var(--space-3); border:1px solid var(--color-border);"><strong>Environnement</strong></td><td style="padding:var(--space-3); border:1px solid var(--color-border);">Navigateur + version, SE, r\u00e9solution d\u2019\u00e9cran, version D365/URL de l\u2019org., r\u00e9gion du centre de donn\u00e9es</td></tr>',
      '<tr><td style="padding:var(--space-3); border:1px solid var(--color-border);"><strong>Pi\u00e8ces jointes</strong></td><td style="padding:var(--space-3); border:1px solid var(--color-border);">Capture d\u2019\u00e9cran annot\u00e9e, fichier HAR pour les probl\u00e8mes r\u00e9seau, journaux de la console du navigateur pour les erreurs JS</td></tr>',
      '</tbody>',
      '</table>',
      '<h2>Formule pour le titre</h2>',
      '<p>Un bon titre de bogue suit ce mod\u00e8le : <strong>[Action] \u00e9choue/entra\u00eene [r\u00e9sultat inattendu] lorsque [condition]</strong></p>',
      '<div class="comparison-grid">',
      '<div class="comparison-card bad"><div class="comparison-label">Faible</div>\u00ab Le formulaire de dossier a une erreur \u00bb</div>',
      '<div class="comparison-card good"><div class="comparison-label">Fort</div>\u00ab La sauvegarde du dossier \u00e9choue avec l\u2019erreur \u2018Object reference not set\u2019 lorsque le type de dossier est laiss\u00e9 vide dans le r\u00f4le Senior \u00bb</div>',
      '</div>',
      '<div class="callout good"><strong>Astuce Azure DevOps :</strong> Utilisez le champ \u00ab \u00c9tapes de reproduction \u00bb format\u00e9. Azure DevOps prend en charge le texte enrichi. Utilisez des puces pour les conditions environnementales, des \u00e9tapes num\u00e9rot\u00e9es pour la s\u00e9quence de reproduction et du gras pour les valeurs cl\u00e9s.</div>',
    ].join("\n"),

    "mod-2-2": [
      '<h1>Plans et suites de tests dans ADO</h1>',
      '<p class="chapter-intro">Azure DevOps Test Plans est la couche formelle de gestion des tests. Il organise les cas de test en suites, suit l\u2019ex\u00e9cution et g\u00e9n\u00e8re des rapports. L\u2019apprendre vous \u00e9l\u00e8ve de \u00ab chercheur de bogues \u00bb \u00e0 \u00ab gestionnaire de qualit\u00e9 \u00bb.</p>',
      '<h2>Hi\u00e9rarchie du plan de test</h2>',
      '<pre style="background:var(--color-bg); border:1px solid var(--color-border); border-radius:var(--radius-md); padding:var(--space-4); font-size:var(--text-sm);">Plan de test (Sprint 24 R\u00e9gression)\n  \u2514\u2500\u2500 Suite de tests (Tests fonctionnels)\n  \u2502     \u2514\u2500\u2500 Cas de test TC-101 : V\u00e9rifier la connexion avec des identifiants valides\n  \u2502     \u2514\u2500\u2500 Cas de test TC-102 : V\u00e9rifier l\u2019erreur de connexion sur mot de passe invalide\n  \u2502     \u2514\u2500\u2500 Cas de test TC-103 : V\u00e9rifier le flux de r\u00e9initialisation du mot de passe\n  \u2502\n  \u2514\u2500\u2500 Suite de tests (Tests d\u2019int\u00e9gration)\n        \u2514\u2500\u2500 Cas de test TC-201 : V\u00e9rifier la synchronisation du dossier vers SharePoint\n        \u2514\u2500\u2500 Cas de test TC-202 : V\u00e9rifier la notification par courriel lors de l\u2019escalade</pre>',
      '<h2>Cr\u00e9er un plan de test</h2>',
      '<ol>',
      '<li>Acc\u00e9dez \u00e0 Azure DevOps &gt; Plans de test &gt; Nouveau plan de test</li>',
      '<li>Nommez-le par sprint/version : p. ex. \u00ab Sprint 24 \u2014 R\u00e9gression \u00bb</li>',
      '<li>D\u00e9finissez le chemin de zone et le chemin d\u2019it\u00e9ration pour correspondre au sprint</li>',
      '<li>Ajoutez des suites de tests (bas\u00e9es sur les exigences, bas\u00e9es sur des requ\u00eates ou statiques)</li>',
      '<li>Assignez des testeurs \u00e0 chaque cas de test</li>',
      '<li>D\u00e9finissez la configuration (Chrome/Windows, Safari/Mac, etc.)</li>',
      '</ol>',
      '<div class="callout tip"><strong>Pratique exemplaire :</strong> Utilisez les suites \u00ab bas\u00e9es sur les exigences \u00bb pour lier les cas de test directement aux user stories. Cela donne une tra\u00e7abilit\u00e9 instantan\u00e9e : \u00ab Tous les CA pour l\u2019histoire #45678 sont couverts par ces 5 tests. \u00bb</div>',
    ].join("\n"),

    "mod-2-3": [
      '<h1>Cr\u00e9er et ex\u00e9cuter des cas de test dans ADO</h1>',
      '<p class="chapter-intro">Les cas de test Azure DevOps sont plus que de simples listes de v\u00e9rification. Ils prennent en charge les \u00e9tapes partag\u00e9es, les param\u00e8tres, les pi\u00e8ces jointes et les rapports de r\u00e9sultats d\u00e9taill\u00e9s.</p>',
      '<h2>Structure d\u2019un cas de test dans ADO</h2>',
      '<p>Chaque cas de test dans Azure DevOps contient :</p>',
      '<ul>',
      '<li><strong>Titre</strong> \u2014 doit correspondre au comportement v\u00e9rifi\u00e9</li>',
      '<li><strong>\u00c9tapes</strong> \u2014 paires num\u00e9rot\u00e9es action + r\u00e9sultat attendu. Utilisez l\u2019\u00e9diteur d\u2019\u00e9tapes int\u00e9gr\u00e9, pas un champ de texte brut.</li>',
      '<li><strong>\u00c9tapes partag\u00e9es</strong> \u2014 s\u00e9quences d\u2019\u00e9tapes r\u00e9utilisables (p. ex. \u00ab Se connecter en tant qu\u2019enqu\u00eateur junior \u00bb) qui peuvent \u00eatre incluses dans plusieurs cas de test. Mettez \u00e0 jour une fois, et tous les cas de test r\u00e9f\u00e9ren\u00e7ants refl\u00e8tent le changement.</li>',
      '<li><strong>Param\u00e8tres</strong> \u2014 tests pilot\u00e9s par les donn\u00e9es. Un seul cas de test avec des param\u00e8tres peut g\u00e9n\u00e9rer de nombreuses variations de test.</li>',
      '</ul>',
      '<h2>Ex\u00e9cuter des tests et enregistrer les r\u00e9sultats</h2>',
      '<p>Pendant l\u2019ex\u00e9cution des tests, Azure DevOps permet de :</p>',
      '<ul>',
      '<li>Marquer chaque \u00e9tape comme R\u00e9ussie, \u00c9chou\u00e9e ou Bloqu\u00e9e</li>',
      '<li>Cr\u00e9er des bogues directement \u00e0 partir d\u2019une \u00e9tape \u00e9chou\u00e9e (pr\u00e9-remplis avec les \u00e9tapes de reproduction)</li>',
      '<li>Capturer des captures d\u2019\u00e9cran et les lier au r\u00e9sultat du test</li>',
      '<li>Enregistrer la build/validation sous test pour la tra\u00e7abilit\u00e9</li>',
      '</ul>',
      '<div class="callout warn"><strong>Erreur fr\u00e9quente :</strong> Marquer un cas de test comme \u00ab R\u00e9ussi \u00bb alors que seul le chemin heureux a \u00e9t\u00e9 v\u00e9rifi\u00e9. Un cas de test avec 5 \u00e9tapes dont l\u2019\u00e9tape 3 est \u00ab V\u00e9rifier que le message d\u2019erreur appara\u00eet pour une entr\u00e9e invalide \u00bb doit r\u00e9ellement tester l\u2019entr\u00e9e invalide. Faites confiance \u00e0 votre plan de test, ne sautez pas d\u2019\u00e9tapes.</div>',
    ].join("\n"),

    "mod-2-4": [
      '<h1>Lier les CA aux tests et aux bogues</h1>',
      '<p class="chapter-intro">La tra\u00e7abilit\u00e9 est la colonne vert\u00e9brale de l\u2019AQ professionnelle. Chaque cas de test et chaque bogue doit pouvoir \u00eatre li\u00e9 \u00e0 une exigence ou \u00e0 un crit\u00e8re d\u2019acceptation.</p>',
      '<h2>La cha\u00eene de tra\u00e7abilit\u00e9</h2>',
      '<pre style="background:var(--color-bg); border:1px solid var(--color-border); border-radius:var(--radius-md); padding:var(--space-4); font-size:var(--text-sm);">User Story #45678\n  \u2514\u2500\u2500 T\u00e2che #45679 : Impl\u00e9menter la d\u00e9tection des doublons\n  \u2514\u2500\u2500 Crit\u00e8res d\u2019acceptation (dans la description de l\u2019histoire)\n        \u2514\u2500\u2500 CA-1 : Un avertissement s\u2019affiche lorsque le nom du sujet correspond \u00e0 un dossier ouvert\n              \u2514\u2500\u2500 Cas de test TC-101 : V\u00e9rifier l\u2019avertissement de doublon sur un nom correspondant\n              \u2514\u2500\u2500 Cas de test TC-102 : V\u00e9rifier que fermer l\u2019avertissement continue la soumission\n                    \u2514\u2500\u2500 Bogue #45901 : Le bouton de fermeture de l\u2019avertissement n\u2019est pas visible sur Safari</pre>',
      '<h2>Comment lier dans Azure DevOps</h2>',
      '<ul>',
      '<li><strong>Cas de test vers une exigence/user story :</strong> Utilisez l\u2019onglet \u00ab Cas de test \u00bb sur l\u2019histoire, ou liez via la section \u00ab Liens \u00bb du cas de test. Utilisez le type de lien \u00ab Tests \u00bb.</li>',
      '<li><strong>Bogue vers cas de test :</strong> Lors de la cr\u00e9ation d\u2019un bogue \u00e0 partir d\u2019une \u00e9tape de test dans le Test Runner, le lien est automatique. Le bogue r\u00e9f\u00e9rence le cas de test; le cas de test r\u00e9f\u00e9rence l\u2019exigence.</li>',
      '<li><strong>Bogue vers CA :</strong> R\u00e9f\u00e9rencez le num\u00e9ro du CA dans le titre et la description du bogue. p. ex. \u00ab Violation du CA-2.1 : Un junior peut escalader des dossiers. \u00bb</li>',
      '</ul>',
      '<div class="callout good"><strong>Pourquoi la tra\u00e7abilit\u00e9 est importante :</strong> Lorsqu\u2019un gestionnaire de version demande \u00ab L\u2019histoire #45678 a-t-elle \u00e9t\u00e9 test\u00e9e? \u00bb, vous pouvez r\u00e9pondre de fa\u00e7on d\u00e9finitive, pas par une supposition. Lorsqu\u2019un bogue est signal\u00e9, vous pouvez imm\u00e9diatement identifier quel CA est viol\u00e9 et quel cas de test aurait d\u00fb le d\u00e9tecter.</div>',
      '<h2>Piste d\u2019audit pour la conformit\u00e9</h2>',
      '<p>Dans les environnements r\u00e9glement\u00e9s (soins de sant\u00e9, services financiers), la tra\u00e7abilit\u00e9 n\u2019est pas facultative. Les v\u00e9rificateurs exigent la preuve que chaque exigence a un test correspondant et que chaque bogue est li\u00e9 \u00e0 son exigence source. Azure DevOps rend cela possible \u2014 mais seulement si vous pratiquez la discipline de liaison chaque jour.</p>',
    ].join("\n"),

    "capstone-advanced": [
      '<div class="cv-placeholder">',
      '<div class="cv-placeholder-icon">🎯</div>',
      '<h3>\u00c9valuation finale avanc\u00e9e</h3>',
      '<p>Cette \u00e9valuation de bout en bout teste tout ce que vous avez appris dans le cours avanc\u00e9 :</p>',
      '<ol style="text-align:left; max-width:480px; margin:var(--space-4) auto; font-size:var(--text-sm); color:var(--color-ink-soft);">',
      '<li style="margin-bottom:var(--space-3);">R\u00e9visez la user story et les crit\u00e8res d\u2019acceptation fournis</li>',
      '<li style="margin-bottom:var(--space-3);">R\u00e9digez un ensemble complet de cas de test couvrant le chemin heureux, les cas limites et les limites de s\u00e9curit\u00e9</li>',
      '<li style="margin-bottom:var(--space-3);">Ex\u00e9cutez les cas de test dans l\u2019environnement de laboratoire D365 CRM</li>',
      '<li style="margin-bottom:var(--space-3);">Consignez les d\u00e9fauts trouv\u00e9s dans la simulation Azure DevOps</li>',
      '<li style="margin-bottom:var(--space-3);">Liez chaque d\u00e9faut au crit\u00e8re d\u2019acceptation viol\u00e9</li>',
      '<li style="margin-bottom:var(--space-3);">Soumettez votre plan de test et vos r\u00e9sultats pour r\u00e9vision</li>',
      '</ol>',
      '<p style="margin-top:var(--space-5);"><a href="capstone-2.html" target="_blank" class="btn btn-primary" style="text-decoration:none;">Ouvrir l\u2019\u00e9valuation avanc\u00e9e \u2192</a></p>',
      '</div>',
    ].join("\n"),
  },
};

// ── FRENCH QUIZ TRANSLATIONS ──────────────────────────────────────────────────
// French versions of quiz questions for courses that support bilingual mode.
// Structure matches COURSE_QUIZZES[courseId][moduleId].
// When language is FR, getQuizQuestions() checks LANG_QUIZZES_FR first.
var LANG_QUIZZES_FR = {

  // ── QA Onboarding — Advanced ─────────────────────────────────────────────
  "qa-onboarding-advanced": {

    // ── MODULE 1: Deep D365 Testing ────────────────────────────────────────
    "mod-1": [
      {
        questionId: "adv-m1-q1",
        type: "multiple-choice",
        questionText: "Quelle est la chose la plus importante \u00e0 v\u00e9rifier apr\u00e8s qu\u2019un workflow ou un plug-in D365 se d\u00e9clenche lors de la sauvegarde d\u2019un enregistrement?",
        options: [
          "Que le message de confirmation toast est apparu",
          "Les effets en aval sur les enregistrements et processus connexes",
          "Que la page n\u2019a pas recharg\u00e9",
          "Que l\u2019horodatage du journal d\u2019audit correspond \u00e0 l\u2019horloge du serveur",
        ],
        correctAnswer: "Les effets en aval sur les enregistrements et processus connexes",
        explanation: "Un test uniquement dans l\u2019interface utilisateur est incomplet. D365 peut indiquer \u00ab Sauvegard\u00e9 avec succ\u00e8s \u00bb m\u00eame si un workflow ou un plug-in a lev\u00e9 une exception. V\u00e9rifiez toujours le r\u00e9sultat concret en aval \u2014 le courriel a-t-il \u00e9t\u00e9 envoy\u00e9, le propri\u00e9taire a-t-il \u00e9t\u00e9 attribu\u00e9, le statut s\u2019est-il propag\u00e9?",
        lessonContext: "Workflows D365 concrets",
      },
      {
        questionId: "adv-m1-q2",
        type: "multiple-choice",
        questionText: "Laquelle des approches suivantes est correcte pour tester les flux de processus d\u2019affaires (BPF)?",
        options: [
          "Tester seulement le chemin heureux pour confirmer que le BPF progresse \u00e0 travers toutes les \u00e9tapes",
          "Tester l\u2019avancement des \u00e9tapes avec des champs obligatoires manquants, la navigation arri\u00e8re et les branchements conditionnels par r\u00f4le",
          "V\u00e9rifier que le BPF est visible uniquement par les administrateurs syst\u00e8me",
          "Ignorer les tests BPF puisque c\u2019est une configuration, pas du code personnalis\u00e9",
        ],
        correctAnswer: "Tester l\u2019avancement des \u00e9tapes avec des champs obligatoires manquants, la navigation arri\u00e8re et les branchements conditionnels par r\u00f4le",
        explanation: "Les BPF imposent des champs obligatoires par \u00e9tape, emp\u00eachent de sauter des \u00e9tapes et peuvent avoir des branchements conditionnels. Chaque r\u00f4le peut voir un BPF diff\u00e9rent. Tester seulement le chemin heureux manque des bogues de validation critiques.",
        lessonContext: "Workflows D365 concrets",
      },
      {
        questionId: "adv-m1-q3",
        type: "true-false",
        questionText: "Lors du test d\u2019un champ Date/Heure dans D365, tester le 29 f\u00e9vrier d\u2019une ann\u00e9e non bissextile est inutile car D365 valide automatiquement les dates.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Faux",
        explanation: "Les cas limites comme le 29 f\u00e9vrier les ann\u00e9es non bissextiles, les transitions de fuseau horaire \u00e0 minuit et les dates avant 1970 peuvent tous produire un comportement inattendu. D365 ne se prot\u00e8ge pas automatiquement contre tous les cas limites \u2014 c\u2019est le travail du testeur.",
        lessonContext: "Cas limites dans D365",
      },
      {
        questionId: "adv-m1-q4",
        type: "multiple-choice",
        questionText: "Quelle est la pratique exemplaire lors du test de la s\u00e9curit\u00e9 D365 entre les r\u00f4les?",
        options: [
          "Tester tout en tant qu\u2019administrateur syst\u00e8me \u2014 si cela passe l\u00e0, cela fonctionne pour tous les r\u00f4les",
          "Cr\u00e9er un compte de test distinct pour chaque r\u00f4le et tester chaque sc\u00e9nario du point de vue de ce r\u00f4le",
          "Documenter le mod\u00e8le de s\u00e9curit\u00e9 et pr\u00e9sumer qu\u2019il fonctionne correctement",
          "Tester les limites de s\u00e9curit\u00e9 seulement lorsqu\u2019un bogue est signal\u00e9",
        ],
        correctAnswer: "Cr\u00e9er un compte de test distinct pour chaque r\u00f4le et tester chaque sc\u00e9nario du point de vue de ce r\u00f4le",
        explanation: "Tester seulement en tant qu\u2019administrateur donne une fausse impression de s\u00e9curit\u00e9. Diff\u00e9rents r\u00f4les peuvent voir des autorisations de champ, des niveaux d\u2019acc\u00e8s aux enregistrements et des BPF diff\u00e9rents. Cr\u00e9ez de vrais comptes de test pour chaque r\u00f4le et testez de leur perspective.",
        lessonContext: "Cas limites dans D365",
      },
      {
        questionId: "adv-m1-q5",
        type: "multiple-choice",
        questionText: "Laquelle de ces options d\u00e9crit la meilleure strat\u00e9gie de gestion des donn\u00e9es de test?",
        options: [
          "Utiliser les donn\u00e9es de production pour l\u2019environnement de test le plus r\u00e9aliste",
          "Maintenir un ensemble de donn\u00e9es de base organis\u00e9 plus des ensembles de donn\u00e9es sp\u00e9cifiques aux sc\u00e9narios et aux limites",
          "Cr\u00e9er toutes les donn\u00e9es de test \u00e0 partir de z\u00e9ro avant chaque cycle de test",
          "Partager un seul ensemble de donn\u00e9es de test entre toutes les \u00e9quipes et tous les environnements de test",
        ],
        correctAnswer: "Maintenir un ensemble de donn\u00e9es de base organis\u00e9 plus des ensembles de donn\u00e9es sp\u00e9cifiques aux sc\u00e9narios et aux limites",
        explanation: "Les donn\u00e9es de production pr\u00e9sentent des risques d\u2019exposition de renseignements personnels et de r\u00e9f\u00e9rences orphelines. Des donn\u00e9es fra\u00eeches chaque cycle sont lentes. Un ensemble de base organis\u00e9 couvre les besoins partag\u00e9s, les donn\u00e9es sp\u00e9cifiques aux sc\u00e9narios ciblent les tests individuels et les donn\u00e9es limites couvrent les cas limites.",
        lessonContext: "Strat\u00e9gies de pr\u00e9paration des donn\u00e9es de test",
      },
      {
        questionId: "adv-m1-q6",
        type: "multiple-choice",
        questionText: "Quel est le principe cl\u00e9 pour les tests d\u2019int\u00e9gration avec D365?",
        options: [
          "Tous les services connect\u00e9s doivent \u00eatre pleinement op\u00e9rationnels pendant les tests, sinon les tests ne peuvent pas avoir lieu",
          "Une d\u00e9faillance d\u2019int\u00e9gration en aval ne doit jamais corrompre les donn\u00e9es D365 en amont",
          "Les int\u00e9grations n\u00e9cessitent pas de tests puisqu\u2019elles utilisent des API standard",
          "Les flux Power Automate sont test\u00e9s par le cr\u00e9ateur du flux, pas par l\u2019\u00e9quipe AQ",
        ],
        correctAnswer: "Une d\u00e9faillance d\u2019int\u00e9gration en aval ne doit jamais corrompre les donn\u00e9es D365 en amont",
        explanation: "D365 doit rester coh\u00e9rent m\u00eame lorsque les services connect\u00e9s (Power Automate, SharePoint, API externes) sont indisponibles. L\u2019int\u00e9gration doit \u00e9chouer gracieusement, consigner l\u2019erreur avec suffisamment de d\u00e9tails et ne pas corrompre l\u2019enregistrement d\u00e9clencheur.",
        lessonContext: "Tests d\u2019int\u00e9gration avec D365",
      },
    ],

    // ── MODULE 2: Azure DevOps Mastery ─────────────────────────────────────
    "mod-2": [
      {
        questionId: "adv-m2-q1",
        type: "multiple-choice",
        questionText: "Quel titre de bogue suit le mieux la formule recommand\u00e9e pour les rapports de bogue professionnels?",
        options: [
          "\u00ab Le formulaire de dossier a une erreur lors de la sauvegarde \u00bb",
          "\u00ab Erreur sur le formulaire \u00bb",
          "\u00ab La sauvegarde du dossier \u00e9choue avec l\u2019erreur \u2018Object reference not set\u2019 lorsque le type de dossier est laiss\u00e9 vide dans le r\u00f4le Senior \u00bb",
          "\u00ab Bogue dans la cr\u00e9ation de dossier \u00bb",
        ],
        correctAnswer: "\u00ab La sauvegarde du dossier \u00e9choue avec l\u2019erreur \u2018Object reference not set\u2019 lorsque le type de dossier est laiss\u00e9 vide dans le r\u00f4le Senior \u00bb",
        explanation: "Un bon titre de bogue suit le mod\u00e8le : [Action] \u00e9choue/entra\u00eene [r\u00e9sultat inattendu] lorsque [condition]. Il inclut l\u2019\u00e9chec sp\u00e9cifique, la condition d\u00e9clencheuse et suffisamment de contexte pour qu\u2019un d\u00e9veloppeur comprenne la port\u00e9e.",
        lessonContext: "R\u00e9diger des rapports de bogue professionnels",
      },
      {
        questionId: "adv-m2-q2",
        type: "multiple-choice",
        questionText: "Quel est le bon usage du champ \u00ab \u00c9tapes de reproduction \u00bb dans un rapport de bogue Azure DevOps?",
        options: [
          "Un bref r\u00e9sum\u00e9 de ce que le d\u00e9veloppeur doit rechercher",
          "Des \u00e9tapes num\u00e9rot\u00e9es \u00e0 partir d\u2019un \u00e9tat connu, incluant les valeurs exactes, permettant \u00e0 quiconque de reproduire le bogue",
          "Un enregistrement vid\u00e9o de la session de test",
          "Un lien vers le cas de test qui a d\u00e9couvert le bogue",
        ],
        correctAnswer: "Des \u00e9tapes num\u00e9rot\u00e9es \u00e0 partir d\u2019un \u00e9tat connu, incluant les valeurs exactes, permettant \u00e0 quiconque de reproduire le bogue",
        explanation: "Les \u00e9tapes de reproduction doivent \u00eatre autonomes et sans ambigu\u00eft\u00e9. Un d\u00e9veloppeur doit pouvoir les suivre \u00e9tape par \u00e9tape et voir le bogue sans avoir besoin de contexte suppl\u00e9mentaire ni de poser des questions de suivi.",
        lessonContext: "R\u00e9diger des rapports de bogue professionnels",
      },
      {
        questionId: "adv-m2-q3",
        type: "true-false",
        questionText: "Dans Azure DevOps Test Plans, utiliser des suites \u00ab bas\u00e9es sur les exigences \u00bb lie les cas de test directement aux user stories pour une tra\u00e7abilit\u00e9 automatique.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Vrai",
        explanation: "Les suites bas\u00e9es sur les exigences cr\u00e9ent un lien direct entre les cas de test et la user story qu\u2019ils valident. Cela donne une tra\u00e7abilit\u00e9 instantan\u00e9e \u2014 vous pouvez voir exactement quels crit\u00e8res d\u2019acceptation sont couverts par quels tests.",
        lessonContext: "Plans et suites de tests dans ADO",
      },
      {
        questionId: "adv-m2-q4",
        type: "multiple-choice",
        questionText: "\u00c0 quoi servent les \u00ab \u00e9tapes partag\u00e9es \u00bb dans les cas de test Azure DevOps?",
        options: [
          "Des \u00e9tapes partag\u00e9es publiquement dans toute l\u2019organisation",
          "Des s\u00e9quences d\u2019\u00e9tapes r\u00e9utilisables (p. ex. \u00ab Se connecter en tant qu\u2019enqu\u00eateur junior \u00bb) qui se mettent \u00e0 jour partout lorsqu\u2019elles sont modifi\u00e9es une fois",
          "Des \u00e9tapes qui sont automatiquement ex\u00e9cut\u00e9es par l\u2019ex\u00e9cuteur de tests",
          "Des \u00e9tapes partag\u00e9es entre le d\u00e9veloppeur et le testeur lors du transfert",
        ],
        correctAnswer: "Des s\u00e9quences d\u2019\u00e9tapes r\u00e9utilisables (p. ex. \u00ab Se connecter en tant qu\u2019enqu\u00eateur junior \u00bb) qui se mettent \u00e0 jour partout lorsqu\u2019elles sont modifi\u00e9es une fois",
        explanation: "Les \u00e9tapes partag\u00e9es \u00e9vitent la duplication de s\u00e9quences courantes. Mettez \u00e0 jour les \u00e9tapes partag\u00e9es une fois, et chaque cas de test qui les r\u00e9f\u00e9rence est automatiquement mis \u00e0 jour. Cela r\u00e9duit consid\u00e9rablement les efforts de maintenance.",
        lessonContext: "Cr\u00e9er et ex\u00e9cuter des cas de test dans ADO",
      },
      {
        questionId: "adv-m2-q5",
        type: "multiple-choice",
        questionText: "Que devez-vous faire lors de l\u2019ex\u00e9cution d\u2019un test dans Azure DevOps lorsque vous rencontrez un bogue?",
        options: [
          "Marquer tout le cas de test comme \u00c9chou\u00e9 et passer \u00e0 autre chose",
          "Marquer l\u2019\u00e9tape \u00e9chou\u00e9e sp\u00e9cifique, cr\u00e9er un bogue directement \u00e0 partir de celle-ci (pr\u00e9-rempli avec les \u00e9tapes de reproduction) et continuer \u00e0 tester les \u00e9tapes restantes",
          "Arr\u00eater tous les tests et le signaler imm\u00e9diatement au responsable",
          "Sauter l\u2019\u00e9tape et marquer le test comme R\u00e9ussi puisque la fonctionnalit\u00e9 principale fonctionne",
        ],
        correctAnswer: "Marquer l\u2019\u00e9tape \u00e9chou\u00e9e sp\u00e9cifique, cr\u00e9er un bogue directement \u00e0 partir de celle-ci (pr\u00e9-rempli avec les \u00e9tapes de reproduction) et continuer \u00e0 tester les \u00e9tapes restantes",
        explanation: "Azure DevOps permet des r\u00e9sultats par \u00e9tape et peut cr\u00e9er automatiquement un bogue pr\u00e9-rempli avec les \u00e9tapes de reproduction. Marquez seulement l\u2019\u00e9tape \u00e9chou\u00e9e, cr\u00e9ez le bogue, puis continuez \u00e0 tester les autres \u00e9tapes. Ne marquez pas un test comme R\u00e9ussi si une \u00e9tape a \u00e9chou\u00e9.",
        lessonContext: "Cr\u00e9er et ex\u00e9cuter des cas de test dans ADO",
      },
      {
        questionId: "adv-m2-q6",
        type: "multiple-choice",
        questionText: "Pourquoi la tra\u00e7abilit\u00e9 entre les bogues, les cas de test et les crit\u00e8res d\u2019acceptation est-elle importante?",
        options: [
          "Elle satisfait aux exigences documentaires de l\u2019\u00e9quipe AQ",
          "Elle permet \u00e0 un gestionnaire de version de confirmer de fa\u00e7on d\u00e9finitive quelles histoires sont test\u00e9es et quels CA sont viol\u00e9s par les bogues ouverts \u2014 essentielle pour les pistes d\u2019audit dans les environnements r\u00e9glement\u00e9s",
          "Elle rend le tableau de bord Azure DevOps plus complet",
          "Elle n\u2019est n\u00e9cessaire que pour les audits de conformit\u00e9, pas pour les tests quotidiens",
        ],
        correctAnswer: "Elle permet \u00e0 un gestionnaire de version de confirmer de fa\u00e7on d\u00e9finitive quelles histoires sont test\u00e9es et quels CA sont viol\u00e9s par les bogues ouverts \u2014 essentielle pour les pistes d\u2019audit dans les environnements r\u00e9glement\u00e9s",
        explanation: "La tra\u00e7abilit\u00e9 transforme l\u2019\u00e9valuation subjective de l\u2019\u00e9tat de pr\u00e9paration (\u00ab Je pense que c\u2019est test\u00e9 \u00bb) en preuve objective. Dans les environnements r\u00e9glement\u00e9s (soins de sant\u00e9, services financiers), les v\u00e9rificateurs exigent la preuve que chaque exigence correspond \u00e0 un test et que chaque bogue est li\u00e9 \u00e0 son CA source.",
        lessonContext: "Lier les CA aux tests et aux bogues",
      },
    ],
  },

  // ── Agile & Scrum for Developers ─────────────────────────────────────────
  "agile-scrum-dev": {

    // ── MODULE 1 QUIZ: Introduction to Agile and Scrum ─────────────────────
    "mod-1": [
      {
        questionId: "as-m1-q1",
        type: "multiple-choice",
        questionText: "Laquelle des propositions suivantes n'est PAS l'une des quatre valeurs du Manifeste Agile?",
        options: [
          "Les individus et leurs interactions plus que les processus et les outils",
          "Des logiciels op\u00e9rationnels plus qu'une documentation exhaustive",
          "Un p\u00e9rim\u00e8tre fixe plut\u00f4t que des exigences changeantes",
          "L'adaptation au changement plus que le suivi d'un plan",
        ],
        correctAnswer: "Un p\u00e9rim\u00e8tre fixe plut\u00f4t que des exigences changeantes",
        explanation: "Le Manifeste Agile valorise 'L'adaptation au changement plus que le suivi d'un plan' — l'oppos\u00e9 d'un p\u00e9rim\u00e8tre fixe. Les quatre valeurs mettent l'accent sur les personnes, les logiciels fonctionnels, la collaboration client et l'adaptabilit\u00e9.",
        lessonContext: "",
      },
      {
        questionId: "as-m1-q2",
        type: "multiple-choice",
        questionText: "Selon le Manifeste Agile, quelle est la principale mesure de progr\u00e8s?",
        options: [
          "Le nombre de story points compl\u00e9t\u00e9s",
          "Un logiciel fonctionnel",
          "Le pourcentage d'exigences document\u00e9es",
          "La livraison \u00e0 temps selon le plan original",
        ],
        correctAnswer: "Un logiciel fonctionnel",
        explanation: "Le Principe #7 stipule : 'Un logiciel fonctionnel est la principale mesure de progr\u00e8s.' Cela d\u00e9place l'attention de la documentation et des plans vers des livrables tangibles et fonctionnels.",
        lessonContext: "",
      },
      {
        questionId: "as-m1-q3",
        type: "multiple-choice",
        questionText: "Scrum est fond\u00e9 sur quel concept philosophique?",
        options: ["Rationalisme", "Empirisme", "D\u00e9terminisme", "Structuralisme"],
        correctAnswer: "Empirisme",
        explanation: "Scrum est fond\u00e9 sur l'empirisme — l'id\u00e9e que la connaissance vient de l'exp\u00e9rience et que les d\u00e9cisions devraient \u00eatre bas\u00e9es sur ce qui est connu. C'est pourquoi Scrum met l'accent sur l'inspection et l'adaptation.",
        lessonContext: "",
      },
      {
        questionId: "as-m1-q4",
        type: "multiple-choice",
        questionText: "Lequel des \u00e9l\u00e9ments suivants n'est PAS l'un des trois piliers de Scrum?",
        options: ["Transparence", "Inspection", "Documentation", "Adaptation"],
        correctAnswer: "Documentation",
        explanation: "Les trois piliers de Scrum sont la Transparence, l'Inspection et l'Adaptation. La Documentation n'est pas un pilier — Scrum valorise les logiciels fonctionnels plus que la documentation exhaustive.",
        lessonContext: "",
      },
      {
        questionId: "as-m1-q5",
        type: "multiple-choice",
        questionText: "Comment Agile g\u00e8re-t-il les changements d'exigences par rapport \u00e0 la m\u00e9thode Cascade?",
        options: [
          "Agile rejette les changements une fois le d\u00e9veloppement commenc\u00e9",
          "Agile accueille les changements, m\u00eame tard dans le d\u00e9veloppement",
          "Les deux g\u00e8rent les changements de la m\u00eame fa\u00e7on",
          "La Cascade est plus flexible avec les changements qu'Agile",
        ],
        correctAnswer: "Agile accueille les changements, m\u00eame tard dans le d\u00e9veloppement",
        explanation: "Le Principe #2 stipule : 'Accueillir les changements d'exigences, m\u00eame tard dans le d\u00e9veloppement.' La Cascade consid\u00e8re le changement comme un risque; Agile le consid\u00e8re comme une opportunit\u00e9.",
        lessonContext: "",
      },
      {
        questionId: "as-m1-q6",
        type: "true-false",
        questionText: "L'\u00e9tat d'esprit Agile exige que les \u00e9quipes suivent un ensemble prescrit de pratiques et de processus exactement comme document\u00e9.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Faux",
        explanation: "Agile est un \u00e9tat d'esprit, pas une m\u00e9thodologie prescriptive. Les \u00e9quipes sont encourag\u00e9es \u00e0 adapter les pratiques \u00e0 leur contexte. Suivre aveugl\u00e9ment les c\u00e9r\u00e9monies sans adopter les valeurs sous-jacentes est souvent appel\u00e9 'cargo-cult Agile'.",
        lessonContext: "",
      },
      {
        questionId: "as-m1-q7",
        type: "multiple-choice",
        questionText: "Laquelle des propositions suivantes d\u00e9crit le mieux pourquoi le mod\u00e8le Agile de Spotify est remarquable?",
        options: [
          "Ils suivent strictement le Guide Scrum sans aucune modification",
          "Ils ont adapt\u00e9 les pratiques Agile (Squads, Tribes, Chapters, Guildes) \u00e0 leur culture",
          "Ils utilisent la Cascade pour la planification et Agile pour l'ex\u00e9cution",
          "Ils ont \u00e9t\u00e9 la premi\u00e8re entreprise \u00e0 adopter Agile",
        ],
        correctAnswer: "Ils ont adapt\u00e9 les pratiques Agile (Squads, Tribes, Chapters, Guildes) \u00e0 leur culture",
        explanation: "Spotify a cr\u00e9\u00e9 un mod\u00e8le unique avec des Squads (mini-startups), Tribes (groupes de squads), Chapters (groupes de comp\u00e9tences) et Guildes (communaut\u00e9s d'int\u00e9r\u00eat). La le\u00e7on cl\u00e9 est qu'ils ont adapt\u00e9 Scrum \u00e0 leur culture plut\u00f4t que de forcer leur culture \u00e0 s'adapter \u00e0 Scrum.",
        lessonContext: "",
      },
      {
        questionId: "as-m1-q8",
        type: "true-false",
        questionText: "Une \u00e9quipe qui tient des m\u00eal\u00e9es quotidiennes, des revues de sprint et des r\u00e9trospectives est garantie d'\u00eatre v\u00e9ritablement Agile.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Faux",
        explanation: "Adopter les c\u00e9r\u00e9monies sans adopter les valeurs sous-jacentes (confiance, autonomisation, s\u00e9curit\u00e9 psychologique) est du 'cargo-cult Agile'. La v\u00e9ritable agilit\u00e9 n\u00e9cessite un changement d'\u00e9tat d'esprit, pas seulement une adoption m\u00e9canique des pratiques.",
        lessonContext: "",
      },
    ],

    // ── MODULE 2 QUIZ: Agile Development Practices ─────────────────────────
    "mod-2": [
      {
        questionId: "as-m2-q1",
        type: "multiple-choice",
        questionText: "Quelle pratique XP implique que deux d\u00e9veloppeurs partagent un poste de travail pour \u00e9crire du code?",
        options: ["R\u00e9vision de code", "Programmation en bin\u00f4me", "Programmation en mob", "Examen par les pairs"],
        correctAnswer: "Programmation en bin\u00f4me",
        explanation: "La programmation en bin\u00f4me est une pratique XP o\u00f9 deux d\u00e9veloppeurs travaillent ensemble \u00e0 un seul poste de travail. L'un \u00e9crit le code (le conducteur) tandis que l'autre r\u00e9vise chaque ligne (le navigateur), am\u00e9liorant la qualit\u00e9 du code et le partage des connaissances.",
        lessonContext: "",
      },
      {
        questionId: "as-m2-q2",
        type: "multiple-choice",
        questionText: "Quelle est la principale diff\u00e9rence entre Scrum et Kanban concernant le p\u00e9rim\u00e8tre de travail?",
        options: [
          "Scrum utilise des sprints de dur\u00e9e fixe; Kanban utilise un flux continu",
          "Kanban utilise des sprints de dur\u00e9e fixe; Scrum utilise un flux continu",
          "Les deux utilisent des sprints de dur\u00e9e fixe",
          "Les deux utilisent un flux continu",
        ],
        correctAnswer: "Scrum utilise des sprints de dur\u00e9e fixe; Kanban utilise un flux continu",
        explanation: "Scrum enferme le travail dans des Sprints de dur\u00e9e fixe (g\u00e9n\u00e9ralement 1 \u00e0 4 semaines), tandis que Kanban utilise un flux continu sans dur\u00e9e d'it\u00e9ration prescrite. C'est une diff\u00e9rence fondamentale entre les deux approches.",
        lessonContext: "",
      },
      {
        questionId: "as-m2-q3",
        type: "multiple-choice",
        questionText: "Dans Kanban, que signifie WIP et quel est son objectif?",
        options: [
          "Work In Progress (Travail en cours) — limite le nombre d'\u00e9l\u00e9ments actifs \u00e0 la fois pour r\u00e9duire le multit\u00e2che",
          "Work Improvement Plan (Plan d'am\u00e9lioration du travail) — une feuille de route pour l'optimisation des processus",
          "Work Integration Point (Point d'int\u00e9gration du travail) — quand le travail se d\u00e9place entre les \u00e9tapes",
          "Weekly Iteration Plan (Plan d'it\u00e9ration hebdomadaire) — l'horaire de l'\u00e9quipe pour la semaine",
        ],
        correctAnswer: "Work In Progress (Travail en cours) — limite le nombre d'\u00e9l\u00e9ments actifs \u00e0 la fois pour r\u00e9duire le multit\u00e2che",
        explanation: "WIP = Work In Progress (Travail en cours). Limiter le WIP est un principe fondamental de Kanban. En restreignant le nombre d'\u00e9l\u00e9ments pouvant \u00eatre en cours \u00e0 la fois, les \u00e9quipes r\u00e9duisent les changements de contexte, identifient les goulots d'\u00e9tranglement et am\u00e9liorent le flux.",
        lessonContext: "",
      },
      {
        questionId: "as-m2-q4",
        type: "true-false",
        questionText: "Le d\u00e9veloppement logiciel Lean, adapt\u00e9 du syst\u00e8me de fabrication de Toyota, inclut le principe d''\u00e9liminer le gaspillage'.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Vrai",
        explanation: "Oui — le premier principe Lean est '\u00c9liminer le gaspillage', ce qui dans le logiciel signifie du code, des fonctionnalit\u00e9s, des d\u00e9lais, des transferts et des d\u00e9fauts inutiles. Les autres principes Lean incluent l'amplification de l'apprentissage et la d\u00e9cision au plus tard possible.",
        lessonContext: "",
      },
      {
        questionId: "as-m2-q5",
        type: "multiple-choice",
        questionText: "Qu'est-ce qu'une approche 'Scrumban'?",
        options: [
          "Une application stricte de Scrum sans aucun \u00e9l\u00e9ment Kanban",
          "Un hybride qui utilise les r\u00f4les et \u00e9v\u00e9nements Scrum avec le tableau visuel et les limites WIP de Kanban",
          "Un niveau de certification pour les Scrum Masters",
          "Un outil pour mesurer la v\u00e9locit\u00e9 de l'\u00e9quipe",
        ],
        correctAnswer: "Un hybride qui utilise les r\u00f4les et \u00e9v\u00e9nements Scrum avec le tableau visuel et les limites WIP de Kanban",
        explanation: "Scrumban combine les r\u00f4les Scrum (PO, SM, D\u00e9veloppeurs) et les \u00e9v\u00e9nements (Planification du Sprint, M\u00eal\u00e9e quotidienne, Revue, R\u00e9tro) avec le tableau visuel et les limites WIP de Kanban. De nombreuses \u00e9quipes trouvent que cet hybride offre \u00e0 la fois structure et flexibilit\u00e9 de flux.",
        lessonContext: "",
      },
      {
        questionId: "as-m2-q6",
        type: "multiple-choice",
        questionText: "Lequel des \u00e9l\u00e9ments suivants n'est PAS un \u00e9l\u00e9ment prescrit du cadre Scrum?",
        options: ["M\u00eal\u00e9e quotidienne", "R\u00e9trospective du Sprint", "Backlog du Sprint", "Graphique burndown"],
        correctAnswer: "Graphique burndown",
        explanation: "Bien que les graphiques burndown soient couramment utilis\u00e9s par les \u00e9quipes Scrum, ils ne sont pas un artefact prescrit dans le Guide Scrum. Les trois artefacts prescrits sont le Backlog du produit, le Backlog du Sprint et l'Incr\u00e9ment.",
        lessonContext: "",
      },
    ],

    // ── MODULE 3 QUIZ: Scrum Roles and Responsibilities ────────────────────
    "mod-3": [
      {
        questionId: "as-m3-q1",
        type: "multiple-choice",
        questionText: "Qui est responsable de maximiser la valeur du produit r\u00e9sultant du travail de l'\u00c9quipe de D\u00e9veloppement?",
        options: ["Scrum Master", "Product Owner", "\u00c9quipe de D\u00e9veloppement", "Gestionnaire de projet"],
        correctAnswer: "Product Owner",
        explanation: "Le Product Owner est la personne unique responsable de maximiser la valeur du produit. Cela inclut la gestion du Backlog du produit, la d\u00e9finition de l'Objectif du produit et la prise de d\u00e9cisions de priorit\u00e9.",
        lessonContext: "",
      },
      {
        questionId: "as-m3-q2",
        type: "multiple-choice",
        questionText: "Quel r\u00f4le est d\u00e9crit comme un 'leader servant' pour l'\u00c9quipe Scrum?",
        options: ["Product Owner", "Scrum Master", "Chef de l'\u00e9quipe de d\u00e9veloppement", "Partie prenante"],
        correctAnswer: "Scrum Master",
        explanation: "Le Scrum Master est un leader servant qui promeut et soutient Scrum. Il coache l'\u00e9quipe, facilite les \u00e9v\u00e9nements, \u00e9limine les obstacles et prot\u00e8ge l'\u00e9quipe des perturbations.",
        lessonContext: "",
      },
      {
        questionId: "as-m3-q3",
        type: "multiple-choice",
        questionText: "Quel est un antipatron courant pour le r\u00f4le de Product Owner?",
        options: [
          "Prendre des d\u00e9cisions de priorit\u00e9 rapides",
          "Agir comme un 'proxy' qui ne fait que relayer les ordres des parties prenantes",
          "Assister aux Revues de Sprint",
          "Collaborer avec l'\u00c9quipe de D\u00e9veloppement sur le raffinement du backlog",
        ],
        correctAnswer: "Agir comme un 'proxy' qui ne fait que relayer les ordres des parties prenantes",
        explanation: "Un PO efficace a l'autorit\u00e9 de prendre de v\u00e9ritables d\u00e9cisions de priorisation. Un PO 'proxy' qui ne fait que relayer les ordres des parties prenantes ne peut pas maximiser efficacement la valeur.",
        lessonContext: "",
      },
      {
        questionId: "as-m3-q4",
        type: "true-false",
        questionText: "Le Scrum Master assigne des t\u00e2ches aux membres de l'\u00c9quipe de D\u00e9veloppement pour garantir que le travail soit effectu\u00e9 efficacement.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Faux",
        explanation: "Les Scrum Masters n'assignent pas de t\u00e2ches — ils facilitent l'autogestion de l'\u00e9quipe. L'\u00c9quipe de D\u00e9veloppement est auto-organis\u00e9e et d\u00e9cide comment transformer les \u00e9l\u00e9ments du Backlog en un Incr\u00e9ment de valeur.",
        lessonContext: "",
      },
      {
        questionId: "as-m3-q5",
        type: "multiple-choice",
        questionText: "Quelle est la taille optimale recommand\u00e9e pour une \u00c9quipe de D\u00e9veloppement Scrum?",
        options: ["1-3 personnes", "3-9 personnes", "10-15 personnes", "Autant que n\u00e9cessaire"],
        correctAnswer: "3-9 personnes",
        explanation: "Le Guide Scrum recommande des \u00c9quipes de D\u00e9veloppement de 3 \u00e0 9 personnes. Les petites \u00e9quipes peuvent manquer de comp\u00e9tences n\u00e9cessaires; les grandes \u00e9quipes ont du mal avec la coordination et les frais de communication.",
        lessonContext: "",
      },
      {
        questionId: "as-m3-q6",
        type: "true-false",
        questionText: "Une \u00c9quipe de D\u00e9veloppement devrait avoir des sous-\u00e9quipes telles qu'une \u00e9quipe AQ distincte et une \u00e9quipe d'architecture distincte pour une meilleure sp\u00e9cialisation.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Faux",
        explanation: "Scrum stipule explicitement qu'il n'y a pas de sous-\u00e9quipes au sein de l'\u00c9quipe de D\u00e9veloppement. L'\u00e9quipe est polyvalente, ce qui signifie qu'elle poss\u00e8de collectivement toutes les comp\u00e9tences n\u00e9cessaires pour livrer un Incr\u00e9ment.",
        lessonContext: "",
      },
      {
        questionId: "as-m3-q7",
        type: "multiple-choice",
        questionText: "Quand les parties prenantes s'engagent-elles principalement avec l'\u00c9quipe Scrum pour inspecter l'Incr\u00e9ment et fournir des commentaires?",
        options: ["M\u00eal\u00e9e quotidienne", "Planification du Sprint", "Revue du Sprint", "R\u00e9trospective du Sprint"],
        correctAnswer: "Revue du Sprint",
        explanation: "La Revue du Sprint est le point de contact formel principal o\u00f9 les parties prenantes inspectent l'Incr\u00e9ment et fournissent des commentaires qui fa\u00e7onnent le Backlog du produit.",
        lessonContext: "",
      },
      {
        questionId: "as-m3-q8",
        type: "true-false",
        questionText: "Les parties prenantes peuvent demander des changements de p\u00e9rim\u00e8tre pendant un Sprint, et l'\u00c9quipe de D\u00e9veloppement doit les accommoder.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Faux",
        explanation: "Aucun changement ne devrait \u00eatre effectu\u00e9 qui pourrait compromettre l'Objectif du Sprint pendant un Sprint. Les parties prenantes devraient respecter la concentration de l'\u00e9quipe et soumettre les nouvelles demandes pour la prochaine Planification du Sprint.",
        lessonContext: "",
      },
    ],

    // ── MODULE 4 QUIZ: Scrum Events and Artifacts ──────────────────────────
    "mod-4": [
      {
        questionId: "as-m4-q1",
        type: "multiple-choice",
        questionText: "Quelle est la dur\u00e9e maximale d'un Sprint dans Scrum?",
        options: ["Une semaine", "Deux semaines", "Un mois", "Trois mois"],
        correctAnswer: "Un mois",
        explanation: "Un Sprint est une bo\u00eete de temps d'un mois ou moins. La plupart des \u00e9quipes de d\u00e9veloppement utilisent des Sprints de 1 \u00e0 2 semaines, mais le Guide Scrum permet jusqu'\u00e0 un mois.",
        lessonContext: "",
      },
      {
        questionId: "as-m4-q2",
        type: "multiple-choice",
        questionText: "Quels sont les trois sujets abord\u00e9s pendant la Planification du Sprint?",
        options: [
          "Ce qui a \u00e9t\u00e9 fait, ce qui n'a pas fonctionn\u00e9, quoi am\u00e9liorer",
          "Pourquoi (valeur), Quoi (p\u00e9rim\u00e8tre), Comment (plan)",
          "Qui travaille, quand cela finira, o\u00f9 d\u00e9ployer",
          "Budget, \u00e9ch\u00e9ancier, ressources",
        ],
        correctAnswer: "Pourquoi (valeur), Quoi (p\u00e9rim\u00e8tre), Comment (plan)",
        explanation: "La Planification du Sprint aborde trois sujets : Pourquoi ce Sprint est-il pr\u00e9cieux (Objectif du Sprint)? Qu'est-ce qui peut \u00eatre fait (p\u00e9rim\u00e8tre)? Comment le travail choisi sera-t-il r\u00e9alis\u00e9 (plan)?",
        lessonContext: "",
      },
      {
        questionId: "as-m4-q3",
        type: "true-false",
        questionText: "La M\u00eal\u00e9e quotidienne est avant tout un rapport d'\u00e9tat \u00e0 la direction sur les progr\u00e8s individuels des membres de l'\u00e9quipe.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Faux",
        explanation: "La M\u00eal\u00e9e quotidienne est un \u00e9v\u00e9nement de planification pour que l'\u00c9quipe de D\u00e9veloppement inspecte les progr\u00e8s vers l'Objectif du Sprint. Ce n'est pas un rapport d'\u00e9tat \u00e0 la direction.",
        lessonContext: "",
      },
      {
        questionId: "as-m4-q4",
        type: "multiple-choice",
        questionText: "Quelle est la bo\u00eete de temps maximale pour une M\u00eal\u00e9e quotidienne?",
        options: ["5 minutes", "15 minutes", "30 minutes", "1 heure"],
        correctAnswer: "15 minutes",
        explanation: "La M\u00eal\u00e9e quotidienne est limit\u00e9e \u00e0 15 minutes. Elle a lieu au m\u00eame endroit et \u00e0 la m\u00eame heure chaque jour du Sprint.",
        lessonContext: "",
      },
      {
        questionId: "as-m4-q5",
        type: "true-false",
        questionText: "La Revue du Sprint devrait \u00eatre trait\u00e9e comme une r\u00e9union de d\u00e9monstration uniquement o\u00f9 l'\u00e9quipe pr\u00e9sente le travail termin\u00e9.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Faux",
        explanation: "La Revue du Sprint est une session de travail, pas une d\u00e9mo. L'\u00e9quipe et les parties prenantes collaborent pour inspecter ce qui a \u00e9t\u00e9 construit et ajuster les priorit\u00e9s. Cela devrait ressembler \u00e0 une conversation, pas \u00e0 une pr\u00e9sentation.",
        lessonContext: "",
      },
      {
        questionId: "as-m4-q6",
        type: "multiple-choice",
        questionText: "Quel est le pi\u00e8ge le plus courant des R\u00e9trospectives de Sprint?",
        options: [
          "Elles prennent trop de temps",
          "Elles ne produisent aucune am\u00e9lioration r\u00e9alisable",
          "Le Scrum Master parle trop",
          "Les parties prenantes assistent et dominent la conversation",
        ],
        correctAnswer: "Elles ne produisent aucune am\u00e9lioration r\u00e9alisable",
        explanation: "Le pi\u00e8ge le plus courant est d'avoir une excellente conversation mais de ne prendre aucune mesure. Chaque R\u00e9trospective devrait produire au moins une am\u00e9lioration r\u00e9alisable \u00e0 laquelle l'\u00e9quipe s'engage.",
        lessonContext: "",
      },
      {
        questionId: "as-m4-q7",
        type: "multiple-choice",
        questionText: "Quel artefact Scrum est une liste ordonn\u00e9e de tout ce qui pourrait \u00eatre n\u00e9cessaire dans le produit?",
        options: ["Backlog du Sprint", "Backlog du produit", "Incr\u00e9ment", "Plan de livraison"],
        correctAnswer: "Backlog du produit",
        explanation: "Le Backlog du produit est une liste ordonn\u00e9e de tout ce qui pourrait \u00eatre n\u00e9cessaire dans le produit. C'est la source unique des exigences et il \u00e9volue \u00e0 mesure que le produit et le march\u00e9 changent.",
        lessonContext: "",
      },
      {
        questionId: "as-m4-q8",
        type: "multiple-choice",
        questionText: "Que repr\u00e9sente la 'D\u00e9finition de Fini' dans Scrum?",
        options: [
          "Quand un Sprint est termin\u00e9",
          "Une description formelle du moment o\u00f9 un Incr\u00e9ment r\u00e9pond aux mesures de qualit\u00e9",
          "La liste des fonctionnalit\u00e9s \u00e0 construire dans la prochaine version",
          "Une approbation du Gestionnaire de projet",
        ],
        correctAnswer: "Une description formelle du moment o\u00f9 un Incr\u00e9ment r\u00e9pond aux mesures de qualit\u00e9",
        explanation: "La D\u00e9finition de Fini est une description formelle de l'\u00e9tat de l'Incr\u00e9ment lorsqu'il r\u00e9pond aux mesures de qualit\u00e9 requises pour le produit. Si le travail ne r\u00e9pond pas \u00e0 la DoD, il ne peut pas \u00eatre livr\u00e9.",
        lessonContext: "",
      },
      {
        questionId: "as-m4-q9",
        type: "multiple-choice",
        questionText: "Qui poss\u00e8de le Backlog du Sprint et peut le modifier pendant le Sprint?",
        options: ["Product Owner", "Scrum Master", "\u00c9quipe de D\u00e9veloppement", "Parties prenantes"],
        correctAnswer: "\u00c9quipe de D\u00e9veloppement",
        explanation: "Le Backlog du Sprint appartient \u00e0 l'\u00c9quipe de D\u00e9veloppement — seuls ses membres peuvent le modifier pendant le Sprint. Il est mis \u00e0 jour tout au long du Sprint \u00e0 mesure que l'\u00e9quipe en apprend davantage sur le travail n\u00e9cessaire.",
        lessonContext: "",
      },
      {
        questionId: "as-m4-q10",
        type: "true-false",
        questionText: "Un \u00e9l\u00e9ment du Backlog du produit qui n'a pas satisfait \u00e0 la D\u00e9finition de Fini peut encore \u00eatre pr\u00e9sent\u00e9 lors de la Revue du Sprint.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Faux",
        explanation: "Si un \u00e9l\u00e9ment du Backlog du produit ne r\u00e9pond pas \u00e0 la DoD, il ne peut pas \u00eatre livr\u00e9 ou pr\u00e9sent\u00e9 lors de la Revue du Sprint. La D\u00e9finition de Fini garantit des normes de qualit\u00e9 coh\u00e9rentes.",
        lessonContext: "",
      },
    ],

    // ── MODULE 5 QUIZ: Agile Testing and Continuous Integration ────────────
    "mod-5": [
      {
        questionId: "as-m5-q1",
        type: "multiple-choice",
        questionText: "Selon les Quadrants de tests Agile, quel type de test soutient l'\u00e9quipe et est orient\u00e9 technologie?",
        options: ["Tests exploratoires", "Tests unitaires et tests de composants", "Tests d'utilisabilit\u00e9", "Tests de performance"],
        correctAnswer: "Tests unitaires et tests de composants",
        explanation: "Le Quadrant 1 est orient\u00e9 technologie et soutient l'\u00e9quipe — cela inclut les tests unitaires et les tests de composants. Ces tests aident les d\u00e9veloppeurs \u00e0 int\u00e9grer la qualit\u00e9 dans le produit d\u00e8s le d\u00e9part.",
        lessonContext: "",
      },
      {
        questionId: "as-m5-q2",
        type: "multiple-choice",
        questionText: "Quel est l'ordre correct des \u00e9tapes du D\u00e9veloppement pilot\u00e9 par les tests (TDD)?",
        options: [
          "\u00c9crire le code \u2192 \u00c9crire les tests \u2192 Refactoriser",
          "\u00c9crire un test qui \u00e9choue \u2192 \u00c9crire le minimum de code pour passer \u2192 Refactoriser",
          "Concevoir \u2192 Coder \u2192 Tester \u2192 D\u00e9ployer",
          "\u00c9crire tous les tests \u2192 \u00c9crire tout le code \u2192 V\u00e9rifier",
        ],
        correctAnswer: "\u00c9crire un test qui \u00e9choue \u2192 \u00c9crire le minimum de code pour passer \u2192 Refactoriser",
        explanation: "Le cycle TDD est Rouge (\u00e9crire un test qui \u00e9choue) \u2192 Vert (\u00e9crire le minimum de code pour passer) \u2192 Refactor (nettoyer le code tout en gardant les tests au vert).",
        lessonContext: "",
      },
      {
        questionId: "as-m5-q3",
        type: "true-false",
        questionText: "L'int\u00e9gration continue exige que les d\u00e9veloppeurs fusionnent les changements de code dans un r\u00e9f\u00e9rentiel partag\u00e9 plusieurs fois par jour.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Vrai",
        explanation: "L'IC est une pratique o\u00f9 les d\u00e9veloppeurs fusionnent les changements de code fr\u00e9quemment — id\u00e9alement plusieurs fois par jour. Chaque fusion d\u00e9clenche une s\u00e9quence automatis\u00e9e de construction et de test.",
        lessonContext: "",
      },
      {
        questionId: "as-m5-q4",
        type: "multiple-choice",
        questionText: "Selon la Pyramide d'automatisation des tests, quel type de tests devrait \u00eatre le plus nombreux?",
        options: ["Tests UI/de bout en bout", "Tests d'int\u00e9gration", "Tests unitaires", "Tests manuels"],
        correctAnswer: "Tests unitaires",
        explanation: "La Pyramide d'automatisation des tests recommande beaucoup de tests unitaires (base), quelques tests d'int\u00e9gration (milieu) et peu de tests UI/de bout en bout (sommet). Les tests unitaires sont rapides et fournissent une r\u00e9troaction rapide.",
        lessonContext: "",
      },
      {
        questionId: "as-m5-q5",
        type: "true-false",
        questionText: "Dans Agile, tous les tests devraient \u00eatre automatis\u00e9s pour atteindre une efficacit\u00e9 maximale.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Faux",
        explanation: "Les tests manuels sont essentiels pour les tests exploratoires, les tests d'utilisabilit\u00e9, les v\u00e9rifications visuelles et les nouveaux cas limites. Une strat\u00e9gie \u00e9quilibr\u00e9e utilise \u00e0 la fois des tests automatis\u00e9s et manuels de fa\u00e7on appropri\u00e9e.",
        lessonContext: "",
      },
      {
        questionId: "as-m5-q6",
        type: "multiple-choice",
        questionText: "Que signifie 'shift left' dans les tests Agile?",
        options: [
          "Reporter les tests \u00e0 la fin du projet",
          "D\u00e9placer les activit\u00e9s de test plus t\u00f4t dans le processus de d\u00e9veloppement",
          "Transf\u00e9rer la responsabilit\u00e9 de l'AQ aux d\u00e9veloppeurs",
          "Utiliser uniquement des outils de test automatis\u00e9s",
        ],
        correctAnswer: "D\u00e9placer les activit\u00e9s de test plus t\u00f4t dans le processus de d\u00e9veloppement",
        explanation: "'Shift left' signifie tester plus t\u00f4t dans le processus de d\u00e9veloppement pour r\u00e9duire le co\u00fbt des d\u00e9fauts. Cela implique des tests automatis\u00e9s, des tests manuels pr\u00e9coces et l'implication de l'AQ d\u00e8s le d\u00e9but du Sprint.",
        lessonContext: "",
      },
    ],

    // ── MODULE 6 QUIZ: Scaling Agile ───────────────────────────────────────
    "mod-6": [
      {
        questionId: "as-m6-q1",
        type: "multiple-choice",
        questionText: "Quel est le principal objectif d'une r\u00e9union Scrum of Scrums?",
        options: [
          "Faire rapport de l'\u00e9tat individuel des membres aux cadres sup\u00e9rieurs",
          "Coordonner les d\u00e9pendances inter-\u00e9quipes et r\u00e9soudre les probl\u00e8mes d'int\u00e9gration",
          "Remplacer les M\u00eal\u00e9es quotidiennes individuelles des \u00e9quipes",
          "Planifier l'ensemble de la feuille de route du produit",
        ],
        correctAnswer: "Coordonner les d\u00e9pendances inter-\u00e9quipes et r\u00e9soudre les probl\u00e8mes d'int\u00e9gration",
        explanation: "Scrum of Scrums coordonne plusieurs \u00e9quipes Scrum en faisant discuter des ambassadeurs de chaque \u00e9quipe des pr\u00e9occupations inter-\u00e9quipes, des d\u00e9pendances et des probl\u00e8mes de coordination.",
        lessonContext: "",
      },
      {
        questionId: "as-m6-q2",
        type: "multiple-choice",
        questionText: "Qu'est-ce qu'un Agile Release Train (ART) dans SAFe?",
        options: [
          "Un train physique utilis\u00e9 pour des exercices de consolidation d'\u00e9quipe",
          "Une \u00e9quipe durable d'\u00e9quipes Agile (50-125 personnes) qui planifie et ex\u00e9cute ensemble",
          "Un outil pour automatiser les d\u00e9ploiements",
          "Un programme de certification pour les Scrum Masters",
        ],
        correctAnswer: "Une \u00e9quipe durable d'\u00e9quipes Agile (50-125 personnes) qui planifie et ex\u00e9cute ensemble",
        explanation: "Un ART dans SAFe est un groupe de 50 \u00e0 125 personnes compos\u00e9 de plusieurs \u00e9quipes Agile qui travaillent ensemble sur la m\u00eame solution. Les ART planifient ensemble lors des \u00e9v\u00e9nements de Planification PI.",
        lessonContext: "",
      },
      {
        questionId: "as-m6-q3",
        type: "multiple-choice",
        questionText: "En quoi LeSS (Large-Scale Scrum) diff\u00e8re-t-il de SAFe dans son approche de mise \u00e0 l'\u00e9chelle?",
        options: [
          "LeSS ajoute plus de r\u00f4les et d'\u00e9v\u00e9nements que SAFe",
          "LeSS supprime autant de processus que possible, restant proche du Scrum standard",
          "LeSS est con\u00e7u uniquement pour des contextes non logiciels",
          "LeSS exige que toutes les \u00e9quipes utilisent Kanban au lieu de Scrum",
        ],
        correctAnswer: "LeSS supprime autant de processus que possible, restant proche du Scrum standard",
        explanation: "LeSS est une approche de mise \u00e0 l'\u00e9chelle minimaliste — il commence par Scrum standard et n'ajoute que ce qui est absolument n\u00e9cessaire pour la coordination. SAFe ajoute plus de structure, de r\u00f4les et d'\u00e9v\u00e9nements.",
        lessonContext: "",
      },
      {
        questionId: "as-m6-q4",
        type: "true-false",
        questionText: "Une organisation devrait adopter un cadre de mise \u00e0 l'\u00e9chelle d\u00e8s qu'elle commence \u00e0 utiliser Scrum, m\u00eame avec une seule \u00e9quipe.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Faux",
        explanation: "Les organisations devraient ma\u00eetriser Scrum avec une seule \u00e9quipe avant de passer \u00e0 l'\u00e9chelle. Passer \u00e0 l'\u00e9chelle avant de comprendre les bases de Scrum conduit \u00e0 une complexit\u00e9 inutile et \u00e0 des pratiques 'cargo-cult' Agile.",
        lessonContext: "",
      },
      {
        questionId: "as-m6-q5",
        type: "multiple-choice",
        questionText: "Que sugg\u00e8re la Loi de Conway concernant les impl\u00e9mentations Agile \u00e0 grande \u00e9chelle?",
        options: [
          "Les grandes \u00e9quipes produisent toujours de meilleurs logiciels",
          "Les organisations con\u00e7oivent des syst\u00e8mes qui refl\u00e8tent leur structure de communication",
          "La mise \u00e0 l'\u00e9chelle devrait toujours suivre le mod\u00e8le Spotify",
          "Agile ne fonctionne pas pour les organisations de plus de 100 personnes",
        ],
        correctAnswer: "Les organisations con\u00e7oivent des syst\u00e8mes qui refl\u00e8tent leur structure de communication",
        explanation: "La Loi de Conway stipule que les organisations con\u00e7oivent des syst\u00e8mes qui refl\u00e8tent leur structure de communication. Si une approche Agile \u00e0 grande \u00e9chelle n\u00e9cessite une coordination complexe, demandez-vous si des changements de structure d'\u00e9quipe pourraient r\u00e9soudre le probl\u00e8me plus directement.",
        lessonContext: "",
      },
      {
        questionId: "as-m6-q6",
        type: "multiple-choice",
        questionText: "Lequel des \u00e9l\u00e9ments suivants est un signe que vous ne devriez PAS encore passer \u00e0 l'\u00e9chelle Agile?",
        options: [
          "Votre produit n\u00e9cessite plus de 9 personnes par \u00e9quipe",
          "Plusieurs \u00e9quipes travaillent sur la m\u00eame base de code",
          "Votre \u00e9quipe unique apprend encore les bases de Scrum",
          "Les d\u00e9pendances inter-\u00e9quipes causent des retards",
        ],
        correctAnswer: "Votre \u00e9quipe unique apprend encore les bases de Scrum",
        explanation: "Les signes indiquant qu'il ne faut pas encore passer \u00e0 l'\u00e9chelle incluent : l'\u00e9quipe apprend encore les bases de Scrum, l'absence de D\u00e9finition de Fini stable, des Revues de Sprint/R\u00e9tro non productives, et une direction qui utilise encore le commandement et contr\u00f4le.",
        lessonContext: "",
      },
    ],

    // ── MODULE 7 QUIZ: Agile Metrics and Monitoring Progress ────────────────
    "mod-7": [
      {
        questionId: "as-m7-q1",
        type: "multiple-choice",
        questionText: "Qu'est-ce que la v\u00e9locit\u00e9 dans Scrum?",
        options: [
          "La rapidit\u00e9 avec laquelle les d\u00e9veloppeurs individuels \u00e9crivent du code",
          "La quantit\u00e9 de travail qu'une \u00e9quipe termine dans un Sprint, mesur\u00e9e en story points",
          "Le nombre de bogues trouv\u00e9s par jour",
          "La vitesse du pipeline CI/CD",
        ],
        correctAnswer: "La quantit\u00e9 de travail qu'une \u00e9quipe termine dans un Sprint, mesur\u00e9e en story points",
        explanation: "La v\u00e9locit\u00e9 est la somme des story points de tous les \u00e9l\u00e9ments termin\u00e9s du Backlog du produit dans un Sprint. Elle est utilis\u00e9e pour les pr\u00e9visions de planification, pas comme m\u00e9trique de performance.",
        lessonContext: "",
      },
      {
        questionId: "as-m7-q2",
        type: "true-false",
        questionText: "Il est appropri\u00e9 de comparer la v\u00e9locit\u00e9 entre diff\u00e9rentes \u00e9quipes pour d\u00e9terminer quelle \u00e9quipe est la plus productive.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Faux",
        explanation: "Les story points sont sp\u00e9cifiques \u00e0 chaque \u00e9quipe et ne peuvent pas \u00eatre compar\u00e9s entre \u00e9quipes. Utiliser la v\u00e9locit\u00e9 pour comparer les \u00e9quipes est insens\u00e9 et cr\u00e9e une comp\u00e9tition destructive.",
        lessonContext: "",
      },
      {
        questionId: "as-m7-q3",
        type: "multiple-choice",
        questionText: "Que montre un graphique burndown?",
        options: [
          "Le travail termin\u00e9 au fil du temps, avec deux lignes pour le p\u00e9rim\u00e8tre total et termin\u00e9",
          "Le travail restant au fil du temps, avec une ligne de tendance id\u00e9ale descendant vers z\u00e9ro \u00e0 la fin du Sprint",
          "Le travail dans chaque \u00e9tat du flux de travail au fil du temps",
          "La disponibilit\u00e9 des membres de l'\u00e9quipe et les jours de vacances",
        ],
        correctAnswer: "Le travail restant au fil du temps, avec une ligne de tendance id\u00e9ale descendant vers z\u00e9ro \u00e0 la fin du Sprint",
        explanation: "Un graphique burndown montre l'effort restant (axe Y) au fil du temps (axe X). La ligne id\u00e9ale descend du coin sup\u00e9rieur gauche au coin inf\u00e9rieur droit. La ligne r\u00e9elle montre les progr\u00e8s r\u00e9els.",
        lessonContext: "",
      },
      {
        questionId: "as-m7-q4",
        type: "multiple-choice",
        questionText: "Quelle est la diff\u00e9rence entre le d\u00e9lai d'ex\u00e9cution (lead time) et le temps de cycle (cycle time)?",
        options: [
          "Le d\u00e9lai d'ex\u00e9cution se mesure en heures; le temps de cycle se mesure en jours",
          "Le d\u00e9lai d'ex\u00e9cution commence quand le travail est demand\u00e9; le temps de cycle commence quand le travail commence",
          "Le d\u00e9lai d'ex\u00e9cution est pour Kanban; le temps de cycle est pour Scrum",
          "Il n'y a pas de diff\u00e9rence — les termes sont interchangeables",
        ],
        correctAnswer: "Le d\u00e9lai d'ex\u00e9cution commence quand le travail est demand\u00e9; le temps de cycle commence quand le travail commence",
        explanation: "Le d\u00e9lai d'ex\u00e9cution mesure le temps total de la demande \u00e0 la livraison (exp\u00e9rience client). Le temps de cycle mesure le temps entre le d\u00e9but r\u00e9el du travail et son ach\u00e8vement (efficacit\u00e9 de l'\u00e9quipe).",
        lessonContext: "",
      },
      {
        questionId: "as-m7-q5",
        type: "multiple-choice",
        questionText: "Selon la Loi de Little, comment une \u00e9quipe peut-elle r\u00e9duire le temps de cycle?",
        options: [
          "Augmenter la taille de l'\u00e9quipe",
          "R\u00e9duire le travail en cours (WIP)",
          "Travailler plus d'heures",
          "Sauter la D\u00e9finition de Fini",
        ],
        correctAnswer: "R\u00e9duire le travail en cours (WIP)",
        explanation: "La Loi de Little stipule : Temps de cycle = WIP / D\u00e9bit. La r\u00e9duction du WIP est le levier le plus efficace pour r\u00e9duire le temps de cycle, car le d\u00e9bit est difficile \u00e0 augmenter.",
        lessonContext: "",
      },
      {
        questionId: "as-m7-q6",
        type: "multiple-choice",
        questionText: "Qu'indique une bande qui s'\u00e9largit dans un Diagramme de flux cumul\u00e9?",
        options: [
          "L'\u00e9quipe livre plus rapidement que pr\u00e9vu",
          "Un goulot d'\u00e9tranglement se forme dans cet \u00e9tat du flux de travail",
          "L'\u00e9quipe a besoin de plus de personnes",
          "Le projet est en avance sur le calendrier",
        ],
        correctAnswer: "Un goulot d'\u00e9tranglement se forme dans cet \u00e9tat du flux de travail",
        explanation: "Des bandes qui s'\u00e9largissent dans un CFD indiquent une augmentation du WIP dans un \u00e9tat particulier. Par exemple, si 'En test' s'\u00e9largit constamment, les tests sont probablement un goulot d'\u00e9tranglement.",
        lessonContext: "",
      },
    ],

    // ── MODULE 8 QUIZ: Advanced Topics in Agile ─────────────────────────────
    "mod-8": [
      {
        questionId: "as-m8-q1",
        type: "multiple-choice",
        questionText: "Pourquoi les contrats traditionnels \u00e0 prix fixe et p\u00e9rim\u00e8tre fixe sont-ils probl\u00e9matiques pour les projets Agile?",
        options: [
          "Ils co\u00fbtent trop d'argent",
          "Ils supposent que les exigences peuvent \u00eatre enti\u00e8rement d\u00e9finies \u00e0 l'avance, ce qui contredit l'acceptation du changement par Agile",
          "Ils n\u00e9cessitent trop de paperasse",
          "Ils n'incluent pas de clause de r\u00e9siliation",
        ],
        correctAnswer: "Ils supposent que les exigences peuvent \u00eatre enti\u00e8rement d\u00e9finies \u00e0 l'avance, ce qui contredit l'acceptation du changement par Agile",
        explanation: "Les contrats \u00e0 prix fixe et p\u00e9rim\u00e8tre fixe supposent que toutes les exigences sont connues \u00e0 l'avance. Agile accepte les changements d'exigences et la d\u00e9couverte it\u00e9rative, ce qui entre en conflit avec ce mod\u00e8le.",
        lessonContext: "",
      },
      {
        questionId: "as-m8-q2",
        type: "multiple-choice",
        questionText: "Quel mod\u00e8le de contrat Agile permet au client d'annuler t\u00f4t et d'ajouter du p\u00e9rim\u00e8tre sans p\u00e9nalit\u00e9?",
        options: ["Temps et mat\u00e9riel", "Prix fixe + it\u00e9ratif", "Argent pour rien, changement gratuit", "Bas\u00e9 sur les r\u00e9sultats"],
        correctAnswer: "Argent pour rien, changement gratuit",
        explanation: "Dans ce mod\u00e8le, le client peut annuler t\u00f4t (en payant des frais de r\u00e9siliation) ou ajouter du p\u00e9rim\u00e8tre sans p\u00e9nalit\u00e9. Le fournisseur est incit\u00e9 \u00e0 livrer de la valeur t\u00f4t et \u00e0 s'adapter aux changements de fa\u00e7on flexible.",
        lessonContext: "",
      },
      {
        questionId: "as-m8-q3",
        type: "true-false",
        questionText: "Agile a \u00e9t\u00e9 con\u00e7u exclusivement pour des \u00e9quipes co-localis\u00e9es et ne peut pas \u00eatre adapt\u00e9 au travail \u00e0 distance ou distribu\u00e9.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Faux",
        explanation: "Bien qu'Agile ait \u00e9t\u00e9 con\u00e7u \u00e0 l'origine pour des \u00e9quipes co-localis\u00e9es, il peut fonctionner \u00e0 distance avec des adaptations d\u00e9lib\u00e9r\u00e9es : surcommunication, c\u00e9r\u00e9monies vid\u00e9o, boucles de r\u00e9troaction asynchrones et temps social virtuel.",
        lessonContext: "",
      },
      {
        questionId: "as-m8-q4",
        type: "multiple-choice",
        questionText: "Quel est le principal d\u00e9fi des \u00e9quipes Agile distribu\u00e9es mentionn\u00e9 dans le cours?",
        options: [
          "Des co\u00fbts d'infrastructure plus \u00e9lev\u00e9s",
          "Un d\u00e9calage de communication d\u00fb au manque de conversation en face \u00e0 face",
          "La difficult\u00e9 \u00e0 trouver des d\u00e9veloppeurs qualifi\u00e9s",
          "L'incapacit\u00e9 \u00e0 utiliser Scrum du tout",
        ],
        correctAnswer: "Un d\u00e9calage de communication d\u00fb au manque de conversation en face \u00e0 face",
        explanation: "Le Principe #6 stipule que la conversation en face \u00e0 face est la m\u00e9thode la plus efficace. La communication textuelle a une bande passante plus faible, ce qui rend plus difficile la transmission des nuances et l'\u00e9tablissement de la confiance.",
        lessonContext: "",
      },
      {
        questionId: "as-m8-q5",
        type: "true-false",
        questionText: "DevOps est une m\u00e9thodologie distincte qui remplace les principes Agile dans les op\u00e9rations et l'infrastructure.",
        options: ["Vrai", "Faux"],
        correctAnswer: "Faux",
        explanation: "DevOps est une extension naturelle des principes Agile dans les op\u00e9rations. Il abat les murs entre le d\u00e9veloppement et les op\u00e9rations, tout comme Agile a abattu les murs entre les affaires et le d\u00e9veloppement.",
        lessonContext: "",
      },
      {
        questionId: "as-m8-q6",
        type: "multiple-choice",
        questionText: "Laquelle des 'Trois voies de DevOps' se concentre sur l'optimisation du flux de travail du d\u00e9veloppement aux op\u00e9rations jusqu'au client?",
        options: ["Flux", "R\u00e9troaction", "Apprentissage continu", "Automatisation"],
        correctAnswer: "Flux",
        explanation: "La Premi\u00e8re voie (Flux) optimise le flux de travail du d\u00e9veloppement aux op\u00e9rations jusqu'au client gr\u00e2ce \u00e0 de petits lots, des transferts r\u00e9duits et des pipelines de d\u00e9ploiement automatis\u00e9s.",
        lessonContext: "",
      },
    ],

    // ── FINAL EXAM: Comprehensive Course Assessment ────────────────────────
    "final-exam": [
      {
        questionId: "as-fe-q1",
        type: "multiple-choice",
        questionText: "Laquelle des propositions suivantes d\u00e9crit le mieux la vision du Manifeste Agile concernant les processus et les outils?",
        options: [
          "Les processus et les outils sont plus importants que les personnes",
          "Les individus et leurs interactions sont valoris\u00e9s plus que les processus et les outils",
          "Les processus et les outils devraient \u00eatre enti\u00e8rement \u00e9limin\u00e9s",
          "Seuls les outils automatis\u00e9s devraient \u00eatre utilis\u00e9s",
        ],
        correctAnswer: "Les individus et leurs interactions sont valoris\u00e9s plus que les processus et les outils",
        explanation: "La premi\u00e8re valeur du Manifeste Agile stipule : 'Les individus et leurs interactions plus que les processus et les outils.' Les personnes et la collaboration sont prioritaires sur les processus rigides.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q2",
        type: "multiple-choice",
        questionText: "Quels sont les trois piliers de Scrum?",
        options: [
          "Planification, Ex\u00e9cution, R\u00e9vision",
          "Transparence, Inspection, Adaptation",
          "R\u00f4les, \u00c9v\u00e9nements, Artefacts",
          "Produit, Sprint, \u00c9quipe",
        ],
        correctAnswer: "Transparence, Inspection, Adaptation",
        explanation: "Les trois piliers de Scrum sont la Transparence (visibilit\u00e9), l'Inspection (v\u00e9rifications fr\u00e9quentes) et l'Adaptation (ajustements bas\u00e9s sur l'inspection). Ils soutiennent le contr\u00f4le empirique des processus de Scrum.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q3",
        type: "multiple-choice",
        questionText: "Une \u00e9quipe adopte toutes les c\u00e9r\u00e9monies Scrum — m\u00eal\u00e9es quotidiennes, revues de sprint, r\u00e9trospectives — mais la direction continue d'assigner les t\u00e2ches et de dicter les priorit\u00e9s. Comment cela s'appelle-t-il?",
        options: ["Scrum efficace", "Cargo-cult Agile", "Gestion Lean", "Agile \u00e0 grande \u00e9chelle"],
        correctAnswer: "Cargo-cult Agile",
        explanation: "Adopter les c\u00e9r\u00e9monies sans adopter les valeurs sous-jacentes de confiance, d'autonomisation et d'autogestion est connu sous le nom de 'cargo-cult Agile.' La v\u00e9ritable agilit\u00e9 n\u00e9cessite un changement d'\u00e9tat d'esprit, pas seulement une adoption m\u00e9canique des pratiques.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q4",
        type: "multiple-choice",
        questionText: "Dans Scrum, qui d\u00e9cide du nombre d'\u00e9l\u00e9ments du Backlog du produit \u00e0 inclure dans un Sprint?",
        options: ["Product Owner", "Scrum Master", "\u00c9quipe de D\u00e9veloppement", "Gestionnaire de projet"],
        correctAnswer: "\u00c9quipe de D\u00e9veloppement",
        explanation: "L'\u00c9quipe de D\u00e9veloppement s\u00e9lectionne les \u00e9l\u00e9ments qu'elle croit pouvoir terminer dans un Sprint. L'\u00e9quipe — pas le PO ni un gestionnaire — fait cette s\u00e9lection en fonction des performances pass\u00e9es et de la capacit\u00e9.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q5",
        type: "multiple-choice",
        questionText: "Qu'est-ce qui distingue Kanban de Scrum le plus fondamentalement?",
        options: [
          "Kanban a plus de r\u00f4les que Scrum",
          "Kanban utilise un flux continu sans it\u00e9rations de dur\u00e9e fixe; Scrum utilise des Sprints avec bo\u00eete de temps",
          "Kanban est uniquement pour la fabrication, pas pour les logiciels",
          "Kanban ne visualise pas le flux de travail",
        ],
        correctAnswer: "Kanban utilise un flux continu sans it\u00e9rations de dur\u00e9e fixe; Scrum utilise des Sprints avec bo\u00eete de temps",
        explanation: "La diff\u00e9rence la plus fondamentale est que Scrum enferme le travail dans des Sprints de dur\u00e9e fixe, tandis que Kanban utilise un flux continu avec des limites WIP mais sans limites d'it\u00e9ration prescrites.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q6",
        type: "multiple-choice",
        questionText: "Quel est le principal avantage du D\u00e9veloppement pilot\u00e9 par les tests (TDD)?",
        options: [
          "\u00c9liminer le besoin de tests manuels",
          "Am\u00e9liorer la conception du code en obligeant les d\u00e9veloppeurs \u00e0 penser aux interfaces avant l'impl\u00e9mentation",
          "R\u00e9duire le nombre de d\u00e9veloppeurs n\u00e9cessaires dans une \u00e9quipe",
          "Supprimer le besoin d'une D\u00e9finition de Fini",
        ],
        correctAnswer: "Am\u00e9liorer la conception du code en obligeant les d\u00e9veloppeurs \u00e0 penser aux interfaces avant l'impl\u00e9mentation",
        explanation: "Le TDD est avant tout une technique de conception. \u00c9crire les tests d'abord oblige les d\u00e9veloppeurs \u00e0 consid\u00e9rer les interfaces, les contrats et le comportement avant l'impl\u00e9mentation, ce qui conduit \u00e0 un code plus propre et plus modulaire.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q7",
        type: "multiple-choice",
        questionText: "Quel \u00e9v\u00e9nement Scrum est explicitement ax\u00e9 sur le 'comment' l'\u00e9quipe peut am\u00e9liorer son processus?",
        options: ["Planification du Sprint", "M\u00eal\u00e9e quotidienne", "Revue du Sprint", "R\u00e9trospective du Sprint"],
        correctAnswer: "R\u00e9trospective du Sprint",
        explanation: "La R\u00e9trospective du Sprint est l'\u00e9v\u00e9nement o\u00f9 l'\u00e9quipe inspecte comment le dernier Sprint s'est d\u00e9roul\u00e9 concernant les personnes, les relations, les processus et les outils, et cr\u00e9e un plan d'am\u00e9lioration.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q8",
        type: "multiple-choice",
        questionText: "Un \u00e9l\u00e9ment du Backlog du produit devrait \u00eatre consid\u00e9r\u00e9 comme 'Fini' quand :",
        options: [
          "Le d\u00e9veloppeur dit que c'est termin\u00e9",
          "Il r\u00e9pond \u00e0 la D\u00e9finition de Fini de l'\u00e9quipe",
          "Le Product Owner approuve la conception",
          "Tous les tests r\u00e9ussissent",
        ],
        correctAnswer: "Il r\u00e9pond \u00e0 la D\u00e9finition de Fini de l'\u00e9quipe",
        explanation: "La D\u00e9finition de Fini est une description formelle des mesures de qualit\u00e9. Un \u00e9l\u00e9ment est Fini seulement lorsqu'il r\u00e9pond \u00e0 tous les crit\u00e8res de la DoD, ce qui peut inclure la r\u00e9vision de code, les tests, la documentation et l'acceptation du PO.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q9",
        type: "multiple-choice",
        questionText: "\u00c0 quoi sert le mieux la v\u00e9locit\u00e9 dans Scrum?",
        options: [
          "\u00c0 \u00e9valuer la performance individuelle des d\u00e9veloppeurs",
          "\u00c0 comparer la productivit\u00e9 des \u00e9quipes",
          "\u00c0 pr\u00e9voir la quantit\u00e9 de travail qu'une \u00e9quipe peut terminer dans les Sprints futurs",
          "\u00c0 d\u00e9terminer les salaires des d\u00e9veloppeurs",
        ],
        correctAnswer: "\u00c0 pr\u00e9voir la quantit\u00e9 de travail qu'une \u00e9quipe peut terminer dans les Sprints futurs",
        explanation: "La v\u00e9locit\u00e9 est un outil de pr\u00e9vision, pas une m\u00e9trique de performance. Une v\u00e9locit\u00e9 stable aide l'\u00e9quipe \u00e0 pr\u00e9voir la capacit\u00e9 future du Sprint lors de la Planification du Sprint.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q10",
        type: "multiple-choice",
        questionText: "Quelle approche de mise \u00e0 l'\u00e9chelle conserve les trois r\u00f4les Scrum (PO, SM, D\u00e9veloppeurs) et ajoute un minimum de processus suppl\u00e9mentaire?",
        options: ["SAFe", "LeSS", "Scrum of Scrums seulement", "Cascade"],
        correctAnswer: "LeSS",
        explanation: "LeSS (Large-Scale Scrum) conserve les trois r\u00f4les Scrum et ajoute aussi peu de processus suppl\u00e9mentaire que possible. Il met les \u00e9v\u00e9nements \u00e0 l'\u00e9chelle plut\u00f4t que d'ajouter de nouveaux r\u00f4les ou couches.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q11",
        type: "multiple-choice",
        questionText: "Dans le mod\u00e8le de contrat 'Argent pour rien, changement gratuit', quelle incitation le fournisseur a-t-il?",
        options: [
          "Livrer le plus lentement possible pour maximiser les heures facturables",
          "Livrer de la valeur t\u00f4t pour que le client puisse annuler t\u00f4t, gagnant ainsi une marge plus \u00e9lev\u00e9e",
          "\u00c9viter tout changement de p\u00e9rim\u00e8tre",
          "Se concentrer sur la documentation plut\u00f4t que sur un logiciel fonctionnel",
        ],
        correctAnswer: "Livrer de la valeur t\u00f4t pour que le client puisse annuler t\u00f4t, gagnant ainsi une marge plus \u00e9lev\u00e9e",
        explanation: "Le fournisseur gagne une marge plus \u00e9lev\u00e9e si le client annule t\u00f4t (argent pour rien), ce qui incite \u00e0 une livraison rapide de valeur. Le client peut aussi ajouter du p\u00e9rim\u00e8tre gratuitement, encourageant la collaboration plut\u00f4t que des contrats rigides.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q12",
        type: "multiple-choice",
        questionText: "Laquelle des affirmations suivantes est correcte concernant le Backlog du Sprint?",
        options: [
          "Il appartient au Product Owner et ne peut pas \u00eatre modifi\u00e9 pendant un Sprint",
          "Il appartient \u00e0 l'\u00c9quipe de D\u00e9veloppement et est mis \u00e0 jour en temps r\u00e9el \u00e0 mesure que le travail progresse",
          "C'est une liste de toutes les fonctionnalit\u00e9s pr\u00e9vues pour l'ensemble du cycle de vie du produit",
          "Il est cr\u00e9\u00e9 par le Scrum Master et assign\u00e9 aux d\u00e9veloppeurs",
        ],
        correctAnswer: "Il appartient \u00e0 l'\u00c9quipe de D\u00e9veloppement et est mis \u00e0 jour en temps r\u00e9el \u00e0 mesure que le travail progresse",
        explanation: "Le Backlog du Sprint appartient \u00e0 l'\u00c9quipe de D\u00e9veloppement et est mis \u00e0 jour tout au long du Sprint. Seule l'\u00c9quipe de D\u00e9veloppement peut le modifier pendant le Sprint.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q13",
        type: "multiple-choice",
        questionText: "\u00c0 quoi sert principalement un Diagramme de flux cumul\u00e9 (CFD) pour une \u00e9quipe?",
        options: [
          "La productivit\u00e9 individuelle des d\u00e9veloppeurs",
          "La sant\u00e9 du flux de travail et les goulots d'\u00e9tranglement potentiels",
          "Le budget restant",
          "Si le produit r\u00e9pond aux besoins des clients",
        ],
        correctAnswer: "La sant\u00e9 du flux de travail et les goulots d'\u00e9tranglement potentiels",
        explanation: "Un CFD montre le travail dans chaque \u00e9tat du flux de travail au fil du temps. Des bandes qui s'\u00e9largissent indiquent des goulots d'\u00e9tranglement, des pentes plates indiquent des progr\u00e8s bloqu\u00e9s, et des bandes parall\u00e8les r\u00e9guli\u00e8res indiquent un flux sain.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q14",
        type: "multiple-choice",
        questionText: "Dans quel quadrant des Quadrants de tests Agile les tests exploratoires sont-ils class\u00e9s?",
        options: [
          "Q1 — Orient\u00e9 technologie, soutient l'\u00e9quipe",
          "Q2 — Orient\u00e9 m\u00e9tier, soutient l'\u00e9quipe",
          "Q3 — Orient\u00e9 m\u00e9tier, critique le produit",
          "Q4 — Orient\u00e9 technologie, critique le produit",
        ],
        correctAnswer: "Q3 — Orient\u00e9 m\u00e9tier, critique le produit",
        explanation: "Les tests exploratoires sont en Q3 — ils sont orient\u00e9s m\u00e9tier (testent le produit du point de vue de l'utilisateur) et critiquent le produit (cherchent \u00e0 trouver des probl\u00e8mes par une exploration cr\u00e9ative).",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q15",
        type: "multiple-choice",
        questionText: "Quel est le principal objectif de la M\u00eal\u00e9e quotidienne?",
        options: [
          "Faire rapport de l'\u00e9tat au Scrum Master",
          "Inspecter les progr\u00e8s vers l'Objectif du Sprint et adapter le plan quotidien",
          "Assigner des t\u00e2ches aux membres de l'\u00e9quipe",
          "Discuter des commentaires des parties prenantes",
        ],
        correctAnswer: "Inspecter les progr\u00e8s vers l'Objectif du Sprint et adapter le plan quotidien",
        explanation: "La M\u00eal\u00e9e quotidienne est un \u00e9v\u00e9nement de planification o\u00f9 l'\u00c9quipe de D\u00e9veloppement inspecte les progr\u00e8s vers l'Objectif du Sprint et adapte le travail planifi\u00e9 \u00e0 venir. Ce n'est pas un rapport d'\u00e9tat.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q16",
        type: "multiple-choice",
        questionText: "Une organisation a adopt\u00e9 Scrum mais les gestionnaires assignent encore les t\u00e2ches individuellement, les m\u00eal\u00e9es quotidiennes sont des rapports d'\u00e9tat, et la D\u00e9finition de Fini est ignor\u00e9e. Quelle est la cause profonde?",
        options: [
          "L'\u00e9quipe a besoin de meilleurs outils",
          "L'organisation a adopt\u00e9 les c\u00e9r\u00e9monies sans adopter l'\u00e9tat d'esprit Agile",
          "Scrum est le mauvais cadre pour cette \u00e9quipe",
          "La dur\u00e9e du Sprint est trop courte",
        ],
        correctAnswer: "L'organisation a adopt\u00e9 les c\u00e9r\u00e9monies sans adopter l'\u00e9tat d'esprit Agile",
        explanation: "C'est un sc\u00e9nario classique de 'cargo-cult Agile'. La v\u00e9ritable agilit\u00e9 n\u00e9cessite la confiance, l'autonomisation, l'autogestion et un engagement envers la qualit\u00e9 — pas seulement une adoption m\u00e9canique des c\u00e9r\u00e9monies.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q17",
        type: "multiple-choice",
        questionText: "Quel est le pourcentage maximal recommand\u00e9 de la capacit\u00e9 du Sprint \u00e0 consacrer au Raffinement du Backlog?",
        options: ["5%", "10%", "20%", "30%"],
        correctAnswer: "10%",
        explanation: "Le Guide Scrum recommande de consacrer jusqu'\u00e0 10% de la capacit\u00e9 du Sprint au Raffinement du Backlog. Cela garantit que le Backlog reste en sant\u00e9 sans consommer trop de temps de d\u00e9veloppement.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q18",
        type: "multiple-choice",
        questionText: "Dans les Trois voies de DevOps, que met l'accent la voie 'R\u00e9troaction'?",
        options: [
          "Des boucles de r\u00e9troaction courtes pour que les probl\u00e8mes soient d\u00e9tect\u00e9s et corrig\u00e9s imm\u00e9diatement",
          "Des \u00e9valuations de performance annuelles",
          "Des sondages de satisfaction client",
          "Des rapports d'\u00e9tat mensuels",
        ],
        correctAnswer: "Des boucles de r\u00e9troaction courtes pour que les probl\u00e8mes soient d\u00e9tect\u00e9s et corrig\u00e9s imm\u00e9diatement",
        explanation: "La Deuxi\u00e8me voie (R\u00e9troaction) met l'accent sur la cr\u00e9ation de boucles de r\u00e9troaction courtes. La surveillance, les alertes et la r\u00e9ponse aux incidents garantissent que les probl\u00e8mes op\u00e9rationnels sont d\u00e9tect\u00e9s et trait\u00e9s rapidement.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q19",
        type: "multiple-choice",
        questionText: "Un Product Owner veut ajouter une fonctionnalit\u00e9 critique en milieu de Sprint. Que devrait faire l'\u00e9quipe?",
        options: [
          "Tout laisser tomber et travailler sur la nouvelle fonctionnalit\u00e9",
          "Expliquer que le p\u00e9rim\u00e8tre du Sprint est fixe et que la fonctionnalit\u00e9 peut \u00eatre ajout\u00e9e lors de la prochaine Planification du Sprint",
          "L'ajouter au Backlog du Sprint sans discussion",
          "Demander au Scrum Master de d\u00e9cider",
        ],
        correctAnswer: "Expliquer que le p\u00e9rim\u00e8tre du Sprint est fixe et que la fonctionnalit\u00e9 peut \u00eatre ajout\u00e9e lors de la prochaine Planification du Sprint",
        explanation: "Aucun changement ne devrait \u00eatre effectu\u00e9 qui pourrait compromettre l'Objectif du Sprint. L'\u00e9quipe devrait prot\u00e9ger son engagement de Sprint et ajouter la nouvelle fonctionnalit\u00e9 au Backlog du produit pour la prochaine Planification du Sprint.",
        lessonContext: "",
      },
      {
        questionId: "as-fe-q20",
        type: "multiple-choice",
        questionText: "Laquelle des propositions suivantes r\u00e9sume le mieux l'\u00e9tat d'esprit Agile?",
        options: [
          "Suivre un plan d\u00e9taill\u00e9 strictement pour garantir la pr\u00e9visibilit\u00e9",
          "Adopter la collaboration, l'apprentissage, l'adaptabilit\u00e9 et l'am\u00e9lioration continue plut\u00f4t que des processus rigides",
          "Tout documenter en profondeur avant de commencer tout travail",
          "Se concentrer sur les outils et l'automatisation pour \u00e9liminer l'erreur humaine",
        ],
        correctAnswer: "Adopter la collaboration, l'apprentissage, l'adaptabilit\u00e9 et l'am\u00e9lioration continue plut\u00f4t que des processus rigides",
        explanation: "L'\u00e9tat d'esprit Agile valorise la collaboration, l'orientation client, l'acceptation de l'incertitude, l'am\u00e9lioration continue, le rythme soutenable et l'excellence technique. Il priorise les personnes et l'adaptabilit\u00e9 plut\u00f4t que les plans et processus rigides.",
        lessonContext: "",
      },
    ],
  },
};
