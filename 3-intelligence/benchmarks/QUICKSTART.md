# Quick Start Guide - Benchmarks

Get started with benchmarking in under 2 minutes.

## Installation

No installation needed! The scripts use PEP 723 inline dependencies:

```bash
cd 3-intelligence/benchmarks
```

## Run Your First Benchmark

### Cost Analysis (Fast - ~5 seconds)

```bash
# Benchmark all patterns
uv run cost_analysis/compare_frameworks.py

# Benchmark specific patterns
uv run cost_analysis/compare_frameworks.py --patterns learning_adaptation,prioritization
```

### Performance Test (Medium - ~30 seconds)

```bash
# Benchmark all patterns
uv run performance_tests/benchmark_patterns.py

# Quick test with fewer patterns
uv run performance_tests/benchmark_patterns.py --patterns prioritization --load 1,5
```

## Understanding the Output

### Cost Analysis Shows:
- **Total Tokens** - ADK uses ~26% more tokens (richer context)
- **API Calls** - ADK makes ~33% fewer calls (better batching)
- **Cost** - Usually $0 with free tier models

**Key Insight:** ADK is more token-intensive but makes fewer API calls.

### Performance Test Shows:
- **Throughput** - ADK is ~20-35% faster
- **P95 Latency** - Critical metric for SLAs
- **Success Rate** - Both frameworks achieve >95%

**Key Insight:** ADK has lower latency and higher throughput.

## Export Results

```bash
# Export to JSON
uv run cost_analysis/compare_frameworks.py --export json --output results/

# Export to CSV
uv run cost_analysis/compare_frameworks.py --export csv --output results/

# Export to both
uv run cost_analysis/compare_frameworks.py --export both --output results/
```

Results saved in `results/` directory with timestamp.

## Quick Decision Guide

### Use ADK if:
- Pattern has many iterations (>5)
- Minimizing API calls matters
- Need lowest latency
- Complex state management

### Use CrewAI if:
- Tasks are independent
- Crew abstraction fits well
- Prefer simpler code
- Parallel execution needed

## Pattern Keys

Available patterns:
- `learning_adaptation`
- `exploration_discovery`
- `evolutionary_curriculum`
- `resource_optimization`
- `prioritization`
- `checkpoint_rollback`
- `exception_handling`
- `goal_monitoring`

## Common Commands

```bash
# Cost analysis with specific model
uv run cost_analysis/compare_frameworks.py --model gemini-1.5-pro

# Performance test with high load
uv run performance_tests/benchmark_patterns.py --load 1,5,10,20

# Quick test (2 patterns, low load)
uv run cost_analysis/compare_frameworks.py --patterns prioritization,exception_handling
uv run performance_tests/benchmark_patterns.py --patterns prioritization --load 1

# Full benchmark with export
uv run cost_analysis/compare_frameworks.py --export both --output results/
uv run performance_tests/benchmark_patterns.py --export json --output results/
```

## What's Being Measured?

### Cost Metrics
- Token usage (input/output)
- API call count
- Estimated costs
- Efficiency ratios

### Performance Metrics
- Execution time
- Throughput (ops/sec)
- Latency (P50, P95, P99)
- Resource usage (CPU, memory)
- Success rates

## Need Help?

```bash
# Show all options
uv run cost_analysis/compare_frameworks.py --help
uv run performance_tests/benchmark_patterns.py --help
```

Read the full [README.md](README.md) for detailed documentation.

## Tips

1. **Start Small** - Test with 1-2 patterns first
2. **Export Results** - Keep history for comparison
3. **Monitor Trends** - Run regularly to catch regressions
4. **Share Results** - Export to CSV for spreadsheet analysis

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [results/README.md](results/README.md) for analyzing exports
- Explore pattern implementations in `../adk-examples/` and `../crewai-examples/`
