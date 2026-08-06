# QA Pilot Browser App Separation

**Created:** 2026-07-13 (Sprint 4 — `QA-PILOT-CARBIDEFRAME-GOVERNANCE-INTEGRATION-1`)
**Authority:** Owner direction per `EPIC-QA-PILOT-OPENWORK-TO-CARBIDEFRAME-MIGRATION-1` (approval `apt_bb2995d2`, `apt_3ed7340e`)
**Boundary:** QA Pilot-local. Does not affect CarbideFrame Librarian.

---

## 1. Purpose

Document and enforce the separation between the QA Pilot **governance framework** and its **migrated web application** within the same CarbideFrame project workspace. This separation is a deliberate architectural decision by the Owner, not an oversight.

## 2. The Three Data Domains

| Domain | Path | Purpose | Governance scope | Examples |
|--------|------|---------|-----------------|----------|
| **Governance framework** | `scripts/`, `docs/governance/`, `docs/schemas/`, `fixtures/`, `project-state/`, `receipts/`, `config/` | QA Pilot's governed advisory framework — validators, schemas, sprint ledger, custody receipts, operational data | ✅ In scope: validated by 59 validators, 65 test runners, signed by Owner decisions | `scripts/validate-qa-pilot-*.py`, `project-state/sprint-ledger.json`, `docs/governance/*.md` |
| **Governance operational data** | `data/` (root level) | Working data produced by governance scripts — evidence packets, test cases, training sims, audit receipts, registry changes | ✅ In scope: advisory-only, never acts on production state | `data/evidence/`, `data/audit/`, `data/training-packages/`, `data/receipts/` |
| **Browser application** | `browser-app/` | The migrated QA Pilot training platform — HTML pages, JS app logic, course content, OS simulator, CSS, assets, build scripts | ❌ Out of scope: application files are not governance data. Their schema is the web platform, not JSON. | `browser-app/index.html`, `browser-app/js/db.js`, `browser-app/data/content.js`, `browser-app/QASimulator.html`, `browser-app/src/os-core.js` |

## 3. Critical Separation Rules

### 3a. `browser-app/data/` vs. root `data/`

| Root `data/` (governance) | `browser-app/data/` (application) |
|---------------------------|-----------------------------------|
| JSON operational records | JavaScript course content modules |
| Produced/consumed by Python governance scripts | Loaded by HTML `<script>` tags |
| Governed by JSON schemas under `docs/schemas/` | No governance schema — plain JS modules |
| Examples: evidence receipts, audit entries, training sim results | Examples: `content.js` (7,055 lines), `quiz-questions.js`, `assignments.js` |
| File type: `.json` | File type: `.js`, `.json` |

**Rule:** No governance validator or script may read, write, index, hash, or validate files under `browser-app/data/`. No application code may write to root `data/`. These are separate concerns with separate contracts.

### 3b. Governance validators and the browser app

Governance validators (`scripts/validate-qa-pilot-*.py`) must not:
- Parse or validate `browser-app/` HTML, JS, or CSS files
- Index `browser-app/` file paths in governance receipts
- Add `browser-app/` files to the sprint ledger
- Require `browser-app/` content to pass any governance validation gate

The browser-app is a **governance-consumer**, not a governance-surface.

### 3c. Startup and status

The migration epic updated `startup-contract.json` to:
- Set `is_web_app: true`
- Add `web_app_root: "active/qa-pilot/browser-app/"`
- Include `browser-app/index.html` in required files (as existence check only)
- Add `browser-app/index.html` to context_sources (as non-required reference context)

These are **awareness-only** changes. The startup contract does not validate web-app content, run web-app checks, or absorb browser-app into governance state.

The `web_app_data_separation` block records the policy so future agents know the two `data/` directories are intentionally distinct.

## 4. Migration Epic Posture

| Sprint | Status | Impact on separation |
|--------|--------|---------------------|
| 1 — Prep & Snapshot | ✅ Complete | Separation designed; `browser-app/` created as dedicated root |
| 2 — App Copy | ✅ Complete | All 123 files copied to `browser-app/`; `browser-app/data/` established as dedicated application data root |
| 3 — Smoke Validation | ✅ Complete | Path defects fixed within `browser-app/` only; no governance surface touched |
| 4 — Governance Integration | ✅ Complete | This doc written; startup-contract and profile updated; separation codified |
| 5 — Roundtrip Validation | ⏳ Pending | Final validation and canonical recommendation |

## 5. Enforcement

This separation is enforced by:
1. **Project profile** — `PROJECT-PROFILE.json` lists `browser-app/` as an allowed mutation path (separate from `data/`, `scripts/`, `docs/`)
2. **Startup contract** — `startup-contract.json` notes the separation in `web_app_data_separation`
3. **Agents** — Hard boundary instruction: governance agents may read `browser-app/` for context but must not validate, index, or absorb its content into governance state
4. **Receipts** — Each migration sprint's receipt records the boundary was honored

## 6. Future Considerations

If a future epic needs to validate the browser app through governance (e.g., automated end-to-end testing), it must:
(a) Be authorized by Owner decision as a distinct work item
(b) Create a new governance lane (e.g., `browser_app_qa`) separate from the advisory governance lanes
(c) Not retroactively apply to the migration epic's boundary
(d) Not mutate root `data/` from within the browser app
