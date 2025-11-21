"""
Pattern 16: Blackboard Pattern
Shared workspace where agents asynchronously contribute to evolving solutions.
Collaborative problem-solving through incremental refinement.

Business Example: Collaborative Product Design - InnovateTech
- Industrial Designer Agent: Aesthetic concepts
- Engineer Agent: Technical constraints
- Cost Analyst Agent: Pricing implications
- Marketing Agent: Market research
- All agents iterate on shared design document

Results:
- Design cycles: 6 months → 6 weeks
- Prototype iterations: 8 → 3
- Market fit score: 7.2 → 8.9
- Development cost: -40%

This example demonstrates Google ADK's blackboard pattern for collaborative design.

Mermaid Diagram Reference: See diagrams/16_blackboard_pattern.mermaid
"""

import asyncio
import json
from typing import Dict, List, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

load_dotenv()


@dataclass
class Blackboard:
    """Shared workspace for collaborative design."""
    design_concept: Dict[str, Any] = field(default_factory=dict)
    contributions: List[Dict[str, Any]] = field(default_factory=list)
    iteration: int = 0

    def add_contribution(self, agent_name: str, contribution: Dict[str, Any]):
        """Add agent contribution to blackboard."""
        self.contributions.append({
            "iteration": self.iteration,
            "agent": agent_name,
            "contribution": contribution
        })

    def get_current_state(self) -> str:
        """Get current design state as text."""
        return json.dumps({
            "concept": self.design_concept,
            "iteration": self.iteration,
            "contributions": len(self.contributions)
        }, indent=2)


# Agent definitions
designer_agent = LlmAgent(
    name="IndustrialDesigner",
    model="gemini-2.5-flash",
    instruction="""You are an Industrial Designer specializing in consumer electronics aesthetics.

    Review the current design on the blackboard and contribute:
    - Aesthetic improvements and visual appeal
    - Ergonomic considerations
    - Material recommendations
    - User experience enhancements

    Build on others' contributions while adding your design expertise.""",
    output_key="design_contribution"
)

engineer_agent = LlmAgent(
    name="EngineeringAgent",
    model="gemini-2.5-flash",
    instruction="""You are a Product Engineer focused on technical feasibility.

    Review the blackboard design and contribute:
    - Technical constraints and feasibility
    - Manufacturing considerations
    - Component specifications
    - Engineering trade-offs

    Validate design concepts against engineering realities.""",
    output_key="engineering_contribution"
)

cost_analyst_agent = LlmAgent(
    name="CostAnalyst",
    model="gemini-2.5-flash",
    instruction="""You are a Cost Analyst focused on pricing and profitability.

    Review the blackboard design and contribute:
    - Cost implications of design choices
    - Target price point analysis
    - Bill of materials estimates
    - Margin and profitability projections

    Ensure design stays within budget constraints.""",
    output_key="cost_contribution"
)

marketing_agent = LlmAgent(
    name="MarketingAgent",
    model="gemini-2.5-flash",
    instruction="""You are a Marketing Strategist focused on market fit.

    Review the blackboard design and contribute:
    - Market research insights
    - Target customer preferences
    - Competitive positioning
    - Feature prioritization based on demand

    Ensure design aligns with market needs.""",
    output_key="marketing_contribution"
)


class BlackboardSystem:
    """Manages collaborative design through shared blackboard."""

    def __init__(self):
        self.blackboard = Blackboard()
        self.agents = [designer_agent, engineer_agent, cost_analyst_agent, marketing_agent]

    async def collaborate(self, product_brief: str, max_rounds: int = 3) -> Dict[str, Any]:
        """Run collaborative design process."""
        print(f"\n{'='*80}")
        print(f"Blackboard Collaboration: {max_rounds} iteration rounds")
        print(f"{'='*80}\n")

        # Initialize with product brief
        self.blackboard.design_concept = {"brief": product_brief}

        for round_num in range(max_rounds):
            self.blackboard.iteration = round_num + 1
            print(f"\nIteration {round_num + 1}/{max_rounds}")
            print("-" * 80)

            # Each agent contributes asynchronously
            for agent in self.agents:
                contribution = await self._get_agent_contribution(agent)
                self.blackboard.add_contribution(agent.name, contribution)
                print(f"✓ {agent.name} contributed")

        return {
            "final_design": self.blackboard.design_concept,
            "total_contributions": len(self.blackboard.contributions),
            "iterations": self.blackboard.iteration,
            "collaborative_insights": self._analyze_collaboration()
        }

    async def _get_agent_contribution(self, agent: LlmAgent) -> Dict[str, Any]:
        """Get contribution from single agent."""
        runner = InMemoryRunner(agent=agent, app_name="blackboard_app")
        session = await runner.session_service.create_session(
            app_name="blackboard_app",
            user_id=f"user_{agent.name}"
        )

        prompt = f"""Current Blackboard State:
{self.blackboard.get_current_state()}

Provide your contribution based on your expertise. Build on existing contributions."""

        content = types.Content(role='user', parts=[types.Part(text=prompt)])
        events = runner.run_async(
            user_id=f"user_{agent.name}",
            session_id=session.id,
            new_message=content
        )

        contribution = None
        async for event in events:
            if event.is_final_response() and event.content:
                contribution = {"text": event.content.parts[0].text}

        return contribution

    def _analyze_collaboration(self) -> str:
        """Analyze collaborative patterns."""
        return f"Incremental refinement through {len(self.blackboard.contributions)} contributions"


async def main():
    """Main execution demonstrating blackboard pattern."""

    print(f"\n{'='*80}")
    print("Pattern 16: Blackboard Pattern - Google ADK")
    print("Business Case: InnovateTech - Collaborative Product Design")
    print(f"{'='*80}\n")

    system = BlackboardSystem()

    product_brief = """
    New Product: Smart Home Security Camera

    Initial Concept:
    - AI-powered indoor security camera
    - Target market: Home security conscious consumers
    - Price point: $150-200
    - Key features: Motion detection, night vision, cloud storage

    Design Requirements:
    - Must be aesthetically pleasing (not industrial-looking)
    - Easy installation (DIY)
    - Competitive with Ring, Nest
    - Profitable at target price point

    Collaborate to refine this concept with all perspectives.
    """

    result = await system.collaborate(product_brief, max_rounds=3)

    print(f"\n\n{'='*80}")
    print("Collaboration Results:")
    print(f"{'='*80}")
    print(f"Total Contributions: {result['total_contributions']}")
    print(f"Iterations: {result['iterations']}")
    print(f"\nBusiness Metrics (InnovateTech):")
    print("  - Design cycles: 6 months → 6 weeks")
    print("  - Prototype iterations: 8 → 3")
    print("  - Market fit score: 7.2 → 8.9")
    print("  - Development cost: -40%")

    print(f"\n{'='*80}")
    print("Key Concepts:")
    print(f"{'='*80}")
    print("""
1. Shared Workspace (Blackboard):
   - All agents read/write to same design document
   - Asynchronous contributions
   - No coordination overhead

2. Incremental Refinement:
   - Each agent adds expertise
   - Builds on previous contributions
   - Design evolves through iterations

3. Multi-Perspective Convergence:
   - Design, Engineering, Cost, Marketing perspectives
   - Holistic solution emerges
   - Better than any single perspective
    """)


if __name__ == "__main__":
    asyncio.run(main())
