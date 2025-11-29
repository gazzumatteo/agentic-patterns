"""
Unit tests for helper utilities.
"""

import pytest
from shared_utilities.common_tools.helpers import (
    format_currency,
    calculate_percentage,
    truncate_text,
    extract_keywords,
    format_duration,
    batch_items,
)


class TestCurrencyFormatting:
    """Test currency formatting."""

    def test_usd_formatting(self):
        """Test USD formatting."""
        assert format_currency(1234.56, "USD") == "$1,234.56"
        assert format_currency(0.99, "USD") == "$0.99"

    def test_other_currencies(self):
        """Test other currency symbols."""
        assert format_currency(1000, "EUR") == "€1,000.00"
        assert format_currency(1000, "GBP") == "£1,000.00"


class TestPercentageCalculation:
    """Test percentage calculations."""

    def test_normal_percentage(self):
        """Test normal percentage calculation."""
        assert calculate_percentage(50, 200) == 25.0
        assert calculate_percentage(100, 100) == 100.0

    def test_zero_whole(self):
        """Test handling of zero denominator."""
        assert calculate_percentage(50, 0) == 0.0


class TestTextTruncation:
    """Test text truncation."""

    def test_short_text(self):
        """Test that short text is not truncated."""
        text = "Short text"
        assert truncate_text(text, 100) == text

    def test_long_text(self):
        """Test that long text is truncated."""
        text = "A" * 200
        result = truncate_text(text, 50)
        assert len(result) <= 50
        assert result.endswith("...")


class TestKeywordExtraction:
    """Test keyword extraction."""

    def test_extract_keywords(self):
        """Test basic keyword extraction."""
        text = "machine learning python data science artificial intelligence"
        keywords = extract_keywords(text, max_keywords=3)
        assert len(keywords) <= 3
        assert all(isinstance(k, str) for k in keywords)


class TestDurationFormatting:
    """Test duration formatting."""

    def test_seconds(self):
        """Test formatting seconds."""
        assert format_duration(30.5) == "30.5s"

    def test_minutes(self):
        """Test formatting minutes."""
        assert format_duration(90) == "1.5m"

    def test_hours(self):
        """Test formatting hours."""
        assert format_duration(7200) == "2.0h"


class TestBatching:
    """Test item batching."""

    def test_exact_batches(self):
        """Test batching with exact division."""
        items = list(range(10))
        batches = batch_items(items, 5)
        assert len(batches) == 2
        assert all(len(b) == 5 for b in batches)

    def test_uneven_batches(self):
        """Test batching with remainder."""
        items = list(range(11))
        batches = batch_items(items, 5)
        assert len(batches) == 3
        assert len(batches[-1]) == 1  # Last batch has remainder
