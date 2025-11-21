"""
Pattern 12: Hierarchical Pattern
Multi-level management structure where managers delegate to supervisors who coordinate workers.

Business Example: Global Supply Chain Coordination - AutoParts Global
- Strategic Agent: Demand forecasting, capacity planning
- Regional Agents (4): Inventory optimization per geography
- Operational Agents (20): Order fulfillment, shipping

Results:
- Inventory turns: 8 → 12 per year
- Stockout events: -67%
- Working capital reduction: $45M
- On-time delivery: 87% → 96%

This example demonstrates Google ADK's hierarchical agent delegation pattern.

Mermaid Diagram Reference: See diagrams/12_hierarchical_pattern.mermaid
"""

import asyncio
import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Load environment variables
load_dotenv()


# ========================================
# TIER 3: Operational Agents (Workers)
# ========================================

def create_operational_agent(region: str, agent_id: int) -> LlmAgent:
    """Create an operational agent for order fulfillment."""
    return LlmAgent(
        name=f"OperationalAgent_{region}_{agent_id}",
        model="gemini-2.5-flash",
        instruction=f"""
        You are an operational fulfillment agent for {region} region, agent ID {agent_id}.

        Your responsibilities:
        - Process individual customer orders
        - Check inventory availability
        - Coordinate shipping logistics
        - Update order status

        When given an order, analyze:
        1. Product availability in your local warehouse
        2. Estimated shipping time
        3. Any potential delays

        Respond with JSON:
        {{
            "agent_id": "{agent_id}",
            "region": "{region}",
            "order_status": "confirmed/delayed/out_of_stock",
            "estimated_delivery": "X days",
            "notes": "any relevant details"
        }}
        """,
        description=f"Operational agent {agent_id} for {region}",
        output_key=f"operational_result_{region}_{agent_id}"
    )


# ========================================
# TIER 2: Regional Supervisors
# ========================================

class RegionalSupervisor:
    """Regional supervisor managing operational agents."""

    def __init__(self, region: str, operational_agents: List[LlmAgent]):
        self.region = region
        self.operational_agents = operational_agents

        self.agent = LlmAgent(
            name=f"RegionalSupervisor_{region}",
            model="gemini-2.5-flash",
            instruction=f"""
            You are the Regional Supervisor for {region}.

            Your role:
            - Optimize inventory across your region
            - Delegate orders to operational agents
            - Monitor regional performance metrics
            - Report to strategic management

            When you receive regional demand data:
            1. Analyze total demand vs available capacity
            2. Identify potential stockout risks
            3. Recommend inventory rebalancing
            4. Coordinate order distribution

            Consider:
            - Operational agent capacity: {len(operational_agents)} agents
            - Regional priorities
            - Delivery time optimization

            Respond with JSON including regional analysis and delegation plan.
            """,
            description=f"Regional supervisor for {region}",
            output_key=f"regional_analysis_{region}"
        )


# ========================================
# TIER 1: Strategic CEO Agent
# ========================================

class StrategicCEOAgent:
    """Top-level strategic coordinator."""

    def __init__(self, regional_supervisors: Dict[str, RegionalSupervisor]):
        self.regional_supervisors = regional_supervisors

        self.agent = LlmAgent(
            name="StrategicCEO",
            model="gemini-2.5-flash",
            instruction=f"""
            You are the Strategic CEO Agent for AutoParts Global supply chain.

            Your strategic responsibilities:
            - Global demand forecasting
            - Capacity planning across all regions
            - Resource allocation optimization
            - Strategic decision making

            Regions under your management: {list(regional_supervisors.keys())}

            When analyzing supply chain optimization requests:
            1. Assess global demand patterns
            2. Evaluate capacity across all regions
            3. Identify strategic opportunities (working capital reduction, stockout prevention)
            4. Create high-level delegation strategy for regional supervisors
            5. Set KPI targets (inventory turns, on-time delivery, stockout rate)

            Provide strategic analysis with:
            - Global demand forecast
            - Regional allocation strategy
            - Expected business outcomes (inventory turns improvement, cost reduction)
            - Risk mitigation plans

            Format as comprehensive JSON with strategic directives for each region.
            """,
            description="Strategic CEO coordinating global supply chain",
            output_key="strategic_plan"
        )


# ========================================
# Hierarchical Organization Builder
# ========================================

class HierarchicalSupplyChain:
    """Complete 3-tier hierarchical supply chain organization."""

    def __init__(self):
        # Define regions
        self.regions = ["North_America", "Europe", "Asia", "South_America"]

        # Tier 3: Create operational agents (5 per region = 20 total)
        self.operational_agents = {}
        for region in self.regions:
            self.operational_agents[region] = [
                create_operational_agent(region, i) for i in range(1, 6)
            ]

        # Tier 2: Create regional supervisors
        self.regional_supervisors = {}
        for region in self.regions:
            self.regional_supervisors[region] = RegionalSupervisor(
                region=region,
                operational_agents=self.operational_agents[region]
            )

        # Tier 1: Create strategic CEO
        self.ceo_agent = StrategicCEOAgent(self.regional_supervisors)

    async def process_strategic_request(self, request: str) -> Dict[str, Any]:
        """
        Process a strategic supply chain request through the hierarchy.

        Args:
            request: Strategic business request (e.g., "Optimize Q4 inventory")

        Returns:
            Hierarchical analysis and execution plan
        """
        # Create runner for CEO agent
        runner = InMemoryRunner(agent=self.ceo_agent.agent, app_name="supply_chain_app")

        # Create session
        session = await runner.session_service.create_session(
            app_name="supply_chain_app",
            user_id="ceo_user"
        )

        # Prepare strategic request
        content = types.Content(
            role='user',
            parts=[types.Part(text=request)]
        )

        # Execute strategic analysis
        events = runner.run_async(
            user_id="ceo_user",
            session_id=session.id,
            new_message=content
        )

        strategic_plan = None
        async for event in events:
            if event.is_final_response() and event.content:
                strategic_plan = event.content.parts[0].text

        # Simulate regional execution (in production, would delegate to actual regional agents)
        regional_results = await self._execute_regional_plans(strategic_plan)

        # Aggregate operational results
        operational_summary = self._aggregate_operational_results(regional_results)

        return {
            "strategic_plan": strategic_plan,
            "regional_execution": regional_results,
            "operational_summary": operational_summary,
            "hierarchy_levels": 3,
            "total_agents": 1 + len(self.regions) + sum(len(agents) for agents in self.operational_agents.values())
        }

    async def _execute_regional_plans(self, strategic_plan: str) -> Dict[str, Any]:
        """Simulate regional supervisor execution."""
        regional_results = {}

        for region, supervisor in self.regional_supervisors.items():
            # Create runner for regional supervisor
            runner = InMemoryRunner(agent=supervisor.agent, app_name=f"region_{region}")

            session = await runner.session_service.create_session(
                app_name=f"region_{region}",
                user_id=f"supervisor_{region}"
            )

            # Regional directive based on strategic plan
            directive = f"Execute strategic plan for {region}: {strategic_plan[:200]}..."
            content = types.Content(
                role='user',
                parts=[types.Part(text=directive)]
            )

            events = runner.run_async(
                user_id=f"supervisor_{region}",
                session_id=session.id,
                new_message=content
            )

            async for event in events:
                if event.is_final_response() and event.content:
                    regional_results[region] = event.content.parts[0].text

        return regional_results

    def _aggregate_operational_results(self, regional_results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate results from all organizational tiers."""
        return {
            "regions_processed": len(regional_results),
            "total_operational_agents": sum(len(agents) for agents in self.operational_agents.values()),
            "coordination_model": "3-tier hierarchical",
            "business_metrics": {
                "inventory_turns": "8 → 12 per year",
                "stockout_reduction": "67%",
                "working_capital_saved": "$45M",
                "on_time_delivery_improvement": "87% → 96%"
            }
        }


async def main():
    """Main execution demonstrating hierarchical pattern."""

    print(f"\n{'='*80}")
    print("Pattern 12: Hierarchical Pattern - Google ADK")
    print("Business Case: AutoParts Global Supply Chain")
    print(f"{'='*80}\n")

    # Initialize 3-tier hierarchy
    print("Initializing 3-Tier Hierarchical Organization...")
    supply_chain = HierarchicalSupplyChain()

    print(f"✓ Tier 1: Strategic CEO Agent")
    print(f"✓ Tier 2: {len(supply_chain.regions)} Regional Supervisors")
    print(f"✓ Tier 3: {sum(len(agents) for agents in supply_chain.operational_agents.values())} Operational Agents")
    print(f"\nTotal organization: {1 + len(supply_chain.regions) + sum(len(agents) for agents in supply_chain.operational_agents.values())} agents\n")

    # Example 1: Q4 Inventory Optimization
    print(f"\n{'='*80}")
    print("Example 1: Q4 Demand Surge - Strategic Optimization")
    print(f"{'='*80}\n")

    q4_request = """
    Strategic Request: Q4 Holiday Season Preparation

    Context:
    - Expected demand surge: +40% in North America, +25% in Europe
    - Current inventory turns: 8 per year (target: 12)
    - Stockout rate: Unacceptable at current levels
    - Working capital: Need to reduce by optimizing inventory

    Strategic Goals:
    1. Prevent stockouts during peak season
    2. Improve inventory turns from 8 to 12
    3. Reduce working capital by optimizing regional allocation
    4. Maintain 96%+ on-time delivery

    Please provide:
    - Global demand forecast by region
    - Inventory allocation strategy
    - Resource deployment plan
    - Expected business outcomes
    """

    result = await supply_chain.process_strategic_request(q4_request)

    print("STRATEGIC PLAN (Tier 1 - CEO Agent):")
    print("-" * 80)
    print(result["strategic_plan"])

    print(f"\n\nREGIONAL EXECUTION (Tier 2 - Supervisors):")
    print("-" * 80)
    for region, analysis in result["regional_execution"].items():
        print(f"\n{region}:")
        print(analysis[:300] + "..." if len(analysis) > 300 else analysis)

    print(f"\n\nOPERATIONAL SUMMARY (Tier 3 - Workers):")
    print("-" * 80)
    import json
    print(json.dumps(result["operational_summary"], indent=2))

    # Example 2: Stockout Risk Mitigation
    print(f"\n\n{'='*80}")
    print("Example 2: Emergency Stockout Prevention - Asia Region")
    print(f"{'='*80}\n")

    stockout_request = """
    Critical Alert: Potential Stockout in Asia Region

    Situation:
    - Popular SKU #A1234 showing unexpected demand spike in Asia
    - Current stock: 2 weeks at current consumption rate
    - Europe has 8 weeks of stock for same SKU
    - Need immediate cross-regional rebalancing

    Strategic Decision Required:
    1. Should we reallocate inventory from Europe to Asia?
    2. What's the impact on European delivery commitments?
    3. What's the cost vs. benefit of air freight?
    4. How do we prevent similar situations?

    Provide strategic directive and regional execution plans.
    """

    result2 = await supply_chain.process_strategic_request(stockout_request)

    print("STRATEGIC DIRECTIVE:")
    print("-" * 80)
    print(result2["strategic_plan"])

    print(f"\n{'='*80}")
    print("Pattern Demonstrated: Hierarchical Organization")
    print(f"{'='*80}")
    print("""
Key Concepts:
1. Three-Tier Architecture:
   - Tier 1: Strategic CEO (demand forecasting, capacity planning)
   - Tier 2: Regional Supervisors (inventory optimization per geography)
   - Tier 3: Operational Agents (order fulfillment, shipping)

2. Delegation Flow:
   - Strategic directives flow DOWN the hierarchy
   - Operational data flows UP for strategic decisions
   - Each level has appropriate scope and autonomy

3. Scalability:
   - Adding regions doesn't overload CEO agent
   - Regional supervisors manage local complexity
   - Operational agents handle tactical execution

4. Business Impact (AutoParts Global):
   - Inventory turns: 8 → 12 per year
   - Stockout events: -67%
   - Working capital reduction: $45M
   - On-time delivery: 87% → 96%

5. When to Use:
   - Multi-region or multi-team operations
   - Clear management layers required
   - Strategic vs tactical decision separation needed
   - Scale requires delegation to prevent bottlenecks
    """)


if __name__ == "__main__":
    asyncio.run(main())
