"""
Custom Engine Agent with Microsoft 365 Agents SDK
This agent demonstrates how to create a custom agent that uses A2A protocol
to communicate with other agents.
"""

import os
import asyncio
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import aiohttp
import json
from aiohttp import web
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """Represents a message in the agent conversation"""
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class A2AProtocolClient:
    """Client for communicating with other agents using A2A protocol"""
    
    def __init__(self, target_agent_endpoint: str, target_agent_api_key: str):
        self.target_agent_endpoint = target_agent_endpoint
        self.target_agent_api_key = target_agent_api_key
    
    async def invoke_agent(
        self, 
        message: str, 
        conversation_id: str = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Invoke another agent using A2A protocol
        
        Args:
            message: The message to send to the target agent
            conversation_id: Optional conversation ID for context
            context: Optional additional context
            
        Returns:
            Dict containing the agent's response
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.target_agent_api_key}",
            "x-protocol": "a2a",
            "x-protocol-version": "1.0"
        }
        
        payload = {
            "message": message,
            "conversation_id": conversation_id or "",
            "context": context or {},
            "timestamp": time.time()
        }
        
        logger.info(f"Invoking target agent: {self.target_agent_endpoint}")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.target_agent_endpoint}/invoke",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info("Successfully received response from target agent")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Target agent error: {response.status} - {error_text}")
                        return {
                            "error": f"Target agent returned status {response.status}",
                            "details": error_text
                        }
            except asyncio.TimeoutError:
                logger.error("Request to target agent timed out")
                return {
                    "error": "Request timeout",
                    "details": "Target agent did not respond in time"
                }
            except Exception as e:
                logger.error(f"Failed to communicate with target agent: {str(e)}")
                return {
                    "error": "Communication failed",
                    "details": str(e)
                }


class CustomEngineAgent:
    """
    Custom Engine Agent using Microsoft 365 Agents SDK
    This agent can process requests and delegate to other agents via A2A protocol
    """
    
    def __init__(
        self, 
        agent_id: str,
        agent_name: str,
        a2a_client: Optional[A2AProtocolClient] = None
    ):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.a2a_client = a2a_client
        self.conversation_history: Dict[str, List[AgentMessage]] = {}
        
    async def process_message(
        self, 
        message: str, 
        conversation_id: str,
        use_delegation: bool = True
    ) -> Dict[str, Any]:
        """
        Process an incoming message
        
        Args:
            message: The user's message
            conversation_id: The conversation ID
            use_delegation: Whether to delegate to another agent via A2A
            
        Returns:
            Dict containing the response
        """
        logger.info(f"Processing message in conversation {conversation_id}")
        
        # Store the user message
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        self.conversation_history[conversation_id].append(
            AgentMessage(role="user", content=message)
        )
        
        # Determine if we should delegate to another agent
        if use_delegation and self.a2a_client:
            logger.info("Delegating to target agent via A2A protocol")
            
            # Prepare context from conversation history
            context = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "history_length": len(self.conversation_history[conversation_id])
            }
            
            # Delegate to target agent
            agent_response = await self.a2a_client.invoke_agent(
                message=message,
                conversation_id=conversation_id,
                context=context
            )
            
            if "error" in agent_response:
                response_text = self._handle_local_processing(message)
                metadata = {
                    "source": "local",
                    "delegation_failed": True,
                    "error": agent_response["error"]
                }
            else:
                response_text = agent_response.get("response", "No response from target agent")
                metadata = {
                    "source": "delegated",
                    "target_agent": "a2a_agent"
                }
        else:
            # Process locally
            logger.info("Processing message locally")
            response_text = self._handle_local_processing(message)
            metadata = {
                "source": "local"
            }
        
        # Store the agent response
        self.conversation_history[conversation_id].append(
            AgentMessage(role="assistant", content=response_text, metadata=metadata)
        )
        
        return {
            "response": response_text,
            "conversation_id": conversation_id,
            "metadata": metadata
        }
    
    def _handle_local_processing(self, message: str) -> str:
        """
        Handle message processing locally (fallback when delegation is not available)
        
        Args:
            message: The user's message
            
        Returns:
            The response text
        """
        # Simple local processing logic
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower:
            return f"Hello! I'm {self.agent_name}, a custom engine agent. How can I help you?"
        elif "help" in message_lower:
            return (
                f"I'm {self.agent_name} and I can:\n"
                "• Process your requests\n"
                "• Delegate to specialized agents via A2A protocol\n"
                "• Maintain conversation context\n"
                "Ask me anything!"
            )
        elif "status" in message_lower:
            return f"Agent {self.agent_name} is running and ready to help!"
        else:
            return (
                f"I received your message: '{message}'. "
                "I can delegate this to a specialized agent or provide a general response."
            )
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities
        
        Returns:
            Dict containing agent capabilities
        """
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "capabilities": [
                "message_processing",
                "conversation_context",
                "a2a_delegation"
            ],
            "protocol_version": "1.0",
            "has_delegation": self.a2a_client is not None
        }


# Initialize A2A client if target agent is configured
TARGET_AGENT_ENDPOINT = os.environ.get("TARGET_AGENT_ENDPOINT")
TARGET_AGENT_API_KEY = os.environ.get("TARGET_AGENT_API_KEY")

a2a_client = None
if TARGET_AGENT_ENDPOINT and TARGET_AGENT_API_KEY:
    a2a_client = A2AProtocolClient(
        target_agent_endpoint=TARGET_AGENT_ENDPOINT,
        target_agent_api_key=TARGET_AGENT_API_KEY
    )
    logger.info(f"A2A client configured for: {TARGET_AGENT_ENDPOINT}")
else:
    logger.warning("No target agent configured, running in local mode only")

# Initialize the custom engine agent
AGENT = CustomEngineAgent(
    agent_id=os.environ.get("AGENT_ID", "custom-engine-agent-001"),
    agent_name=os.environ.get("AGENT_NAME", "Custom Engine Agent"),
    a2a_client=a2a_client
)


async def invoke_handler(request: web.Request) -> web.Response:
    """
    Handle incoming agent invocation requests
    
    Args:
        request: The HTTP request
        
    Returns:
        HTTP response with agent output
    """
    try:
        # Parse request
        data = await request.json()
        message = data.get("message", "")
        conversation_id = data.get("conversation_id", "default")
        
        if not message:
            return web.json_response(
                {"error": "Message is required"},
                status=400
            )
        
        # Process the message
        response = await AGENT.process_message(
            message=message,
            conversation_id=conversation_id,
            use_delegation=True
        )
        
        return web.json_response(response, status=200)
        
    except json.JSONDecodeError:
        return web.json_response(
            {"error": "Invalid JSON"},
            status=400
        )
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return web.json_response(
            {"error": "Internal server error", "details": str(e)},
            status=500
        )


async def capabilities_handler(request: web.Request) -> web.Response:
    """
    Handle agent capabilities requests
    
    Args:
        request: The HTTP request
        
    Returns:
        HTTP response with agent capabilities
    """
    capabilities = await AGENT.get_capabilities()
    return web.json_response(capabilities, status=200)


async def health_handler(request: web.Request) -> web.Response:
    """Health check endpoint"""
    return web.json_response(
        {
            "status": "healthy",
            "service": "custom-engine-agent",
            "agent_id": AGENT.agent_id
        },
        status=200
    )


def create_app() -> web.Application:
    """Create and configure the web application"""
    app = web.Application()
    
    # Add routes
    app.router.add_post("/invoke", invoke_handler)
    app.router.add_get("/capabilities", capabilities_handler)
    app.router.add_get("/health", health_handler)
    
    return app


def main():
    """Main entry point"""
    app = create_app()
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"🚀 Custom Engine Agent starting on port {port}")
    logger.info(f"📡 Agent ID: {AGENT.agent_id}")
    logger.info(f"📝 Agent Name: {AGENT.agent_name}")
    logger.info(f"🔗 A2A Delegation: {'Enabled' if a2a_client else 'Disabled'}")
    
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
