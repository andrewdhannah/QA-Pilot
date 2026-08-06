# QA Pilot Visual Integration Contract — QA-PILOT-VISUAL-INTEGRATION-CONTRACT-1

**Sprint:** QA-PILOT-VISUAL-INTEGRATION-CONTRACT-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review
**Authority:** Advisory only. Defines presentation contract — no authority conferred.

## 1. Purpose

Define how QA-Pilot (and all future add-ons) consume the Librarian presentation system without creating parallel UI authority. Establish the Add-on Visual Contract as the governed boundary between data layer and user-facing surface.

## 2. Architecture

```
Librarian Design System
    ├── Public/theme.css (tokens)
    ├── Public/styles.css (components)
    ├── V1X-DESIGN-LANGUAGE.md (principles)
    └── LIBRARIAN-DESIGN-SYSTEM.md (system)
            │
            │ ADD-ON-VISUAL-CONTRACT (this work order)
            ▼
QA-Pilot / Add-on surfaces
    │
    ├── Consumes shared CSS (compulsory)
    ├── Uses governed components (compulsory)
    ├── Preserves authority boundaries (compulsory)
    └── Exposes provenance (compulsory)
```

## 3. Scope (In scope)

1. `docs/governance/ADD-ON-VISUAL-CONTRACT.md` — the platform-level visual contract
2. `scripts/validate-addon-visual-contract.py` — deterministic validator (5 rules)
3. Governance document for the work order (this file)
4. Visual compliance mapping for QA-Pilot's existing academy pages

## 4. Scope (Out of scope / Non-goals)

- ❌ No UI rebuild of QA-Pilot
- ❌ No CSS system creation
- ❌ No framework migration
- ❌ No new components — the contract defines how to use existing ones

## 5. Acceptance Gates

| Gate | Rule | Validation |
|---|---|---|
| **VIS-001** | Shared CSS loaded | QA-Pilot HTML references `theme.css` and `styles.css` |
| **VIS-002** | No duplicate tokens | No `:root` redefinition of `--color-*`, `--space-*`, `--text-*` core tokens |
| **VIS-003** | Status semantics match | Status classes use governed state names (ok, pending, blocked, error, neutral) |
| **VIS-004** | Provenance visible | Evidence-backed surfaces have `.view-data-footer` with source chips |
| **VIS-005** | Authority-safe text | No forbidden authority language (seal, approve, merge, authorize as action verbs) |

## 6. Required Invariants

```
Add-on consumes theme.css + styles.css          → Mandatory
Add-on uses :root tokens without redefining     → Mandatory
Status badges map to platform semantics         → Mandatory
Provenance footers on evidence surfaces         → Mandatory
No UI language implying add-on authority        → Mandatory
```

## 7. Files

| File | Location | Description |
|---|---|---|
| ADD-ON-VISUAL-CONTRACT.md | `active/librarian/docs/governance/` | Platform-level visual contract |
| validate-addon-visual-contract.py | `active/librarian/scripts/` | Visual contract validator |
| QA-PILOT-VISUAL-INTEGRATION-CONTRACT-1.md | `active/qa-pilot/docs/governance/` | This governance document |

## 8. Dependencies

- **Requires:** LIBRARIAN-DESIGN-SYSTEM.md (design system)
- **Requires:** V1X-DESIGN-LANGUAGE.md (visual language)
- **Requires:** Public/theme.css (design tokens)
- **Requires:** Public/styles.css (components)
- **Provides:** Presentation contract for QA-PILOT-SCENARIO-ADAPTER-1, QA-PILOT-AI-QUALIFICATION-1
