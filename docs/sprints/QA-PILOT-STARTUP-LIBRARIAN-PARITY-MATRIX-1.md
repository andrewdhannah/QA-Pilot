# QA-PILOT-STARTUP-LIBRARIAN-PARITY-MATRIX-1 — Sprint Receipt

**Sprint ID:** QA-PILOT-STARTUP-LIBRARIAN-PARITY-MATRIX-1
**Type:** Governance / documentation
**Lane:** parallel_planning
**Boundary:** QA Pilot-local only
**Librarian impact:** none (read-only comparison, no Librarian files modified)
**Input dependencies:** All sealed QA Pilot sprints (#1–19), Librarian startup-contract.json, Librarian PROJECT-STARTUP.md, Librarian governance profile, shared SessionStartup/* protocol docs

## Scope Satisfied

- Analyzed QA Pilot and Librarian startup contracts (startup-contract.json) for structural parity — 14 comparison dimensions (SC-1 through SC-14)
- Compared governance profiles (librarian-full-governance vs qa-pilot-full-governance) — 18 module statuses compared (GP-1 through GP-18)
- Compared lifecycle cursor states, phases, and transitions (LC-1 through LC-4)
- Compared MCP context acquisition tools and usage (MC-1 through MC-5)
- Compared PROJECT-STARTUP.md structure and content (PD-1 through PD-7)
- Compared startup checks scripts, validators, and state generation (CH-1 through CH-9)
- Compared output mode and report format contracts (OR-1 through OR-6)
- Compared session identity derivation rules (SI-1 through SI-4)
- Compared degraded mode handling and fallback docs (DM-1 through DM-3)
- Compared cross-project boundary definitions (XB-1 through XB-3)
- Categorized all findings as: ✅ Same, ⚠️ Divergent (by design), ❌ Gap, 🔍 Unknown
- Documented 6 gaps with priority and proposed actions (G-1 through G-6)
- Documented 8 intentional divergences with rationales (D-1 through D-8)
- Defined 5 invariants (PM-1 through PM-5) for maintaining parity over time
- Created parity matrix validator `scripts/validate-qa-pilot-startup-parity-matrix.py` (rules PM-1 through PM-12)
- Created governance doc at `docs/governance/QA-PILOT-STARTUP-LIBRARIAN-PARITY-MATRIX.md`
- Created sprint receipt at `docs/sprints/QA-PILOT-STARTUP-LIBRARIAN-PARITY-MATRIX-1.md`

## Coverage

| Section | Dimensions | Status |
|---------|-----------|--------|
| Startup Contract | 14 (SC-1 through SC-14) | 11 same, 3 gaps |
| Governance Profile | 18 (GP-1 through GP-18) | 18 same, 0 gaps |
| Lifecycle Cursor | 4 (LC-1 through LC-4) | 0 same, 4 divergent |
| MCP Context | 5 (MC-1 through MC-5) | 5 same, 0 gaps |
| Project Startup Doc | 7 (PD-1 through PD-7) | 1 same, 1 gap |
| Startup Checks | 9 (CH-1 through CH-9) | 8 same, 1 gap |
| Output Mode & Report | 6 (OR-1 through OR-6) | 6 same, 0 gaps |
| Session Identity | 4 (SI-1 through SI-4) | 4 same, 0 gaps |
| Degraded Mode | 3 (DM-1 through DM-3) | 2 same, 1 gap |
| Cross-Project Boundaries | 3 (XB-1 through XB-3) | 0 same, 3 divergent |

## Hard Boundaries Enforced

- ❌ No Librarian file mutation
- ❌ No cross-project writes
- ❌ No modification to sealed sprint ledger entries
- ❌ No modification to existing governance docs
- ❌ No startup contract changes (gaps noted for future sprints only)

## Next Authorized Sprint

G-1 through G-6 gap resolution — or Owner direction. The gaps identified in this matrix are:
- **G-1 (Medium):** Add mcp_context block to QA Pilot startup-contract.json
- **G-2 (Medium):** Add operational_state block to QA Pilot startup-contract.json
- **G-3 (Low):** Add fallback_docs to QA Pilot startup-contract.json
- **G-4 (Medium):** Add work identity binding rules to QA Pilot PROJECT-STARTUP.md
- **G-5 (Low):** Create QA Pilot-local `scripts/check-mcp-health.sh`
- **G-6 (Low):** Add fallback_docs to QA Pilot startup-contract.json (resolved by G-3)
