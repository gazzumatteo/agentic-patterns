"""
Pattern 6: Planning
Multi-step strategy generation where agents create execution plans before acting.

Business Example: Project management assistant

Mermaid Diagram Reference: See diagrams/06_planning.mermaid
"""

from crewai import Agent, Task, Crew, Process


def create_planning_crew():
    """Create crew for project planning."""
    
    planner = Agent(
        role="Strategic Planner",
        goal="Create comprehensive project plans with phases, milestones, and resources",
        backstory="Expert at breaking down complex projects into executable plans.",
        verbose=True
    )
    
    task_manager = Agent(
        role="Task Manager",
        goal="Break down project phases into specific, actionable tasks",
        backstory="Specialist in task decomposition and dependency management.",
        verbose=True
    )
    
    resource_manager = Agent(
        role="Resource Manager",
        goal="Allocate resources efficiently across project tasks",
        backstory="Expert in team composition and resource optimization.",
        verbose=True
    )
    
    return Crew(
        agents=[planner, task_manager, resource_manager],
        tasks=[],
        process=Process.sequential,
        planning=True,  # Enable CrewAI planning feature
        verbose=True
    )


def main():
    """Demonstrate planning pattern."""
    print("=" * 80)
    print("Pattern 6: Planning with CrewAI")
    print("=" * 80)
    
    crew = create_planning_crew()
    planner, task_manager, resource_manager = crew.agents
    
    project_desc = """
    Project: Build an e-commerce platform
    Timeline: 6 months
    Budget: $500K
    Team: 8 developers, 2 designers, 1 PM
    """
    
    plan_task = Task(
        description=f"Create a comprehensive project plan for: {project_desc}",
        expected_output="Detailed project plan with phases and milestones",
        agent=planner
    )
    
    breakdown_task = Task(
        description="Break down the project plan into specific tasks",
        expected_output="List of actionable tasks with dependencies",
        agent=task_manager,
        context=[plan_task]
    )
    
    allocation_task = Task(
        description="Create resource allocation plan for all tasks",
        expected_output="Resource assignment and timeline",
        agent=resource_manager,
        context=[plan_task, breakdown_task]
    )
    
    crew.tasks = [plan_task, breakdown_task, allocation_task]
    result = crew.kickoff()
    
    print("\nFinal Plan:")
    print(result)


if __name__ == "__main__":
    main()
