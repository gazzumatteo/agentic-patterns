"""
Pattern 28: Goal Setting and Monitoring - Google ADK Implementation

SMART goals for agents with progress tracking.

Business Example: SalesForce competitor
- Goal achievement: 67% → 92%
- Pipeline velocity: +40%
- Forecast accuracy: ±5%
- Sales productivity: +55%

Mermaid Diagram Reference: diagrams/pattern-28-goal-monitoring.mmd
Medium Article: Part 3 - Governance and Reliability Patterns
"""

import asyncio
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai.types import GenerateContentConfig
from google.genai import types
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn

load_dotenv()
console = Console()


@dataclass
class SMARTGoal:
    """SMART goal definition."""
    specific: str
    measurable: str
    achievable: str
    relevant: str
    time_bound: datetime
    target_value: float
    current_value: float = 0.0


class MetricsCollector:
    """Collects and tracks goal metrics."""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}

    def record(self, metric_name: str, value: float):
        """Record metric value."""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(value)

    def get_current(self, metric_name: str) -> float:
        """Get current metric value."""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return 0.0
        return self.metrics[metric_name][-1]

    def get_average(self, metric_name: str) -> float:
        """Get average metric value."""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return 0.0
        return sum(self.metrics[metric_name]) / len(self.metrics[metric_name])

    def get_trend(self, metric_name: str) -> str:
        """Get metric trend."""
        if metric_name not in self.metrics or len(self.metrics[metric_name]) < 2:
            return "stable"

        recent = self.metrics[metric_name][-1]
        previous = self.metrics[metric_name][-2]

        if recent > previous:
            return "improving"
        elif recent < previous:
            return "declining"
        return "stable"


class GoalOrientedSalesAgent:
    """Sales agent with goal monitoring."""

    def __init__(self, goal: SMARTGoal):
        self.goal = goal
        self.metrics = MetricsCollector()

        self.agent = LlmAgent(
    name="Agent",
    model="gemini-2.5-flash"
        )

        console.print(f"[green]✓[/green] Goal-Oriented Sales Agent initialized")
        console.print(f"[cyan]Goal:[/cyan] {goal.specific}")
        console.print(f"[cyan]Target:[/cyan] {goal.target_value} by {goal.time_bound.strftime('%Y-%m-%d')}")

    async def qualify_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Qualify a lead and track progress."""
        prompt = f"""You are a sales qualification agent. Evaluate this lead:

Company: {lead_data['company']}
Industry: {lead_data['industry']}
Size: {lead_data['employees']} employees
Budget: ${lead_data['budget']:,}
Timeline: {lead_data['timeline']}

Determine if this is a qualified lead (yes/no) and provide qualification score (0-100)."""

        runner = InMemoryRunner(agent=self.agent, app_name="sales_agent")
        session = await runner.session_service.create_session(
            app_name="sales_agent",
            user_id="sales"
        )

        content = types.Content(role='user', parts=[types.Part(text=prompt)])
        events = runner.run_async(
            user_id="sales",
            session_id=session.id,
            new_message=content
        )

        response_text = None
        async for event in events:
            if event.is_final_response() and event.content:
                response_text = event.content.parts[0].text
                break

        # Parse response (simplified)
        qualified = "yes" in response_text.lower() if response_text else False
        score = 75 if qualified else 40  # Simplified scoring

        # Record metrics
        if qualified:
            self.metrics.record("qualified_leads", self.metrics.get_current("qualified_leads") + 1)

        return {
            "lead_id": lead_data["lead_id"],
            "qualified": qualified,
            "score": score,
            "timestamp": datetime.now()
        }

    def check_goal_progress(self) -> Dict[str, Any]:
        """Check progress toward goal."""
        current = self.metrics.get_current("qualified_leads")
        progress_percentage = (current / self.goal.target_value) * 100 if self.goal.target_value > 0 else 0

        time_remaining = (self.goal.time_bound - datetime.now()).days
        days_elapsed = 30 - time_remaining  # Assuming 30-day goal period
        expected_progress = (days_elapsed / 30) * self.goal.target_value

        on_track = current >= expected_progress

        return {
            "current_value": current,
            "target_value": self.goal.target_value,
            "progress_percentage": progress_percentage,
            "time_remaining_days": time_remaining,
            "on_track": on_track,
            "expected_at_this_point": expected_progress,
            "trend": self.metrics.get_trend("qualified_leads")
        }

    def generate_progress_report(self) -> str:
        """Generate progress report."""
        progress = self.check_goal_progress()

        report = f"""
Goal Progress Report
{'='*50}

Goal: {self.goal.specific}
Target: {self.goal.target_value} {self.goal.measurable}
Deadline: {self.goal.time_bound.strftime('%Y-%m-%d')}

Current Progress:
  Achieved: {progress['current_value']:.0f} / {progress['target_value']:.0f}
  Percentage: {progress['progress_percentage']:.1f}%
  Status: {'✓ ON TRACK' if progress['on_track'] else '⚠ BEHIND SCHEDULE'}
  Trend: {progress['trend'].upper()}

Time Remaining: {progress['time_remaining_days']} days

Expected at this point: {progress['expected_at_this_point']:.0f}
Actual: {progress['current_value']:.0f}
Gap: {progress['current_value'] - progress['expected_at_this_point']:+.0f}
"""
        return report


async def demonstrate_goal_monitoring():
    """Demonstrate goal monitoring pattern."""
    console.print("\n[bold blue]═══ Pattern 28: Goal Setting and Monitoring ═══[/bold blue]")
    console.print("[bold]Business: SalesForce Competitor - Pipeline Management[/bold]\n")

    # Define SMART goal
    goal = SMARTGoal(
        specific="Qualify 50 high-quality leads",
        measurable="Number of qualified leads",
        achievable="Based on historical 30-40/month performance",
        relevant="Drives Q4 revenue targets",
        time_bound=datetime.now() + timedelta(days=15),
        target_value=50
    )

    agent = GoalOrientedSalesAgent(goal=goal)

    # Simulate lead qualification over time
    sample_leads = [
        {"lead_id": "L001", "company": "TechCorp", "industry": "SaaS", "employees": 500, "budget": 100000, "timeline": "Q4"},
        {"lead_id": "L002", "company": "RetailCo", "industry": "Retail", "employees": 200, "budget": 50000, "timeline": "Q1"},
        {"lead_id": "L003", "company": "FinServe", "industry": "Finance", "employees": 1000, "budget": 250000, "timeline": "Q4"},
        {"lead_id": "L004", "company": "StartupX", "industry": "Tech", "employees": 20, "budget": 10000, "timeline": "Future"},
        {"lead_id": "L005", "company": "Enterprise", "industry": "Manufacturing", "employees": 5000, "budget": 500000, "timeline": "Q4"},
    ]

    console.print("\n[bold yellow]Qualifying leads...[/bold yellow]")

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("[cyan]Processing leads...", total=len(sample_leads))

        for lead in sample_leads:
            result = await agent.qualify_lead(lead)
            console.print(
                f"  {result['lead_id']}: "
                f"{'[green]QUALIFIED[/green]' if result['qualified'] else '[red]NOT QUALIFIED[/red]'} "
                f"(score: {result['score']})"
            )
            progress.update(task, advance=1)

    # Display progress report
    console.print("\n" + "="*50)
    console.print(agent.generate_progress_report())

    # Simulate additional progress
    console.print("\n[bold yellow]Simulating additional progress...[/bold yellow]")
    for i in range(15):  # Simulate 15 more qualified leads
        agent.metrics.record("qualified_leads", agent.metrics.get_current("qualified_leads") + 1)

    # Final report
    console.print("\n" + "="*50)
    console.print(agent.generate_progress_report())

    # Display business metrics
    display_business_metrics()


def display_business_metrics():
    """Display SalesForce competitor business impact."""
    console.print("\n[bold cyan]═══ Business Impact: SalesForce Competitor ═══[/bold cyan]")

    metrics = Table(title="Goal-Oriented Sales Metrics")
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Before Goal Monitoring", style="red")
    metrics.add_column("After Goal Monitoring", style="green")
    metrics.add_column("Impact", style="yellow")

    metrics.add_row("Goal Achievement", "67%", "92%", "+25 points")
    metrics.add_row("Pipeline Velocity", "Baseline", "+40%", "Faster deals")
    metrics.add_row("Forecast Accuracy", "±15%", "±5%", "Better planning")
    metrics.add_row("Sales Productivity", "Baseline", "+55%", "Efficiency")

    console.print(metrics)

    console.print("\n[bold green]Key Goal Monitoring Benefits:[/bold green]")
    console.print("✓ Clear targets drive agent performance")
    console.print("✓ Progress tracking enables course correction")
    console.print("✓ SMART goals ensure achievability")
    console.print("✓ Accountability improves outcomes")


if __name__ == "__main__":
    asyncio.run(demonstrate_goal_monitoring())
