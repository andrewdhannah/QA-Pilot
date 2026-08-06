# QA Pilot Validation Profile Contract — QA-PILOT-VALIDATION-PROFILE-CONTRACT-1

**Sprint:** QA-PILOT-VALIDATION-PROFILE-CONTRACT-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review
**Authority:** Advisory only. Profiles route validation; they do not confer authority.

## 1. Purpose

Bridge project startup to QA-Pilot validation by defining what testing applies to a given project, which domains are enabled, which contracts are referenced, and what review gates are required.

This is the equivalent of OE-002 (what is a finding) or the learning-object-v1 (what is a lesson) for the operational layer: **what validation profile applies to this project?**

## 2. Architecture

```
STARTUP CONTRACT
    │
    │ "QA-Pilot is available for this project"
    │
    ▼
VALIDATION PROFILE (this contract)
    │
    │ profile: release-validation-v1
    │ domains: regression, security, uat, accessibility, ai
    │ reviews: owner
    │ contracts: learning-object-v1, sdk, epic-scenario
    │ pipeline: run-pipeline
    │
    ▼
QA-PILOT PIPELINE
    │
    │ executes enabled domains
    │ produces validation package
    │ routes to reviewer
    │
    ▼
OWNER REVIEW
```

## 3. Default Profiles by Project Type

| Project Type | Default Domains | Review Gate |
|---|---|---|
| `governance` | regression, security, uat, accessibility, ai | Owner |
| `mcp_bridge` | regression, security | Owner |
| `add_on` | regression, security, uat | Owner |
| `extension` | regression, security | Owner |
| `runtime` | regression, security, performance | Owner |
| `tracker` | regression | Peer |
| `external` | regression | Automated |

## 4. Existing Profiles

| Project | Profile ID | Domains | Status |
|---|---|---|---|
| Librarian | VP-LIBRARIAN-001 | 5 (regression, security, uat, accessibility, ai) | ✅ VP rules pass |
| Agent Bridge | VP-AGENT-BRIDGE-001 | 2 (regression, security) | ✅ VP rules pass |

## 5. Results

| Metric | Value |
|--------|-------|
| Schema | `qa-project-validation-profile-v1` |
| Validator rules | 8 (VP-1 through VP-8) |
| Profiles created | 2 (Librarian, Agent Bridge) |
| Profile validator | ✅ All 8 rules pass on both profiles |

## 6. Files

| File | Description |
|---|---|
| `docs/schemas/qa-project-validation-profile.schema.json` | Profile schema |
| `docs/governance/QA-PILOT-PROJECT-VALIDATION-PROFILE-CONTRACT.md` | Full contract document |
| `docs/governance/QA-PILOT-VALIDATION-PROFILE-CONTRACT-1.md` | This work order governance doc |
| `profiles/librarian-validation-profile.json` | Librarian profile (5 domains) |
| `profiles/agent-bridge-validation-profile.json` | Agent Bridge profile (2 domains) |
| `scripts/validate-qa-pilot-validation-profile.py` | 8-rule profile validator |

## 7. QA-Pilot Complete State

| Phase | Work Orders | Status |
|---|---|---|
| Infrastructure Boundary | 4 | ✅ |
| Teaching Capability | 5 | ✅ |
| Qualification | 1 | ✅ |
| Portability | 1 | ✅ |
| Production Hardening | 1 | ✅ |
| Operational Proof | 1 | ✅ |
| Governance Maintenance | 1 | ✅ |
| Expansion | 1 | ✅ |
| External Pilot | 1 | ✅ |
| Test Domain Expansion | 1 | ✅ |
| Continuous Pipeline | 1 | ✅ |
| **Validation Profile Contract** | **1** | **✅ ← Complete** |
| **Total** | **20** | **All sealed** |
