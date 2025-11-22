"""
Pattern 29: Checkpoint/Rollback - CrewAI Implementation

Restoration points before risky operations.

Business Example: DataCorp
- 2M records protected
- Rollback in 47 seconds
- $20M saved

Mermaid Diagram Reference: diagrams/pattern-29-checkpoint-rollback.mmd
"""

import copy
import json
from typing import Dict, Any
from datetime import datetime
from crewai import Agent
from rich.console import Console
from rich.panel import Panel

console = Console()


class StateManager:
    """Manages state checkpoints."""

    def __init__(self):
        self.checkpoints: Dict[str, Dict[str, Any]] = {}
        self.current_state: Dict[str, Any] = {}

    def create_checkpoint(self, description: str) -> str:
        """Create checkpoint."""
        checkpoint_id = f"cp_{datetime.now().timestamp()}"
        self.checkpoints[checkpoint_id] = {
            "state": copy.deepcopy(self.current_state),
            "description": description,
            "timestamp": datetime.now()
        }

        console.print(f"[green]✓ Checkpoint:[/green] {checkpoint_id}")
        return checkpoint_id

    def rollback(self, checkpoint_id: str) -> bool:
        """Rollback to checkpoint."""
        if checkpoint_id in self.checkpoints:
            self.current_state = copy.deepcopy(self.checkpoints[checkpoint_id]["state"])
            console.print(f"[yellow]↺ Rolled back:[/yellow] {checkpoint_id}")
            return True
        return False

    def commit(self, checkpoint_id: str):
        """Commit changes."""
        console.print(f"[green]✓ Committed:[/green] {checkpoint_id}")


class SafeMigrationCrew:
    """Crew with checkpoint/rollback."""

    def __init__(self):
        self.state_manager = StateManager()

        # Initialize data
        self.state_manager.current_state = {
            "customers": {
                "CUST-001": {"name": "Alice", "email": "alice@example.com"},
                "CUST-002": {"name": "Bob", "email": "bob@example.com"}
            }
        }

        self.agent = Agent(
            role="Database Administrator",
            goal="Execute migrations safely with checkpoint/rollback",
            backstory="You ensure data integrity with checkpoints.",
            verbose=True
        )

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate data."""
        for customer_id, customer in data.get("customers", {}).items():
            if "@" not in customer.get("email", ""):
                return False
        return True

    def execute_migration(self, name: str, migration_fn):
        """Execute with checkpoint."""
        console.print(f"\n[cyan]Migration:[/cyan] {name}")

        # Create checkpoint
        checkpoint_id = self.state_manager.create_checkpoint(f"Before {name}")

        start = datetime.now()

        try:
            # Apply migration
            new_state = migration_fn(copy.deepcopy(self.state_manager.current_state))

            # Validate
            if not self.validate_data(new_state):
                console.print("[red]✗ Validation failed - rolling back[/red]")
                self.state_manager.rollback(checkpoint_id)
                duration = (datetime.now() - start).total_seconds() * 1000
                return {"status": "rolled_back", "rollback_duration_ms": duration}

            # Commit
            self.state_manager.current_state = new_state
            self.state_manager.commit(checkpoint_id)

            return {"status": "committed"}

        except Exception as e:
            console.print(f"[red]✗ Error:[/red] {e}")
            self.state_manager.rollback(checkpoint_id)
            return {"status": "rolled_back", "error": str(e)}


def successful_migration(state):
    """Add loyalty points."""
    for customer_id in state["customers"]:
        state["customers"][customer_id]["loyalty_points"] = 100
    return state


def corrupting_migration(state):
    """Corrupt emails (simulated failure)."""
    for customer_id in state["customers"]:
        state["customers"][customer_id]["email"] = "CORRUPTED"
    return state


def demonstrate_checkpoint_rollback():
    """Demonstrate checkpoint/rollback."""
    console.print("\n[bold blue]═══ Pattern 29: Checkpoint/Rollback - CrewAI ═══[/bold blue]")

    crew = SafeMigrationCrew()

    # Test 1: Success
    console.print("\n[bold]Test 1: Successful Migration[/bold]")
    result1 = crew.execute_migration("Add loyalty points", successful_migration)
    console.print(Panel(json.dumps(result1, indent=2), border_style="green"))

    # Test 2: Rollback
    console.print("\n[bold]Test 2: Failed Migration (Rollback)[/bold]")
    result2 = crew.execute_migration("Corrupt data", corrupting_migration)
    console.print(Panel(json.dumps(result2, indent=2), border_style="red"))

    # Final state
    console.print("\n[bold]Final State:[/bold]")
    console.print(json.dumps(crew.state_manager.current_state, indent=2))

    console.print("\n[bold cyan]Business Impact: DataCorp[/bold cyan]")
    console.print("✓ 2M records protected")
    console.print("✓ Rollback in 47 seconds")
    console.print("✓ $20M saved in recovery costs")


if __name__ == "__main__":
    demonstrate_checkpoint_rollback()
