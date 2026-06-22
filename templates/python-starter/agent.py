"""Agente mínimo del Claude Agent SDK (Python).

Postura de permisos: lectura pre-aprobada (Read/Glob/Grep/WebSearch) y aprobación
manual (s/n) para acciones sensibles (Bash/Edit/Write).
Autenticación: suscripción Claude Max. Usa tu login de Claude Code automáticamente;
el token CLAUDE_CODE_OAUTH_TOKEN solo hace falta en CI/servidores sin login.
"""

import os
import sys
import asyncio

# La verificación de versión va ANTES de importar el SDK (que requiere 3.10+).
if sys.version_info < (3, 10):
    sys.exit("Se requiere Python 3.10+. Versión actual: " + sys.version.split()[0])

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
from claude_agent_sdk.types import (
    HookMatcher,
    PermissionResultAllow,
    PermissionResultDeny,
    ToolPermissionContext,
)

# Tools que requieren aprobación manual.
SENSIBLES = {"Bash", "Edit", "Write"}


def revisar_entorno() -> None:
    """Revisa la autenticación de suscripción. NO aborta si falta el token: el SDK
    usa tu login de Claude Code cuando está disponible."""
    if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        print(
            "Nota: CLAUDE_CODE_OAUTH_TOKEN no está definido; usaré tu login de Claude\n"
            "Code (suscripción) si está disponible. En CI/servidores sin login, genera\n"
            "un token con:  claude setup-token  y expórtalo como CLAUDE_CODE_OAUTH_TOKEN."
        )
    if os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "AVISO: ANTHROPIC_API_KEY está definida y tiene prioridad sobre la\n"
            "suscripción; facturaría por API. Ejecuta:  unset ANTHROPIC_API_KEY"
        )


async def aprobar(tool_name: str, input_data: dict, context: ToolPermissionContext):
    """Pre-aprueba lectura; pide confirmación (s/n) para acciones sensibles."""
    if tool_name in SENSIBLES:
        print(f"\nEl agente quiere usar {tool_name}: {input_data}")
        if input("¿permitir? (s/n): ").strip().lower() != "s":
            return PermissionResultDeny(message="Rechazado por el usuario")
    return PermissionResultAllow(updated_input=input_data)


# Hook dummy: mantiene el stream abierto para que can_use_tool pueda invocarse.
async def dummy_hook(input_data, tool_use_id, context):
    return {"continue_": True}


# Prompt en modo streaming (generador async), requerido por can_use_tool.
async def prompt_stream():
    yield {
        "type": "user",
        "message": {"role": "user", "content": "¿Qué archivos hay en este directorio?"},
    }


async def main() -> None:
    revisar_entorno()
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep", "WebSearch"],  # pre-aprobadas
        permission_mode="default",                            # lo demás pasa por el callback
        can_use_tool=aprobar,
        hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[dummy_hook])]},
    )
    async for message in query(prompt=prompt_stream(), options=options):
        if isinstance(message, ResultMessage):
            print(message.result)


if __name__ == "__main__":
    asyncio.run(main())
