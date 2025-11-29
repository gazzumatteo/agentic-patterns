"""
Pattern 33: Self-Organizing Modular Agent
Dynamic assembly of specialized modules based on task requirements.

Business Example: Universal Customer Service
- Same system handles chat, email, voice, video
- 87% first-contact resolution across all channels
- Training cost: -90% (one system vs many)

This example demonstrates CrewAI's role-based modular architecture.

Mermaid Diagram Reference: See diagrams/33_modular_agent.mermaid
"""

from typing import Dict, Any, List
from crewai import Agent, Task, Crew, Process


class ModularCrewBuilder:
    """Builds custom crews from specialized agent modules."""

    def __init__(self):
        self.agent_modules = self._create_agent_modules()

    def _create_agent_modules(self) -> Dict[str, Dict[str, Agent]]:
        """Create library of specialized agent modules."""
        return {
            "perception": {
                "text": Agent(
                    role="Text Analyzer",
                    goal="Extract key information from text",
                    backstory="Expert at understanding written communication",
                    verbose=True
                ),
                "voice": Agent(
                    role="Voice Analyzer",
                    goal="Process audio and extract intent/emotion",
                    backstory="Specialist in voice communication analysis",
                    verbose=True
                ),
                "visual": Agent(
                    role="Visual Analyzer",
                    goal="Analyze images and screenshots",
                    backstory="Expert at visual problem identification",
                    verbose=True
                )
            },
            "memory": {
                "customer_history": Agent(
                    role="Customer History Specialist",
                    goal="Retrieve and contextualize customer history",
                    backstory="Maintains deep understanding of customer interactions",
                    verbose=True,
                    memory=True
                ),
                "product_knowledge": Agent(
                    role="Product Knowledge Expert",
                    goal="Access technical product documentation",
                    backstory="Master of product features and troubleshooting",
                    verbose=True,
                    memory=True
                )
            },
            "reasoning": {
                "technical": Agent(
                    role="Technical Problem Solver",
                    goal="Diagnose and resolve technical issues",
                    backstory="Expert troubleshooter with deep technical knowledge",
                    verbose=True
                ),
                "billing": Agent(
                    role="Billing Specialist",
                    goal="Resolve billing and payment issues",
                    backstory="Expert in financial calculations and refund policies",
                    verbose=True
                ),
                "general": Agent(
                    role="General Support Specialist",
                    goal="Handle general customer inquiries",
                    backstory="Versatile customer service professional",
                    verbose=True
                )
            },
            "action": {
                "response": Agent(
                    role="Response Generator",
                    goal="Create professional customer responses",
                    backstory="Expert at empathetic, clear communication",
                    verbose=True
                ),
                "escalation": Agent(
                    role="Escalation Manager",
                    goal="Route complex issues to appropriate teams",
                    backstory="Expert at triage and escalation procedures",
                    verbose=True
                )
            }
        }

    def select_configuration(self, request: Dict[str, Any]) -> List[Agent]:
        """Select agent configuration based on request characteristics."""
        selected_agents = []

        # Perception layer
        if "voice" in request.get("channels", []):
            selected_agents.append(self.agent_modules["perception"]["voice"])
        elif "image" in request.get("channels", []):
            selected_agents.append(self.agent_modules["perception"]["visual"])
        else:
            selected_agents.append(self.agent_modules["perception"]["text"])

        # Memory layer
        if request.get("type") == "technical":
            selected_agents.append(self.agent_modules["memory"]["product_knowledge"])
        else:
            selected_agents.append(self.agent_modules["memory"]["customer_history"])

        # Reasoning layer
        reasoning_type = request.get("type", "general")
        selected_agents.append(self.agent_modules["reasoning"].get(reasoning_type,
                                                                   self.agent_modules["reasoning"]["general"]))

        # Action layer
        if request.get("complexity", "low") == "high":
            selected_agents.append(self.agent_modules["action"]["escalation"])
        else:
            selected_agents.append(self.agent_modules["action"]["response"])

        return selected_agents

    def build_crew(self, request: Dict[str, Any]) -> Crew:
        """Build custom crew for specific request."""
        agents = self.select_configuration(request)

        # Create sequential tasks for each agent
        tasks = []
        for idx, agent in enumerate(agents):
            task = Task(
                description=f"""
                Process step {idx+1} of customer request:

                Request ID: {request.get('id')}
                Content: {request.get('content')}

                {"This is the perception step - extract key information." if idx == 0 else ""}
                {"This is the memory step - retrieve relevant context." if idx == 1 else ""}
                {"This is the reasoning step - determine solution." if idx == 2 else ""}
                {"This is the action step - generate final output." if idx == 3 else ""}

                Pass your output to the next stage.
                """,
                agent=agent,
                expected_output=f"Step {idx+1} output with key findings",
                context=tasks[-1:] if tasks else []
            )
            tasks.append(task)

        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )


def main():
    """Demonstrate self-organizing modular agent."""

    print("=" * 80)
    print("Pattern 33: Self-Organizing Modular Agent (CrewAI)")
    print("Dynamic Crew Assembly for Universal Customer Service")
    print("=" * 80)

    builder = ModularCrewBuilder()

    # Test scenarios
    scenarios = [
        {
            "id": "CS001",
            "type": "technical",
            "channels": ["text"],
            "complexity": "medium",
            "content": "My app keeps crashing when uploading photos"
        },
        {
            "id": "CS002",
            "type": "billing",
            "channels": ["voice"],
            "complexity": "low",
            "content": "I was charged twice for my subscription"
        },
        {
            "id": "CS003",
            "type": "general",
            "channels": ["image"],
            "complexity": "high",
            "content": "Error screenshot - can't access account"
        }
    ]

    for scenario in scenarios:
        print(f"\n\n{'='*80}")
        print(f"SCENARIO: {scenario['id']} - {scenario['type'].upper()}")
        print(f"{'='*80}")

        # Build custom crew
        crew = builder.build_crew(scenario)

        print(f"\n🔧 Assembled Crew Configuration:")
        for idx, agent in enumerate(crew.agents, 1):
            print(f"   {idx}. {agent.role}")

        # Execute
        print(f"\n▶ Processing request...")
        result = crew.kickoff()

        print(f"\n✓ Request Processed Successfully")
        print(f"   Agents Used: {len(crew.agents)}")
        print(f"   Tasks Completed: {len(crew.tasks)}")

    print("\n\n" + "=" * 80)
    print("Pattern Demonstrated: Self-Organizing Modular Agent")
    print("=" * 80)
    print("""
    Key Observations:
    1. Dynamic Assembly: Crew built per-request based on characteristics
    2. Role Specialization: Each module has specific expertise
    3. Sequential Flow: Information passes through specialized agents
    4. Reusable Modules: Same agents used in different combinations
    5. Scalable Design: Easy to add new specialized agents

    CrewAI Advantages:
    - Natural role-based architecture
    - Easy agent specialization
    - Built-in memory for context modules
    - Clear sequential processing
    - Intuitive task chaining

    Business Impact:
    - 87% first-contact resolution across all channels
    - Training cost: -90% (unified system)
    - Handles chat, email, voice, video with same platform
    - Specialized configuration per interaction type

    Applications:
    - Multi-channel customer support
    - Adaptive content pipelines
    - Configurable data analysis
    - Flexible automation systems
    """)


if __name__ == "__main__":
    main()
