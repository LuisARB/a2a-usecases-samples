"""
A2A Client - Reusable client for communicating with A2A agents.
Uses the A2A SDK for protocol-compliant communication.
"""

import uuid
from typing import cast

from httpx import AsyncClient

from a2a.client import Client, ClientFactory
from a2a.client.card_resolver import A2ACardResolver
from a2a.client.client import ClientConfig
from a2a.types import AgentCard, Message, Part, Role, TextPart


class A2AAgentClient:
    """
    Client for communicating with A2A agents.
    Handles agent card resolution.
    """

    def __init__(self, base_url: str, card_url: str = "v1/card"):
        """
        Initialize the A2A client.
        
        Args:
            base_url: Base URL of the A2A agent (e.g., http://localhost:5066/a2a/pirate)
            card_url: Relative path to the agent card endpoint
        """
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
            context_id: Optional context/conversation ID for multi-turn conversations

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
    
    @property
    def agent_name(self) -> str:
        """Get the agent name from the card."""
        if self._agent_card:
            return self._agent_card.name
        return "Unknown Agent"
