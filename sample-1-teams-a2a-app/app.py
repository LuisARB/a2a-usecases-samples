"""
Microsoft Teams App with A2A Protocol Integration
This bot demonstrates how a Teams app can communicate with an AI agent using the A2A protocol.
"""

import os
import asyncio
from typing import Any, Dict
from botbuilder.core import BotFrameworkAdapter, TurnContext, BotFrameworkAdapterSettings
from botbuilder.schema import Activity, ActivityTypes
from aiohttp import web
import aiohttp
import json

class A2AClient:
    """Client for communicating with agents using A2A protocol"""
    
    def __init__(self, agent_endpoint: str, agent_api_key: str):
        self.agent_endpoint = agent_endpoint
        self.agent_api_key = agent_api_key
    
    async def send_message(self, message: str, conversation_id: str = None) -> Dict[str, Any]:
        """
        Send a message to the agent using A2A protocol
        
        Args:
            message: The message to send to the agent
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dict containing the agent's response
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.agent_api_key}",
            "x-protocol": "a2a"
        }
        
        payload = {
            "message": message,
            "conversation_id": conversation_id,
            "protocol_version": "1.0"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.agent_endpoint}/invoke",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        return {
                            "error": f"Agent returned status {response.status}",
                            "details": error_text
                        }
            except Exception as e:
                return {
                    "error": "Failed to communicate with agent",
                    "details": str(e)
                }


class TeamsBot:
    """Teams bot that uses A2A protocol to communicate with an AI agent"""
    
    def __init__(self, a2a_client: A2AClient):
        self.a2a_client = a2a_client
        self.conversation_references: Dict[str, str] = {}
    
    async def on_message_activity(self, turn_context: TurnContext):
        """
        Handle incoming messages from Teams users
        
        Args:
            turn_context: The context for the current turn
        """
        user_message = turn_context.activity.text
        conversation_id = turn_context.activity.conversation.id
        
        # Store conversation reference
        self.conversation_references[conversation_id] = conversation_id
        
        # Send typing indicator
        await turn_context.send_activity(
            Activity(type=ActivityTypes.typing)
        )
        
        # Forward message to agent via A2A protocol
        agent_response = await self.a2a_client.send_message(
            message=user_message,
            conversation_id=conversation_id
        )
        
        # Process and send response back to user
        if "error" in agent_response:
            response_text = f"⚠️ Error: {agent_response['error']}"
        else:
            response_text = agent_response.get("response", "No response from agent")
        
        await turn_context.send_activity(response_text)
    
    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        """
        Handle new members added to the conversation
        
        Args:
            members_added: List of members that were added
            turn_context: The context for the current turn
        """
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                welcome_message = (
                    "👋 Welcome! I'm a Teams bot that uses A2A protocol to communicate "
                    "with an AI agent. Send me a message and I'll forward it to the agent!"
                )
                await turn_context.send_activity(welcome_message)


# Bot Framework Adapter
SETTINGS = BotFrameworkAdapterSettings(
    app_id=os.environ.get("MICROSOFT_APP_ID", ""),
    app_password=os.environ.get("MICROSOFT_APP_PASSWORD", "")
)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# A2A Client
A2A_CLIENT = A2AClient(
    agent_endpoint=os.environ.get("A2A_AGENT_ENDPOINT", "https://your-agent-endpoint.com"),
    agent_api_key=os.environ.get("A2A_AGENT_API_KEY", "")
)

# Bot instance
BOT = TeamsBot(A2A_CLIENT)


async def messages(req: web.Request) -> web.Response:
    """
    Main bot message handler endpoint
    
    Args:
        req: The incoming HTTP request
        
    Returns:
        HTTP response
    """
    # Main bot message handler
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return web.Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    async def aux_func(turn_context: TurnContext):
        if turn_context.activity.type == ActivityTypes.message:
            await BOT.on_message_activity(turn_context)
        elif turn_context.activity.type == ActivityTypes.conversation_update:
            await BOT.on_members_added_activity(
                turn_context.activity.members_added, turn_context
            )

    await ADAPTER.process_activity(activity, auth_header, aux_func)
    return web.Response(status=200)


async def health_check(req: web.Request) -> web.Response:
    """Health check endpoint"""
    return web.json_response({"status": "healthy", "service": "teams-a2a-bot"})


def main():
    """Main entry point for the application"""
    app = web.Application()
    app.router.add_post("/api/messages", messages)
    app.router.add_get("/health", health_check)
    
    port = int(os.environ.get("PORT", 3978))
    
    print(f"🚀 Teams A2A Bot is running on port {port}")
    print(f"📡 Bot endpoint: http://localhost:{port}/api/messages")
    
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
