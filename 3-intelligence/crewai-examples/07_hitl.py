"""
Pattern 25: HITL - CrewAI Implementation

Human judgment at critical decision points.

Business Example: HealthSystem USA
- Accuracy: 89% → 97%
- False positives: -64%

Mermaid Diagram Reference: diagrams/pattern-25-hitl.mmd
"""

import os
from crewai import Agent, Task, Crew
from rich.console import Console
from rich.prompt import Confirm

console = Console()


def get_human_approval(prompt: str, default: bool = True) -> bool:
    """Get human approval with test mode support."""
    if os.getenv("TEST_MODE", "false").lower() == "true":
        console.print(f"  [yellow][AUTO-APPROVED in TEST_MODE][/yellow] {prompt}")
        return default
    return Confirm.ask(prompt, default=default)


class HITLDiagnosticCrew:
    """Diagnostic crew with human oversight."""

    def __init__(self):
        self.agent = Agent(
            role="Diagnostic Assistant",
            goal="Analyze symptoms and request physician review for high-risk cases",
            backstory="You flag high-risk cases for physician review.",
            verbose=True
        )

    def process_patient(self, patient_id: str, symptoms: str):
        """Process patient with HITL."""
        console.print(f"\n[cyan]Patient:[/cyan] {patient_id} - {symptoms}")

        # Simulate diagnosis
        high_risk = "chest pain" in symptoms.lower() or "fever" in symptoms.lower()

        if high_risk:
            console.print("[yellow]High risk - requesting physician review...[/yellow]")
            approved = get_human_approval("Approve diagnosis?", default=True)

            if approved:
                console.print("[green]✓ Approved by physician[/green]")
                return {"status": "approved", "reviewed_by": "physician"}
            else:
                console.print("[red]Modified by physician[/red]")
                return {"status": "modified", "reviewed_by": "physician"}
        else:
            console.print("[green]✓ Auto-approved (low risk)[/green]")
            return {"status": "auto_approved"}


def demonstrate_hitl():
    """Demonstrate HITL."""
    console.print("\n[bold blue]═══ Pattern 25: HITL - CrewAI ═══[/bold blue]")

    crew = HITLDiagnosticCrew()

    cases = [
        {"patient_id": "PT-001", "symptoms": "Mild cough"},
        {"patient_id": "PT-002", "symptoms": "High fever and chest pain"}
    ]

    for case in cases:
        result = crew.process_patient(**case)
        console.print(f"Result: {result}\n")

    console.print("\n[bold cyan]Business Impact: HealthSystem USA[/bold cyan]")
    console.print("✓ Accuracy: 89% → 97%")
    console.print("✓ False positives: -64%")
    console.print("✓ Time saved: 2hrs/day")


if __name__ == "__main__":
    demonstrate_hitl()
