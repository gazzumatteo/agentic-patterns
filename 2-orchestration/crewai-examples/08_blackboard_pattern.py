"""
Pattern 16: Blackboard Pattern
Shared workspace where agents asynchronously contribute to evolving solutions.

Business Example: Collaborative Product Design - InnovateTech
Results: Design cycles 6 months → 6 weeks, Prototype iterations 8 → 3

This example demonstrates CrewAI's blackboard pattern using shared context.

Mermaid Diagram Reference: See diagrams/16_blackboard_pattern.mermaid
"""

from crewai import Agent, Task, Crew, Process
from typing import Dict


def create_blackboard_crew() -> Crew:
    """Create collaborative design crew with shared workspace."""

    designer = Agent(
        role="Industrial Designer",
        goal="Contribute aesthetic and ergonomic design expertise to shared product concept",
        backstory="""You specialize in consumer electronics design. You contribute visual appeal,
        ergonomics, materials, and UX. You read the shared design and add your expertise.""",
        verbose=True,
        allow_delegation=False
    )

    engineer = Agent(
        role="Product Engineer",
        goal="Contribute technical feasibility and manufacturing expertise",
        backstory="""You validate technical feasibility. You contribute constraints,
        specifications, and engineering trade-offs to the shared design.""",
        verbose=True,
        allow_delegation=False
    )

    cost_analyst = Agent(
        role="Cost Analyst",
        goal="Contribute pricing and profitability analysis",
        backstory="""You analyze cost implications. You contribute BOM estimates,
        margin analysis, and ensure design stays within budget.""",
        verbose=True,
        allow_delegation=False
    )

    marketer = Agent(
        role="Marketing Strategist",
        goal="Contribute market research and customer insights",
        backstory="""You ensure market fit. You contribute customer preferences,
        competitive positioning, and feature prioritization.""",
        verbose=True,
        allow_delegation=False
    )

    # Blackboard tasks - each reads shared state and contributes
    design_task = Task(
        description="""Review product brief: {product_brief}

        Contribute your design expertise to the shared workspace.
        Iteration {iteration}: Build on previous contributions if available.""",
        expected_output="Design contribution: aesthetics, ergonomics, materials, UX",
        agent=designer
    )

    engineering_task = Task(
        description="""Review current design concept from blackboard.

        Contribute technical analysis and engineering constraints.""",
        expected_output="Engineering contribution: feasibility, specs, constraints",
        agent=engineer,
        context=[design_task]
    )

    cost_task = Task(
        description="""Review design and engineering contributions.

        Contribute cost analysis and profitability assessment.""",
        expected_output="Cost contribution: BOM, margins, pricing",
        agent=cost_analyst,
        context=[design_task, engineering_task]
    )

    marketing_task = Task(
        description="""Review all contributions on the blackboard.

        Contribute market analysis and customer insights.
        Synthesize final design recommendation.""",
        expected_output="Marketing contribution + synthesized design recommendation",
        agent=marketer,
        context=[design_task, engineering_task, cost_task]
    )

    return Crew(
        agents=[designer, engineer, cost_analyst, marketer],
        tasks=[design_task, engineering_task, cost_task, marketing_task],
        process=Process.sequential,
        verbose=True
    )


def main():
    """Main execution demonstrating blackboard pattern."""

    print(f"\n{'='*80}")
    print("Pattern 16: Blackboard Pattern - CrewAI")
    print("Business Case: InnovateTech - Collaborative Product Design")
    print(f"{'='*80}\n")

    crew = create_blackboard_crew()

    product_brief = """
    Smart Home Security Camera

    - Target: Home security consumers
    - Price: $150-200
    - Features: AI motion detection, night vision, cloud storage
    - Requirements: Aesthetically pleasing, easy DIY install
    - Competition: Ring, Nest

    Collaborate to refine this concept."""

    result = crew.kickoff(inputs={"product_brief": product_brief, "iteration": 1})

    print(f"\nResult:\n{result}")

    print(f"\n{'='*80}")
    print("Business Metrics (InnovateTech):")
    print(f"{'='*80}")
    print("- Design cycles: 6 months → 6 weeks")
    print("- Prototype iterations: 8 → 3")
    print("- Market fit score: 7.2 → 8.9")
    print("- Development cost: -40%")


if __name__ == "__main__":
    main()
