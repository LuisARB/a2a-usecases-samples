# Teams A2A Agent with ChatPrompt

Bot de Microsoft Teams que usa **ChatPrompt** con **A2AClientPlugin** para comunicarse con agentes A2A.

## 🏗️ Arquitectura

```
┌─────────────────┐     ┌──────────────────────────────────────────────┐     ┌─────────────────┐
│  Microsoft      │────▶│           Teams A2A Bot                       │────▶│  Pirate Agent   │
│  Teams          │◀────│  ┌────────────────────────────────────────┐  │◀────│  (A2A Server)   │
└─────────────────┘     │  │            ChatPrompt                   │  │     │  Puerto 5066    │
                        │  │  ┌──────────────┐  ┌────────────────┐   │  │     └─────────────────┘
                        │  │  │ OpenAI Model │  │ A2AClientPlugin│   │  │              │
                        │  │  │ (Orquestador)│  │ (Pirate Agent) │   │  │              ▼
                        │  │  └──────────────┘  └────────────────┘   │  │     ┌──────────────┐
                        │  └────────────────────────────────────────┘  │     │ Azure OpenAI │
                        └──────────────────────────────────────────────┘     └──────────────┘
                                    Puerto 3980
```

## 📁 Diferencia con teams-a2a-agent

| Característica | teams-a2a-agent | teams-a2a-agent-chatprompt |
|----------------|-----------------|----------------------------|
| **Comunicación A2A** | Directa (A2AAgentClient) | Via plugin (A2AClientPlugin) |
| **Orquestación** | Manual | ChatPrompt con LLM |
| **Modelo LLM** | Solo en agente A2A | Dos modelos (orquestador + agente) |
| **Decisión de routing** | Código | El LLM decide cuándo usar el agente |
| **Historial de conversación** | No | Sí, gestionado por ChatPrompt |

## 📁 Estructura del Proyecto

```
teams-a2a-agent-chatprompt/
├── src/
│   └── main.py              # Código principal con ChatPrompt
├── appPackage/
│   ├── manifest.json        # Manifest de Teams
│   ├── color.png
│   └── outline.png
├── .env.example             # Template de variables de entorno
├── pyproject.toml           # Dependencias Python
└── teamsapp.local.yml       # Configuración de Teams Toolkit
```

## 🚀 Requisitos Previos

1. **Python 3.12+**
2. **uv** - Gestor de paquetes Python
3. **Azure OpenAI** - Para el modelo orquestador
4. **Agente A2A corriendo** - El pirateagent en puerto 5066

## ⚙️ Configuración

### 1. Configurar Variables de Entorno

Copiar `.env.example` a `.env` y configurar:

```env
PORT=3980
DEVTOOLS_PORT=3981
CLIENT_ID=<tu-app-id>
CLIENT_SECRET=<tu-client-secret>
TENANT_ID=<tu-tenant-id>

# A2A Agent Configuration
A2A_AGENT_BASE_URL=http://localhost:5066/a2a/pirate
A2A_AGENT_CARD_URL=v1/card

# Azure OpenAI Configuration (para ChatPrompt orquestador)
AZURE_OPENAI_ENDPOINT=https://<tu-recurso>.openai.azure.com/
AZURE_OPENAI_API_KEY=<tu-api-key>
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

### 2. Instalar Dependencias

```bash
cd teams-a2a-agent-chatprompt

# Opción 1: Con pip
python3 -m venv .venv
source .venv/bin/activate
pip install python-dotenv microsoft-teams-apps microsoft-teams-ai microsoft-teams-a2a microsoft-teams-openai microsoft-teams-devtools

# Opción 2: Con uv
uv sync
```

### 3. Instalar y Configurar Dev Tunnel

Dev Tunnels permite exponer tu servidor local a internet para que Microsoft Teams pueda comunicarse con tu bot.

#### Instalación

**Linux (x64):**
```bash
curl -sL https://aka.ms/TunnelsCliDownload/linux-x64 -o devtunnel
chmod +x devtunnel
sudo mv devtunnel /usr/local/bin/
```

**Linux (ARM64):**
```bash
curl -sL https://aka.ms/TunnelsCliDownload/linux-arm64 -o devtunnel
chmod +x devtunnel
sudo mv devtunnel /usr/local/bin/
```

**macOS (Intel):**
```bash
curl -sL https://aka.ms/TunnelsCliDownload/osx-x64-zip -o devtunnel.zip
unzip devtunnel.zip
chmod +x devtunnel
sudo mv devtunnel /usr/local/bin/
```

**macOS (Apple Silicon):**
```bash
curl -sL https://aka.ms/TunnelsCliDownload/osx-arm64-zip -o devtunnel.zip
unzip devtunnel.zip
chmod +x devtunnel
sudo mv devtunnel /usr/local/bin/
```

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri https://aka.ms/TunnelsCliDownload/win-x64-exe -OutFile devtunnel.exe
# Mover a una carpeta en el PATH o agregar la ubicación actual al PATH
```

#### Verificar instalación

```bash
devtunnel --version
```

#### Iniciar sesión

```bash
# Login con cuenta Microsoft (abre navegador)
devtunnel user login

# O login con código de dispositivo (sin navegador)
devtunnel user login -d

# O login con cuenta de GitHub
devtunnel user login -g
```

#### Crear y configurar el túnel

```bash
# Crear un túnel persistente con nombre
devtunnel create teams-a2a-chatprompt --allow-anonymous

# Agregar el puerto del bot (3980)
devtunnel port create teams-a2a-chatprompt -p 3980

# Ver la URL del túnel
devtunnel show teams-a2a-chatprompt
```

La salida mostrará la URL pública, por ejemplo:
```
Connect via browser: https://abc123xyz.devtunnels.ms:3980
```

**Usa esta URL** para configurar el endpoint del bot en Azure y en el manifest de Teams.

#### Comandos útiles

```bash
# Listar todos los túneles
devtunnel list

# Eliminar un túnel
devtunnel delete teams-a2a-chatprompt

# Ver información del usuario actual
devtunnel user show
```

### 4. Configurar URL del Túnel en el Manifest

El manifest de Teams (`appPackage/manifest.json`) usa **variables de entorno** para evitar hardcodear URLs. La variable `${{BOT_DOMAIN}}` se resuelve automáticamente desde los archivos de entorno.

#### Opción A: Configurar manualmente (sin Teams Toolkit)

1. **Obtener la URL del túnel:**
   ```bash
   devtunnel show teams-a2a-chatprompt
   ```
   Copia el dominio (ej: `abc123xyz.devtunnels.ms`)

2. **Actualizar el archivo de entorno** `env/.env.dev`:
   ```env
   BOT_DOMAIN=abc123xyz.devtunnels.ms
   BOT_ENDPOINT=https://abc123xyz.devtunnels.ms
   ```

3. **Generar el manifest resuelto:**
   ```bash
   cd appPackage
   
   # Usar envsubst para reemplazar variables (Linux/macOS)
   export $(cat ../env/.env.dev | grep -v '^#' | xargs)
   cat manifest.json | envsubst > build/manifest.json
   ```

#### Opción B: Script automático (recomendado)

Crea un script `scripts/build-package.sh`:

```bash
#!/bin/bash
set -e

# Obtener URL del túnel automáticamente
TUNNEL_URL=$(devtunnel show teams-a2a-chatprompt 2>/dev/null | grep -oP 'https://\K[^/]+' | head -1)

if [ -z "$TUNNEL_URL" ]; then
    echo "❌ Error: No se encontró el túnel. Asegúrate de haberlo creado."
    exit 1
fi

echo "🔗 URL del túnel: $TUNNEL_URL"

# Cargar variables de entorno
export $(cat env/.env.dev | grep -v '^#' | xargs)
export BOT_DOMAIN="$TUNNEL_URL"
export BOT_ENDPOINT="https://$TUNNEL_URL"

# Crear directorio de build si no existe
mkdir -p appPackage/build

# Generar manifest con variables resueltas
envsubst < appPackage/manifest.json > appPackage/build/manifest.json

echo "✅ Manifest generado en appPackage/build/manifest.json"
```

Ejecutar:
```bash
chmod +x scripts/build-package.sh
./scripts/build-package.sh
```

#### Opción C: Con Teams Toolkit (VS Code)

Si usas **Teams Toolkit** en VS Code:

1. Actualiza `env/.env.dev` con la URL del túnel:
   ```env
   BOT_DOMAIN=abc123xyz.devtunnels.ms
   BOT_ENDPOINT=https://abc123xyz.devtunnels.ms
   ```

2. Ejecuta **Teams Toolkit: Provision** - esto genera el manifest automáticamente

### 5. Generar el Paquete ZIP de Teams

Una vez que el manifest está configurado:

```bash
cd appPackage/build

# Crear el paquete ZIP con los archivos necesarios
zip -j ../teams-a2a-chatprompt.zip manifest.json ../color.png ../outline.png

echo "✅ Paquete creado: appPackage/teams-a2a-chatprompt.zip"
```

**Script completo** (añadir a `scripts/build-package.sh`):

```bash
#!/bin/bash
set -e

# Obtener URL del túnel automáticamente
TUNNEL_URL=$(devtunnel show teams-a2a-chatprompt 2>/dev/null | grep -oP 'https://\K[^/]+' | head -1)

if [ -z "$TUNNEL_URL" ]; then
    echo "❌ Error: No se encontró el túnel. Créalo con: devtunnel create teams-a2a-chatprompt --allow-anonymous"
    exit 1
fi

echo "🔗 URL del túnel: $TUNNEL_URL"

# Cargar variables de entorno base
if [ -f env/.env.dev ]; then
    export $(cat env/.env.dev | grep -v '^#' | xargs)
fi

# Configurar variables del túnel
export BOT_DOMAIN="$TUNNEL_URL"
export BOT_ENDPOINT="https://$TUNNEL_URL"
export TEAMS_APP_ID="${TEAMS_APP_ID:-$(uuidgen | tr '[:upper:]' '[:lower:]')}"
export BOT_ID="${BOT_ID:-$TEAMS_APP_ID}"
export APP_NAME_SUFFIX="${APP_NAME_SUFFIX:-dev}"

# Crear directorio de build
mkdir -p appPackage/build

# Generar manifest con variables resueltas
envsubst < appPackage/manifest.json > appPackage/build/manifest.json

# Crear paquete ZIP
cd appPackage/build
zip -j ../teams-a2a-chatprompt.zip manifest.json ../color.png ../outline.png

echo ""
echo "✅ Paquete generado: appPackage/teams-a2a-chatprompt.zip"
echo ""
echo "📋 Configuración aplicada:"
echo "   BOT_DOMAIN=$BOT_DOMAIN"
echo "   BOT_ID=$BOT_ID"
echo "   TEAMS_APP_ID=$TEAMS_APP_ID"
```

### 6. Instalar la App en Teams

1. Abre **Microsoft Teams**
2. Ve a **Apps** → **Manage your apps** → **Upload an app**
3. Selecciona **Upload a custom app**
4. Sube el archivo `appPackage/teams-a2a-chatprompt.zip`
5. Instala y abre el chat con el bot

## 🏃 Ejecución

### 1. Asegurarse que el Agente A2A está corriendo

```bash
cd ../a2a-agent/pirateagent
dotnet run --urls "http://localhost:5066"
```

### 2. Iniciar el Bot de Teams

```bash
cd teams-a2a-agent-chatprompt
uv run python src/main.py
```

### 3. Iniciar Dev Tunnel

```bash
# Iniciar el túnel configurado previamente
devtunnel host teams-a2a-chatprompt --allow-anonymous
```

> **Nota:** El túnel debe estar corriendo para que Teams pueda enviar mensajes a tu bot local.

## 💡 Cómo Funciona

1. **Usuario envía mensaje** en Teams
2. **ChatPrompt recibe el mensaje** y lo procesa con el modelo OpenAI orquestador
3. **El LLM decide** si necesita usar el agente pirata (A2AClientPlugin)
4. Si es necesario, **A2AClientPlugin envía la petición** al agente A2A
5. **La respuesta se devuelve** al usuario a través de Teams

### Ejemplo de Flujo

```
Usuario: "¿Cómo se dice 'buenos días' en pirata?"

ChatPrompt (OpenAI):
  → Detecta que necesita el agente pirata
  → Llama al A2AClientPlugin con "pirate-agent"

A2AClientPlugin:
  → POST http://localhost:5066/a2a/pirate
  → Recibe respuesta del Pirate Agent

ChatPrompt:
  → Integra la respuesta del agente pirata
  → Devuelve al usuario: "¡Arrr, buenos días se dice: 'Buen amanecer, marinero de agua salada!'"
```

## 📊 Logs

Ver logs en tiempo real:

```bash
# Logs del bot de Teams
tail -f /tmp/teams-bot-chatprompt.log

# Logs del agente A2A
tail -f /tmp/pirateagent.log
```

## 🔧 Personalización

### Cambiar el System Message del Orquestador

En `src/main.py`:

```python
prompt = ChatPrompt(
    model=model,
    plugins=[a2a_client],
    system_message="""Tu nuevo system message aquí.
Define cuándo usar el agente pirata."""
)
```

### Agregar Más Agentes A2A

```python
# Agregar otro agente
a2a_client.on_use_plugin(
    A2APluginUseParams(
        key="ninja-agent",
        base_url="http://localhost:5067/a2a/ninja",
        card_url="v1/card"
    )
)

# Actualizar system message
system_message="""Puedes usar:
- 'pirate-agent' para respuestas de pirata
- 'ninja-agent' para respuestas misteriosas de ninja"""
```

## 📚 Referencias

- [microsoft-teams-a2a Package](https://github.com/microsoft/teams.py/blob/main/packages/a2aprotocol/README.md)
- [microsoft-teams-ai Package](https://github.com/microsoft/teams.py/blob/main/packages/ai/README.md)
- [A2A Protocol](https://github.com/google/A2A)
