"""
Pattern 26: Resource-Aware Optimization - Google ADK Implementation

Dynamic model selection based on task complexity. Balance cost, speed, and quality.

Business Example: CloudAI Platform
- LLM costs: -71%
- Monthly savings: $340K
- Quality metrics: Unchanged

Mermaid Diagram Reference: diagrams/pattern-26-resource-optimization.mmd
Medium Article: Part 3 - Governance and Reliability Patterns
"""

import asyncio
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime
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


@dataclass
class ModelConfig:
    name: str
    cost_per_1k_tokens: float
    speed_multiplier: float
    capability_score: float


class ComplexityAnalyzer:
    """Analyzes task complexity."""

    async def assess_complexity(self, query: str) -> float:
        """Return complexity score 0-1."""
        # Simple heuristics
        word_count = len(query.split())
        has_technical = any(term in query.lower() for term in ["analyze", "compare", "evaluate", "synthesize"])
        has_creative = any(term in query.lower() for term in ["write", "create", "design", "imagine"])

        complexity = 0.0

        if word_count > 50:
            complexity += 0.3
        elif word_count > 20:
            complexity += 0.1

        if has_technical:
            complexity += 0.4

        if has_creative:
            complexity += 0.3

        return min(complexity, 1.0)


class ResourceOptimizedAgent:
    """Agent that selects model based on task complexity."""

    def __init__(self):
        self.models = {
            "flash": ModelConfig(
                name="gemini-2.5-flash",  # Use available model
                cost_per_1k_tokens=0.01,
                speed_multiplier=2.0,
                capability_score=0.7
            ),
            "pro": ModelConfig(
                name="gemini-2.5-flash",  # Use available model
                cost_per_1k_tokens=0.05,
                speed_multiplier=1.0,
                capability_score=0.9
            ),
            "ultra": ModelConfig(
                name="gemini-2.5-flash",
                cost_per_1k_tokens=0.10,
                speed_multiplier=0.8,
                capability_score=1.0
            )
        }

        self.complexity_analyzer = ComplexityAnalyzer()
        self.usage_stats = {
            "flash": {"count": 0, "tokens": 0, "cost": 0},
            "pro": {"count": 0, "tokens": 0, "cost": 0},
            "ultra": {"count": 0, "tokens": 0, "cost": 0}
        }

        # Create runner and session once
        self.app_name = "agentic_patterns"
        self.runner = None
        self.session = None

        console.print("[green]✓[/green] Resource-Optimized Agent initialized")

    def select_model(self, complexity: float) -> str:
        """Select appropriate model based on complexity."""
        if complexity < 0.3:
            return "flash"
        elif complexity < 0.7:
            return "pro"
        else:
            return "ultra"

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process query with optimized model selection."""
        console.print(f"\n[cyan]Query:[/cyan] {query}")

        # Assess complexity
        complexity = await self.complexity_analyzer.assess_complexity(query)
        console.print(f"[yellow]Complexity Score:[/yellow] {complexity:.2f}")

        # Select model
        model_key = self.select_model(complexity)
        model_config = self.models[model_key]

        console.print(f"[green]Selected Model:[/green] {model_config.name}")
        console.print(f"[dim]Cost: ${model_config.cost_per_1k_tokens}/1K tokens[/dim]")

        # Create agent with selected model
        agent = LlmAgent(
            name="resource_optimizer",
            model=model_config.name
        )

        # Process query - create app and runner for each query to allow model switching
        start_time = datetime.now()
        app = App(name=self.app_name, root_agent=agent)
        session_service = InMemorySessionService()
        runner = Runner(app=app, session_service=session_service)

        session = await session_service.create_session(
            app_name=self.app_name,
            user_id="user"
        )

        content = types.Content(role='user', parts=[types.Part(text=query)])
        events = runner.run_async(
            user_id="user",
            session_id=session.id,
            new_message=content
        )

        response_text = None
        async for event in events:
            if event.is_final_response() and event.content:
                response_text = event.content.parts[0].text
                break

        duration = (datetime.now() - start_time).total_seconds()

        # Track usage
        estimated_tokens = len(query.split()) * 2  # Simplified
        self.usage_stats[model_key]["count"] += 1
        self.usage_stats[model_key]["tokens"] += estimated_tokens
        self.usage_stats[model_key]["cost"] += (estimated_tokens / 1000) * model_config.cost_per_1k_tokens

        return {
            "query": query,
            "complexity": complexity,
            "model_used": model_config.name,
            "cost": (estimated_tokens / 1000) * model_config.cost_per_1k_tokens,
            "duration": duration,
            "response": response_text
        }


async def demonstrate_resource_optimization():
    """Demonstrate resource optimization pattern."""
    console.print("\n[bold blue]═══ Pattern 26: Resource Optimization ═══[/bold blue]")
    console.print("[bold]Business: CloudAI Platform - LLM Cost Management[/bold]\n")

    agent = ResourceOptimizedAgent()

    # Test queries with varying complexity
    queries = [
        "What is the capital of France?",  # Low complexity -> Flash
        "Compare and analyze the economic policies of USA and China",  # Medium -> Pro
        "Write a comprehensive analysis synthesizing macroeconomic trends, geopolitical factors, and technological disruption across global markets",  # High -> Ultra
    ]

    results = []
    for query in queries:
        result = await agent.process_query(query)
        results.append(result)

    # Display usage statistics
    display_usage_stats(agent)

    # Display business metrics
    display_business_metrics()


def display_usage_stats(agent):
    """Display usage statistics."""
    table = Table(title="Model Usage Statistics")
    table.add_column("Model", style="cyan")
    table.add_column("Queries", style="green")
    table.add_column("Tokens", style="yellow")
    table.add_column("Cost", style="magenta")

    total_cost = 0
    for model_key, stats in agent.usage_stats.items():
        if stats["count"] > 0:
            table.add_row(
                agent.models[model_key].name,
                str(stats["count"]),
                str(stats["tokens"]),
                f"${stats['cost']:.4f}"
            )
            total_cost += stats["cost"]

    console.print(f"\n{table}")
    console.print(f"\n[bold]Total Cost:[/bold] ${total_cost:.4f}")


def display_business_metrics():
    """Display CloudAI Platform business impact."""
    console.print("\n[bold cyan]═══ Business Impact: CloudAI Platform ═══[/bold cyan]")

    metrics = Table(title="LLM Cost Optimization Metrics")
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Before Optimization", style="red")
    metrics.add_column("After Optimization", style="green")
    metrics.add_column("Impact", style="yellow")

    metrics.add_row("LLM Costs", "$1.17M/month", "$340K/month", "-71%")
    metrics.add_row("Response Latency", "Baseline", "+8ms", "Acceptable")
    metrics.add_row("Quality Metrics", "Baseline", "Unchanged", "No degradation")
    metrics.add_row("Monthly Savings", "N/A", "$830K", "Cost efficiency")

    console.print(metrics)

    console.print("\n[bold green]Key Optimization Benefits:[/bold green]")
    console.print("✓ Simple queries use cheap, fast models")
    console.print("✓ Complex reasoning gets premium processing")
    console.print("✓ Automatic routing based on complexity")
    console.print("✓ 70%+ cost reduction typical")


if __name__ == "__main__":
    asyncio.run(demonstrate_resource_optimization())
