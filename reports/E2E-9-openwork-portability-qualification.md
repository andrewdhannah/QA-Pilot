# E2E-9: Openwork Portability Qualification

**Date:** 2026-08-11
**Status:** IN PROGRESS
**Target:** Openwork (https://github.com/andrewdhannah/openwork)
**Target Location:** `/Users/andrew/Desktop/CarbideFrame/active/librarian-workbench/upstream/openwork/`

---

## Target Identity

| Field | Value |
|---|---|
| Target ID | openwork |
| Target Name | OpenWork |
| Target Type | Desktop app (TypeScript/React/Tauri) |
| Provenance | Forked from different-ai/openwork (external origin) |
| Purpose | Open-source AI workflow sharing desktop app |
| Tech Stack | TypeScript, React, Tauri, Rust, pnpm |
| Repository | https://github.com/andrewdhannah/openwork |
| Local Path | `/Users/andrew/Desktop/CarbideFrame/active/librarian-workbench/upstream/openwork/` |

---

## Portability Test Question

**Can QA-Pilot independently interrogate a system it did not originate from, using the same contracts, capability registry, evidence model, and governance boundaries?**

---

## Project Structure

```
openwork/
├── apps/           # Desktop app, orchestrator, server
├── packages/       # Shared packages
├── docs/           # Documentation
├── scripts/        # Build/dev scripts
├── evals/          # Evaluation tests
├── changelog/      # Release notes
├── ee/             # Enterprise edition
├── patches/        # Patches
├── packaging/      # Build packaging
├── .github/        # CI/CD
├── package.json    # Root package
├── pnpm-workspace.yaml
├── turbo.json
└── README.md
```

---

## QA-Pilot Capabilities Applicable

| Capability | Status | Applicable? |
|---|---|---|
| SCRIPT_EXECUTION | AVAILABLE | ✓ (package.json, scripts/) |
| SCHEMA_VALIDATION | AVAILABLE | ✓ (TypeScript types, Zod schemas) |
| MCP_API_INTERACTION | VALIDATED | ✓ (if Openwork has MCP endpoints) |
| BROWSER_INTERACTION | VALIDATED | ✓ (desktop app is browser-based) |

---

## Target Adapter

| Adapter | Target Type | Status |
|---|---|---|
| cli | CLI/scripts | AVAILABLE |
| browser-playwright | Browser/UI | AVAILABLE |
| mcp-jsonrpc | MCP endpoints | PENDING (need to discover) |

---

## Initial Discovery Requirements

1. **Project structure** — What are the main components?
2. **Test infrastructure** — What tests exist? How are they run?
3. **Build system** — How is the project built?
4. **Interfaces** — What APIs/endpoints does it expose?
5. **Existing claims** — What does the README/docs say it does?

---

## Acceptance Gates

| Gate | Requirement | Status |
|---|---|---|
| E9-1 | Target discovered and mapped | PENDING |
| E9-2 | QA-Pilot capabilities resolve | PENDING |
| E9-3 | Target adapter resolves | PENDING |
| E9-4 | No Librarian-specific logic imported | PENDING |
| E9-5 | Independent assurance extraction | PENDING |
| E9-6 | Tests constructed from requirements | PENDING |
| E9-7 | Tests executed against target | PENDING |
| E9-8 | Evidence produced | PENDING |
| E9-9 | Reproducibility verified | PENDING |

---

*Portability qualification — advisory-only.*
