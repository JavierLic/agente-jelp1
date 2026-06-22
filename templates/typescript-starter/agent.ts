// Agente mínimo del Claude Agent SDK (TypeScript).
// Permisos: lectura pre-aprobada (Read/Glob/Grep/WebSearch); aprobación manual (s/n)
// para acciones sensibles (Bash/Edit/Write). Auth: suscripción Claude Max.

import { query } from "@anthropic-ai/claude-agent-sdk";
import * as readline from "readline/promises";

// Tools que requieren aprobación manual.
const SENSIBLES = new Set(["Bash", "Edit", "Write"]);

// Valida la autenticación antes de cualquier llamada al SDK.
function revisarEntorno(): void {
  if (!process.env.CLAUDE_CODE_OAUTH_TOKEN) {
    console.error(
      "Falta CLAUDE_CODE_OAUTH_TOKEN.\n" +
        "Genéralo con:  claude setup-token  (requiere plan Pro/Max/Team/Enterprise)\n" +
        "Luego:         export CLAUDE_CODE_OAUTH_TOKEN=<token>",
    );
    process.exit(1);
  }
  if (process.env.ANTHROPIC_API_KEY) {
    console.warn(
      "AVISO: ANTHROPIC_API_KEY está definida y tiene prioridad sobre el token de\n" +
        "suscripción; facturaría por API. Ejecuta:  unset ANTHROPIC_API_KEY",
    );
  }
}

async function preguntar(q: string): Promise<string> {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const r = await rl.question(q);
  rl.close();
  return r;
}

async function main(): Promise<void> {
  revisarEntorno();
  for await (const message of query({
    prompt: "¿Qué archivos hay en este directorio?",
    options: {
      allowedTools: ["Read", "Glob", "Grep", "WebSearch"], // pre-aprobadas
      permissionMode: "default",                           // lo demás pasa por el callback
      canUseTool: async (toolName, input) => {
        if (SENSIBLES.has(toolName)) {
          console.log(`\nEl agente quiere usar ${toolName}: ${JSON.stringify(input)}`);
          const r = (await preguntar("¿permitir? (s/n): ")).trim().toLowerCase();
          if (r !== "s") return { behavior: "deny", message: "Rechazado por el usuario" };
        }
        return { behavior: "allow", updatedInput: input };
      },
    },
  })) {
    if ("result" in message) console.log(message.result);
  }
}

main();
