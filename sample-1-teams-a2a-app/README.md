# Sample 1: Microsoft Teams App with A2A Protocol

This sample demonstrates how to create a Microsoft Teams bot that communicates with an AI agent using the A2A (Agent-to-Agent) protocol.

## Overview

The bot receives messages from Microsoft Teams users and forwards them to an AI agent using the A2A protocol. The agent's responses are then sent back to the Teams user, creating a seamless conversational experience.

## Architecture

```
Teams User --> Teams Bot --> [A2A Protocol] --> AI Agent
                  ^                                  |
                  |__________________________________|
```

## Features

- ✅ Microsoft Teams integration using Bot Framework SDK
- ✅ A2A protocol communication with AI agents
- ✅ Asynchronous message handling
- ✅ Conversation context tracking
- ✅ Welcome messages for new users
- ✅ Typing indicators for better UX
- ✅ Error handling and user feedback

## Prerequisites

- Python 3.8 or higher
- Microsoft Teams account
- Azure Bot Service registration
- An AI agent endpoint that supports A2A protocol

## Setup Instructions

### 1. Register Your Bot in Azure

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new **Azure Bot** resource
3. Configure the messaging endpoint: `https://your-domain.com/api/messages`
4. Save your App ID and App Password

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:
```
MICROSOFT_APP_ID=your-app-id-from-azure
MICROSOFT_APP_PASSWORD=your-app-password-from-azure
A2A_AGENT_ENDPOINT=https://your-agent-endpoint.com
A2A_AGENT_API_KEY=your-agent-api-key
PORT=3978
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Bot

```bash
python app.py
```

The bot will start on `http://localhost:3978`

### 5. Test Locally with Bot Framework Emulator

1. Download and install [Bot Framework Emulator](https://github.com/Microsoft/BotFramework-Emulator/releases)
2. Open the emulator and connect to `http://localhost:3978/api/messages`
3. Enter your App ID and App Password
4. Start chatting with your bot!

### 6. Deploy to Azure

For production deployment, you can use Azure App Service:

```bash
# Create Azure App Service
az webapp create --resource-group <your-rg> --plan <your-plan> --name <your-bot-name> --runtime "PYTHON:3.9"

# Deploy the code
az webapp up --name <your-bot-name> --resource-group <your-rg>

# Set environment variables
az webapp config appsettings set --name <your-bot-name> --resource-group <your-rg> --settings \
    MICROSOFT_APP_ID="your-app-id" \
    MICROSOFT_APP_PASSWORD="your-app-password" \
    A2A_AGENT_ENDPOINT="your-agent-endpoint" \
    A2A_AGENT_API_KEY="your-api-key"
```

## A2A Protocol Integration

The bot uses the A2A protocol to communicate with the AI agent. The protocol includes:

### Request Format
```json
{
  "message": "User's message",
  "conversation_id": "teams-conversation-id",
  "protocol_version": "1.0"
}
```

### Headers
- `Content-Type: application/json`
- `Authorization: Bearer <agent-api-key>`
- `x-protocol: a2a`

### Response Format
```json
{
  "response": "Agent's response",
  "conversation_id": "teams-conversation-id",
  "metadata": {}
}
```

## Code Structure

- `app.py` - Main application file
  - `A2AClient` - Handles A2A protocol communication
  - `TeamsBot` - Bot logic and message handling
  - `messages()` - Webhook endpoint for Teams
  - `health_check()` - Health check endpoint

## Troubleshooting

### Bot doesn't respond
- Check that your A2A agent endpoint is accessible
- Verify your API keys are correct
- Check the console logs for errors

### Authentication errors
- Ensure your Microsoft App ID and Password are correct
- Verify the bot registration in Azure Portal

### Connection timeout
- Check if your agent endpoint is responding
- Verify network connectivity
- Consider increasing timeout values if needed

## Next Steps

- Implement conversation history
- Add support for rich cards and adaptive cards
- Implement authentication for secure agent access
- Add telemetry and logging
- Support for proactive messages

## Resources

- [Bot Framework Documentation](https://docs.microsoft.com/en-us/azure/bot-service/)
- [Teams Bot Development](https://docs.microsoft.com/en-us/microsoftteams/platform/bots/what-are-bots)
- [A2A Protocol Specification](https://github.com/microsoft/agents)

## License

MIT License - See LICENSE file for details
