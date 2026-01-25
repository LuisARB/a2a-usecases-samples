# Dockerfile for A2A Agents Workflow
# This application orchestrates AI agents via the A2A protocol using Microsoft Agent Framework

FROM python:3.11-slim

WORKDIR /app

# Copy and install requirements first for better caching
COPY a2a-agents-workflow/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY a2a-agents-workflow/src user_agent/

WORKDIR /app/user_agent

EXPOSE 8088

#ENV AZURE_AI_PROJECT_ENDPOINT="https://tc2026aiz6ek.services.ai.azure.com/api/projects/techconnect2026"
#ENV AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1"

# A2A Agent URLs (Azure Container Apps)
#ENV NINJA_AGENT_URL="https://ninjaagent.wonderfuldesert-c30b6b4e.northcentralus.azurecontainerapps.io/a2a/ninja"
#ENV PIRATE_AGENT_URL="https://pirateagent.wonderfuldesert-c30b6b4e.northcentralus.azurecontainerapps.io/a2a/pirate"

# Set default ASP.NET Core environment variables
ENV ASPNETCORE_URLS=http://+:8088
ENV ASPNETCORE_ENVIRONMENT=Production

CMD ["python", "main.py"]


