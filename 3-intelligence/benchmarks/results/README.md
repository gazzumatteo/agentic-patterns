# Benchmark Results

This directory stores benchmark output files.

## File Naming Convention

### Cost Analysis
- `cost_analysis_YYYYMMDD_HHMMSS.json`
- `cost_analysis_YYYYMMDD_HHMMSS.csv`

### Performance Tests
- `performance_benchmark_YYYYMMDD_HHMMSS.json`

## Retention Policy

Benchmark results are not tracked in git by default. Keep results locally for:
- Historical comparison
- Performance regression analysis
- Cost trend monitoring

## Analyzing Results

### JSON Files

Use `jq` for command-line analysis:

```bash
# View all patterns
cat cost_analysis_*.json | jq '.patterns | keys'

# Compare ADK vs CrewAI for a pattern
cat cost_analysis_*.json | jq '.patterns.learning_adaptation'

# Get total cost
cat cost_analysis_*.json | jq '[.patterns[][].estimated_cost_usd] | add'
```

### CSV Files

Import into spreadsheet software or analyze with Python:

```python
import pandas as pd

df = pd.read_csv('cost_analysis_20250118_103000.csv')
print(df.groupby('Framework')['Estimated Cost (USD)'].sum())
```

## CI/CD Integration

For automated benchmarking, commit results to a separate branch:

```bash
git checkout -b benchmark-results
cp results/*.json results/*.csv archived/
git add archived/
git commit -m "Add benchmark results $(date +%Y%m%d)"
git push origin benchmark-results
```
