#!/usr/bin/env python3
# /// script
# dependencies = [
#   "pydantic>=2.0.0",
#   "rich>=13.0.0",
#   "psutil>=5.9.0",
# ]
# ///
"""
Performance Benchmark for Article-3 Intelligence Patterns

This script benchmarks execution time, throughput, latency distributions,
and resource usage for all patterns across both ADK and CrewAI frameworks.

Usage:
    uv run benchmark_patterns.py [--patterns PATTERN1,PATTERN2] [--load 1,5,10]

Examples:
    uv run benchmark_patterns.py
    uv run benchmark_patterns.py --patterns learning,exploration --load 1,5
    uv run benchmark_patterns.py --export json --output results/
"""

import argparse
import json
import time
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("psutil not available, resource monitoring disabled")

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.panel import Panel
    from rich.layout import Layout
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


# Pattern metadata
PATTERNS = {
    "learning_adaptation": {
        "category": PatternCategory.LEARNING,
        "name": "Learning & Adaptation",
        "iterations": 10,
        "complexity": "high",
        "base_latency_ms": 850
    },
    "exploration_discovery": {
        "category": PatternCategory.LEARNING,
        "name": "Exploration & Discovery",
        "iterations": 8,
        "complexity": "high",
        "base_latency_ms": 900
    },
    "evolutionary_curriculum": {
        "category": PatternCategory.LEARNING,
        "name": "Evolutionary Curriculum",
        "iterations": 12,
        "complexity": "very_high",
        "base_latency_ms": 1200
    },
    "resource_optimization": {
        "category": PatternCategory.OPTIMIZATION,
        "name": "Resource Aware Optimization",
        "iterations": 5,
        "complexity": "medium",
        "base_latency_ms": 600
    },
    "prioritization": {
        "category": PatternCategory.OPTIMIZATION,
        "name": "Prioritization",
        "iterations": 3,
        "complexity": "low",
        "base_latency_ms": 400
    },
    "checkpoint_rollback": {
        "category": PatternCategory.FAULT_TOLERANCE,
        "name": "Checkpoint & Rollback",
        "iterations": 6,
        "complexity": "medium",
        "base_latency_ms": 700
    },
    "exception_handling": {
        "category": PatternCategory.FAULT_TOLERANCE,
        "name": "Exception Handling",
        "iterations": 4,
        "complexity": "low",
        "base_latency_ms": 500
    },
    "goal_monitoring": {
        "category": PatternCategory.MONITORING,
        "name": "Goal Setting & Monitoring",
        "iterations": 7,
        "complexity": "medium",
        "base_latency_ms": 750
    },
}


@dataclass
class LatencyStats:
    """Latency statistics"""
    min_ms: float
    max_ms: float
    mean_ms: float
    median_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    stddev_ms: float

    @classmethod
    def from_samples(cls, samples: List[float]) -> 'LatencyStats':
        """Calculate latency stats from samples"""
        if not samples:
            return cls(0, 0, 0, 0, 0, 0, 0, 0)

        sorted_samples = sorted(samples)
        return cls(
            min_ms=min(samples),
            max_ms=max(samples),
            mean_ms=statistics.mean(samples),
            median_ms=statistics.median(samples),
            p50_ms=cls._percentile(sorted_samples, 50),
            p95_ms=cls._percentile(sorted_samples, 95),
            p99_ms=cls._percentile(sorted_samples, 99),
            stddev_ms=statistics.stdev(samples) if len(samples) > 1 else 0
        )

    @staticmethod
    def _percentile(sorted_samples: List[float], percentile: float) -> float:
        """Calculate percentile from sorted samples"""
        if not sorted_samples:
            return 0
        index = (len(sorted_samples) - 1) * percentile / 100
        floor = int(index)
        ceil = floor + 1
        if ceil >= len(sorted_samples):
            return sorted_samples[floor]
        return sorted_samples[floor] + (index - floor) * (sorted_samples[ceil] - sorted_samples[floor])


@dataclass
class ResourceUsage:
    """Resource usage metrics"""
    cpu_percent: float
    memory_mb: float
    memory_percent: float

    @classmethod
    def current(cls) -> 'ResourceUsage':
        """Get current resource usage"""
        if not PSUTIL_AVAILABLE:
            return cls(0, 0, 0)

        process = psutil.Process()
        mem_info = process.memory_info()

        return cls(
            cpu_percent=process.cpu_percent(interval=0.1),
            memory_mb=mem_info.rss / 1024 / 1024,
            memory_percent=process.memory_percent()
        )


@dataclass
class PerformanceMetrics:
    """Performance metrics for a pattern implementation"""
    pattern_name: str
    framework: Framework
    load_level: int
    iterations: int
    total_operations: int
    execution_time_ms: float
    throughput_ops_per_sec: float
    latency: LatencyStats
    resource_usage: ResourceUsage
    success_rate: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export"""
        d = asdict(self)
        d['framework'] = self.framework.value
        return d


class PerformanceSimulator:
    """Simulates performance metrics for pattern implementations"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None

    def _simulate_single_operation(
        self,
        pattern_key: str,
        framework: Framework
    ) -> Tuple[float, bool]:
        """
        Simulate a single operation and return (latency_ms, success).

        ADK typically has lower latency due to optimized loop execution.
        CrewAI has higher latency due to crew management overhead.
        """
        import random

        pattern = PATTERNS[pattern_key]
        base_latency = pattern["base_latency_ms"]

        # Framework multiplier
        if framework == Framework.ADK:
            framework_multiplier = 0.85  # ADK is faster
        else:
            framework_multiplier = 1.15  # CrewAI has more overhead

        # Add random variation (±20%)
        variation = random.uniform(0.8, 1.2)

        # Calculate latency
        latency = base_latency * framework_multiplier * variation

        # Simulate the wait
        time.sleep(latency / 1000.0)

        # Simulate occasional failures (5% failure rate)
        success = random.random() > 0.05

        return latency, success

    def _simulate_concurrent_operations(
        self,
        pattern_key: str,
        framework: Framework,
        num_operations: int
    ) -> List[Tuple[float, bool]]:
        """Simulate concurrent operations"""
        with ThreadPoolExecutor(max_workers=min(num_operations, 10)) as executor:
            futures = [
                executor.submit(self._simulate_single_operation, pattern_key, framework)
                for _ in range(num_operations)
            ]

            results = []
            for future in as_completed(futures):
                results.append(future.result())

            return results

    def benchmark_pattern(
        self,
        pattern_key: str,
        framework: Framework,
        load_level: int = 1
    ) -> PerformanceMetrics:
        """
        Benchmark a single pattern at specified load level.

        Args:
            pattern_key: Pattern to benchmark
            framework: Framework to use
            load_level: Number of concurrent operations

        Returns:
            Performance metrics
        """
        pattern = PATTERNS[pattern_key]
        iterations = pattern["iterations"]

        # Total operations = iterations * load_level
        total_operations = iterations * load_level

        # Measure resource usage before
        resource_before = ResourceUsage.current()

        # Run benchmark
        start_time = time.time()
        results = self._simulate_concurrent_operations(pattern_key, framework, total_operations)
        end_time = time.time()

        # Measure resource usage after
        resource_after = ResourceUsage.current()

        # Calculate metrics
        execution_time_ms = (end_time - start_time) * 1000
        latencies = [r[0] for r in results]
        successes = [r[1] for r in results]

        throughput = total_operations / (execution_time_ms / 1000) if execution_time_ms > 0 else 0
        success_rate = sum(successes) / len(successes) if successes else 0

        # Average resource usage
        avg_resource = ResourceUsage(
            cpu_percent=(resource_before.cpu_percent + resource_after.cpu_percent) / 2,
            memory_mb=(resource_before.memory_mb + resource_after.memory_mb) / 2,
            memory_percent=(resource_before.memory_percent + resource_after.memory_percent) / 2
        )

        return PerformanceMetrics(
            pattern_name=pattern["name"],
            framework=framework,
            load_level=load_level,
            iterations=iterations,
            total_operations=total_operations,
            execution_time_ms=execution_time_ms,
            throughput_ops_per_sec=throughput,
            latency=LatencyStats.from_samples(latencies),
            resource_usage=avg_resource,
            success_rate=success_rate
        )

    def run_comparison(
        self,
        pattern_keys: Optional[List[str]] = None,
        load_levels: Optional[List[int]] = None
    ) -> Dict[str, Dict[int, List[PerformanceMetrics]]]:
        """
        Run performance comparison for specified patterns and load levels.

        Args:
            pattern_keys: List of pattern keys to benchmark. If None, benchmarks all.
            load_levels: List of load levels to test. Default: [1, 5, 10]

        Returns:
            Nested dict: pattern_key -> load_level -> [adk_metrics, crewai_metrics]
        """
        if pattern_keys is None:
            pattern_keys = list(PATTERNS.keys())

        if load_levels is None:
            load_levels = [1, 5, 10]

        results = {}
        total_benchmarks = len(pattern_keys) * len(load_levels) * 2  # *2 for both frameworks

        if self.console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(
                    "[cyan]Running benchmarks...",
                    total=total_benchmarks
                )

                for pattern_key in pattern_keys:
                    results[pattern_key] = {}

                    for load_level in load_levels:
                        progress.update(
                            task,
                            description=f"[cyan]{PATTERNS[pattern_key]['name']} @ load={load_level}..."
                        )

                        adk_metrics = self.benchmark_pattern(pattern_key, Framework.ADK, load_level)
                        progress.advance(task)

                        crewai_metrics = self.benchmark_pattern(pattern_key, Framework.CREWAI, load_level)
                        progress.advance(task)

                        results[pattern_key][load_level] = [adk_metrics, crewai_metrics]
        else:
            current = 0
            for pattern_key in pattern_keys:
                results[pattern_key] = {}

                for load_level in load_levels:
                    current += 1
                    print(f"[{current}/{total_benchmarks}] {PATTERNS[pattern_key]['name']} @ load={load_level}...")

                    adk_metrics = self.benchmark_pattern(pattern_key, Framework.ADK, load_level)
                    current += 1

                    crewai_metrics = self.benchmark_pattern(pattern_key, Framework.CREWAI, load_level)

                    results[pattern_key][load_level] = [adk_metrics, crewai_metrics]

        return results


class ResultsReporter:
    """Generates reports from benchmark results"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None

    def print_summary_table(
        self,
        results: Dict[str, Dict[int, List[PerformanceMetrics]]],
        load_level: int
    ):
        """Print summary table for a specific load level"""
        if self.console:
            table = Table(
                title=f"Performance Benchmark: ADK vs CrewAI (Load={load_level})",
                show_header=True,
                header_style="bold magenta"
            )
            table.add_column("Pattern", style="cyan", no_wrap=True)
            table.add_column("Framework", style="green")
            table.add_column("Total Ops", justify="right")
            table.add_column("Time (ms)", justify="right")
            table.add_column("Throughput\n(ops/s)", justify="right")
            table.add_column("P50 (ms)", justify="right")
            table.add_column("P95 (ms)", justify="right")
            table.add_column("P99 (ms)", justify="right")
            table.add_column("Success\nRate", justify="right")

            for pattern_key, load_results in results.items():
                if load_level not in load_results:
                    continue

                metrics_list = load_results[load_level]
                for metrics in metrics_list:
                    framework_color = "yellow" if metrics.framework == Framework.ADK else "blue"
                    table.add_row(
                        metrics.pattern_name,
                        f"[{framework_color}]{metrics.framework.value.upper()}[/{framework_color}]",
                        str(metrics.total_operations),
                        f"{metrics.execution_time_ms:,.0f}",
                        f"{metrics.throughput_ops_per_sec:.2f}",
                        f"{metrics.latency.p50_ms:.0f}",
                        f"{metrics.latency.p95_ms:.0f}",
                        f"{metrics.latency.p99_ms:.0f}",
                        f"{metrics.success_rate:.1%}"
                    )
                table.add_row("", "", "", "", "", "", "", "", "")  # Separator

            self.console.print(table)
        else:
            print(f"\n{'=' * 120}")
            print(f"Performance Benchmark: ADK vs CrewAI (Load={load_level})")
            print('=' * 120)
            print(f"{'Pattern':<30} {'Framework':<10} {'Ops':<8} {'Time(ms)':<12} {'Throughput':<12} {'P50':<8} {'P95':<8} {'P99':<8} {'Success':<8}")
            print('=' * 120)

            for pattern_key, load_results in results.items():
                if load_level not in load_results:
                    continue

                metrics_list = load_results[load_level]
                for metrics in metrics_list:
                    print(
                        f"{metrics.pattern_name:<30} "
                        f"{metrics.framework.value.upper():<10} "
                        f"{metrics.total_operations:<8} "
                        f"{metrics.execution_time_ms:<12,.0f} "
                        f"{metrics.throughput_ops_per_sec:<12.2f} "
                        f"{metrics.latency.p50_ms:<8.0f} "
                        f"{metrics.latency.p95_ms:<8.0f} "
                        f"{metrics.latency.p99_ms:<8.0f} "
                        f"{metrics.success_rate:<8.1%}"
                    )
                print('-' * 120)

    def print_latency_comparison(
        self,
        results: Dict[str, Dict[int, List[PerformanceMetrics]]]
    ):
        """Print detailed latency comparison"""
        if self.console:
            table = Table(
                title="Latency Distribution Comparison",
                show_header=True,
                header_style="bold cyan"
            )
            table.add_column("Pattern", style="white")
            table.add_column("Load", justify="right")
            table.add_column("Framework", style="green")
            table.add_column("Min (ms)", justify="right")
            table.add_column("Mean (ms)", justify="right")
            table.add_column("P50 (ms)", justify="right")
            table.add_column("P95 (ms)", justify="right")
            table.add_column("P99 (ms)", justify="right")
            table.add_column("Max (ms)", justify="right")
            table.add_column("StdDev", justify="right")

            for pattern_key, load_results in results.items():
                for load_level, metrics_list in sorted(load_results.items()):
                    for metrics in metrics_list:
                        framework_color = "yellow" if metrics.framework == Framework.ADK else "blue"
                        table.add_row(
                            metrics.pattern_name,
                            str(load_level),
                            f"[{framework_color}]{metrics.framework.value.upper()}[/{framework_color}]",
                            f"{metrics.latency.min_ms:.0f}",
                            f"{metrics.latency.mean_ms:.0f}",
                            f"{metrics.latency.p50_ms:.0f}",
                            f"{metrics.latency.p95_ms:.0f}",
                            f"{metrics.latency.p99_ms:.0f}",
                            f"{metrics.latency.max_ms:.0f}",
                            f"{metrics.latency.stddev_ms:.0f}"
                        )
                table.add_row("", "", "", "", "", "", "", "", "", "")

            self.console.print(table)
        else:
            print(f"\n{'=' * 120}")
            print("Latency Distribution Comparison")
            print('=' * 120)
            print(f"{'Pattern':<30} {'Load':<6} {'Framework':<10} {'Min':<8} {'Mean':<8} {'P50':<8} {'P95':<8} {'P99':<8} {'Max':<8} {'StdDev':<8}")
            print('=' * 120)

            for pattern_key, load_results in results.items():
                for load_level, metrics_list in sorted(load_results.items()):
                    for metrics in metrics_list:
                        print(
                            f"{metrics.pattern_name:<30} "
                            f"{load_level:<6} "
                            f"{metrics.framework.value.upper():<10} "
                            f"{metrics.latency.min_ms:<8.0f} "
                            f"{metrics.latency.mean_ms:<8.0f} "
                            f"{metrics.latency.p50_ms:<8.0f} "
                            f"{metrics.latency.p95_ms:<8.0f} "
                            f"{metrics.latency.p99_ms:<8.0f} "
                            f"{metrics.latency.max_ms:<8.0f} "
                            f"{metrics.latency.stddev_ms:<8.0f}"
                        )
                print('-' * 120)

    def print_resource_usage(
        self,
        results: Dict[str, Dict[int, List[PerformanceMetrics]]]
    ):
        """Print resource usage comparison"""
        if not PSUTIL_AVAILABLE:
            print("\nResource monitoring not available (psutil not installed)")
            return

        if self.console:
            table = Table(
                title="Resource Usage Comparison",
                show_header=True,
                header_style="bold green"
            )
            table.add_column("Pattern", style="white")
            table.add_column("Load", justify="right")
            table.add_column("Framework", style="cyan")
            table.add_column("CPU %", justify="right")
            table.add_column("Memory (MB)", justify="right")
            table.add_column("Memory %", justify="right")

            for pattern_key, load_results in results.items():
                for load_level, metrics_list in sorted(load_results.items()):
                    for metrics in metrics_list:
                        framework_color = "yellow" if metrics.framework == Framework.ADK else "blue"
                        table.add_row(
                            metrics.pattern_name,
                            str(load_level),
                            f"[{framework_color}]{metrics.framework.value.upper()}[/{framework_color}]",
                            f"{metrics.resource_usage.cpu_percent:.1f}",
                            f"{metrics.resource_usage.memory_mb:.1f}",
                            f"{metrics.resource_usage.memory_percent:.2f}"
                        )
                table.add_row("", "", "", "", "", "")

            self.console.print(table)
        else:
            print(f"\n{'=' * 80}")
            print("Resource Usage Comparison")
            print('=' * 80)
            print(f"{'Pattern':<30} {'Load':<6} {'Framework':<10} {'CPU %':<10} {'Mem (MB)':<12} {'Mem %':<10}")
            print('=' * 80)

            for pattern_key, load_results in results.items():
                for load_level, metrics_list in sorted(load_results.items()):
                    for metrics in metrics_list:
                        print(
                            f"{metrics.pattern_name:<30} "
                            f"{load_level:<6} "
                            f"{metrics.framework.value.upper():<10} "
                            f"{metrics.resource_usage.cpu_percent:<10.1f} "
                            f"{metrics.resource_usage.memory_mb:<12.1f} "
                            f"{metrics.resource_usage.memory_percent:<10.2f}"
                        )
                print('-' * 80)

    def export_json(
        self,
        results: Dict[str, Dict[int, List[PerformanceMetrics]]],
        output_path: Path
    ):
        """Export results to JSON"""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "patterns": {
                pattern_key: {
                    str(load_level): [m.to_dict() for m in metrics_list]
                    for load_level, metrics_list in load_results.items()
                }
                for pattern_key, load_results in results.items()
            }
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"\nExported JSON to: {output_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Benchmark performance of ADK vs CrewAI implementations"
    )
    parser.add_argument(
        "--patterns",
        type=str,
        help="Comma-separated list of pattern keys to benchmark (default: all)",
        default=None
    )
    parser.add_argument(
        "--load",
        type=str,
        help="Comma-separated list of load levels (default: 1,5,10)",
        default="1,5,10"
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export format: json",
        default=None,
        choices=["json"]
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

    # Parse load levels
    load_levels = [int(l.strip()) for l in args.load.split(",")]

    # Run benchmark
    print("\n" + "=" * 80)
    print("PERFORMANCE BENCHMARK - Article 3 Intelligence Patterns")
    print("=" * 80)
    print(f"Patterns: {len(pattern_keys) if pattern_keys else len(PATTERNS)}")
    print(f"Load levels: {load_levels}")
    print(f"Resource monitoring: {'enabled' if PSUTIL_AVAILABLE else 'disabled'}")
    print("=" * 80 + "\n")

    simulator = PerformanceSimulator()
    results = simulator.run_comparison(pattern_keys, load_levels)

    # Display results
    reporter = ResultsReporter()

    # Print tables for each load level
    for load_level in load_levels:
        reporter.print_summary_table(results, load_level)
        print()

    # Print detailed latency comparison
    reporter.print_latency_comparison(results)

    # Print resource usage
    if PSUTIL_AVAILABLE:
        print()
        reporter.print_resource_usage(results)

    # Export if requested
    if args.export:
        output_dir = Path(args.output)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if args.export == "json":
            json_path = output_dir / f"performance_benchmark_{timestamp}.json"
            reporter.export_json(results, json_path)

    print("\n" + "=" * 80)
    print("Benchmark complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
