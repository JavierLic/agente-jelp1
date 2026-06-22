# Python starter — Claude Agent SDK

Agente mínimo que lista los archivos del directorio. Lectura pre-aprobada; pide
aprobación (s/n) para Bash/Edit/Write. Usa tu suscripción Claude Max.

## Pasos

1. Verifica Python 3.10+:
   ```bash
   python3 --version
   ```
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Autenticación (suscripción, no API):
   - Si ya usas Claude Code logueado en esta máquina, **no necesitas hacer nada**: el SDK usa ese login.
   - Solo para CI/servidores sin login, genera un token:
   ```bash
   claude setup-token
   export CLAUDE_CODE_OAUTH_TOKEN=<token>
   ```
   - Asegúrate de no tener `ANTHROPIC_API_KEY` (tiene prioridad y facturaría por API): `unset ANTHROPIC_API_KEY`
4. Smoke test:
   ```bash
   python agent.py
   ```
   Debe listar los archivos del directorio usando solo tools de lectura.