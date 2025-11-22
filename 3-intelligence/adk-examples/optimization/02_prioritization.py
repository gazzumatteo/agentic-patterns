"""
Prioritization Pattern - Google ADK Implementation

This pattern demonstrates how agents evaluate tasks based on urgency, importance,
and dependencies to determine optimal execution order.

Business Use Case: Proactive Maintenance (Manufacturing)
The agent assigns maximum urgency to an imminent failure alarm versus routine inspection.

Pattern: Prioritization
Section: III - Governance, Reliability, and Support Patterns
Framework: Google ADK
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import FunctionTool
from google.genai.types import Content, Part


# --- Constants ---
APP_NAME = "prioritization_app"
USER_ID = "maintenance_manager"
MODEL = "gemini-2.5-flash-exp"


# --- Task Management System ---
class MaintenanceTask:
    """Represents a maintenance task with priority attributes"""

    def __init__(self, task_id: str, title: str, task_type: str,
                 urgency: int, importance: int, estimated_hours: float,
                 equipment_id: str, dependencies: List[str] = None):
        self.task_id = task_id
        self.title = title
        self.task_type = task_type  # "failure_alarm", "preventive", "routine", "upgrade"
        self.urgency = urgency  # 1-10 scale
        self.importance = importance  # 1-10 scale
        self.estimated_hours = estimated_hours
        self.equipment_id = equipment_id
        self.dependencies = dependencies or []
        self.priority_score: float = 0.0
        self.execution_order: Optional[int] = None
        self.status: str = "pending"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "type": self.task_type,
            "urgency": self.urgency,
            "importance": self.importance,
            "estimated_hours": self.estimated_hours,
            "equipment_id": self.equipment_id,
            "dependencies": self.dependencies,
            "priority_score": round(self.priority_score, 2),
            "execution_order": self.execution_order,
            "status": self.status
        }


class TaskQueue:
    """Manages maintenance task queue with prioritization"""

    def __init__(self):
        self.tasks: Dict[str, MaintenanceTask] = {}
        self.execution_plan: List[str] = []

    def add_task(self, task: MaintenanceTask):
        """Add task to queue"""
        self.tasks[task.task_id] = task

    def get_all_tasks(self) -> List[MaintenanceTask]:
        """Get all tasks"""
        return list(self.tasks.values())

    def get_task(self, task_id: str) -> Optional[MaintenanceTask]:
        """Get specific task"""
        return self.tasks.get(task_id)

    def update_priority_scores(self):
        """Calculate priority scores for all tasks"""
        for task in self.tasks.values():
            # Priority formula: weighted combination of factors
            urgency_weight = 0.5
            importance_weight = 0.3
            time_weight = 0.2

            # Time factor: shorter tasks get slight boost for quick wins
            time_factor = max(1, 10 - (task.estimated_hours / 2))

            task.priority_score = (
                task.urgency * urgency_weight +
                task.importance * importance_weight +
                time_factor * time_weight
            )

    def create_execution_plan(self) -> List[str]:
        """
        Create execution plan considering priorities and dependencies.
        Returns list of task_ids in execution order.
        """
        # Get tasks sorted by priority
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda t: t.priority_score,
            reverse=True
        )

        execution_order = []
        scheduled = set()

        def can_schedule(task: MaintenanceTask) -> bool:
            """Check if all dependencies are scheduled"""
            return all(dep in scheduled for dep in task.dependencies)

        # Schedule tasks respecting dependencies
        max_iterations = len(sorted_tasks) * 2
        iteration = 0

        while len(execution_order) < len(sorted_tasks) and iteration < max_iterations:
            iteration += 1
            for task in sorted_tasks:
                if task.task_id not in scheduled and can_schedule(task):
                    execution_order.append(task.task_id)
                    scheduled.add(task.task_id)
                    task.execution_order = len(execution_order)

        self.execution_plan = execution_order
        return execution_order


# Initialize task queue
task_queue = TaskQueue()

# Add sample tasks
sample_tasks = [
    MaintenanceTask(
        task_id="T001",
        title="CRITICAL: Bearing temperature alarm on CNC-05",
        task_type="failure_alarm",
        urgency=10,
        importance=10,
        estimated_hours=2.0,
        equipment_id="CNC-05"
    ),
    MaintenanceTask(
        task_id="T002",
        title="Routine lubrication for conveyor belt CB-12",
        task_type="routine",
        urgency=3,
        importance=5,
        estimated_hours=0.5,
        equipment_id="CB-12"
    ),
    MaintenanceTask(
        task_id="T003",
        title="Preventive maintenance: Replace hydraulic pump seals HP-08",
        task_type="preventive",
        urgency=7,
        importance=8,
        estimated_hours=4.0,
        equipment_id="HP-08"
    ),
    MaintenanceTask(
        task_id="T004",
        title="Upgrade PLC software on packaging line PL-03",
        task_type="upgrade",
        urgency=5,
        importance=7,
        estimated_hours=6.0,
        equipment_id="PL-03",
        dependencies=[]
    ),
    MaintenanceTask(
        task_id="T005",
        title="Calibration check for pressure sensors on HP-08",
        task_type="routine",
        urgency=4,
        importance=6,
        estimated_hours=1.0,
        equipment_id="HP-08",
        dependencies=["T003"]  # Must be done after hydraulic maintenance
    ),
    MaintenanceTask(
        task_id="T006",
        title="WARNING: Unusual vibration detected on motor M-22",
        task_type="failure_alarm",
        urgency=8,
        importance=9,
        estimated_hours=3.0,
        equipment_id="M-22"
    ),
    MaintenanceTask(
        task_id="T007",
        title="Monthly inspection of safety guards",
        task_type="routine",
        urgency=4,
        importance=8,
        estimated_hours=2.0,
        equipment_id="ALL"
    ),
]

for task in sample_tasks:
    task_queue.add_task(task)


# --- Tools ---
def list_pending_tasks() -> str:
    """
    List all pending maintenance tasks with their attributes.

    Returns:
        JSON string with all tasks
    """
    tasks = task_queue.get_all_tasks()
    return json.dumps({
        "total_tasks": len(tasks),
        "tasks": [t.to_dict() for t in tasks]
    }, indent=2)


def analyze_task_urgency(task_id: str) -> str:
    """
    Analyze the urgency factors of a specific task.

    Args:
        task_id: ID of the task to analyze

    Returns:
        JSON string with urgency analysis
    """
    task = task_queue.get_task(task_id)
    if not task:
        return json.dumps({"error": f"Task {task_id} not found"})

    urgency_factors = []

    if task.task_type == "failure_alarm":
        urgency_factors.append("Active failure alarm - immediate attention required")
    elif task.task_type == "preventive":
        urgency_factors.append("Preventive task - prevents future failures")
    elif task.task_type == "routine":
        urgency_factors.append("Routine maintenance - scheduled task")

    if task.urgency >= 8:
        urgency_factors.append("High urgency level - prioritize immediately")
    elif task.urgency >= 5:
        urgency_factors.append("Moderate urgency - schedule soon")

    if task.importance >= 8:
        urgency_factors.append("High importance - critical equipment")

    if task.estimated_hours <= 1:
        urgency_factors.append("Quick task - can be completed efficiently")

    return json.dumps({
        "task_id": task_id,
        "title": task.title,
        "urgency_level": task.urgency,
        "importance_level": task.importance,
        "factors": urgency_factors,
        "recommendation": "immediate" if task.urgency >= 8 else "schedule_soon" if task.urgency >= 5 else "normal"
    }, indent=2)


def calculate_priorities() -> str:
    """
    Calculate priority scores for all tasks based on urgency, importance, and time.

    Returns:
        JSON string with updated priorities
    """
    task_queue.update_priority_scores()

    sorted_tasks = sorted(
        task_queue.get_all_tasks(),
        key=lambda t: t.priority_score,
        reverse=True
    )

    return json.dumps({
        "message": "Priority scores calculated",
        "prioritized_tasks": [
            {
                "task_id": t.task_id,
                "title": t.title,
                "priority_score": round(t.priority_score, 2),
                "urgency": t.urgency,
                "importance": t.importance
            }
            for t in sorted_tasks
        ]
    }, indent=2)


def check_dependencies(task_id: str) -> str:
    """
    Check if a task has dependencies and if they are satisfied.

    Args:
        task_id: ID of the task to check

    Returns:
        JSON string with dependency status
    """
    task = task_queue.get_task(task_id)
    if not task:
        return json.dumps({"error": f"Task {task_id} not found"})

    dependencies_info = []
    all_satisfied = True

    for dep_id in task.dependencies:
        dep_task = task_queue.get_task(dep_id)
        if dep_task:
            satisfied = dep_task.status == "completed" or dep_task.execution_order is not None
            dependencies_info.append({
                "dependency_id": dep_id,
                "title": dep_task.title,
                "satisfied": satisfied
            })
            if not satisfied:
                all_satisfied = False

    return json.dumps({
        "task_id": task_id,
        "has_dependencies": len(task.dependencies) > 0,
        "dependencies": dependencies_info,
        "all_satisfied": all_satisfied,
        "can_schedule": all_satisfied
    }, indent=2)


def create_execution_plan() -> str:
    """
    Create optimized execution plan considering priorities and dependencies.

    Returns:
        JSON string with execution plan
    """
    execution_order = task_queue.create_execution_plan()

    plan = []
    for order, task_id in enumerate(execution_order, 1):
        task = task_queue.get_task(task_id)
        if task:
            plan.append({
                "order": order,
                "task_id": task_id,
                "title": task.title,
                "type": task.task_type,
                "priority_score": round(task.priority_score, 2),
                "estimated_hours": task.estimated_hours,
                "equipment": task.equipment_id
            })

    return json.dumps({
        "message": "Execution plan created",
        "total_tasks": len(plan),
        "total_estimated_hours": sum(p["estimated_hours"] for p in plan),
        "execution_plan": plan
    }, indent=2)


# Create FunctionTools
list_tool = FunctionTool(func=list_pending_tasks)
urgency_tool = FunctionTool(func=analyze_task_urgency)
priority_tool = FunctionTool(func=calculate_priorities)
dependency_tool = FunctionTool(func=check_dependencies)
plan_tool = FunctionTool(func=create_execution_plan)


# --- Agents ---
task_analyzer = LlmAgent(
    model=MODEL,
    name="TaskAnalyzer",
    instruction="""You are a Task Analyzer agent. Your role is to:
    1. List all pending tasks using the list_pending_tasks tool
    2. Identify critical tasks (failure alarms with high urgency)
    3. Store task count and critical task IDs in session state
    4. Provide a summary of the task landscape""",
    tools=[list_tool, urgency_tool],
)

priority_calculator = LlmAgent(
    model=MODEL,
    name="PriorityCalculator",
    instruction="""You are a Priority Calculator agent. Your role is to:
    1. Calculate priority scores for all tasks
    2. Check dependencies for high-priority tasks
    3. Store the prioritized list in session state
    4. Highlight any dependency conflicts""",
    tools=[priority_tool, dependency_tool],
)

execution_planner = LlmAgent(
    model=MODEL,
    name="ExecutionPlanner",
    instruction="""You are an Execution Planner agent. Your role is to:
    1. Create an optimized execution plan respecting dependencies
    2. Store the execution plan in session state
    3. Provide recommendations for immediate actions
    4. Calculate total estimated time for all tasks""",
    tools=[plan_tool],
)

# Sequential workflow
prioritization_workflow = SequentialAgent(
    name="PrioritizationWorkflow",
    sub_agents=[task_analyzer, priority_calculator, execution_planner],
)


# --- Main Execution ---
async def run_prioritization_demo():
    """Demonstrate prioritization pattern"""
    print("=" * 80)
    print("Prioritization Pattern - Intelligent Task Scheduling")
    print("=" * 80)

    # Initialize services
    session_service = InMemorySessionService()

    # Create runner
    runner = Runner(
        agent=prioritization_workflow,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # Create session
    session_id = "priority_session_001"
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id
    )

    # User message
    user_message = Content(
        parts=[Part(text="""Analyze all pending maintenance tasks and create an optimized
        execution plan. Prioritize critical failure alarms while respecting task dependencies
        and considering both urgency and importance.""")],
        role="user"
    )

    print("\n🎯 Objective: Create optimized maintenance task execution plan")
    print(f"📊 Total Tasks: {len(task_queue.get_all_tasks())}")
    print("\n" + "=" * 80)
    print("Analyzing and Prioritizing Tasks...")
    print("=" * 80 + "\n")

    # Run the prioritization workflow
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=user_message
    ):
        if event.content and event.content.parts:
            text = event.content.parts[0].text
            if text:
                print(f"\n[{event.author}]")
                print(f"{text}")
                print("-" * 80)

    # Final results
    print("\n" + "=" * 80)
    print("Prioritization Complete!")
    print("=" * 80)

    print("\n📋 Final Execution Plan:")
    for order, task_id in enumerate(task_queue.execution_plan, 1):
        task = task_queue.get_task(task_id)
        if task:
            urgency_emoji = "🔴" if task.urgency >= 8 else "🟡" if task.urgency >= 5 else "🟢"
            print(f"\n   {order}. {urgency_emoji} [{task.task_type.upper()}]")
            print(f"      Task: {task.title}")
            print(f"      Priority Score: {task.priority_score:.2f}")
            print(f"      Urgency: {task.urgency}/10, Importance: {task.importance}/10")
            print(f"      Estimated: {task.estimated_hours}h")
            if task.dependencies:
                print(f"      Dependencies: {', '.join(task.dependencies)}")

    total_hours = sum(task_queue.get_task(tid).estimated_hours
                     for tid in task_queue.execution_plan)
    print(f"\n⏱️  Total Estimated Time: {total_hours} hours")

    critical_count = sum(1 for tid in task_queue.execution_plan[:3]
                        if task_queue.get_task(tid).urgency >= 8)
    print(f"🔴 Critical tasks in top 3: {critical_count}")

    print("\n✅ Prioritization Pattern demonstrated successfully!")
    print("   Tasks intelligently prioritized based on urgency, importance, and dependencies.")


if __name__ == "__main__":
    asyncio.run(run_prioritization_demo())
