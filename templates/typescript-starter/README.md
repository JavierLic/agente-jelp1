# TypeScript starter — Claude Agent SDK

Agente mínimo que lista los archivos del directorio. Lectura pre-aprobada; pide
aprobación (s/n) para Bash/Edit/Write. Usa tu suscripción Claude Max.

## Pasos

1. Verifica Node (22+ recomendado para `--experimental-strip-types`):
   ```bash
   node --version
   ```
2. Instala dependencias:
   ```bash
   npm install
   ```
3. Autentica con tu suscripción (no API):
   ```bash
   claude setup-token
   export CLAUDE_CODE_OAUTH_TOKEN=<token>
   unset ANTHROPIC_API_KEY      # por si estaba definida (tiene prioridad)
   ```
4. Smoke test:
   ```bash
   npm start
   ```
   Debe listar los archivos del directorio usando solo tools de lectura.
