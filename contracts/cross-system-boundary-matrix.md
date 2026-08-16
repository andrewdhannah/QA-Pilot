# Cross-System Contract Boundary Matrix

**Sprint:** Cross-System Contract Hardening (#236)
**Status:** ACTIVE — Owner-authorized 2026-08-16
**Boundary:** System interface definitions only

---

## 1. Purpose

Define exactly what each subsystem may provide, consume, and never assume. Prevents accidental role expansion.

## 2. Boundary Matrix

| System | Produces | Consumes | Cannot Do |
|--------|----------|----------|-----------|
| **Librarian Core** | governance state, receipts, findings | evidence, declarations | execute agent actions |
| **FlightPlan** | runtime observations | runtime context | classify authority |
| **QA-Pilot** | assurance evidence, validation results | project state | approve capability changes |
| **LINK** | advisory projections | assessments, signals | create decisions |
| **Agents** | proposed actions, artifacts | contracts, capabilities | modify governance state |

## 3. System Definitions

### 3.1 Librarian Core

| Aspect | Definition |
|--------|------------|
| **Role** | Governance substrate and state management |
| **Produces** | Governance state, receipts, findings, work packets |
| **Consumes** | Evidence, declarations, capability registrations |
| **Authority** | State management, receipt generation |
| **Cannot** | Execute agent actions, make planning decisions |
| **Boundary** | Librarian manages state; it does not act on behalf of agents |

### 3.2 FlightPlan

| Aspect | Definition |
|--------|------------|
| **Role** | Runtime observation and resource tracking |
| **Produces** | Runtime observations, resource consumption data |
| **Consumes** | Runtime context, session information |
| **Authority** | Observation and measurement |
| **Cannot** | Classify authority, make governance decisions |
| **Boundary** | FlightPlan observes; it does not interpret governance |

### 3.3 QA-Pilot

| Aspect | Definition |
|--------|------------|
| **Role** | Assurance evaluation and qualification |
| **Produces** | Assurance evidence, validation results, risk assessments |
| **Consumes** | Project state, evidence, capability declarations |
| **Authority** | Evaluation and recommendation |
| **Cannot** | Approve capability changes, create work, close findings |
| **Boundary** | QA-Pilot evaluates; Owner decides |

### 3.4 LINK

| Aspect | Definition |
|--------|------------|
| **Role** | Planning context and advisory projection |
| **Produces** | Advisory projections, planning context |
| **Consumes** | Assessments, signals, assurance state |
| **Authority** | Context provision |
| **Cannot** | Create decisions, authorize actions |
| **Boundary** | LINK informs; Owner decides |

### 3.5 Agents

| Aspect | Definition |
|--------|------------|
| **Role** | Task execution and artifact creation |
| **Produces** | Proposed actions, artifacts, evidence |
| **Consumes** | Contracts, capabilities, planning context |
| **Authority** | Task execution within bounds |
| **Cannot** | Modify governance state, approve changes |
| **Boundary** | Agents execute; they do not govern |

## 4. Information Flow

```
Librarian Core ←→ QA-Pilot
        ↑              ↑
        |              |
   Governance    Assurance
   State         Evidence
        |              |
        ↓              ↓
   FlightPlan ←→ Agents
        ↑              ↑
        |              |
   Runtime      Actions
   Observations
        |              |
        ↓              ↓
      LINK ←→ Owner
```

## 5. Human Decision Points

| Decision | System Detects | Owner Decides |
|----------|---------------|---------------|
| Risk acceptance | QA-Pilot identifies risk | Owner accepts or defers |
| Capability approval | QA-Pilot qualifies | Owner approves or rejects |
| Work authorization | LINK provides context | Owner authorizes or rejects |
| Finding closure | QA-Pilot detects finding | Owner verifies resolution |
