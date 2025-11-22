"""
Pattern 23: Guardrails/Safety Patterns - Google ADK Implementation

Input/output filters preventing harmful behaviors. Your safety net against prompt
injection, data leakage, and policy violations.

Business Example: AlgoTrader
- Blocked $50M erroneous order (decimal point error)
- Prevented 10,000 duplicate trades (loop bug)
- Stopped PII leakage in reports
- Prevention value: $200M+

Mermaid Diagram Reference: diagrams/pattern-23-guardrails.mmd
Medium Article: Part 3 - Governance and Reliability Patterns
"""

import asyncio
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai.types import GenerateContentConfig
from google.genai import types
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

load_dotenv()
console = Console()


class ViolationType(Enum):
    """Types of safety violations."""
    PII_DETECTED = "pii_detected"
    EXCESSIVE_AMOUNT = "excessive_amount"
    BLOCKED_TERM = "blocked_term"
    DUPLICATE_REQUEST = "duplicate_request"
    RATE_LIMIT = "rate_limit"


@dataclass
class SafetyViolation:
    """Safety violation record."""
    timestamp: datetime
    violation_type: ViolationType
    severity: str  # low, medium, high, critical
    details: str
    blocked_value: Any


class InputValidator:
    """Validates and sanitizes input."""

    def __init__(self):
        # PII patterns
        self.pii_patterns = {
            "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            "credit_card": re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        }

        # Blocked terms
        self.blocked_terms = [
            "password", "secret_key", "api_key", "private_key"
        ]

    def validate(self, input_text: str) -> tuple[bool, Optional[SafetyViolation]]:
        """Validate input for safety violations."""
        # Check for PII
        for pii_type, pattern in self.pii_patterns.items():
            if pattern.search(input_text):
                return False, SafetyViolation(
                    timestamp=datetime.now(),
                    violation_type=ViolationType.PII_DETECTED,
                    severity="high",
                    details=f"Detected {pii_type} in input",
                    blocked_value=pii_type
                )

        # Check for blocked terms
        for term in self.blocked_terms:
            if term.lower() in input_text.lower():
                return False, SafetyViolation(
                    timestamp=datetime.now(),
                    violation_type=ViolationType.BLOCKED_TERM,
                    severity="high",
                    details=f"Blocked term detected: {term}",
                    blocked_value=term
                )

        return True, None


class OutputFilter:
    """Filters output for safety compliance."""

    def __init__(self):
        self.max_order_amount = 1000000  # $1M limit
        self.pii_patterns = InputValidator().pii_patterns

    def filter(self, output: Dict[str, Any]) -> tuple[bool, Optional[SafetyViolation]]:
        """Filter output for safety violations."""
        # Check order amounts
        if "amount" in output and output["amount"] is not None:
            amount = float(output["amount"])
            if amount > self.max_order_amount:
                return False, SafetyViolation(
                    timestamp=datetime.now(),
                    violation_type=ViolationType.EXCESSIVE_AMOUNT,
                    severity="critical",
                    details=f"Order amount ${amount:,.2f} exceeds limit ${self.max_order_amount:,.2f}",
                    blocked_value=amount
                )

        # Check for PII in output
        output_str = str(output)
        for pii_type, pattern in self.pii_patterns.items():
            if pattern.search(output_str):
                return False, SafetyViolation(
                    timestamp=datetime.now(),
                    violation_type=ViolationType.PII_DETECTED,
                    severity="high",
                    details=f"Output contains {pii_type}",
                    blocked_value=pii_type
                )

        return True, None


class DuplicateDetector:
    """Detects duplicate requests."""

    def __init__(self, window_seconds: int = 60):
        self.window_seconds = window_seconds
        self.request_history: List[tuple[datetime, str]] = []

    def is_duplicate(self, request: str) -> bool:
        """Check if request is a duplicate within time window."""
        now = datetime.now()

        # Clean old requests
        self.request_history = [
            (ts, req) for ts, req in self.request_history
            if (now - ts).total_seconds() < self.window_seconds
        ]

        # Check for duplicates
        for ts, prev_request in self.request_history:
            if prev_request == request:
                return True

        # Add to history
        self.request_history.append((now, request))
        return False


class SafetyGuardrails:
    """Complete safety guardrails system."""

    def __init__(self):
        self.input_validator = InputValidator()
        self.output_filter = OutputFilter()
        self.duplicate_detector = DuplicateDetector()
        self.violations: List[SafetyViolation] = []

        console.print("[green]✓[/green] Safety Guardrails initialized")

    def pre_process(self, input_text: str) -> tuple[bool, Optional[SafetyViolation]]:
        """Pre-process validation."""
        # Check for duplicates
        if self.duplicate_detector.is_duplicate(input_text):
            violation = SafetyViolation(
                timestamp=datetime.now(),
                violation_type=ViolationType.DUPLICATE_REQUEST,
                severity="medium",
                details="Duplicate request detected within time window",
                blocked_value=input_text[:50]
            )
            self.violations.append(violation)
            return False, violation

        # Validate input
        valid, violation = self.input_validator.validate(input_text)
        if not valid:
            self.violations.append(violation)

        return valid, violation

    def post_process(self, output: Dict[str, Any]) -> tuple[bool, Optional[SafetyViolation]]:
        """Post-process filtering."""
        valid, violation = self.output_filter.filter(output)
        if not valid:
            self.violations.append(violation)

        return valid, violation

    def get_violations(self) -> List[SafetyViolation]:
        """Get all violations."""
        return self.violations


class SafeTradingAgent:
    """Trading agent with safety guardrails."""

    def __init__(self):
        self.guardrails = SafetyGuardrails()

        self.agent = LlmAgent(
            name="TradingAgent",
            model="gemini-2.5-flash"
        )

        console.print("[green]✓[/green] Safe Trading Agent initialized")

    async def execute_trade(self, order_request: str) -> Dict[str, Any]:
        """Execute trade with safety checks."""
        console.print(f"\n[cyan]Trade Request:[/cyan] {order_request}")

        # Pre-process validation
        valid, violation = self.guardrails.pre_process(order_request)
        if not valid:
            console.print(f"[red]BLOCKED:[/red] {violation.details}")
            return {
                "status": "blocked",
                "reason": violation.details,
                "violation_type": violation.violation_type.value
            }

        # Simulate trade execution
        app_name = "agentic_patterns"
        runner = InMemoryRunner(agent=self.agent, app_name=app_name)
        session = await runner.session_service.create_session(
            app_name=app_name,
            user_id="trader"
        )

        prompt = f"""Parse this trade order and extract details: {order_request}

Return JSON with: symbol, action (buy/sell), quantity, amount"""

        content = types.Content(role='user', parts=[types.Part(text=prompt)])
        events = runner.run_async(
            user_id="trader",
            session_id=session.id,
            new_message=content
        )

        result_text = None
        async for event in events:
            if event.is_final_response() and event.content:
                result_text = event.content.parts[0].text
                break

        # Parse response (simplified)
        try:
            import json
            if result_text:
                # Extract JSON from response
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    order_data = json.loads(result_text[json_start:json_end])
                else:
                    order_data = {"amount": 100000}
            else:
                order_data = {"amount": 100000}
        except:
            order_data = {"amount": 100000}

        # Post-process filtering
        valid, violation = self.guardrails.post_process(order_data)
        if not valid:
            console.print(f"[red]BLOCKED:[/red] {violation.details}")
            return {
                "status": "blocked",
                "reason": violation.details,
                "violation_type": violation.violation_type.value,
                "attempted_order": order_data
            }

        # Trade approved
        console.print(f"[green]APPROVED:[/green] Trade executed")
        return {
            "status": "approved",
            "order_data": order_data
        }


async def demonstrate_guardrails_pattern():
    """Demonstrate guardrails safety pattern."""
    console.print("\n[bold blue]═══ Pattern 23: Guardrails/Safety ═══[/bold blue]")
    console.print("[bold]Business: AlgoTrader - Trading Safety[/bold]\n")

    agent = SafeTradingAgent()

    # Test cases
    test_cases = [
        {
            "request": "Buy 1000 shares of AAPL at market price",
            "expected": "approved"
        },
        {
            "request": "Buy 1000000 shares of TSLA for $55000000",
            "expected": "blocked - excessive amount"
        },
        {
            "request": "Buy 1000 shares of AAPL at market price",
            "expected": "blocked - duplicate"
        },
        {
            "request": "Send report to john.doe@email.com with account 123-45-6789",
            "expected": "blocked - PII"
        }
    ]

    results = []
    for test in test_cases:
        result = await agent.execute_trade(test["request"])
        results.append(result)

        console.print(Panel(
            f"Status: {result['status'].upper()}\n"
            f"Expected: {test['expected']}",
            title=f"[bold]Test Result[/bold]",
            border_style="green" if result['status'] == "approved" else "red"
        ))

    # Display violations
    display_violations(agent.guardrails)

    # Display business metrics
    display_business_metrics()


def display_violations(guardrails: SafetyGuardrails):
    """Display safety violations."""
    table = Table(title="Safety Violations Detected")
    table.add_column("Time", style="cyan")
    table.add_column("Type", style="red")
    table.add_column("Severity", style="yellow")
    table.add_column("Details", style="white", max_width=50)

    for v in guardrails.get_violations():
        table.add_row(
            v.timestamp.strftime('%H:%M:%S'),
            v.violation_type.value,
            v.severity,
            v.details
        )

    console.print(f"\n{table}")


def display_business_metrics():
    """Display AlgoTrader business impact."""
    console.print("\n[bold cyan]═══ Business Impact: AlgoTrader ═══[/bold cyan]")

    metrics = Table(title="Trading Safety Metrics")
    metrics.add_column("Incident Type", style="cyan")
    metrics.add_column("Prevention", style="green")
    metrics.add_column("Value Saved", style="yellow")

    metrics.add_row("Decimal Point Error", "$50M order blocked", "$50M")
    metrics.add_row("Loop Bug", "10,000 duplicates blocked", "$100M+")
    metrics.add_row("PII Leakage", "Reports sanitized", "Compliance")
    metrics.add_row("Total Prevention Value", "Multiple incidents", "$200M+")

    console.print(metrics)

    console.print("\n[bold green]Key Guardrail Benefits:[/bold green]")
    console.print("✓ Prevent catastrophic errors before execution")
    console.print("✓ PII detection prevents data breaches")
    console.print("✓ Amount limits catch decimal errors")
    console.print("✓ Duplicate detection stops runaway loops")


if __name__ == "__main__":
    asyncio.run(demonstrate_guardrails_pattern())
