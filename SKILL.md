---
name: agente-jelp1
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
- **En una máquina con Claude Code logueado:** el SDK usa ese login automáticamente; no hace falta el token.
- **En CI/servidores sin login:** generar token con `claude setup-token` (requiere Claude Code CLI + plan Pro/Max/Team/Enterprise) y exportar `CLAUDE_CODE_OAUTH_TOKEN=<token>`.
- Correr **sin** `ANTHROPIC_API_KEY` (esa variable tiene prioridad y facturaría por API).

(Existe también auth por API key para producción/terceros; fuera del alcance de esta skill.)

## Permisos por defecto

Los agentes generados pre-aprueban tools de solo lectura (`Read`, `Glob`, `Grep`,
`WebSearch`) y piden aprobación para acciones sensibles (`Bash`, `Edit`, `Write`).
