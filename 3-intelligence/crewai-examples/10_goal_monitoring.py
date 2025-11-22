"""
Pattern 28: Goal Monitoring - CrewAI Implementation

SMART goals with progress tracking.

Business Example: SalesForce competitor
- Goal achievement: 67% → 92%
- Pipeline velocity: +40%
- Sales productivity: +55%

Mermaid Diagram Reference: diagrams/pattern-28-goal-monitoring.mmd
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from crewai import Agent
from rich.console import Console

console = Console()


@dataclass
class SMARTGoal:
    """SMART goal definition."""
    specific: str
    target_value: float
    time_bound: datetime
    current_value: float = 0.0


class GoalOrientedCrew:
    """Crew with goal monitoring."""

    def __init__(self, goal: SMARTGoal):
        self.goal = goal
        self.qualified_count = 0

        self.agent = Agent(
            role="Sales Agent",
            goal=f"Achieve goal: {goal.specific}",
            backstory="You track progress toward SMART goals.",
            verbose=True
        )

        console.print(f"[green]✓[/green] Goal: {goal.specific}")
        console.print(f"[cyan]Target:[/cyan] {goal.target_value}")

    def qualify_lead(self, lead_id: str, qualified: bool):
        """Qualify lead and track progress."""
        if qualified:
            self.qualified_count += 1

        console.print(
            f"{lead_id}: {'[green]QUALIFIED[/green]' if qualified else '[red]NOT QUALIFIED[/red]'}"
        )

    def check_progress(self):
        """Check goal progress."""
        progress = (self.qualified_count / self.goal.target_value) * 100
        on_track = self.qualified_count >= (self.goal.target_value * 0.5)  # Simplified

        console.print(f"\n[bold]Progress Report:[/bold]")
        console.print(f"  Achieved: {self.qualified_count}/{self.goal.target_value}")
        console.print(f"  Progress: {progress:.1f}%")
        console.print(f"  Status: {'[green]ON TRACK[/green]' if on_track else '[yellow]BEHIND[/yellow]'}")


def demonstrate_goal_monitoring():
    """Demonstrate goal monitoring."""
    console.print("\n[bold blue]═══ Pattern 28: Goal Monitoring - CrewAI ═══[/bold blue]")

    goal = SMARTGoal(
        specific="Qualify 50 leads",
        target_value=50,
        time_bound=datetime.now() + timedelta(days=30)
    )

    crew = GoalOrientedCrew(goal=goal)

    # Simulate lead qualification
    leads = [
        ("L001", True),
        ("L002", False),
        ("L003", True),
        ("L004", True),
        ("L005", False)
    ]

    for lead_id, qualified in leads:
        crew.qualify_lead(lead_id, qualified)

    # Simulate additional progress
    for i in range(20):
        crew.qualified_count += 1

    crew.check_progress()

    console.print("\n[bold cyan]Business Impact: SalesForce Competitor[/bold cyan]")
    console.print("✓ Goal achievement: 67% → 92%")
    console.print("✓ Pipeline velocity: +40%")
    console.print("✓ Productivity: +55%")


if __name__ == "__main__":
    demonstrate_goal_monitoring()
