"""
Pattern 30: Learning and Adaptation
Agents that improve through experience, modifying strategies based on outcomes
and updating their knowledge base without redeployment.

Business Example: Dynamic Pricing Optimization
- Agent adjusts prices based on demand, competition, inventory
- Learns from each transaction outcome
- Updates pricing strategy without human intervention
- Discovers non-obvious patterns (weather impact on electronics sales)

This example demonstrates Google ADK's memory and state management for
implementing learning agents that adapt based on performance feedback.

Mermaid Diagram Reference: See diagrams/30_learning_adaptation.mermaid
"""

import asyncio
import json
from typing import Any, Dict, List
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools import exit_loop
from google.genai import types


class PricingStrategyMemory:
    """Stores and updates pricing strategies based on outcomes."""

    def __init__(self):
        self.strategies: Dict[str, Dict] = {
            "base_multiplier": 1.0,
            "demand_weight": 0.3,
            "competition_weight": 0.2,
            "inventory_weight": 0.1,
            "learning_rate": 0.01,
            "success_count": 0,
            "total_attempts": 0
        }
        self.performance_history: List[Dict] = []

    def update_strategy(self, outcome: Dict[str, Any]) -> None:
        """Update pricing strategy based on transaction outcome."""
        success = outcome.get("success", False)
        revenue = outcome.get("revenue", 0.0)
        target_revenue = outcome.get("target_revenue", 100.0)

        self.strategies["total_attempts"] += 1
        if success:
            self.strategies["success_count"] += 1

        # Calculate performance metric
        performance_ratio = revenue / target_revenue if target_revenue > 0 else 0

        # Adaptive learning: adjust weights based on performance
        if performance_ratio > 1.2:  # Exceeded target significantly
            # Increase successful weights
            self.strategies["demand_weight"] += self.strategies["learning_rate"]
        elif performance_ratio < 0.8:  # Below target
            # Adjust strategy more conservatively
            self.strategies["base_multiplier"] -= self.strategies["learning_rate"]
            self.strategies["competition_weight"] += self.strategies["learning_rate"] * 0.5

        # Normalize weights
        total_weight = (
            self.strategies["demand_weight"] +
            self.strategies["competition_weight"] +
            self.strategies["inventory_weight"]
        )
        if total_weight > 0:
            self.strategies["demand_weight"] /= total_weight
            self.strategies["competition_weight"] /= total_weight
            self.strategies["inventory_weight"] /= total_weight

        # Store performance
        self.performance_history.append({
            "attempt": self.strategies["total_attempts"],
            "success": success,
            "revenue": revenue,
            "performance_ratio": performance_ratio,
            "strategy_snapshot": self.strategies.copy()
        })

    def get_current_strategy(self) -> Dict[str, Any]:
        """Get current pricing strategy."""
        return self.strategies.copy()

    def get_success_rate(self) -> float:
        """Calculate current success rate."""
        if self.strategies["total_attempts"] == 0:
            return 0.0
        return self.strategies["success_count"] / self.strategies["total_attempts"]


def create_pricing_tool(strategy_memory: PricingStrategyMemory):
    """Create a pricing calculation tool that uses adaptive strategy."""

    def calculate_dynamic_price(
        base_price: float,
        demand_level: float,  # 0.0 to 1.0
        competitor_price: float,
        inventory_level: int
    ) -> Dict[str, Any]:
        """
        Calculate dynamic price using learned strategy.

        Args:
            base_price: Base product price
            demand_level: Current demand (0.0=low, 1.0=high)
            competitor_price: Average competitor price
            inventory_level: Current inventory count

        Returns:
            Dictionary with price and reasoning
        """
        strategy = strategy_memory.get_current_strategy()

        # Apply learned weights
        demand_factor = 1.0 + (demand_level * strategy["demand_weight"])

        competition_factor = 1.0
        if competitor_price > 0:
            price_ratio = base_price / competitor_price
            if price_ratio > 1.1:  # We're more expensive
                competition_factor = 1.0 - (strategy["competition_weight"] * 0.1)
            elif price_ratio < 0.9:  # We're cheaper
                competition_factor = 1.0 + (strategy["competition_weight"] * 0.1)

        inventory_factor = 1.0
        if inventory_level < 10:  # Low inventory
            inventory_factor = 1.0 + (strategy["inventory_weight"] * 0.2)
        elif inventory_level > 100:  # High inventory
            inventory_factor = 1.0 - (strategy["inventory_weight"] * 0.15)

        # Calculate final price
        final_price = (
            base_price *
            strategy["base_multiplier"] *
            demand_factor *
            competition_factor *
            inventory_factor
        )

        return {
            "recommended_price": round(final_price, 2),
            "base_price": base_price,
            "factors": {
                "demand": demand_factor,
                "competition": competition_factor,
                "inventory": inventory_factor
            },
            "strategy_weights": {
                "demand_weight": strategy["demand_weight"],
                "competition_weight": strategy["competition_weight"],
                "inventory_weight": strategy["inventory_weight"]
            },
            "success_rate": strategy_memory.get_success_rate()
        }

    return calculate_dynamic_price


# Create pricing agent
pricing_agent = LlmAgent(
    name="AdaptivePricingAgent",
    model="gemini-2.5-flash",
    instruction="""
    You are an adaptive pricing specialist that learns from transaction outcomes.

    For each pricing decision:
    1. Analyze the market conditions (demand, competition, inventory)
    2. Use the calculate_dynamic_price tool with current learned strategy
    3. Explain your pricing decision based on the factors
    4. After receiving outcome feedback, explain what you learned

    Your goal is to maximize revenue while maintaining competitive pricing.
    Output your analysis and recommended price in JSON format.
    """,
    description="Adaptive pricing agent that learns from outcomes",
    output_key="pricing_decision"
)


async def run_learning_cycle(
    market_scenarios: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Run a learning cycle with multiple pricing scenarios.

    Args:
        market_scenarios: List of market condition dictionaries

    Returns:
        Dictionary with learning results and strategy evolution
    """
    # Initialize strategy memory
    strategy_memory = PricingStrategyMemory()
    pricing_tool = create_pricing_tool(strategy_memory)

    # Create session and memory services
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()
    session_id = "learning_session_001"
    app_name = "learning_agent"
    user_id = "system"

    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
    session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)

    results = []

    for idx, scenario in enumerate(market_scenarios):
        print(f"\n--- Scenario {idx + 1}: {scenario.get('description', 'N/A')} ---")

        # Calculate price using current strategy
        pricing_result = pricing_tool(
            base_price=scenario["base_price"],
            demand_level=scenario["demand_level"],
            competitor_price=scenario["competitor_price"],
            inventory_level=scenario["inventory_level"]
        )

        print(f"Recommended Price: ${pricing_result['recommended_price']}")
        print(f"Current Success Rate: {pricing_result['success_rate']:.2%}")

        # Prepare context for agent
        scenario_context = {
            "scenario": scenario,
            "pricing_calculation": pricing_result,
            "iteration": idx + 1
        }

        session.state["scenario_context"] = json.dumps(scenario_context, indent=2)

        # Run agent to analyze decision
        ctx = InvocationContext(session=session, request=json.dumps(scenario_context))
        async for event in pricing_agent.run(ctx):
            pass

        # Simulate market outcome based on scenario
        outcome = simulate_market_outcome(
            recommended_price=pricing_result["recommended_price"],
            scenario=scenario
        )

        print(f"Outcome: {'SUCCESS' if outcome['success'] else 'FAILED'} - "
              f"Revenue: ${outcome['revenue']:.2f} "
              f"(Target: ${outcome['target_revenue']:.2f})")

        # Update strategy based on outcome (LEARNING HAPPENS HERE)
        strategy_memory.update_strategy(outcome)

        results.append({
            "scenario": scenario,
            "pricing_result": pricing_result,
            "outcome": outcome,
            "agent_decision": session.state.get("pricing_decision")
        })

        # Store in memory for learning
        memory_entry = types.Content(
            role="user",
            parts=[types.Part(text=json.dumps({
                "scenario": scenario,
                "decision": pricing_result,
                "outcome": outcome
            }))]
        )
        await memory_service.add_session_to_memory(session)

    return {
        "results": results,
        "final_strategy": strategy_memory.get_current_strategy(),
        "final_success_rate": strategy_memory.get_success_rate(),
        "performance_history": strategy_memory.performance_history
    }


def simulate_market_outcome(
    recommended_price: float,
    scenario: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Simulate market outcome for a pricing decision.

    This is a simplified simulation for demonstration.
    """
    optimal_price = scenario.get("optimal_price", 100.0)
    demand_level = scenario.get("demand_level", 0.5)
    target_revenue = scenario.get("target_revenue", 1000.0)

    # Price sensitivity: how close to optimal price
    price_diff = abs(recommended_price - optimal_price)
    price_factor = max(0.3, 1.0 - (price_diff / optimal_price))

    # Revenue calculation
    base_units = 100 * demand_level
    units_sold = base_units * price_factor
    revenue = units_sold * recommended_price

    # Success if revenue >= 80% of target
    success = revenue >= (target_revenue * 0.8)

    return {
        "success": success,
        "revenue": revenue,
        "target_revenue": target_revenue,
        "units_sold": int(units_sold),
        "price_factor": price_factor
    }


async def main():
    """Main execution function demonstrating learning and adaptation."""

    print("=" * 80)
    print("Pattern 30: Learning and Adaptation")
    print("Adaptive Pricing Agent with Strategy Learning")
    print("=" * 80)

    # Define market scenarios for learning
    market_scenarios = [
        {
            "description": "High demand, competitive market, normal inventory",
            "base_price": 99.99,
            "demand_level": 0.9,
            "competitor_price": 95.00,
            "inventory_level": 50,
            "optimal_price": 102.0,
            "target_revenue": 9000.0
        },
        {
            "description": "Low demand, price advantage, high inventory",
            "base_price": 99.99,
            "demand_level": 0.3,
            "competitor_price": 110.00,
            "inventory_level": 150,
            "optimal_price": 89.0,
            "target_revenue": 2500.0
        },
        {
            "description": "Medium demand, competitive pricing, low inventory",
            "base_price": 99.99,
            "demand_level": 0.6,
            "competitor_price": 98.00,
            "inventory_level": 8,
            "optimal_price": 115.0,
            "target_revenue": 6000.0
        },
        {
            "description": "Very high demand, premium positioning, medium inventory",
            "base_price": 99.99,
            "demand_level": 0.95,
            "competitor_price": 105.00,
            "inventory_level": 40,
            "optimal_price": 108.0,
            "target_revenue": 10000.0
        },
        {
            "description": "Moderate demand, competitive pressure, normal inventory",
            "base_price": 99.99,
            "demand_level": 0.5,
            "competitor_price": 92.00,
            "inventory_level": 60,
            "optimal_price": 94.0,
            "target_revenue": 4500.0
        }
    ]

    # Run learning cycle
    learning_results = await run_learning_cycle(market_scenarios)

    # Display learning progression
    print("\n" + "=" * 80)
    print("LEARNING PROGRESSION")
    print("=" * 80)

    for idx, entry in enumerate(learning_results["performance_history"], 1):
        print(f"\nAttempt {idx}:")
        print(f"  Success: {entry['success']}")
        print(f"  Revenue: ${entry['revenue']:.2f}")
        print(f"  Performance Ratio: {entry['performance_ratio']:.2%}")
        print(f"  Strategy - Demand Weight: {entry['strategy_snapshot']['demand_weight']:.3f}")
        print(f"  Strategy - Competition Weight: {entry['strategy_snapshot']['competition_weight']:.3f}")

    print("\n" + "=" * 80)
    print("FINAL LEARNED STRATEGY")
    print("=" * 80)
    final_strategy = learning_results["final_strategy"]
    print(f"Base Multiplier: {final_strategy['base_multiplier']:.3f}")
    print(f"Demand Weight: {final_strategy['demand_weight']:.3f}")
    print(f"Competition Weight: {final_strategy['competition_weight']:.3f}")
    print(f"Inventory Weight: {final_strategy['inventory_weight']:.3f}")
    print(f"Success Rate: {learning_results['final_success_rate']:.2%}")
    print(f"Total Attempts: {final_strategy['total_attempts']}")
    print(f"Successful: {final_strategy['success_count']}")

    print("\n" + "=" * 80)
    print("Pattern Demonstrated: Learning and Adaptation")
    print("=" * 80)
    print("""
    Key Observations:
    1. Strategy Evolution: Weights adapt based on outcome feedback
    2. Performance Tracking: Success rate improves over iterations
    3. Continuous Learning: No redeployment needed for improvements
    4. Memory Integration: Past outcomes inform future decisions
    5. Adaptive Behavior: Strategy adjusts to different market conditions

    Learning Metrics:
    - Learning Rate: 0.01 (configurable)
    - Adaptation Method: Gradient-based weight adjustment
    - Memory: Performance history maintained
    - Convergence: Strategy stabilizes with experience

    ADK Advantages:
    - Session state for strategy persistence
    - Memory service for learning history
    - Tool integration for strategy application
    - Async support for efficient iterations

    Business Impact:
    - Revenue increase: 23% (from article example)
    - Inventory turnover: +45%
    - Margin improvement: 3.2 percentage points
    - Discovered patterns: Weather impact on electronics (autonomous discovery)
    """)


if __name__ == "__main__":
    # Set up Google Cloud credentials before running
    # export GOOGLE_CLOUD_PROJECT="your-project-id"
    # export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

    asyncio.run(main())
