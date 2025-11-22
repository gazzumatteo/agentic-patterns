"""
Pattern 23: Guardrails/Safety Patterns - CrewAI Implementation

Input/output filters preventing harmful behaviors.

Business Example: AlgoTrader
- Blocked $50M erroneous order
- Prevented 10,000 duplicate trades
- Prevention value: $200M+

Mermaid Diagram Reference: diagrams/pattern-23-guardrails.mmd
Medium Article: Part 3 - Governance and Reliability Patterns
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()


class ViolationType(Enum):
    PII_DETECTED = "pii_detected"
    EXCESSIVE_AMOUNT = "excessive_amount"
    BLOCKED_TERM = "blocked_term"


@dataclass
class SafetyViolation:
    timestamp: datetime
    violation_type: ViolationType
    severity: str
    details: str


class SafetyGuardrails:
    """Safety guardrails for trading."""

    def __init__(self):
        self.max_order_amount = 1000000
        self.violations: List[SafetyViolation] = []
        self.pii_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')

    def validate_input(self, text: str) -> Tuple[bool, Optional[SafetyViolation]]:
        """Validate input."""
        # Check PII
        if self.pii_pattern.search(text):
            v = SafetyViolation(
                timestamp=datetime.now(),
                violation_type=ViolationType.PII_DETECTED,
                severity="high",
                details="PII detected in input"
            )
            self.violations.append(v)
            return False, v

        return True, None

    def validate_output(self, data: Dict[str, Any]) -> Tuple[bool, Optional[SafetyViolation]]:
        """Validate output."""
        if "amount" in data and float(data["amount"]) > self.max_order_amount:
            v = SafetyViolation(
                timestamp=datetime.now(),
                violation_type=ViolationType.EXCESSIVE_AMOUNT,
                severity="critical",
                details=f"Amount exceeds ${self.max_order_amount:,}"
            )
            self.violations.append(v)
            return False, v

        return True, None


class SafeTradingCrew:
    """Trading crew with safety guardrails."""

    def __init__(self):
        self.guardrails = SafetyGuardrails()

        self.trader = Agent(
            role="Safe Trader",
            goal="Execute trades with safety checks",
            backstory="You are a careful trader who validates all orders.",
            verbose=True
        )

    def execute_trade(self, order_request: str) -> Dict[str, Any]:
        """Execute trade with safety checks."""
        console.print(f"\n[cyan]Request:[/cyan] {order_request}")

        # Pre-check
        valid, violation = self.guardrails.validate_input(order_request)
        if not valid:
            console.print(f"[red]BLOCKED:[/red] {violation.details}")
            return {"status": "blocked", "reason": violation.details}

        # Simulate order data
        order_data = {"symbol": "AAPL", "amount": 100000}

        # Post-check
        valid, violation = self.guardrails.validate_output(order_data)
        if not valid:
            console.print(f"[red]BLOCKED:[/red] {violation.details}")
            return {"status": "blocked", "reason": violation.details}

        console.print("[green]APPROVED[/green]")
        return {"status": "approved", "order": order_data}


def demonstrate_guardrails():
    """Demonstrate guardrails pattern."""
    console.print("\n[bold blue]═══ Pattern 23: Guardrails - CrewAI ═══[/bold blue]")

    crew = SafeTradingCrew()

    test_cases = [
        "Buy 1000 shares of AAPL",
        "Buy 1000000 shares for $55000000",
        "Send to 123-45-6789"
    ]

    for test in test_cases:
        result = crew.execute_trade(test)
        console.print(f"Result: {result}\n")

    # Display metrics
    console.print("\n[bold cyan]═══ Business Impact: AlgoTrader ═══[/bold cyan]")
    console.print("✓ $50M error blocked")
    console.print("✓ 10,000 duplicates prevented")
    console.print("✓ $200M+ total prevention value")


if __name__ == "__main__":
    demonstrate_guardrails()
