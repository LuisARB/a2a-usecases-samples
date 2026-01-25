using Microsoft.Extensions.AI;

/// <summary>
/// A chat client wrapper that logs all interactions for demo purposes
/// </summary>
public class LoggingChatClient : IChatClient
{
    private readonly IChatClient _innerClient;
    private readonly Action<string> _log;

    public LoggingChatClient(IChatClient innerClient)
    {
        _innerClient = innerClient;
        _log = message => Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] 🤖 {message}");
    }

    public async Task<ChatResponse> GetResponseAsync(
        IEnumerable<ChatMessage> chatMessages,
        ChatOptions? options = null,
        CancellationToken cancellationToken = default)
    {
        var messagesList = chatMessages.ToList();
        
        _log("═══════════════════════════════════════════════════════════");
        _log("🧠 LLM REQUEST");
        _log($"   Messages count: {messagesList.Count}");
        
        foreach (var msg in messagesList)
        {
            var content = msg.Text?.Length > 200 ? msg.Text[..200] + "..." : msg.Text;
            _log($"   [{msg.Role}]: {content}");
        }
        
        var result = await _innerClient.GetResponseAsync(messagesList, options, cancellationToken);
        
        _log("───────────────────────────────────────────────────────────");
        _log("📤 LLM RESPONSE");
        var responseText = result.Text?.Length > 500 
            ? result.Text[..500] + "..." 
            : result.Text;
        _log($"   Response: {responseText}");
        _log($"   Finish Reason: {result.FinishReason}");
        _log("═══════════════════════════════════════════════════════════");
        
        return result;
    }

    public async IAsyncEnumerable<ChatResponseUpdate> GetStreamingResponseAsync(
        IEnumerable<ChatMessage> chatMessages,
        ChatOptions? options = null,
        [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        var messagesList = chatMessages.ToList();
        
        _log("═══════════════════════════════════════════════════════════");
        _log("🧠 LLM STREAMING REQUEST");
        _log($"   Messages count: {messagesList.Count}");
        
        foreach (var msg in messagesList)
        {
            var content = msg.Text?.Length > 200 ? msg.Text[..200] + "..." : msg.Text;
            _log($"   [{msg.Role}]: {content}");
        }
        
        _log("📤 LLM STREAMING RESPONSE:");
        
        await foreach (var update in _innerClient.GetStreamingResponseAsync(messagesList, options, cancellationToken))
        {
            if (!string.IsNullOrEmpty(update.Text))
            {
                Console.Write(update.Text);
            }
            yield return update;
        }
        
        Console.WriteLine();
        _log("═══════════════════════════════════════════════════════════");
    }

    public object? GetService(Type serviceType, object? key = null)
        => _innerClient.GetService(serviceType, key);

    public void Dispose() => _innerClient.Dispose();
}

