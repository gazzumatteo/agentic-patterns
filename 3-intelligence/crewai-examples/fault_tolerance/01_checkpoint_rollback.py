"""
Checkpoint and Rollback Pattern - CrewAI Implementation

This pattern demonstrates how agents create checkpoints before risky operations
and rollback to previous states when errors occur.

Business Use Case: Sensitive Data Management (Services)
An agent managing a customer database creates checkpoints before performing
irreversible changes like bulk deletions or schema migrations, enabling
rollback if issues are detected.

Pattern: Checkpoint and Rollback
Section: IV - Intelligence and Learning Patterns
Framework: CrewAI
"""

import json
import copy
from typing import Dict, Any
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# --- Simulated Database Environment ---
class DatabaseEnvironment:
    """Simulates a customer database with checkpoint/rollback capabilities"""

    def __init__(self):
        self.data = {
            "customers": [
                {"id": 1, "name": "Acme Corp", "status": "active", "balance": 15000},
                {"id": 2, "name": "TechStart Inc", "status": "active", "balance": 8500},
                {"id": 3, "name": "Global Solutions", "status": "inactive", "balance": 0},
                {"id": 4, "name": "Innovation Labs", "status": "active", "balance": 12000},
                {"id": 5, "name": "DataCo", "status": "suspended", "balance": 3000},
            ]
        }
        self.checkpoints: Dict[str, Dict[str, Any]] = {}
        self.operation_log = []

    def get_current_state(self) -> Dict[str, Any]:
        return {
            "total_customers": len(self.data["customers"]),
            "active_customers": len([c for c in self.data["customers"] if c["status"] == "active"]),
            "total_balance": sum(c["balance"] for c in self.data["customers"]),
            "customers": copy.deepcopy(self.data["customers"])
        }

    def create_checkpoint(self, checkpoint_id: str, description: str) -> Dict[str, Any]:
        checkpoint_data = {
            "id": checkpoint_id,
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "state": copy.deepcopy(self.data)
        }
        self.checkpoints[checkpoint_id] = checkpoint_data
        self.operation_log.append({
            "type": "checkpoint_created",
            "checkpoint_id": checkpoint_id,
            "timestamp": checkpoint_data["timestamp"]
        })
        return {
            "checkpoint_id": checkpoint_id,
            "timestamp": checkpoint_data["timestamp"],
            "customers_count": len(self.data["customers"]),
            "description": description
        }

    def execute_bulk_operation(self, operation_type: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        affected_records = 0
        errors = []

        try:
            if operation_type == "delete_inactive":
                initial_count = len(self.data["customers"])
                self.data["customers"] = [c for c in self.data["customers"] if c["status"] != "inactive"]
                affected_records = initial_count - len(self.data["customers"])

            elif operation_type == "update_status":
                old_status = criteria.get("old_status")
                new_status = criteria.get("new_status")
                for customer in self.data["customers"]:
                    if customer["status"] == old_status:
                        customer["status"] = new_status
                        affected_records += 1

            elif operation_type == "delete_zero_balance":
                initial_count = len(self.data["customers"])
                self.data["customers"] = [c for c in self.data["customers"] if c["balance"] > 0]
                affected_records = initial_count - len(self.data["customers"])

            elif operation_type == "corrupt_data":
                raise Exception("Data corruption detected during bulk update!")

            if affected_records > 3:
                errors.append(f"Warning: {affected_records} records affected (threshold: 3)")

            self.operation_log.append({
                "type": "operation_executed",
                "operation": operation_type,
                "affected_records": affected_records,
                "timestamp": datetime.now().isoformat()
            })

            return {
                "success": True if not errors else False,
                "operation": operation_type,
                "affected_records": affected_records,
                "remaining_customers": len(self.data["customers"]),
                "errors": errors
            }

        except Exception as e:
            self.operation_log.append({
                "type": "operation_failed",
                "operation": operation_type,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return {
                "success": False,
                "operation": operation_type,
                "affected_records": 0,
                "errors": [str(e)]
            }

    def rollback_to_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        if checkpoint_id not in self.checkpoints:
            return {
                "success": False,
                "error": f"Checkpoint {checkpoint_id} not found"
            }

        checkpoint = self.checkpoints[checkpoint_id]
        self.data = copy.deepcopy(checkpoint["state"])

        self.operation_log.append({
            "type": "rollback_executed",
            "checkpoint_id": checkpoint_id,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "success": True,
            "checkpoint_id": checkpoint_id,
            "checkpoint_timestamp": checkpoint["timestamp"],
            "restored_customers": len(self.data["customers"]),
            "description": checkpoint["description"]
        }


# Initialize database environment
db_env = DatabaseEnvironment()


# --- Custom Tools ---
class GetDatabaseStateTool(BaseTool):
    name: str = "get_database_state"
    description: str = "Get the current state of the database including customer counts and balances"

    def _run(self) -> str:
        state = db_env.get_current_state()
        return json.dumps(state, indent=2)


class CreateCheckpointInput(BaseModel):
    checkpoint_id: str = Field(..., description="Unique identifier for this checkpoint")
    description: str = Field(..., description="Description of what operation this checkpoint protects")


class CreateCheckpointTool(BaseTool):
    name: str = "create_checkpoint"
    description: str = "Create a checkpoint of the current database state before risky operations"

    def _run(self, checkpoint_id: str, description: str) -> str:
        result = db_env.create_checkpoint(checkpoint_id, description)
        return json.dumps(result, indent=2)


class ExecuteOperationInput(BaseModel):
    operation_type: str = Field(..., description="Type of operation")
    criteria: Dict[str, Any] = Field(..., description="Operation-specific criteria")


class ExecuteOperationTool(BaseTool):
    name: str = "execute_database_operation"
    description: str = "Execute a bulk database operation that could be risky"

    def _run(self, operation_type: str, criteria: Dict[str, Any]) -> str:
        result = db_env.execute_bulk_operation(operation_type, criteria)
        return json.dumps(result, indent=2)


class RollbackInput(BaseModel):
    checkpoint_id: str = Field(..., description="ID of the checkpoint to restore")


class RollbackTool(BaseTool):
    name: str = "rollback_to_checkpoint"
    description: str = "Rollback the database to a previous checkpoint state"

    def _run(self, checkpoint_id: str) -> str:
        result = db_env.rollback_to_checkpoint(checkpoint_id)
        return json.dumps(result, indent=2)


# Initialize tools
state_tool = GetDatabaseStateTool()
checkpoint_tool = CreateCheckpointTool()
operation_tool = ExecuteOperationTool()
rollback_tool = RollbackTool()


# --- Agents ---
def create_pre_operation_agent() -> Agent:
    return Agent(
        role="Pre-Operation Safety Checker",
        goal="Create checkpoints before risky database operations",
        backstory="""You are a Database Safety specialist who ensures data
        protection by creating checkpoints before any risky operation. You
        analyze operations and create safety points for recovery.""",
        tools=[state_tool, checkpoint_tool],
        verbose=True,
        allow_delegation=False
    )


def create_operation_executor() -> Agent:
    return Agent(
        role="Database Operation Executor",
        goal="Execute database operations and monitor for errors",
        backstory="""You are a Database Operations specialist who executes
        bulk operations carefully and monitors for any issues or warnings.""",
        tools=[operation_tool],
        verbose=True,
        allow_delegation=False
    )


def create_rollback_decision_maker() -> Agent:
    return Agent(
        role="Rollback Decision Maker",
        goal="Decide if rollback is needed and execute it if necessary",
        backstory="""You are a Database Recovery specialist who reviews
        operation results and determines if rollback is necessary for safety.
        You always prioritize data integrity over operation completion.""",
        tools=[rollback_tool, state_tool],
        verbose=True,
        allow_delegation=False
    )


# --- Main Execution ---
def run_checkpoint_rollback_demo():
    """Demonstrate checkpoint and rollback pattern with different scenarios"""
    global db_env
    
    print("=" * 80)
    print("Checkpoint and Rollback Pattern - Sensitive Data Management")
    print("=" * 80)

    scenarios = [
        {
            "name": "Safe Bulk Delete Operation",
            "operation": "delete_inactive",
            "criteria": {}
        },
        {
            "name": "Risky Operation with Rollback",
            "operation": "update_status",
            "criteria": {"old_status": "active", "new_status": "archived"}
        }
    ]

    for idx, scenario in enumerate(scenarios, 1):
        print(f"\n{'=' * 80}")
        print(f"Scenario {idx}: {scenario['name']}")
        print(f"{'=' * 80}")

        # Reset database for each scenario
        if idx > 1:
            db_env = DatabaseEnvironment()

        print(f"\nInitial Database State:")
        print(json.dumps(db_env.get_current_state(), indent=2))

        # Create agents
        pre_op = create_pre_operation_agent()
        executor = create_operation_executor()
        rollback_maker = create_rollback_decision_maker()

        # Create tasks
        checkpoint_task = Task(
            description=f"""Prepare for {scenario['operation']} operation:
            1. Get current database state
            2. Create checkpoint with ID 'checkpoint_{idx:03d}'
            3. Description should explain the operation being protected""",
            agent=pre_op,
            expected_output="Checkpoint created with confirmation"
        )

        execute_task = Task(
            description=f"""Execute database operation:
            Operation: {scenario['operation']}
            Criteria: {scenario['criteria']}
            
            Execute the operation and report results including:
            - Success status
            - Affected records
            - Any errors or warnings""",
            agent=executor,
            expected_output="Operation execution results",
            context=[checkpoint_task]
        )

        rollback_task = Task(
            description=f"""Review operation results and decide on rollback:
            1. Check if operation had errors or warnings
            2. If errors exist or affected records > 3, perform rollback to checkpoint_{idx:03d}
            3. If no issues, confirm operation success
            4. Verify final database state""",
            agent=rollback_maker,
            expected_output="Rollback decision and final state confirmation",
            context=[execute_task]
        )

        # Create crew
        crew = Crew(
            agents=[pre_op, executor, rollback_maker],
            tasks=[checkpoint_task, execute_task, rollback_task],
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

        print(f"\nFinal Database State:")
        print(json.dumps(db_env.get_current_state(), indent=2))

    print(f"\n{'=' * 80}")
    print("Pattern Demonstration Complete")
    print(f"{'=' * 80}")
    print("""
Key Observations:
1. Checkpoint Creation: Automatic checkpoints before risky operations
2. Safe Execution: Operations proceed with safety net in place
3. Error Detection: Monitors operation results for failures or warnings
4. Automatic Rollback: Restores previous state when issues detected
5. State Preservation: All checkpoint data maintained for audit trail
""")


if __name__ == "__main__":
    run_checkpoint_rollback_demo()
