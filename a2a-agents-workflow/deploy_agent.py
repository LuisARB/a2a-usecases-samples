#!/usr/bin/env python3
"""
Deploy A2A Workflow Hosted Agent to Microsoft Foundry

Required environment variables:
  PROJECT_ENDPOINT              - Azure AI Project endpoint
  AGENT_NAME                    - Name of the agent to create/update
  CONTAINER_IMAGE               - Container image URL from ACR
  NINJA_AGENT_URL               - URL of the Ninja A2A agent
  PIRATE_AGENT_URL              - URL of the Pirate A2A agent
  AZURE_AI_PROJECT_ENDPOINT     - Azure AI Project endpoint for the workflow
  AZURE_AI_MODEL_DEPLOYMENT_NAME - Model deployment name (e.g., gpt-4.1)

Optional environment variables:
  APPLICATIONINSIGHTS_CONNECTION_STRING - Application Insights connection string for logging
"""
import os
import sys
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ImageBasedHostedAgentDefinition, ProtocolVersionRecord, AgentProtocol
from azure.identity import DefaultAzureCredential


def get_required_env(name: str) -> str:
    """Get a required environment variable or exit with error."""
    value = os.getenv(name)
    if not value:
        print(f"❌ Error: Required environment variable '{name}' is not set.")
        sys.exit(1)
    return value


def main():
    # Required configuration from environment variables
    PROJECT_ENDPOINT = get_required_env("PROJECT_ENDPOINT")
    AGENT_NAME = get_required_env("AGENT_NAME")
    CONTAINER_IMAGE = get_required_env("CONTAINER_IMAGE")
    NINJA_AGENT_URL = get_required_env("NINJA_AGENT_URL")
    PIRATE_AGENT_URL = get_required_env("PIRATE_AGENT_URL")
    AZURE_AI_PROJECT_ENDPOINT = get_required_env("AZURE_AI_PROJECT_ENDPOINT")
    AZURE_AI_MODEL_DEPLOYMENT_NAME = get_required_env("AZURE_AI_MODEL_DEPLOYMENT_NAME")
    
    # Optional configuration
    APPINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    print("🚀 Deploying A2A Workflow Agent to Azure Foundry...")
    print(f"   Project: {PROJECT_ENDPOINT}")
    print(f"   Agent Name: {AGENT_NAME}")
    print(f"   Container Image: {CONTAINER_IMAGE}")
    print()
    print("📡 Agent Configuration:")
    print(f"   Ninja Agent URL: {NINJA_AGENT_URL}")
    print(f"   Pirate Agent URL: {PIRATE_AGENT_URL}")
    print(f"   Model Deployment: {AZURE_AI_MODEL_DEPLOYMENT_NAME}")

    if APPINSIGHTS_CONNECTION_STRING:
        print(f"   Application Insights: Enabled")
    else:
        print(f"   Application Insights: Disabled (set APPLICATIONINSIGHTS_CONNECTION_STRING to enable)")
    print()

    # Initialize the client
    print("🔐 Authenticating with Azure...")
    client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential()
    )


    # Create the agent from container image
    print("📦 Creating hosted agent version...")
    agent = client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=ImageBasedHostedAgentDefinition(
            container_protocol_versions=[
                ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="v1")
            ],
            cpu="3.5",
            memory="7Gi",
            image=CONTAINER_IMAGE,
            
            environment_variables={
                "OLLAMA_BASE_URL": "http://localhost:11434/v1/",
                
                 "APPLICATIONINSIGHTS_CONNECTION_STRING": APPINSIGHTS_CONNECTION_STRING,
                 "NINJA_AGENT_URL": NINJA_AGENT_URL,
                 "PIRATE_AGENT_URL": PIRATE_AGENT_URL,
                 "AZURE_AI_PROJECT_ENDPOINT": AZURE_AI_PROJECT_ENDPOINT,
                 "AZURE_AI_MODEL_DEPLOYMENT_NAME": AZURE_AI_MODEL_DEPLOYMENT_NAME,
            }
        )
    )

    print()
    print("✅ Agent version created successfully!")
    print(f"   Agent ID: {agent.id}")
    print(f"   Agent Name: {agent.name}")
    print(f"   Agent Version: {agent.version}")
    print()


if __name__ == "__main__":
    main()
