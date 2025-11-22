# Article 3 Intelligence Patterns - Benchmarks

Comprehensive benchmark suite for comparing Google ADK and CrewAI implementations of intelligence patterns.

## Overview

This benchmark suite provides two types of analysis:

1. **Cost Analysis** - Token usage, API calls, and estimated costs
2. **Performance Tests** - Execution time, throughput, latency, and resource usage

Both benchmarks use simulation and do not require actual LLM API calls, making them fast and cost-free to run.

## Prerequisites

### Installation

Install dependencies using `uv`:

```bash
# Install required dependencies
uv add pydantic rich psutil
```

Or run scripts directly with inline dependencies:

```bash
# uv automatically installs dependencies from PEP 723 metadata
uv run cost_analysis/compare_frameworks.py
uv run performance_tests/benchmark_patterns.py
```

### Optional Dependencies

- **rich** - Enhanced terminal output with tables and progress bars (recommended)
- **psutil** - Resource monitoring (CPU, memory usage)

Scripts will work without these but with reduced functionality.

## Cost Analysis Benchmark

### What It Measures

The cost analysis benchmark tracks:

- **Token Usage** - Input tokens, output tokens, total tokens per pattern
- **API Calls** - Number of API requests made
- **Estimated Costs** - Cost in USD based on model pricing
- **Cost Efficiency** - Cost per iteration, tokens per iteration
- **Model Distribution** - Which models are used and how often

### Running Cost Analysis

#### Basic Usage

```bash
# Benchmark all patterns with default model (gemini-2.5-flash-exp)
uv run cost_analysis/compare_frameworks.py
```

#### Advanced Options

```bash
# Benchmark specific patterns
uv run cost_analysis/compare_frameworks.py --patterns learning_adaptation,exploration_discovery

# Use different model for cost estimation
uv run cost_analysis/compare_frameworks.py --model gemini-1.5-pro

# Export results to JSON
uv run cost_analysis/compare_frameworks.py --export json --output results/

# Export to both JSON and CSV
uv run cost_analysis/compare_frameworks.py --export both --output results/
```

#### Available Patterns

- `learning_adaptation` - Learning & Adaptation
- `exploration_discovery` - Exploration & Discovery
- `evolutionary_curriculum` - Evolutionary Curriculum
- `resource_optimization` - Resource Aware Optimization
- `prioritization` - Prioritization
- `checkpoint_rollback` - Checkpoint & Rollback
- `exception_handling` - Exception Handling
- `goal_monitoring` - Goal Setting & Monitoring

#### Supported Models

- `gemini-2.5-flash-exp` (default, free tier)
- `gemini-1.5-pro`
- `gemini-1.5-flash`
- `gpt-4`
- `gpt-3.5-turbo`

### Sample Output

```
================================================================================
COST ANALYSIS BENCHMARK - Article 3 Intelligence Patterns
================================================================================
Model: gemini-2.5-flash-exp
Patterns: 8
================================================================================

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Pattern                   ┃ Framework ┃ Iterations┃ API Calls┃ Total Tokens┃ Est. Cost ($)┃ Cost/Iter ($)┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Learning & Adaptation     │ ADK       │ 10        │ 20       │ 24,000     │ 0.000000   │ 0.000000   │
│ Learning & Adaptation     │ CREWAI    │ 10        │ 30       │ 21,000     │ 0.000000   │ 0.000000   │
│                           │           │           │          │            │            │            │
│ Exploration & Discovery   │ ADK       │ 8         │ 16       │ 19,200     │ 0.000000   │ 0.000000   │
│ Exploration & Discovery   │ CREWAI    │ 8         │ 24       │ 16,800     │ 0.000000   │ 0.000000   │
...
```

### Understanding Cost Metrics

#### ADK vs CrewAI Cost Differences

**Google ADK:**
- Lower API call count due to LoopAgent optimization
- Higher token usage due to richer context and detailed instructions
- Better for complex workflows with many iterations
- More efficient API batching

**CrewAI:**
- Higher API call count due to crew management overhead
- Lower token usage per call (more concise)
- Better for simple, discrete tasks
- More modular but less optimized for loops

#### Cost Optimization Strategies

1. **Use Free Tier Models** - `gemini-2.5-flash-exp` for development and testing
2. **Minimize Iterations** - Implement early stopping conditions
3. **Batch Operations** - ADK's LoopAgent is better for iterative patterns
4. **Choose Framework Wisely** - ADK for loops, CrewAI for independent tasks

## Performance Benchmark

### What It Measures

The performance benchmark tracks:

- **Execution Time** - Total time to complete pattern
- **Throughput** - Operations per second
- **Latency Distribution** - P50, P95, P99 percentiles
- **Resource Usage** - CPU and memory consumption (with psutil)
- **Success Rate** - Percentage of successful operations
- **Concurrency Performance** - Behavior under different load levels

### Running Performance Tests

#### Basic Usage

```bash
# Benchmark all patterns with default load levels (1, 5, 10)
uv run performance_tests/benchmark_patterns.py
```

#### Advanced Options

```bash
# Benchmark specific patterns
uv run performance_tests/benchmark_patterns.py --patterns learning_adaptation,prioritization

# Test with custom load levels
uv run performance_tests/benchmark_patterns.py --load 1,5,10,20

# Export results to JSON
uv run performance_tests/benchmark_patterns.py --export json --output results/
```

### Sample Output

```
================================================================================
PERFORMANCE BENCHMARK - Article 3 Intelligence Patterns
================================================================================
Patterns: 8
Load levels: [1, 5, 10]
Resource monitoring: enabled
================================================================================

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ Pattern                   ┃ Framework ┃ Total Ops┃ Time (ms)┃ Throughput ┃ P50 (ms)┃ P95 (ms)┃ P99 (ms)┃ Success┃
┃                           ┃           ┃         ┃          ┃ (ops/s)    ┃        ┃        ┃        ┃ Rate   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━┩
│ Learning & Adaptation     │ ADK       │ 10      │ 7,225    │ 1.38       │ 723    │ 850    │ 865    │ 100.0% │
│ Learning & Adaptation     │ CREWAI    │ 10      │ 9,775    │ 1.02       │ 978    │ 1,150  │ 1,165  │ 95.0%  │
...
```

### Understanding Performance Metrics

#### Key Metrics Explained

**Throughput (ops/s):**
- Number of operations completed per second
- Higher is better
- ADK typically 20-35% faster than CrewAI

**Latency Percentiles:**
- **P50 (Median)** - 50% of requests complete in this time or less
- **P95** - 95% of requests complete in this time or less (critical for SLA)
- **P99** - 99% of requests complete in this time or less (worst-case scenarios)

**Success Rate:**
- Percentage of operations that complete without errors
- Target: > 95% for production systems
- Both frameworks typically achieve > 95%

#### ADK vs CrewAI Performance

**Google ADK:**
- Lower latency (15-30% faster)
- Better throughput for iterative patterns
- More efficient resource usage
- Optimized for loop-based workflows
- Lower overhead per operation

**CrewAI:**
- Higher latency due to crew management
- More overhead for crew initialization
- Better for independent, parallel tasks
- Simpler mental model for discrete operations

#### Load Level Analysis

Test with different concurrent operations:

- **Load 1** - Single sequential execution (baseline)
- **Load 5** - Light concurrent load (typical usage)
- **Load 10** - Heavy concurrent load (stress test)

Higher load levels help identify:
- Concurrency bottlenecks
- Resource contention
- Framework scaling characteristics

### Resource Usage Analysis

When psutil is installed, benchmarks track:

- **CPU Usage** - Percentage of CPU consumed
- **Memory Usage** - Memory in MB and percentage
- **Resource Efficiency** - Operations per MB of memory

**Typical Resource Consumption:**

| Framework | CPU (avg) | Memory (avg) |
|-----------|-----------|--------------|
| ADK       | 15-25%    | 50-100 MB    |
| CrewAI    | 20-35%    | 80-150 MB    |

## Interpreting Results

### When to Use ADK

✅ Use Google ADK when:
- Pattern requires many iterations (> 5)
- Loop-based workflows are central
- Minimizing API calls is critical
- Need lowest possible latency
- Working with complex state management
- Cost optimization is important

**Best Patterns for ADK:**
- Learning & Adaptation
- Evolutionary Curriculum
- Goal Setting & Monitoring
- Checkpoint & Rollback

### When to Use CrewAI

✅ Use CrewAI when:
- Tasks are independent and discrete
- Crew-based mental model fits naturally
- Parallel execution is required
- Simpler code is preferred
- Working with multiple specialized agents
- Each task has distinct responsibilities

**Best Patterns for CrewAI:**
- Prioritization
- Exception Handling
- Resource Optimization (discrete tasks)
- Exploration & Discovery (parallel paths)

## Export Formats

### JSON Export

```bash
uv run cost_analysis/compare_frameworks.py --export json --output results/
```

JSON structure:
```json
{
  "timestamp": "2025-01-18T10:30:00",
  "patterns": {
    "learning_adaptation": [
      {
        "pattern_name": "Learning & Adaptation",
        "framework": "adk",
        "model": "gemini-2.5-flash-exp",
        "iterations": 10,
        "api_calls": 20,
        "tokens": {...},
        "estimated_cost_usd": 0.0
      }
    ]
  }
}
```

### CSV Export

```bash
uv run cost_analysis/compare_frameworks.py --export csv --output results/
```

CSV columns:
- Pattern, Framework, Model, Iterations, API Calls
- Input Tokens, Output Tokens, Total Tokens
- Execution Time (ms), Estimated Cost (USD)
- Cost per Iteration (USD), Tokens per Iteration

## Customization

### Adding New Patterns

Edit the `PATTERNS` dictionary in either script:

```python
PATTERNS = {
    "your_pattern": {
        "category": PatternCategory.LEARNING,
        "name": "Your Pattern Name",
        "iterations": 5,
        "complexity": "medium",
        "base_latency_ms": 600  # Performance test only
    }
}
```

### Complexity Levels

- `low` - Simple patterns (1-3 iterations)
- `medium` - Moderate complexity (4-7 iterations)
- `high` - Complex patterns (8-12 iterations)
- `very_high` - Very complex (12+ iterations)

Complexity affects:
- Token usage estimates
- Execution time simulation
- Resource consumption

### Model Pricing

Update `MODEL_PRICING` dictionary for new models:

```python
MODEL_PRICING = {
    "new-model": {
        "input": 1.0,   # USD per 1M input tokens
        "output": 2.0   # USD per 1M output tokens
    }
}
```

## Troubleshooting

### Common Issues

**Issue: "Rich not available"**
```bash
uv add rich
```

**Issue: "psutil not available"**
```bash
uv add psutil
```
Resource monitoring will be disabled without psutil, but benchmarks will still run.

**Issue: "Invalid pattern keys"**
- Check spelling against available patterns
- Use `--help` to see valid pattern keys

**Issue: Benchmarks too slow**
- Run fewer patterns: `--patterns pattern1,pattern2`
- Use fewer load levels: `--load 1,5`
- Results are simulated, so shouldn't take long

### Getting Help

```bash
# Cost analysis help
uv run cost_analysis/compare_frameworks.py --help

# Performance test help
uv run performance_tests/benchmark_patterns.py --help
```

## Continuous Integration

### Running in CI/CD

Both benchmarks are designed for CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Cost Analysis
  run: |
    uv run 3-intelligence/benchmarks/cost_analysis/compare_frameworks.py \
      --export both --output benchmark-results/

- name: Upload Benchmark Results
  uses: actions/upload-artifact@v3
  with:
    name: benchmark-results
    path: benchmark-results/
```

### Performance Regression Testing

Compare benchmark results over time:

```bash
# Export with timestamp
uv run performance_tests/benchmark_patterns.py \
  --export json \
  --output results/$(date +%Y%m%d)/
```

## Best Practices

### 1. Regular Benchmarking

Run benchmarks:
- Before major refactoring
- After implementing new patterns
- When evaluating framework choices
- During performance optimization

### 2. Cost Monitoring

Track costs for:
- Development vs Production
- Different models
- Pattern complexity growth
- API usage trends

### 3. Performance Baselines

Establish baselines for:
- Acceptable latency (e.g., P95 < 2000ms)
- Minimum throughput (e.g., > 1 ops/sec)
- Success rate targets (e.g., > 95%)
- Resource limits (e.g., < 200MB memory)

### 4. Framework Selection

Choose framework based on:
- Pattern characteristics (iterative vs discrete)
- Performance requirements
- Cost constraints
- Team familiarity
- Ecosystem integration

## Related Documentation

- [Article 3: Intelligence Patterns](../README.md)
- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs/adk)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Pattern Implementation Guide](../../docs/patterns.md)

## Contributing

To add new benchmarks or improve existing ones:

1. Follow existing code structure
2. Add comprehensive docstrings
3. Include sample output in this README
4. Test with all patterns
5. Update changelog

## License

Part of the Agentic Design Patterns educational series.
