# QA-Pilot Local AI Integration Architecture

WHO:    The Owner (Andrew) and all local/cloud AI agents
WHAT:   Infrastructure layout for running lower-cost agent arrays on an 8GB GPU Mac
WHEN:   Referenced when modifying the local runner setup, tools, or MCP layers
WHERE:   Project root -> LOCAL-AI-ARCHITECTURE.md
WHY:    Maintains zero-cost inference pipelines without exceeding 8GB VRAM limits

---

## 1. The Multi-Agent Tier Layout

WHO:    Orchestration layer / OpenWork
WHAT:   Splits incoming tasks between local hardware and cloud models
WHEN:   Evaluated on every incoming user prompt
WHERE:  OpenWork routing configuration
WHY:    Maximizes use of free local compute; protects cloud token budgets

────────────────────────┐│    OpenWork Router     │└───────────┬────────────┘│┌────────────────────────────────┴────────────────────────┐▼                                                 ▼┌─────────────────────────────────┐       ┌──────────────────────────────── BST/CLOUD TIER ───────────────────────────┐│   LOCAL TIER: Gemma 4 (3B-it)   │       │     CLOUD TIER: Claude 3.5       │├─────────────────────────────────┤       ├──────────────────────────────────┤│ VRAM Footprint: ~4.5GB          │       │ Cost: Per 1M tokens              ││ Tasks:                          │       │ Tasks:                          │
│ • Running fivews_session_start  │       │ • Complex logic refactoring      │
│ • Appending logs & features     │       │ • Designing new system arches    │
│ • Generating basic CSS/HTML     │       │ • Debugging deep memory leaks    │
│ • Running node build.js loops   │       │                                  │
└─────────────────────────────────┘       └──────────────────────────────────┘


---

## 2. Hardware Engine Boot Scripts

WHO:    System Administrator / The Owner
WHAT:   The deterministic shell commands required to initialize local hardware acceleration
WHEN:   Run once at the beginning of a development session
WHERE:  Host Terminal (Native macOS shell environment)
WHY:    Enforces Vulkan acceleration, avoiding slow Intel CPU fallback

### Step 1: Initialize Vulkan Environment
Ensure your terminal session explicitly points to your LunarG SDK paths:
```bash
export VULKAN_SDK="/Applications/VulkanSDK/1.4.xxx/macOS" # Adjust path to installed version
export PATH="\$VULKAN_SDK/bin:\$PATH"
```

### Step 2: Boot the Hardware Accelerated Engine
Launch the local server with 4-bit Quantized KV cache constraints to safeguard your 8GB VRAM pool:
```bash
./bin/llama-server \
  -m ./models/gemma-4-3b-it.Q4_K_M.gguf \
  -c 16384 \
  -ngl 99 \
  --flash-attn \
  --ctk q4_0 \
  --ctv q4_0 \
  --host 127.0.0.1 \
  --port 8080
```

---

## 3. OpenWork Connection Configuration

WHO:    OpenWork Framework
WHAT:   Mapping environment targets to loop back to the local `llama.cpp` port
WHEN:   Evaluated during workspace startup
WHERE:  Project root -> .env
WHY:    Tricks OpenAI-native frontends into parsing local open-source models natively

```env
# OpenWork Model Routing Parameters
OPENAI_API_BASE="http://127.0.0.1:8080/v1"
OPENAI_API_KEY="local-no-token-required"
DEFAULT_MODEL="gemma-4-3b-it"

# FlightPlan / Goose Scale Local Defaults
FLIGHTPLAN_LOCAL_FALLBACK=true
MAX_CONTEXT_TOKENS=16384
```

---

## 4. MCP Schema Enforcement Strategy

WHO:    Five Ws MCP Server Layer
WHAT:   Translates agent goals into raw structured mutations, skipping LLM string generation
WHEN:   Triggered by agent tools requests
WHERE:  Inside `.fivews/` data-store directory
WHY:    Saves local model tokens by avoiding the need to teach Gemma 4 Markdown syntax parsing

Because Gemma 4 only speaks to your custom MCP tools using JSON parameters, it bypasses the need to self-generate code structure:

```json
{
  "tool": "fivews_update_feature",
  "arguments": {
    "feature_name": "Simulated Teams App Chat Layout",
    "status": "🔍",
    "notes": "Compiled single file build verified via node build.js. Awaiting owner check."
  }
}
```
The MCP server intercepts this JSON object on your host Mac processor, updates your flat `FEATURE-STATUS.md` file natively using simple file system appending, and returns a lightweight "Success" code to the model.

---

## 5. Performance and Resource Guardrails

WHO:    The Local Developer / System Monitor
WHAT:   Metrics thresholds to keep the development workspace stable
WHEN:   Monitored continuously during build/compilation loops
WHERE:   macOS Activity Monitor -> GPU History Panel
WHY:    Preventing system lag or total GPU kernel crashes due to memory overflow

* **Target Model Allocation:** ~2.8 GB VRAM.
* **Target KV Cache Allocation (16K Context via q4_0):** ~1.4 GB VRAM.
* **Operating System Base Window Overhead:** ~1.5 GB VRAM.
* **Total Workspace Buffer (Safe zone):** **~5.7 GB used out of 8.0 GB available.**

If your GPU history spikes past 7.5 GB during deep agent loops, immediately drop the model context window parameter to `-c 12288` inside your terminal boot script to restore headroom.
Step-by-Step Implementation MapTo bring this fully into production across your local stack:Initialize the Document Workspace: Drop your PROJECT-PRIMER.md file along with the other structural documents into your root directory.Build your MCP Provider: Code your tool specs (fivews_init, fivews_session_start, etc.) as a simple Node.js or Python MCP script to host locally.Mount inside OpenWork: Point your application settings directly to the local loopback addresses specified in the document above.

---

## 6. Lightweight Node.js Five Ws MCP Implementation

WHO:    The Node.js Runtime Engine / OpenWork Framework
WHAT:   A standalone, zero-dependency Fast-MCP server providing core coordination tools
WHEN:   Booted as an MCP extension during OpenWork initialization
WHERE:  Project root -> `fivews-mcp.js`
WHY:    Mechanically locks files against formatting drift; processes data on native CPU to save GPU VRAM

This executable script implements the **Librarian pattern**. Save this as `fivews-mcp.js` in your project folder. It uses the official `@modelcontextprotocol/sdk` to expose `fivews_init` and `fivews_session_start` directly to your local Gemma 4 agent array.

### Dependencies Installation
Run this inside your project root directory to add the lightweight MCP core:
```bash
npm install @modelcontextprotocol/sdk
```

### Server Source Code (`fivews-mcp.js`)
```javascript
#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import fs from "fs";
import path from "path";
import crypto from "crypto";

// Initialize the MCP server container
const server = new McpServer({
  name: "fivews-custody-layer",
  version: "1.0.0"
});

/**
 * Utility: Generates SHA-256 hashes of un-slotted template areas
 * Ensures agents don't accidentally erase or mutate structural rules.
 */
function calculateSectionHash(content) {
  // Strip out project-specific mutable slots to leave only invariant template text
  const cleanTemplate = content.replace(/<!-- PROJECT-SLOT:[\s\S]*?<!-- \/PROJECT-SLOT:.*? -->/g, "");
  return crypto.createHash("sha256").update(cleanTemplate).digest("hex");
}

/**
 * TOOL 1: fivews_init
 * Scaffolds project files and writes immutable structure hashes to the filesystem.
 */
server.tool(
  "fivews_init",
  {
    project_name: z.string().describe("Name of the active project"),
    repo: z.string().describe("Git remote repository URL"),
    local_path: z.string().describe("Absolute system file path to project directory"),
    stack: z.string().describe("Tech stack properties and constraints"),
    build_command: z.string().describe("The exact shell command executed to compile files"),
    owner: z.string().describe("The human designer supervising the repository"),
    address_term: z.string().describe("The designated name or callsign for the AI agent"),
    agent_roster: z.array(z.string()).describe("List of allowed developer agent profiles"),
    constraints: z.array(z.string()).optional().describe("Extra single-file/file:// rules")
  },
  async ({ project_name, repo, local_path, stack, build_command, owner, address_term, agent_roster, constraints }) => {
    const configDir = path.join(process.cwd(), ".fivews");
    if (!fs.existsSync(configDir)) fs.mkdirSync(configDir);

    const configPayload = { project_name, repo, local_path, stack, build_command, owner, address_term, agent_roster };
    fs.writeFileSync(path.join(configDir, "config.json"), JSON.stringify(configPayload, null, 2));

    // Simple raw template generator for PROJECT-PRIMER.md
    const primerContent = \`# \${project_name} — Session Primer

WHO:    Every LLM agent starting a session on this project
WHAT:   Identity, session start protocol, behaviour rules, session end protocol
WHEN:   Auto-loaded at every session start. Read before any other file.
WHERE:  Project root. Filename must be PROJECT-PRIMER.md.
WHY:    Without this, every session starts cold. Agents re-learn the project.

<!-- PROJECT-SLOT:HEADER -->
**Project name:** \${project_name}
**Repo:** \${repo}
**Local path:** \${local_path}
**Stack:** \${stack}
**Build command:** \${build_command}
**Owner:** \${owner}
**Owner address term:** \${address_term}
**Agent roster:** \${agent_roster.join(", ")}
<!-- /PROJECT-SLOT:HEADER -->

## Session Start — Do These In Order, Every Time
WHO:    The agent starting a session
WHAT:   Three steps that must complete before any task work begins
...
<!-- PROJECT-SLOT:PROJECT-CODE-RULES -->
\${(constraints || []).map(c => \`- \${c}\`).join("\\n")}
<!-- /PROJECT-SLOT:PROJECT-CODE-RULES -->
\`;

    const primerPath = path.join(process.cwd(), "PROJECT-PRIMER.md");
    let skipped = false;

    if (!fs.existsSync(primerPath)) {
      fs.writeFileSync(primerPath, primerContent);
    } else {
      skipped = true;
    }

    // Store structural snapshot integrity proof
    const hashes = {
      "PROJECT-PRIMER.md": calculateSectionHash(fs.readFileSync(primerPath, "utf-8"))
    };
    fs.writeFileSync(path.join(configDir, "hashes.json"), JSON.stringify(hashes, null, 2));

    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          status: "success",
          files_created: skipped ? [] : ["PROJECT-PRIMER.md"],
          hashes_stored: Object.keys(hashes).length,
          warning: skipped ? "PROJECT-PRIMER.md already existed. Skipping rewrite." : undefined
        }, null, 2)
      }]
    };
  }
);

/**
 * TOOL 2: fivews_session_start
 * Automatically processes structural layout logs on native CPU, protecting GPU VRAM.
 */
server.tool(
  "fivews_session_start",
  {},
  async () => {
    const primerPath = path.join(process.cwd(), "PROJECT-PRIMER.md");
    const hashFilePath = path.join(process.cwd(), ".fivews", "hashes.json");
    
    let validationStatus = "pass";
    let summaryMessage = "All structural universal constraints match the canonical initialization.";

    if (!fs.existsSync(primerPath)) {
      return {
        content: [{ type: "text", text: JSON.stringify({ validation_status: "fail", validation_summary: "Critical missing file: PROJECT-PRIMER.md" }) }]
      };
    }

    if (fs.existsSync(hashFilePath)) {
      const storedHashes = JSON.parse(fs.readFileSync(hashFilePath, "utf-8"));
      const currentPrimerHash = calculateSectionHash(fs.readFileSync(primerPath, "utf-8"));

      if (storedHashes["PROJECT-PRIMER.md"] !== currentPrimerHash) {
        validationStatus = "warn";
        summaryMessage = "Warning: Universal configuration structural shift detected outside allowed slot zones.";
      }
    }

    // Mock response objects mimicking functional downstream target files for early pipeline runs
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          handoff: {
            last_session_date: new Date().toISOString().split('T')[0],
            last_session_agent: "System Setup",
            completed: ["Pipeline structural wiring complete"],
            in_progress: [{ item: "Local runner verification", file: "build.js", detail: "Waiting for model check" }],
            priorities: ["Execute build verification loop", "Test file:// loading"],
            recent_gotchas: ["Browsers enforce file:// path isolation filters unless bundled via node build.js"]
          },
          feature_status: {
            total_features: 1,
            by_status: { verified: 0, partial: 0, broken: 0, stub: 1, needs_review: 0 },
            broken_features: [],
            release_blockers: []
          },
          architecture_loaded: true,
          validation_status: validationStatus,
          validation_summary: summaryMessage
        }, null, 2)
      }]
    };
  }
);

// Instantiate standard I/O connection parameters for OpenWork coupling
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  process.stderr.write(\`MCP Execution Failure: \${error.message}\\n\`);
  process.exit(1);
});
```

---

## 7. Activating the Local Environment

To hook this up to your agent array inside OpenWork, append this declaration to your local OpenWork or Claude Code tools configuration manifest:

```json
{
  "mcpServers": {
    "fivews-custody": {
      "command": "node",
      "args": ["/Users/andrew/Desktop/Open Work/QA Pilot/fivews-mcp.js"]
    }
  }
}
```

---

## 8. The `FEATURE-STATUS.md` Matrix Template

WHO:    Every AI agent running verification loops, supervised by the Owner (Andrew)
WHAT:   The absolute ground truth matrix tracking functional vs broken simulation states
WHEN:   Read during session start; modified immediately when code behaviors change
WHERE:  Project root -> `FEATURE-STATUS.md`
WHY:    Prevents multi-agent confusion regarding what works versus what is currently broken

```markdown
# QA-Pilot — Feature Status Matrix

WHO:    All developer agents and the project supervisor
WHAT:   Ground-truth verification states for simulated OS apps and core features
WHEN:   Read during session initialization. Updated after every build loop.
WHERE:  Project root -> FEATURE-STATUS.md
WHY:    Without a centralized matrix, agents break existing apps while fixing others.

<!-- PROJECT-SLOT:METRICS -->

| Total Features | Verified (✅) | Partial (⚠️) | Broken (❌) | Stubs (🔲) | Under Review (🔍) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 7 | 0 | 0 | 0 | 7 | 0 |
<!-- /PROJECT-SLOT:METRICS -->

---

## Core Infrastructure

WHO:    Engine agents
WHAT:   Underlying file parsing, compilation, and cross-language translation layers
WHEN:   Checked before any application-level modifications are attempted
WHERE:  Project compilation tree
WHY:    App components fail if the translation tables or bundle mechanics drift

<!-- PROJECT-SLOT:INFRASTRUCTURE_TABLE -->

| Feature Name | Status | Last Change | Verified Date | Notes / Blockers |
| :--- | :---: | :--- | :--- | :--- |
| `build.js` Compiler Pipeline | 🔲 | Initial setup | 2026-05-21 | Needs to parse raw components into single file |
| `i18n.js` Translation Mapping | 🔲 | Matrix created | 2026-05-21 | Must bind correctly to lang-en.js and lang-fr.js |
| `IndexedDB` Local Storage | 🔲 | Spec complete | 2026-05-21 | Must bypass file:// storage sandbox safely |
<!-- /PROJECT-SLOT:INFRASTRUCTURE_TABLE -->

---

## Desktop Applications (Simulated Windows 11 Workspace)

WHO:    Frontend agents
WHAT:   The individual application layers rendering inside the desktop simulator view
WHEN:    Updated immediately following a browser runtime manual validation test
WHERE:  Source directory components -> built file
WHY:    Tracks individual isolated application features inside the single-file envelope

<!-- PROJECT-SLOT:APPLICATIONS_TABLE -->

| Feature Name | Status | Last Change | Verified Date | Notes / Blockers |
| :--- | :---: | :--- | :--- | :--- |
| `QASimulator.html` Desktop Shell | 🔲 | UI Skeleton | 2026-05-21 | Base workspace environment |
| Dynamics 365 Simulator (`dynamics.html` component) | 🔲 | Planned stub | 2026-05-21 | Needs mock business record grid views |
| Azure DevOps Simulator (`ado.html` component) | 🔲 | Planned stub | 2026-05-21 | Needs functional agile board simulator |
| Microsoft Teams Simulator (`teams.html` component) | 🔲 | Planned stub | 2026-05-21 | Needs bilingual mock user chat streams |
<!-- /PROJECT-SLOT:APPLICATIONS_TABLE -->

---

## Release Blockers

WHO:    The Owner (Andrew)
WHAT:   Non-negotiable criteria before the simulation package can be finalized
WHEN:   Evaluated prior to final session closure
WHERE:  Project build environment
WHY:    Ensures no breaking developer drift escapes to deployment

<!-- PROJECT-SLOT:RELEASE_BLOCKERS -->
- [ ] Ensure all code passes `node build.js` compilation without throw flags.
- [ ] Guarantee absolute functionality inside a plain browser instance loaded via `file://`.
- [ ] English and French strings must map smoothly with zero unresolved translation hooks.
<!-- /PROJECT-SLOT:RELEASE_BLOCKERS -->
```

---

## 9. The Monolithic Compiler Framework (`build.js`)

WHO:    The Node.js Engine / Automation Agent Tools
WHAT:   A zero-dependency file-bundler script that combines split source modules into a single `file://` safe file
WHEN:   Executed automatically following any workspace code modification
WHERE:  Project root -> `build.js`
WHY:    Bypasses modern browser cross-origin asset resource restrictions smoothly

Save this file as `build.js` in your root directory. It looks for a `src/` directory containing separate sub-files and generates a single production file (`QASimulator.html`) instantly using low-overhead CPU operations.

```javascript
#!/usr/bin/env node

/**
 * WHO:    Node.js Build Tooling
 * WHAT:   Compiles isolated HTML, CSS, and JS files into one monolithic file
 * WHEN:   Triggered by local agents immediately post-edit
 * WHERE:  Project root -> build.js (Outputs to project root -> QASimulator.html)
 * WHY:    Removes file:// CORS limits so the project runs with double-click ease
 */

import fs from "fs";
import path from "path";

const SRC_DIR = path.join(process.cwd(), "src");
const OUTPUT_FILE = path.join(process.cwd(), "QASimulator.html");

function compile() {
  console.log("🏗️  Initializing QA-Pilot Single-File Build Pipeline...");

  // Enforce source tree directories existence
  if (!fs.existsSync(SRC_DIR)) {
    console.error("❌ Error: Missing 'src/' source folder layout structure.");
    process.exit(1);
  }

  // Define critical source path configurations
  const paths = {
    shell: path.join(SRC_DIR, "shell.html"),
    styles: path.join(SRC_DIR, "styles.css"),
    i18n: path.join(SRC_DIR, "i18n.js"),
    langEn: path.join(SRC_DIR, "lang-en.js"),
    langFr: path.join(SRC_DIR, "lang-fr.js"),
    dynamics: path.join(SRC_DIR, "dynamics.html"),
    ado: path.join(SRC_DIR, "ado.html"),
    teams: path.join(SRC_DIR, "teams.html")
  };

  // Ensure primary shell layout is intact
  if (!fs.existsSync(paths.shell)) {
    console.error("❌ Error: Base shell element 'src/shell.html' missing.");
    process.exit(1);
  }

  try {
    // Read raw code contents into RAM buffers
    let htmlShell = fs.readFileSync(paths.shell, "utf-8");
    const cssContent = fs.existsSync(paths.styles) ? fs.readFileSync(paths.styles, "utf-8") : "/* Missing styles.css */";
    const i18nCore = fs.existsSync(paths.i18n) ? fs.readFileSync(paths.i18n, "utf-8") : "";
    const langEnContent = fs.existsSync(paths.langEn) ? fs.readFileSync(paths.langEn, "utf-8") : "const langEn = {};";
    const langFrContent = fs.existsSync(paths.langFr) ? fs.readFileSync(paths.langFr, "utf-8") : "const langFr = {};";
    
    // Read individual application template modules
    const apps = {
      dynamics: fs.existsSync(paths.dynamics) ? fs.readFileSync(paths.dynamics, "utf-8") : "<div>Dynamics Missing</div>",
      ado: fs.existsSync(paths.ado) ? fs.readFileSync(paths.ado, "utf-8") : "<div>Azure DevOps Missing</div>",
      teams: fs.existsSync(paths.teams) ? fs.readFileSync(paths.teams, "utf-8") : "<div>Teams Missing</div>"
    };

    // Inject styles inline into the compiled template block
    const injectedCSS = \`<style>\\n\${cssContent}\\n</style>\`;
    htmlShell = htmlShell.replace("</head>", \`\${injectedCSS}\\n</head>\`);

    // Bundle core scripts and component frameworks together inside a structured payload array
    const compiledScripts = \`
<script>
// --- Multi-Language Data Architecture Layer ---
\${langEnContent}
\${langFrContent}
\${i18nCore}

// --- Windows 11 App Template Registry Infrastructure ---
const AppVirtualFileTemplates = {
  dynamics: \`\${apps.dynamics.replace(/\\`/g, "\\\\`").replace(/\\${/g, "\\\\${")}\`,
  ado: \`\${apps.ado.replace(/\\`/g, "\\\\`").replace(/\\${/g, "\\\\${")}\`,
  teams: \`\${apps.teams.replace(/\\`/g, "\\\\`").replace(/\\${/g, "\\\\${")}\`
};

console.log("🖥️  QA-Pilot Virtual App Register Loaded Successfully.");
</script>
\`;

    // Inject script bundle directly before the trailing body closing boundary tag
    htmlShell = htmlShell.replace("</body>", \`\${compiledScripts}\\n</body>\`);

    // Write out the absolute compiled target artifact
    fs.writeFileSync(OUTPUT_FILE, htmlShell, "utf-8");
    console.log("✅ Build complete! Monolithic file written -> QASimulator.html");
    
  } catch (err) {
    console.error(\`❌ Critical compilation runtime exception: \${err.message}\`);
    process.exit(1);
  }
}

compile();
\`