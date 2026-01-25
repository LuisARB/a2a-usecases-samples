"""
Microsoft Teams App with A2A Protocol using ChatPrompt and A2AClientPlugin

This bot demonstrates how to use the A2AClientPlugin with ChatPrompt to communicate
with an AI agent using the A2A protocol. This approach integrates the A2A agent
as a plugin within the ChatPrompt pipeline.
"""

import os
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from microsoft_teams.api import (
    ConversationUpdateActivity,
    MessageActivity,
    TypingActivityInput,
)
from microsoft_teams.apps import ActivityContext, App
from microsoft_teams.devtools import DevToolsPlugin
from microsoft_teams.ai import ChatPrompt
from microsoft_teams.ai.memory import Memory
from microsoft_teams.a2a import A2AClientPlugin, A2APluginUseParams
from microsoft_teams.openai.completions_model import OpenAICompletionsAIModel


# Configuration
A2A_AGENT_BASE_URL = os.environ.get("A2A_AGENT_BASE_URL", "http://localhost:5066/a2a/pirate")
A2A_AGENT_CARD_URL = os.environ.get("A2A_AGENT_CARD_URL", "v1/card")
AZURE_OPENAI_MODEL = os.environ.get("AZURE_OPENAI_MODEL", os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"))


def create_chat_prompt() -> ChatPrompt:
    """
    Create a ChatPrompt with the A2AClientPlugin configured.
    This integrates the A2A agent as a plugin that can be used during chat.
    """
    # Create the Azure OpenAI model (uses AZURE_OPENAI_* env vars automatically)
    model = OpenAICompletionsAIModel(model=AZURE_OPENAI_MODEL)
    
    # Create the A2A client plugin
    a2a_client = A2AClientPlugin()
    
    # Configure the plugin to connect to our pirate agent
    a2a_client.on_use_plugin(
        A2APluginUseParams(
            key="PirateAgent",
            base_url=A2A_AGENT_BASE_URL,
            card_url=A2A_AGENT_CARD_URL
        )
    )
    
    # Create the ChatPrompt with the A2A plugin
    prompt = ChatPrompt(
        model=model,
        plugins=[a2a_client],
    )
    
    return prompt


# Initialize the ChatPrompt
chat_prompt = create_chat_prompt()

# Initialize Teams App
app = App(plugins=[DevToolsPlugin()])



@app.on_conversation_update
async def handle_conversation_update(ctx: ActivityContext[ConversationUpdateActivity]) -> None:
    """Handle new members added to the conversation."""
    if ctx.activity.members_added:
        for member in ctx.activity.members_added:
            if member.id != ctx.activity.recipient.id:
                welcome_message = (
                    "👋 ¡Bienvenido! Soy un bot de Teams que usa ChatPrompt con A2AClientPlugin.\n\n"
                    "Puedo comunicarme con un agente pirata a través del protocolo A2A.\n"
                    "¡Pregúntame algo y usaré el agente pirata para responder!"
                )
                await ctx.send(welcome_message)


@app.on_message
async def handle_message(ctx: ActivityContext[MessageActivity]) -> None:
    """
    Handle message activities using ChatPrompt with A2AClientPlugin.
    """
    # Send typing indicator
    await ctx.reply(TypingActivityInput())

    user_message = ctx.activity.text
    conversation_id = ctx.activity.conversation.id

    try:
        # Use ChatPrompt to process the message
        # The A2AClientPlugin will automatically route to the pirate agent when needed
        print(f"📨 Processing message with ChatPrompt: {user_message}")
        
        # Use the send method with the user message and memory
        result = await chat_prompt.send(user_message)

        response_text = result.response.content if result.response and result.response.content else "No response received"
        
        print(f"📤 Response from ChatPrompt: {response_text}")
        await ctx.send(response_text)
        
    except Exception as e:
        error_message = f"⚠️ Error processing message: {str(e)}"
        print(f"❌ {error_message}")
        await ctx.send(error_message)


def main() -> None:
    """Main entry point for the application."""
    print("🚀 Teams A2A Bot (ChatPrompt mode) is starting...")
    print(f"📡 A2A Agent Base URL: {A2A_AGENT_BASE_URL}")
    print(f"📄 A2A Agent Card URL: {A2A_AGENT_CARD_URL}")
    print(f"🧠 Using Azure OpenAI model: {AZURE_OPENAI_MODEL}")
    
    import asyncio
    asyncio.run(app.start())


if __name__ == "__main__":
    main()
