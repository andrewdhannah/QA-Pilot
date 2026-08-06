# QA Pilot Training Content Model

**Sprint:** QA-PILOT-TRAINING-CONTENT-MODEL-1
**Epic:** EPIC-QA-PILOT-TRAINING-SYSTEM-1 (Sprint 4/11)
**Status:** complete_pending_owner_review

## Purpose

Define the 7 training artifact types, their schemas, examples, and validation rules. Every artifact must carry source references, intended audience, validation status, and ownership state.

## Artifact Types

| Type | Description | Audience | Exercises Required? |
|------|-------------|----------|-------------------|
| `onboarding_guide` | New project team introduction to governed work | onboarding | No |
| `operator_guide` | Day-to-day operational workflows | operator | No |
| `developer_guide` | How to extend governed projects | developer | No |
| `troubleshooting_guide` | Common failure modes and recovery | operator | No |
| `architecture_explanation` | System architecture overview | architect | No |
| `workflow_tutorial` | Step-by-step guided task walkthrough | developer | **Yes** |
| `validation_exercise` | Self-check quiz to verify understanding | all | **Yes** |

## Rules

| Rule | Description |
|------|-------------|
| CM-1 | schema_version must be 'training-content-v1' |
| CM-2 | artifact_type must be one of 7 known types |
| CM-3 | intended_audience must be valid |
| CM-4 | governance.authority_posture must be 'advisory' |
| CM-5 | governance.owner_decision_required_for_publish must be true |
| CM-6 | governance.validation_status must be valid |
| CM-7 | provenance.librarian_sources must have ≥1 entry |
| CM-8 | provenance.source_hash must be valid SHA-256 |
| CM-9 | Every section must have ≥1 source reference |
| CM-10 | validation_exercise and workflow_tutorial must have exercises |
| CM-11 | content.sections must have ≥1 section |
| CM-12 | No authority expansion patterns in content |
| CM-13 | No Librarian mutation paths in content |
| CM-14 | pack_id must match TC- pattern |

## Artifacts

| Path | Description |
|------|-------------|
| `docs/schemas/qa-pilot-training-content-model.schema.json` | Training pack schema (unified for all 7 types) |
| `scripts/validate-qa-pilot-training-content-model.py` | Validator (14 rules) |
| `scripts/test-qa-pilot-training-content-model.sh` | Test runner |
| `docs/examples/qa-pilot-training-content-model/` | 7 valid + 3 invalid fixtures |
| `docs/governance/QA-PILOT-TRAINING-CONTENT-MODEL.md` | This doc |
