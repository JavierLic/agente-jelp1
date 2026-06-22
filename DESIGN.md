# Diseño: skill `agent-sdk-builder`

**Fecha:** 2026-06-22
**Autor:** Javier (ACM) + Claude
**Estado:** Aprobado por el usuario, pendiente de implementación

## 1. Propósito

Una skill personal que enseña, hace scaffold y sirve de referencia para construir
agentes con el **Claude Agent SDK** en Python o TypeScript. Cubre tres modos de uso
según lo que pida el usuario en el momento: aprender, construir (scaffold) o
consultar referencia.

No reemplaza ni se solapa con gstack (no es navegación web). Es específica para
desarrollar agentes propios sobre el Agent SDK (uso personal/interno: ACM, MedMarket,
GBM).

## 2. Decisiones tomadas (brainstorming)

| Decisión | Valor |
|---|---|
| Propósito | Enseñar + scaffold + referencia (combinado) |
| Lenguajes | Python **y** TypeScript (pregunta cuál por proyecto) |
| Scaffold | Mínimo que corre (agente "hola mundo"), sin ruido |
| Permisos por defecto | Lectura pre-aprobada + ejecución (Bash/Edit/Write) con aprobación |
| Autenticación | **Solo modo suscripción** (`CLAUDE_CODE_OAUTH_TOKEN`); API key solo como nota |
| Estructura | Divulgación progresiva (Opción B): SKILL.md corto + reference/ + templates/ |
| Ubicación | `~/.agents/skills/agent-sdk-builder/` (global, symlink a Claude Code) |

## 3. Arquitectura (Opción B — divulgación progresiva)

```
agent-sdk-builder/
├── SKILL.md              ← router corto (~1 pantalla)
├── reference/
│   ├── concepts.md       ← 6 bloques: tools, permissions, sessions, subagents, MCP, hooks
│   ├── python.md         ← instalación, auth (suscripción), patrón query()
│   └── typescript.md     ← instalación, auth (suscripción), patrón query()
└── templates/
    ├── python-starter/   ← agent.py + requirements.txt + .env.example + README.md
    └── typescript-starter/ ← agent.ts + package.json + .env.example + README.md
```

### Flujo del router (SKILL.md)

1. Detecta intención: aprender / construir (scaffold) / consultar referencia.
2. Si construye o aprende → pregunta: ¿Python o TypeScript?
3. Carga solo el archivo que toca (concepts.md / python.md / typescript.md / template).
4. Para scaffold: copia el starter, ajusta nombre, explica cada archivo, recuerda
   configurar `CLAUDE_CODE_OAUTH_TOKEN`.
5. Cierra recordando la postura de permisos por defecto y cómo ampliarla con cuidado.

## 4. Contenido de referencia

### reference/concepts.md
Los 6 bloques en 3–5 líneas cada uno + mini-ejemplo:
- **Tools** — Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch; selección con `allowed_tools`.
- **Permissions** — pre-aprobar / pedir aprobación / bloquear; aquí vive el default del usuario.
- **Sessions** — memoria entre turnos; capturar `session_id` y `resume`.
- **Subagents** — delegar vía `AgentDefinition` + tool `Agent`.
- **MCP** — conectar sistemas externos; enlaza con `mcp-server-dev` ya instalado.
- **Hooks** — código propio en `PreToolUse`/`PostToolUse`/etc.
Cierra con: Agent SDK (Claude maneja el ciclo de tools) vs Client SDK (tú lo programas).

### reference/python.md
- `pip install claude-agent-sdk` (requiere Python 3.10+).
- **Auth (modo suscripción):** `claude setup-token` → exportar `CLAUDE_CODE_OAUTH_TOKEN`.
  Correr **sin** `ANTHROPIC_API_KEY` (esta tiene prioridad y facturaría por API).
- Patrón base: `query(prompt, options=ClaudeAgentOptions(...))` con `async for`.
- Campos: `allowed_tools`, `permission_mode`, `agents=`, `mcp_servers=`, `hooks=`.
- Nota breve: existe también auth por API key para producción/terceros (no documentada aquí).

### reference/typescript.md
- `npm install @anthropic-ai/claude-agent-sdk` (trae binario de Claude Code incluido).
- **Auth (modo suscripción):** igual, `claude setup-token` → `CLAUDE_CODE_OAUTH_TOKEN`.
- Patrón base: `query({ prompt, options })` con `for await`.
- Campos camelCase: `allowedTools`, `permissionMode`, `agents`, `mcpServers`, `hooks`.

Todo el contenido proviene de la documentación oficial de Anthropic (code.claude.com /
docs.claude.com), con enlaces para verificar la versión vigente.

## 5. Templates (scaffold)

Estructura idéntica en ambos lenguajes:
```
agent.{py,ts}     ← agente "hola mundo" que corre
requirements.txt / package.json
.env.example      ← CLAUDE_CODE_OAUTH_TOKEN=
README.md         ← cómo correrlo en 3 pasos + smoke test
```

`agent.py` / `agent.ts`:
- Tarea sencilla (ej. "¿qué archivos hay en este directorio?").
- Permisos por defecto: lectura (`Read`, `Glob`, `Grep`, `WebSearch`) pre-aprobada;
  acciones sensibles (`Bash`, `Edit`, `Write`) pasan por una función de aprobación
  que imprime la acción y espera confirmación (s/n).
- Comentarios en español explicando cada línea (objetivo didáctico).

## 6. Manejo de errores (el starter valida y avisa claro)

- Falta `CLAUDE_CODE_OAUTH_TOKEN` → instrucción para generarlo con `claude setup-token`.
- `ANTHROPIC_API_KEY` presente junto al OAuth token → aviso: tiene prioridad y
  facturaría por API; sugerir desexportarla.
- Python < 3.10 → aviso explícito.
- Dependencias sin instalar → instrucción exacta.

## 7. Pruebas

Smoke test: correr el agente una vez y verificar que responde / lista archivos.
El README incluye ese paso. Para agentes reales, la skill sugiere probar primero
en solo-lectura.

## 8. Fuera de alcance (YAGNI)

- Slash command / scripts de auto-scaffold (Opción C) — se puede agregar después.
- Plantillas a medida de los sistemas del usuario (CFDI, portal) — solo el mínimo.
- Documentar autenticación por API key, Bedrock/Vertex/Azure — solo nota breve.

## 9. Notas

- La carpeta no es un repo git; el spec se guarda aquí (junto a la futura skill) y se
  omite el commit.
- La skill carga en sesión nueva tras instalarse (igual que find-skills/subagent-creator).
