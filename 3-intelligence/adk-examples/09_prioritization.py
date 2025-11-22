"""
Pattern 27: Prioritization - Google ADK Implementation

Intelligent task scheduling based on business impact, dependencies, and SLAs.

Business Example: MegaComm (10M subscribers)
- P1 response time: 47 min → 3 min
- Customer satisfaction: 3.2 → 4.6 stars
- Churn reduction: 23%
- Revenue retention: +$45M

Mermaid Diagram Reference: diagrams/pattern-27-prioritization.mmd
Medium Article: Part 3 - Governance and Reliability Patterns
"""

import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import GenerateContentConfig
from google.genai import types
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()


class Priority(Enum):
    P1_CRITICAL = 1
    P2_HIGH = 2
    P3_NORMAL = 3
    P4_LOW = 4


@dataclass
class SupportTicket:
    ticket_id: str
    customer_id: str
    issue_type: str
    description: str
    affected_users: int
    created_at: datetime
    sla_deadline: datetime
    priority: Priority = Priority.P3_NORMAL
    priority_score: float = 0.0


class PriorityCalculator:
    """Calculates ticket priority based on multiple factors."""

    def calculate_priority(self, ticket: SupportTicket) -> tuple[Priority, float]:
        """Calculate priority and score."""
        score = 0.0

        # Business impact (affected users)
        if ticket.affected_users > 1000:
            score += 50
        elif ticket.affected_users > 100:
            score += 30
        elif ticket.affected_users > 10:
            score += 10

        # SLA urgency
        time_to_deadline = (ticket.sla_deadline - datetime.now()).total_seconds() / 3600  # hours
        if time_to_deadline < 1:
            score += 40
        elif time_to_deadline < 4:
            score += 25
        elif time_to_deadline < 24:
            score += 10

        # Issue type severity
        if "outage" in ticket.issue_type.lower():
            score += 50
        elif "degraded" in ticket.issue_type.lower():
            score += 30
        elif "billing" in ticket.issue_type.lower():
            score += 15

        # Determine priority level
        if score >= 80:
            priority = Priority.P1_CRITICAL
        elif score >= 50:
            priority = Priority.P2_HIGH
        elif score >= 25:
            priority = Priority.P3_NORMAL
        else:
            priority = Priority.P4_LOW

        return priority, score


class PrioritizedSupportAgent:
    """Support agent with intelligent prioritization."""

    def __init__(self):
        self.agent = LlmAgent(
            name="support_agent",
            model="gemini-2.5-flash"
        )

        self.priority_calculator = PriorityCalculator()
        self.ticket_queue: List[SupportTicket] = []

        console.print("[green]✓[/green] Prioritized Support Agent initialized")

    def add_ticket(self, ticket: SupportTicket) -> None:
        """Add ticket to queue and calculate priority."""
        priority, score = self.priority_calculator.calculate_priority(ticket)
        ticket.priority = priority
        ticket.priority_score = score

        self.ticket_queue.append(ticket)

        # Re-sort queue by priority
        self.ticket_queue.sort(key=lambda t: (t.priority.value, -t.priority_score))

        console.print(
            f"[cyan]New Ticket:[/cyan] {ticket.ticket_id} - "
            f"[{'red' if priority == Priority.P1_CRITICAL else 'yellow' if priority == Priority.P2_HIGH else 'green'}]"
            f"{priority.name}[/] (score: {score:.0f})"
        )

    async def process_next_ticket(self) -> Dict[str, Any]:
        """Process highest priority ticket."""
        if not self.ticket_queue:
            return {"status": "no_tickets"}

        ticket = self.ticket_queue.pop(0)

        console.print(f"\n[bold yellow]Processing:[/bold yellow] {ticket.ticket_id} ({ticket.priority.name})")
        console.print(f"[dim]Issue: {ticket.description}[/dim]")
        console.print(f"[dim]Affected users: {ticket.affected_users}[/dim]")

        # Simulate ticket processing
        start_time = datetime.now()

        prompt = f"""You are a customer support agent. Resolve this issue:

Ticket: {ticket.ticket_id}
Issue Type: {ticket.issue_type}
Description: {ticket.description}
Affected Users: {ticket.affected_users}
Priority: {ticket.priority.name}

Provide resolution steps."""

        app_name = "agentic_patterns"
        app = App(name=app_name, root_agent=self.agent)
        session_service = InMemorySessionService()
        runner = Runner(app=app, session_service=session_service)

        session = await session_service.create_session(
            app_name=app_name,
            user_id="support"
        )

        content = types.Content(role='user', parts=[types.Part(text=prompt)])
        events = runner.run_async(
            user_id="support",
            session_id=session.id,
            new_message=content
        )

        resolution = None
        async for event in events:
            if event.is_final_response() and event.content:
                resolution = event.content.parts[0].text
                break

        duration = (datetime.now() - start_time).total_seconds() * 60  # minutes

        console.print(f"[green]✓ Resolved in {duration:.1f} minutes[/green]")

        return {
            "ticket_id": ticket.ticket_id,
            "priority": ticket.priority.name,
            "affected_users": ticket.affected_users,
            "resolution_time_min": duration,
            "resolution": resolution
        }

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        return {
            "total_tickets": len(self.ticket_queue),
            "by_priority": {
                "P1": len([t for t in self.ticket_queue if t.priority == Priority.P1_CRITICAL]),
                "P2": len([t for t in self.ticket_queue if t.priority == Priority.P2_HIGH]),
                "P3": len([t for t in self.ticket_queue if t.priority == Priority.P3_NORMAL]),
                "P4": len([t for t in self.ticket_queue if t.priority == Priority.P4_LOW])
            }
        }


async def demonstrate_prioritization_pattern():
    """Demonstrate prioritization pattern."""
    console.print("\n[bold blue]═══ Pattern 27: Prioritization ═══[/bold blue]")
    console.print("[bold]Business: MegaComm - Customer Service Triage[/bold]\n")

    agent = PrioritizedSupportAgent()

    # Create test tickets
    now = datetime.now()

    tickets = [
        SupportTicket(
            ticket_id="TKT-001",
            customer_id="CUST-1001",
            issue_type="General Question",
            description="How to change account settings?",
            affected_users=1,
            created_at=now,
            sla_deadline=now + timedelta(hours=48)
        ),
        SupportTicket(
            ticket_id="TKT-002",
            customer_id="CUST-1002",
            issue_type="Service Outage",
            description="Network connectivity lost for entire region",
            affected_users=5000,
            created_at=now,
            sla_deadline=now + timedelta(hours=1)
        ),
        SupportTicket(
            ticket_id="TKT-003",
            customer_id="CUST-1003",
            issue_type="Billing Inquiry",
            description="Question about last invoice",
            affected_users=1,
            created_at=now,
            sla_deadline=now + timedelta(hours=24)
        ),
        SupportTicket(
            ticket_id="TKT-004",
            customer_id="CUST-1004",
            issue_type="Service Degraded",
            description="Slow internet speeds reported by 150 users",
            affected_users=150,
            created_at=now,
            sla_deadline=now + timedelta(hours=4)
        )
    ]

    # Add tickets to queue
    for ticket in tickets:
        agent.add_ticket(ticket)

    # Display queue status
    display_queue_status(agent)

    # Process tickets in priority order
    console.print("\n[bold yellow]Processing tickets in priority order...[/bold yellow]")

    results = []
    while agent.ticket_queue:
        result = await agent.process_next_ticket()
        if result.get("status") != "no_tickets":
            results.append(result)

    # Display results
    display_results(results)

    # Display business metrics
    display_business_metrics()


def display_queue_status(agent: PrioritizedSupportAgent):
    """Display queue status."""
    status = agent.get_queue_status()

    table = Table(title="Support Queue Status")
    table.add_column("Priority", style="cyan")
    table.add_column("Count", style="green")

    for priority_level, count in status["by_priority"].items():
        color = "red" if priority_level == "P1" else "yellow" if priority_level == "P2" else "white"
        table.add_row(priority_level, f"[{color}]{count}[/{color}]")

    table.add_row("[bold]TOTAL[/bold]", f"[bold]{status['total_tickets']}[/bold]")

    console.print(f"\n{table}")


def display_results(results):
    """Display processing results."""
    table = Table(title="Ticket Processing Results")
    table.add_column("Ticket", style="cyan")
    table.add_column("Priority", style="yellow")
    table.add_column("Affected Users", style="magenta")
    table.add_column("Resolution Time", style="green")

    for result in results:
        priority_color = "red" if "P1" in result["priority"] else "yellow" if "P2" in result["priority"] else "white"
        table.add_row(
            result["ticket_id"],
            f"[{priority_color}]{result['priority']}[/{priority_color}]",
            str(result["affected_users"]),
            f"{result['resolution_time_min']:.1f} min"
        )

    console.print(f"\n{table}")


def display_business_metrics():
    """Display MegaComm business impact."""
    console.print("\n[bold cyan]═══ Business Impact: MegaComm ═══[/bold cyan]")

    metrics = Table(title="Customer Service Prioritization Metrics")
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Before Prioritization", style="red")
    metrics.add_column("After Prioritization", style="green")
    metrics.add_column("Impact", style="yellow")

    metrics.add_row("P1 Response Time", "47 minutes", "3 minutes", "94% improvement")
    metrics.add_row("Customer Satisfaction", "3.2 stars", "4.6 stars", "+1.4 stars")
    metrics.add_row("Churn Reduction", "Baseline", "23% lower", "Retention")
    metrics.add_row("Revenue Retention", "Baseline", "+$45M", "Business value")

    console.print(metrics)

    console.print("\n[bold green]Key Prioritization Benefits:[/bold green]")
    console.print("✓ Critical issues get immediate attention")
    console.print("✓ Business impact drives priority")
    console.print("✓ SLA compliance improved dramatically")
    console.print("✓ Resource allocation optimized")


if __name__ == "__main__":
    asyncio.run(demonstrate_prioritization_pattern())
