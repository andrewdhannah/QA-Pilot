# QA Pilot — Product Roadmap
**Last updated:** May 2026 | **Maintained by:** Andrew + Ash (CoWork)

---

## Milestone overview

| Milestone | Theme | Status |
|-----------|-------|--------|
| **V1** | Core platform — releasable to Elyse | 🔄 In progress |
| **V1.1** | Training completeness + facilitator tools | 📋 Planned |
| **V1.2** | Analytics, inspector, scenario expansion | 📋 Planned |
| **V2.0** | Multi-trainee, authoring, advanced track complete | 🔭 Future |

---

## V1 — Core Platform Release
**Goal:** A working, bug-free platform Elyse can use with real trainees today.
**Target:** When C10, C11, G9, G7, G8, C12 are merged and verified.

### V1 Release Checklist
- [ ] SPRINT-C10: Scoring engine bundled, context menu fixed, start menu search fixed, Dynamics form-load bug fixed
- [ ] SPRINT-G9: Lesson 4 quiz layout fixed (double topbar)
- [ ] SPRINT-C11: Health checks, keyboard shortcut registry, Settings keyboard panel
- [ ] SPRINT-G7: Lesson 5 created (test planning + triage)
- [ ] SPRINT-G8: capstone-2.html (advanced capstone, lesson-5 gated)
- [ ] SPRINT-C12: Training app UI (scenario selector + step-through)
- [ ] Manual smoke test: all lessons, both capstones, submit flow, results in Reports
- [ ] SPRINT-G10: Facilitator guide + student quick-start docs published
- [ ] Hand off to Elyse

---

## V1.1 — Training Completeness + Facilitator Tools
**Goal:** Fill the remaining gaps Elyse will notice in week 1.
**Theme:** Polish over new features.

| Feature | Sprint | Notes |
|---------|--------|-------|
| Reports app live data | SPRINT-C13 | IndexedDB analytics, session detail view |
| case-003 scenario (4 bugs, Expert) | SPRINT-G11 | Multi-system, Teams + Dynamics + ADO |
| ADO — AC format validation + hints | SPRINT-C9 (partial) | AC ref must match `AC-#.#` format |
| ADO — bug history list in-app | Planned C14 | Trainee can see previously filed reports |
| Dynamics — required field validation on save | Planned C14 | Save button currently has no validation |
| Notification Centre — clear all tested | Smoke test | Mark ✅ after manual verification |
| Task View — working thumbnails | Planned C15 | Cards currently render blank |
| Inspector app — basic scenario inspection UI | Planned C15 | Currently a stub |
| AC Panel — scenario data loads on APP_BOOT | Needs re-verification | Marked 🔍 in FEATURE-STATUS |

---

## V1.2 — Analytics, Inspection, and Scenario Expansion
**Goal:** Give Elyse real insight into trainee progress and expand the content library.

| Feature | Sprint | Notes |
|---------|--------|-------|
| capstone-3.html (Expert, case-003) | Planned G12 | Requires C13 + G11 merged |
| Facilitator dashboard (aggregate stats) | Planned C15 | Multi-session view in Reports |
| Inspector app — scenario debugging UI | Planned C15 | For Andrew to debug scenarios |
| Training app — custom step authoring | Planned C16 | Elyse or Andrew adds steps without code |
| Lesson 3 quiz — re-verify and fix | Smoke test | Reported quiz issues, marked 🔍 |
| Browser app — apps receive APP_BOOT in br-frame | Planned C16 | Currently scenarios don't populate in browser-embedded apps |
| Training app — cross-app guided steps | Planned C17 | Steps that tell trainee to open specific apps |

---

## V2.0 — Multi-Trainee + Content Authoring
**Goal:** Elyse can run the platform for a team without Andrew involved.
**Theme:** Self-service for the trainer.

| Feature | Notes |
|---------|-------|
| Scenario authoring UI (no-code) | Elyse creates new scenarios from the admin panel |
| Multi-trainee result tracking (non-local) | Results exportable as JSON or CSV |
| Named trainee login (persistent identity) | "Andrew H" not just a session — results tied to a name across sessions |
| Facilitator mode — live session view | See what trainee is doing in real-time (stretch goal) |
| case-004+ scenario library | Quarterly new scenarios matching real client types |
| Certificate generator with trainee name | PDF-style certificate from the Academy |
| Admin dashboard outside the OS | A web page Elyse can use without opening the simulator |

---

## Sprint Queue — Ready to execute

Sprint prompts written and in `Documents/`:

| Sprint | Assignee | Status | Depends on |
|--------|----------|--------|------------|
| SPRINT-C10 | Copilot | 🔄 In progress | — |
| SPRINT-G9 | Gemma | 🔄 In progress | — |
| SPRINT-C11 | Copilot | 📋 Queued | C10 merged |
| SPRINT-G7 | Gemma | 📋 Queued | — |
| SPRINT-G8 | Gemma | 📋 Queued | G7 merged |
| SPRINT-C12 | Copilot | 📋 Queued | C9 merged |
| SPRINT-G10 | Gemma | 📋 Queued | C12, G8 merged |
| SPRINT-C13 | Copilot | 📋 Queued | C10 merged |
| SPRINT-G11 | Gemma | 📋 Queued | C7 merged |

---

## Principles

**File:// first.** No server, no CDN, no fetch(). Every feature must work as a local file
opened in a browser. This is a hard constraint until V2.0 explicitly revisits it.

**LLM division of labour:**
- Copilot (C sprints): JavaScript logic, build pipeline, OS internals, data/state
- Gemma (G sprints): HTML/CSS, lesson pages, docs, visual design, content
- Ash (CoWork): Architecture review, sprint prompt authoring, cross-sprint continuity

**Andrew is the review layer.** All LLM output is reviewed before merge.
FEATURE-STATUS.md is updated after each verified merge, not before.

**Elyse is the real user.** Features that don't serve a trainee or a facilitator don't
ship in V1/V1.1. Engineering-only features (Inspector, diagnostics) are V1.2+.

---

## How to add a new sprint

1. Ash writes a sprint prompt in `Documents/SPRINT-Cnn-` or `SPRINT-Gnn-` format
2. Andrew hands it to the appropriate LLM (Copilot or Gemma)
3. LLM submits PR or writes output files
4. Andrew reviews → merges → runs `node build.js`
5. Manual smoke test of changed features
6. FEATURE-STATUS.md updated
7. Sprint file moved to `Documents/Completed/`
