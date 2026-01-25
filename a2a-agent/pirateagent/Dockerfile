# Dockerfile for PirateAgent
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Copy project file and restore
COPY pirateagent.csproj .
RUN dotnet restore

# Copy source and build
COPY . .
RUN dotnet publish -c Release -o /app/publish

# Runtime image
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app

COPY --from=build /app/publish .

# Expose port
EXPOSE 5066

# Environment variables (override at runtime)
ENV ASPNETCORE_URLS=http://+:5066
ENV ASPNETCORE_ENVIRONMENT=Production

# Agent base URL for agent card (set to public HTTPS URL)
ENV AGENT_BASE_URL=""

# Azure OpenAI configuration (set these at runtime)
ENV AZURE_OPENAI_ENDPOINT=""
ENV AZURE_OPENAI_DEPLOYMENT_NAME=""
ENV AZURE_OPENAI_API_KEY=""

ENTRYPOINT ["dotnet", "pirateagent.dll"]
