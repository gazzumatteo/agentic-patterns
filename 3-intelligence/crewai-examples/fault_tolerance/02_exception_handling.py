"""
Exception Handling and Recovery Pattern - CrewAI Implementation

This pattern demonstrates how agents handle failures gracefully with retry logic,
fallback strategies, and human escalation when automatic recovery fails.

Business Use Case: Supply Chain Error Handling (Manufacturing)
An agent managing supplier API integrations implements retry logic for transient
failures (503 errors, timeouts), fallback strategies (alternate suppliers), and
human escalation for critical issues.

Pattern: Exception Handling and Recovery
Section: IV - Intelligence and Learning Patterns
Framework: CrewAI
"""

import json
import random
from typing import Dict, Any
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# --- Constants ---
MAX_RETRIES = 3


# --- Simulated Supplier API Environment ---
class SupplierAPIEnvironment:
    """Simulates supplier APIs with various failure scenarios"""

    def __init__(self):
        self.primary_supplier = "GlobalParts Inc"
        self.fallback_supplier = "ReliableComponents Ltd"
        self.api_call_count = 0
        self.failure_log = []
        self.escalation_log = []
        self.primary_reliability = 0.6  # 60% success rate
        self.fallback_reliability = 0.9  # 90% success rate

    def call_supplier_api(self, supplier: str, action: str, parameters: Dict[str, Any], retry_attempt: int = 0) -> Dict[str, Any]:
        self.api_call_count += 1

        reliability = self.primary_reliability if supplier == self.primary_supplier else self.fallback_reliability
        success = random.random() < reliability

        if not success:
            error_types = [
                {"code": 503, "message": "Service Temporarily Unavailable", "type": "transient"},
                {"code": 408, "message": "Request Timeout", "type": "transient"},
                {"code": 500, "message": "Internal Server Error", "type": "transient"},
                {"code": 404, "message": "Endpoint Not Found", "type": "permanent"},
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

        # Success
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

        return {
            "success": True,
            "supplier": supplier,
            "action": action,
            "message": "Action completed successfully"
        }

    def escalate_to_human(self, issue_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
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


# Initialize supplier environment
supplier_env = SupplierAPIEnvironment()


# --- Custom Tools ---
class CallAPIInput(BaseModel):
    supplier: str = Field(..., description="Supplier name")
    action: str = Field(..., description="API action")
    parameters: Dict[str, Any] = Field(..., description="Action parameters")
    retry_attempt: int = Field(default=0, description="Current retry attempt")


class CallAPITool(BaseTool):
    name: str = "call_api_with_retry"
    description: str = "Call supplier API with automatic retry logic for transient failures"

    def _run(self, supplier: str, action: str, parameters: Dict[str, Any], retry_attempt: int = 0) -> str:
        result = supplier_env.call_supplier_api(supplier, action, parameters, retry_attempt)
        return json.dumps(result, indent=2)


class ExecuteFallbackInput(BaseModel):
    original_supplier: str = Field(..., description="The supplier that failed")
    fallback_supplier: str = Field(..., description="Alternative supplier to try")
    action: str = Field(..., description="Same action to execute")
    parameters: Dict[str, Any] = Field(..., description="Same parameters")


class ExecuteFallbackTool(BaseTool):
    name: str = "execute_fallback_strategy"
    description: str = "Execute fallback strategy by trying an alternate supplier"

    def _run(self, original_supplier: str, fallback_supplier: str, action: str, parameters: Dict[str, Any]) -> str:
        result = supplier_env.call_supplier_api(fallback_supplier, action, parameters)
        return json.dumps({
            "fallback_executed": True,
            "original_supplier": original_supplier,
            "fallback_supplier": fallback_supplier,
            "result": result
        }, indent=2)


class EscalateInput(BaseModel):
    issue_description: str = Field(..., description="Description of the issue")
    context: Dict[str, Any] = Field(..., description="Context information")


class EscalateTool(BaseTool):
    name: str = "escalate_to_human"
    description: str = "Escalate issue to human operator when automatic recovery fails"

    def _run(self, issue_description: str, context: Dict[str, Any]) -> str:
        escalation = supplier_env.escalate_to_human(issue_description, context)
        return json.dumps(escalation, indent=2)


# Initialize tools
retry_tool = CallAPITool()
fallback_tool = ExecuteFallbackTool()
escalation_tool = EscalateTool()


# --- Agents ---
def create_retry_handler() -> Agent:
    return Agent(
        role="Retry Handler",
        goal=f"Call supplier APIs with retry logic up to {MAX_RETRIES} attempts",
        backstory=f"""You are an API Reliability specialist who handles
        transient failures gracefully. You retry failed API calls up to
        {MAX_RETRIES} times for transient errors like 503, 408, 500.""",
        tools=[retry_tool],
        verbose=True,
        allow_delegation=False
    )


def create_fallback_executor() -> Agent:
    return Agent(
        role="Fallback Strategy Executor",
        goal="Execute fallback strategies when primary supplier fails",
        backstory=f"""You are a Supplier Management specialist who maintains
        backup suppliers. When the primary supplier fails, you switch to
        {supplier_env.fallback_supplier} as a fallback option.""",
        tools=[fallback_tool],
        verbose=True,
        allow_delegation=False
    )


def create_escalation_handler() -> Agent:
    return Agent(
        role="Escalation Handler",
        goal="Escalate unresolvable issues to human operators",
        backstory="""You are an Issue Resolution specialist who knows when
        to escalate problems to humans. You create detailed escalation tickets
        with full context for manual intervention.""",
        tools=[escalation_tool],
        verbose=True,
        allow_delegation=False
    )


# --- Main Execution ---
def run_exception_handling_demo():
    """Demonstrate exception handling pattern"""
    global supplier_env
    
    print("=" * 80)
    print("Exception Handling and Recovery Pattern - Supply Chain Management")
    print("=" * 80)

    scenarios = [
        {
            "name": "API Call with Automatic Retry",
            "supplier": supplier_env.primary_supplier,
            "action": "check_inventory",
            "parameters": {"part_number": "MOTOR-X500", "quantity": 150}
        },
        {
            "name": "Fallback to Alternative Supplier",
            "supplier": supplier_env.primary_supplier,
            "action": "check_inventory",
            "parameters": {"part_number": "SENSOR-Z100", "quantity": 75},
            "force_failure": True
        }
    ]

    for idx, scenario in enumerate(scenarios, 1):
        print(f"\n{'=' * 80}")
        print(f"Scenario {idx}: {scenario['name']}")
        print(f"{'=' * 80}\n")

        if scenario.get("force_failure"):
            supplier_env.primary_reliability = 0.1  # Force failures

        # Create agents
        retry_handler = create_retry_handler()
        fallback_executor = create_fallback_executor()
        escalation_handler = create_escalation_handler()

        # Create tasks
        retry_task = Task(
            description=f"""Call supplier API with retry logic:
            Supplier: {scenario['supplier']}
            Action: {scenario['action']}
            Parameters: {scenario['parameters']}
            
            Try up to {MAX_RETRIES} times for transient failures.
            Report final result including retry attempts.""",
            agent=retry_handler,
            expected_output="API call result with retry information"
        )

        fallback_task = Task(
            description=f"""If primary supplier failed with transient errors:
            Execute fallback to {supplier_env.fallback_supplier}
            
            If successful on primary or fallback, report success.
            If both fail, prepare for escalation.""",
            agent=fallback_executor,
            expected_output="Fallback execution result or success confirmation",
            context=[retry_task]
        )

        escalation_task = Task(
            description="""Review results and escalate if needed:
            If both primary and fallback failed, create escalation ticket
            with full error details and business impact.
            
            Otherwise, confirm successful completion.""",
            agent=escalation_handler,
            expected_output="Escalation ticket or success confirmation",
            context=[fallback_task]
        )

        # Create crew
        crew = Crew(
            agents=[retry_handler, fallback_executor, escalation_handler],
            tasks=[retry_task, fallback_task, escalation_task],
            process=Process.sequential,
            verbose=True
        )

        # Execute
        try:
            result = crew.kickoff()
            print(f"\n[Scenario {idx} Result]")
            print(result)
        except Exception as e:
            print(f"\n[Error in scenario {idx}]: {e}")

        # Reset reliability
        supplier_env.primary_reliability = 0.6

    # Final statistics
    print(f"\n{'=' * 80}")
    print("Session Statistics")
    print(f"{'=' * 80}")
    print(json.dumps(supplier_env.get_failure_statistics(), indent=2))

    print(f"\n{'=' * 80}")
    print("Pattern Demonstration Complete")
    print(f"{'=' * 80}")
    print(f"""
Key Observations:
1. Automatic Retry: Up to {MAX_RETRIES} retries for transient failures
2. Smart Retry Logic: Only retries transient errors
3. Fallback Strategy: Switches to alternative supplier when primary fails
4. Human Escalation: Escalates when all automated recovery fails
5. Error Classification: Distinguishes transient vs permanent errors
""")


if __name__ == "__main__":
    run_exception_handling_demo()
