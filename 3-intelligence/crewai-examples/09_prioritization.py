"""
Pattern 27: Prioritization - CrewAI Implementation

Intelligent task scheduling based on business impact.

Business Example: MegaComm
- P1 response: 47 min → 3 min
- Customer satisfaction: 3.2 → 4.6 stars
- Revenue retention: +$45M

Mermaid Diagram Reference: diagrams/pattern-27-prioritization.mmd
"""

from typing import List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from crewai import Agent
from rich.console import Console
from rich.table import Table

console = Console()


class Priority(Enum):
    P1_CRITICAL = 1
    P2_HIGH = 2
    P3_NORMAL = 3
    P4_LOW = 4


@dataclass
class Ticket:
    ticket_id: str
    issue_type: str
    affected_users: int
    priority: Priority = Priority.P3_NORMAL
    priority_score: float = 0.0


class PrioritizedSupportCrew:
    """Support crew with prioritization."""

    def __init__(self):
        self.agent = Agent(
            role="Support Agent",
            goal="Process tickets by priority",
            backstory="You prioritize based on business impact.",
            verbose=True
        )

        self.ticket_queue: List[Ticket] = []

    def calculate_priority(self, ticket: Ticket) -> tuple[Priority, float]:
        """Calculate priority."""
        score = 0.0

        if ticket.affected_users > 1000:
            score += 50
        elif ticket.affected_users > 100:
            score += 30

        if "outage" in ticket.issue_type.lower():
            score += 50
        elif "degraded" in ticket.issue_type.lower():
            score += 30

        if score >= 80:
            priority = Priority.P1_CRITICAL
        elif score >= 50:
            priority = Priority.P2_HIGH
        else:
            priority = Priority.P3_NORMAL

        return priority, score

    def add_ticket(self, ticket: Ticket):
        """Add and prioritize ticket."""
        priority, score = self.calculate_priority(ticket)
        ticket.priority = priority
        ticket.priority_score = score

        self.ticket_queue.append(ticket)
        self.ticket_queue.sort(key=lambda t: (t.priority.value, -t.priority_score))

        console.print(f"[cyan]{ticket.ticket_id}:[/cyan] {priority.name} (score: {score:.0f})")

    def process_next(self):
        """Process highest priority."""
        if not self.ticket_queue:
            return None

        ticket = self.ticket_queue.pop(0)
        console.print(f"\n[yellow]Processing:[/yellow] {ticket.ticket_id} ({ticket.priority.name})")
        return ticket


def demonstrate_prioritization():
    """Demonstrate prioritization."""
    console.print("\n[bold blue]═══ Pattern 27: Prioritization - CrewAI ═══[/bold blue]")

    crew = PrioritizedSupportCrew()

    tickets = [
        Ticket("TKT-001", "General Question", 1),
        Ticket("TKT-002", "Service Outage", 5000),
        Ticket("TKT-003", "Billing", 1),
        Ticket("TKT-004", "Service Degraded", 150)
    ]

    for ticket in tickets:
        crew.add_ticket(ticket)

    # Process in priority order
    console.print("\n[bold]Processing Queue:[/bold]")
    while crew.ticket_queue:
        crew.process_next()

    console.print("\n[bold cyan]Business Impact: MegaComm[/bold cyan]")
    console.print("✓ P1 response: 47min → 3min")
    console.print("✓ Satisfaction: 3.2 → 4.6 stars")
    console.print("✓ Revenue retention: +$45M")


if __name__ == "__main__":
    demonstrate_prioritization()
