# QA Pilot — Post-Validation Decision Review

**Purpose:** Classify the 6 validation recommendations into maintenance, deferred, new capability, or cross-system proposal.
**Preceding gate:** Validation Sprint (✅ complete)
**Status:** ADVISORY — Owner decision required for any non-maintenance action.

---

## 1. Recommendation Classification

| # | Recommendation | Classification | Authority Required? | Priority |
|---|---------------|---------------|-------------------|----------|
| 1 | Add `authority_level: advisory` to #182 Performance | **Maintenance** | No | Low |
| 2 | Add `direct_scan` evidence reference convention for #188 | **Maintenance** | No | Low |
| 3 | Cross-project validation against librarian-runtime-node | **Deferred** | No (re-run validation) | Medium |
| 4 | Age-test evidence freshness classification | **Deferred** | No (re-run validation) | Low |
| 5 | Migrate #179–#182 to #185 assurance_report format | **Deferred** | Yes (format migration) | Low |
| 6 | QA Pilot → Librarian integration | **Cross-system proposal** | Yes (architecture review) | Deferred |

---

## 2. Maintenance Items (Operating Mode Permitted)

These items can be handled under the existing operating mode without planning, invariant review, or Owner authorization.

### 2.1 #182 Performance — Add authority_level field

**Current state:** `data/performance-baseline.json` lacks `"authority_level": "advisory"`. All other evidence files include it.

**Impact:** Minor. The field's absence does not affect functionality. The Release Readiness Profile does not validate this field — it treats any non-standard evidence as OBSERVATION.

**Action:** Add one line to `scripts/qa_pilot_performance_capability.py`:
```python
"authority_level": "advisory"
```

**Risk:** None. This is a metadata field addition with no schema or behavior change.

**Recommendation:** ✅ Apply when convenient — low priority, no authorization needed.

### 2.2 #188 Security — Improve evidence reference uniformity

**Current state:** 6/13 findings have `evidence_references`. The remaining 7 are direct-scan findings without explicit provenance.

**Impact:** Minor. All direct-scan findings still have `check` and `affected_components` fields for traceability. The provenance gap is documentation, not data loss.

**Action:** Add `"evidence_references": ["direct_scan:browser-app"]` to direct-scan findings in `scripts/qa_pilot_security_assurance_profile.py`.

**Risk:** None. Evidence reference paths are advisory metadata.

**Recommendation:** ✅ Apply when convenient — low priority, no authorization needed.

---

## 3. Deferred Items

These items are valuable but not urgent. They should not be started immediately.

### 3.1 Cross-Project Validation (Recommendation 3)

**Proposal:** Run the framework against `librarian-runtime-node` to test generality.

**Concern:** This would validate that the framework works on non-QA-Pilot targets. However, the validation just completed — the framework's boundary and utility are confirmed. Cross-project validation adds proof of generality but may not change any decisions.

**Recommendation:** ⏸️ **Defer.** Revisit if a new project needs assurance assessment. If pursued, it is a re-execution of the existing validation plan, not new framework work.

### 3.2 Freshness Age-Testing (Recommendation 4)

**Proposal:** Manually age evidence files and re-run Release Readiness to verify STALE propagation.

**Concern:** The freshness logic is simple (timestamp comparison with 7-day threshold). The risk of a bug is low, and the cost of a missed stale classification is minimal (a stale evidence tag is advisory only).

**Recommendation:** ⏸️ **Defer.** Low value. The STALE logic can be verified during any future evidence update cycle.

### 3.3 Migrate #179–#182 to #185 Format (Recommendation 5)

**Proposal:** Convert regression, UAT, accessibility, and performance capabilities to produce `assurance_report` format evidence.

**Evaluation:** This should be evaluated carefully because migrations can create unnecessary churn if existing evidence is already consumable.

| Factor | Assessment |
|--------|------------|
| Current evidence consumable? | ✅ Yes — Release Readiness correctly handles legacy formats |
| Classification loss? | ✅ No — all evidence content is preserved |
| Benefit of migration | Standardized schema; structured PASS/OBSERVATION/ODR instead of derived |
| Cost of migration | 4 scripts to modify, test, and re-validate |
| Risk | Script changes could introduce bugs; output format change could break downstream consumers |

**Recommendation:** ⏸️ **Defer.** The operating mode already lists this as a known limitation. Migration is only valuable if a downstream consumer requires the #185 format. No current consumer has that requirement — Release Readiness normalizes legacy formats correctly.

---

## 4. Cross-System Proposal

This item crosses the frozen boundary between QA Pilot and Librarian. It requires formal architecture review before any planning or implementation.

### 4.1 QA Pilot → Librarian Integration (Recommendation 6)

**Current state:** QA Pilot produces evidence in its own data directory. The Librarian platform has its own evidence schema (`platform-evidence-v1`). No connection exists between them.

**Potential integration paths (not evaluated):**
- QA Pilot evidence consumed by Librarian Intelligence Layer
- QA Pilot findings surfaced in Librarian governance views
- Release Readiness Profile output consumed by Librarian release workflow

**Concern:** Integration would cross the established boundary between QA Pilot (advisory assurance) and Librarian (governance authority). It should be driven by demonstrated value, not architectural opportunity.

**Prerequisites before pursuing:**
1. A clear value proposition (what does Librarian gain from consuming QA Pilot evidence?)
2. An architecture review (does integration preserve both systems' boundaries?)
3. An invariant review (does integration create hidden authority paths?)
4. Owner authorization

**Recommendation:** ⏸️ **Defer until a clear value proposition exists.** Do not pursue integration planning as a default next step.

---

## 5. Current Assurance Framework State

| Component | Status |
|-----------|--------|
| Operating Mode Declaration | ✅ EFFECTIVE |
| #179 Regression | ✅ Sealed |
| #180 UAT | ✅ Sealed |
| #181 Accessibility | ✅ Sealed |
| #182 Performance | ✅ Sealed |
| #186 Privacy Assurance | ✅ Sealed |
| #187 Dependency Risk | ✅ Sealed |
| #188 Security Assurance | ✅ Sealed |
| Release Readiness Profile | ✅ Sealed |
| Validation Sprint | ✅ Complete |
| Post-Validation Decision Review | ✅ **Complete** |

## 6. Owner Decision Required

| Action | Recommended Classification | Authority Required? |
|--------|--------------------------|-------------------|
| Apply authority_level fix to #182 | ✅ Maintenance — proceed when convenient | No |
| Apply evidence reference fix to #188 | ✅ Maintenance — proceed when convenient | No |
| Cross-project validation | ⏸️ Defer | No |
| Freshness age-testing | ⏸️ Defer | No |
| Migrate #179–#182 to #185 | ⏸️ Defer | Yes, if pursued |
| QA Pilot → Librarian integration | ⏸️ Defer — requires value proposition | Yes |

---

*Document: QA-PILOT-POST-VALIDATION-DECISION-REVIEW.md*
*Status: Advisory | Owner decision required for non-maintenance items*
*Framework state: Stable — no expansion warranted*
