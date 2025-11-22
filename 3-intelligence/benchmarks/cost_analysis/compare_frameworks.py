#!/usr/bin/env python3
# /// script
# dependencies = [
#   "pydantic>=2.0.0",
#   "rich>=13.0.0",
# ]
# ///
"""
Cost Analysis Benchmark for Article-3 Intelligence Patterns

This script compares cost metrics between ADK and CrewAI implementations
of intelligence patterns, tracking token usage, API calls, and estimated costs.

Usage:
    uv run compare_frameworks.py [--patterns PATTERN1,PATTERN2] [--export json|csv|both]

Examples:
    uv run compare_frameworks.py
    uv run compare_frameworks.py --patterns learning,exploration
    uv run compare_frameworks.py --export both --output results/
"""

import argparse
import json
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich not available, using plain text output")


# --- Constants ---
class Framework(Enum):
    """Supported frameworks"""
    ADK = "adk"
    CREWAI = "crewai"


class PatternCategory(Enum):
    """Pattern categories in article-3"""
    LEARNING = "learning_agents"
    OPTIMIZATION = "optimization"
    FAULT_TOLERANCE = "fault_tolerance"
    MONITORING = "monitoring"


# Model pricing (as of Jan 2025, per 1M tokens)
MODEL_PRICING = {
    "gemini-2.5-flash-exp": {"input": 0.0, "output": 0.0},  # Free tier
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gpt-4": {"input": 30.0, "output": 60.0},
    "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
}


# Pattern metadata
PATTERNS = {
    "learning_adaptation": {
        "category": PatternCategory.LEARNING,
        "name": "Learning & Adaptation",
        "iterations": 10,
        "complexity": "high"
    },
    "exploration_discovery": {
        "category": PatternCategory.LEARNING,
        "name": "Exploration & Discovery",
        "iterations": 8,
        "complexity": "high"
    },
    "evolutionary_curriculum": {
        "category": PatternCategory.LEARNING,
        "name": "Evolutionary Curriculum",
        "iterations": 12,
        "complexity": "very_high"
    },
    "resource_optimization": {
        "category": PatternCategory.OPTIMIZATION,
        "name": "Resource Aware Optimization",
        "iterations": 5,
        "complexity": "medium"
    },
    "prioritization": {
        "category": PatternCategory.OPTIMIZATION,
        "name": "Prioritization",
        "iterations": 3,
        "complexity": "low"
    },
    "checkpoint_rollback": {
        "category": PatternCategory.FAULT_TOLERANCE,
        "name": "Checkpoint & Rollback",
        "iterations": 6,
        "complexity": "medium"
    },
    "exception_handling": {
        "category": PatternCategory.FAULT_TOLERANCE,
        "name": "Exception Handling",
        "iterations": 4,
        "complexity": "low"
    },
    "goal_monitoring": {
        "category": PatternCategory.MONITORING,
        "name": "Goal Setting & Monitoring",
        "iterations": 7,
        "complexity": "medium"
    },
}


@dataclass
class TokenUsage:
    """Token usage metrics"""
    input_tokens: int
    output_tokens: int
    total_tokens: int

    @property
    def ratio(self) -> float:
        """Input to output token ratio"""
        return self.input_tokens / max(self.output_tokens, 1)


@dataclass
class CostMetrics:
    """Cost metrics for a pattern implementation"""
    pattern_name: str
    framework: Framework
    model: str
    iterations: int
    api_calls: int
    tokens: TokenUsage
    execution_time_ms: float
    estimated_cost_usd: float
    cost_per_iteration: float
    tokens_per_iteration: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export"""
        d = asdict(self)
        d['framework'] = self.framework.value
        return d


class CostSimulator:
    """Simulates cost metrics for pattern implementations"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None

    def _estimate_tokens(
        self,
        pattern_key: str,
        framework: Framework,
        iterations: int
    ) -> TokenUsage:
        """
        Estimate token usage based on pattern characteristics.

        ADK typically uses more tokens due to richer context and tool calling overhead.
        CrewAI is more efficient but may require more iterations for complex tasks.
        """
        pattern = PATTERNS[pattern_key]
        complexity_multiplier = {
            "low": 1.0,
            "medium": 1.5,
            "high": 2.0,
            "very_high": 3.0
        }[pattern["complexity"]]

        # Base tokens per iteration
        if framework == Framework.ADK:
            # ADK: More verbose due to detailed instructions and tool calls
            base_input = int(800 * complexity_multiplier)
            base_output = int(400 * complexity_multiplier)
        else:
            # CrewAI: More concise but may need more back-and-forth
            base_input = int(600 * complexity_multiplier)
            base_output = int(350 * complexity_multiplier)

        # Total across iterations
        input_tokens = base_input * iterations
        output_tokens = base_output * iterations

        return TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens
        )

    def _estimate_api_calls(
        self,
        pattern_key: str,
        framework: Framework,
        iterations: int
    ) -> int:
        """
        Estimate API calls based on framework and pattern.

        ADK uses LoopAgent which batches calls more efficiently.
        CrewAI creates new crews per iteration which may lead to more calls.
        """
        if framework == Framework.ADK:
            # ADK: Fewer calls due to loop agent optimization
            # ~2-3 calls per iteration (agent execution + tool calls)
            return iterations * 2
        else:
            # CrewAI: More calls due to crew overhead
            # ~3-4 calls per iteration (crew kickoff + task execution)
            return iterations * 3

    def _estimate_cost(
        self,
        tokens: TokenUsage,
        model: str
    ) -> float:
        """Calculate estimated cost in USD"""
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["gemini-2.5-flash-exp"])

        input_cost = (tokens.input_tokens / 1_000_000) * pricing["input"]
        output_cost = (tokens.output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def _simulate_execution_time(
        self,
        pattern_key: str,
        framework: Framework,
        api_calls: int
    ) -> float:
        """
        Simulate execution time in milliseconds.

        Based on typical API latencies and framework overhead.
        """
        pattern = PATTERNS[pattern_key]

        # Average API call latency (ms)
        avg_latency = 800

        # Framework overhead per call
        if framework == Framework.ADK:
            overhead = 100  # ADK has lower overhead
        else:
            overhead = 200  # CrewAI has higher overhead due to crew management

        base_time = api_calls * (avg_latency + overhead)

        # Add complexity factor
        complexity_factor = {
            "low": 1.0,
            "medium": 1.2,
            "high": 1.5,
            "very_high": 2.0
        }[pattern["complexity"]]

        return base_time * complexity_factor

    def benchmark_pattern(
        self,
        pattern_key: str,
        framework: Framework,
        model: str = "gemini-2.5-flash-exp"
    ) -> CostMetrics:
        """Run cost benchmark for a single pattern"""
        pattern = PATTERNS[pattern_key]
        iterations = pattern["iterations"]

        # Simulate metrics
        tokens = self._estimate_tokens(pattern_key, framework, iterations)
        api_calls = self._estimate_api_calls(pattern_key, framework, iterations)
        cost = self._estimate_cost(tokens, model)
        exec_time = self._simulate_execution_time(pattern_key, framework, api_calls)

        return CostMetrics(
            pattern_name=pattern["name"],
            framework=framework,
            model=model,
            iterations=iterations,
            api_calls=api_calls,
            tokens=tokens,
            execution_time_ms=exec_time,
            estimated_cost_usd=cost,
            cost_per_iteration=cost / iterations if iterations > 0 else 0,
            tokens_per_iteration=tokens.total_tokens // iterations if iterations > 0 else 0
        )

    def run_comparison(
        self,
        pattern_keys: Optional[List[str]] = None,
        model: str = "gemini-2.5-flash-exp"
    ) -> Dict[str, List[CostMetrics]]:
        """
        Run cost comparison for specified patterns.

        Args:
            pattern_keys: List of pattern keys to benchmark. If None, benchmarks all.
            model: Model to use for cost estimation

        Returns:
            Dictionary mapping pattern keys to [adk_metrics, crewai_metrics]
        """
        if pattern_keys is None:
            pattern_keys = list(PATTERNS.keys())

        results = {}

        if self.console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Benchmarking {len(pattern_keys)} patterns...",
                    total=len(pattern_keys)
                )

                for pattern_key in pattern_keys:
                    progress.update(
                        task,
                        description=f"[cyan]Benchmarking {PATTERNS[pattern_key]['name']}..."
                    )

                    adk_metrics = self.benchmark_pattern(pattern_key, Framework.ADK, model)
                    crewai_metrics = self.benchmark_pattern(pattern_key, Framework.CREWAI, model)

                    results[pattern_key] = [adk_metrics, crewai_metrics]
                    progress.advance(task)
        else:
            for i, pattern_key in enumerate(pattern_keys, 1):
                print(f"[{i}/{len(pattern_keys)}] Benchmarking {PATTERNS[pattern_key]['name']}...")

                adk_metrics = self.benchmark_pattern(pattern_key, Framework.ADK, model)
                crewai_metrics = self.benchmark_pattern(pattern_key, Framework.CREWAI, model)

                results[pattern_key] = [adk_metrics, crewai_metrics]

        return results


class ResultsReporter:
    """Generates reports from benchmark results"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None

    def print_summary_table(self, results: Dict[str, List[CostMetrics]]):
        """Print summary comparison table"""
        if self.console:
            table = Table(title="Cost Analysis: ADK vs CrewAI", show_header=True, header_style="bold magenta")
            table.add_column("Pattern", style="cyan", no_wrap=True)
            table.add_column("Framework", style="green")
            table.add_column("Iterations", justify="right")
            table.add_column("API Calls", justify="right")
            table.add_column("Total Tokens", justify="right")
            table.add_column("Est. Cost ($)", justify="right")
            table.add_column("Cost/Iter ($)", justify="right")

            for pattern_key, metrics_list in results.items():
                for metrics in metrics_list:
                    framework_color = "yellow" if metrics.framework == Framework.ADK else "blue"
                    table.add_row(
                        metrics.pattern_name,
                        f"[{framework_color}]{metrics.framework.value.upper()}[/{framework_color}]",
                        str(metrics.iterations),
                        str(metrics.api_calls),
                        f"{metrics.tokens.total_tokens:,}",
                        f"{metrics.estimated_cost_usd:.6f}",
                        f"{metrics.cost_per_iteration:.6f}"
                    )
                table.add_row("", "", "", "", "", "", "")  # Separator

            self.console.print(table)
        else:
            print("\n" + "=" * 100)
            print(f"{'Pattern':<30} {'Framework':<10} {'Iters':<8} {'API Calls':<10} {'Tokens':<12} {'Cost ($)':<12} {'$/Iter':<10}")
            print("=" * 100)

            for pattern_key, metrics_list in results.items():
                for metrics in metrics_list:
                    print(
                        f"{metrics.pattern_name:<30} "
                        f"{metrics.framework.value.upper():<10} "
                        f"{metrics.iterations:<8} "
                        f"{metrics.api_calls:<10} "
                        f"{metrics.tokens.total_tokens:<12,} "
                        f"{metrics.estimated_cost_usd:<12.6f} "
                        f"{metrics.cost_per_iteration:<10.6f}"
                    )
                print("-" * 100)

    def print_aggregate_stats(self, results: Dict[str, List[CostMetrics]]):
        """Print aggregate statistics"""
        adk_metrics = [m for metrics_list in results.values() for m in metrics_list if m.framework == Framework.ADK]
        crewai_metrics = [m for metrics_list in results.values() for m in metrics_list if m.framework == Framework.CREWAI]

        adk_total_cost = sum(m.estimated_cost_usd for m in adk_metrics)
        crewai_total_cost = sum(m.estimated_cost_usd for m in crewai_metrics)

        adk_total_tokens = sum(m.tokens.total_tokens for m in adk_metrics)
        crewai_total_tokens = sum(m.tokens.total_tokens for m in crewai_metrics)

        adk_total_calls = sum(m.api_calls for m in adk_metrics)
        crewai_total_calls = sum(m.api_calls for m in crewai_metrics)

        if self.console:
            stats_table = Table(title="Aggregate Statistics", show_header=True, header_style="bold cyan")
            stats_table.add_column("Metric", style="white")
            stats_table.add_column("ADK", style="yellow", justify="right")
            stats_table.add_column("CrewAI", style="blue", justify="right")
            stats_table.add_column("Difference", style="green", justify="right")

            # Total cost
            cost_diff = ((adk_total_cost - crewai_total_cost) / crewai_total_cost * 100) if crewai_total_cost > 0 else 0
            stats_table.add_row(
                "Total Cost ($)",
                f"{adk_total_cost:.6f}",
                f"{crewai_total_cost:.6f}",
                f"{cost_diff:+.2f}%"
            )

            # Total tokens
            token_diff = ((adk_total_tokens - crewai_total_tokens) / crewai_total_tokens * 100) if crewai_total_tokens > 0 else 0
            stats_table.add_row(
                "Total Tokens",
                f"{adk_total_tokens:,}",
                f"{crewai_total_tokens:,}",
                f"{token_diff:+.2f}%"
            )

            # Total API calls
            calls_diff = ((adk_total_calls - crewai_total_calls) / crewai_total_calls * 100) if crewai_total_calls > 0 else 0
            stats_table.add_row(
                "Total API Calls",
                f"{adk_total_calls:,}",
                f"{crewai_total_calls:,}",
                f"{calls_diff:+.2f}%"
            )

            # Average cost per pattern
            avg_adk = adk_total_cost / len(adk_metrics) if adk_metrics else 0
            avg_crewai = crewai_total_cost / len(crewai_metrics) if crewai_metrics else 0
            avg_diff = ((avg_adk - avg_crewai) / avg_crewai * 100) if avg_crewai > 0 else 0
            stats_table.add_row(
                "Avg Cost/Pattern ($)",
                f"{avg_adk:.6f}",
                f"{avg_crewai:.6f}",
                f"{avg_diff:+.2f}%"
            )

            self.console.print(stats_table)
        else:
            print("\n" + "=" * 80)
            print("AGGREGATE STATISTICS")
            print("=" * 80)
            print(f"{'Metric':<30} {'ADK':<20} {'CrewAI':<20} {'Diff':<10}")
            print("-" * 80)

            cost_diff = ((adk_total_cost - crewai_total_cost) / crewai_total_cost * 100) if crewai_total_cost > 0 else 0
            print(f"{'Total Cost ($)':<30} {adk_total_cost:<20.6f} {crewai_total_cost:<20.6f} {cost_diff:+.2f}%")

            token_diff = ((adk_total_tokens - crewai_total_tokens) / crewai_total_tokens * 100) if crewai_total_tokens > 0 else 0
            print(f"{'Total Tokens':<30} {adk_total_tokens:<20,} {crewai_total_tokens:<20,} {token_diff:+.2f}%")

            calls_diff = ((adk_total_calls - crewai_total_calls) / crewai_total_calls * 100) if crewai_total_calls > 0 else 0
            print(f"{'Total API Calls':<30} {adk_total_calls:<20,} {crewai_total_calls:<20,} {calls_diff:+.2f}%")

            avg_adk = adk_total_cost / len(adk_metrics) if adk_metrics else 0
            avg_crewai = crewai_total_cost / len(crewai_metrics) if crewai_metrics else 0
            avg_diff = ((avg_adk - avg_crewai) / avg_crewai * 100) if avg_crewai > 0 else 0
            print(f"{'Avg Cost/Pattern ($)':<30} {avg_adk:<20.6f} {avg_crewai:<20.6f} {avg_diff:+.2f}%")
            print("=" * 80)

    def export_json(self, results: Dict[str, List[CostMetrics]], output_path: Path):
        """Export results to JSON"""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "patterns": {
                pattern_key: [m.to_dict() for m in metrics_list]
                for pattern_key, metrics_list in results.items()
            }
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"\nExported JSON to: {output_path}")

    def export_csv(self, results: Dict[str, List[CostMetrics]], output_path: Path):
        """Export results to CSV"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Pattern",
                "Framework",
                "Model",
                "Iterations",
                "API Calls",
                "Input Tokens",
                "Output Tokens",
                "Total Tokens",
                "Execution Time (ms)",
                "Estimated Cost (USD)",
                "Cost per Iteration (USD)",
                "Tokens per Iteration"
            ])

            for pattern_key, metrics_list in results.items():
                for metrics in metrics_list:
                    writer.writerow([
                        metrics.pattern_name,
                        metrics.framework.value,
                        metrics.model,
                        metrics.iterations,
                        metrics.api_calls,
                        metrics.tokens.input_tokens,
                        metrics.tokens.output_tokens,
                        metrics.tokens.total_tokens,
                        f"{metrics.execution_time_ms:.2f}",
                        f"{metrics.estimated_cost_usd:.6f}",
                        f"{metrics.cost_per_iteration:.6f}",
                        metrics.tokens_per_iteration
                    ])

        print(f"Exported CSV to: {output_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Compare cost metrics between ADK and CrewAI implementations"
    )
    parser.add_argument(
        "--patterns",
        type=str,
        help="Comma-separated list of pattern keys to benchmark (default: all)",
        default=None
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Model to use for cost estimation",
        default="gemini-2.5-flash-exp",
        choices=list(MODEL_PRICING.keys())
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export format: json, csv, or both",
        default=None,
        choices=["json", "csv", "both"]
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory for exports",
        default="results"
    )

    args = parser.parse_args()

    # Parse pattern keys
    pattern_keys = None
    if args.patterns:
        pattern_keys = [p.strip() for p in args.patterns.split(",")]
        # Validate pattern keys
        invalid = [p for p in pattern_keys if p not in PATTERNS]
        if invalid:
            print(f"Error: Invalid pattern keys: {invalid}")
            print(f"Valid patterns: {', '.join(PATTERNS.keys())}")
            return

    # Run benchmark
    print("\n" + "=" * 80)
    print("COST ANALYSIS BENCHMARK - Article 3 Intelligence Patterns")
    print("=" * 80)
    print(f"Model: {args.model}")
    print(f"Patterns: {len(pattern_keys) if pattern_keys else len(PATTERNS)}")
    print("=" * 80 + "\n")

    simulator = CostSimulator()
    results = simulator.run_comparison(pattern_keys, args.model)

    # Display results
    reporter = ResultsReporter()
    reporter.print_summary_table(results)
    reporter.print_aggregate_stats(results)

    # Export if requested
    if args.export:
        output_dir = Path(args.output)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if args.export in ["json", "both"]:
            json_path = output_dir / f"cost_analysis_{timestamp}.json"
            reporter.export_json(results, json_path)

        if args.export in ["csv", "both"]:
            csv_path = output_dir / f"cost_analysis_{timestamp}.csv"
            reporter.export_csv(results, csv_path)

    print("\n" + "=" * 80)
    print("Benchmark complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
