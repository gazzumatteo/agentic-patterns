"""
Pattern 18: Market-Based Pattern
Agents bid for tasks or resources. Economic principles drive allocation.

Business Example: Cloud Resource Allocation - InfraCloud
Results: Utilization 68% → 91%, Customer cost -23%, Revenue +41%

This example demonstrates CrewAI's market-based allocation approach.

Mermaid Diagram Reference: See diagrams/18_market_based_pattern.mermaid
"""

from crewai import Agent, Task, Crew, Process
from typing import Dict
import random


def create_market_based_crew(num_agents: int = 5) -> Crew:
    """Create crew with market-based resource allocation."""

    # Create compute agents with bidding capability
    agents = []
    tasks = []

    for i in range(num_agents):
        capacity = random.choice([4, 8, 16, 32])
        current_load = random.uniform(0, 0.8)

        agent = Agent(
            role=f"Compute Agent {i} ({capacity} cores)",
            goal=f"Bid competitively for jobs to maximize revenue while balancing load",
            backstory=f"""You are compute resource {i} with {capacity} cores.
            Current load: {current_load:.0%}

            Bidding strategy:
            - Base price: $0.10 per core-hour
            - Adjust based on current load (higher load = higher price)
            - Offer spot discounts for non-critical jobs
            - Maximize revenue while maintaining optimal utilization

            Your bids reflect your availability and capabilities.""",
            verbose=False,
            allow_delegation=False
        )

        agents.append(agent)

        task = Task(
            description="""Calculate your bid for job: {job_description}

            Consider:
            - Your current load
            - Job requirements
            - Profit optimization
            - Competitive positioning

            Submit competitive bid.""",
            expected_output=f"Bid from Agent {i}: price, rationale, capabilities",
            agent=agent
        )

        tasks.append(task)

    # Auction manager selects winner
    auction_manager = Agent(
        role="Auction Manager",
        goal="Select winning bid based on price and capabilities",
        backstory="""You manage the resource allocation auction.
        You collect all bids and select the winner based on:
        - Lowest price (primary)
        - Capability match
        - SLA requirements

        You ensure efficient allocation and fair pricing.""",
        verbose=True,
        allow_delegation=False
    )

    selection_task = Task(
        description="""Review all bids for job: {job_description}

        Select winning bid based on:
        - Price (lowest wins)
        - Capability match
        - Availability

        Announce winner and explain selection.""",
        expected_output="Winner announcement with price and rationale",
        agent=auction_manager,
        context=tasks  # Sees all bids
    )

    return Crew(
        agents=agents + [auction_manager],
        tasks=tasks + [selection_task],
        process=Process.sequential,
        verbose=True
    )


def main():
    """Main execution demonstrating market-based pattern."""

    print(f"\n{'='*80}")
    print("Pattern 18: Market-Based Pattern - CrewAI")
    print("Business Case: InfraCloud - Resource Allocation")
    print(f"{'='*80}\n")

    crew = create_market_based_crew(num_agents=5)

    job_description = """
    Job: ML Model Training

    Requirements:
    - 16 cores
    - 64GB RAM
    - 8 hours estimated runtime
    - Priority: Normal (not spot)

    Submit your bid with price and rationale."""

    result = crew.kickoff(inputs={"job_description": job_description})

    print(f"\nAuction Result:\n{result}")

    print(f"\n{'='*80}")
    print("Business Metrics (InfraCloud):")
    print(f"{'='*80}")
    print("- Resource utilization: 68% → 91%")
    print("- Customer cost: -23% average")
    print("- SLA compliance: 99.95% → 99.99%")
    print("- Revenue per server: +41%")

    print(f"\n{'='*80}")
    print("Key Concepts:")
    print(f"{'='*80}")
    print("""
- Market Mechanism: Agents bid competitively
- Price Discovery: Supply/demand sets prices
- Automatic Load Balancing: Low-load agents win more
- Economic Efficiency: Resources flow to highest value
- Transparent Allocation: No politics, pure economics
    """)


if __name__ == "__main__":
    main()
