"""
Pattern 29: Checkpoint and Rollback - Google ADK Implementation

Creates restoration points before risky operations. Your undo button for agent actions.

Business Example: DataCorp
- Detected corruption in 2M customer records
- Automatic rollback in 47 seconds
- Zero data loss
- Saved estimated $20M in recovery costs

Mermaid Diagram Reference: diagrams/pattern-29-checkpoint-rollback.mmd
Medium Article: Part 3 - Governance and Reliability Patterns
"""

import asyncio
import json
import copy
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
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


class CheckpointStatus(Enum):
    ACTIVE = "active"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Checkpoint:
    """Checkpoint containing state snapshot."""
    checkpoint_id: str
    timestamp: datetime
    state_snapshot: Dict[str, Any]
    description: str
    status: CheckpointStatus = CheckpointStatus.ACTIVE


class StateManager:
    """Manages state checkpoints and rollbacks."""

    def __init__(self):
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.current_state: Dict[str, Any] = {}

        console.print("[green]✓[/green] State Manager initialized")

    def create_checkpoint(self, description: str) -> str:
        """Create a checkpoint of current state."""
        checkpoint_id = f"cp_{datetime.now().timestamp()}"

        # Deep copy of current state
        state_snapshot = copy.deepcopy(self.current_state)

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            timestamp=datetime.now(),
            state_snapshot=state_snapshot,
            description=description,
            status=CheckpointStatus.ACTIVE
        )

        self.checkpoints[checkpoint_id] = checkpoint

        console.print(f"[green]✓ Checkpoint created:[/green] {checkpoint_id}")
        console.print(f"[dim]Description: {description}[/dim]")

        return checkpoint_id

    def commit(self, checkpoint_id: str) -> bool:
        """Commit checkpoint (operation successful)."""
        if checkpoint_id not in self.checkpoints:
            return False

        self.checkpoints[checkpoint_id].status = CheckpointStatus.COMMITTED
        console.print(f"[green]✓ Checkpoint committed:[/green] {checkpoint_id}")

        return True

    def rollback(self, checkpoint_id: str) -> bool:
        """Rollback to checkpoint state."""
        if checkpoint_id not in self.checkpoints:
            console.print(f"[red]✗ Checkpoint not found:[/red] {checkpoint_id}")
            return False

        checkpoint = self.checkpoints[checkpoint_id]

        # Restore state from snapshot
        self.current_state = copy.deepcopy(checkpoint.state_snapshot)

        checkpoint.status = CheckpointStatus.ROLLED_BACK

        console.print(f"[yellow]↺ Rolled back to:[/yellow] {checkpoint_id}")
        console.print(f"[dim]State restored from: {checkpoint.timestamp.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")

        return True

    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update current state."""
        self.current_state.update(updates)

    def get_state(self) -> Dict[str, Any]:
        """Get current state."""
        return copy.deepcopy(self.current_state)


class DataValidator:
    """Validates data integrity."""

    @staticmethod
    def validate_customer_data(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate customer data."""
        # Check required fields
        required_fields = ["customer_id", "name", "email"]
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"

        # Validate email format
        if "@" not in data["email"]:
            return False, f"Invalid email format: {data['email']}"

        # Check for data corruption markers
        if "CORRUPTED" in str(data.values()):
            return False, "Data corruption detected"

        return True, None


class SafeDatabaseAgent:
    """Database agent with checkpoint/rollback capability."""

    def __init__(self):
        self.state_manager = StateManager()
        self.validator = DataValidator()

        self.agent = LlmAgent(
    name="Agent",
    model="gemini-2.5-flash"
        )

        # Initialize with sample data
        self.state_manager.update_state({
            "customers": {
                "CUST-001": {"customer_id": "CUST-001", "name": "Alice Johnson", "email": "alice@example.com", "balance": 1000},
                "CUST-002": {"customer_id": "CUST-002", "name": "Bob Smith", "email": "bob@example.com", "balance": 2000},
            }
        })

        console.print("[green]✓[/green] Safe Database Agent initialized")

    async def execute_migration(
        self,
        migration_name: str,
        migration_fn
    ) -> Dict[str, Any]:
        """Execute database migration with checkpoint/rollback."""
        console.print(f"\n[cyan]Executing Migration:[/cyan] {migration_name}")

        # Step 1: Create checkpoint
        checkpoint_id = self.state_manager.create_checkpoint(
            description=f"Before {migration_name}"
        )

        start_time = datetime.now()

        try:
            # Step 2: Execute migration
            console.print("[yellow]Applying changes...[/yellow]")
            new_state = migration_fn(self.state_manager.get_state())

            # Step 3: Validate result
            console.print("[yellow]Validating data integrity...[/yellow]")
            for customer_id, customer_data in new_state.get("customers", {}).items():
                valid, error = self.validator.validate_customer_data(customer_data)

                if not valid:
                    console.print(f"[red]✗ Validation failed:[/red] {error}")
                    console.print(f"[red]Corrupted customer:[/red] {customer_id}")

                    # Step 4a: Rollback on validation failure
                    rollback_start = datetime.now()
                    self.state_manager.rollback(checkpoint_id)
                    rollback_duration = (datetime.now() - rollback_start).total_seconds()

                    return {
                        "status": "rolled_back",
                        "checkpoint_id": checkpoint_id,
                        "reason": error,
                        "rollback_duration_ms": rollback_duration * 1000,
                        "data_loss": False
                    }

            # Step 4b: Commit on success
            self.state_manager.update_state(new_state)
            self.state_manager.commit(checkpoint_id)

            duration = (datetime.now() - start_time).total_seconds()

            console.print(f"[green]✓ Migration completed successfully[/green]")

            return {
                "status": "committed",
                "checkpoint_id": checkpoint_id,
                "duration_ms": duration * 1000,
                "records_updated": len(new_state.get("customers", {}))
            }

        except Exception as e:
            # Step 4c: Rollback on exception
            console.print(f"[red]✗ Migration failed:[/red] {str(e)}")

            rollback_start = datetime.now()
            self.state_manager.rollback(checkpoint_id)
            rollback_duration = (datetime.now() - rollback_start).total_seconds()

            return {
                "status": "rolled_back",
                "checkpoint_id": checkpoint_id,
                "reason": str(e),
                "rollback_duration_ms": rollback_duration * 1000
            }


def successful_migration(state: Dict[str, Any]) -> Dict[str, Any]:
    """Migration that succeeds."""
    new_state = copy.deepcopy(state)

    # Add loyalty_points field to all customers
    for customer_id in new_state["customers"]:
        new_state["customers"][customer_id]["loyalty_points"] = 100

    return new_state


def corrupting_migration(state: Dict[str, Any]) -> Dict[str, Any]:
    """Migration that corrupts data."""
    new_state = copy.deepcopy(state)

    # Simulate data corruption
    for customer_id in new_state["customers"]:
        new_state["customers"][customer_id]["email"] = "CORRUPTED"  # Invalid email

    return new_state


async def demonstrate_checkpoint_rollback():
    """Demonstrate checkpoint/rollback pattern."""
    console.print("\n[bold blue]═══ Pattern 29: Checkpoint and Rollback ═══[/bold blue]")
    console.print("[bold]Business: DataCorp - Database Migration Safety[/bold]\n")

    agent = SafeDatabaseAgent()

    # Test 1: Successful migration
    console.print("\n" + "="*60)
    console.print("[bold]Test 1: Successful Migration[/bold]")
    result1 = await agent.execute_migration(
        "Add loyalty points field",
        successful_migration
    )

    console.print(Panel(
        json.dumps(result1, indent=2),
        title="[bold green]Migration Result[/bold green]",
        border_style="green"
    ))

    # Test 2: Failed migration with rollback
    console.print("\n" + "="*60)
    console.print("[bold]Test 2: Failed Migration with Rollback[/bold]")
    result2 = await agent.execute_migration(
        "Corrupt email fields (simulated failure)",
        corrupting_migration
    )

    console.print(Panel(
        json.dumps(result2, indent=2),
        title="[bold red]Migration Result[/bold red]",
        border_style="red"
    ))

    # Display final state
    console.print("\n" + "="*60)
    console.print("[bold]Final State:[/bold]")
    final_state = agent.state_manager.get_state()
    console.print(json.dumps(final_state, indent=2))

    # Display business metrics
    display_business_metrics()


def display_business_metrics():
    """Display DataCorp business impact."""
    console.print("\n[bold cyan]═══ Business Impact: DataCorp ═══[/bold cyan]")

    metrics = Table(title="Database Migration Safety Metrics")
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Without Checkpoint", style="red")
    metrics.add_column("With Checkpoint", style="green")
    metrics.add_column("Impact", style="yellow")

    metrics.add_row(
        "Data Corruption Incident",
        "2M records lost",
        "Detected & rolled back",
        "Zero data loss"
    )
    metrics.add_row(
        "Recovery Time",
        "Days/weeks",
        "47 seconds",
        "99.9% faster"
    )
    metrics.add_row(
        "Recovery Cost",
        "$20M estimated",
        "$0",
        "$20M saved"
    )
    metrics.add_row(
        "Business Continuity",
        "Major outage",
        "Seamless",
        "No impact"
    )

    console.print(metrics)

    console.print("\n[bold green]Key Checkpoint/Rollback Benefits:[/bold green]")
    console.print("✓ Instant undo for failed operations")
    console.print("✓ Data integrity validation before commit")
    console.print("✓ Zero data loss on errors")
    console.print("✓ Enables bold automation with safety net")


if __name__ == "__main__":
    asyncio.run(demonstrate_checkpoint_rollback())
