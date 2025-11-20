"""
Common validation utilities for agentic systems.
"""

import json
import re
from typing import Any, Dict
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_json(text: str) -> tuple[bool, Dict[str, Any] | None]:
    """
    Validate and parse JSON string.

    Args:
        text: JSON string to validate

    Returns:
        Tuple of (is_valid, parsed_data or None)
    """
    try:
        data = json.loads(text)
        return True, data
    except (json.JSONDecodeError, TypeError):
        return False, None


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (basic US format).

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    # Remove common separators
    cleaned = re.sub(r'[-()\s]', '', phone)
    # Check if it's 10 digits or 11 with country code
    return bool(re.match(r'^\+?1?\d{10}$', cleaned))


def validate_credit_card(card_number: str) -> bool:
    """
    Validate credit card using Luhn algorithm.

    Args:
        card_number: Credit card number (digits only)

    Returns:
        True if valid, False otherwise
    """
    # Remove spaces and dashes
    card_number = re.sub(r'[\s-]', '', card_number)

    if not card_number.isdigit():
        return False

    # Luhn algorithm
    def luhn_check(num: str) -> bool:
        digits = [int(d) for d in num]
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
        return checksum % 10 == 0

    return luhn_check(card_number)
