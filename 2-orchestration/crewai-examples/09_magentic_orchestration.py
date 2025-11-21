"""
Pattern 17: Magentic Orchestration
Dynamic plan generation with task ledger management.

Business Example: Dynamic Project Management - StrategyPartners
Results: On-time delivery 62% → 94%, Resource utilization 71% → 89%

This example demonstrates CrewAI's dynamic planning approach.

Mermaid Diagram Reference: See diagrams/17_magentic_orchestration.mermaid
"""

from crewai import Agent, Task, Crew, Process
from typing import Dict


def create_magentic_crew() -> Crew:
    """Create crew with dynamic planning capability."""

    manager = Agent(
        role="Dynamic Project Manager",
        goal="Create and continuously update project plans based on actual progress",
        backstory="""You use magentic orchestration to manage projects.
        You create initial plans but continuously replan based on:
        - Task execution results
        - Changing requirements
        - Resource availability
        - Discovered dependencies

        You maintain a dynamic task ledger that evolves with reality.""",
        verbose=True,
        allow_delegation=True
    )

    executor = Agent(
        role="Project Executor",
        goal="Execute tasks and report progress for replanning",
        backstory="""You execute project tasks and report results.
        Your feedback helps the manager replan dynamically.""",
        verbose=True,
        allow_delegation=False
    )

    planning_task = Task(
        description="""Create initial project plan for: {project_goal}

        Break down into tasks with dependencies and timeline.
        This is the initial plan - it will evolve.""",
        expected_output="Initial task ledger with tasks, dependencies, timeline",
        agent=manager
    )

    execution_task = Task(
        description="""Execute tasks from the plan.

        Report: What worked, what failed, what changed.
        This feedback triggers replanning.""",
        expected_output="Execution results and discovered issues",
        agent=executor,
        context=[planning_task]
    )

    replan_task = Task(
        description="""Based on execution results, update the plan.

        Adjust tasks, dependencies, resources, timeline.
        Create updated task ledger.""",
        expected_output="Updated task ledger reflecting reality",
        agent=manager,
        context=[planning_task, execution_task]
    )

    return Crew(
        agents=[manager, executor],
        tasks=[planning_task, execution_task, replan_task],
        process=Process.sequential,
        verbose=True
    )


def main():
    """Main execution demonstrating magentic orchestration."""

    print(f"\n{'='*80}")
    print("Pattern 17: Magentic Orchestration - CrewAI")
    print("Business Case: StrategyPartners - Dynamic Project Management")
    print(f"{'='*80}\n")

    crew = create_magentic_crew()

    project_goal = """
    Digital Transformation Project

    - Migrate legacy systems to cloud
    - Implement new CRM
    - Timeline: 6 months, Team: 12 people, Budget: $2M

    Challenges: Frequent requirement changes, discovered dependencies,
    fluctuating resources, technical blockers

    Need: Plan that adapts to reality"""

    result = crew.kickoff(inputs={"project_goal": project_goal})

    print(f"\nResult:\n{result}")

    print(f"\n{'='*80}")
    print("Business Metrics (StrategyPartners):")
    print(f"{'='*80}")
    print("- On-time delivery: 62% → 94%")
    print("- Resource utilization: 71% → 89%")
    print("- Change handling: 3x faster")
    print("- Profitability: +28%")


if __name__ == "__main__":
    main()
