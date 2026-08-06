# QA Pilot Evidence-to-Lesson Generator — QA-PILOT-EVIDENCE-TO-LESSON-GENERATOR-1

**Sprint:** QA-PILOT-EVIDENCE-TO-LESSON-GENERATOR-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review
**Authority:** Advisory only. Learning objects reference evidence; they do not create evidence.

## 1. Purpose

Prove the end-to-end translation pipeline: Diagnostic Finding → Learning Object → Lesson/Exercise/Assessment package. This is the smallest complete proof of the new teaching architecture.

## 2. End-to-End Pipeline

```
SDK (EvidenceProvider)
    │
    ├── getFindings()
    │
    ▼
Evidence Plane findings (13 diagnostic findings)
    │
    ▼
Evidence-to-Lesson Generator (deterministic, template-based)
    │
    ▼
Learning Objects (validated against learning-object-v1.schema.json)
    │
    ├── lesson content (explanation with educational context)
    ├── exercise scenario (finding-specific scenario)
    ├── assessment refs (quiz questions + scoring model)
    └── certification criteria (understanding, not system correctness)
    │
    ▼
Stored in data/learning-objects/
```

## 3. Generator Design

- **Deterministic:** Same finding input always produces same learning object output
- **Template-based:** Educational explanations use governed templates per finding category
- **No LLM:** No language model involved — content is constructed from finding metadata
- **Self-validating:** Every generated learning object is validated against the schema

### Category Templates

| Category | Template Source | Educational Analogy |
|---|---|---|
| CURSOR (EV-GOV-*) | Lifecycle cursor | Odometer reading / smoke alarm |
| RECONCILIATION (EV-EVID-*) | Evidence comparison | Balancing a checkbook |
| EPIC (EV-EVID-*) | Epic registry | Library catalog |
| RUNTIME PROVENANCE (EV-SRC-*) | Chain of custody | Forensic evidence bag |
| PROJECTION PROVENANCE (EV-PROJ-*) | Surface verification | Dashboard gauge |

## 4. Results

| Metric | Value |
|--------|-------|
| Findings processed | 13 available, 12 matched categories |
| Learning objects generated | 12 (all schema-valid) |
| Categories covered | CURSOR, RECONCILIATION, EPIC, SOURCE_STATE, PROJECTION_PROVENANCE |
| Schema validation rate | 100% |
| Pipeline stages | 3 (SDK → Generator → Validated LO) |

## 5. Generated Learning Objects

| ID | Source Finding | Category | Title |
|---|---|---|---|
| LO-EV-GOV-002-0001 | F-0001 | CURSOR | Understanding Gov 002 |
| LO-EV-GOV-001-0002 | F-0002 | CURSOR | Understanding Gov 001 |
| LO-EV-EVID-002-0005 | F-0005 | EPIC | Understanding Evid 002 |
| LO-EV-EVID-001-0008 | F-0008 | RECONCILIATION | Understanding Evid 001 |
| LO-EV-SRC-002-3001 | F-3001 | SOURCE_STATE | Understanding Src 002 |
| LO-EV-PROJ-003-5001 | F-5001 | PROJECTION_PROVENANCE | Understanding Proj 003 |
| + 6 more | | | |

## 6. Files

| File | Description |
|---|---|
| `scripts/qa_pilot_lesson_generator.py` | Generator — list, generate, output commands |
| `data/learning-objects/LO-*.json` | Generated learning objects (3 reference samples) |
| `docs/governance/QA-PILOT-EVIDENCE-TO-LESSON-GENERATOR-1.md` | This governance document |

## 7. Next

| Phase | Work Order | When |
|---|---|---|
| 2C | QA-PILOT-SCENARIO-ADAPTER-1 | Connect scoring.js to governed LO data |
| 2D | QA-PILOT-AI-QUALIFICATION-1 | AI performs scenario, QA-Pilot evaluates |
