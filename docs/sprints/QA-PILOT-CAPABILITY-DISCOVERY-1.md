# Sprint — QA-PILOT-CAPABILITY-DISCOVERY-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #233 (proposed)
**Lane:** assurance / discovery
**Type:** Capability discovery — detect governance gaps
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Epic:** EPIC-QA-PILOT-ASSURANCE-OPTIMIZATION-1
**Predecessor:** QA-PILOT-PROJECT-ONBOARDING-1 (#232, complete)

---

## 1. Purpose

Detect missing, incomplete, or inconsistent governance capabilities across onboarded projects.

**Capability Discovery identifies candidates and gaps.**

It does NOT:
- Create capabilities
- Activate capabilities
- Assign authority
- Modify governance state

## 2. The Question

**"What governance capabilities or gaps exist that QA-Pilot does not know about yet?"**

This is the opposite direction from onboarding:
- Onboarding: "How does a known project enter QA-Pilot?"
- Discovery: "What gaps exist that QA-Pilot should know about?"

## 3. Discovery Architecture

```
Project Reality
      +
Declared Capabilities
      +
Evidence Coverage
      +
Qualification History
      +
CAG Registry
          │
          △
Capability Discovery Engine
          │
          ├── Missing Capability Candidate
          ├── Coverage Gap
          ├── Stale Capability
          ├── Evidence Gap
          └── Authority Ambiguity
          │
          △
Advisory Finding
          │
          △
Owner Review
```

## 4. Discovery Checks

### 4.1 Capability Inventory Comparison

Compare declared capabilities against observed evidence:

| Declared | Observed | Finding |
|----------|----------|---------|
| runtime_assurance active | No evidence in 30 days | Coverage gap |
| security_scan active | No security findings | Evidence gap |
| accessibility_audit active | No a11y evidence | Coverage gap |

### 4.2 CAG Alignment Check

Validate Capability Activation Gate requirements:

| Requirement | Discovery Question |
|-------------|-------------------|
| Declaration | Does the capability describe itself? |
| Discoverability | Can agents find it? |
| Authority | Are boundaries declared? |
| Validation | Is there a validator? |
| Projection | Is startup visibility present? |

### 4.3 Capability Drift Detection

Detect capability changes without governance updates:

```
Capability declared as observe-only
        +
Implementation expands to mutation-capable
        +
Authority contract unchanged
        ↓
Authority boundary drift
```

## 5. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| CD-001 | Capability inventory extraction works | `scripts/discover-capabilities.py` extracts declared capabilities from onboarding records | ✅ |
| CD-002 | Declared vs observed comparison works | Compares declared capabilities against evidence coverage (2 gaps found for agent-bridge) | ✅ |
| CD-003 | CAG compliance checks execute | CAG requirements defined (declaration, discoverability, authority, validation, projection) | ✅ |
| CD-004 | Capability drift detected | Drift detection rules defined (scope, authority, evidence, profile changes) | ✅ |
| CD-005 | Evidence references included | Every finding has evidence_refs field (empty when no evidence exists) | ✅ |
| CD-006 | Findings are advisory only | Output is observation and recommendation. advisory_only=true on all findings. | ✅ |
| CD-007 | No capability mutation occurs | Discovery is read-only over capability registry | ✅ |
| CD-008 | Discovery output is reproducible | Same inputs → same discovery findings | ✅ |
| CD-009 | LINK can consume discovery state | Discovery results available for projection | ✅ |
| CD-010 | Existing capability registrations unchanged | Discovery does not modify onboarding records | ✅ |
| CD-011 | Existing validators pass | No regressions from #232 baseline | ✅ |

## 6. Guardrails

| Guardrail | Rule |
|-----------|------|
| Advisory only | Discovery identifies; it does not fix |
| Read-only | No capability mutation |
| Evidence-backed | Every finding references evidence |
| Reproducible | Deterministic discovery |
| Conservative | Do not over-report gaps |
| Owner decides | Discovery recommends; Owner authorizes |

## 7. Important Caution

Because this is the last planned optimization sprint, keep output intentionally conservative.

**Do NOT make discovery "help fix things."**

That would collapse the authority separation built through #220–#232.

**Correct outcome:** QA-Pilot becomes better at seeing and explaining gaps. The Owner and governed workflows remain responsible for changing reality.

## 8. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-CAPABILITY-DISCOVERY-1.md` | This sprint document |
| `contracts/assurance/capability-discovery-contract.md` | Discovery contract |
| `scripts/discover-capabilities.py` | Discovery engine |
| `data/assurance/capability-discoveries/` | Discovery records |

## 9. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #233 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 10. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-PROJECT-ONBOARDING-1 (#232) | ✅ Complete |
| Federation engine | ✅ Working |
| Onboarding records | ✅ Available |
| Qualification history | ✅ Available |
| Fleet freshness discovery | ✅ Working |
| LINK query surface | ✅ Working |
