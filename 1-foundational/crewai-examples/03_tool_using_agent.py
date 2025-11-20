"""
Pattern 5: Tool Use
Integration with external APIs and tools to extend agent capabilities.

Business Example: Research agent with search and database tools

Mermaid Diagram Reference: See diagrams/05_tool_use.mermaid
"""

from crewai import Agent, Task, Crew
from crewai.tools import tool
import json
import random


@tool("Web Search")
def web_search(query: str) -> str:
    """Search the web for information."""
    results = [{
        "title": f"Result for: {query}",
        "snippet": f"Information about {query}",
    }]
    return json.dumps(results)


@tool("Database Query")
def query_database(table: str) -> str:
    """Query database for records."""
    records = [{
        "id": 1,
        "name": "Sample Record",
    }]
    return json.dumps(records)


def main():
    researcher = Agent(
        role="Research Analyst",
        goal="Gather and analyze information using available tools",
        backstory="Expert at using tools to research topics.",
        tools=[web_search, query_database],
        verbose=True
    )
    
    task = Task(
        description="Research AI trends using web search and database",
        expected_output="Research summary",
        agent=researcher
    )
    
    crew = Crew(agents=[researcher], tasks=[task])
    result = crew.kickoff()
    print(result)

if __name__ == "__main__":
    main()
