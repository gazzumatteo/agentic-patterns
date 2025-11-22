"""
Prioritization Pattern - CrewAI Implementation

This pattern demonstrates how agents evaluate tasks based on urgency, importance,
and dependencies to determine optimal execution order.

Business Use Case: Proactive Maintenance (Manufacturing)
The agent assigns maximum urgency to an imminent failure alarm versus routine inspection.

Pattern: Prioritization
Section: III - Governance, Reliability, and Support Patterns
Framework: CrewAI
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# --- Task Management System ---
class MaintenanceTask:
    """Represents a maintenance task with priority attributes"""

    def __init__(self, task_id: str, title: str, task_type: str,
                 urgency: int, importance: int, estimated_hours: float,
                 equipment_id: str, dependencies: List[str] = None):
        self.task_id = task_id
        self.title = title
        self.task_type = task_type
        self.urgency = urgency
        self.importance = importance
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
        self.tasks[task.task_id] = task

    def get_all_tasks(self) -> List[MaintenanceTask]:
        return list(self.tasks.values())

    def get_task(self, task_id: str) -> Optional[MaintenanceTask]:
        return self.tasks.get(task_id)

    def update_priority_scores(self):
        """Calculate priority scores for all tasks"""
        for task in self.tasks.values():
            urgency_weight = 0.5
            importance_weight = 0.3
            time_weight = 0.2

            time_factor = max(1, 10 - (task.estimated_hours / 2))

            task.priority_score = (
                task.urgency * urgency_weight +
                task.importance * importance_weight +
                time_factor * time_weight
            )

    def create_execution_plan(self) -> List[str]:
        """Create execution plan considering priorities and dependencies"""
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda t: t.priority_score,
            reverse=True
        )

        execution_order = []
        scheduled = set()

        def can_schedule(task: MaintenanceTask) -> bool:
            return all(dep in scheduled for dep in task.dependencies)

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


# Initialize task queue with sample tasks
task_queue = TaskQueue()

sample_tasks = [
    MaintenanceTask("T001", "CRITICAL: Bearing temperature alarm on CNC-05",
                    "failure_alarm", 10, 10, 2.0, "CNC-05"),
    MaintenanceTask("T002", "Routine lubrication for conveyor belt CB-12",
                    "routine", 3, 5, 0.5, "CB-12"),
    MaintenanceTask("T003", "Preventive maintenance: Replace hydraulic pump seals HP-08",
                    "preventive", 7, 8, 4.0, "HP-08"),
    MaintenanceTask("T004", "Upgrade PLC software on packaging line PL-03",
                    "upgrade", 5, 7, 6.0, "PL-03", []),
    MaintenanceTask("T005", "Calibration check for pressure sensors on HP-08",
                    "routine", 4, 6, 1.0, "HP-08", ["T003"]),
    MaintenanceTask("T006", "WARNING: Unusual vibration detected on motor M-22",
                    "failure_alarm", 8, 9, 3.0, "M-22"),
    MaintenanceTask("T007", "Monthly inspection of safety guards",
                    "routine", 4, 8, 2.0, "ALL"),
]

for task in sample_tasks:
    task_queue.add_task(task)


# --- Custom Tools ---
class ListTasksTool(BaseTool):
    name: str = "list_pending_tasks"
    description: str = "List all pending maintenance tasks with their attributes"

    def _run(self) -> str:
        tasks = task_queue.get_all_tasks()
        return json.dumps({
            "total_tasks": len(tasks),
            "tasks": [t.to_dict() for t in tasks]
        }, indent=2)


class CalculatePrioritiesTool(BaseTool):
    name: str = "calculate_priorities"
    description: str = "Calculate priority scores for all tasks based on urgency, importance, and time"

    def _run(self) -> str:
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


class CreateExecutionPlanTool(BaseTool):
    name: str = "create_execution_plan"
    description: str = "Create optimized execution plan considering priorities and dependencies"

    def _run(self) -> str:
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


# Initialize tools
list_tool = ListTasksTool()
priority_tool = CalculatePrioritiesTool()
plan_tool = CreateExecutionPlanTool()


# --- Agents ---
def create_task_analyzer() -> Agent:
    return Agent(
        role="Task Analyzer",
        goal="Analyze all pending maintenance tasks and identify critical ones",
        backstory="""You are a Maintenance Task Analysis expert who reviews
        all pending work orders and identifies critical failure alarms that
        need immediate attention.""",
        tools=[list_tool],
        verbose=True,
        allow_delegation=False
    )


def create_priority_calculator() -> Agent:
    return Agent(
        role="Priority Calculator",
        goal="Calculate priority scores and check dependencies",
        backstory="""You are a Priority Analysis specialist who evaluates
        tasks based on urgency, importance, and estimated time. You ensure
        dependencies are considered when scheduling.""",
        tools=[priority_tool],
        verbose=True,
        allow_delegation=False
    )


def create_execution_planner() -> Agent:
    return Agent(
        role="Execution Planner",
        goal="Create optimized execution plan respecting priorities and dependencies",
        backstory="""You are a Production Scheduling expert who creates
        efficient work plans that maximize equipment uptime and minimize
        downtime risks.""",
        tools=[plan_tool],
        verbose=True,
        allow_delegation=False
    )


# --- Main Execution ---
def run_prioritization_demo():
    """Demonstrate prioritization pattern"""
    print("=" * 80)
    print("Prioritization Pattern - Intelligent Task Scheduling")
    print("=" * 80)

    print(f"\nObjective: Create optimized maintenance task execution plan")
    print(f"Total Tasks: {len(task_queue.get_all_tasks())}")
    print(f"\n{'=' * 80}")
    print("Analyzing and Prioritizing Tasks...")
    print(f"{'=' * 80}\n")

    # Create agents
    analyzer = create_task_analyzer()
    calculator = create_priority_calculator()
    planner = create_execution_planner()

    # Create tasks
    analyze_task = Task(
        description="""Analyze all pending maintenance tasks:
        1. List all tasks using list_pending_tasks
        2. Identify critical failure alarms (urgency >= 8)
        3. Summarize the task landscape""",
        agent=analyzer,
        expected_output="Summary of all tasks with identification of critical ones"
    )

    calculate_task = Task(
        description="""Calculate priorities for all tasks:
        1. Use calculate_priorities to score all tasks
        2. Review high-priority tasks and their dependencies
        3. Report the prioritized list""",
        agent=calculator,
        expected_output="Prioritized task list with scores",
        context=[analyze_task]
    )

    plan_task = Task(
        description="""Create execution plan:
        1. Use create_execution_plan to build optimized schedule
        2. Ensure dependencies are respected
        3. Provide recommendations for immediate actions
        4. Calculate total estimated time""",
        agent=planner,
        expected_output="Optimized execution plan with time estimates",
        context=[calculate_task]
    )

    # Create crew
    crew = Crew(
        agents=[analyzer, calculator, planner],
        tasks=[analyze_task, calculate_task, plan_task],
        process=Process.sequential,
        verbose=True
    )

    # Execute
    try:
        result = crew.kickoff()
        print(f"\n{'=' * 80}")
        print("Prioritization Complete!")
        print(f"{'=' * 80}")
        print(f"\n{result}")
    except Exception as e:
        print(f"\n[Error]: {e}")
        return

    # Display final execution plan
    print(f"\n{'=' * 80}")
    print("Final Execution Plan:")
    print(f"{'=' * 80}")

    for order, task_id in enumerate(task_queue.execution_plan, 1):
        task = task_queue.get_task(task_id)
        if task:
            urgency_emoji = "🔴" if task.urgency >= 8 else "🟡" if task.urgency >= 5 else "🟢"
            print(f"\n{order}. {urgency_emoji} [{task.task_type.upper()}]")
            print(f"   Task: {task.title}")
            print(f"   Priority Score: {task.priority_score:.2f}")
            print(f"   Urgency: {task.urgency}/10, Importance: {task.importance}/10")
            print(f"   Estimated: {task.estimated_hours}h")
            if task.dependencies:
                print(f"   Dependencies: {', '.join(task.dependencies)}")

    total_hours = sum(task_queue.get_task(tid).estimated_hours
                     for tid in task_queue.execution_plan)
    print(f"\nTotal Estimated Time: {total_hours} hours")

    critical_count = sum(1 for tid in task_queue.execution_plan[:3]
                        if task_queue.get_task(tid).urgency >= 8)
    print(f"Critical tasks in top 3: {critical_count}")

    print("\nPrioritization Pattern demonstrated successfully!")


if __name__ == "__main__":
    run_prioritization_demo()
