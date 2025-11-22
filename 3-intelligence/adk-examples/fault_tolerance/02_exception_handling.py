"""
Exception Handling and Recovery Pattern - Google ADK Implementation

This pattern demonstrates how agents handle failures gracefully with retry logic,
fallback strategies, and human escalation when automatic recovery fails.

Business Use Case: Supply Chain Error Handling (Manufacturing)
An agent managing supplier API integrations implements retry logic for transient
failures (503 errors, timeouts), fallback strategies (alternate suppliers), and
human escalation for critical issues.

Pattern: Exception Handling and Recovery
Section: IV - Intelligence and Learning Patterns
Framework: Google ADK
Mermaid Diagram Reference: See diagrams/article-3/exception_handling.mermaid
"""

import asyncio
import json
import random
from typing import Dict, Any, Optional
from datetime import datetime
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import FunctionTool
from google.genai.types import Content, Part


# --- Constants ---
APP_NAME = "exception_handling_app"
USER_ID = "supply_chain_manager"
MODEL = "gemini-2.5-flash-exp"

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1


# --- Simulated Supplier API Environment ---
class SupplierAPIEnvironment:
    """Simulates supplier APIs with various failure scenarios"""

    def __init__(self):
        self.primary_supplier = "GlobalParts Inc"
        self.fallback_supplier = "ReliableComponents Ltd"
        self.api_call_count = 0
        self.failure_log = []
        self.escalation_log = []

        # Simulate API reliability
        self.primary_reliability = 0.6  # 60% success rate (simulates issues)
        self.fallback_reliability = 0.9  # 90% success rate

    def call_supplier_api(
        self,
        supplier: str,
        action: str,
        parameters: Dict[str, Any],
        retry_attempt: int = 0
    ) -> Dict[str, Any]:
        """
        Simulate calling a supplier API with various failure modes.

        Args:
            supplier: Supplier name (primary or fallback)
            action: API action (check_inventory, place_order, get_delivery_time)
            parameters: Action-specific parameters
            retry_attempt: Current retry attempt number

        Returns:
            API response or error information
        """
        self.api_call_count += 1

        # Determine reliability based on supplier
        reliability = (
            self.primary_reliability
            if supplier == self.primary_supplier
            else self.fallback_reliability
        )

        # Simulate random failures based on reliability
        success = random.random() < reliability

        if not success:
            # Randomly choose error type
            error_types = [
                {"code": 503, "message": "Service Temporarily Unavailable", "type": "transient"},
                {"code": 408, "message": "Request Timeout", "type": "transient"},
                {"code": 500, "message": "Internal Server Error", "type": "transient"},
                {"code": 404, "message": "Endpoint Not Found", "type": "permanent"},
                {"code": 401, "message": "Authentication Failed", "type": "permanent"},
            ]
            error = random.choice(error_types)

            failure_info = {
                "success": False,
                "supplier": supplier,
                "action": action,
                "error_code": error["code"],
                "error_message": error["message"],
                "error_type": error["type"],
                "retry_attempt": retry_attempt,
                "timestamp": datetime.now().isoformat(),
                "can_retry": error["type"] == "transient" and retry_attempt < MAX_RETRIES
            }

            self.failure_log.append(failure_info)
            return failure_info

        # Success - return mock data based on action
        if action == "check_inventory":
            return {
                "success": True,
                "supplier": supplier,
                "action": action,
                "part_number": parameters.get("part_number"),
                "available_quantity": random.randint(50, 500),
                "unit_price": round(random.uniform(10, 100), 2),
                "lead_time_days": random.randint(1, 14),
                "timestamp": datetime.now().isoformat()
            }

        elif action == "place_order":
            return {
                "success": True,
                "supplier": supplier,
                "action": action,
                "order_id": f"ORD-{random.randint(10000, 99999)}",
                "part_number": parameters.get("part_number"),
                "quantity": parameters.get("quantity"),
                "total_cost": round(parameters.get("quantity", 0) * random.uniform(10, 100), 2),
                "estimated_delivery": f"{random.randint(3, 10)} business days",
                "timestamp": datetime.now().isoformat()
            }

        elif action == "get_delivery_time":
            return {
                "success": True,
                "supplier": supplier,
                "action": action,
                "order_id": parameters.get("order_id"),
                "current_status": random.choice(["processing", "shipped", "in_transit"]),
                "estimated_arrival": f"{random.randint(1, 5)} days",
                "timestamp": datetime.now().isoformat()
            }

        return {
            "success": True,
            "supplier": supplier,
            "action": action,
            "message": "Action completed successfully"
        }

    def escalate_to_human(self, issue_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Escalate an issue to human operator when automatic recovery fails.

        Args:
            issue_description: Description of the issue
            context: Additional context about the failure

        Returns:
            Escalation confirmation
        """
        escalation_id = f"ESC-{len(self.escalation_log) + 1:04d}"
        escalation = {
            "escalation_id": escalation_id,
            "issue": issue_description,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "status": "pending_human_review",
            "priority": "high" if "critical" in issue_description.lower() else "normal"
        }

        self.escalation_log.append(escalation)
        return escalation

    def get_failure_statistics(self) -> Dict[str, Any]:
        """Get statistics on API failures"""
        if not self.failure_log:
            return {"total_failures": 0, "message": "No failures recorded"}

        transient_failures = len([f for f in self.failure_log if f["error_type"] == "transient"])
        permanent_failures = len([f for f in self.failure_log if f["error_type"] == "permanent"])

        return {
            "total_api_calls": self.api_call_count,
            "total_failures": len(self.failure_log),
            "transient_failures": transient_failures,
            "permanent_failures": permanent_failures,
            "failure_rate": round(len(self.failure_log) / self.api_call_count * 100, 2),
            "escalations": len(self.escalation_log)
        }


# Initialize supplier API environment
supplier_env = SupplierAPIEnvironment()


# --- Tools ---
def call_api_with_retry(
    supplier: str,
    action: str,
    parameters: Dict[str, Any],
    retry_attempt: int = 0
) -> str:
    """
    Call supplier API with automatic retry logic for transient failures.

    Args:
        supplier: Supplier name (e.g., "GlobalParts Inc", "ReliableComponents Ltd")
        action: API action (check_inventory, place_order, get_delivery_time)
        parameters: Action parameters as dict (e.g., {"part_number": "ABC123", "quantity": 100})
        retry_attempt: Current retry attempt (0 for first attempt)

    Returns:
        JSON string with API response or error details including retry capability
    """
    result = supplier_env.call_supplier_api(supplier, action, parameters, retry_attempt)
    return json.dumps(result, indent=2)


def execute_fallback_strategy(
    original_supplier: str,
    fallback_supplier: str,
    action: str,
    parameters: Dict[str, Any]
) -> str:
    """
    Execute fallback strategy by trying an alternate supplier.

    Args:
        original_supplier: The supplier that failed
        fallback_supplier: Alternative supplier to try
        action: Same action to execute with fallback
        parameters: Same parameters for the action

    Returns:
        JSON string with fallback execution result
    """
    print(f"\n⚠️  Executing fallback: {original_supplier} -> {fallback_supplier}")

    result = supplier_env.call_supplier_api(fallback_supplier, action, parameters)

    return json.dumps({
        "fallback_executed": True,
        "original_supplier": original_supplier,
        "fallback_supplier": fallback_supplier,
        "result": result
    }, indent=2)


def escalate_to_human(issue_description: str, context: Dict[str, Any]) -> str:
    """
    Escalate issue to human operator when automatic recovery fails.

    Args:
        issue_description: Clear description of the issue requiring human intervention
        context: Dict with context like failed suppliers, error codes, retry attempts

    Returns:
        JSON string with escalation ticket information
    """
    escalation = supplier_env.escalate_to_human(issue_description, context)
    return json.dumps(escalation, indent=2)


def get_failure_statistics() -> str:
    """
    Get statistics on API failures and recovery attempts.

    Returns:
        JSON string with failure statistics
    """
    stats = supplier_env.get_failure_statistics()
    return json.dumps(stats, indent=2)


# Create FunctionTools
retry_tool = FunctionTool(func=call_api_with_retry)
fallback_tool = FunctionTool(func=execute_fallback_strategy)
escalation_tool = FunctionTool(func=escalate_to_human)
stats_tool = FunctionTool(func=get_failure_statistics)


# --- Agents ---
# Agent 1: Primary API Caller with Retry Logic
retry_agent = LlmAgent(
    model=MODEL,
    name="RetryHandler",
    instruction=f"""You are a Retry Handler for supplier API calls.

Your role:
1. Call the supplier API using call_api_with_retry with the primary supplier
2. If the response shows success=false, check if can_retry=true
3. If can_retry is true and retry_attempt < {MAX_RETRIES}:
   - Wait briefly (mention you're retrying)
   - Call call_api_with_retry again with retry_attempt incremented by 1
   - Repeat up to {MAX_RETRIES} total attempts
4. Store the final result in session state as 'api_result'
5. Set 'needs_fallback' to true if all retries failed with transient errors
6. Set 'needs_escalation' to true if permanent error encountered

Primary supplier: "{supplier_env.primary_supplier}"
Always start with retry_attempt=0 for the first call.""",
    tools=[retry_tool],
)

# Agent 2: Fallback Strategy Executor
fallback_agent = LlmAgent(
    model=MODEL,
    name="FallbackExecutor",
    instruction=f"""You are a Fallback Strategy Executor.

Your role:
1. Check session state for 'needs_fallback' flag
2. If needs_fallback is false, skip and report success
3. If needs_fallback is true:
   - Execute fallback strategy using execute_fallback_strategy
   - Use fallback supplier: "{supplier_env.fallback_supplier}"
   - Use the same action and parameters from the original request
4. Store fallback result in state as 'fallback_result'
5. If fallback also fails, set 'needs_escalation' to true

The fallback supplier is more reliable but may have different pricing.""",
    tools=[fallback_tool],
)

# Agent 3: Human Escalation Handler
escalation_agent = LlmAgent(
    model=MODEL,
    name="EscalationHandler",
    instruction="""You are a Human Escalation Handler.

Your role:
1. Check session state for 'needs_escalation' flag
2. If needs_escalation is false, provide a success summary
3. If needs_escalation is true:
   - Gather all error context from api_result and fallback_result
   - Create a clear issue description for the human operator
   - Call escalate_to_human with detailed context
   - Provide the escalation ticket ID to the user

Include in escalation context:
- All error codes and messages encountered
- Number of retry attempts made
- Whether fallback was attempted
- Business impact (order delays, inventory issues)

Always be clear and professional in escalation messages.""",
    tools=[escalation_tool, stats_tool],
)


# Create sequential workflow
exception_handling_workflow = SequentialAgent(
    name="ExceptionHandlingWorkflow",
    sub_agents=[
        retry_agent,
        fallback_agent,
        escalation_agent
    ]
)


# --- Main Execution ---
async def run_exception_handling_demo():
    """Demonstrate exception handling pattern with various failure scenarios"""
    print("=" * 80)
    print("Exception Handling and Recovery Pattern - Supply Chain Management")
    print("=" * 80)

    # Initialize services
    session_service = InMemorySessionService()

    # Create runner
    runner = Runner(
        agent=exception_handling_workflow,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # Scenario 1: Successful call (may take retries)
    print("\n" + "=" * 80)
    print("Scenario 1: API Call with Automatic Retry")
    print("=" * 80)

    session_id_1 = "inventory_check_session"
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id_1
    )

    user_message_1 = Content(
        parts=[Part(text='Check inventory for part number "MOTOR-X500" with quantity 150 units using the primary supplier.')],
        role="user"
    )

    print("\n📞 Executing: Inventory check (may encounter transient failures)")
    print("-" * 80)

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id_1,
        new_message=user_message_1
    ):
        if event.content and event.content.parts:
            text = event.content.parts[0].text
            if text:
                print(f"\n[{event.author}] {text[:500]}")

    # Scenario 2: Fallback strategy execution
    print("\n\n" + "=" * 80)
    print("Scenario 2: Fallback to Alternative Supplier")
    print("=" * 80)

    session_id_2 = "fallback_order_session"
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id_2
    )

    # Lower primary reliability to trigger fallback
    supplier_env.primary_reliability = 0.1  # Force failures

    user_message_2 = Content(
        parts=[Part(text='Place an order for part number "SENSOR-Z100" quantity 75 units.')],
        role="user"
    )

    print("\n🔄 Executing: Order placement (primary supplier unreliable)")
    print("-" * 80)

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id_2,
        new_message=user_message_2
    ):
        if event.content and event.content.parts:
            text = event.content.parts[0].text
            if text:
                print(f"\n[{event.author}] {text[:600]}")

    # Restore primary reliability
    supplier_env.primary_reliability = 0.6

    # Scenario 3: Human escalation
    print("\n\n" + "=" * 80)
    print("Scenario 3: Critical Failure Requiring Human Escalation")
    print("=" * 80)

    session_id_3 = "escalation_session"
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id_3
    )

    # Force both suppliers to fail
    supplier_env.primary_reliability = 0.0
    supplier_env.fallback_reliability = 0.0

    user_message_3 = Content(
        parts=[Part(text='This is a critical order: place order for part number "CRITICAL-PART-001" quantity 500 units. This is needed for production line shutdown prevention.')],
        role="user"
    )

    print("\n⚠️  Executing: Critical order (both suppliers failing)")
    print("-" * 80)

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id_3,
        new_message=user_message_3
    ):
        if event.content and event.content.parts:
            text = event.content.parts[0].text
            if text:
                print(f"\n[{event.author}] {text[:600]}")

    # Final statistics
    print("\n" + "=" * 80)
    print("Session Statistics")
    print("=" * 80)
    print(json.dumps(supplier_env.get_failure_statistics(), indent=2))

    print("\n" + "=" * 80)
    print("Escalation Log")
    print("=" * 80)
    for escalation in supplier_env.escalation_log:
        print(json.dumps(escalation, indent=2))

    # Summary
    print("\n" + "=" * 80)
    print("Pattern Demonstration Complete")
    print("=" * 80)
    print(f"""
Key Observations:
1. Automatic Retry: Up to {MAX_RETRIES} retries for transient failures (503, 408, 500)
2. Smart Retry Logic: Only retries transient errors, not permanent ones (404, 401)
3. Fallback Strategy: Switches to alternative supplier when primary fails
4. Human Escalation: Escalates to human when all automated recovery fails
5. Error Classification: Distinguishes between transient and permanent errors

Performance Metrics:
- API Calls Made: {supplier_env.api_call_count}
- Total Failures: {len(supplier_env.failure_log)}
- Escalations Created: {len(supplier_env.escalation_log)}
- Recovery Success: Automatic recovery succeeded in scenarios 1-2

Production Considerations:
- Implement exponential backoff for retries
- Add circuit breaker pattern for failing services
- Monitor failure rates and adjust retry policies
- Set up alerts for escalation patterns
- Track supplier SLA compliance
- Implement cost optimization for fallback suppliers
""")


if __name__ == "__main__":
    # Set up Google Cloud credentials before running
    # export GOOGLE_CLOUD_PROJECT="your-project-id"
    # export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

    asyncio.run(run_exception_handling_demo())
