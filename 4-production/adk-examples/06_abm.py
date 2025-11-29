"""
Pattern 35: Agent-Based Modeling (ABM)
Simulates complex systems through interacting agents. Reveals emergent
behaviors and non-obvious system dynamics.

Business Example: Supply Chain Resilience (GlobalAuto)
- 10,000 agents: suppliers, plants, distributors
- Simulate disruption scenarios (port closure, chip shortage)
- Measure cascade effects and recovery time
- Result: Prevented $200M loss during actual disruption

This example demonstrates Google ADK for multi-agent simulation systems.

Mermaid Diagram Reference: See diagrams/35_agent_based_modeling.mermaid
"""

import asyncio
import json
import random
from typing import Dict, List, Any
from dataclasses import dataclass
from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.sessions import InMemorySessionService
from google.adk.agents.invocation_context import InvocationContext


@dataclass
class AgentState:
    """State of a supply chain agent."""
    id: str
    type: str  # supplier, manufacturer, distributor
    inventory: int
    capacity: int
    operational: bool
    connections: List[str]


class SupplyChainSimulation:
    """ABM simulation for supply chain."""

    def __init__(self):
        self.agents: Dict[str, AgentState] = {}
        self.time_step = 0
        self.disruption_log: List[Dict] = []

    def create_supply_chain(self) -> None:
        """Create network of supply chain agents."""
        # 20 suppliers
        for i in range(20):
            self.agents[f"supplier_{i}"] = AgentState(
                id=f"supplier_{i}",
                type="supplier",
                inventory=random.randint(80, 120),
                capacity=100,
                operational=True,
                connections=[]
            )

        # 5 manufacturers
        for i in range(5):
            # Connect to random suppliers
            supplier_connections = random.sample(
                [f"supplier_{j}" for j in range(20)],
                k=4
            )
            self.agents[f"mfg_{i}"] = AgentState(
                id=f"mfg_{i}",
                type="manufacturer",
                inventory=random.randint(40, 60),
                capacity=50,
                operational=True,
                connections=supplier_connections
            )

        # 10 distributors
        for i in range(10):
            # Connect to random manufacturers
            mfg_connections = random.sample(
                [f"mfg_{j}" for j in range(5)],
                k=2
            )
            self.agents[f"dist_{i}"] = AgentState(
                id=f"dist_{i}",
                type="distributor",
                inventory=random.randint(20, 40),
                capacity=30,
                operational=True,
                connections=mfg_connections
            )

    def inject_disruption(self, disruption: Dict[str, Any]) -> None:
        """Inject disruption into simulation."""
        if disruption["type"] == "supplier_failure":
            target_id = disruption["target"]
            if target_id in self.agents:
                self.agents[target_id].operational = False
                self.disruption_log.append({
                    "time_step": self.time_step,
                    "event": f"{target_id} disrupted",
                    "type": disruption["type"]
                })

    def simulate_step(self) -> Dict[str, Any]:
        """Simulate one time step."""
        self.time_step += 1
        cascade_effects = []

        # Suppliers try to maintain inventory
        for agent_id, agent in self.agents.items():
            if agent.type == "supplier" and agent.operational:
                # Replenish inventory
                agent.inventory = min(agent.inventory + 10, agent.capacity)

        # Manufacturers consume supplier inventory
        for agent_id, agent in self.agents.items():
            if agent.type == "manufacturer" and agent.operational:
                # Try to get supplies
                supplies_available = True
                for supplier_id in agent.connections:
                    supplier = self.agents[supplier_id]
                    if not supplier.operational or supplier.inventory < 10:
                        supplies_available = False
                        cascade_effects.append({
                            "affected": agent_id,
                            "cause": supplier_id,
                            "time": self.time_step
                        })

                if supplies_available:
                    # Consume supplies and produce
                    for supplier_id in agent.connections:
                        self.agents[supplier_id].inventory -= 10
                    agent.inventory = min(agent.inventory + 5, agent.capacity)
                else:
                    # Can't produce
                    agent.inventory = max(0, agent.inventory - 2)

        # Distributors consume manufacturer inventory
        for agent_id, agent in self.agents.items():
            if agent.type == "distributor" and agent.operational:
                supplies_available = True
                for mfg_id in agent.connections:
                    mfg = self.agents[mfg_id]
                    if not mfg.operational or mfg.inventory < 5:
                        supplies_available = False
                        cascade_effects.append({
                            "affected": agent_id,
                            "cause": mfg_id,
                            "time": self.time_step
                        })

                if supplies_available:
                    for mfg_id in agent.connections:
                        self.agents[mfg_id].inventory -= 5
                    agent.inventory = min(agent.inventory + 3, agent.capacity)

        return {
            "time_step": self.time_step,
            "cascade_effects": cascade_effects,
            "operational_count": sum(1 for a in self.agents.values() if a.operational),
            "total_inventory": sum(a.inventory for a in self.agents.values())
        }

    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics."""
        total_agents = len(self.agents)
        operational = sum(1 for a in self.agents.values() if a.operational)
        total_inventory = sum(a.inventory for a in self.agents.values())
        avg_inventory = total_inventory / total_agents

        return {
            "operational_percentage": operational / total_agents * 100,
            "total_inventory": total_inventory,
            "avg_inventory": avg_inventory,
            "time_step": self.time_step
        }


# Analysis agent
analysis_agent = LlmAgent(
    name="SimulationAnalyzer",
    model="gemini-2.5-flash",
    instruction="""
    You are a supply chain resilience analyst.

    Analyze simulation results and identify:
    1. Cascade effects from disruptions
    2. Critical points of failure
    3. Recovery patterns
    4. System vulnerabilities
    5. Recommended mitigation strategies

    Provide clear, actionable insights.
    """,
    description="Analyzes ABM simulation results",
    output_key="analysis"
)


async def run_disruption_scenario(
    scenario_name: str,
    disruption: Dict[str, Any],
    duration: int = 20
) -> Dict[str, Any]:
    """Run simulation with disruption scenario."""

    sim = SupplyChainSimulation()
    sim.create_supply_chain()

    print(f"\n{'='*80}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'='*80}")

    initial_health = sim.get_system_health()
    print(f"\n📊 Initial System Health:")
    print(f"   Operational: {initial_health['operational_percentage']:.1f}%")
    print(f"   Total Inventory: {initial_health['total_inventory']}")

    # Run pre-disruption steps
    for _ in range(5):
        sim.simulate_step()

    # Inject disruption
    print(f"\n⚠️  DISRUPTION: {disruption['type']}")
    sim.inject_disruption(disruption)

    # Track metrics
    metrics_history = []

    # Run post-disruption simulation
    for step in range(duration):
        step_result = sim.simulate_step()
        health = sim.get_system_health()
        metrics_history.append(health)

        if step % 5 == 0:
            print(f"\n   Step {step + 6}: "
                  f"Operational {health['operational_percentage']:.0f}%, "
                  f"Inventory {health['total_inventory']}")

    final_health = sim.get_system_health()

    # Agent analysis
    session_service = InMemorySessionService()
    session_id = "abm_analysis"
    app_name = "abm_agent"
    user_id = "system"
    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
    session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)

    session.state["simulation_data"] = json.dumps({
        "scenario": scenario_name,
        "disruption": disruption,
        "initial_health": initial_health,
        "final_health": final_health,
        "disruption_log": sim.disruption_log,
        "cascade_count": len([m for m in metrics_history if m.get("cascade_effects")])
    })

    ctx = InvocationContext(
        session=session,
        request="Analyze simulation results and provide insights"
    )

    async for event in analysis_agent.run(ctx):
        pass

    return {
        "scenario": scenario_name,
        "initial_health": initial_health,
        "final_health": final_health,
        "metrics_history": metrics_history,
        "analysis": session.state.get("analysis"),
        "disruption_log": sim.disruption_log
    }


async def main():
    """Main execution demonstrating ABM."""

    print("=" * 80)
    print("Pattern 35: Agent-Based Modeling (ABM)")
    print("Supply Chain Resilience Simulation")
    print("=" * 80)

    scenarios = [
        {
            "name": "Single Supplier Failure",
            "disruption": {"type": "supplier_failure", "target": "supplier_5"},
            "duration": 15
        },
        {
            "name": "Major Supplier Disruption",
            "disruption": {"type": "supplier_failure", "target": "supplier_0"},
            "duration": 20
        }
    ]

    results = []

    for scenario in scenarios:
        result = await run_disruption_scenario(
            scenario["name"],
            scenario["disruption"],
            scenario["duration"]
        )
        results.append(result)

        impact = ((result["initial_health"]["operational_percentage"] -
                  result["final_health"]["operational_percentage"]))

        print(f"\n📊 Impact Analysis:")
        print(f"   Operational Impact: {impact:.1f}% reduction")
        print(f"   Inventory Impact: "
              f"{result['initial_health']['total_inventory'] - result['final_health']['total_inventory']} units")

    print("\n\n" + "=" * 80)
    print("Pattern Demonstrated: Agent-Based Modeling")
    print("=" * 80)
    print("""
    Key Observations:
    1. Emergent Behavior: System-level patterns from individual agents
    2. Cascade Effects: Disruptions propagate through network
    3. Non-Obvious Dynamics: ABM reveals hidden vulnerabilities
    4. Scenario Testing: Safe virtual testing of disruptions
    5. Strategic Insights: Identifies critical nodes and mitigation

    ABM Components:
    - Agent States: Inventory, capacity, operational status
    - Agent Interactions: Supply/demand relationships
    - Network Topology: Connection patterns
    - Disruption Injection: Simulated failures
    - Emergent Metrics: System-level health

    Business Impact (from article):
    - Identified 3 critical single points of failure
    - Optimal inventory buffer: 18 days (was 30)
    - Dual-sourcing for 12 components
    - Prevented $200M loss during actual disruption

    Applications:
    - Supply chain resilience
    - Market dynamics simulation
    - Epidemic modeling
    - Traffic flow optimization
    - Financial system stress testing
    """)


if __name__ == "__main__":
    asyncio.run(main())
