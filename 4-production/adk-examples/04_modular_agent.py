"""
Pattern 33: Self-Organizing Modular Agent
Dynamic assembly of specialized modules based on task requirements. One
platform, infinite configurations through composable intelligence.

Business Example: Universal Customer Service
- Perception modules: Text, voice, image understanding
- Memory modules: Customer history, product knowledge
- Reasoning modules: Technical, billing, emotional support
- Action modules: Response generation, ticket creation, escalation

This example demonstrates Google ADK's modular architecture with dynamic
module selection and composition.

Mermaid Diagram Reference: See diagrams/33_modular_agent.mermaid
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.agents.invocation_context import InvocationContext


class ModuleRegistry:
    """Registry of available agent modules."""

    def __init__(self):
        self.perception_modules = {}
        self.memory_modules = {}
        self.reasoning_modules = {}
        self.action_modules = {}

    def register_perception(self, name: str, agent: LlmAgent):
        self.perception_modules[name] = agent

    def register_memory(self, name: str, agent: LlmAgent):
        self.memory_modules[name] = agent

    def register_reasoning(self, name: str, agent: LlmAgent):
        self.reasoning_modules[name] = agent

    def register_action(self, name: str, agent: LlmAgent):
        self.action_modules[name] = agent

    def get_available_modules(self) -> Dict[str, List[str]]:
        return {
            "perception": list(self.perception_modules.keys()),
            "memory": list(self.memory_modules.keys()),
            "reasoning": list(self.reasoning_modules.keys()),
            "action": list(self.action_modules.keys())
        }


class MetaController:
    """Controls dynamic module selection and assembly."""

    def __init__(self, registry: ModuleRegistry):
        self.registry = registry

    def analyze_task(self, task: Dict[str, Any]) -> Dict[str, str]:
        """Determine which modules are needed for a task."""
        task_type = task.get("type", "unknown")
        channels = task.get("channels", [])
        complexity = task.get("complexity", "medium")

        # Simple rule-based selection (in production, could use LLM)
        config = {}

        # Perception
        if "voice" in channels:
            config["perception"] = "audio_processor"
        elif "image" in channels:
            config["perception"] = "vision_processor"
        else:
            config["perception"] = "text_processor"

        # Memory
        if task_type == "technical":
            config["memory"] = "product_knowledge"
        else:
            config["memory"] = "customer_history"

        # Reasoning
        if task_type == "technical":
            config["reasoning"] = "technical_reasoning"
        elif task_type == "billing":
            config["reasoning"] = "financial_reasoning"
        else:
            config["reasoning"] = "general_reasoning"

        # Action
        if complexity == "high":
            config["action"] = "escalation_handler"
        else:
            config["action"] = "response_generator"

        return config

    def assemble_agent(
        self,
        module_config: Dict[str, str]
    ) -> SequentialAgent:
        """Dynamically assemble an agent from modules."""
        selected_modules = []

        for module_type, module_name in module_config.items():
            if module_type == "perception":
                module = self.registry.perception_modules.get(module_name)
            elif module_type == "memory":
                module = self.registry.memory_modules.get(module_name)
            elif module_type == "reasoning":
                module = self.registry.reasoning_modules.get(module_name)
            elif module_type == "action":
                module = self.registry.action_modules.get(module_name)
            else:
                continue

            if module:
                selected_modules.append(module)

        return SequentialAgent(
            name="DynamicAssembledAgent",
            sub_agents=selected_modules
        )


# Create module registry
registry = ModuleRegistry()

# Perception Modules
text_processor = LlmAgent(
    name="TextPerception",
    model="gemini-2.5-flash",
    instruction="Extract key information from text input. Output structured JSON.",
    output_key="perceived_data"
)

audio_processor = LlmAgent(
    name="AudioPerception",
    model="gemini-2.5-flash",
    instruction="Process audio/voice input. Extract intent and emotion. Output JSON.",
    output_key="perceived_data"
)

vision_processor = LlmAgent(
    name="VisionPerception",
    model="gemini-2.5-flash",
    instruction="Analyze visual input (images/screenshots). Identify issues. Output JSON.",
    output_key="perceived_data"
)

# Memory Modules
customer_history = LlmAgent(
    name="CustomerHistoryMemory",
    model="gemini-2.5-flash",
    instruction="Retrieve customer interaction history. Output relevant context.",
    output_key="memory_context"
)

product_knowledge = LlmAgent(
    name="ProductKnowledgeMemory",
    model="gemini-2.5-flash",
    instruction="Retrieve product technical documentation. Output relevant knowledge.",
    output_key="memory_context"
)

# Reasoning Modules
technical_reasoning = LlmAgent(
    name="TechnicalReasoning",
    model="gemini-2.5-flash",
    instruction="Apply technical troubleshooting logic. Diagnose issues. Output solution.",
    output_key="reasoning_result"
)

financial_reasoning = LlmAgent(
    name="FinancialReasoning",
    model="gemini-2.5-flash",
    instruction="Apply billing/financial logic. Calculate adjustments. Output resolution.",
    output_key="reasoning_result"
)

general_reasoning = LlmAgent(
    name="GeneralReasoning",
    model="gemini-2.5-flash",
    instruction="Apply general customer service logic. Determine best response.",
    output_key="reasoning_result"
)

# Action Modules
response_generator = LlmAgent(
    name="ResponseGenerator",
    model="gemini-2.5-flash",
    instruction="Generate customer-facing response. Professional and empathetic.",
    output_key="final_response"
)

escalation_handler = LlmAgent(
    name="EscalationHandler",
    model="gemini-2.5-flash",
    instruction="Create escalation ticket with all context. Route to appropriate team.",
    output_key="final_response"
)

# Register modules
registry.register_perception("text_processor", text_processor)
registry.register_perception("audio_processor", audio_processor)
registry.register_perception("vision_processor", vision_processor)
registry.register_memory("customer_history", customer_history)
registry.register_memory("product_knowledge", product_knowledge)
registry.register_reasoning("technical_reasoning", technical_reasoning)
registry.register_reasoning("financial_reasoning", financial_reasoning)
registry.register_reasoning("general_reasoning", general_reasoning)
registry.register_action("response_generator", response_generator)
registry.register_action("escalation_handler", escalation_handler)


async def handle_customer_request(
    request: Dict[str, Any],
    controller: MetaController
) -> Dict[str, Any]:
    """Handle customer request with dynamically assembled agent."""

    # Analyze task and select modules
    module_config = controller.analyze_task(request)

    print(f"\n📋 Task Analysis:")
    print(f"   Type: {request.get('type')}")
    print(f"   Channel: {request.get('channels')}")
    print(f"   Complexity: {request.get('complexity')}")

    print(f"\n🔧 Selected Modules:")
    for module_type, module_name in module_config.items():
        print(f"   {module_type.title()}: {module_name}")

    # Assemble agent dynamically
    assembled_agent = controller.assemble_agent(module_config)

    # Execute assembled agent
    session_service = InMemorySessionService()
    session_id = f"session_{request.get('id', '001')}"
    app_name = "modular_agent"
    user_id = "system"
    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
    session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    session.state["request"] = json.dumps(request)

    ctx = InvocationContext(
        session=session,
        request=request.get("content", "")
    )

    async for event in assembled_agent.run(ctx):
        pass

    return {
        "request_id": request.get("id"),
        "module_config": module_config,
        "perceived_data": session.state.get("perceived_data"),
        "memory_context": session.state.get("memory_context"),
        "reasoning_result": session.state.get("reasoning_result"),
        "final_response": session.state.get("final_response")
    }


async def main():
    """Main execution demonstrating modular agent."""

    print("=" * 80)
    print("Pattern 33: Self-Organizing Modular Agent")
    print("Dynamic Module Assembly for Universal Customer Service")
    print("=" * 80)

    controller = MetaController(registry)

    # Show available modules
    available = registry.get_available_modules()
    print(f"\n📦 Available Modules:")
    for module_type, modules in available.items():
        print(f"   {module_type.title()}: {', '.join(modules)}")

    # Test scenarios with different configurations
    scenarios = [
        {
            "id": "CS001",
            "type": "technical",
            "channels": ["text"],
            "complexity": "medium",
            "content": "My app keeps crashing when I try to upload photos"
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
            "content": "Screenshot of error message - can't login"
        }
    ]

    for scenario in scenarios:
        print(f"\n\n{'='*80}")
        print(f"SCENARIO: {scenario['id']}")
        print(f"{'='*80}")

        result = await handle_customer_request(scenario, controller)

        print(f"\n✓ Request Processed")
        print(f"   Configuration: {list(result['module_config'].values())}")
        print(f"   Response Generated: {result['final_response'] is not None}")

    print("\n\n" + "=" * 80)
    print("Pattern Demonstrated: Self-Organizing Modular Agent")
    print("=" * 80)
    print("""
    Key Observations:
    1. Dynamic Assembly: Agents composed on-demand based on task
    2. Module Reusability: Same modules used in different combinations
    3. Scalability: Add new modules without changing core architecture
    4. Flexibility: Infinite configurations from fixed module set
    5. Efficiency: Only load/use needed capabilities

    Modular Architecture:
    - Perception Layer: Text, voice, vision processing
    - Memory Layer: Customer history, product knowledge
    - Reasoning Layer: Technical, financial, general logic
    - Action Layer: Response generation, escalation

    ADK Implementation:
    - Module Registry: Central module management
    - Meta Controller: Intelligent module selection
    - Sequential Agent: Dynamic pipeline assembly
    - State Management: Context flow between modules

    Business Impact (from article):
    - 87% first-contact resolution across all channels
    - Training cost: -90% (one system vs many specialists)
    - Same system handles chat, email, voice, video
    - Specialized configuration per interaction

    Applications:
    - Multi-channel customer service
    - Adaptive data analysis pipelines
    - Configurable content generation
    - Flexible automation workflows
    """)


if __name__ == "__main__":
    asyncio.run(main())
