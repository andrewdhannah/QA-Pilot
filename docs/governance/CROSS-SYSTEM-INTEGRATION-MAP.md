# Cross-System Integration Map: QA-Pilot ↔ Librarian

**Document type:** Integration architecture  
**Status:** ✅ **Owner-authorized 2026-08-15**  
**Date:** 2026-08-15  
**Purpose:** How retroactive qualification becomes a standard operating mode across both systems, discoverable by agents and usable in sprint planning with LINK.

---

## What Already Exists

### Librarian Infrastructure (Ready)

| Infrastructure | Location | Maturity | Cross-Project Ready |
|---------------|----------|----------|-------------------|
| **14 governance service modules** | `governance-implementations/` | High | Yes — patterns are generic |
| **Project Index (10 projects)** | `project-state/project-index.json` | High | Yes — QA-Pilot listed |
| **Sprint Ledger (10,593 lines)** | `project-state/sprint-ledger.json` | High | Yes — ledger-derived indexes available |
| **Capability Qualification Contract** | `docs/governance/CAPABILITY-QUALIFICATION-CONTRACT-1.md` | Defined | Yes — 31 registered, 0 qualified (correct state) |
| **Regression Qualification Registry** | `project-state/regression-qualification-registry.json` | High | Yes — 4 qualified capabilities tracked |
| **LINK (interpretation layer)** | 8+ governance docs, MCP surface | High | Yes — intended bridge |
| **Cross-Project Memory Boundaries** | `docs/architecture/cross-project-memory-boundaries.md` | Defined | Yes — 5 boundary rules |
| **Global Cross-Project Planning Mode** | `STARTUP-INTENT-AUTHORIZATION-PROTOCOL.md` | Implemented | Yes — `start planning` intent |
| **Receipt External Reader** | `governance-implementations/receipt_external_reader.py` | Implemented | Yes — 4 governance dimensions |
| **Sprint Import Guard** | `governance-implementations/sprint_import_guard.py` | Implemented | Yes — import classification |
| **Validation Harness (450 lines)** | `scripts/run-validation-harness.sh` | High | Yes — QA-PROOF-1 category exists |
| **Honest Reporting Standard** | `docs/rules/TESTING-COMPLETION-HONESTY-STANDARD.md` | Defined | Yes — binding on all agents |
| **68 Epic Contracts** | `docs/governance/epic-packets/` | High | Yes — qualification targets |

### QA-Pilot Infrastructure (Ready)

| Infrastructure | Location | Maturity | Cross-Project Ready |
|---------------|----------|----------|-------------------|
| **Target Adapter Contract** | `contracts/target-adapter-v1.schema.json` | Implemented | Yes — adapter is the only coupling point |
| **Knowledge Adapter** | `scripts/qa_pilot_knowledge_adapter.py` | Implemented | Yes — read-only bridge to Librarian |
| **Broker Layer** | `scripts/librarian_broker_qa_pilot.py` | Implemented | Yes — 10 custody conditions |
| **Work Proposal Contract** | `docs/governance/QA-PILOT-WORK-PROPOSAL-CONTRACT.md` | Defined | Yes — field mapping to Librarian packets |
| **Assurance Contracts (5)** | `contracts/assurance/` | Implemented | Yes — cross-consumer vocabulary proven |
| **Qualification Compiler** | `qualification/compiler/qualification_compiler.py` | Implemented | Yes — IR → suite → evidence |
| **Qualification Baseline v1** | `docs/governance/QUALIFICATION-BASELINE-V1.md` | Defined | Yes — 34 checks, 5 domains |
| **Validation Profiles (2)** | `profiles/` | Implemented | Yes — Librarian + Agent Bridge |
| **Capability Manifest v2** | `qa-pilot-manifest-v2.json` | Implemented | Yes — granular maturity model |
| **MCP API Capability** | `capability-registry/` | Validated | Yes — connects to Librarian MCP endpoint |

### What's Missing

| Gap | What's Needed | Impact |
|-----|--------------|--------|
| **Librarian project adapter** | `adapters/project-adapter-librarian.json` | Referenced by profile but doesn't exist |
| **Retroactive Qualification Engine** | Engine that applies baseline to historical work | Can't qualify historical sprints yet |
| **Applicability determination logic** | Code that decides temporal/domain/scope applicability | Baseline exists but no runtime |
| **Qualification history storage** | Append-only store for qualification records | Can't track qualification over time |
| **LINK qualification surface** | LINK integration point for qualification results | Agent can't discover qualification mode |

---

## Integration Architecture

```
                    Agent Session
                         │
                         ▼
                   LINK (Interpretation Layer)
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    State Queries   Finding Queries   Qualification Queries
          │              │              │
          ▼              ▼              ▼
    Librarian MCP   Librarian MCP   QA-Pilot MCP
    (receipts,      (findings,      (qualification
     ledger,        evidence,       compiler,
     project        assessment)     baseline,
     index)                         evidence)
          │              │              │
          ▼              ▼              ▼
    ┌─────────────────────────────────────┐
    │         Custody Boundary            │
    │  Librarian owns: receipts, ledger,  │
    │  canonical state, decisions         │
    │  QA-Pilot owns: qualification,      │
    │  evidence, findings, proposals      │
    │  Owner owns: all authority          │
    └─────────────────────────────────────┘
```

### The Integration Flow

```
1. Agent starts with `start planning` or `start qa-pilot`
         │
2. LINK assembles context from Librarian + QA-Pilot
         │
3. Agent discovers qualification capabilities via MCP query
         │
4. Agent selects target (epic/sprint/project)
         │
5. Qualification Compiler generates IR from contract
         │
6. Compiler compiles IR to test suite
         │
7. Suite executes against target (read-only)
         │
8. Evidence pack produced (QE-* artifacts)
         │
9. Qualification record appended (QR-* artifacts)
         │
10. Findings routed through LINK to Owner
         │
11. Owner disposes (PASS / FINDING / NOT APPLICABLE)
         │
12. Learning objects generated from findings
         │
13. Training delivery (browser-app)
```

---

## Standard Operating Mode: Agent-Discoverable

### How an Agent Knows This Exists

The qualification mode is discoverable through three mechanisms:

**1. Startup Intent Routing**

```
start planning
```

Triggers `global_cross_project_planning_start` intent class. Agent gets read-only visibility across all projects, including QA-Pilot qualification capabilities.

**2. MCP Capability Query**

```
search_capabilities("qualification")
```

Returns QA-Pilot qualification compiler capabilities. Agent can discover:
- `qa_qualification_compile` — compile IR to test suite
- `qa_qualification_execute` — execute qualification suite
- `qa_qualification_baseline` — query baseline checks
- `qa_qualification_history` — query qualification records

**3. LINK Context Assembly**

LINK's context assembly service queries 5 source classes and generates auditable manifests. When qualification is relevant, LINK includes:
- Available baselines
- Previous qualification records
- Applicable checks for the target
- Compiler readiness status

### Sprint Planning with LINK

When planning a sprint, an agent can:

```
1. LINK: "What qualification capabilities are available?"
   → Returns: Qualification Compiler v1.0.0, Baseline v1, 34 checks

2. LINK: "What's the qualification status of the target epic?"
   → Returns: No prior qualification, or last qualification record

3. LINK: "What checks apply to this sprint type?"
   → Returns: Applicability matrix lookup

4. LINK: "Generate qualification plan for this sprint"
   → Returns: Qualification IR with selected domains and checks

5. Agent: "Qualify this sprint"
   → Compiler executes, produces evidence, records disposition
```

### The LINK Query Surface

From `LINK-MCP-QUERY-CONTRACT.md`, agents can query:

| Query | Returns |
|-------|---------|
| `governance_state` | Current governance posture across projects |
| `finding_state` | Active findings by project, severity, domain |
| `evidence_state` | Evidence artifacts by type, freshness, completeness |
| `diagnostic_state` | System health, drift, degradation |
| **New: `qualification_state`** | Qualification records, baseline status, compiler readiness |

---

## How It Ties Together

### The Assur loop

```
Retroactive Qualification
    │
    ├── Scans historical epics/sprints
    ├── Applies Qualification Baseline v1
    ├── Determines applicability (temporal, domain, scope)
    ├── Compiles domain-specific test suites
    ├── Executes (read-only against target)
    ├── Produces evidence (QE-* artifacts)
    ├── Records qualification (QR-* artifacts)
    │
    ▼
Findings (by domain, severity, applicability)
    │
    ├── Routed through LINK to Owner
    ├── Owner disposes (PASS / FINDING / NOT APPLICABLE)
    │
    ▼
Learning Objects (from qa_pilot_lesson_generator.py)
    │
    ├── Patterns: "governance sprints often lack evidence receipts"
    ├── Patterns: "frontend sprints miss accessibility checks"
    ├── Patterns: "training sprints lack provenance tracking"
    │
    ▼
Training Delivery (browser-app)
    │
    ├── Courses generated from qualification patterns
    ├── Quizzes test knowledge of common findings
    ├── Capstone scenarios mirror real qualification results
    │
    ▼
Future Work Improvement
    │
    ├── Sprint planning includes qualification checks
    ├── Agent knows baseline exists via LINK discovery
    ├── Forward qualification is part of normal workflow
    │
    ▼
Stronger Forward Qualification
    │
    └── Cycle repeats
```

### The Sprint Planning Integration

When an agent plans a new sprint:

```
1. LINK assembles context
   ├── Project identity
   ├── Active epic
   ├── Historical qualification results
   └── Applicable baseline checks

2. Agent receives qualification brief
   ├── "This sprint type requires: functional, testing, operational"
   ├── "Previous similar sprints had findings in: evidence completeness"
   └── "Recommended: generate qualification IR before implementation"

3. Agent creates sprint with qualification gate
   ├── Sprint includes: implementation + qualification
   ├── Qualification IR is part of sprint deliverables
   └── Sprint cannot seal without qualification disposition

4. During execution
   ├── Agent compiles IR to test suite
   ├── Suite executes alongside implementation
   ├── Evidence produced alongside code
   └── Both feed into sprint receipt

5. At seal time
   ├── Original seal records implementation
   ├── Qualification record records assurance
   ├── Both are immutable
   └── Neither depends on the other
```

---

## Implementation Sequence (Owner-Authorized)

| Order | Artifact | Why This Order |
|-------|----------|---------------|
| 1 | **Librarian Project Adapter** | Establishes canonical input. Proves read-only boundary. Prevents QA-Pilot from inventing project state. |
| 2 | **Qualification Run Record Contract** | Gives the runtime a durable output target. Defines the evidence boundary. |
| 3 | **Applicability Engine** | Prevents meaningless qualification runs. Defines qualification profiles. |
| 4 | **Retroactive Qualification Runtime** | Now has inputs (adapter) and outputs (run record). Orchestrates the loop. |
| 5 | **LINK Qualification Query Surface** | Makes the capability discoverable to agents. |

Each artifact is deliberately thin. None becomes a second implementation of the other system. The integration points are narrow by design.

---

## Key Architectural Conclusion

**The missing capability is orchestration, not invention.**

Both projects already contain the necessary primitives. The remaining work is creating the controlled boundary between them through explicit contracts.

The combined system becomes a Governed Development Loop:

```
Plan → Build → Qualify → Evidence → Findings → Learn → Improve → Plan Better
```

This loop is why the training platform, qualification compiler, and Librarian substrate belong together. They are not three products. They are three components of one loop:

- **Qualification Compiler** = Qualify + Evidence
- **Librarian Substrate** = Plan + Build + Evidence Custody
- **Training Platform** = Learn + Improve

The architecture has converged. The remaining work is connecting existing governed capabilities through explicit contracts.

---

## Key Invariants

1. **Original seals are never modified.** Qualification adds a new layer.
2. **Applicability is explicit.** Every check has a reason.
3. **Temporal fairness.** Old sprints don't fail new requirements.
4. **Advisory only.** QA-Pilot proposes, Owner decides.
5. **Cross-project boundaries preserved.** QA-Pilot reads Librarian; Librarian reads QA-Pilot receipts. Neither mutates the other.
6. **LINK is the bridge.** Agents discover qualification through LINK, not through direct filesystem access.
7. **Honest reporting.** Qualification results claim only what evidence supports (per TESTING-COMPLETION-HONESTY-STANDARD.md).
