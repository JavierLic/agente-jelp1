# Referencia: Agent SDK en TypeScript

API verificada contra la documentación oficial de Anthropic. Enlaces al final para
confirmar la versión vigente.

## Instalación

```bash
npm install @anthropic-ai/claude-agent-sdk
```

Trae incluido el binario de Claude Code para tu plataforma (no necesitas instalar
Claude Code por separado).

## Autenticación (suscripción Claude Max)

Esta skill usa la suscripción, no API de pago por token:

```bash
claude setup-token                      # requiere Claude Code CLI + plan Pro/Max/Team/Enterprise
export CLAUDE_CODE_OAUTH_TOKEN=<token>  # token de larga duración (~1 año)
```

Corre **sin** `ANTHROPIC_API_KEY`: esa variable tiene prioridad y facturaría por API.
Si la tienes exportada de otro proyecto, ejecuta `unset ANTHROPIC_API_KEY`.

(Existe también auth por API key para producción/terceros; fuera del alcance de esta skill.)

## Patrón base

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "¿Qué archivos hay aquí?",
  options: { allowedTools: ["Read", "Glob", "Grep"] },
})) {
  if ("result" in message) console.log(message.result);  // texto final
}
```

`query()` devuelve un iterable async: se recorre con `for await`. El texto final está
en el mensaje de tipo `result` (`message.result`).

## Campos de `options`

- `allowedTools: string[]` — tools pre-aprobadas (ej. `["Read", "Glob", "Grep", "WebSearch"]`).
- `disallowedTools: string[]` — tools negadas.
- `permissionMode` — ver abajo.
- `canUseTool` — callback de aprobación para tools no pre-aprobadas.
- `hooks` — código propio en momentos clave.
- `agents` — subagentes (`Record<string, AgentDefinition>`).
- `mcpServers` — servidores MCP a conectar.
- `systemPrompt` — prompt de sistema.

## Permisos con aprobación

Modos (`permissionMode`): `"default"` (lo no pre-aprobado dispara `canUseTool`),
`"dontAsk"` (niega sin preguntar), `"acceptEdits"`, `"bypassPermissions"` (aprueba
todo; `allowedTools` NO lo limita), `"plan"`.

Postura por defecto de esta skill (lectura pre-aprobada + aprobación para
`Bash`/`Edit`/`Write`):

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import * as readline from "readline/promises";

const SENSIBLES = new Set(["Bash", "Edit", "Write"]);

async function preguntar(q: string): Promise<string> {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const r = await rl.question(q);
  rl.close();
  return r;
}

for await (const message of query({
  prompt: "¿Qué archivos hay aquí?",
  options: {
    allowedTools: ["Read", "Glob", "Grep", "WebSearch"],  // pre-aprobadas
    permissionMode: "default",                            // lo demás pasa por el callback
    canUseTool: async (toolName, input) => {
      if (SENSIBLES.has(toolName)) {
        console.log(`El agente quiere usar ${toolName}: ${JSON.stringify(input)}`);
        const r = (await preguntar("¿permitir? (s/n): ")).trim().toLowerCase();
        if (r !== "s") return { behavior: "deny", message: "Rechazado por el usuario" };
      }
      return { behavior: "allow", updatedInput: input };
    },
  },
})) {
  if ("result" in message) console.log(message.result);
}
```

- Permitir: `{ behavior: "allow", updatedInput: input }`.
- Negar: `{ behavior: "deny", message: "..." }`.

(A diferencia de Python, en TypeScript `canUseTool` no necesita modo streaming ni un
hook dummy: funciona con un `prompt` de string.)

## Verificar / enlaces

- TypeScript API: https://code.claude.com/docs/en/agent-sdk/typescript
- Permisos: https://code.claude.com/docs/en/agent-sdk/permissions
- Aprobaciones/input: https://code.claude.com/docs/en/agent-sdk/user-input
