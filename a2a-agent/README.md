# A2A Agents - NinjaAgent y PirateAgent

Agentes de IA expuestos a través del protocolo **A2A (Agent-to-Agent)** implementados en .NET 9.

- **NinjaAgent** 🥷 - Habla con sabiduría misteriosa y filosófica
- **PirateAgent** 🏴‍☠️ - Habla como un pirata

## 🏗️ Arquitectura

```
┌──────────────────┐     ┌─────────────────┐     ┌──────────────┐
│  A2A Client      │────▶│  NinjaAgent     │────▶│ Azure OpenAI │
│  (Workflow,      │◀────│  Puerto 5067    │◀────│              │
│   Teams Bot)     │     └─────────────────┘     │  GPT-4.1     │
│                  │     ┌─────────────────┐     │              │
│                  │────▶│  PirateAgent    │────▶│              │
│                  │◀────│  Puerto 5066    │◀────│              │
└──────────────────┘     └─────────────────┘     └──────────────┘
```

## 📁 Estructura del Proyecto

```
a2a-agent/
├── a2a-agent.sln              # Solución .NET
├── ninjaagent/
│   ├── Program.cs             # Código principal del ninja
│   ├── LoggingChatClient.cs   # Wrapper para logging de LLM
│   ├── Dockerfile             # Dockerfile para Container Apps
│   └── ninjaagent.csproj
└── pirateagent/
    ├── Program.cs             # Código principal del pirata
    ├── LoggingChatClient.cs
    ├── Dockerfile
    └── pirateagent.csproj
```

## 🚀 Requisitos Previos

- .NET 9.0 SDK
- Azure OpenAI endpoint y API Key
- Docker (para despliegue)
- Azure CLI (para despliegue en Container Apps)

## ⚙️ Configuración

### Variables de Entorno

```bash
export AZURE_OPENAI_ENDPOINT="https://<tu-recurso>.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4.1"
export AZURE_OPENAI_API_KEY="<tu-api-key>"

# Solo para Container Apps (HTTPS)
export AGENT_BASE_URL="https://<tu-container-app>.azurecontainerapps.io"
```

O en `appsettings.Development.json`:

```json
{
  "AZURE_OPENAI_ENDPOINT": "https://<tu-recurso>.openai.azure.com/",
  "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4.1",
  "AZURE_OPENAI_API_KEY": "<tu-api-key>"
}
```

## 🏃 Ejecución Local

### Desarrollo

```bash
# Terminal 1 - NinjaAgent
cd ninjaagent
dotnet run

# Terminal 2 - PirateAgent
cd pirateagent
dotnet run
```

Los agentes estarán disponibles en:
- NinjaAgent: `http://localhost:5067/a2a/ninja`
- PirateAgent: `http://localhost:5066/a2a/pirate`

## 🐳 Despliegue en Azure Container Apps

### 1. Construir imágenes Docker

```bash
cd ninjaagent
docker build -t ninjaagent .

cd ../pirateagent
docker build -t pirateagent .
```

### 2. Subir a Azure Container Registry

```bash
# Login en ACR
az acr login --name <tu-acr>

# Tag y push
docker tag ninjaagent <tu-acr>.azurecr.io/ninjaagent:latest
docker tag pirateagent <tu-acr>.azurecr.io/pirateagent:latest

docker push <tu-acr>.azurecr.io/ninjaagent:latest
docker push <tu-acr>.azurecr.io/pirateagent:latest
```

### 3. Crear Container Apps

```bash
# Crear Container Apps Environment
az containerapp env create \
  --name cae-a2a-agents \
  --resource-group <tu-rg> \
  --location <region>

# Crear NinjaAgent
az containerapp create \
  --name ninjaagent \
  --resource-group <tu-rg> \
  --environment cae-a2a-agents \
  --image <tu-acr>.azurecr.io/ninjaagent:latest \
  --registry-server <tu-acr>.azurecr.io \
  --target-port 5067 \
  --ingress external \
  --env-vars \
    AZURE_OPENAI_ENDPOINT="<endpoint>" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4.1" \
    AZURE_OPENAI_API_KEY="<api-key>" \
    AGENT_BASE_URL="https://ninjaagent.<domain>.azurecontainerapps.io"

# Crear PirateAgent (similar)
az containerapp create \
  --name pirateagent \
  --resource-group <tu-rg> \
  --environment cae-a2a-agents \
  --image <tu-acr>.azurecr.io/pirateagent:latest \
  --registry-server <tu-acr>.azurecr.io \
  --target-port 5066 \
  --ingress external \
  --env-vars \
    AZURE_OPENAI_ENDPOINT="<endpoint>" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4.1" \
    AZURE_OPENAI_API_KEY="<api-key>" \
    AGENT_BASE_URL="https://pirateagent.<domain>.azurecontainerapps.io"
```

> **Importante**: La variable `AGENT_BASE_URL` es necesaria para que el Agent Card devuelva la URL HTTPS correcta cuando se ejecuta detrás de un proxy.

## 🔌 Endpoints A2A

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/a2a/ninja/v1/card` | GET | Agent Card del ninja |
| `/a2a/ninja` | POST | Enviar mensaje al ninja |
| `/a2a/pirate/v1/card` | GET | Agent Card del pirata |
| `/a2a/pirate` | POST | Enviar mensaje al pirata |

## 🧪 Pruebas

### Verificar Agent Card

```bash
curl https://<tu-agent>.azurecontainerapps.io/a2a/ninja/v1/card
```

### Enviar Mensaje

```bash
curl -X POST https://<tu-agent>.azurecontainerapps.io/a2a/ninja \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "messageId": "msg-001",
        "role": "user",
        "parts": [{"kind": "text", "text": "¿Cuál es el camino del guerrero?"}]
      }
    }
  }'
```

## 📊 Logging

Los agentes incluyen logging detallado para demos:

```
🥷 Ninja Agent started!
🔗 A2A endpoint: /a2a/ninja
📋 Agent Card: /a2a/ninja/v1/card

═══════════════════════════════════════════════════════════
📥 A2A REQUEST RECEIVED
   Path: /a2a/ninja
   Method: POST
   📝 Request Body: {"method":"message/send",...}
═══════════════════════════════════════════════════════════

🤖 🧠 LLM REQUEST
🤖    [user]: ¿Cuál es el camino del guerrero?
🤖 📤 LLM RESPONSE
🤖    Response: El camino del guerrero es como el río...
```

## 📚 Referencias

- [A2A Protocol Specification](https://github.com/google/A2A)
- [Microsoft.Extensions.AI](https://devblogs.microsoft.com/dotnet/introducing-microsoft-extensions-ai-preview/)
- [Azure Container Apps](https://docs.microsoft.com/azure/container-apps/)
