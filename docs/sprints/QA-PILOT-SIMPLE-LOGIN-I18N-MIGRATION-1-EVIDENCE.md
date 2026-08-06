# QA-PILOT-SIMPLE-LOGIN-I18N-MIGRATION-1-EVIDENCE.md

**Produced by:** QA-PILOT-SIMPLE-LOGIN-I18N-MIGRATION-1 (ledger #173)
**Date:** 2026-07-20
**Classification:** Advisory evidence only

---

## Acceptance Gate Results

| Gate | Result | Assessment |
|------|--------|------------|
| LOGIN-I18N-1 | PASS | All identified user-facing strings migrated |
| LOGIN-I18N-2 | PASS | 13 EN/FR keys added, parity maintained |
| LOGIN-I18N-3 | PASS | Existing authentication flow preserved (login(), handleFile(), initDB() intact) |
| LOGIN-I18N-4 | PASS | Language toggle added and functional |
| LOGIN-I18N-5 | PASS | No unrelated legacy pages modified |
| LOGIN-I18N-6 | PASS | Evidence produced (this document) |

**6 PASS, 0 FAIL**

---

## Files Modified

| File | Change |
|------|--------|
| `browser-app/simple-login.html` | Added i18n scripts, toggle container, translate function |
| `js/lang-en.js` | 13 new keys added |
| `js/lang-fr.js` | 13 new French translations added |

---

## Keys Added (13 per language)

| Key | EN Value | FR Value |
|-----|----------|----------|
| `simple_login_hero_desc` | Your hands-on training platform... | Votre plateforme de formation pratique... |
| `simple_login_team_login` | Team Login | Connexion d'équipe |
| `simple_login_subtitle` | Upload your class file... | Téléchargez votre fichier de classe... |
| `simple_login_upload` | Upload Class File | Télécharger le fichier de classe |
| `simple_login_upload_hint` | Click to select the .json file... | Cliquez pour sélectionner le fichier .json... |
| `simple_login_your_name` | Your Name | Votre nom |
| `simple_login_name_placeholder` | Type your name… | Tapez votre nom… |
| `simple_login_scenarios` | Scenarios | Scénarios |
| `simple_login_lessons` | Lessons | Leçons |
| `simple_login_unlock_code` | Unlock Code | Code de déverrouillage |
| `simple_login_unlock_placeholder` | Enter the unlock code from your trainer | Entrez le code de déverrouillage... |
| `simple_login_unlock_hint` | Your trainer shared this code... | Votre formateur a partagé ce code... |
| `simple_login_login` | Login | Connexion |

---

## Scope Compliance

| Check | Result |
|-------|--------|
| Authentication logic changed | No |
| db.js/app.js behavior changed | No |
| QASimulator/capstone modified | No |
| Desktop/extension decisions | Not touched |
| App module audit | Not touched |

---

**Produced by:** QA-PILOT-SIMPLE-LOGIN-I18N-MIGRATION-1 (ledger #173)
**Classification:** Advisory evidence only — does not perform any decision.
