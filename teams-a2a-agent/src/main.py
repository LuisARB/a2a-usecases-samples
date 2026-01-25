"""
Microsoft Teams App with A2A Protocol Integration
This bot demonstrates how a Teams app can communicate with an AI agent using the A2A protocol.
Uses microsoft-teams-a2a package utilities for A2A communication.
"""

import asyncio
import os
import re
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import uuid
from typing import cast

from httpx import AsyncClient

from a2a.client import Client, ClientFactory
from a2a.client.card_resolver import A2ACardResolver
from a2a.client.client import ClientConfig
from a2a.types import AgentCard, Message, Part, Role, TextPart

from microsoft_teams.api import (
    ConversationUpdateActivity,
    MessageActivity,
    TypingActivityInput,
)
from microsoft_teams.apps import ActivityContext, App
from microsoft_teams.devtools import DevToolsPlugin


class A2AAgentClient:
    """
    Client for communicating with A2A agents.
    Uses the same underlying libraries as microsoft-teams-a2a.
    """

    def __init__(self, base_url: str, card_url: str = "v1/card"):
        self.base_url = base_url
        self.card_url = card_url
        self._client: Client | None = None
        self._agent_card: AgentCard | None = None

    async def _fetch_agent_card(self) -> AgentCard:
        """Retrieve the agent card from the A2A server."""
        async with AsyncClient() as httpx_client:
            resolver = A2ACardResolver(httpx_client, self.base_url)
            card = await resolver.get_agent_card(self.card_url)
            return card

    async def _get_client(self) -> Client:
        """Get or create the A2A client."""
        if self._client is None:
            self._agent_card = await self._fetch_agent_card()
            client_config = ClientConfig()
            self._client = ClientFactory(client_config).create(card=self._agent_card)
        return self._client

    async def send_message(self, text: str, context_id: str | None = None) -> str:
        """
        Send a message to the A2A agent and return the response.

        Args:
            text: The message text to send
            context_id: Optional context/conversation ID

        Returns:
            The agent's response as a string
        """
        client = await self._get_client()

        # Create A2A message
        message = Message(
            message_id=str(uuid.uuid4()),
            role=Role("user"),
            parts=[Part(root=TextPart(kind="text", text=text))],
            context_id=context_id,
        )

        # Send message and collect response
        last_message: Message | None = None
        async for event in client.send_message(message):
            # Unwrap tuple from transport implementations
            if isinstance(event, tuple):
                event = event[0]
            if isinstance(event, Message):
                last_message = event

        if last_message is None:
            return "No response from agent"

        # Extract text from response message parts
        text_parts: list[str] = []
        for part in last_message.parts:
            if getattr(part.root, "kind", None) == "text":
                text_part = cast(TextPart, part.root)
                text_parts.append(text_part.text)

        return " ".join(text_parts) if text_parts else "Agent responded with no text content."

    @property
    def agent_card(self) -> AgentCard | None:
        """Get the agent card if already fetched."""
        return self._agent_card


# A2A Agent configuration
A2A_AGENT_BASE_URL = os.environ.get("A2A_AGENT_BASE_URL", "http://localhost:5066/a2a/pirate")
A2A_AGENT_CARD_URL = os.environ.get("A2A_AGENT_CARD_URL", "v1/card")

# Initialize A2A Client
a2a_client = A2AAgentClient(
    base_url=A2A_AGENT_BASE_URL,
    card_url=A2A_AGENT_CARD_URL,
)

# Initialize Teams App
app = App(plugins=[DevToolsPlugin()])


@app.on_message_pattern(re.compile(r"^(hello|hi|greetings|hola)$", re.IGNORECASE))
async def handle_greeting(ctx: ActivityContext[MessageActivity]) -> None:
    """Handle greeting messages."""
    await ctx.send("👋 Hola! Estoy conectado a un agente de IA a través del protocolo A2A. ¿Cómo puedo ayudarte hoy?")


@app.on_conversation_update
async def handle_conversation_update(ctx: ActivityContext[ConversationUpdateActivity]) -> None:
    """Handle new members added to the conversation."""
    if ctx.activity.members_added:
        for member in ctx.activity.members_added:
            # Don't greet the bot itself
            if member.id != ctx.activity.recipient.id:
                welcome_message = (
                    "👋 ¡Bienvenido! Soy un bot de Teams que utiliza el protocolo A2A para comunicarse "
                    "con un agente de IA. ¡Envíame un mensaje y lo reenviaré al agente!"
                )
                await ctx.send(welcome_message)


@app.on_message
async def handle_message(ctx: ActivityContext[MessageActivity]) -> None:
    """
    Handle message activities by forwarding to A2A agent.
    This handler processes all messages not caught by specific patterns.
    """
    # Send typing indicator while processing
    await ctx.reply(TypingActivityInput())

    user_message = ctx.activity.text
    conversation_id = ctx.activity.conversation.id

    # Forward message to agent via A2A protocol
    try:
        response_text = await a2a_client.send_message(
            text=user_message,
            context_id=conversation_id,
        )
        await ctx.send(response_text)
    except Exception as e:
        await ctx.send(f"⚠️ Error communicating with agent: {str(e)}")


def main() -> None:
    """Main entry point for the application."""
    print("🚀 Teams A2A Bot is starting...")
    print(f"📡 A2A Agent Base URL: {A2A_AGENT_BASE_URL}")
    print(f"📄 A2A Agent Card URL: {A2A_AGENT_CARD_URL}")
    asyncio.run(app.start())


if __name__ == "__main__":
    main()
