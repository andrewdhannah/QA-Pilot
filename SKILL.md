---
name: qa-pilot-validation
displayName: QA Pilot Validation
description: "Governed quality assurance framework for AI-assisted product work. Provides structured QA lanes, evidence collection, manual verification scripts, and readiness assessments. Advisory-only validation execution environment."
version: "1.0.0"
author: "Andrew Hannah"
license: "MIT"
tags:
  - qa
  - quality-assurance
  - validation
  - testing
  - harness-governed
category: "validator"
sourceType: "user"
sourceReference: "https://github.com/andrewdhannah/qa-pilot-v2"
---

# QA Pilot Validation

## Purpose

QA Pilot is a governed quality assurance framework for AI-assisted product work. It provides:

- Structured QA lanes (evidence checklist, manual verification, readiness assessment)
- Evidence collection and receipt production
- Manual verification scripts
- Readiness assessments
- Advisory-only validation execution (does not grant approval authority)

## Capability Type

**validator** — This capability performs validation and quality assurance tasks.

## Authority

- **Advisory-only**: QA Pilot produces evidence and recommendations. It does not approve, seal, grant merge authority, assert production readiness, or enforce runtime custody.
- **Owner retains final authority**: All seal decisions remain with the Owner.
- **Harness-governed**: QA Pilot operates as a separate add-on project with its own ledger, receipts, status surfaces, and governance.

## Execution Target

- **Project**: `qa-pilot`
- **Routing**: Project selector protocol (`start qa-pilot`)
- **Validation commands**: `python3 scripts/validate-qa-pilot-delegation.py`

## Evidence Production

QA Pilot produces receipts conforming to `qa-pilot-receipt.schema.json` with:
- Packet type: QAProductionReceipt, QAProductionEvidenceReceipt, QAProductionVerificationReceipt, QAProductionReadinessReceipt
- Authority: advisory
- Evidence kinds: document_review, fixture_validation, validator_output, command_output, screenshot_reference, human_observation, repository_status, receipt_reference, schema_validation, hash_verification
- Results: pass, partial_pass, fail, blocked, inconclusive
- Recommendations: proceed, proceed_with_caveats, request_revision, owner_review_required, do_not_proceed

## Integration with Sprint Validation Contract

When a sprint declares a validation requirement with `capability_type: "testing"` and `capability_refs: ["qa-pilot-validation"]`:

1. **Planning phase**: Capability Registry query discovers `qa-pilot-validation`
2. **Routing**: Execution Runtime routes to QA Pilot via project selector
3. **Execution**: QA Pilot runs validation against sprint artifacts
4. **Evidence**: QA Pilot receipt attaches to sprint evidence
5. **Seal eligibility**: Sprint completion checks for validation receipt before Owner seal

## Non-Goals

- Does not redesign QA Pilot
- Does not merge QA Pilot into Librarian
- Does not make QA Pilot the authority
- Does not replace existing tests
- Does not require every sprint to use identical validation
- Does not automate Owner approval

## Security Classification

- **S2**: Code generation, testing, sandboxed tool execution
- **Runtime isolation proof**: Required
- **Capability manifest**: Required
- **Ephemeral runtime**: No persistent credentials

## Qualification Profile

- **Profile**: TESTING-001
- **Policy**: ADVISORY-OR-EXECUTION
- **Checks**: boundary-compliance, token-discipline, evidence-linkage, canonical-rule-compat, mutation-detection, advisory-authority-check

## Dependencies

- Librarian Capability Registry (discovery)
- Librarian Project Selector (routing)
- Librarian Receipt Store (evidence linkage)
- QA Pilot project (execution environment)