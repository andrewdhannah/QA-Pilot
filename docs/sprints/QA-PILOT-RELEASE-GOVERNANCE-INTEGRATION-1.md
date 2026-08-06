# QA-PILOT-RELEASE-GOVERNANCE-INTEGRATION-1 — Release Governance Integration

**Type:** implementation / governance integration
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** assurance
**Boundary:** QA Pilot-local, Librarian advisory boundary
**Dependencies:** #195 (automation refinement)

---

## Purpose

Connect assurance evidence to the release governance lifecycle. Creates a structured link between commit → assurance execution → evidence package → risk context → Owner release decision → decision receipt.

---

## Scope

### Included

| # | Area | Action |
|---|------|--------|
| 1 | Release candidate binding | Link commit to assurance evidence package |
| 2 | Decision surface generation | Produce structured Owner decision package from readiness profile |
| 3 | Decision receipt integration | Record Owner decision reference in assurance history |
| 4 | Evidence package attachment | Package all capability evidence for release decision |

### Non-Scope

- Automated release approval/rejection
- Deployment automation
- CI/CD integration
- Change approval

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| RG-1 | Release candidate bound to assurance evidence |
| RG-2 | Decision surface generated from readiness profile |
| RG-3 | Decision receipt reference recorded in history |
| RG-4 | Evidence package attached to release context |
| RG-5 | No automated release decisions |
| RG-6 | Evidence produced |

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Ledger entry:** #196 (authorized)
