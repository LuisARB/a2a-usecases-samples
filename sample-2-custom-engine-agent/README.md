# Sample 2: Custom Engine Agent with Microsoft 365 Agents SDK

This sample demonstrates how to create a custom engine agent using Microsoft 365 Agents SDK that communicates with other agents using the A2A (Agent-to-Agent) protocol.

## Overview

This custom agent can process incoming requests and intelligently delegate tasks to other specialized agents using the A2A protocol. It maintains conversation context and can fallback to local processing when delegation is not available.

## Architecture

```
Client/User --> Custom Engine Agent --> [A2A Protocol] --> Target Agent
                      |                                         |
                      |<----------------------------------------|
                      |
                      v
                Local Processing (Fallback)
```

## Features

- ✅ Custom agent implementation with M365 Agents SDK patterns
- ✅ A2A protocol integration for agent delegation
- ✅ Conversation context management
- ✅ Fallback to local processing
- ✅ RESTful API endpoints
- ✅ Health checks and capabilities discovery
- ✅ Comprehensive error handling
- ✅ Structured logging

## Prerequisites

- Python 3.8 or higher
- Access to Microsoft 365 Agents SDK
- A target agent endpoint supporting A2A protocol (optional for local testing)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:
```
AGENT_ID=custom-engine-agent-001
AGENT_NAME=Custom Engine Agent
TARGET_AGENT_ENDPOINT=https://your-target-agent.com
TARGET_AGENT_API_KEY=your-api-key
PORT=8000
```

### 3. Run the Agent

```bash
python agent.py
```

The agent will start on `http://localhost:8000`

## API Endpoints

### POST /invoke
Invoke the agent with a message.

**Request:**
```json
{
  "message": "Your message here",
  "conversation_id": "optional-conversation-id"
}
```

**Response:**
```json
{
  "response": "Agent's response",
  "conversation_id": "conversation-id",
  "metadata": {
    "source": "delegated",
    "target_agent": "a2a_agent"
  }
}
```

### GET /capabilities
Get agent capabilities and information.

**Response:**
```json
{
  "agent_id": "custom-engine-agent-001",
  "agent_name": "Custom Engine Agent",
  "capabilities": [
    "message_processing",
    "conversation_context",
    "a2a_delegation"
  ],
  "protocol_version": "1.0",
  "has_delegation": true
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "custom-engine-agent",
  "agent_id": "custom-engine-agent-001"
}
```

## Testing the Agent

### Using curl

Test the agent locally:
```bash
# Invoke the agent
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, agent!", "conversation_id": "test-123"}'

# Get capabilities
curl http://localhost:8000/capabilities

# Health check
curl http://localhost:8000/health
```

### Using Python

```python
import aiohttp
import asyncio

async def test_agent():
    async with aiohttp.ClientSession() as session:
        # Invoke the agent
        async with session.post(
            "http://localhost:8000/invoke",
            json={
                "message": "What can you do?",
                "conversation_id": "test-conversation"
            }
        ) as response:
            result = await response.json()
            print(result)

asyncio.run(test_agent())
```

## A2A Protocol Implementation

The agent implements the A2A protocol for inter-agent communication:

### Request to Target Agent
```json
{
  "message": "Delegated message",
  "conversation_id": "conversation-id",
  "context": {
    "agent_id": "custom-engine-agent-001",
    "agent_name": "Custom Engine Agent",
    "history_length": 5
  },
  "timestamp": 1234567890.123
}
```

### Headers
- `Content-Type: application/json`
- `Authorization: Bearer <api-key>`
- `x-protocol: a2a`
- `x-protocol-version: 1.0`

### Response from Target Agent
```json
{
  "response": "Target agent's response",
  "conversation_id": "conversation-id",
  "metadata": {}
}
```

## Deployment

### Deploy to Azure Container Apps

1. Create a container registry:
```bash
az acr create --resource-group <rg-name> --name <acr-name> --sku Basic
```

2. Build and push the image:
```bash
az acr build --registry <acr-name> --image custom-engine-agent:latest .
```

3. Create the container app:
```bash
az containerapp create \
  --name custom-engine-agent \
  --resource-group <rg-name> \
  --environment <env-name> \
  --image <acr-name>.azurecr.io/custom-engine-agent:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    AGENT_ID=custom-engine-agent-001 \
    AGENT_NAME="Custom Engine Agent" \
    TARGET_AGENT_ENDPOINT="https://target-agent.com" \
    TARGET_AGENT_API_KEY=secretref:target-agent-key
```

### Deploy to Azure App Service

```bash
# Create App Service
az webapp create \
  --resource-group <rg-name> \
  --plan <plan-name> \
  --name <app-name> \
  --runtime "PYTHON:3.9"

# Configure environment variables
az webapp config appsettings set \
  --name <app-name> \
  --resource-group <rg-name> \
  --settings \
    AGENT_ID=custom-engine-agent-001 \
    AGENT_NAME="Custom Engine Agent" \
    TARGET_AGENT_ENDPOINT="https://target-agent.com" \
    TARGET_AGENT_API_KEY="your-api-key" \
    PORT=8000

# Deploy code
az webapp up --name <app-name> --resource-group <rg-name>
```

## Code Structure

```
sample-2-custom-engine-agent/
├── agent.py                 # Main agent implementation
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── README.md               # This file
├── Dockerfile              # Docker configuration (optional)
└── deploy.yaml             # Deployment configuration (optional)
```

### Key Components

- **A2AProtocolClient**: Handles communication with other agents using A2A protocol
- **CustomEngineAgent**: Main agent logic with delegation and local processing
- **AgentMessage**: Data structure for conversation messages
- **API Handlers**: RESTful endpoints for agent invocation

## Advanced Features

### Conversation Context
The agent maintains conversation history for each conversation ID, enabling context-aware responses.

### Delegation Strategy
The agent can intelligently decide when to delegate to specialized agents versus handling requests locally.

### Error Handling
Comprehensive error handling with fallback to local processing when delegation fails.

## Troubleshooting

### Agent doesn't start
- Check that port 8000 is available
- Verify all required environment variables are set
- Check the console logs for specific errors

### Delegation fails
- Verify the target agent endpoint is accessible
- Check that the API key is correct
- Ensure the target agent supports A2A protocol

### Timeout errors
- Check network connectivity to the target agent
- Consider increasing timeout values in the code
- Verify the target agent is responding

## Next Steps

- Add authentication and authorization
- Implement more sophisticated delegation logic
- Add metrics and monitoring
- Support for multiple target agents
- Implement caching for improved performance
- Add support for streaming responses

## Resources

- [Microsoft 365 Agents SDK Documentation](https://learn.microsoft.com/en-us/microsoft-365/agents/)
- [A2A Protocol Specification](https://github.com/microsoft/agents)
- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)

## License

MIT License - See LICENSE file for details
