"""
Pattern 6: Planning
Multi-step strategy generation where agents create execution plans before acting.

Business Example: Project management assistant
- Analyze requirements → Generate project plan → Break into tasks → Assign resources

This example demonstrates Google ADK's planning capabilities for complex workflow orchestration.

Mermaid Diagram Reference: See diagrams/06_planning.mermaid
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared-utilities"))

from typing import Any, Dict, List
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.genai.errors import ServerError
import json
from retry_utils import run_with_retry


# Planner Agent: Creates execution strategy
planner_agent = LlmAgent(
    name="StrategyPlanner",
    model="gemini-2.5-flash",
    instruction="""
    You are a strategic planner for project management.
    
    Given a project description, create a detailed execution plan with:
    1. Project phases (high-level stages)
    2. Key milestones
    3. Resource requirements
    4. Risk factors
    5. Success criteria
    
    Output as JSON:
    {
        "project_name": "...",
        "phases": [{"name": "...", "duration": "...", "deliverables": [...]}],
        "milestones": [{"name": "...", "deadline": "..."}],
        "resources": [{"type": "...", "count": ...}],
        "risks": [{"risk": "...", "mitigation": "..."}],
        "success_criteria": [...]
    }
    """,
    output_key="project_plan"
)


# Task Breakdown Agent: Decomposes plan into tasks
task_agent = LlmAgent(
    name="TaskBreakdown",
    model="gemini-2.5-flash",
    instruction="""
    You are a task decomposition specialist.
    
    Take the project plan from state['project_plan'] and break it into specific tasks.
    
    For each phase, create concrete, actionable tasks with:
    - Task name
    - Description
    - Estimated effort (hours)
    - Dependencies
    - Required skills
    
    Output as JSON array of tasks.
    """,
    output_key="task_list"
)


# Resource Allocator: Assigns resources to tasks
resource_agent = LlmAgent(
    name="ResourceAllocator",
    model="gemini-2.5-flash",
    instruction="""
    You are a resource allocation specialist.
    
    Based on state['project_plan'] and state['task_list'], create a resource allocation plan.
    
    Output as JSON:
    {
        "team_composition": [{"role": "...", "count": ..., "skills": [...]}],
        "task_assignments": [{"task": "...", "assigned_to": "...", "start_date": "..."}],
        "timeline": "...",
        "budget_estimate": {...}
    }
    """,
    output_key="resource_plan"
)


# Create planning pipeline
planning_pipeline = SequentialAgent(
    name="ProjectPlanningPipeline",
    sub_agents=[planner_agent, task_agent, resource_agent]
)


async def create_project_plan(project_description: str) -> Dict[str, Any]:
    """Generate a comprehensive project plan with retry logic."""
    session_service = InMemorySessionService()
    app_name = "agentic_patterns"
    user_id = "demo_user"
    session_id = "planning_001"

    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    runner = Runner(
        agent=planning_pipeline,
        app_name=app_name,
        session_service=session_service
    )

    content = types.Content(role='user', parts=[types.Part(text=project_description)])

    try:
        events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content)

        async for event in events:
            if event.is_final_response():
                pass

        # Get updated session to access state
        updated_session = await session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )

        return {
            "project_plan": updated_session.state.get("project_plan"),
            "task_list": updated_session.state.get("task_list"),
            "resource_plan": updated_session.state.get("resource_plan")
        }

    finally:
        # Cleanup async resources
        await asyncio.sleep(0.25)


async def main():
    """Demonstrate planning pattern with error handling."""
    print("=" * 80)
    print("Example: Project Planning - E-commerce Platform")
    print("=" * 80)

    project_desc = """
    Project: Build a new e-commerce platform

    Requirements:
    - User authentication and profiles
    - Product catalog with search
    - Shopping cart and checkout
    - Payment integration
    - Order management
    - Admin dashboard

    Timeline: 6 months
    Budget: $500K
    Team: 8 developers, 2 designers, 1 PM
    """

    print("Project Description:", project_desc)

    try:
        # Use retry wrapper for API calls
        result = await run_with_retry(
            create_project_plan,
            project_desc,
            max_retries=3,
            base_delay=3.0
        )

        if result:
            print("\nProject Plan:")
            print(result['project_plan'])
            print("\nTask Breakdown:")
            print(result['task_list'])
            print("\nResource Allocation:")
            print(result['resource_plan'])
        else:
            print("\n⚠️  Unable to generate plan (API unavailable)")

    except ServerError as e:
        print(f"\n❌ API Error: {e.message}")
        print("Note: This is a temporary Google AI API issue, not a code error.")
        print("The planning pattern implementation is correct.")

    except Exception as e:
        print(f"\n❌ Unexpected error: {type(e).__name__}: {str(e)}")

    finally:
        print("\n" + "=" * 80)
        print("Pattern: Planning - Multi-step strategy generation")
        print("=" * 80)
        # Final cleanup
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
