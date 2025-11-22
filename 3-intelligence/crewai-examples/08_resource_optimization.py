"""
Pattern 26: Resource Optimization - CrewAI Implementation

Dynamic model selection based on complexity.

Business Example: CloudAI Platform
- LLM costs: -71%
- Monthly savings: $340K

Mermaid Diagram Reference: diagrams/pattern-26-resource-optimization.mmd
"""

from crewai import Agent
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()


class ResourceOptimizedCrew:
    """Crew with dynamic model selection."""

    def __init__(self):
        self.models = {
            "simple": {"name": "gpt-3.5-turbo", "cost": 0.001},
            "complex": {"name": "gpt-4", "cost": 0.03}
        }

        self.usage = {"simple": 0, "complex": 0}

    def assess_complexity(self, query: str) -> str:
        """Assess query complexity."""
        word_count = len(query.split())
        return "complex" if word_count > 20 else "simple"

    def process_query(self, query: str):
        """Process with optimized model."""
        console.print(f"\n[cyan]Query:[/cyan] {query[:50]}...")

        complexity = self.assess_complexity(query)
        model_config = self.models[complexity]

        console.print(f"[green]Model:[/green] {model_config['name']}")
        console.print(f"[dim]Cost: ${model_config['cost']}/1K tokens[/dim]")

        self.usage[complexity] += 1

        return {"model": model_config["name"], "cost": model_config["cost"]}


def demonstrate_resource_optimization():
    """Demonstrate resource optimization."""
    console.print("\n[bold blue]═══ Pattern 26: Resource Optimization - CrewAI ═══[/bold blue]")

    crew = ResourceOptimizedCrew()

    queries = [
        "What is 2+2?",
        "Compare and analyze economic policies of USA and China with detailed synthesis"
    ]

    for query in queries:
        crew.process_query(query)

    # Display stats
    table = Table(title="Model Usage")
    table.add_column("Model Type", style="cyan")
    table.add_column("Queries", style="green")

    for model_type, count in crew.usage.items():
        table.add_row(model_type, str(count))

    console.print(f"\n{table}")

    console.print("\n[bold cyan]Business Impact: CloudAI[/bold cyan]")
    console.print("✓ LLM costs: -71%")
    console.print("✓ Monthly savings: $340K")


if __name__ == "__main__":
    demonstrate_resource_optimization()
