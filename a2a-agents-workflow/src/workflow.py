"""
Sequential Workflow with A2A Agents

This module defines a sequential workflow using Microsoft Agent Framework
that orchestrates two agents via the A2A protocol:
1. NinjaAgent - Speaks with mysterious and philosophical ninja wisdom
2. PirateAgent - Speaks like a pirate

The workflow pattern:
User Input -> NinjaExecutor -> PirateExecutor -> Final Output
"""

from dataclasses import dataclass
from typing_extensions import Never

from agent_framework import (
    ChatMessage,
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    WorkflowOutputEvent,
    WorkflowStatusEvent,
    WorkflowRunState,
    ExecutorFailedEvent,
    WorkflowFailedEvent,
    handler
)

from a2a_client import A2AAgentClient


@dataclass
class WorkflowMessage:
    """Message passed between executors in the workflow."""
    original_input: str
    ninja_response: str | None = None
    pirate_response: str | None = None


@dataclass
class WorkflowResult:
    """Final result of the workflow containing both agent responses."""
    original_input: str
    ninja_response: str
    pirate_response: str


class NinjaExecutor(Executor):
    """
    First executor in the workflow.
    Sends the user's message to the NinjaAgent via A2A protocol
    and forwards the response to the next executor.
    """

    def __init__(self, ninja_agent_url: str, id: str = "ninja_executor"):
        self.a2a_client = A2AAgentClient(base_url=ninja_agent_url)
        super().__init__(id=id)

    @handler
    async def handle_input(self, messages: list[ChatMessage], ctx: WorkflowContext[WorkflowMessage]) -> None:
        """
        Receive user input, send to NinjaAgent, and forward to next executor.
        
        Args:
            messages: The list of chat messages from the user
            ctx: Workflow context for sending messages downstream
        """
        # Extract the user message content from the last message
        user_input = messages[-1].text if messages else ""
        
        print(f"\n🥷 NinjaExecutor: Sending message to NinjaAgent via A2A...")
        print(f"   Input: {user_input}")
        
        try:
            # Send message to NinjaAgent via A2A protocol
            ninja_response = await self.a2a_client.send_message(user_input)
            print(f"\n🥷 NinjaAgent responded:")
            print(f"   {ninja_response}")
            
            # Create message for next executor
            message = WorkflowMessage(
                original_input=user_input,
                ninja_response=ninja_response
            )
            
            # Forward to PirateExecutor
            await ctx.send_message(message)
            
        except Exception as e:
            print(f"\n❌ Error communicating with NinjaAgent: {e}")
            # Forward with error message
            message = WorkflowMessage(
                original_input=user_input,
                ninja_response=f"[Error: {str(e)}]"
            )
            await ctx.send_message(message)


class PirateExecutor(Executor):
    """
    Second executor in the workflow.
    Receives the ninja's response and sends it to PirateAgent via A2A protocol.
    This is the terminal node that yields the final workflow output.
    """

    def __init__(self, pirate_agent_url: str, id: str = "pirate_executor"):
        self.a2a_client = A2AAgentClient(base_url=pirate_agent_url)
        super().__init__(id=id)

    @handler
    async def handle_ninja_response(
        self, message: WorkflowMessage, ctx: WorkflowContext[Never, WorkflowResult]
    ) -> None:
        """
        Receive ninja's response, send to PirateAgent, and yield final output.
        
        The pirate will respond to/translate the ninja's philosophical message
        in pirate style.
        
        Args:
            message: WorkflowMessage containing the ninja's response
            ctx: Workflow context for yielding final output
        """
        print(f"\n🏴‍☠️ PirateExecutor: Sending ninja's wisdom to PirateAgent via A2A...")
        
        # Create a prompt that includes the ninja's response
        pirate_prompt = (
            f"El ninja sabio dijo: '{message.ninja_response}'. "
            f"¿Qué opinas de esta sabiduría? Responde como un pirata auténtico."
        )
        print(f"   Prompt: {pirate_prompt}")
        
        try:
            # Send to PirateAgent via A2A protocol
            pirate_response = await self.a2a_client.send_message(pirate_prompt)
            print(f"\n🏴‍☠️ PirateAgent responded:")
            print(f"   {pirate_response}")
            
            # Create final result
            result = WorkflowResult(
                original_input=message.original_input,
                ninja_response=message.ninja_response or "",
                pirate_response=pirate_response
            )
            
            # Yield final output - workflow will complete
            await ctx.yield_output(result)
            
        except Exception as e:
            print(f"\n❌ Error communicating with PirateAgent: {e}")
            result = WorkflowResult(
                original_input=message.original_input,
                ninja_response=message.ninja_response or "",
                pirate_response=f"[Error: {str(e)}]"
            )
            await ctx.yield_output(result)


def build_a2a_workflow(ninja_url: str, pirate_url: str):
    """
    Build the sequential A2A workflow.
    
    The workflow connects: User Input -> NinjaExecutor -> PirateExecutor -> Output
    
    Args:
        ninja_url: Base URL for the NinjaAgent A2A endpoint
        pirate_url: Base URL for the PirateAgent A2A endpoint
        
    Returns:
        A configured Workflow ready to execute
    """
    # Build workflow using fluent API
    # Pattern: ninja -> pirate (sequential)
    workflow = (
        WorkflowBuilder()
        .register_executor(lambda: NinjaExecutor(ninja_agent_url=ninja_url), name="NinjaAgent")
        .register_executor(lambda: PirateExecutor(pirate_agent_url=pirate_url), name="PirateAgent")
        .set_start_executor("NinjaAgent")
        .add_edge("NinjaAgent", "PirateAgent")
        .build()
    )
    
    return workflow
