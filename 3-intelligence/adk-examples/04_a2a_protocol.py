"""
Pattern 22: Inter-Agent Communication (A2A) - Google ADK Implementation

Protocol for agents built with different frameworks to communicate. Enables
heterogeneous agent ecosystems.

Business Example: OmniChannel Corp
- Integration time: 2 days → 2 hours per agent
- Vendor lock-in: Eliminated
- Innovation speed: 3x faster
- System flexibility: Mix best tools for each job

Mermaid Diagram Reference: diagrams/pattern-22-a2a.mmd
Medium Article: Part 3 - Governance and Reliability Patterns
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai.types import GenerateContentConfig
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

load_dotenv()
console = Console()


class AgentFramework(Enum):
    """Supported agent frameworks."""
    GOOGLE_ADK = "google_adk"
    CREWAI = "crewai"
    LANGCHAIN = "langchain"
    CUSTOM_PYTHON = "custom_python"


class MessageType(Enum):
    """A2A message types."""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"


@dataclass
class A2AMessage:
    """Standardized A2A protocol message."""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    timestamp: datetime
    payload: Dict[str, Any]
    conversation_id: Optional[str] = None


@dataclass
class AgentCapability:
    """Agent capability definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


class MessageBus:
    """Central message bus for A2A communication."""

    def __init__(self):
        self.messages: List[A2AMessage] = []
        self.agents: Dict[str, 'A2AAgent'] = {}
        console.print("[green]✓[/green] Message Bus initialized")

    def register_agent(self, agent: 'A2AAgent') -> None:
        """Register an agent with the message bus."""
        self.agents[agent.agent_id] = agent
        console.print(f"[green]✓[/green] Registered agent: {agent.agent_id} ({agent.framework.value})")

    async def send_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Route message to recipient agent."""
        self.messages.append(message)

        console.print(
            f"[cyan]→[/cyan] {message.sender_id} → {message.receiver_id}: "
            f"{message.message_type.value}"
        )

        # Route to recipient
        if message.receiver_id in self.agents:
            recipient = self.agents[message.receiver_id]
            response = await recipient.receive_message(message)
            return response
        else:
            console.print(f"[red]Agent {message.receiver_id} not found[/red]")
            return None

    def get_message_history(self) -> List[A2AMessage]:
        """Get complete message history."""
        return self.messages


class A2AAgent:
    """Base class for A2A-compatible agents."""

    def __init__(
        self,
        agent_id: str,
        framework: AgentFramework,
        capabilities: List[AgentCapability],
        message_bus: MessageBus
    ):
        self.agent_id = agent_id
        self.framework = framework
        self.capabilities = capabilities
        self.message_bus = message_bus

        # Register with message bus
        message_bus.register_agent(self)

    async def receive_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Handle incoming A2A message."""
        raise NotImplementedError("Subclasses must implement receive_message")

    async def send_message(
        self,
        receiver_id: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> Optional[A2AMessage]:
        """Send A2A message to another agent."""
        message = A2AMessage(
            message_id=f"msg_{datetime.now().timestamp()}",
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            timestamp=datetime.now(),
            payload=payload,
            conversation_id=conversation_id
        )

        return await self.message_bus.send_message(message)


class ADKInventoryAgent(A2AAgent):
    """ADK-based inventory management agent."""

    def __init__(self, message_bus: MessageBus):
        super().__init__(
            agent_id="adk_inventory_agent",
            framework=AgentFramework.GOOGLE_ADK,
            capabilities=[
                AgentCapability(
                    name="check_inventory",
                    description="Check product inventory levels",
                    input_schema={"product_id": "string"},
                    output_schema={"quantity": "number", "available": "boolean"}
                )
            ],
            message_bus=message_bus
        )

        # Create ADK agent
        self.llm_agent = LlmAgent(
    name="LlmAgent",
    model="gemini-2.5-flash"
        )

        # Simulated inventory
        self.inventory = {
            "PROD-001": {"quantity": 150, "reserved": 20},
            "PROD-002": {"quantity": 75, "reserved": 10},
            "PROD-003": {"quantity": 0, "reserved": 0}
        }

    async def receive_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Handle inventory requests."""
        if message.message_type == MessageType.REQUEST:
            action = message.payload.get("action")

            if action == "check_inventory":
                product_id = message.payload.get("product_id")
                inventory_data = self.inventory.get(product_id, {"quantity": 0, "reserved": 0})

                available = inventory_data["quantity"] - inventory_data["reserved"]

                response_payload = {
                    "product_id": product_id,
                    "quantity": inventory_data["quantity"],
                    "available": available,
                    "status": "in_stock" if available > 0 else "out_of_stock"
                }

                return A2AMessage(
                    message_id=f"msg_{datetime.now().timestamp()}",
                    sender_id=self.agent_id,
                    receiver_id=message.sender_id,
                    message_type=MessageType.RESPONSE,
                    timestamp=datetime.now(),
                    payload=response_payload,
                    conversation_id=message.conversation_id
                )

        return None


class CustomPythonPricingAgent(A2AAgent):
    """Custom Python pricing agent (legacy system)."""

    def __init__(self, message_bus: MessageBus):
        super().__init__(
            agent_id="python_pricing_agent",
            framework=AgentFramework.CUSTOM_PYTHON,
            capabilities=[
                AgentCapability(
                    name="calculate_price",
                    description="Calculate product pricing with discounts",
                    input_schema={"product_id": "string", "quantity": "number"},
                    output_schema={"unit_price": "number", "total_price": "number", "discount": "number"}
                )
            ],
            message_bus=message_bus
        )

        # Pricing rules
        self.prices = {
            "PROD-001": 100.00,
            "PROD-002": 150.00,
            "PROD-003": 200.00
        }

    async def receive_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Handle pricing requests."""
        if message.message_type == MessageType.REQUEST:
            action = message.payload.get("action")

            if action == "calculate_price":
                product_id = message.payload.get("product_id")
                quantity = message.payload.get("quantity", 1)

                unit_price = self.prices.get(product_id, 0.00)

                # Volume discounts
                if quantity >= 100:
                    discount = 0.15
                elif quantity >= 50:
                    discount = 0.10
                elif quantity >= 10:
                    discount = 0.05
                else:
                    discount = 0.00

                total_price = unit_price * quantity * (1 - discount)

                response_payload = {
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount_percentage": discount * 100,
                    "total_price": total_price
                }

                return A2AMessage(
                    message_id=f"msg_{datetime.now().timestamp()}",
                    sender_id=self.agent_id,
                    receiver_id=message.sender_id,
                    message_type=MessageType.RESPONSE,
                    timestamp=datetime.now(),
                    payload=response_payload,
                    conversation_id=message.conversation_id
                )

        return None


class ADKOrchestratorAgent(A2AAgent):
    """ADK orchestrator that coordinates other agents."""

    def __init__(self, message_bus: MessageBus):
        super().__init__(
            agent_id="adk_orchestrator",
            framework=AgentFramework.GOOGLE_ADK,
            capabilities=[
                AgentCapability(
                    name="process_order",
                    description="Process customer order by coordinating inventory and pricing",
                    input_schema={"product_id": "string", "quantity": "number"},
                    output_schema={"order_summary": "object"}
                )
            ],
            message_bus=message_bus
        )

        self.llm_agent = LlmAgent(
    name="LlmAgent",
    model="gemini-2.5-flash"
        )

    async def process_order(
        self,
        product_id: str,
        quantity: int
    ) -> Dict[str, Any]:
        """Process order by coordinating with other agents."""
        console.print(f"\n[bold yellow]Processing Order:[/bold yellow] {product_id} x {quantity}")

        conversation_id = f"order_{datetime.now().timestamp()}"

        # Step 1: Check inventory (ADK agent)
        inventory_response = await self.send_message(
            receiver_id="adk_inventory_agent",
            message_type=MessageType.REQUEST,
            payload={
                "action": "check_inventory",
                "product_id": product_id
            },
            conversation_id=conversation_id
        )

        if not inventory_response:
            return {"error": "Failed to check inventory"}

        inventory_data = inventory_response.payload

        # Step 2: Calculate pricing (Python legacy agent)
        pricing_response = await self.send_message(
            receiver_id="python_pricing_agent",
            message_type=MessageType.REQUEST,
            payload={
                "action": "calculate_price",
                "product_id": product_id,
                "quantity": quantity
            },
            conversation_id=conversation_id
        )

        if not pricing_response:
            return {"error": "Failed to calculate pricing"}

        pricing_data = pricing_response.payload

        # Step 3: Synthesize order summary
        order_summary = {
            "product_id": product_id,
            "requested_quantity": quantity,
            "available_quantity": inventory_data["available"],
            "can_fulfill": inventory_data["available"] >= quantity,
            "unit_price": pricing_data["unit_price"],
            "discount_percentage": pricing_data["discount_percentage"],
            "total_price": pricing_data["total_price"],
            "status": "approved" if inventory_data["available"] >= quantity else "backorder"
        }

        return order_summary

    async def receive_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Handle orchestration requests."""
        return None


async def demonstrate_a2a_pattern():
    """Demonstrate A2A inter-agent communication."""
    console.print("\n[bold blue]═══ Pattern 22: Inter-Agent Communication (A2A) ═══[/bold blue]")
    console.print("[bold]Business: OmniChannel Corp - Hybrid Agent Ecosystem[/bold]\n")

    # Initialize message bus
    message_bus = MessageBus()

    # Create heterogeneous agent ecosystem
    inventory_agent = ADKInventoryAgent(message_bus)
    pricing_agent = CustomPythonPricingAgent(message_bus)
    orchestrator = ADKOrchestratorAgent(message_bus)

    console.print("\n[bold green]Agent Ecosystem Registered:[/bold green]")
    console.print("✓ ADK Inventory Agent (Google ADK)")
    console.print("✓ Python Pricing Agent (Legacy Python)")
    console.print("✓ ADK Orchestrator Agent (Google ADK)")

    # Process sample orders
    orders = [
        {"product_id": "PROD-001", "quantity": 50},
        {"product_id": "PROD-002", "quantity": 100},
        {"product_id": "PROD-003", "quantity": 10}
    ]

    for order in orders:
        result = await orchestrator.process_order(
            product_id=order["product_id"],
            quantity=order["quantity"]
        )

        console.print(Panel(
            json.dumps(result, indent=2),
            title=f"[bold green]Order Summary: {order['product_id']}[/bold green]",
            border_style="green"
        ))

    # Display message history
    display_message_history(message_bus)

    # Display business metrics
    display_business_metrics()


def display_message_history(message_bus: MessageBus):
    """Display A2A message history."""
    table = Table(title="A2A Message Exchange History")
    table.add_column("Time", style="cyan")
    table.add_column("From", style="green", max_width=20)
    table.add_column("To", style="yellow", max_width=20)
    table.add_column("Type", style="magenta")
    table.add_column("Action", style="white")

    for msg in message_bus.get_message_history():
        action = msg.payload.get("action", "response")
        table.add_row(
            msg.timestamp.strftime('%H:%M:%S'),
            msg.sender_id,
            msg.receiver_id,
            msg.message_type.value,
            action
        )

    console.print(f"\n{table}")


def display_business_metrics():
    """Display OmniChannel Corp business impact."""
    console.print("\n[bold cyan]═══ Business Impact: OmniChannel Corp ═══[/bold cyan]")

    metrics = Table(title="Hybrid Agent Ecosystem Metrics")
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Before A2A", style="red")
    metrics.add_column("After A2A", style="green")
    metrics.add_column("Impact", style="yellow")

    metrics.add_row("Integration Time", "2 days/agent", "2 hours/agent", "92% reduction")
    metrics.add_row("Vendor Lock-in", "High", "Eliminated", "Freedom")
    metrics.add_row("Innovation Speed", "Baseline", "3x faster", "Agility")
    metrics.add_row("System Flexibility", "Limited", "Best-of-breed", "Optimal")

    console.print(metrics)

    console.print("\n[bold green]Key A2A Benefits:[/bold green]")
    console.print("✓ Mix ADK, CrewAI, and legacy systems seamlessly")
    console.print("✓ Standardized protocol prevents vendor lock-in")
    console.print("✓ Use best tool for each specific job")
    console.print("✓ Future-proof architecture")


if __name__ == "__main__":
    asyncio.run(demonstrate_a2a_pattern())
