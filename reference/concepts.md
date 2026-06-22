# Conceptos del Claude Agent SDK

Los 6 bloques que necesitas entender. Los ejemplos son ilustrativos (Python); la
sintaxis exacta y verificada vive en `python.md` y `typescript.md`.

## 1. Tools (herramientas)

El agente trae herramientas integradas: `Read`, `Write`, `Edit`, `Bash`, `Glob`,
`Grep`, `WebSearch`, `WebFetch` (y más). Tú eliges cuáles puede usar con
`allowed_tools` (Python) / `allowedTools` (TS). El SDK ejecuta las herramientas por ti.

```python
options = ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"])
```

## 2. Permissions (permisos)

Controlas qué puede hacer el agente: pre-aprobar tools seguras (vía `allowed_tools`),
pedir aprobación antes de acciones sensibles, o bloquear. Postura por defecto de esta
skill: lectura pre-aprobada (`Read`/`Glob`/`Grep`/`WebSearch`) y aprobación para
`Bash`/`Edit`/`Write`.

## 3. Sessions (sesiones)

El agente recuerda contexto entre turnos. Capturas el `session_id` (del mensaje de
init) y reanudas más tarde con `resume`, manteniendo todo el contexto previo.

## 4. Subagents (subagentes)

Delegas subtareas a agentes especializados con `AgentDefinition`, invocados vía la
tool `Agent` (incluye `"Agent"` en `allowed_tools` para auto-aprobarlos).

## 5. MCP (Model Context Protocol)

Conectas sistemas externos (bases de datos, navegadores, APIs) como tools del agente
vía `mcp_servers`. Para *crear* tus propios servidores MCP, usa la skill
`mcp-server-dev` (ya instalada).

## 6. Hooks

Corres código tuyo en momentos clave del ciclo del agente: `PreToolUse`,
`PostToolUse`, `Stop`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`. Sirven para
validar, registrar, bloquear o transformar el comportamiento.

---

## Agent SDK vs Client SDK

- **Agent SDK** (esto): Claude maneja el ciclo de pensar → usar tool → ver resultado →
  repetir, por ti. Le das un objetivo y se encarga.
- **Client SDK** (la API de mensajes): tú programas ese ciclo a mano.

Para construir agentes que actúan solos, usa el Agent SDK.

---

Verificar versión vigente: https://code.claude.com/docs/en/agent-sdk/overview
