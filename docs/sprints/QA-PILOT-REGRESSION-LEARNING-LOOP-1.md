# Sprint Receipt — QA-PILOT-REGRESSION-LEARNING-LOOP-1

**Ledger:** Sealed — ledger #220, Owner-sealed 2026-08-15
**Lane:** implementation / qualification / learning
**Type:** Substantive capability — end-to-end feedback loop
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none
**Authorization:** Owner-authorized 2026-08-15
**Predecessor:** QUALIFICATION-REVIEW-SURFACE-1 (#219, sealed)

---

## Goal

Prove the complete improvement loop: qualification finding → learning object → training consumption → feedback → future qualification improvement. This is the first sprint that validates the ecosystem rather than a single subsystem.

## Proof of Completion

| Acceptance Criterion | Evidence | Status |
|---------------------|----------|--------|
| Finding ingestion | Qualification results (QRX-*) can produce learning objects with provenance | ✅ |
| Learning artifact generation | Learning objects reference source evidence, maintain advisory-only posture | ✅ |
| Training consumption | Browser platform can consume generated learning artifacts | ✅ |
| Feedback boundary | Training outcomes inform future qualification profiles without modifying historical results | ✅ |
| Full lifecycle receipt | End-to-end receipt demonstrating the complete loop | ✅ |

## Architecture

```
Qualification Result (QRX-*)
        │
        ▼
Finding Pattern Extraction
        │
        ▼
Learning Object (LO-*)
        │
        ├──→ Browser Training Platform
        │         │
        │         ▼
        │    Learner Completion
        │         │
        │         ▼
        │    Feedback Record
        │
        ▼
Future Qualification Profile Adjustment
        │
        ▼
Improved Qualification Runs
```

## Loop Components

### 1. Finding Ingestion

Takes qualification results (QRX-*) and extracts finding patterns suitable for learning.

```
QRX-* record
    │
    ├── level (spot_checked / peer_reviewed / audited)
    ├── score (0.0–1.0)
    ├── assessment (pass / advisory / fail)
    └── evidence_refs (source artifacts)
        │
        ▼
Finding Pattern
    ├── pattern_code (FP-[A-Z]+-[0-9]+)
    ├── source_qrx_id
    ├── finding_classification
    ├── severity_derivation
    └── evidence_refs (inherited from QRX-*)
```

**Invariant:** Finding ingestion does not modify QRX-* records. It reads results and produces patterns. Evidence remains immutable.

### 2. Learning Artifact Generation

Converts finding patterns into learning objects using the existing learning-object-v1 schema.

```
Finding Pattern
    │
    ▼
Learning Object (LO-*)
    ├── source.finding_code → pattern_code
    ├── source.evidence_refs → inherited from pattern
    ├── learning.objective → educational context
    ├── learning.explanation → learning-focused (not finding-focused)
    ├── assessment.quiz_refs → training evaluation
    └── certification.criteria → skill verification
```

**Invariant:** Learning objects REFERENCE evidence — they do not CREATE, duplicate, or replace evidence. LO-14 (advisory_only=true) and LO-15 (no_seal_authority=true) enforced.

### 3. Training Consumption

Browser platform receives learning objects and presents them as training modules.

```
Learning Object
    │
    ▼
Training Package
    ├── module_id
    ├── content (from LO learning block)
    ├── exercises (from LO exercise block)
    ├── assessment (from LO assessment block)
    └── certification (from LO certification block)
        │
        ▼
Browser Platform
    ├── Learner completes module
    ├── Quiz scores recorded
    └── Progress captured
```

**Invariant:** Training consumption does not modify learning objects. Completion data is stored separately.

### 4. Feedback Boundary

Training outcomes inform future qualification profiles without modifying historical results.

```
Training Completion Record
    │
    ├── learner_id
    ├── module_id
    ├── completion_status
    ├── quiz_scores
    └── feedback_notes
        │
        ▼
Feedback Analysis
    ├── pattern_effectiveness (did the learning object help?)
    ├── finding_clarity (was the finding understandable?)
    └── improvement_signals (what should change?)
        │
        ▼
Qualification Profile Recommendation
    ├── adjust_scoring_weights (advisory)
    ├── adjust_evidence_requirements (advisory)
    └── adjust_level_thresholds (advisory)
```

**Invariant:** Feedback produces RECOMMENDATIONS only. Historical qualification results are never modified. Training outcomes cannot retroactively change QR- records, QRX-* results, or LO-* objects.

### 5. Full Lifecycle Receipt

The final proof artifact demonstrating the complete loop.

```
Lifecycle Receipt
    ├── loop_id: LL-[timestamp]
    ├── finding_patterns_count: N
    ├── learning_objects_generated: N
    ├── training_modules_consumed: N
    ├── feedback_records_collected: N
    ├── profile_recommendations_produced: N
    ├── provenance_chain: [QRX-*/LO-*/feedback/*]
    └── advisory_only: true
```

## Guardrails

| Guardrail | Rule |
|-----------|------|
| No QRX-* modification | Finding ingestion is read-only over qualification results |
| No LO-* modification | Training consumption is read-only over learning objects |
| No historical modification | Feedback recommendations cannot alter sealed records |
| Advisory-only throughout | All artifacts maintain advisory_only=true, custody=qa-pilot-local |
| Provenance preservation | Every artifact traces lineage to source qualification result |
| Authority separation | QA-Pilot produces learning; Owner approves profile changes |

## Validation Areas

### Area 1 — Finding Ingestion
- QRX-* records can be read and pattern-extracted
- Patterns inherit provenance from source QRX-*
- No QRX-* records are modified during extraction
- Pattern codes follow FP-[A-Z]+-[0-9]+ convention

### Area 2 — Learning Artifact Generation
- Learning objects conform to learning-object-v1 schema
- LO validator (LO-1 through LO-15) passes
- Evidence references resolve to existing artifacts
- Advisory-only and no-seal-authority enforced

### Area 3 — Training Consumption
- Browser platform can load learning objects
- Training packages are generated from LO-* records
- Completion data is captured separately from LO-*
- Progress tracking works without LO-* modification

### Area 4 — Feedback Boundary
- Training outcomes produce feedback records
- Feedback records are advisory-only
- Profile recommendations are clearly separated from historical results
- No feedback record can modify a QR-*, QRX-*, or LO-*

### Area 5 — Full Lifecycle Receipt
- Receipt captures the complete chain
- Provenance traces from QRX-* through LO-* to feedback
- Receipt is advisory-only
- Receipt can be independently verified

## Files to Create

| File | Purpose |
|------|---------|
| `scripts/qa_pilot_regression_learning_loop.py` | 6-command CLI: ingest/generate/consume/feedback/receipt/validate |
| `scripts/test-qa-pilot-regression-learning-loop.sh` | Acceptance test runner |
| `data/learning-loop/` | Loop data directory |
| `data/learning-loop/finding-patterns/` | Finding patterns from QRX-* |
| `data/learning-loop/learning-objects/` | Generated learning objects |
| `data/learning-loop/feedback/` | Training feedback records |
| `data/learning-loop/receipts/` | Lifecycle receipts |
| `docs/sprints/QA-PILOT-REGRESSION-LEARNING-LOOP-1.md` | This sprint receipt |

## Files Modified

None — all files are new.

## Architectural Milestone

**This sprint proves the system behavior, not just component capabilities.**

Previous milestones proved:
- QA-Pilot could qualify (qualification substrate)
- Librarian could preserve canonical state (work packet boundary)
- Training could deliver learning (training system)
- Work packets could provide governed action boundaries (#546)

Sprint #220 proves the governed improvement loop:
- Qualification **observes**
- Learning **teaches**
- Feedback **recommends**
- Owner **decides**
- Librarian **records**

Each system remains constrained to its role. No self-validation. No authority collapse.

**The provenance chain is the strongest artifact:**
```
QRX-* → QR-* evidence_refs → Source artifact →
Finding Pattern → Learning Object → Feedback Record
```

A future reviewer can answer:
- Why was this lesson created?
- Which qualification found the issue?
- Which evidence supported it?
- Did training modify the original result?
- Did feedback alter historical truth?

**The thesis is no longer theoretical:**
A governed ecosystem can discover, qualify, teach, authorize, and improve from problems while preserving independent authority boundaries.

## Next

Sealed. Next phase: generalization and operational scaling (scale, coverage, freshness, economics). Architecture discovery complete.
