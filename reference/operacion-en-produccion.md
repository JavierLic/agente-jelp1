# Referencia: operación en producción (lecciones de agentes reales)

Cosas que **no salen en los docs del SDK** pero rompen agentes de verdad. Carga este
archivo cuando el agente vaya a: **usar un navegador**, **correr solo** (cron/launchd) o
**integrarse con apps del usuario** (correo, OneDrive, etc.).

## 1. Navegador headless: cierre GARANTIZADO (si no, satura la máquina)

Un `browser` de Playwright que no se cierra deja procesos `chrome-headless-shell` vivos
que acumulan RAM y traban la Mac. El cierre debe estar garantizado **aunque la lógica
lance excepción**. Regla: un navegador por tarea (abrir → usar → cerrar), `headless=True`,
y verificar que no queden procesos.

```python
import atexit, signal, subprocess
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright

_PROC = "chrome-headless-shell"

@asynccontextmanager
async def navegador(headless: bool = True):
    async with async_playwright() as p:            # mata el driver al salir del bloque
        browser = await p.chromium.launch(headless=headless)
        try:
            context = await browser.new_context(accept_downloads=True)
            yield await context.new_page()
        finally:
            await browser.close()                  # cierra aunque haya excepción

def _matar_huerfanos(*_):
    subprocess.run(["pkill", "-f", _PROC], capture_output=True)

atexit.register(_matar_huerfanos)                  # cierre de emergencia si el proceso muere
try:
    signal.signal(signal.SIGTERM, lambda *_: (_matar_huerfanos(), exit(0)))
except (ValueError, OSError):
    pass                                           # no es el hilo principal; el finally igual cierra
```

Uso: `async with navegador() as page: ...`. Verifica tras correr: `pgrep -fl
chrome-headless-shell` debe salir vacío. La clave es `async with async_playwright()` +
`try/finally`; el `atexit/SIGTERM` es el respaldo para `kill`/Ctrl-C.

> Cuidado con el `pkill` global: solo úsalo en un proceso dedicado al agente. Si el
> agente convive con otros navegadores headless, mata solo los que él lanzó (rastrea PIDs).

## 2. Agentes que corren solos (launchd / cron)

Para que el agente trabaje sin que lo lances, un `LaunchAgent` (macOS) que corra un
wrapper cada N segundos. El wrapper activa el venv, corre el agente y **loguea**:

```bash
#!/bin/zsh
cd "$HOME/Proyectos/mi-agente" || exit 1
mkdir -p logs
source .venv/bin/activate
echo "===== $(date '+%F %T') =====" >> logs/run.log
python main.py >> logs/run.log 2>&1
```

`~/Library/LaunchAgents/com.tuempresa.miagente.plist` con `StartInterval` (segundos),
`RunAtLoad`, y `StandardOutPath`/`StandardErrorPath`. Cargar: `launchctl load <plist>`;
verificar: `launchctl list | grep miagente`.

- **Idempotencia:** la corrida debe poder repetirse sin duplicar. Procesa por lotes y
  **mueve** lo ya hecho a otra carpeta para no reprocesarlo.
- **Acciones de salida (enviar correo, publicar):** decide explícito con el usuario si el
  corre-solo **ejecuta** o **deja borrador**. Por defecto, borrador hasta validar.
- **Permiso de Automatización (macOS):** la primera vez que un proceso de launchd controle
  otra app (osascript → Outlook/Finder), macOS pide autorizar *Automatización*. Avísale al
  usuario que dé **Permitir** una vez.

## 3. Integrarse con apps del usuario: gotchas reales

- **Outlook "nuevo" en Mac:** por AppleScript **SÍ envía / crea borradores**, pero **NO
  lee** la bandeja Exchange (drafts/inbox salen vacíos). Para *ingerir* correo no uses
  AppleScript: usa **Power Automate**, Microsoft Graph o IMAP.
- **Power Automate como "feeder" sin código ni admin:** flujo *"Cuando llega correo con
  adjuntos → Crear archivo en OneDrive"* deja los archivos en una carpeta que el agente
  vigila. Usa el permiso del propio usuario (no requiere admin del tenant). Es la forma
  más robusta de meter correo a un agente local.
- **OneDrive / Dropbox (carpetas que sincronizan):** el agente lee archivos **locales**; la
  bajada nube→disco **se atora a veces** (la subida suele ir bien). Si el agente "no ve"
  archivos que sí están en la nube: `open -a OneDrive` o `killall OneDrive` y reintenta.
- **Permisos de macOS en general:** leer pantalla (computer-use) pide *Grabación de
  pantalla*; leer cookies del navegador pide *Keychain*. No asumas que están concedidos;
  ten un plan B que use solo el permiso que el usuario ya tiene.

## 4. Procesa por el dato autoritativo + guardián de seguridad

- **No confíes en el remitente ni en el nombre de archivo** (mienten o son ambiguos).
  Decide con el **dato autoritativo de adentro**. Ej.: para una factura mexicana, el RFC
  del receptor en el **XML del CFDI**, no el asunto del correo.
- **Guardián:** define qué SÍ debe procesar el agente y **aparta** (no borres) lo demás sin
  actuar. Ej.: si una carpeta puede recibir cosas ajenas, filtra por el identificador
  correcto y mueve lo que no aplica a `_apartados/` — nunca lo envíes ni lo proceses.
- Esto evita el peor fallo de un agente con auto-envío: mandar/actuar sobre algo que no
  era suyo.

## 5. Dónde vive el código del agente

El código **NO** va en carpetas que sincronizan (OneDrive, Dropbox, iCloud): sincronizan
`venv/`, `node_modules/`, `.git/` y traban la máquina. Código **local** (ej.
`~/Proyectos/<agente>`) + respaldo en un repo Git privado. Los **datos** del agente sí
pueden vivir en la nube (es lo que el usuario quiere ver/respaldar).
