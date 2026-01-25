# A2A Protocol Use Cases - Sample Repository

Colección de ejemplos que demuestran cómo comunicarse con agentes de IA utilizando el protocolo **A2A (Agent-to-Agent)** en la plataforma Microsoft (Azure AI Foundry y Microsoft Teams).

## 📚 Ejemplos



[**a2a-agent**](./a2a-agent/) | Agentes A2A en .NET (NinjaAgent y PirateAgent) que pueden desplegarse en Azure Container Apps | .NET 9, Azure OpenAI 

[**a2a-agents-workflow**](./a2a-agents-workflow/) | Workflow que orquesta múltiples agentes A2A usando Microsoft Agent Framework, desplegable como Hosted Agent en Azure AI Foundry | Python, Agent Framework 

[**teams-a2a-agent**](./teams-a2a-agent/) | Bot de Microsoft Teams que se comunica directamente con agentes A2A | Python, Teams AI Library  

[**teams-a2a-agent-chatprompt**](./teams-a2a-agent-chatprompt/) | Bot de Teams con ChatPrompt y A2AClientPlugin para orquestación inteligente | Python, Teams AI Library 

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Azure AI Foundry                                    │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                    A2A Workflow (Hosted Agent)                            │  │
│  │                    a2a-agents-workflow                                    │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  │                  ▼
┌───────────────────────────┐          │    ┌───────────────────────────┐
│   Azure Container Apps    │          │    │   Azure Container Apps    │
│  ┌─────────────────────┐  │          │    │  ┌─────────────────────┐  │
│  │    NinjaAgent 🥷    │  │          │    │  │   PirateAgent 🏴‍☠️  │  │
│  │    a2a-agent        │  │          │    │  │    a2a-agent        │  │
│  └─────────────────────┘  │          │    │  └─────────────────────┘  │
└───────────────────────────┘          │    └───────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
┌───────────────────────────┐             ┌───────────────────────────┐
│    Microsoft Teams        │             │    Microsoft Teams        │
│  ┌─────────────────────┐  │             │  ┌─────────────────────┐  │
│  │  teams-a2a-agent    │  │             │  │ teams-a2a-agent-    │  │
│  │                     │  │             │  │ chatprompt          │  │
│  └─────────────────────┘  │             │  └─────────────────────┘  │
└───────────────────────────┘             └───────────────────────────┘
```

## 🚀 Quick Start

### Prerrequisitos

- Python 3.12+
- .NET 9.0 SDK
- Azure CLI
- Docker (para despliegue)
- Cuenta de Azure con acceso a Azure OpenAI y Azure AI Foundry

### Orden de Despliegue Recomendado

1. **Desplegar los agentes A2A** ([a2a-agent](./a2a-agent/README.md))
   - Construir y subir imágenes Docker al Azure Container Registry
   - Crear Container Apps para NinjaAgent y PirateAgent

2. **Desplegar el workflow** ([a2a-agents-workflow](./a2a-agents-workflow/README.md))
   - Construir imagen Docker del workflow
   - Desplegar como Hosted Agent en Azure AI Foundry

3. **Opcional: Desplegar bot de Teams** ([teams-a2a-agent](./teams-a2a-agent/README.md))
   - Configurar Azure Bot Service
   - Instalar la app en Teams

## 📖 A2A Protocol Overview

El protocolo **Agent-to-Agent (A2A)** permite la comunicación estandarizada entre agentes de IA. Características principales:

- **Agent Card**: Metadatos del agente (nombre, descripción, capacidades)
- **JSON-RPC 2.0**: Formato de mensajes estandarizado
- **Streaming**: Soporte para respuestas en streaming (opcional)
- **Context Preservation**: Mantener contexto de conversación

### Ejemplo de Agent Card

```bash
curl https://mi-agente.azurecontainerapps.io/a2a/pirate/v1/card
```

```json
{
  "name": "PirateAgent",
  "description": "An agent that speaks like a pirate.",
  "version": "1.0",
  "protocolVersion": "0.3.0",
  "url": "https://mi-agente.azurecontainerapps.io/a2a/pirate",
  "capabilities": {
    "streaming": false,
    "pushNotifications": false
  }
}
```

### Ejemplo de Mensaje A2A

```bash
curl -X POST https://mi-agente.azurecontainerapps.io/a2a/pirate \
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
        "parts": [{"kind": "text", "text": "¡Hola pirata!"}]
      }
    }
  }'
```

## 📚 Documentación Detallada

Cada proyecto contiene su propio README con instrucciones detalladas:

- [**a2a-agent/README.md**](./a2a-agent/README.md) - Arquitectura, configuración y despliegue de agentes .NET
- [**a2a-agents-workflow/README.md**](./a2a-agents-workflow/README.md) - Workflow con Agent Framework y despliegue en Foundry
- [**teams-a2a-agent/README.md**](./teams-a2a-agent/README.md) - Bot de Teams con comunicación A2A directa
- [**teams-a2a-agent-chatprompt/README.md**](./teams-a2a-agent-chatprompt/README.md) - Bot con ChatPrompt y plugins

## 📚 Referencias

- [A2A Protocol Specification](https://github.com/google/A2A)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Azure AI Foundry](https://ai.azure.com/)
- [Microsoft Teams AI Library](https://github.com/microsoft/teams-ai)
