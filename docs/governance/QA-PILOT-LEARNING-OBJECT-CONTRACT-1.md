# QA Pilot Learning Object Contract — QA-PILOT-LEARNING-OBJECT-CONTRACT-1

**Sprint:** QA-PILOT-LEARNING-OBJECT-CONTRACT-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** Advisory only. Defines contract boundary — no authority conferred.

## 1. Purpose

Define the semantic contract between governed Librarian evidence and teaching/testing/certification artifacts. Establish what a "learning object" IS before any generator, adapter, or UI capability is built.

This is the equivalent of OE-002 for the teaching layer. OE-002 defined "what is a diagnostic finding." This defines "what is a learning object."

## 2. Architecture

```
Librarian Evidence Plane
        │
        │ SDK (read-only)
        ▼
Diagnostic Finding
        │
        ▼
Learning Object Contract        ← THIS WORK ORDER
        │
        ├── Learning content     (explanation, objectives)
        ├── Exercise scenario    (references, not inline)
        ├── Assessment refs      (quiz questions, scoring model)
        └── Certification        (criteria, passing score)
```

## 3. Invariants

| Invariant | Enforcement | Violation Risk |
|---|---|---|
| Learning objects reference evidence — they never create evidence | `source.evidence_refs` required; no embedded findings | Learning object becomes authority source |
| Diagnostic findings remain owned by Librarian | `source.finding_code` references, does not redefine | Duplicate truth |
| QA-Pilot certification evaluates understanding, not system correctness | `certification.criteria` describes knowledge assessment | QA-Pilot becomes a second seal authority |
| Certification criteria cannot imply Librarian seal authority | Forbidden terms in criteria descriptions | Authority boundary collapse |
| Existing V1.5 assets adapted through contract, not duplicated | `assessment.quiz_refs` references, does not embed | Content drift |

## 4. Schema

See `docs/schemas/learning-object-v1.schema.json` for the complete contract.

Key sections:

| Section | Required | Purpose |
|---|---|---|
| `source` | ✅ | Links learning object to governed evidence finding |
| `learning` | ✅ | Teaching content — explanation, objectives |
| `exercise` | ❌ | Scenario-based activity (required for `evaluateSubmission` scoring) |
| `assessment` | ✅ | Quiz references and scoring model |
| `certification` | ✅ | Evaluation criteria and passing threshold |

## 5. Scope (In scope)

1. `learning-object-v1.schema.json` — Draft 2020-12 JSON Schema
2. Valid and invalid fixtures
3. Deterministic validator (LO-1 through LO-12+ rules)
4. Contract tests
5. Governance document

## 6. Scope (Out of scope / Non-goals)

- ❌ No generator (Evidence-to-Lesson is future work)
- ❌ No scenario adapter (future work)
- ❌ No scoring.js integration (future work)
- ❌ No teaching UI
- ❌ No AI qualification

## 7. Acceptance Gates

| Gate | Criteria | Validated By |
|---|---|---|
| **LO-001** | Learning object references evidence — does not become evidence | `source.evidence_refs` required, no evidence creation fields |
| **LO-002** | `source.finding_code` maps to valid diagnostic-finding code | Pattern validation: `^EV-[A-Z]+-[0-9]{3,}$` |
| **LO-003** | `learning.explanation` is distinct from the finding — adds teaching context | Min length 20, checked for finding-text overlap |
| **LO-004** | `assessment.quiz_refs` reference existing quiz questions | References external IDs — not inline content |
| **LO-005** | `certification.criteria` does not overlap with Librarian seal authority | Forbidden terms checked (seal, approve, merge, authorize) |

## 8. Authority Boundaries

- **Librarian** owns evidence, provenance, and governance state
- **Learning Objects** reference evidence — they do not create it
- **Certification** evaluates understanding — not system correctness
- **No seal authority** — learning objects cannot be used to seal epics, approve changes, or authorize production releases

## 9. Files

| File | Description |
|---|---|
| `docs/schemas/learning-object-v1.schema.json` | The contract |
| `docs/governance/QA-PILOT-LEARNING-OBJECT-CONTRACT-1.md` | This governance document |
| `docs/examples/learning-object-v1/` | Valid and invalid fixtures |
| `scripts/validate-learning-object.py` | Validator |
| `scripts/test-learning-object.sh` | Test runner |

## 10. Dependencies

- **Requires:** QA-PILOT-SDK-INTEGRATION-1 (governed evidence access)
- **Requires:** QA-PILOT-EPIC-SCENARIO-SUITES (evidence validation)
- **Provides:** Contract boundary for Evidence-to-Lesson Generator, Scenario Adapter, Scoring Integration, AI Qualification
