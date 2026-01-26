# A2A Agents Workflow

Workflow secuencial que orquesta dos agentes A2A utilizando **Microsoft Agent Framework**, desplegable como **Hosted Agent** en Azure AI Foundry.

1. **NinjaAgent** 🥷 - Responde con sabiduría misteriosa y filosófica
2. **PirateAgent** 🏴‍☠️ - Traduce/responde al mensaje del ninja con estilo pirata

## 🏗️ Arquitectura

```
+------------------------------------------------------------------------------+
|                            Azure AI Foundry                                  |
|  +------------------------------------------------------------------------+  |
|  |                    A2A Workflow (Hosted Agent)                         |  |
|  |                                                                        |  |
|  |   [User Input]                                                         |  |
|  |        |                                                               |  |
|  |        v                                                               |  |
|  |   +--------------+    A2A    +--------------------------+              |  |
|  |   | NinjaExecutor|---------->| NinjaAgent  (Container)  |              |  |
|  |   |              |<----------|  Azure Container Apps    |              |  |
|  |   +--------------+           +--------------------------+              |  |
|  |        |                                                               |  |
|  |        v                                                               |  |
|  |   +--------------+    A2A    +--------------------------+              |  |
|  |   |PirateExecutor|---------->| PirateAgent (Container)  |              |  |
|  |   |              |<----------|  Azure Container Apps    |              |  |
|  |   +--------------+           +--------------------------+              |  |
|  |        |                                                               |  |
|  |        v                                                               |  |
|  |   [Final Output: Ninja + Pirate responses]                             |  |
|  +------------------------------------------------------------------------+  |
+------------------------------------------------------------------------------+
```

## 📁 Estructura del Proyecto

```
a2a-agents-workflow/
├── src/
│   ├── main.py             # Punto de entrada del workflow
│   ├── a2a_client.py       # Cliente A2A reutilizable
│   └── workflow.py         # Definición del workflow secuencial
├── Dockerfile              # Para Hosted Agent en Foundry
├── deploy_agent.py         # Script de despliegue a Azure AI Foundry
├── requirements.txt        # Dependencias Python
└── .env.example            # Ejemplo de variables de entorno
```

## 🚀 Requisitos Previos

- Python 3.12+
- Azure CLI
- Docker
- Los agentes NinjaAgent y PirateAgent desplegados en Azure Container Apps

## ⚙️ Configuración

### Variables de Entorno para Desarrollo Local

```bash
export NINJA_AGENT_URL="http://localhost:5067/a2a/ninja"
export PIRATE_AGENT_URL="http://localhost:5066/a2a/pirate"
export AZURE_AI_PROJECT_ENDPOINT="https://<tu-proyecto>.services.ai.azure.com/api/projects/<proyecto>"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1"
```

### Variables de Entorno para Despliegue

```bash
# Para el script deploy_agent.py
export PROJECT_ENDPOINT="https://<tu-proyecto>.services.ai.azure.com/api/projects/<proyecto>"
export AGENT_NAME="a2a-workflow-agent"
export CONTAINER_IMAGE="<tu-acr>.azurecr.io/a2a-agents-workflow:latest"
export NINJA_AGENT_URL="https://ninjaagent.<domain>.azurecontainerapps.io/a2a/ninja"
export PIRATE_AGENT_URL="https://pirateagent.<domain>.azurecontainerapps.io/a2a/pirate"
export AZURE_AI_PROJECT_ENDPOINT="https://<tu-proyecto>.services.ai.azure.com/api/projects/<proyecto>"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1"

# Opcional: Application Insights
export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=xxx;..."
```

## 🏃 Ejecución Local

### 1. Iniciar los agentes .NET

```bash
# Terminal 1 - NinjaAgent
cd ../a2a-agent/ninjaagent
dotnet run

# Terminal 2 - PirateAgent
cd ../a2a-agent/pirateagent
dotnet run
```

### 2. Ejecutar el workflow

```bash
cd a2a-agents-workflow
pip install -r requirements.txt
python src/main.py
```

## 🐳 Despliegue en Azure AI Foundry

### 1. Construir y subir la imagen Docker

```bash
# Desde la raíz del repositorio
docker build -t a2a-agents-workflow -f a2a-agents-workflow/Dockerfile .

# Tag y push al ACR
az acr login --name <tu-acr>
docker tag a2a-agents-workflow <tu-acr>.azurecr.io/a2a-agents-workflow:latest
docker push <tu-acr>.azurecr.io/a2a-agents-workflow:latest
```

### 2. Desplegar como Hosted Agent

```bash
# Configurar variables de entorno (ver sección anterior)
cd a2a-agents-workflow
python deploy_agent.py
```

El script `deploy_agent.py` creará una nueva versión del agente en Azure AI Foundry con las variables de entorno configuradas.

### 3. Probar desde Azure AI Foundry

Una vez desplegado, puedes probar el agente desde:
- Azure AI Foundry Portal → Agents → Tu agente → Playground
- API REST usando el endpoint del agente

## 📊 Flujo del Workflow

```
1. Usuario envía mensaje: "¿Qué es lo mejor de la vida?"

2. NinjaExecutor → NinjaAgent (A2A)
   Respuesta: "El camino del guerrero es como el río en la montaña..."

3. PirateExecutor → PirateAgent (A2A)
   Input: Respuesta del ninja
   Respuesta: "¡Arrr! Ese ninja habla con más misterio que un cofre hundido..."

4. Resultado final:
   {
     "original_input": "¿Qué es lo mejor de la vida?",
     "ninja_response": "El camino del guerrero es como el río...",
     "pirate_response": "¡Arrr! Ese ninja habla con más misterio..."
   }
```

## 🧪 Pruebas

### Probar localmente con curl

Si ejecutas el workflow localmente con `from_agent_framework`, el agente expone un endpoint:

```bash
curl -X POST http://localhost:8088/api/messages \
  -H "Content-Type: application/json" \
  -d '{"text": "¿Cuál es el secreto de la vida?"}'
```

### Probar desde Azure AI Foundry

Usa el Playground en el portal de Azure AI Foundry o la API REST del agente.

## 📝 Notas Importantes

- **URLs HTTPS**: Al desplegar en Azure, asegúrate de usar URLs HTTPS para los agentes
- **Application Insights**: Configura `APPLICATIONINSIGHTS_CONNECTION_STRING` para ver logs del agente
- **Timeouts**: Los agentes A2A pueden tardar varios segundos en responder

## 📚 Referencias

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Azure AI Foundry - Hosted Agents](https://learn.microsoft.com/azure/ai-studio/)
- [A2A Protocol Specification](https://github.com/google/A2A)
