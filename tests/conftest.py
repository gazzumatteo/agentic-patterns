"""
Pytest configuration and fixtures for agentic patterns testing.
"""

import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_query():
    """Sample user query for testing."""
    return "best laptop for gaming under $1500"


@pytest.fixture
def sample_product_data():
    """Sample product database for testing."""
    return {
        "LAP001": {
            "name": "Gaming Laptop Pro",
            "category": "laptops",
            "price": 1299.99,
            "stock": 15,
        },
        "LAP002": {
            "name": "Budget Laptop",
            "category": "laptops",
            "price": 499.99,
            "stock": 42,
        },
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "output": "product_search",
        "classification": '{"route": "product_search", "category": "laptops"}',
    }
