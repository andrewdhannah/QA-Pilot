# CAPABILITY-ACTIVATION-AUDIT-001 — Work Order Record

**Finding ID:** LIBRARIAN-QA-CAPABILITY-ACTIVATION-001
**Status:** OWNER DECISION REQUIRED
**Created:** 2026-08-17
**Session:** 3ed10fbb-2791-43f0-ada5-26cff8591c1b

---

## Purpose

Cross-system capability activation audit to determine which Librarian capabilities participate in governed execution.

## Phases Completed

| Phase | Status | Deliverable |
|-------|--------|-------------|
| Phase 1 — Baseline | COMPLETE | Activation matrix (43 capabilities classified) |
| Phase 2 — Characterization | COMPLETE | Disposition matrix (13 capabilities characterized) |
| Phase 3 — Remediation | NOT AUTHORIZED | Awaiting Owner decision |

## Key Findings

1. **System is not primarily dead code.** 55% ACTIVE, 18% AVAILABLE.
2. **Implementation maturity exceeds activation maturity.** Capabilities exist but are not connected to governed execution paths.
3. **Single-point architectural defect.** `GeneratedMCPDispatchMap.swift` has `handlerFunction: "unknown"` for every tool. Affects 7+ broken tools.
4. **Authorization flow (B2) is unwired.** Three competing implementations; OwnerDecision never injected upstream.

## Disposition Matrix

| Disposition | Count | Description |
|-------------|-------|-------------|
| CONNECT | 8 | Fix dispatch wiring, serialization, or lookup paths |
| CONNECT + CONSOLIDATE | 1 | Wire OwnerDecision into authorization path (B2) |
| KEEP + COMPLETE | 1 | Owner decisions needed for 3 entities |
| DEPRECATE + RE-REGISTER | 1 | Remove hollow extension, re-register via hardened path |

## Remediation Candidates

| Priority | Capability | Effort |
|----------|-----------|--------|
| P0 | `addon_qualify_for_migration` | Low |
| P0 | `project_validate_profile` | Low |
| P0 | `get_standard_profile` | Low |
| P1 | QA-Pilot Cursor Deadlock | Low |
| P1 | Knowledge Substrate MCP | Low |
| P1 | `extension_verify_manifest_hash` | Low |
| P1 | `capability_evidence_agent_usage` | Medium |
| P1 | `capability_evidence_task_history` | Medium |
| P2 | `addon_get_identity` | Medium |
| P2 | Extension Lifecycle | Medium |
| P2 | Librarian Cursor Corruption | Medium |
| P2 | Entity Lifecycle Phases | Medium |
| P3 | Authorization Flow (B2) | High |

## Owner Decision Required

Authorize one of:
1. P0 remediation (3 low-effort fixes)
2. P1 remediation (5 tools, cursor + dispatch map)
3. P2 remediation (extension + cursor + entities)
4. P3 remediation (authorization flow consolidation)
5. Close and defer (preserve findings without remediation)

## Evidence

- Audit report: `audits/capability-activation-audit-2026-08-17.md`
- Governance audit: `audits/governance-audit-2026-08-16.md`
- Feature status: `FEATURE-STATUS.md`

---

*Record created by OpenWork-Claude (mimo-v2.5) on 2026-08-17*
