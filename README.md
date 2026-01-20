# A2A Protocol Use Cases - Sample Repository

Collection of samples that demonstrate how to communicate with AI agents using the A2A (Agent-to-Agent) protocol in Microsoft platform (Microsoft Foundry, Copilot Studio, and Microsoft Teams).

## 📚 Samples Overview

This repository contains three comprehensive samples showcasing different use cases for the A2A protocol:

### [Sample 1: Microsoft Teams App with A2A Protocol](./sample-1-teams-a2a-app/)

A Microsoft Teams bot that communicates with an AI agent using the A2A protocol. Users can chat with the bot in Teams, and their messages are forwarded to an AI agent via A2A protocol.

**Key Features:**
- ✅ Microsoft Teams integration using Bot Framework SDK
- ✅ A2A protocol communication with AI agents
- ✅ Asynchronous message handling
- ✅ Conversation context tracking
- ✅ Welcome messages and typing indicators

**Tech Stack:** Python, Bot Framework SDK, aiohttp

[📖 View Full Documentation](./sample-1-teams-a2a-app/README.md)

---

### [Sample 2: Custom Engine Agent with M365 Agents SDK](./sample-2-custom-engine-agent/)

A custom engine agent that uses the Microsoft 365 Agents SDK and communicates with other agents through the A2A protocol. This agent can process requests locally or delegate to specialized agents.

**Key Features:**
- ✅ Custom agent implementation with M365 Agents SDK patterns
- ✅ A2A protocol integration for agent delegation
- ✅ Conversation context management
- ✅ Fallback to local processing
- ✅ RESTful API endpoints

**Tech Stack:** Python, M365 Agents SDK, aiohttp, Docker

[📖 View Full Documentation](./sample-2-custom-engine-agent/README.md)

---

### [Sample 3: Bank Alerts Workflow with Agent Framework](./sample-3-bank-alerts-workflow/)

A Microsoft Agent Framework workflow that coordinates two agents: one reads suspicious bank movement alerts from Cosmos DB, and the other sends notifications via WhatsApp through Azure Communication Services.

**Key Features:**
- ✅ Multi-agent workflow coordination
- ✅ Azure Cosmos DB integration for alert storage
- ✅ WhatsApp notifications via Azure Communication Services
- ✅ Risk score-based filtering and prioritization
- ✅ Batch processing and continuous monitoring

**Tech Stack:** Python, Azure Cosmos DB, Azure Communication Services, aiohttp

[📖 View Full Documentation](./sample-3-bank-alerts-workflow/README.md)

---

## 🚀 Getting Started

Each sample is self-contained in its own directory with:
- Complete source code
- `README.md` with detailed setup instructions
- `requirements.txt` for Python dependencies
- `.env.example` for environment configuration
- Deployment guides for Azure

### Prerequisites

- Python 3.8 or higher
- Azure subscription (for Samples 2 and 3)
- Microsoft 365 account (for Sample 1)

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LuisARB/a2a-usecases-samples.git
   cd a2a-usecases-samples
   ```

2. **Choose a sample and navigate to its directory:**
   ```bash
   cd sample-1-teams-a2a-app  # or sample-2-custom-engine-agent or sample-3-bank-alerts-workflow
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the sample:**
   ```bash
   python app.py  # or agent.py or workflow.py depending on the sample
   ```

## 📖 A2A Protocol Overview

The Agent-to-Agent (A2A) protocol enables seamless communication between AI agents in the Microsoft ecosystem. Key features include:

- **Standardized Communication**: Common message format for interoperability
- **Context Preservation**: Maintain conversation context across agent interactions
- **Error Handling**: Built-in error handling and fallback mechanisms
- **Scalability**: Support for complex multi-agent workflows

### Basic A2A Request Format

```json
{
  "message": "User's message or task",
  "conversation_id": "unique-conversation-id",
  "context": {
    "additional": "metadata"
  },
  "protocol_version": "1.0"
}
```

### Basic A2A Response Format

```json
{
  "response": "Agent's response",
  "conversation_id": "unique-conversation-id",
  "metadata": {
    "source": "agent-id",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## 🏗️ Architecture Patterns

### Pattern 1: User Interface → Agent (Sample 1)
```
User (Teams) → Bot → [A2A] → AI Agent → Response
```

### Pattern 2: Agent → Agent Delegation (Sample 2)
```
Client → Custom Agent → [A2A] → Specialized Agent → Response
```

### Pattern 3: Multi-Agent Workflow (Sample 3)
```
Workflow Orchestrator → Agent 1 (Data Reader) → Agent 2 (Notifier)
```

## 🔐 Security Considerations

- Store credentials securely using Azure Key Vault
- Use managed identities for Azure resources
- Enable encryption at rest and in transit
- Implement proper authentication and authorization
- Regularly rotate access keys
- Follow principle of least privilege

## 📦 Deployment Options

All samples can be deployed to:
- **Azure App Service**: For web applications and APIs
- **Azure Container Apps**: For containerized workloads
- **Azure Container Instances**: For simple container deployments
- **Azure Functions**: For event-driven scenarios
- **Azure Kubernetes Service**: For production-scale deployments

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

- [Microsoft Agent Framework Documentation](https://github.com/microsoft/agents)
- [A2A Protocol Specification](https://github.com/microsoft/agents)
- [Bot Framework Documentation](https://docs.microsoft.com/en-us/azure/bot-service/)
- [Azure Cosmos DB Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/)
- [Azure Communication Services Documentation](https://docs.microsoft.com/en-us/azure/communication-services/)
- [Microsoft 365 Agents SDK](https://learn.microsoft.com/en-us/microsoft-365/agents/)

## 💬 Support

For questions and support:
- Open an issue in this repository
- Check the individual sample README files for specific guidance
- Refer to official Microsoft documentation

## 🎯 Sample Use Cases

- **Customer Service**: Teams bot forwarding queries to specialized AI agents
- **Financial Services**: Monitoring and alerting on suspicious transactions
- **Enterprise Automation**: Multi-agent workflows for complex business processes
- **DevOps**: Intelligent incident response and remediation
- **Healthcare**: Patient monitoring and notification systems
