"""
Unit tests for validation utilities.
"""

import pytest
from shared_utilities.common_tools.validators import (
    validate_email,
    validate_json,
    validate_url,
    validate_phone,
    validate_credit_card,
)


class TestEmailValidation:
    """Test email validation."""

    def test_valid_emails(self):
        """Test that valid emails pass validation."""
        assert validate_email("user@example.com")
        assert validate_email("john.doe@company.co.uk")
        assert validate_email("test+tag@domain.com")

    def test_invalid_emails(self):
        """Test that invalid emails fail validation."""
        assert not validate_email("invalid")
        assert not validate_email("@example.com")
        assert not validate_email("user@")
        assert not validate_email("user @example.com")


class TestJsonValidation:
    """Test JSON validation."""

    def test_valid_json(self):
        """Test that valid JSON is parsed correctly."""
        valid, data = validate_json('{"key": "value"}')
        assert valid
        assert data == {"key": "value"}

    def test_invalid_json(self):
        """Test that invalid JSON is rejected."""
        valid, data = validate_json("not json")
        assert not valid
        assert data is None

    def test_empty_json(self):
        """Test empty object."""
        valid, data = validate_json("{}")
        assert valid
        assert data == {}


class TestUrlValidation:
    """Test URL validation."""

    def test_valid_urls(self):
        """Test that valid URLs pass validation."""
        assert validate_url("https://example.com")
        assert validate_url("http://subdomain.example.com/path")
        assert validate_url("https://example.com/path?query=value")

    def test_invalid_urls(self):
        """Test that invalid URLs fail validation."""
        assert not validate_url("not a url")
        assert not validate_url("example.com")  # Missing scheme
        assert not validate_url("http://")  # Missing netloc


class TestPhoneValidation:
    """Test phone number validation."""

    def test_valid_phones(self):
        """Test that valid phone numbers pass validation."""
        assert validate_phone("5551234567")
        assert validate_phone("(555) 123-4567")
        assert validate_phone("+1-555-123-4567")

    def test_invalid_phones(self):
        """Test that invalid phone numbers fail validation."""
        assert not validate_phone("123")
        assert not validate_phone("abc-def-ghij")


class TestCreditCardValidation:
    """Test credit card validation."""

    def test_valid_cards(self):
        """Test that valid credit cards pass validation."""
        # Valid test card numbers (Luhn algorithm compliant)
        assert validate_credit_card("4532015112830366")  # Visa
        assert validate_credit_card("5425233430109903")  # Mastercard

    def test_invalid_cards(self):
        """Test that invalid credit cards fail validation."""
        assert not validate_credit_card("1234567890123456")
        assert not validate_credit_card("not a number")
        assert not validate_credit_card("123")
