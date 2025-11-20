"""
Pattern 5: Tool Use
Integration with external APIs, databases, and custom functions to extend agent capabilities.

Business Example: Research agent with search and database tools
- Search web → Query database → Calculate metrics → Generate report

This example demonstrates Google ADK's function-based tool system for enabling agents
to interact with external systems and perform specialized operations.

Mermaid Diagram Reference: See diagrams/05_tool_use.mermaid
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from typing import Any, List, Dict
from datetime import datetime
from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext
import json
import random


# Tool 1: Web Search (simulated)
async def web_search(query: str, max_results: int = 5, tool_context: ToolContext = None) -> str:
    """Search the web for information."""
    results = [{
        "title": f"Result {i+1} for: {query}",
        "url": f"https://example.com/result-{i+1}",
        "snippet": f"Information about {query} from source {i+1}.",
    } for i in range(min(max_results, 3))]
    return json.dumps(results, indent=2)


# Tool 2: Database Query (simulated)
async def query_database(table: str, limit: int = 10, tool_context: ToolContext = None) -> str:
    """Query database for records."""
    if table == "customers":
        records = [{
            "id": i + 1,
            "name": f"Customer {i + 1}",
            "email": f"customer{i + 1}@example.com",
            "lifetime_value": random.randint(1000, 10000),
        } for i in range(min(limit, 5))]
    else:
        records = []
    return json.dumps(records, indent=2)


# Create agent with tools
research_agent = LlmAgent(
    name="ResearchAnalyst",
    model="gemini-2.5-flash",
    instruction="You are a research analyst. Use tools to gather and analyze information.",
    tools=[web_search, query_database]
)


async def main():
    print("Pattern 5: Tool Use - Agents can use external tools")

if __name__ == "__main__":
    asyncio.run(main())
