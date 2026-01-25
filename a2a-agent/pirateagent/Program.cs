using System.ClientModel;
using A2A.AspNetCore;
using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.AspNetCore.HttpOverrides;
using Microsoft.Agents.AI.Hosting;
using Microsoft.Extensions.AI;

var builder = WebApplication.CreateBuilder(args);

// Configure forwarded headers for running behind a reverse proxy (like Azure Container Apps)
builder.Services.Configure<ForwardedHeadersOptions>(options =>
{
    options.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
    options.KnownNetworks.Clear();
    options.KnownProxies.Clear();
});

// Enable detailed logging for demo
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.SetMinimumLevel(LogLevel.Information);
builder.Logging.AddFilter("Microsoft.AspNetCore", LogLevel.Warning);
builder.Logging.AddFilter("A2A", LogLevel.Debug);
builder.Logging.AddFilter("Microsoft.Agents", LogLevel.Debug);

string endpoint = builder.Configuration["AZURE_OPENAI_ENDPOINT"]
    ?? throw new InvalidOperationException("AZURE_OPENAI_ENDPOINT is not set.");
string deploymentName = builder.Configuration["AZURE_OPENAI_DEPLOYMENT_NAME"]
    ?? throw new InvalidOperationException("AZURE_OPENAI_DEPLOYMENT_NAME is not set.");
string apiKey = builder.Configuration["AZURE_OPENAI_API_KEY"]
    ?? throw new InvalidOperationException("AZURE_OPENAI_API_KEY is not set.");

// Register the chat client with logging wrapper
IChatClient innerChatClient = new AzureOpenAIClient(
        new Uri(endpoint),
        new ApiKeyCredential(apiKey))
    .GetChatClient(deploymentName)
    .AsIChatClient();

// Wrap with logging
IChatClient chatClient = new LoggingChatClient(innerChatClient);
builder.Services.AddSingleton(chatClient);

// Register an agent
var pirateAgent = builder.AddAIAgent("pirate", instructions: "Eres un pirata. Habla como un pirata.");

var app = builder.Build();

// Enable forwarded headers for HTTPS detection behind proxy
app.UseForwardedHeaders();

var logger = app.Services.GetRequiredService<ILoggerFactory>().CreateLogger("A2A-Demo");

// Add request logging middleware
app.Use(async (context, next) =>
{
    if (context.Request.Path.StartsWithSegments("/a2a"))
    {
        logger.LogInformation("═══════════════════════════════════════════════════════════");
        logger.LogInformation("📥 A2A REQUEST RECEIVED");
        logger.LogInformation("   Path: {Path}", context.Request.Path);
        logger.LogInformation("   Method: {Method}", context.Request.Method);
        logger.LogInformation("   Content-Type: {ContentType}", context.Request.ContentType);
        
        // Read and log request body
        context.Request.EnableBuffering();
        using var reader = new StreamReader(context.Request.Body, leaveOpen: true);
        var body = await reader.ReadToEndAsync();
        context.Request.Body.Position = 0;
        
        if (!string.IsNullOrEmpty(body) && body.Length < 2000)
        {
            logger.LogInformation("   📝 Request Body: {Body}", body);
        }
        logger.LogInformation("═══════════════════════════════════════════════════════════");
    }
    await next();
});

// Expose the agent via A2A protocol. You can also customize the agentCard
var pirateBaseUrl = builder.Configuration["AGENT_BASE_URL"] ?? "";
app.MapA2A(pirateAgent, path: "/a2a/pirate", agentCard: new()
{
    Name = "PirateAgent",
    Description = "An agent that speaks like a pirate.",
    Version = "1.0",
    Url = string.IsNullOrEmpty(pirateBaseUrl) ? null : $"{pirateBaseUrl}/a2a/pirate"
});

logger.LogInformation("🏴‍☠️ Pirate Agent started!");
logger.LogInformation("🔗 A2A endpoint: /a2a/pirate");
logger.LogInformation("📋 Agent Card: /a2a/pirate/v1/card");

app.Run();