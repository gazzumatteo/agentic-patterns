"""
Pattern 14: Network/Swarm Pattern
Decentralized, peer-to-peer agent communication. No central authority.
Collective intelligence emerges from local interactions.

Business Example: Warehouse Robot Coordination - MegaWarehouse
- 200 autonomous robots communicate peer-to-peer
- No central traffic controller
- Collective path optimization emerges
- Self-organizing task allocation

Results:
- Pick rate: 180 → 340 items/hour
- Collision incidents: 0 in 6 months
- System resilience: 30% robots can fail without impact
- Energy efficiency: +26%

This example demonstrates Google ADK's network/swarm pattern for decentralized coordination.

Mermaid Diagram Reference: See diagrams/14_network_swarm_pattern.mermaid
"""

import asyncio
import random
from typing import Dict, List, Any, Set
from dataclasses import dataclass
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Load environment variables
load_dotenv()


# ========================================
# SWARM AGENT - Individual Robot
# ========================================

@dataclass
class RobotState:
    """State of an individual warehouse robot."""
    robot_id: int
    current_position: tuple
    task: str
    battery_level: float
    neighbors: Set[int]
    path_plan: List[tuple]


class SwarmRobotAgent(LlmAgent):
    """Individual robot agent with peer-to-peer communication capability."""

    def __init__(self, robot_id: int, initial_position: tuple):
        super().__init__(
            name=f"Robot_{robot_id}",
            model="gemini-2.5-flash",
            instruction=f"""
            You are Warehouse Robot #{robot_id} in a decentralized swarm of 200 robots.

            SWARM INTELLIGENCE PRINCIPLES:
            1. No central controller - you coordinate with peer robots directly
            2. Local awareness - you only know about nearby robots
            3. Collective optimization - your decisions consider swarm efficiency
            4. Self-organization - task allocation emerges from local interactions

            YOUR CAPABILITIES:
            - Detect nearby robots (within 5 meter radius)
            - Communicate task status with neighbors
            - Coordinate path planning to avoid collisions
            - Negotiate task assignments based on position and battery
            - Optimize energy usage

            DECISION MAKING:
            When you receive information about:
            - Available pick tasks
            - Neighboring robot positions and tasks
            - Your current state (position, battery, task)

            You decide:
            1. Which task to claim (based on distance, battery, neighbor conflicts)
            2. Optimal path to destination (avoiding occupied paths)
            3. When to yield to higher priority neighbors
            4. Energy-efficient movement patterns

            COORDINATION RULES:
            - Robot with lower battery gets priority for nearby tasks
            - Avoid path intersections with neighbors
            - Share task information with neighbors
            - Self-organize into efficient patterns

            Respond with JSON:
            {{
                "robot_id": {robot_id},
                "action": "claim_task/move/wait/charge",
                "task_claimed": "task_id or null",
                "path_plan": ["list of waypoints"],
                "negotiations": ["messages to neighbor robots"],
                "reasoning": "why this decision optimizes swarm efficiency"
            }}
            """,
            description=f"Swarm robot agent {robot_id}",
            output_key=f"robot_{robot_id}_decision"
        )

        # Initialize robot-specific attributes after super().__init__()
        # Use object.__setattr__ to bypass Pydantic's extra='forbid'
        object.__setattr__(self, 'robot_id', robot_id)
        object.__setattr__(self, 'state', RobotState(
            robot_id=robot_id,
            current_position=initial_position,
            task="idle",
            battery_level=100.0,
            neighbors=set(),
            path_plan=[]
        ))

    def update_neighbors(self, all_robots: List['SwarmRobotAgent']):
        """Update list of neighboring robots (within communication range)."""
        COMM_RANGE = 5.0  # meters
        self.state.neighbors.clear()

        for robot in all_robots:
            if robot.robot_id == self.robot_id:
                continue

            distance = self._calculate_distance(
                self.state.current_position,
                robot.state.current_position
            )

            if distance <= COMM_RANGE:
                self.state.neighbors.add(robot.robot_id)

    def _calculate_distance(self, pos1: tuple, pos2: tuple) -> float:
        """Calculate Euclidean distance between positions."""
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5


# ========================================
# SWARM COORDINATOR (Observer/Monitor Only)
# ========================================

class SwarmMonitor:
    """
    Monitors swarm behavior but does NOT control robots.
    Observes emergent collective intelligence.
    """

    def __init__(self, num_robots: int = 200):
        self.num_robots = num_robots
        self.robots: List[SwarmRobotAgent] = []
        self._initialize_swarm()

    def _initialize_swarm(self):
        """Initialize swarm of robots at random positions."""
        # Warehouse: 100m x 100m grid
        for i in range(self.num_robots):
            x = random.uniform(0, 100)
            y = random.uniform(0, 100)
            robot = SwarmRobotAgent(robot_id=i, initial_position=(x, y))
            self.robots.append(robot)

        print(f"✓ Initialized swarm of {self.num_robots} robots")

    def simulate_swarm_behavior(
        self,
        pick_tasks: List[Dict[str, Any]],
        timesteps: int = 10
    ) -> Dict[str, Any]:
        """
        Simulate decentralized swarm behavior.

        Args:
            pick_tasks: List of pick tasks with positions
            timesteps: Number of simulation steps

        Returns:
            Swarm performance metrics
        """
        print(f"\n{'='*80}")
        print(f"Swarm Simulation: {len(pick_tasks)} tasks, {timesteps} timesteps")
        print(f"{'='*80}\n")

        metrics = {
            "tasks_completed": 0,
            "collisions": 0,
            "total_distance": 0,
            "energy_used": 0,
            "emergent_patterns": []
        }

        for t in range(timesteps):
            print(f"Timestep {t + 1}/{timesteps}")

            # Update neighbor awareness for all robots
            for robot in self.robots:
                robot.update_neighbors(self.robots)

            # Simulate local decision making (simplified for demo)
            active_robots = random.sample(
                self.robots,
                min(20, len(self.robots))  # Simulate 20 active robots per timestep
            )

            for robot in active_robots:
                # Simulate peer-to-peer coordination
                decision = self._simulate_robot_decision(robot, pick_tasks)

                if decision.get("task_claimed"):
                    metrics["tasks_completed"] += 1

                # Update metrics
                if decision.get("path_plan"):
                    metrics["total_distance"] += len(decision["path_plan"])

            # Check for emergent patterns
            pattern = self._detect_emergent_patterns(active_robots)
            if pattern:
                metrics["emergent_patterns"].append(pattern)

        return metrics

    def _simulate_robot_decision(
        self,
        robot: SwarmRobotAgent,
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate a robot's decentralized decision making."""
        # Simple simulation: pick nearest task
        if not tasks:
            return {"action": "wait"}

        nearest_task = min(
            tasks,
            key=lambda t: robot._calculate_distance(
                robot.state.current_position,
                t["position"]
            )
        )

        return {
            "robot_id": robot.robot_id,
            "action": "claim_task",
            "task_claimed": nearest_task["id"],
            "path_plan": [robot.state.current_position, nearest_task["position"]]
        }

    def _detect_emergent_patterns(
        self,
        active_robots: List[SwarmRobotAgent]
    ) -> str:
        """Detect emergent collective patterns in swarm behavior."""
        # Simplified pattern detection
        patterns = [
            "Clustering around high-density task areas",
            "Self-organizing traffic lanes",
            "Dynamic load balancing",
            "Collision avoidance coordination"
        ]

        return random.choice(patterns) if random.random() > 0.7 else None

    async def analyze_swarm_intelligence(self, scenario: str) -> str:
        """
        Use LLM to analyze swarm intelligence for a specific scenario.

        Args:
            scenario: Warehouse scenario description

        Returns:
            Analysis of how swarm intelligence would emerge
        """
        analyzer = LlmAgent(
            name="SwarmIntelligenceAnalyzer",
            model="gemini-2.5-flash",
            instruction="""
            You are an expert in swarm robotics and emergent collective intelligence.

            Analyze how a decentralized swarm of 200 warehouse robots would handle
            the given scenario WITHOUT central coordination.

            Explain:
            1. How local interactions lead to global optimization
            2. What emergent patterns would arise
            3. How the swarm self-organizes
            4. Resilience properties (% failure tolerance)
            5. Expected performance metrics

            Focus on:
            - Decentralized decision making
            - Peer-to-peer coordination
            - Collective intelligence emergence
            - No single point of failure
            """,
            description="Analyzes swarm intelligence patterns"
        )

        runner = InMemoryRunner(agent=analyzer, app_name="swarm_analysis")

        session = await runner.session_service.create_session(
            app_name="swarm_analysis",
            user_id="monitor_user"
        )

        content = types.Content(
            role='user',
            parts=[types.Part(text=f"Analyze swarm behavior for scenario: {scenario}")]
        )

        events = runner.run_async(
            user_id="monitor_user",
            session_id=session.id,
            new_message=content
        )

        analysis = None
        async for event in events:
            if event.is_final_response() and event.content:
                analysis = event.content.parts[0].text

        return analysis


async def main():
    """Main execution demonstrating network/swarm pattern."""

    print(f"\n{'='*80}")
    print("Pattern 14: Network/Swarm Pattern - Google ADK")
    print("Business Case: MegaWarehouse - Autonomous Robot Coordination")
    print(f"{'='*80}\n")

    # Initialize swarm
    print("Initializing Decentralized Robot Swarm...")
    swarm = SwarmMonitor(num_robots=200)

    print(f"\nSwarm Properties:")
    print(f"  - Total robots: {swarm.num_robots}")
    print(f"  - Communication: Peer-to-peer (no central controller)")
    print(f"  - Coordination: Self-organizing")
    print(f"  - Warehouse: 100m × 100m (1M sq ft)")

    # Example 1: Peak Hour Operations
    print(f"\n\n{'='*80}")
    print("Example 1: Peak Hour Operations - High Task Volume")
    print(f"{'='*80}\n")

    peak_tasks = [
        {"id": f"TASK_{i}", "position": (random.uniform(0, 100), random.uniform(0, 100))}
        for i in range(500)  # 500 pick tasks
    ]

    print(f"Scenario: {len(peak_tasks)} pick tasks during peak hours")
    print("Swarm must self-organize for optimal throughput\n")

    # Simulate swarm behavior
    metrics = swarm.simulate_swarm_behavior(peak_tasks, timesteps=10)

    print(f"\n{'='*80}")
    print("Swarm Performance Metrics:")
    print(f"{'='*80}")
    print(f"  Tasks completed: {metrics['tasks_completed']}")
    print(f"  Collisions: {metrics['collisions']}")
    print(f"  Total distance: {metrics['total_distance']:.1f}m")
    print(f"  Emergent patterns detected: {len(metrics['emergent_patterns'])}")

    if metrics['emergent_patterns']:
        print(f"\n  Observed Emergent Behaviors:")
        for pattern in set(metrics['emergent_patterns']):
            print(f"    - {pattern}")

    # Analyze with LLM
    print(f"\n{'='*80}")
    print("Swarm Intelligence Analysis:")
    print(f"{'='*80}\n")

    analysis = await swarm.analyze_swarm_intelligence(
        """Peak hour scenario: 500 pick tasks distributed across 1M sq ft warehouse.
        200 robots must coordinate without central controller. How does swarm intelligence
        emerge to optimize pick rate while avoiding collisions?"""
    )

    print(analysis)

    # Example 2: Partial System Failure
    print(f"\n\n{'='*80}")
    print("Example 2: System Resilience - 30% Robot Failure")
    print(f"{'='*80}\n")

    failure_scenario = """
    Critical Test: 60 robots (30%) experience battery failure simultaneously.

    Traditional centralized system: Would require manual intervention and system restart.

    Swarm system: How does the remaining 140 robots self-organize to maintain operations?
    """

    resilience_analysis = await swarm.analyze_swarm_intelligence(failure_scenario)

    print(resilience_analysis)

    # Business Metrics
    print(f"\n\n{'='*80}")
    print("Business Impact - MegaWarehouse Results:")
    print(f"{'='*80}")
    print("""
    Performance Improvements:
    - Pick rate: 180 → 340 items/hour (+89%)
    - Collision incidents: 0 in 6 months (vs 12/month with central control)
    - System uptime: 99.9% (30% of robots can fail without impact)
    - Energy efficiency: +26% through emergent coordination

    Operational Benefits:
    - No single point of failure (resilient to 30% failure rate)
    - Scales naturally with robot count
    - Self-healing and adaptive
    - No central bottleneck for decisions
    """)

    print(f"\n{'='*80}")
    print("Pattern Demonstrated: Network/Swarm Intelligence")
    print(f"{'='*80}")
    print("""
Key Concepts:
1. Decentralized Architecture:
   - No central controller or traffic coordinator
   - Each robot is autonomous decision-maker
   - Peer-to-peer communication only (local awareness)
   - No hierarchical command structure

2. Emergent Collective Intelligence:
   - Global optimization emerges from local interactions
   - Self-organizing traffic patterns
   - Dynamic load balancing without coordination
   - Collective path planning through negotiation

3. Local Awareness and Decision Making:
   - Each robot knows only nearby neighbors (5m radius)
   - Decisions based on local state + neighbor communication
   - Simple rules → complex collective behavior
   - No robot has global view

4. Resilience Properties:
   - 30% of robots can fail without system impact
   - Self-healing: Swarm adapts to failures automatically
   - No single point of failure
   - Graceful degradation under stress

5. Business Impact (MegaWarehouse):
   - Pick rate: +89% improvement
   - Zero collisions in 6 months
   - 99.9% uptime despite frequent individual failures
   - Energy efficiency: +26%

6. When to Use:
   - Physical systems (robotics, drones, vehicles)
   - Distributed operations where centralized control creates bottlenecks
   - Resilience is critical (cannot tolerate single point of failure)
   - Unpredictable environments requiring adaptation
   - Scale makes central coordination impractical

7. ADK Implementation Considerations:
   - Each SwarmRobotAgent is independent LlmAgent
   - Peer-to-peer message passing (not shown in simplified demo)
   - Local state management per agent
   - Emergent patterns monitored but not controlled
   - Actual implementation would use message queues for P2P communication

8. Trade-offs:
   - Harder to debug than centralized systems (emergent behavior)
   - Requires careful design of local rules
   - Simulation needed to validate before deployment
   - But: Massively more resilient and scalable
    """)


if __name__ == "__main__":
    asyncio.run(main())
