"""
Pattern 22: Inter-Agent Communication (A2A) - CrewAI Implementation

Protocol for agents built with different frameworks to communicate. Enables
heterogeneous agent ecosystems.

Business Example: OmniChannel Corp
- Integration time: 2 days → 2 hours per agent
- Vendor lock-in: Eliminated
- Innovation speed: 3x faster

Mermaid Diagram Reference: diagrams/pattern-22-a2a.mmd
Medium Article: Part 3 - Governance and Reliability Patterns
"""

import json
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

load_dotenv()
console = Console()


class MessageType(Enum):
    """A2A message types."""
    REQUEST = "request"
    RESPONSE = "response"


@dataclass
class A2AMessage:
    """A2A protocol message."""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    timestamp: datetime
    payload: Dict[str, Any]


class MessageBus:
    """Message bus for A2A communication."""

    def __init__(self):
        self.messages: List[A2AMessage] = []
        self.handlers: Dict[str, Any] = {}

    def register_handler(self, agent_id: str, handler: Any):
        """Register message handler."""
        self.handlers[agent_id] = handler
        console.print(f"[green]✓[/green] Registered: {agent_id}")

    def send_message(self, message: A2AMessage) -> Any:
        """Route message to handler."""
        self.messages.append(message)
        console.print(f"[cyan]→[/cyan] {message.sender_id} → {message.receiver_id}")

        if message.receiver_id in self.handlers:
            return self.handlers[message.receiver_id](message)
        return None


class InventoryService:
    """Simulated inventory service."""

    def __init__(self):
        self.inventory = {
            "PROD-001": {"quantity": 150, "reserved": 20},
            "PROD-002": {"quantity": 75, "reserved": 10},
            "PROD-003": {"quantity": 0, "reserved": 0}
        }

    def handle_message(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle inventory requests."""
        if message.payload.get("action") == "check_inventory":
            product_id = message.payload.get("product_id")
            inv = self.inventory.get(product_id, {"quantity": 0, "reserved": 0})
            available = inv["quantity"] - inv["reserved"]

            return {
                "product_id": product_id,
                "quantity": inv["quantity"],
                "available": available,
                "status": "in_stock" if available > 0 else "out_of_stock"
            }
        return {}


class PricingService:
    """Simulated pricing service."""

    def __init__(self):
        self.prices = {
            "PROD-001": 100.00,
            "PROD-002": 150.00,
            "PROD-003": 200.00
        }

    def handle_message(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle pricing requests."""
        if message.payload.get("action") == "calculate_price":
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

            return {
                "product_id": product_id,
                "unit_price": unit_price,
                "discount_percentage": discount * 100,
                "total_price": total_price
            }
        return {}


class A2AOrchestrationCrew:
    """Crew that orchestrates A2A communication."""

    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus

        # Setup services
        self.inventory_service = InventoryService()
        self.pricing_service = PricingService()

        # Register handlers
        self.message_bus.register_handler("inventory_service", self.inventory_service.handle_message)
        self.message_bus.register_handler("pricing_service", self.pricing_service.handle_message)

        # Create orchestrator agent
        self.orchestrator = Agent(
            role="Order Processing Orchestrator",
            goal="Coordinate inventory and pricing services to process orders",
            backstory="""You coordinate multiple backend services to process
            customer orders efficiently.""",
            verbose=True
        )

    def process_order(self, product_id: str, quantity: int) -> Dict[str, Any]:
        """Process order using A2A communication."""
        console.print(f"\n[bold yellow]Processing Order:[/bold yellow] {product_id} x {quantity}")

        # Check inventory
        inv_msg = A2AMessage(
            message_id=f"msg_{datetime.now().timestamp()}",
            sender_id="orchestrator",
            receiver_id="inventory_service",
            message_type=MessageType.REQUEST,
            timestamp=datetime.now(),
            payload={"action": "check_inventory", "product_id": product_id}
        )
        inventory_data = self.message_bus.send_message(inv_msg)

        # Calculate pricing
        price_msg = A2AMessage(
            message_id=f"msg_{datetime.now().timestamp()}",
            sender_id="orchestrator",
            receiver_id="pricing_service",
            message_type=MessageType.REQUEST,
            timestamp=datetime.now(),
            payload={"action": "calculate_price", "product_id": product_id, "quantity": quantity}
        )
        pricing_data = self.message_bus.send_message(price_msg)

        # Synthesize result
        return {
            "product_id": product_id,
            "requested_quantity": quantity,
            "available_quantity": inventory_data["available"],
            "can_fulfill": inventory_data["available"] >= quantity,
            "unit_price": pricing_data["unit_price"],
            "discount_percentage": pricing_data["discount_percentage"],
            "total_price": pricing_data["total_price"],
            "status": "approved" if inventory_data["available"] >= quantity else "backorder"
        }


def demonstrate_a2a_pattern():
    """Demonstrate A2A pattern."""
    console.print("\n[bold blue]═══ Pattern 22: A2A Protocol - CrewAI ═══[/bold blue]")
    console.print("[bold]Business: OmniChannel Corp - Hybrid Ecosystem[/bold]\n")

    # Initialize
    message_bus = MessageBus()
    crew = A2AOrchestrationCrew(message_bus)

    # Process orders
    orders = [
        {"product_id": "PROD-001", "quantity": 50},
        {"product_id": "PROD-002", "quantity": 100}
    ]

    for order in orders:
        result = crew.process_order(**order)
        console.print(Panel(
            json.dumps(result, indent=2),
            title=f"[bold green]Order: {order['product_id']}[/bold green]",
            border_style="green"
        ))

    # Display metrics
    display_business_metrics()


def display_business_metrics():
    """Display business impact."""
    console.print("\n[bold cyan]═══ Business Impact: OmniChannel Corp ═══[/bold cyan]")

    metrics = Table(title="A2A Integration Metrics")
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Before", style="red")
    metrics.add_column("After", style="green")

    metrics.add_row("Integration Time", "2 days", "2 hours")
    metrics.add_row("Vendor Lock-in", "High", "Eliminated")
    metrics.add_row("Innovation Speed", "1x", "3x")

    console.print(metrics)


if __name__ == "__main__":
    demonstrate_a2a_pattern()
