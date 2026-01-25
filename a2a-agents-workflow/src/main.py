"""
A2A Agents Workflow - Main Entry Point

This script runs a sequential workflow that orchestrates two AI agents
via the A2A (Agent-to-Agent) protocol using Microsoft Agent Framework.

Workflow:
1. User sends a message
2. NinjaAgent responds with philosophical wisdom via A2A
3. PirateAgent responds to the ninja's wisdom in pirate style via A2A
4. Both responses are returned to the user

Prerequisites:
- NinjaAgent running at http://localhost:5067/a2a/ninja
- PirateAgent running at http://localhost:5066/a2a/pirate
"""

import asyncio
import os
from pathlib import Path

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agentserver.agentframework import from_agent_framework

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


from workflow import build_a2a_workflow


# Default agent URLs
DEFAULT_NINJA_URL = "http://localhost:5067/a2a/ninja"
DEFAULT_PIRATE_URL = "http://localhost:5066/a2a/pirate"


def get_config() -> tuple[str, str]:
    """Get agent URLs from environment or use defaults."""
    ninja_url = os.environ.get("NINJA_AGENT_URL", DEFAULT_NINJA_URL)
    pirate_url = os.environ.get("PIRATE_AGENT_URL", DEFAULT_PIRATE_URL)
    return ninja_url, pirate_url


async def main() -> None:
    """Main entry point for the A2A workflow."""
    # Get configuration
    ninja_url, pirate_url = get_config()
    
    print("\n" + "🌟" * 35)
    print("       A2A AGENTS SEQUENTIAL WORKFLOW")
    print("       Using Microsoft Agent Framework")
    print("🌟" * 35)
    
    print(f"\n📡 Agent Configuration:")
    print(f"   NinjaAgent URL:  {ninja_url}")
    print(f"   PirateAgent URL: {pirate_url}")
    
    
        
    workflow = build_a2a_workflow(
        ninja_url=ninja_url,
        pirate_url=pirate_url
    )

    agentwf = workflow.as_agent()
    await from_agent_framework(agentwf).run_async()
    
  
if __name__ == "__main__":
    asyncio.run(main())
