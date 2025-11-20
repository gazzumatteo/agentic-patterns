"""
Common helper utilities for agentic systems.
"""

from typing import Any, Dict, List
from datetime import datetime, timedelta


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency string.

    Args:
        amount: Numeric amount
        currency: Currency code (USD, EUR, etc.)

    Returns:
        Formatted currency string
    """
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥"}
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def calculate_percentage(part: float, whole: float) -> float:
    """
    Calculate percentage.

    Args:
        part: Part value
        whole: Whole value

    Returns:
        Percentage (0-100)
    """
    if whole == 0:
        return 0.0
    return (part / whole) * 100


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    Extract keywords from text (simple implementation).

    Args:
        text: Input text
        max_keywords: Maximum number of keywords

    Returns:
        List of keywords
    """
    # Simple keyword extraction: most common words after removing stop words
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
    }

    words = text.lower().split()
    keywords = [w for w in words if w not in stop_words and len(w) > 3]

    # Count frequency
    word_freq: Dict[str, int] = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1

    # Return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:max_keywords]]


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable form.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def batch_items(items: List[Any], batch_size: int) -> List[List[Any]]:
    """
    Split items into batches.

    Args:
        items: List of items to batch
        batch_size: Size of each batch

    Returns:
        List of batches
    """
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]
