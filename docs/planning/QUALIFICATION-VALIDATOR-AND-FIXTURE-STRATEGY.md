# Qualification Validator & Fixture Strategy

**Part of:** QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1
**Tier:** T2 (Required for Operationalization)
**Prepared:** 2026-07-16

---

## 1. Validator Architecture

Following the established QA Pilot pattern:

```
scripts/validate-qa-pilot-qualification.py
├── Mode: fixture       # Validate fixture files against schema + rules
├── Mode: live          # Validate live qualification store
├── Mode: validate      # Validate a specific qualification record
└── Mode: chain         # Run all upstream validators for regression
```

### Validation Rule Groups

| Group | Rules | Scope |
|-------|-------|-------|
| **QR-1–QR-5** | Schema compliance | Record structure, required fields, type constraints |
| **QR-6–QR-10** | Authority boundary | advisory_only, custody, librarian_impact, no authority claims |
| **QR-11–QR-15** | Evidence integrity | evidence_refs resolve, not stale, not missing, not corrupted |
| **QR-16–QR-20** | Qualification logic | level matches score, level meets minimum, expiry valid |
| **QR-21–QR-25** | Provenance | assessor_id present, session_id present, tool_call_log present |

### 25 Validation Rules (QR-1 through QR-25)

| Rule | Description | Severity |
|------|-------------|----------|
| QR-1 | Must be valid JSON Schema Draft 2020-12 | error |
| QR-2 | All required fields present | error |
| QR-3 | record_id matches pattern QR-[A-Z0-9]{8}-[0-9]{4} | error |
| QR-4 | qualification_type is valid enum | error |
| QR-5 | target_type is valid enum | error |
| QR-6 | advisory_only must be true | error |
| QR-7 | custody must be qa-pilot-local | error |
| QR-8 | librarian_impact must be none | error |
| QR-9 | No forbidden authority-claiming fields | error |
| QR-10 | qualification_level in valid enum | error |
| QR-11 | evidence_refs array must have at least 1 item | warning (0 = unqualified) |
| QR-12 | Each evidence_ref must have evidence_id | error |
| QR-13 | Each evidence_ref must have verification_status | error |
| QR-14 | No stale evidence (>90d from verified_at) | warning |
| QR-15 | evidence_source path must exist | error |
| QR-16 | overall_score must be 0.0–1.0 | error |
| QR-17 | level matches score range (0.80+ = spot_checked, 0.90+ = peer_reviewed, 0.95+ = audited) | warning |
| QR-18 | If level is audited, must have ≥3 evidence_refs | warning |
| QR-19 | expiry_date must be in the future | warning |
| QR-20 | If superseded_by set, target must exist | error |
| QR-21 | assessed_at must be valid date-time | error |
| QR-22 | assessed_by must be non-empty | warning |
| QR-23 | provenance.assessor_id must be present | warning |
| QR-24 | provenance.session_id must be present | warning |
| QR-25 | If qualification_type is reviewer, evidence_refs must include owner_decision | warning |

## 2. Fixture Strategy

### Fixture Taxonomy

```
docs/examples/qa-pilot-qualification/
├── valid/
│   ├── artifact-spot-checked.json          # Artifact, spot_checked level
│   ├── artifact-peer-reviewed.json         # Artifact, peer_reviewed level
│   ├── artifact-audited.json               # Artifact, audited level
│   ├── process-peer-reviewed.json          # Process, peer_reviewed level
│   ├── reviewer-audited.json               # Reviewer, audited level
│   ├── exempt-by-policy.json               # Exempt target
│   └── unqualified-no-evidence.json        # Unqualified (valid state)
│
└── invalid/
    ├── missing-required-field.json         # QR-2 violation
    ├── authority-claiming.json             # QR-9 violation
    ├── bad-custody.json                    # QR-7 violation
    ├── stale-evidence.json                 # QR-14 violation
    ├── bad-level-for-score.json            # QR-17 violation
    ├── audited-insufficient-evidence.json  # QR-18 violation
    ├── expired-qualification.json          # QR-19 violation
    └── reviewer-no-decision-evidence.json  # QR-25 violation
```

### Fixture Count Target

| Category | Expected Fixtures | Purpose |
|----------|------------------|---------|
| Valid | 7 | Cover all qualification levels + all 3 types + exempt |
| Invalid | 8 | Cover top 8 QR rule violations |
| **Total** | **15** | Verification of validator completeness |

## 3. Test Runner Strategy

```
scripts/test-qa-pilot-qualification.sh
├── 17 acceptance gates
│   ├── AG-1  to AG-7:   Valid fixture validation (7 tests)
│   ├── AG-8  to AG-15:  Invalid fixture rejection (8 tests)
│   └── AG-16 to AG-17:  Schema validation + boundary checks
```

## 4. Upstream Validator Integration

When deployed, the qualification validator must be added to the chain sweep:

```
Existing QA Pilot validator chain:
  QA-PILOT-STARTUP-REGRESSION-SUITE-1 (#22)
  → QA-PILOT-PIPELINE-HEALTH-REGRESSION-1 (#38)
  → QA-PILOT-PIPELINE-DRIFT-DETECTION-1 (#39)
  → QA-PILOT-STARTUP-SURFACE-REGRESSION-SNAPSHOT-1 (#56)
  → QA-PILOT-SNAPSHOT-UPDATE-GATE-1 (#57)
  → NEW: QA-PILOT-QUALIFICATION-VALIDATOR (planned)
```
