"""
Goal Setting and Monitoring Pattern - CrewAI Implementation

This pattern demonstrates how agents set SMART goals, track progress toward
those goals, and dynamically adjust strategies to achieve objectives.

Business Use Case: Project Monitoring (Software Development)
An agent monitors a software project's progress against SMART goals
(e.g., "Complete 80% of sprint tasks by Friday"), tracking metrics like
task completion rate, velocity, and blockers, then adjusting strategy
when goals are at risk.

Pattern: Goal Setting and Monitoring
Section: IV - Intelligence and Learning Patterns
Framework: CrewAI
"""

import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# --- Constants ---
MONITORING_INTERVAL_HOURS = 4
GOAL_ACHIEVEMENT_THRESHOLD = 0.95
MAX_MONITORING_CYCLES = 5


# --- Project Environment ---
class ProjectEnvironment:
    """Simulates a software project with tasks, metrics, and goals"""

    def __init__(self):
        self.sprint_start = datetime.now()
        self.sprint_end = self.sprint_start + timedelta(days=14)
        self.current_time = self.sprint_start

        self.tasks = [
            {"id": 1, "title": "User Authentication API", "story_points": 8, "status": "in_progress", "completed": 0.6},
            {"id": 2, "title": "Payment Integration", "story_points": 13, "status": "in_progress", "completed": 0.3},
            {"id": 3, "title": "Dashboard UI", "story_points": 5, "status": "completed", "completed": 1.0},
            {"id": 4, "title": "Email Notifications", "story_points": 5, "status": "not_started", "completed": 0.0},
            {"id": 5, "title": "User Profile Page", "story_points": 8, "status": "in_progress", "completed": 0.4},
            {"id": 6, "title": "Search Functionality", "story_points": 8, "status": "not_started", "completed": 0.0},
            {"id": 7, "title": "Bug Fixes", "story_points": 5, "status": "in_progress", "completed": 0.7},
            {"id": 8, "title": "Unit Tests", "story_points": 8, "status": "blocked", "completed": 0.1},
        ]

        self.total_story_points = sum(t["story_points"] for t in self.tasks)
        self.goals = {}
        self.progress_history = []
        self.strategy_adjustments = []

    def set_smart_goal(self, goal_id: str, description: str, target_metric: str, target_value: float, deadline: str, measurement_unit: str) -> Dict[str, Any]:
        goal = {
            "id": goal_id,
            "description": description,
            "target_metric": target_metric,
            "target_value": target_value,
            "current_value": 0.0,
            "deadline": deadline,
            "measurement_unit": measurement_unit,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        self.goals[goal_id] = goal
        return goal

    def track_progress(self, goal_id: str) -> Dict[str, Any]:
        if goal_id not in self.goals:
            return {"error": f"Goal {goal_id} not found"}

        goal = self.goals[goal_id]
        target_metric = goal["target_metric"]

        # Calculate current metric value
        if target_metric == "completion_rate":
            completed_points = sum(t["story_points"] * t["completed"] for t in self.tasks)
            current_value = (completed_points / self.total_story_points) * 100

        elif target_metric == "velocity":
            days_elapsed = max(1, (self.current_time - self.sprint_start).days)
            completed_points = sum(t["story_points"] * t["completed"] for t in self.tasks)
            current_value = completed_points / days_elapsed

        elif target_metric == "task_completion_count":
            current_value = len([t for t in self.tasks if t["completed"] >= 1.0])

        elif target_metric == "blocked_tasks":
            current_value = len([t for t in self.tasks if t["status"] == "blocked"])

        else:
            current_value = 0.0

        goal["current_value"] = round(current_value, 2)

        # Calculate progress percentage
        if target_metric == "blocked_tasks":
            progress_pct = max(0, (goal["target_value"] - current_value) / goal["target_value"] * 100)
        else:
            progress_pct = (current_value / goal["target_value"]) * 100

        # Determine status
        if progress_pct >= GOAL_ACHIEVEMENT_THRESHOLD * 100:
            goal["status"] = "achieved"
        elif progress_pct < 50:
            goal["status"] = "at_risk"
        else:
            goal["status"] = "on_track"

        time_remaining = datetime.fromisoformat(goal["deadline"]) - self.current_time
        days_remaining = time_remaining.days

        progress_data = {
            "goal_id": goal_id,
            "description": goal["description"],
            "target_metric": target_metric,
            "target_value": goal["target_value"],
            "current_value": current_value,
            "progress_percentage": round(progress_pct, 2),
            "status": goal["status"],
            "days_remaining": days_remaining,
            "measurement_unit": goal["measurement_unit"]
        }

        self.progress_history.append({
            "timestamp": self.current_time.isoformat(),
            "goal_id": goal_id,
            "progress": progress_data
        })

        return progress_data

    def evaluate_all_goals(self) -> Dict[str, Any]:
        evaluations = {}
        for goal_id in self.goals:
            evaluations[goal_id] = self.track_progress(goal_id)

        return {
            "total_goals": len(self.goals),
            "achieved": len([g for g in evaluations.values() if g.get("status") == "achieved"]),
            "on_track": len([g for g in evaluations.values() if g.get("status") == "on_track"]),
            "at_risk": len([g for g in evaluations.values() if g.get("status") == "at_risk"]),
            "goals": evaluations
        }

    def adjust_strategy(self, goal_id: str, adjustment_description: str, actions: List[str]) -> Dict[str, Any]:
        adjustment = {
            "timestamp": self.current_time.isoformat(),
            "goal_id": goal_id,
            "description": adjustment_description,
            "actions": actions,
            "status": "planned"
        }

        self.strategy_adjustments.append(adjustment)

        # Simulate impact of strategy adjustment
        for task in self.tasks:
            if task["status"] == "blocked" and "unblock" in adjustment_description.lower():
                task["status"] = "in_progress"
            elif task["status"] == "in_progress":
                task["completed"] = min(1.0, task["completed"] + 0.15)

        return {
            "adjustment_id": len(self.strategy_adjustments),
            "goal_id": goal_id,
            "description": adjustment_description,
            "actions": actions,
            "applied": True
        }

    def advance_time(self, hours: int):
        self.current_time += timedelta(hours=hours)
        for task in self.tasks:
            if task["status"] == "in_progress":
                task["completed"] = min(1.0, task["completed"] + 0.05)
                if task["completed"] >= 1.0:
                    task["status"] = "completed"

    def get_project_snapshot(self) -> Dict[str, Any]:
        return {
            "current_time": self.current_time.isoformat(),
            "sprint_start": self.sprint_start.isoformat(),
            "sprint_end": self.sprint_end.isoformat(),
            "total_tasks": len(self.tasks),
            "completed_tasks": len([t for t in self.tasks if t["completed"] >= 1.0]),
            "in_progress_tasks": len([t for t in self.tasks if t["status"] == "in_progress"]),
            "blocked_tasks": len([t for t in self.tasks if t["status"] == "blocked"]),
            "total_story_points": self.total_story_points,
            "completed_story_points": sum(t["story_points"] * t["completed"] for t in self.tasks),
            "overall_completion": round(sum(t["story_points"] * t["completed"] for t in self.tasks) / self.total_story_points * 100, 2)
        }


# Initialize project environment
project_env = ProjectEnvironment()


# --- Custom Tools ---
class SetGoalInput(BaseModel):
    goal_id: str = Field(..., description="Unique goal identifier")
    description: str = Field(..., description="Clear description of the goal")
    target_metric: str = Field(..., description="Metric to measure")
    target_value: float = Field(..., description="Target value")
    deadline: str = Field(..., description="ISO format deadline")
    measurement_unit: str = Field(..., description="Unit of measurement")


class SetGoalsTool(BaseTool):
    name: str = "set_goals"
    description: str = "Set a SMART goal for the project"

    def _run(self, goal_id: str, description: str, target_metric: str, target_value: float, deadline: str, measurement_unit: str) -> str:
        result = project_env.set_smart_goal(goal_id, description, target_metric, target_value, deadline, measurement_unit)
        return json.dumps(result, indent=2)


class TrackProgressInput(BaseModel):
    goal_id: str = Field(..., description="ID of the goal to track")


class TrackProgressTool(BaseTool):
    name: str = "track_progress"
    description: str = "Track current progress toward a specific goal"

    def _run(self, goal_id: str) -> str:
        result = project_env.track_progress(goal_id)
        return json.dumps(result, indent=2)


class EvaluateGoalsTool(BaseTool):
    name: str = "evaluate_goal_status"
    description: str = "Evaluate the status of all active goals"

    def _run(self) -> str:
        result = project_env.evaluate_all_goals()
        return json.dumps(result, indent=2)


class AdjustStrategyInput(BaseModel):
    goal_id: str = Field(..., description="Goal that needs adjustment")
    adjustment_description: str = Field(..., description="Description of adjustment")
    actions: List[str] = Field(..., description="Specific actions to take")


class AdjustStrategyTool(BaseTool):
    name: str = "adjust_strategy"
    description: str = "Adjust project strategy to improve goal achievement"

    def _run(self, goal_id: str, adjustment_description: str, actions: List[str]) -> str:
        result = project_env.adjust_strategy(goal_id, adjustment_description, actions)
        return json.dumps(result, indent=2)


class GetProjectStatusTool(BaseTool):
    name: str = "get_project_status"
    description: str = "Get current project snapshot with task and progress information"

    def _run(self) -> str:
        result = project_env.get_project_snapshot()
        return json.dumps(result, indent=2)


# Initialize tools
set_goals_tool = SetGoalsTool()
track_progress_tool = TrackProgressTool()
evaluate_tool = EvaluateGoalsTool()
adjust_strategy_tool = AdjustStrategyTool()
project_status_tool = GetProjectStatusTool()


# --- Agents ---
def create_goal_setter() -> Agent:
    return Agent(
        role="Goal Setter",
        goal="Set SMART goals for project success",
        backstory="""You are a Project Management specialist who sets clear,
        measurable, achievable, relevant, and time-bound goals. You ensure
        goals align with project objectives and are trackable.""",
        tools=[project_status_tool, set_goals_tool],
        verbose=True,
        allow_delegation=False
    )


def create_progress_tracker() -> Agent:
    return Agent(
        role="Progress Tracker",
        goal="Track progress toward all goals and identify at-risk ones",
        backstory="""You are a Progress Monitoring specialist who continuously
        tracks project metrics against goals. You identify risks early and
        provide clear status updates.""",
        tools=[track_progress_tool, evaluate_tool, project_status_tool],
        verbose=True,
        allow_delegation=False
    )


def create_strategy_adjuster() -> Agent:
    return Agent(
        role="Strategy Adjuster",
        goal="Adjust strategies when goals are at risk",
        backstory="""You are an Adaptive Strategy specialist who adjusts
        project approaches when goals are at risk. You propose concrete
        actions to get back on track.""",
        tools=[adjust_strategy_tool, project_status_tool],
        verbose=True,
        allow_delegation=False
    )


# --- Main Execution ---
def run_goal_monitoring_demo():
    """Demonstrate goal setting and monitoring pattern"""
    print("=" * 80)
    print("Goal Setting and Monitoring Pattern - Project Management")
    print("=" * 80)

    print(f"\nInitial Project State:")
    print(json.dumps(project_env.get_project_snapshot(), indent=2))

    print(f"\n{'=' * 80}")
    print("Starting Goal-Based Monitoring")
    print(f"{'=' * 80}\n")

    # Create agents
    goal_setter = create_goal_setter()
    progress_tracker = create_progress_tracker()
    strategy_adjuster = create_strategy_adjuster()

    # Run monitoring cycles
    for cycle in range(MAX_MONITORING_CYCLES):
        print(f"\n{'=' * 80}")
        print(f"Monitoring Cycle {cycle + 1}/{MAX_MONITORING_CYCLES}")
        print(f"{'=' * 80}")

        # Create tasks for this cycle
        if cycle == 0:
            # First cycle: Set goals
            goal_task = Task(
                description=f"""Set SMART goals for the 2-week sprint:
                1. Overall completion: 80% of {project_env.total_story_points} story points
                2. Blocked tasks: Reduce to 0
                3. Daily velocity: At least 4 story points per day
                
                Deadline: {project_env.sprint_end.isoformat()}""",
                agent=goal_setter,
                expected_output="SMART goals created for sprint"
            )

            crew = Crew(
                agents=[goal_setter],
                tasks=[goal_task],
                process=Process.sequential,
                verbose=True
            )
        else:
            # Subsequent cycles: Track and adjust
            track_task = Task(
                description="""Track progress for all goals:
                1. Evaluate all goals using evaluate_goal_status
                2. Identify any at-risk goals
                3. Report progress percentages and status""",
                agent=progress_tracker,
                expected_output="Progress report with goal statuses"
            )

            adjust_task = Task(
                description="""If any goals are at-risk:
                1. Propose strategy adjustments
                2. Specify concrete actions to improve progress
                3. Use adjust_strategy to implement changes""",
                agent=strategy_adjuster,
                expected_output="Strategy adjustments or confirmation of on-track status",
                context=[track_task]
            )

            crew = Crew(
                agents=[progress_tracker, strategy_adjuster],
                tasks=[track_task, adjust_task],
                process=Process.sequential,
                verbose=True
            )

        # Execute cycle
        try:
            result = crew.kickoff()
            print(f"\n[Cycle {cycle + 1} Result]")
            print(result)
        except Exception as e:
            print(f"\n[Error in cycle {cycle + 1}]: {e}")

        # Advance time
        if cycle < MAX_MONITORING_CYCLES - 1:
            project_env.advance_time(MONITORING_INTERVAL_HOURS)
            print(f"\nTime advanced by {MONITORING_INTERVAL_HOURS} hours...")

        # Check if all goals achieved
        evaluation = project_env.evaluate_all_goals()
        if evaluation["achieved"] == evaluation["total_goals"]:
            print("\nAll goals achieved! Stopping monitoring.")
            break

    # Final results
    print(f"\n{'=' * 80}")
    print("Monitoring Complete - Final Results")
    print(f"{'=' * 80}")

    final_evaluation = project_env.evaluate_all_goals()
    print(f"\nFinal Goal Status:")
    print(json.dumps(final_evaluation, indent=2))

    print(f"\nFinal Project State:")
    print(json.dumps(project_env.get_project_snapshot(), indent=2))

    print(f"\nStrategy Adjustments Made: {len(project_env.strategy_adjustments)}")

    print("\nGoal Setting and Monitoring Pattern demonstrated successfully!")


if __name__ == "__main__":
    run_goal_monitoring_demo()
