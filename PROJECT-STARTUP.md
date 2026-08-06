# PROJECT-STARTUP.md — QA Pilot

**This file provides project-specific startup context for agents working on QA Pilot.**
**QA Pilot is a harness_governed add-on project — see PROJECT-IDENTITY.md for full identity, boundaries, and authority.**

---

## Delegation

QA Pilot's project identity and governance are defined in:

- **Identity:** `PROJECT-IDENTITY.md` (project_id, thesis, owner, boundaries)
- **Profile:** `PROJECT-PROFILE.json` (repo_path, workspace_path, sandbox_boundary, allowed_mutation_paths, forbidden_cross_project_paths)
- **Status:** `FEATURE-STATUS.md`, `SESSION-HANDOFF.md`, `project-state/sprint-ledger.json`
- **Governance:** `docs/governance/QA-PILOT-PROJECT-GOVERNANCE.md`

## Project Identity

| Field | Value |
|-------|-------|
| `project_id` | `qa-pilot` |
| `project_name` | QA Pilot |
| `profile_id` | `lightweight-custody` |
| `owner` | Andrew Hannah |
| `thesis` | A governed quality assurance framework for AI-assisted product work, providing structured QA lanes, evidence collection, manual verification scripts, and readiness assessments. |

## MCP Context Acquisition

QA Pilot uses the generic startup protocol defined in `SessionStartup/AGENT-START.md` §13 (project selector) and `docs/rules/PROJECT-HARNESS-STARTUP-PROTOCOL.md`.

Per the workspace startup protocol (`SessionStartup/STARTUP-PROTOCOL.md` §3.2), acquire governed project context by calling **in parallel**:

```text
1. MCP: project_get_profile(profile_id: "qa-pilot-full-governance")
2. MCP: project_get_cursor(project_id: "qa-pilot")
3. MCP: project_get_allowed_transitions(project_id: "qa-pilot")
```

Then call sequentially:

```text
4. MCP: project_assemble_context(
      project_id: "qa-pilot",
      project_name: "QA Pilot",
      owner: "Andrew Hannah",
      canonical_repo: "{{active_project_root}}",
      profile_id: "qa-pilot-full-governance",
      thesis: "A governed quality assurance framework for AI-assisted product work...",
      current_state: "<from PROJECT-PROFILE.json active_sprint>"
    )
```

After context is acquired, output the startup report using the mode contract (`SessionStartup/STARTUP-OUTPUT-CONTRACT.md`):
- `start` → strict: report only, no uncontrolled prose
- `start verbose` → step narration + report + ≤4-line governance summary
- `start debug` → diagnostics + report
- `start repair` → diagnostics + report + blocker/repair guidance

### start &lt;project-id&gt; Command (Project Selector)

The `start <project-id>` command (e.g. `start qa-pilot`) is handled by the **generic project selector protocol** defined in `SessionStartup/PROJECT-SELECTOR-PROTOCOL.md`.

### start &lt;WORK-ID&gt; Command

When the user says `start <WORK-ID>` (e.g. `start QA-PILOT-STARTUP-PARITY-GAP-CLOSURE-1`), the agent runs the **standard startup protocol** defined in `SessionStartup/STARTUP-PROTOCOL.md`, then binds `<WORK-ID>` as the **active work identity** for the session.

This command has **three distinct phases**. They execute in order and are not collapsed:

#### Phase 1 — Identity Binding (always executes)

1. **Work identity takes highest priority.** The `<WORK-ID>` is used as the session identity for session title derivation and for the startup report's `Current task` and `Next action` fields.
2. **Session title derivation.** After the startup report, the silent `session.rename` (Step 10) uses the `<WORK-ID>` as the derived title. If the work ID resolves to a known sprint, the sprint ID is used as-is. If unknown or invalid, the session title falls back to standard derivation rules.
3. **Existing checks preserved.** All existing startup checks (root verification, MCP health, operating mode detection, governance context acquisition) are unchanged. `start <WORK-ID>` does not skip or shortcut any step.

#### Phase 2 — Work Packet Discovery (always executes)

After identity binding, the agent searches for a **canonical sprint brief or work packet** for the supplied `<WORK-ID>`:

1. **Search locations** (in order):
   - `docs/sprints/<WORK-ID>.md` — sprint receipt (indicates completed work)
   - `SESSION-HANDOFF.md` — handoff entry for the work ID
   - `project-state/sprint-ledger.json` — ledger entry for the work ID
   - `docs/governance/` — governance docs referencing the work ID

2. **Canonical sprint brief found.** If a sprint receipt or handoff entry exists with full acceptance gates, scope, and task definition, the agent loads it as the work packet. This is the **execution-eligible** state.

3. **No canonical sprint brief.** If no sprint receipt, handoff entry, or planning doc exists for the work ID, the agent enters **pre-execution hold**:
   - Report `"No canonical sprint brief found for <WORK-ID>"` in the startup report's `Blockers` field
   - Set `Current task` to `"<WORK-ID> — awaiting sprint brief"`
   - Set `Next action` to `"Draft or request sprint brief for <WORK-ID> — do not implement until brief is approved"`
   - **Do not begin implementation.** Do not infer acceptance gates, file scope, or commit behavior.

#### Phase 3 — Execution Authorization (conditional)

Execution authorization depends on Phase 2 outcome:

| Phase 2 Result | Phase 3 Action |
|----------------|----------------|
| Canonical sprint brief found (execution-eligible) | Load the brief. If the user's message also contains the full sprint specification, proceed under that brief. If not, report the brief and await Owner direction. |
| No canonical sprint brief (pre-execution hold) | **Stop.** Do not implement. Generate or request the sprint brief. Await Owner approval before proceeding. |
| Work ID is unknown | **Stop.** Report as blocker. Await Owner clarification. |
| Work ID is sealed | **Stop.** Report sealed status. Await Owner direction. |
| Work ID is superseded | **Stop.** Report supersession. Await Owner direction. |
| Work ID is stale | **Stop.** Report staleness. Await Owner correction. |

**Hard rules for Phase 3:**
- **No implementation from ID-only startup.** The `<WORK-ID>` alone does not authorize code changes, file edits, commits, or seals.
- **No inferred acceptance gates.** The agent must read the actual acceptance gates from the sprint brief, not infer them from the work ID.
- **No inferred file scope.** The agent must read the actual file scope from the sprint brief, not guess which files to modify.
- **No inferred commit/seal behavior.** The agent must follow the sprint brief's closeout instructions, not assume default commit messages or seal procedures.
- **No bypass of Owner work packet approval.** If no sprint brief exists, the Owner must approve one before implementation begins.

### Step 10 — Derive Session Identity and Rename OpenWork Sidebar Title

After the startup report is emitted (per `STARTUP-PROTOCOL.md` §4), silently rename the current OpenWork session to reflect the derived work identity:

1. **Derive identity** per SESSION-IDENTITY-DERIVATION.md priority rules:
   - Active sprint/work ID → use sprint ID
   - Project selected, no active work → `QA Pilot (idle)`
   - No project selected → `startup — no project`
   - Degraded mode → `QA Pilot (degraded)`

2. **Read session ID** from `openwork_ui_snapshot` route path.

3. **Rename** by calling:
   ```
   openwork_ui_execute_action({
     actionId: "session.rename",
     args: { sessionId: "<id>", title: "<derived-title>" }
   })
   ```

4. **Zero output text.** This step produces no visible prose — it does not violate strict mode's zero-postamble rule because tool calls are not output text.

5. **Non-blocking.** If the rename action is unavailable or fails, silently continue. The session retains its default title. Do not degrade startup mode for a cosmetic rename failure.

## QA Pilot-Specific Rules

### Paths
- **Read/write:** `{{active_project_root}}/`
- **Read-only (historical):** `{{historical_root}}/`
- **Do not edit:** `{{historical_root}}/` unless explicitly authorized

### Allowed Mutation Paths
- `docs/`, `scripts/`, `fixtures/`, `project-state/`, `receipts/`
- `PROJECT-IDENTITY.md`, `PROJECT-PROFILE.json`, `FEATURE-STATUS.md`, `SESSION-HANDOFF.md`

### Forbidden Cross-Project Paths
- See `PROJECT-PROFILE.json` `forbidden_cross_project_paths` for the full list

### Agent Authority
- Authority level: `advisory-only`
- No agent may self-verify work or mark it `✅ Verified`
- All agent work is `🔍 Pending` until Owner reviews
- QA Pilot is a separate add-on project — must not mutate The Librarian repo
- See `PROJECT-IDENTITY.md` for the complete boundary rules
