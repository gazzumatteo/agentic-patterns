"""
Pattern 24: Exception Handling and Recovery - Google ADK Implementation

Resilience patterns for network failures, API limits, and unexpected errors.
Graceful degradation over catastrophic failure.

Business Example: GlobalLogistics
- Primary system down 4 hours
- 73% orders processed via fallbacks
- Zero customer impact
- Competitor lost $5M in same period

Mermaid Diagram Reference: diagrams/pattern-24-exception-handling.mmd
Medium Article: Part 3 - Governance and Reliability Patterns
"""

import asyncio
from typing import Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai.types import GenerateContentConfig
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()


class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


@dataclass
class RetryConfig:
    max_attempts: int = 3
    backoff_multiplier: float = 2.0
    initial_delay: float = 1.0


class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.status = ServiceStatus.HEALTHY

    def record_success(self):
        """Record successful call."""
        self.failure_count = 0
        self.status = ServiceStatus.HEALTHY

    def record_failure(self):
        """Record failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.status = ServiceStatus.DOWN
            console.print("[red]Circuit breaker OPEN - service unavailable[/red]")

    def is_open(self) -> bool:
        """Check if circuit is open."""
        if self.status == ServiceStatus.DOWN:
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed > self.recovery_timeout:
                    self.status = ServiceStatus.DEGRADED
                    console.print("[yellow]Circuit breaker HALF-OPEN - attempting recovery[/yellow]")
                    return False
            return True
        return False


class ResilientShippingAgent:
    """Shipping agent with resilience patterns."""

    def __init__(self):
        self.primary_circuit = CircuitBreaker()
        self.retry_config = RetryConfig()

        self.agent = LlmAgent(
    name="Agent",
    model="gemini-2.5-flash"
        )

        # Simulate multiple carrier APIs
        self.carriers = {
            "primary": {"name": "FastShip", "available": True},
            "backup1": {"name": "ReliableCarrier", "available": True},
            "backup2": {"name": "BudgetShip", "available": True}
        }

        console.print("[green]✓[/green] Resilient Shipping Agent initialized")

    async def get_shipping_quote(
        self,
        destination: str,
        weight_kg: float,
        carrier: str = "primary"
    ) -> dict:
        """Get shipping quote with retry logic."""

        for attempt in range(self.retry_config.max_attempts):
            try:
                # Simulate API call
                await asyncio.sleep(0.1)

                if not self.carriers[carrier]["available"]:
                    raise Exception(f"{self.carriers[carrier]['name']} unavailable")

                # Success
                quote = {
                    "carrier": self.carriers[carrier]["name"],
                    "destination": destination,
                    "cost": weight_kg * 5.0,
                    "estimated_days": 3
                }

                self.primary_circuit.record_success()
                return quote

            except Exception as e:
                console.print(f"[yellow]Attempt {attempt + 1} failed: {e}[/yellow]")

                if attempt < self.retry_config.max_attempts - 1:
                    delay = self.retry_config.initial_delay * (self.retry_config.backoff_multiplier ** attempt)
                    console.print(f"[dim]Retrying in {delay}s...[/dim]")
                    await asyncio.sleep(delay)
                else:
                    self.primary_circuit.record_failure()
                    raise

    async def process_shipment(
        self,
        order_id: str,
        destination: str,
        weight_kg: float
    ) -> dict:
        """Process shipment with fallback carriers."""

        console.print(f"\n[cyan]Processing Shipment:[/cyan] Order {order_id}")

        # Try primary carrier
        if not self.primary_circuit.is_open():
            try:
                quote = await self.get_shipping_quote(destination, weight_kg, "primary")
                console.print(f"[green]✓ Primary carrier:[/green] {quote['carrier']}")
                return {"status": "success", "carrier": "primary", "quote": quote}
            except Exception as e:
                console.print(f"[red]Primary carrier failed:[/red] {e}")

        # Fallback to backup carrier 1
        console.print("[yellow]Trying backup carrier 1...[/yellow]")
        try:
            quote = await self.get_shipping_quote(destination, weight_kg, "backup1")
            console.print(f"[green]✓ Backup carrier 1:[/green] {quote['carrier']}")
            return {"status": "degraded", "carrier": "backup1", "quote": quote}
        except Exception as e:
            console.print(f"[red]Backup 1 failed:[/red] {e}")

        # Last resort: backup carrier 2
        console.print("[yellow]Trying backup carrier 2...[/yellow]")
        try:
            quote = await self.get_shipping_quote(destination, weight_kg, "backup2")
            console.print(f"[green]✓ Backup carrier 2:[/green] {quote['carrier']}")
            return {"status": "degraded", "carrier": "backup2", "quote": quote}
        except Exception as e:
            console.print(f"[red]All carriers failed[/red]")
            return {"status": "failed", "error": "No carriers available"}


async def demonstrate_exception_handling():
    """Demonstrate exception handling pattern."""
    console.print("\n[bold blue]═══ Pattern 24: Exception Handling ═══[/bold blue]")
    console.print("[bold]Business: GlobalLogistics - Supply Chain Resilience[/bold]\n")

    agent = ResilientShippingAgent()

    # Simulate primary carrier outage
    agent.carriers["primary"]["available"] = False

    # Process shipments
    shipments = [
        {"order_id": "ORD-001", "destination": "New York", "weight_kg": 10.0},
        {"order_id": "ORD-002", "destination": "Los Angeles", "weight_kg": 15.0},
        {"order_id": "ORD-003", "destination": "Chicago", "weight_kg": 8.0}
    ]

    results = []
    for shipment in shipments:
        result = await agent.process_shipment(**shipment)
        results.append(result)

    # Display results
    display_results(results)

    # Display business metrics
    display_business_metrics()


def display_results(results):
    """Display shipment results."""
    table = Table(title="Shipment Processing Results")
    table.add_column("Order", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Carrier", style="green")
    table.add_column("Cost", style="white")

    for i, result in enumerate(results, 1):
        status_color = "green" if result["status"] == "success" else "yellow" if result["status"] == "degraded" else "red"
        table.add_row(
            f"ORD-{i:03d}",
            f"[{status_color}]{result['status']}[/{status_color}]",
            result.get("carrier", "N/A"),
            f"${result.get('quote', {}).get('cost', 0):.2f}" if "quote" in result else "N/A"
        )

    console.print(f"\n{table}")


def display_business_metrics():
    """Display GlobalLogistics business impact."""
    console.print("\n[bold cyan]═══ Business Impact: GlobalLogistics ═══[/bold cyan]")

    metrics = Table(title="Supply Chain Resilience Metrics")
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Without Resilience", style="red")
    metrics.add_column("With Resilience", style="green")
    metrics.add_column("Impact", style="yellow")

    metrics.add_row("Orders Processed (4hr outage)", "0%", "73%", "Business continuity")
    metrics.add_row("Customer Impact", "Complete", "Zero", "Reputation saved")
    metrics.add_row("Revenue Loss", "$5M+ (competitor)", "$0", "$5M saved")
    metrics.add_row("Service Level", "Failed", "Maintained", "SLA compliance")

    console.print(metrics)

    console.print("\n[bold green]Key Resilience Benefits:[/bold green]")
    console.print("✓ Automatic failover to backup carriers")
    console.print("✓ Circuit breaker prevents cascade failures")
    console.print("✓ Exponential backoff reduces system load")
    console.print("✓ Graceful degradation maintains partial service")


if __name__ == "__main__":
    asyncio.run(demonstrate_exception_handling())
