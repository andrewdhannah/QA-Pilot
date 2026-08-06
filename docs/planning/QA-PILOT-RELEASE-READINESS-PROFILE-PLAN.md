# Release Readiness Profile — Planning Definition

**Document:** Release Readiness Profile Planning  
**Status:** ✅ **SEALED — Planning defined, implementation complete, all 8 gates pass**  
**Preceding capabilities:** #179 ✅, #180 ✅, #181 ✅, #182 ✅, #183 ✅, #185 ✅, #186 ✅, #187 ✅, #188 ✅  
**Consumes:** #179, #180, #181, #182, #186, #187, #188  
**Next transition:** Invariant Review → Authorization → Implementation

---

## 1. Objective

Create a governed aggregation layer that answers:

> "What evidence exists about this release, what findings remain, and what decisions require Owner review?"

It must **not** answer:

> "Should this release ship?"

That remains an Owner decision.

---

## 2. Core Boundary

```
Release Readiness Assessment
        ≠
Release Decision
        ≠
Authorization
        ≠
Deployment Execution
```

The profile produces a readiness picture, not approval.

---

## 3. Architecture Position

```
QA Pilot Assurance Framework

Evidence Sources (#179–#188)
       |
       v
Release Readiness Profile (aggregation)
       |
       v
Owner Review
       |
       v
Release Decision (Owner-owned, not automated)
```

The profile is a **composition layer**, not a new scanner or assessment surface. It answers questions about evidence completeness and finding severity. It does not approve or block.

---

## 4. Input Sources

The profile consumes existing capability evidence — no new scans, no new assessments:

| Capability | Evidence File | Coverage |
|-----------|--------------|----------|
| #179 Regression | `data/regression-evidence.json` | Change detection, test coverage |
| #180 UAT | `data/uat-evidence.json` | Acceptance validation, scenario coverage |
| #181 Accessibility | `data/accessibility-evidence.json` | WCAG criteria, semantic elements |
| #182 Performance | `data/performance-baseline.json` | Response times, throughput, resource usage |
| #186 Privacy Assurance | `data/privacy-assurance-evidence.json` | Data handling, storage, third-party services |
| #187 Dependency Risk | `data/dependency-risk-evidence.json` | Dependency inventory, version analysis, risk findings |
| #188 Security Assurance | `data/security-assurance-evidence.json` | Dependency surface, data protection, auth, config, external services |

### Input Discovery Rules

- Each input is loaded by evidence file path
- If an evidence file is missing, it is recorded as `MISSING` — not assumed as PASS
- If an evidence file is stale (timestamp > 7 days), it is recorded as `STALE` — tagged with age
- The profile does not regenerate missing or stale evidence — it reports the gap

---

## 5. Output Model

### Schema

```json
{
  "assurance_report": {
    "profile": "release-readiness",
    "profile_name": "Release Readiness Profile",
    "version": "1.0.0",
    "release": "release-identifier",
    "generated_at": "ISO8601",
    
    "inputs": [
      {"capability": "#179", "file": "data/regression-evidence.json", "status": "AVAILABLE", "generated_at": "ISO8601"},
      {"capability": "#180", "file": "data/uat-evidence.json", "status": "AVAILABLE", "generated_at": "ISO8601"}
    ],
    
    "summary": {
      "capabilities_total": 8,
      "capabilities_available": 8,
      "capabilities_missing": 0,
      "capabilities_stale": 0,
      "total_findings": 45,
      "pass": 15,
      "observations": 22,
      "owner_decision_required": 8,
      "overall": "OBSERVATION"
    },
    
    "coverage": [
      {
        "capability": "#186",
        "status": "AVAILABLE",
        "overall": "OWNER_DECISION_REQUIRED",
        "generated_at": "2026-07-20T21:01:15",
        "findings_count": 6
      }
    ],
    
    "owner_decisions": [
      {
        "source": "#186",
        "finding": "Analytics patterns found in 19 file(s)",
        "classification": "OWNER_DECISION_REQUIRED",
        "evidence_reference": "data/privacy-assurance-evidence.json"
      }
    ],
    
    "authority_level": "advisory",
    "owner_action_required": true
  },
  
  "evidence_id": "RR-{date}-{seq}",
  "producer": "release_readiness_profile",
  "capacity": "Release Readiness",
  "consumable_by": "governance_view"
}
```

### Output Rules

- `overall` is the highest severity across all input capability summaries
- `owner_action_required: true` when any input capability has `overall: OWNER_DECISION_REQUIRED`
- All PASS findings carry no action — they are informational
- All OBSERVATION findings are listed for awareness — no action required
- All OWNER_DECISION_REQUIRED findings are explicitly surfaced in `owner_decisions` section
- The profile does not transform observations into failures automatically
- Evidence freshness is tracked per input — stale data is tagged, not assumed current

---

## 6. Assessment Model

### Coverage

| Question | How It's Answered |
|----------|------------------|
| Which assurance areas have evidence? | Listed in `coverage` array with AVAILABLE/MISSING/STALE status |
| Which capabilities are missing? | Capabilities in input list not found on disk → reported as MISSING |
| Are inputs current? | `generated_at` compared to report time → >7 days flagged as STALE |

### Findings Aggregation

| Input Classification | Profile Handling |
|---------------------|------------------|
| PASS | Counted, listed for completeness, no action |
| OBSERVATION | Counted, listed for Owner awareness |
| OWNER_DECISION_REQUIRED | Counted, listed in `owner_decisions` with source capability and evidence reference |

### Traceability

Every readiness finding maps back:

```
Release Finding
        ↓
Input Capability (e.g., #186)
        ↓
Profile (e.g., Privacy Assurance)
        ↓
Evidence Artifact (data/privacy-assurance-evidence.json)
```

---

## 7. Evidence Freshness

| Condition | Label | Behavior |
|-----------|-------|----------|
| Evidence file exists, generated within 7 days | `AVAILABLE` | Included normally |
| Evidence file exists, generated >7 days ago | `STALE` | Included but tagged with `stale: true`, `age_days` field |
| Evidence file does not exist | `MISSING` | Recorded in coverage; not assumed as PASS |
| Evidence file exists but is unparseable | `ERROR` | Recorded with error detail |

### Freshness Rule

The profile does **not** regenerate stale or missing evidence. It reports the gap honestly. The Owner decides whether to accept stale evidence or request regeneration.

---

## 8. Non-Goals

The Release Readiness Profile must **not**:

- Approve releases
- Block releases automatically
- Modify release artifacts
- Perform deployment
- Replace QA/security review
- Assign business risk acceptance
- Create compliance certification
- Add new assessment surfaces or scanners
- Transform observations into failures automatically
- Generate release notes
- Make ship/no-ship decisions

---

## 9. Acceptance Gates

| Gate | Requirement |
|------|-------------|
| RR-1 | Consumes #185 profile contract schema |
| RR-2 | All source evidence references preserved (each finding traces to source capability and file) |
| RR-3 | Missing evidence is visible (not silently assumed PASS) |
| RR-4 | Findings classifications preserved (PASS / OBSERVATION / OWNER_DECISION_REQUIRED) |
| RR-5 | No automatic release decision (no deployment approval or blocking) |
| RR-6 | Owner authority preserved (no auto-acceptance, no auto-remediation) |
| RR-7 | Evidence chain reconstructable (findings trace: release → capability → profile → artifact) |
| RR-8 | Output consumable by future governance views (`consumable_by` field) |

---

## 10. Assurance Framework Complete

After Release Readiness Profile:

```
QA Pilot Assurance Framework

Discovery Phase
       ↓
Assessment Profiles (#185)
       ↓
Individual Capabilities (#179–#188)
       ↓
Evidence Classification (PASS/OBSERVATION/OWNER_DECISION_REQUIRED)
       ↓
Release Readiness Profile (aggregation)
       ↓
Owner Review
       ↓
Release Decision (Owner-owned)
```

| # | Capability | Status |
|---|-----------|--------|
| #179 | Regression | ✅ Sealed |
| #180 | UAT | ✅ Sealed |
| #181 | Accessibility | ✅ Sealed |
| #182 | Performance | ✅ Sealed |
| #183 | Security Capability | ✅ Existing |
| #185 | Assurance Profile Architecture | ✅ Sealed |
| #186 | Privacy Assurance | ✅ Sealed |
| #187 | Dependency Risk | ✅ Sealed |
| #188 | Security Assurance | ✅ Sealed |
| — | **Release Readiness Profile** | **⏳ Planning defined — awaiting authorization** |

---

## 11. Next Valid Transition

**Release Readiness Profile Planning → Invariant Review → Authorization → Implementation.**

After authorization:
1. Implement aggregation logic — load all 8 capability evidence files
2. Compute coverage, findings summary, and owner decisions
3. Produce `data/release-readiness-evidence.json`
4. Verify all 8 acceptance gates (RR-1 through RR-8)

---

*Document: QA-PILOT-RELEASE-READINESS-PROFILE-PLAN.md*
*Capability: Release Readiness Profile | Status: Planning Definition Complete*
*Core boundary: Release Readiness Assessment ≠ Release Decision ≠ Authorization ≠ Deployment Execution*
