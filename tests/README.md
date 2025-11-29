# Testing Infrastructure

Comprehensive test suite for all agentic design patterns.

## Structure

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests for pattern workflows
├── fixtures/          # Shared test data and fixtures
└── conftest.py        # Pytest configuration
```

## Running Tests

### All Tests
```bash
uv run pytest
```

### Specific Test File
```bash
uv run pytest tests/unit/test_validators.py
```

### With Coverage
```bash
uv run pytest --cov=. --cov-report=html
```

### Verbose Output
```bash
uv run pytest -v
```

## Test Categories

### Unit Tests (`tests/unit/`)
- Test individual functions and classes
- Mock external dependencies
- Fast execution
- High code coverage

### Integration Tests (`tests/integration/`)
- Test complete workflows
- Test pattern combinations
- Test framework integrations (ADK, CrewAI)
- May use real API calls (with rate limiting)

### Fixtures (`tests/fixtures/`)
- Sample data files
- Mock responses
- Test configurations

## Writing Tests

### Test Naming Convention
- File: `test_<module>.py`
- Class: `Test<Feature>`
- Method: `test_<scenario>`

### Example
```python
import pytest
from mymodule import my_function

class TestMyFunction:
    def test_normal_case(self):
        """Test normal operation."""
        result = my_function(input_data)
        assert result == expected

    def test_edge_case(self):
        """Test edge case."""
        with pytest.raises(ValueError):
            my_function(invalid_data)
```

## Continuous Integration

Tests run automatically on:
- Every commit
- Pull requests
- Pre-merge checks

## Coverage Goals

- Overall: >80%
- Critical paths: >95%
- New code: 100%
