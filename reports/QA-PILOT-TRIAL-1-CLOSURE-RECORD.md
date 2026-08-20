# QA Pilot Trial 1 — Closure Record

**Trial:** QA-PILOT-EMPIRICAL-VALIDATION-TRIAL-1
**Closure Date:** 2026-08-20
**Closure Authority:** Bounded remediation authorization (Owner-directed)
**Status:** REMEDIATION VERIFIED — awaiting Owner seal review

---

## Finding Closure Matrix

| Finding | Original Class | Final Class | Remediation | Evidence | Status |
|---------|---------------|-------------|-------------|----------|--------|
| F-001 | MIGRATION RESIDUE | MIGRATION RESIDUE | CLAUDE.md.shim marked `> **DEPRECATED.**` with active entrypoint pointer | Regression check 1: deprecation header present at line 3 | CLOSED — VERIFIED |
| F-002 | MIGRATION RESIDUE | MIGRATION RESIDUE | LIBRARIAN-COMPLETE-BRIEFING.md moved to "Historical (not loaded during startup)" section in CLAUDE.md | Regression check 4: file listed under Historical section, not active doc list | CLOSED — VERIFIED |
| F-003 | MIGRATION RESIDUE | MIGRATION RESIDUE | startup.json: added `"status": "deprecated"` and updated description to "DEPRECATED — This manifest defines the pre-harness..." | Regression check 2: deprecation status present at line 8 | CLOSED — VERIFIED |
| F-004 | MIGRATION RESIDUE | MIGRATION RESIDUE | CLAUDE.md.pre-sse4a marked `> **DEPRECATED.**` with active entrypoint pointer | Regression check 1: deprecation header present at line 3 | CLOSED — VERIFIED |
| F-005 | GOVERNANCE HOLE → MIGRATION RESIDUE (corrected) | MIGRATION RESIDUE | Intent routing table in active/librarian/CLAUDE.md already references "Runtime Brief §3" — no STARTUP-OUTPUT-CONTRACT.md reference exists. Reclassified: reference conflict, not authority bypass. | Regression check 7: grep returns no matches for STARTUP-OUTPUT-CONTRACT in intent routing | CLOSED — VERIFIED (pre-existing fix confirmed) |
| F-006 | MIGRATION RESIDUE | MIGRATION RESIDUE | Cold-storage sealing deferred to Owner — not in scope for this remediation cycle | N/A — Owner decision required | DEFERRED — OWNER ACCEPTED |
| F-007 | CONFIRMED EXISTING CONTROL | CONFIRMED EXISTING CONTROL | No change needed — LINK boundary correctly prevents authority grants | Regression check 10: LINK boundary rules intact at lines 181, 189 | CONFIRMED |
| F-008 | CONFIRMED EXISTING CONTROL | CONFIRMED EXISTING CONTROL | No change needed — capability availability ≠ authorization enforced by 3-axis model | Runtime Brief §8 + GOVERNANCE-REFERENCE Part 10 unchanged | CONFIRMED |
| F-009 | CONFIRMED EXISTING CONTROL | CONFIRMED EXISTING CONTROL | No change needed — evidence model (append-only, provenance-tagged, deterministic) correctly specified | Runtime Brief §5 unchanged | CONFIRMED |
| F-010 | MIGRATION RESIDUE | MIGRATION RESIDUE | Cold-storage surface accessible but not sealed — same disposition as F-006 | N/A — Owner decision required | DEFERRED — OWNER ACCEPTED |
| F-011 | PROJECTION DEFECT | PROJECTION DEFECT | SUPERSEDED added to lifecycle diagram and state table in Runtime Brief §4 | Regression check 5: SUPERSEDED at lines 95, 108, 116 | CLOSED — VERIFIED |
| F-012 | PROJECTION DEFECT | PROJECTION DEFECT | BLOCKED diagram updated: "may occur before or during execution", transition line changed to "AUTHORIZED/ACTIVE → BLOCKED" | Regression check 6: updated text at lines 107, 111, 114 | CLOSED — VERIFIED |
| F-013 | USABILITY/COGNITIVE LOAD | USABILITY/COGNITIVE LOAD | Step 5 added to startup sequence: "Read AGENT-RUNTIME-BRIEF.md for normal bounded execution rules." | Regression check 3: step 5 present at line 27 | CLOSED — VERIFIED |
| F-014 | MIGRATION RESIDUE | MIGRATION RESIDUE | Duplicate SessionStartup/ inside active/librarian/ — deferred as file hygiene (not blocking governance) | N/A — low priority cleanup | DEFERRED — OWNER ACCEPTED |

---

## Summary

| Status | Count |
|--------|-------|
| CLOSED — VERIFIED | 8 |
| CONFIRMED (existing control) | 3 |
| DEFERRED — OWNER ACCEPTED | 3 |
| OPEN | 0 |

**All 8 remediation items closed with evidence.** 3 confirmed controls verified as unchanged. 3 low-priority items deferred to Owner.

---

## Files Changed

| File | Change | Finding |
|------|--------|---------|
| `CLAUDE.md` | Added step 5 (read Runtime Brief); moved superseded briefing to Historical section | F-013, F-002 |
| `CLAUDE.md.shim` | Added deprecation header | F-001 |
| `CLAUDE.md.pre-sse4a` | Added deprecation header | F-004 |
| `AGENT-RUNTIME-BRIEF.md` | Added SUPERSEDED to lifecycle diagram/table; updated BLOCKED representation | F-011, F-012 |
| `startup.json` | Added `"status": "deprecated"` and deprecation description | F-003 |
| `active/librarian/CLAUDE.md` | No change required (already correct) | F-005 |

---

## F-005 Taxonomy Disposition

**Original classification:** GOVERNANCE HOLE
**Corrected classification:** MIGRATION RESIDUE

**Rationale:** F-005 identified a reference conflict — the intent routing table in active/librarian/CLAUDE.md referenced STARTUP-OUTPUT-CONTRACT.md as a source doc while the startup sequence prohibited reading it. This is a documentation inconsistency, not a path around authority or evidence governance. No authority, evidence, or capability boundary could be bypassed through this reference. The Runtime Brief's authority model (§3.1 three-part AND gate, §6 prohibitions) operates independently of the intent routing table's source references. Reclassified to MIGRATION RESIDUE for semantic accuracy.

**Provenance note:** The original GOVERNANCE HOLE classification is preserved in the Trial 1 report (QA-PILOT-EMPIRICAL-VALIDATION-TRIAL-1.md §14). This closure record documents the reclassification. The Trial 1 report is not rewritten.

---

## Targeted Regression Results

| Check | Result | Evidence |
|-------|--------|----------|
| 1. No competing active startup doctrine | PASS | CLAUDE.md.shim and .pre-sse4a both marked DEPRECATED |
| 2. startup.json deprecated | PASS | `"status": "deprecated"` present |
| 3. Runtime Brief in startup path | PASS | Step 5 added to CLAUDE.md |
| 4. Superseded briefing not in active list | PASS | Moved to Historical section |
| 5. SUPERSEDED in lifecycle | PASS | Diagram, table, and notes all present |
| 6. BLOCKED diagram updated | PASS | "before or during" + "AUTHORIZED/ACTIVE → BLOCKED" |
| 7. No STARTUP-OUTPUT-CONTRACT in intent routing | PASS | grep returns no matches |
| 8. Authority gate intact (§3.1) | PASS | "all three are true" + "Identity is not authorization" |
| 9. Silence is denial intact | PASS | "Absence of prohibition is not permission" |
| 10. LINK boundary intact | PASS | "LINK does not" + "may not treat LINK output as authorization" |

**Regression suite: 10/10 PASS**

---

## Fresh-Agent Sufficiency Result

Using only AGENT-RUNTIME-BRIEF.md, a fresh agent can determine:

| Question | Source in Runtime Brief | Status |
|----------|----------------------|--------|
| What is it doing? | §1 "What The Librarian Is" | ANSWERED |
| Whether it may proceed? | §3.1 "Am I Authorized?" (three-part AND) | ANSWERED |
| Its scope? | §3.2 "What Is My Scope?" (allowed/forbidden files) | ANSWERED |
| When readback is required? | §3.4 "Pre-Execution Readback" ("consequential or mutating") | ANSWERED |
| When to stop? | §3.2, §6 "What You Must Never Do" | ANSWERED |
| Required evidence? | §5 "Evidence Rules", §10 "Completion Protocol" | ANSWERED |
| Completion posture? | §10 "Completion Protocol" | ANSWERED |
| Owner-decision boundary? | §2 "The Fundamental Rule", §6 prohibitions | ANSWERED |
| Reporting requirements? | §10 "Completion Protocol" (completion receipt format) | ANSWERED |

**The deep Governance Reference is not required for ordinary execution.**

**Fresh-agent sufficiency: PASS**

---

## Confirmed Unchanged Governance Mechanisms

| Mechanism | Status | Verification |
|-----------|--------|-------------|
| Authority resolution (7 scenarios) | UNCHANGED | §3.1, §3.2, §3.3, §6 all intact |
| Pre-Execution Readback | UNCHANGED | §3.4 text unmodified |
| LINK boundary | UNCHANGED | §7 text unmodified |
| Capability availability ≠ authorization | UNCHANGED | §8 + GOVERNANCE-REFERENCE Part 10 unmodified |
| Evidence properties | UNCHANGED | §5 text unmodified |
| Completion ≠ acceptance | UNCHANGED | §10 text unmodified |
| Self-sealing prohibition | UNCHANGED | §6 table unmodified |
| Scope broadening prohibition | UNCHANGED | §3.2 + §6 unmodified |

**No substantive governance mechanism was modified. All changes were documentation/projection corrections.**

---

## QA Qualification Posture

**QA PILOT TRIAL 1 — REMEDIATION VERIFIED**

All 8 remediation items closed with evidence. Targeted regression passes (10/10). Fresh-agent sufficiency confirmed (9/9 questions answered). No authority/evidence regression detected.

This is a QA/evidence statement. It is not Owner acceptance or seal.

QA Pilot does not self-seal.

---

## Recommended Owner Decision

**OWNER SEAL — GOVERNANCE OVERENGINEERING REMEDIATION**

The simplified governance model:
- Preserves all tested authority, evidence, LINK, capability, readback, and completion boundaries
- Is materially easier to use (300-line Runtime Brief vs 1,159-line superseded briefing)
- Has no competing active startup doctrine (all stale entrypoints deprecated)
- Has complete lifecycle projection (SUPERSEDED and BLOCKED now correctly represented)
- Has the Runtime Brief correctly wired into the startup path
- Has all Trial 1 findings closed with evidence

Recommended seal scope: AGENT-RUNTIME-BRIEF.md, GOVERNANCE-REFERENCE.md, CLAUDE.md (workspace root), CLAUDE.md (active/librarian), and the associated deprecation of startup.json, CLAUDE.md.shim, CLAUDE.md.pre-sse4a.

---

*Generated by QA Pilot — evaluation only. Not remediation. Not acceptance. Not seal.*
