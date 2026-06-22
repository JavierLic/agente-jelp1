# agent-sdk-builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `agent-sdk-builder` skill — a personal skill that teaches, scaffolds, and serves as reference for building Claude Agent SDK agents in Python or TypeScript, authenticated via the user's Claude Max subscription.

**Architecture:** Progressive-disclosure skill. A short `SKILL.md` router points to `reference/` docs (loaded on demand) and `templates/` (copied on scaffold). Reference docs are sourced from official Anthropic docs at build time; the runnable starter templates reuse the exact APIs captured in those reference docs, so no SDK API is hardcoded from memory.

**Tech Stack:** Markdown (skill + reference), Python 3.10+ (`claude-agent-sdk`), TypeScript/Node (`@anthropic-ai/claude-agent-sdk`). Auth: `CLAUDE_CODE_OAUTH_TOKEN` via `claude setup-token`.

## Global Constraints

- Skill root: `~/.agents/skills/agent-sdk-builder/` (already exists; contains `DESIGN.md`, `PLAN.md`).
- Auth is **subscription-only**: `CLAUDE_CODE_OAUTH_TOKEN`. API key is mentioned only as a one-line note; never as a primary path.
- Default permission posture in generated agents: read-only tools (`Read`, `Glob`, `Grep`, `WebSearch`) pre-approved; sensitive tools (`Bash`, `Edit`, `Write`) require explicit approval.
- Python floor: **3.10+**.
- All SDK API signatures (options fields, the permission-approval callback, message iteration) MUST be copied from official docs (`code.claude.com/docs/en/agent-sdk/...`) during Tasks 3–4, not written from memory. Tasks 5–6 reuse those exact signatures.
- Comments in generated starter code are in Spanish (didactic).
- No git repo here — commits are skipped; "Commit" steps are replaced by a file-existence/verification check.

---

### Task 1: Skill router (`SKILL.md`)

**Files:**
- Create: `~/.agents/skills/agent-sdk-builder/SKILL.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the skill entrypoint. References (by relative path) `reference/concepts.md`, `reference/python.md`, `reference/typescript.md`, `templates/python-starter/`, `templates/typescript-starter/` — those paths must match the files created in Tasks 2–6.

- [ ] **Step 1: Write `SKILL.md` with frontmatter + router body**

```markdown
---
name: agent-sdk-builder
description: Enseña, hace scaffold y da referencia para construir agentes con el Claude Agent SDK en Python o TypeScript, autenticados con suscripción Claude Max. Usar cuando el usuario diga "construye un agente SDK", "créame un agente con Claude", "enséñame el Agent SDK", o quiera generar/entender un agente del Agent SDK. NO usar para navegación web (eso es gstack /browse).
---

# Agent SDK Builder

Construye agentes con el **Claude Agent SDK** (Python o TypeScript), autenticados
con la **suscripción Claude Max** del usuario (no facturación por API).

## Flujo

1. Detecta la intención del usuario:
   - **Aprender** → carga `reference/concepts.md` y explica los bloques relevantes.
   - **Construir (scaffold)** → pregunta lenguaje, copia el template, explica cada archivo.
   - **Consultar referencia** → carga `reference/python.md` o `reference/typescript.md`.
2. Si va a construir o aprender y no es claro el lenguaje, pregunta: **¿Python o TypeScript?**
3. Carga SOLO el archivo que toca (no todos a la vez):
   - Conceptos: `reference/concepts.md`
   - Python: `reference/python.md`  ·  TypeScript: `reference/typescript.md`
   - Scaffold: `templates/python-starter/` o `templates/typescript-starter/`
4. **Scaffold:** copia el starter al directorio que indique el usuario, ajusta el nombre,
   explica cada archivo y recuérdale generar el token con `claude setup-token` y exportar
   `CLAUDE_CODE_OAUTH_TOKEN`.
5. Cierra siempre recordando la postura de permisos por defecto (lectura pre-aprobada +
   aprobación para Bash/Edit/Write) y cómo ampliarla con cuidado.

## Autenticación (importante)

Estos agentes usan la **suscripción Claude Max**, no API de pago por token:
- Generar token: `claude setup-token` (requiere Claude Code CLI + plan Pro/Max/Team/Enterprise).
- Exportar: `export CLAUDE_CODE_OAUTH_TOKEN=<token>`.
- Correr **sin** `ANTHROPIC_API_KEY` (esa variable tiene prioridad y facturaría por API).

(Existe también auth por API key para producción/terceros; fuera del alcance de esta skill.)

## Permisos por defecto

Los agentes generados pre-aprueban tools de solo lectura (`Read`, `Glob`, `Grep`,
`WebSearch`) y piden aprobación para acciones sensibles (`Bash`, `Edit`, `Write`).
```

- [ ] **Step 2: Verify the file exists and frontmatter is valid**

Run: `head -5 ~/.agents/skills/agent-sdk-builder/SKILL.md`
Expected: shows `---`, `name: agent-sdk-builder`, a `description:` line, `---`.

---

### Task 2: Concepts reference (`reference/concepts.md`)

**Files:**
- Create: `~/.agents/skills/agent-sdk-builder/reference/concepts.md`

**Interfaces:**
- Consumes: nothing (conceptual prose).
- Produces: the "learn" content the router loads. No code APIs are load-bearing here — examples are illustrative and must be marked as such.

- [ ] **Step 1: Fetch the official overview to ground the concepts**

Run (via WebFetch): `https://code.claude.com/docs/en/agent-sdk/overview`
Extract: the 6 capability tabs (Built-in tools, Hooks, Subagents, MCP, Permissions, Sessions) and the "Agent SDK vs Client SDK" comparison.

- [ ] **Step 2: Write `reference/concepts.md`**

Structure (each block 3–5 lines + one short illustrative snippet, in Spanish):
- **Tools** — Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch; cómo se eligen con `allowed_tools` / `allowedTools`.
- **Permissions** — pre-aprobar / pedir aprobación / bloquear; aquí vive el default del usuario.
- **Sessions** — memoria entre turnos; capturar `session_id` y reanudar con `resume`.
- **Subagents** — delegar subtareas con `AgentDefinition` + tool `Agent`.
- **MCP** — conectar sistemas externos como tools; enlazar a la skill `mcp-server-dev` ya instalada.
- **Hooks** — código propio en `PreToolUse` / `PostToolUse` / etc.
End with a short "Agent SDK vs Client SDK" note: el Agent SDK maneja el ciclo de tools por ti; el Client SDK lo programas tú.
Include the official URL as a "verificar versión vigente" footer link.

- [ ] **Step 3: Verify**

Run: `grep -c -iE 'tools|permissions|sessions|subagents|mcp|hooks' ~/.agents/skills/agent-sdk-builder/reference/concepts.md`
Expected: count ≥ 6 (all six blocks present).

---

### Task 3: Python reference (`reference/python.md`)

**Files:**
- Create: `~/.agents/skills/agent-sdk-builder/reference/python.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the **authoritative Python API** that Task 5 reuses verbatim — specifically: the `query()` call shape, `ClaudeAgentOptions` field names, the message-iteration pattern, and the **permission-approval callback signature** (name, parameters, return shape). Task 5 must not invent any of these.

- [ ] **Step 1: Fetch official Python docs**

Run (via WebFetch):
- `https://code.claude.com/docs/en/agent-sdk/python` (API reference)
- `https://code.claude.com/docs/en/agent-sdk/permissions` (permission-approval callback / `can_use_tool` / PreToolUse decision shape)
Extract exact: `query()` signature, `ClaudeAgentOptions` fields (`allowed_tools`, `permission_mode`, `hooks`, `agents`, `mcp_servers`, and the approval-callback field), the callback's parameters and its allow/deny return value, and how to read the final result message.

- [ ] **Step 2: Write `reference/python.md`** with these sections (real content, no placeholders):
  - **Instalación:** `pip install claude-agent-sdk` (Python 3.10+; nota del error si la versión es menor).
  - **Auth (suscripción):** `claude setup-token` → `export CLAUDE_CODE_OAUTH_TOKEN=...`; correr sin `ANTHROPIC_API_KEY`; advertencia de prioridad. One-line note that API key auth exists but is out of scope.
  - **Patrón base:** the exact `query(...)` + `async for message in ...` snippet from the docs.
  - **Campos de `ClaudeAgentOptions`:** `allowed_tools`, `permission_mode`, `agents`, `mcp_servers`, `hooks`, and the approval callback — each one line, copied from docs.
  - **Permisos con aprobación:** the exact callback signature + allow/deny return shape (this is what Task 5 consumes).
  - Footer: official URLs.

- [ ] **Step 3: Verify the approval-callback API is captured**

Run: `grep -iE 'can_use_tool|permission|allow|deny' ~/.agents/skills/agent-sdk-builder/reference/python.md`
Expected: the callback field name and its allow/deny return shape appear (non-empty match). If empty, the doc fetch missed it — re-fetch before proceeding (Task 5 depends on this).

---

### Task 4: TypeScript reference (`reference/typescript.md`)

**Files:**
- Create: `~/.agents/skills/agent-sdk-builder/reference/typescript.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the **authoritative TypeScript API** Task 6 reuses verbatim — `query()` shape, camelCase option fields (`allowedTools`, `permissionMode`, `hooks`, `agents`, `mcpServers`), the message iteration (`for await`), and the permission-approval callback signature/return shape.

- [ ] **Step 1: Fetch official TypeScript docs**

Run (via WebFetch):
- `https://code.claude.com/docs/en/agent-sdk/typescript`
- `https://code.claude.com/docs/en/agent-sdk/permissions`
Extract exact: `query({ prompt, options })` shape, camelCase option fields, `for await (const message of ...)`, and the approval-callback signature + allow/deny return.

- [ ] **Step 2: Write `reference/typescript.md`** mirroring `python.md` section-for-section:
  - **Instalación:** `npm install @anthropic-ai/claude-agent-sdk` (trae binario de Claude Code incluido).
  - **Auth (suscripción):** same as Python (token + `CLAUDE_CODE_OAUTH_TOKEN`, sin `ANTHROPIC_API_KEY`).
  - **Patrón base:** exact `query({...})` + `for await` snippet.
  - **Campos (camelCase):** `allowedTools`, `permissionMode`, `agents`, `mcpServers`, `hooks`, approval callback.
  - **Permisos con aprobación:** exact callback signature + return shape (Task 6 consumes this).
  - Footer: official URLs.

- [ ] **Step 3: Verify**

Run: `grep -iE 'allowedTools|permission|allow|deny' ~/.agents/skills/agent-sdk-builder/reference/typescript.md`
Expected: non-empty (camelCase fields + callback shape present).

---

### Task 5: Python starter template (`templates/python-starter/`)

**Files:**
- Create: `~/.agents/skills/agent-sdk-builder/templates/python-starter/agent.py`
- Create: `~/.agents/skills/agent-sdk-builder/templates/python-starter/requirements.txt`
- Create: `~/.agents/skills/agent-sdk-builder/templates/python-starter/.env.example`
- Create: `~/.agents/skills/agent-sdk-builder/templates/python-starter/README.md`

**Interfaces:**
- Consumes: the exact `query()` call, `ClaudeAgentOptions` fields, and approval-callback signature captured in `reference/python.md` (Task 3). Do NOT invent these — open `reference/python.md` and copy the verified forms.
- Produces: a runnable read-only-by-default agent used as the scaffold base.

- [ ] **Step 1: Write `requirements.txt`**

```
claude-agent-sdk
```

- [ ] **Step 2: Write `.env.example`**

```
# Suscripción Claude Max (modo único de esta skill).
# Genera el token con:  claude setup-token
CLAUDE_CODE_OAUTH_TOKEN=
# NO definas ANTHROPIC_API_KEY: tiene prioridad y facturaría por API.
```

- [ ] **Step 3: Write `agent.py`**

Requirements for the file (write complete code; pull the exact SDK forms from `reference/python.md`):
- Comments in Spanish explaining each section.
- Startup checks (before any SDK call):
  - if `CLAUDE_CODE_OAUTH_TOKEN` is missing → print how to generate it (`claude setup-token`) and exit.
  - if `ANTHROPIC_API_KEY` is set → print a warning that it takes priority and would bill API; suggest `unset ANTHROPIC_API_KEY`.
  - if `sys.version_info < (3, 10)` → print explicit message and exit.
- Build `ClaudeAgentOptions` with `allowed_tools=["Read", "Glob", "Grep", "WebSearch"]` (read-only pre-approved) and the approval callback (verbatim signature from `reference/python.md`) that, for `Bash`/`Edit`/`Write`, prints the requested action and reads `input("¿permitir? (s/n): ")`, returning allow on `s` and deny otherwise.
- Prompt: `"¿Qué archivos hay en este directorio?"`.
- Iterate messages with the documented `async for` pattern and print the final result.

Skeleton (fill the SDK-specific lines from the reference doc):

```python
import os
import sys
import asyncio
# from claude_agent_sdk import query, ClaudeAgentOptions   # confirmar import exacto en reference/python.md

def _check_env() -> None:
    if sys.version_info < (3, 10):
        sys.exit("Se requiere Python 3.10+. Versión actual: %s" % sys.version.split()[0])
    if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        sys.exit("Falta CLAUDE_CODE_OAUTH_TOKEN. Genéralo con: claude setup-token")
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("AVISO: ANTHROPIC_API_KEY está definida y tiene prioridad; facturaría por API. "
              "Ejecuta: unset ANTHROPIC_API_KEY")

# Callback de aprobación: copiar firma exacta de reference/python.md.
# Para Bash/Edit/Write imprime la acción y pide confirmación (s/n).

async def main() -> None:
    _check_env()
    # options = ClaudeAgentOptions(
    #     allowed_tools=["Read", "Glob", "Grep", "WebSearch"],
    #     can_use_tool=<callback>,   # nombre/forma exactos de reference/python.md
    # )
    # async for message in query(prompt="¿Qué archivos hay en este directorio?", options=options):
    #     ... imprimir resultado final ...

if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 4: Write `README.md`** with exactly these steps:
  1. `python3 --version` (debe ser ≥ 3.10).
  2. `pip install -r requirements.txt`.
  3. `claude setup-token` y `export CLAUDE_CODE_OAUTH_TOKEN=<token>`; `unset ANTHROPIC_API_KEY`.
  4. Smoke test: `python agent.py` → debe listar los archivos del directorio.

- [ ] **Step 5: Verify the file is syntactically valid Python**

Run: `python3 -m py_compile ~/.agents/skills/agent-sdk-builder/templates/python-starter/agent.py && echo OK`
Expected: `OK` (no syntax errors). Note: this does not run the agent (that needs the token + subscription) — it only confirms the file parses.

---

### Task 6: TypeScript starter template (`templates/typescript-starter/`)

**Files:**
- Create: `~/.agents/skills/agent-sdk-builder/templates/typescript-starter/agent.ts`
- Create: `~/.agents/skills/agent-sdk-builder/templates/typescript-starter/package.json`
- Create: `~/.agents/skills/agent-sdk-builder/templates/typescript-starter/.env.example`
- Create: `~/.agents/skills/agent-sdk-builder/templates/typescript-starter/README.md`

**Interfaces:**
- Consumes: the exact `query()` shape, camelCase option fields, iteration pattern, and approval-callback signature from `reference/typescript.md` (Task 4). Do NOT invent these.
- Produces: the TS scaffold base, behaviorally identical to the Python starter.

- [ ] **Step 1: Write `package.json`**

```json
{
  "name": "agent-sdk-starter",
  "version": "0.1.0",
  "type": "module",
  "scripts": { "start": "node --experimental-strip-types agent.ts" },
  "dependencies": { "@anthropic-ai/claude-agent-sdk": "*" }
}
```

- [ ] **Step 2: Write `.env.example`** (same content as the Python starter's `.env.example`).

- [ ] **Step 3: Write `agent.ts`**

Same behavior as `agent.py`, using the verified TS API from `reference/typescript.md`:
- Comments in Spanish.
- Startup checks: missing `CLAUDE_CODE_OAUTH_TOKEN` → message + exit; `ANTHROPIC_API_KEY` set → warning.
- `options` with `allowedTools: ["Read", "Glob", "Grep", "WebSearch"]` + approval callback (verbatim from reference) prompting (s/n) for `Bash`/`Edit`/`Write`.
- Prompt `"¿Qué archivos hay en este directorio?"`; iterate with `for await`; print final result.

Skeleton (fill SDK lines from the reference doc):

```typescript
// import { query } from "@anthropic-ai/claude-agent-sdk"; // confirmar en reference/typescript.md

function checkEnv(): void {
  if (!process.env.CLAUDE_CODE_OAUTH_TOKEN) {
    console.error("Falta CLAUDE_CODE_OAUTH_TOKEN. Genéralo con: claude setup-token");
    process.exit(1);
  }
  if (process.env.ANTHROPIC_API_KEY) {
    console.warn("AVISO: ANTHROPIC_API_KEY tiene prioridad y facturaría por API. Ejecuta: unset ANTHROPIC_API_KEY");
  }
}

// Callback de aprobación: copiar firma exacta de reference/typescript.md.

async function main(): Promise<void> {
  checkEnv();
  // for await (const message of query({ prompt: "¿Qué archivos hay en este directorio?", options: { allowedTools: [...], /* callback */ } })) { ... }
}

main();
```

- [ ] **Step 4: Write `README.md`** mirroring the Python one:
  1. `node --version` (≥ 22 recomendado para `--experimental-strip-types`; si no, compilar con `tsc`/`tsx`).
  2. `npm install`.
  3. `claude setup-token` + `export CLAUDE_CODE_OAUTH_TOKEN=<token>`; `unset ANTHROPIC_API_KEY`.
  4. Smoke test: `npm start` → debe listar los archivos.

- [ ] **Step 5: Verify the TS file parses**

Run: `node --check ~/.agents/skills/agent-sdk-builder/templates/typescript-starter/agent.ts 2>/dev/null && echo OK || echo "revisar con tsc/tsx"`
Expected: `OK` if the runtime supports TS type-stripping; otherwise note to validate with `tsc --noEmit`. Either way confirm the file has no plain-JS syntax errors.

---

### Task 7: End-to-end validation

**Files:**
- No new files. Validates the whole skill.

**Interfaces:**
- Consumes: all files from Tasks 1–6.
- Produces: confirmation the skill is well-formed and (where possible) the starter runs.

- [ ] **Step 1: Confirm structure**

Run: `find ~/.agents/skills/agent-sdk-builder -type f | sort`
Expected: SKILL.md, DESIGN.md, PLAN.md, reference/{concepts,python,typescript}.md, templates/python-starter/{agent.py,requirements.txt,.env.example,README.md}, templates/typescript-starter/{agent.ts,package.json,.env.example,README.md}.

- [ ] **Step 2: Confirm no leftover placeholder markers in shipped files**

Run: `grep -rnE 'TODO|TBD|confirmar en reference|<callback>|copiar firma exacta' ~/.agents/skills/agent-sdk-builder/templates ~/.agents/skills/agent-sdk-builder/reference ~/.agents/skills/agent-sdk-builder/SKILL.md`
Expected: **no matches** in `SKILL.md`, `reference/`, or `templates/` — every "fill from reference" placeholder from the skeletons must have been replaced with the real SDK API. (Matches are allowed only in `PLAN.md`/`DESIGN.md`.)

- [ ] **Step 3: Live smoke test (requires the user's environment)**

Ask the user to run, in a scratch dir with the Python starter copied and the token exported:
`python agent.py`
Expected: the agent lists the files in the directory using read-only tools, with no approval prompt (read-only tools are pre-approved). If a `Bash` action is attempted, an (s/n) prompt appears.
If the user lacks Python/token at this moment, mark this step as deferred and note it explicitly — do not claim the smoke test passed.

- [ ] **Step 4: Reload note**

Confirm to the user that the new skill loads on the next Claude Code session (`/exit` then `claude --continue`), same as the other skills installed today.
