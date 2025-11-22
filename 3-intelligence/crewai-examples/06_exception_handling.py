"""
Pattern 24: Exception Handling - CrewAI Implementation

Resilience patterns for failures. Graceful degradation over catastrophic failure.

Business Example: GlobalLogistics
- 73% orders processed during 4-hour outage
- Zero customer impact
- Competitor lost $5M

Mermaid Diagram Reference: diagrams/pattern-24-exception-handling.mmd
"""

import asyncio
from typing import Dict, Any
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()


class ResilientShippingCrew:
    """Shipping crew with fallback logic."""

    def __init__(self):
        self.carriers = {
            "primary": {"name": "FastShip", "available": False},  # Simulating outage
            "backup": {"name": "ReliableCarrier", "available": True}
        }

        self.agent = Agent(
            role="Shipping Coordinator",
            goal="Process shipments with fallback carriers",
            backstory="You handle shipping with resilience patterns.",
            verbose=True
        )

    def process_shipment(self, order_id: str, destination: str) -> Dict[str, Any]:
        """Process shipment with fallback."""
        console.print(f"\n[cyan]Processing:[/cyan] {order_id}")

        # Try primary
        if self.carriers["primary"]["available"]:
            console.print("[green]✓ Primary carrier[/green]")
            return {"status": "success", "carrier": "primary"}

        # Fallback to backup
        console.print("[yellow]Primary down, using backup...[/yellow]")
        if self.carriers["backup"]["available"]:
            console.print("[green]✓ Backup carrier[/green]")
            return {"status": "degraded", "carrier": "backup"}

        return {"status": "failed"}


def demonstrate_exception_handling():
    """Demonstrate exception handling."""
    console.print("\n[bold blue]═══ Pattern 24: Exception Handling - CrewAI ═══[/bold blue]")

    crew = ResilientShippingCrew()

    shipments = ["ORD-001", "ORD-002", "ORD-003"]

    for order_id in shipments:
        result = crew.process_shipment(order_id, "New York")
        console.print(f"Result: {result}\n")

    console.print("\n[bold cyan]Business Impact: GlobalLogistics[/bold cyan]")
    console.print("✓ 73% orders processed during outage")
    console.print("✓ Zero customer impact")
    console.print("✓ $5M saved vs competitor")


if __name__ == "__main__":
    demonstrate_exception_handling()
