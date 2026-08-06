# QA-PILOT-REGRESSION-CAPABILITY-1 — Regression Testing Capability

**Type:** implementation / testing capability
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** implementation
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Architecture basis:** #178 (testing capability architecture, Phase 1)

---

## Purpose

Implement regression testing capability. Consumes sprint-ledger history, changed files, and previous evidence to produce impacted test selection and pass/fail evidence packages.

**Inputs:** sprint-ledger history, changed file detection, previous evidence receipts
**Outputs:** impacted regression suite, pass/fail matrix, evidence package
**Architecture pattern:** Generate → Validate → Execute → Capture → Classify → Output

---

## Scope

### Included

- Changed file detection against sprint baseline
- Impact analysis — which test suites are affected
- Regression execution harness
- Pass/fail matrix generation
- Evidence package output

### Non-Scope

- UAT scenarios
- Language/i18n testing
- Accessibility
- Performance
- Security

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| REG-1 | Changed file detection implemented |
| REG-2 | Impact analysis produces candidate suite |
| REG-3 | Regression execution harness functional |
| REG-4 | Pass/fail evidence generated |
| REG-5 | Output matches #178 evidence schema |
| REG-6 | Evidence produced |

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Ledger entry:** #179 (authorized)
