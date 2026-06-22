# Referencia: Agent SDK en Python

API verificada contra la documentación oficial de Anthropic. Enlaces al final para
confirmar la versión vigente.

## Instalación

```bash
pip install claude-agent-sdk
```

Requiere **Python 3.10+**. Si `pip` dice `No matching distribution found for
claude-agent-sdk`, tu intérprete es menor a 3.10 (verifica con `python3 --version`).

## Autenticación (suscripción Claude Max)

Esta skill usa la suscripción, no API de pago por token. Dos casos:

- **En tu máquina con Claude Code logueado:** el SDK usa ese login automáticamente.
  No necesitas el token; solo corre el agente.
- **En CI / servidores sin login:** genera un token de larga duración (~1 año) y expórtalo:

```bash
claude setup-token                      # requiere Claude Code CLI + plan Pro/Max/Team/Enterprise
export CLAUDE_CODE_OAUTH_TOKEN=<token>
```

Corre **sin** `ANTHROPIC_API_KEY`: esa variable tiene prioridad y facturaría por API.
Si la tienes exportada de otro proyecto, ejecuta `unset ANTHROPIC_API_KEY`.

(Existe también auth por API key para producción/terceros; fuera del alcance de esta skill.)

## Patrón base (solo lectura, sin aprobación)

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def main():
    options = ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"])
    async for message in query(prompt="¿Qué archivos hay aquí?", options=options):
        if isinstance(message, ResultMessage):
            print(message.result)   # texto final

asyncio.run(main())
```

`query()` es asíncrono: se recorre con `async for`. El texto final está en
`ResultMessage.result`.

## Campos de `ClaudeAgentOptions`

- `allowed_tools: list[str]` — tools pre-aprobadas (ej. `["Read", "Glob", "Grep", "WebSearch"]`).
- `permission_mode` — ver abajo.
- `can_use_tool` — callback de aprobación para tools no pre-aprobadas.
- `hooks` — código propio en momentos clave (`PreToolUse`, `PostToolUse`, etc.).
- `agents` — subagentes (`dict[str, AgentDefinition]`).
- `mcp_servers` — servidores MCP a conectar.
- `system_prompt` — prompt de sistema.

## Permisos con aprobación

Modos (`permission_mode`):

```python
# "default"            → tools no pre-aprobadas disparan tu callback can_use_tool
# "dontAsk"            → niega todo lo no pre-aprobado (no llama al callback)
# "acceptEdits"        → auto-aprueba ediciones de archivos
# "bypassPermissions"  → aprueba todo (usar con cuidado; allowed_tools NO lo limita)
# "plan"               → explora/planea sin editar; ediciones pasan por el callback
```

> **IMPORTANTE (Python):** `can_use_tool` requiere **modo streaming** — el `prompt`
> debe ser un generador async que produce mensajes de usuario — **y** un hook
> `PreToolUse` dummy que retorne `{"continue_": True}`. Sin ese hook, el stream se
> cierra antes de que se invoque el callback. (En TypeScript no hace falta.)

Postura por defecto de esta skill (lectura pre-aprobada + aprobación para
`Bash`/`Edit`/`Write`):

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
from claude_agent_sdk.types import (
    HookMatcher,
    PermissionResultAllow,
    PermissionResultDeny,
    ToolPermissionContext,
)

SENSIBLES = {"Bash", "Edit", "Write"}

async def aprobar(tool_name: str, input_data: dict, context: ToolPermissionContext):
    if tool_name in SENSIBLES:
        print(f"El agente quiere usar {tool_name}: {input_data}")
        if input("¿permitir? (s/n): ").strip().lower() != "s":
            return PermissionResultDeny(message="Rechazado por el usuario")
    return PermissionResultAllow(updated_input=input_data)

# Hook dummy: mantiene el stream abierto para que can_use_tool pueda invocarse.
async def dummy_hook(input_data, tool_use_id, context):
    return {"continue_": True}

# Prompt en modo streaming (generador async).
async def prompt_stream():
    yield {"type": "user",
           "message": {"role": "user", "content": "¿Qué archivos hay aquí?"}}

async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep", "WebSearch"],  # pre-aprobadas
        permission_mode="default",                            # lo demás pasa por el callback
        can_use_tool=aprobar,
        hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[dummy_hook])]},
    )
    async for message in query(prompt=prompt_stream(), options=options):
        if isinstance(message, ResultMessage):
            print(message.result)

asyncio.run(main())
```

- Permitir: `PermissionResultAllow(updated_input=input_data)`.
- Negar: `PermissionResultDeny(message="...")` (opcional `interrupt=True`).

## Verificar / enlaces

- Python API: https://code.claude.com/docs/en/agent-sdk/python
- Permisos: https://code.claude.com/docs/en/agent-sdk/permissions
- Aprobaciones/input: https://code.claude.com/docs/en/agent-sdk/user-input
