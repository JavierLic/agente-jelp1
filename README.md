# agente-jelp1

Skill de Claude Code que **enseña, hace scaffold y sirve de referencia** para construir
agentes con el [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)
en **Python** o **TypeScript**.

Los agentes que genera se autentican con tu **suscripción Claude Max**
(`CLAUDE_CODE_OAUTH_TOKEN`), no con facturación por llamada API.

## Qué hace

Cuando la invocas, detecta tu intención y actúa en uno de tres modos:

- **Aprender** — explica los 6 bloques del SDK (tools, permisos, sesiones, subagentes, MCP, hooks).
- **Construir (scaffold)** — copia un proyecto base mínimo que ya corre y te explica cada archivo.
- **Consultar referencia** — guía de API de Python o TypeScript, con el API verificado contra la doc oficial.

Disparadores típicos: *"construye un agente SDK"*, *"créame un agente con Claude"*,
*"enséñame el Agent SDK"*.

## Instalación

Copia la carpeta a tu directorio de skills de agentes:

```bash
git clone <url-de-este-repo> ~/.agents/skills/agente-jelp1
```

Carga en la siguiente sesión de tu agente (Claude Code, Codex, etc.). Para verificar,
escribe `/` y búscala, o pídela en lenguaje natural.

## Autenticación (suscripción, no API de pago)

```bash
claude setup-token                      # requiere Claude Code CLI + plan Pro/Max/Team/Enterprise
export CLAUDE_CODE_OAUTH_TOKEN=<token>
unset ANTHROPIC_API_KEY                 # tiene prioridad y facturaría por API
```

## Permisos por defecto

Los agentes generados pre-aprueban tools de **solo lectura** (`Read`, `Glob`, `Grep`,
`WebSearch`) y piden **aprobación (s/n)** antes de acciones sensibles (`Bash`, `Edit`, `Write`).

## Estructura

```
agente-jelp1/
├── SKILL.md              # router de la skill
├── reference/
│   ├── concepts.md       # los 6 bloques del SDK
│   ├── python.md         # API Python (incl. modo streaming + hook de permisos)
│   └── typescript.md     # API TypeScript
└── templates/
    ├── python-starter/   # agent.py + requirements.txt + .env.example + README.md
    └── typescript-starter/ # agent.ts + package.json + .env.example + README.md
```

## Seguridad

🔒 **Nunca pongas tu token o API key en archivos rastreados por git.** El `.gitignore`
ya excluye `.env` y secretos; el token va en un `.env` local o como variable de entorno.
Los `.env.example` deben quedar siempre con el valor **vacío**.

## Licencia

[MIT](LICENSE) © 2026 Javier Lic. Úsalo, modifícalo y compártelo libremente.
