# Teams A2A Agent

Bot de Microsoft Teams que se comunica con un agente de IA usando el protocolo **A2A (Agent-to-Agent)**.

## 🏗️ Arquitectura

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Microsoft      │────▶│  Teams A2A Bot   │────▶│  Pirate Agent   │────▶│ Azure OpenAI │
│  Teams          │◀────│  (Python)        │◀────│  (A2A Server)   │◀────│              │
└─────────────────┘     └──────────────────┘     └─────────────────┘     └──────────────┘
      Usuario              Puerto 3978            Puerto 5066           LLM en la nube
```

## 📁 Estructura del Proyecto

```
teams-a2a-agent/
├── src/
│   └── main.py              # Código principal del bot
├── appPackage/
│   ├── manifest.json        # Manifest de Teams (template)
│   ├── color.png            # Icono de la app
│   ├── outline.png          # Icono outline
│   └── build/
│       └── manifest.json    # Manifest con valores reales
├── .env                     # Variables de entorno (credenciales)
├── pyproject.toml           # Dependencias Python
└── teamsapp.local.yml       # Configuración de Teams Toolkit
```

## 🚀 Requisitos Previos

1. **Python 3.12+**
2. **uv** - Gestor de paquetes Python: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. **.NET 9.0** - Para el agente A2A (pirateagent)
4. **Azure CLI** - Para crear recursos de Azure
5. **Dev Tunnel** - Para exponer el bot a internet

## ⚙️ Configuración

### 1. Crear Azure Bot Service

```bash
# Login en Azure
az login --use-device-code

# Crear App Registration
az ad app create --display-name "TeamsA2aAgent" --sign-in-audience AzureADMultipleOrgs

# Obtener el App ID de la salida anterior y crear secreto
az ad app credential reset --id <APP_ID> --append

# Crear Service Principal (IMPORTANTE)
az ad sp create --id <APP_ID>

# Crear Azure Bot Service (SingleTenant)
TENANT_ID=$(az account show --query tenantId -o tsv)
az bot create \
  --resource-group "<RESOURCE_GROUP>" \
  --name "teams-a2a-bot" \
  --app-type SingleTenant \
  --appid "<APP_ID>" \
  --tenant-id "$TENANT_ID" \
  --endpoint "https://<TU_TUNNEL_URL>/api/messages"

# Habilitar canal de Teams
az bot msteams create --resource-group "<RESOURCE_GROUP>" --name "teams-a2a-bot"
```

### 2. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
PORT=3978
CLIENT_ID=<tu-app-id>
CLIENT_SECRET=<tu-client-secret>
TENANT_ID=<tu-tenant-id>
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
devtunnel create teams-a2a-bot --allow-anonymous

# Agregar el puerto del bot (3978)
devtunnel port create teams-a2a-bot -p 3978

# Ver la URL del túnel
devtunnel show teams-a2a-bot
```

#### Iniciar el túnel

```bash
# Iniciar el túnel (mantenlo corriendo mientras usas el bot)
devtunnel host teams-a2a-bot --allow-anonymous
```

La salida mostrará la URL pública, por ejemplo:
```
Connect via browser: https://abc123xyz.devtunnels.ms:3978
```

**Usa esta URL** para configurar el endpoint del bot en Azure y en el manifest de Teams.

#### Comandos útiles

```bash
# Listar todos los túneles
devtunnel list

# Eliminar un túnel
devtunnel delete teams-a2a-bot

# Ver información del usuario actual
devtunnel user show
```

### 4. Generar Paquete de Teams

El proyecto incluye un script que genera automáticamente el paquete ZIP con la URL del túnel:

```bash
# Generar paquete con valores del túnel automáticamente
# Usa el BOT_ID obtenido al crear el Azure Bot
BOT_ID="<your-bot-id>" \
TEAMS_APP_ID="<your-bot-id>" \
./scripts/build-package.sh
```

El script:
1. Detecta la URL del túnel `teams-a2a-bot`
2. Reemplaza las variables en el manifest
3. Genera `appPackage/teams-a2a-agent.zip`

**Manualmente** (alternativa):

```bash
cd appPackage/build
zip -j ../teams-a2a-agent.zip manifest.json ../color.png ../outline.png
```

## 🏃 Ejecución

### 1. Iniciar el Agente A2A (terminal 1)

```bash
cd a2a-agent/pirateagent
dotnet run --urls "http://localhost:5066"
```

### 2. Iniciar el Dev Tunnel (terminal 2)

```bash
devtunnel host teams-a2a-bot --allow-anonymous
```

### 3. Iniciar el Bot de Teams (terminal 3)

```bash
cd teams-a2a-agent
uv run python src/main.py
```

### 3. Iniciar el Dev Tunnel

```bash
devtunnel host --allow-anonymous
```

### 4. Instalar en Teams

1. Abrir Microsoft Teams
2. Ir a **Apps** → **Manage your apps** → **Upload an app**
3. Seleccionar **Upload a custom app**
4. Subir `appPackage/teams-a2a-agent.zip`
5. Instalar y abrir el chat con el bot

## 📊 Monitoreo y Logs

### Ver logs del Bot de Teams

```bash
tail -f /tmp/teams-bot.log
```

### Ver logs del Agente A2A

```bash
tail -f /tmp/pirateagent.log
```

### Ejemplo de flujo en logs

```
# Bot de Teams recibe mensaje
INFO: 52.112.116.180:0 - "POST /api/messages HTTP/1.1" 200 OK

# Agente A2A recibe petición
📥 A2A REQUEST RECEIVED
   Path: /a2a/pirate
   Method: POST
   📝 Request Body: {"method":"message/send","params":{"message":{"parts":[{"text":"Hola"}]}}}

# LLM procesa el mensaje
🧠 LLM REQUEST
   [user]: Hola
📤 LLM RESPONSE
   Response: ¡Arrr, saludos marinero!
```

## 🔧 Solución de Problemas

### Error: `AADSTS7000229: missing service principal`

```bash
az ad sp create --id <APP_ID>
```

### Error: `invalid_client`

Verifica que:
1. El `.env` tiene las credenciales correctas
2. El Service Principal existe
3. El secreto no ha expirado

### Error: `Connection refused` al agente A2A

Asegúrate de que el agente pirateagent está corriendo en el puerto 5066:

```bash
curl http://localhost:5066/a2a/pirate/v1/card
```

### El túnel no funciona

Verifica que el túnel está activo:

```bash
curl https://<tu-tunnel-url>/
```

## 📚 Referencias

- [A2A Protocol](https://github.com/google/A2A)
- [Microsoft Teams SDK](https://github.com/microsoft/teams.py)
- [Azure Bot Service](https://docs.microsoft.com/azure/bot-service/)
- [Dev Tunnels](https://docs.microsoft.com/azure/developer/dev-tunnels/)
