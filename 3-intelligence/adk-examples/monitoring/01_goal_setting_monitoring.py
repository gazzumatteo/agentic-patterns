"""
Goal Setting and Monitoring Pattern - Google ADK Implementation

This pattern demonstrates how agents set SMART goals, track progress toward
those goals, and dynamically adjust strategies to achieve objectives.

Business Use Case: Project Monitoring (Software Development)
An agent monitors a software project's progress against SMART goals
(e.g., "Complete 80% of sprint tasks by Friday"), tracking metrics like
task completion rate, velocity, and blockers, then adjusting strategy
when goals are at risk.

Pattern: Goal Setting and Monitoring
Section: IV - Intelligence and Learning Patterns
Framework: Google ADK
Mermaid Diagram Reference: See diagrams/article-3/goal_setting_monitoring.mermaid
"""

import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.adk.tools import FunctionTool
from google.genai.types import Content, Part


# --- Constants ---
APP_NAME = "goal_monitoring_app"
USER_ID = "project_manager"
MODEL = "gemini-2.5-flash-exp"

# Goal monitoring configuration
MONITORING_INTERVAL_HOURS = 4
GOAL_ACHIEVEMENT_THRESHOLD = 0.95  # 95% of goal = achieved


# --- Project Environment ---
class ProjectEnvironment:
    """Simulates a software project with tasks, metrics, and goals"""

    def __init__(self):
        self.sprint_start = datetime.now()
        self.sprint_end = self.sprint_start + timedelta(days=14)  # 2-week sprint
        self.current_time = self.sprint_start

        # Sprint tasks
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

        # SMART goals
        self.goals = {}
        self.progress_history = []
        self.strategy_adjustments = []

    def set_smart_goal(
        self,
        goal_id: str,
        description: str,
        target_metric: str,
        target_value: float,
        deadline: str,
        measurement_unit: str
    ) -> Dict[str, Any]:
        """
        Set a SMART goal (Specific, Measurable, Achievable, Relevant, Time-bound).

        Args:
            goal_id: Unique identifier for the goal
            description: Clear description of what should be achieved
            target_metric: The metric to measure (e.g., "completion_rate", "velocity")
            target_value: Target value for the metric
            deadline: ISO format deadline
            measurement_unit: Unit of measurement (e.g., "percentage", "story_points")

        Returns:
            Goal configuration
        """
        goal = {
            "id": goal_id,
            "description": description,
            "target_metric": target_metric,
            "target_value": target_value,
            "current_value": 0.0,
            "deadline": deadline,
            "measurement_unit": measurement_unit,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "is_smart": self._validate_smart_criteria(description)
        }

        self.goals[goal_id] = goal
        return goal

    def _validate_smart_criteria(self, description: str) -> Dict[str, bool]:
        """Validate if goal meets SMART criteria"""
        return {
            "specific": len(description) > 20,  # Has detailed description
            "measurable": True,  # Has target metric (implied by function args)
            "achievable": True,  # Assume achievable for demo
            "relevant": True,  # Assume relevant for demo
            "time_bound": True  # Has deadline (implied by function args)
        }

    def track_progress(self, goal_id: str) -> Dict[str, Any]:
        """
        Track current progress toward a goal.

        Args:
            goal_id: ID of the goal to track

        Returns:
            Progress metrics and status
        """
        if goal_id not in self.goals:
            return {"error": f"Goal {goal_id} not found"}

        goal = self.goals[goal_id]
        target_metric = goal["target_metric"]

        # Calculate current metric value
        if target_metric == "completion_rate":
            # Percentage of story points completed
            completed_points = sum(
                t["story_points"] * t["completed"]
                for t in self.tasks
            )
            current_value = (completed_points / self.total_story_points) * 100

        elif target_metric == "velocity":
            # Story points completed per day
            days_elapsed = (self.current_time - self.sprint_start).days
            if days_elapsed == 0:
                days_elapsed = 1
            completed_points = sum(
                t["story_points"] * t["completed"]
                for t in self.tasks
            )
            current_value = completed_points / days_elapsed

        elif target_metric == "task_completion_count":
            # Number of fully completed tasks
            current_value = len([t for t in self.tasks if t["completed"] >= 1.0])

        elif target_metric == "blocked_tasks":
            # Number of blocked tasks (lower is better)
            current_value = len([t for t in self.tasks if t["status"] == "blocked"])

        else:
            current_value = 0.0

        # Update goal
        goal["current_value"] = round(current_value, 2)

        # Calculate progress percentage
        if target_metric == "blocked_tasks":
            # For blocked tasks, lower is better
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

        # Time analysis
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
            "measurement_unit": goal["measurement_unit"],
            "is_smart": goal["is_smart"]
        }

        self.progress_history.append({
            "timestamp": self.current_time.isoformat(),
            "goal_id": goal_id,
            "progress": progress_data
        })

        return progress_data

    def evaluate_all_goals(self) -> Dict[str, Any]:
        """Evaluate status of all active goals"""
        evaluations = {}
        for goal_id in self.goals:
            evaluations[goal_id] = self.track_progress(goal_id)

        summary = {
            "total_goals": len(self.goals),
            "achieved": len([g for g in evaluations.values() if g["status"] == "achieved"]),
            "on_track": len([g for g in evaluations.values() if g["status"] == "on_track"]),
            "at_risk": len([g for g in evaluations.values() if g["status"] == "at_risk"]),
            "goals": evaluations
        }

        return summary

    def adjust_strategy(self, goal_id: str, adjustment_description: str, actions: List[str]) -> Dict[str, Any]:
        """
        Adjust project strategy to improve goal achievement probability.

        Args:
            goal_id: Goal that needs strategy adjustment
            adjustment_description: Description of the adjustment
            actions: List of concrete actions to take

        Returns:
            Strategy adjustment confirmation
        """
        adjustment = {
            "timestamp": self.current_time.isoformat(),
            "goal_id": goal_id,
            "description": adjustment_description,
            "actions": actions,
            "status": "planned"
        }

        self.strategy_adjustments.append(adjustment)

        # Simulate impact of strategy adjustment (improve task progress)
        for task in self.tasks:
            if task["status"] == "blocked" and "unblock" in adjustment_description.lower():
                task["status"] = "in_progress"
            elif task["status"] == "in_progress":
                # Slightly improve progress
                task["completed"] = min(1.0, task["completed"] + 0.15)

        return {
            "adjustment_id": len(self.strategy_adjustments),
            "goal_id": goal_id,
            "description": adjustment_description,
            "actions": actions,
            "applied": True
        }

    def advance_time(self, hours: int):
        """Simulate passage of time"""
        self.current_time += timedelta(hours=hours)

        # Simulate natural task progress
        for task in self.tasks:
            if task["status"] == "in_progress":
                task["completed"] = min(1.0, task["completed"] + 0.05)
                if task["completed"] >= 1.0:
                    task["status"] = "completed"

    def get_project_snapshot(self) -> Dict[str, Any]:
        """Get current project state"""
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
            "overall_completion": round(
                sum(t["story_points"] * t["completed"] for t in self.tasks) / self.total_story_points * 100, 2
            )
        }


# Initialize project environment
project_env = ProjectEnvironment()


# --- Tools ---
def set_goals(
    goal_id: str,
    description: str,
    target_metric: str,
    target_value: float,
    deadline: str,
    measurement_unit: str
) -> str:
    """
    Set a SMART goal for the project.

    Args:
        goal_id: Unique goal identifier (e.g., "sprint_completion_goal")
        description: Clear, specific description of the goal
        target_metric: Metric to measure (completion_rate, velocity, task_completion_count, blocked_tasks)
        target_value: Target value for the metric
        deadline: ISO format deadline (e.g., "2024-12-31T23:59:59")
        measurement_unit: Unit (percentage, story_points_per_day, count, etc.)

    Returns:
        JSON string with goal configuration
    """
    result = project_env.set_smart_goal(
        goal_id, description, target_metric, target_value, deadline, measurement_unit
    )
    return json.dumps(result, indent=2)


def track_progress(goal_id: str) -> str:
    """
    Track current progress toward a specific goal.

    Args:
        goal_id: ID of the goal to track

    Returns:
        JSON string with current progress metrics and status
    """
    result = project_env.track_progress(goal_id)
    return json.dumps(result, indent=2)


def evaluate_goal_status() -> str:
    """
    Evaluate the status of all active goals.

    Returns:
        JSON string with comprehensive goal evaluation including achieved, on-track, and at-risk goals
    """
    result = project_env.evaluate_all_goals()
    return json.dumps(result, indent=2)


def adjust_strategy(goal_id: str, adjustment_description: str, actions: List[str]) -> str:
    """
    Adjust project strategy to improve goal achievement.

    Args:
        goal_id: Goal that needs adjustment
        adjustment_description: Description of why adjustment is needed
        actions: List of specific actions to take (e.g., ["Assign more developers to Payment Integration", "Unblock testing infrastructure"])

    Returns:
        JSON string with strategy adjustment confirmation
    """
    result = project_env.adjust_strategy(goal_id, adjustment_description, actions)
    return json.dumps(result, indent=2)


def get_project_status() -> str:
    """
    Get current project snapshot with task and progress information.

    Returns:
        JSON string with current project state
    """
    result = project_env.get_project_snapshot()
    return json.dumps(result, indent=2)


# Create FunctionTools
set_goals_tool = FunctionTool(func=set_goals)
track_progress_tool = FunctionTool(func=track_progress)
evaluate_tool = FunctionTool(func=evaluate_goal_status)
adjust_strategy_tool = FunctionTool(func=adjust_strategy)
project_status_tool = FunctionTool(func=get_project_status)


# --- Agents ---
# Agent 1: Goal Setter
goal_setter_agent = LlmAgent(
    model=MODEL,
    name="GoalSetter",
    instruction="""You are a Goal Setting agent for project management.

Your role:
1. Get current project status using get_project_status
2. Set SMART goals using set_goals function
3. Ensure goals are:
   - Specific: Clear and well-defined
   - Measurable: Have quantifiable metrics
   - Achievable: Realistic given project constraints
   - Relevant: Aligned with project objectives
   - Time-bound: Have clear deadlines

Example goals:
- "Complete 80% of sprint story points by end of sprint"
- "Reduce blocked tasks to 0 within 3 days"
- "Maintain velocity above 5 story points per day"

Store created goal IDs in session state under 'active_goal_ids'.""",
    tools=[project_status_tool, set_goals_tool],
)

# Agent 2: Progress Tracker
progress_tracker_agent = LlmAgent(
    model=MODEL,
    name="ProgressTracker",
    instruction="""You are a Progress Tracking agent.

Your role:
1. Get active_goal_ids from session state
2. Track progress for each goal using track_progress
3. Evaluate all goals using evaluate_goal_status
4. Store evaluation results in state as 'goal_evaluation'
5. Identify goals that are 'at_risk'
6. Set 'needs_strategy_adjustment' to true if any goals are at risk

Provide clear progress reports with percentages and time remaining.""",
    tools=[track_progress_tool, evaluate_tool, project_status_tool],
)

# Agent 3: Strategy Adjuster
strategy_adjuster_agent = LlmAgent(
    model=MODEL,
    name="StrategyAdjuster",
    instruction="""You are a Strategy Adjustment agent.

Your role:
1. Check if 'needs_strategy_adjustment' is true in session state
2. If true, review the goal_evaluation to identify at-risk goals
3. For each at-risk goal:
   - Analyze what's blocking progress
   - Propose concrete actions (unblock tasks, reallocate resources, adjust scope)
   - Call adjust_strategy with specific actions
4. After adjustments, set 'continue_monitoring' based on:
   - true: If goals not yet achieved and time remains
   - false: If all goals achieved or deadline passed

Be specific with action plans and consider project constraints.""",
    tools=[adjust_strategy_tool, project_status_tool],
)


# --- Loop Workflow ---
def should_continue_monitoring(session: Session) -> bool:
    """
    Exit condition: Stop when all goals achieved or max iterations reached.
    """
    continue_flag = session.state.get("continue_monitoring", True)
    iteration = session.state.get("iteration", 0)

    # Stop after 5 monitoring cycles for demo
    return continue_flag and iteration < 5


monitoring_loop = LoopAgent(
    name="GoalMonitoringLoop",
    sub_agents=[goal_setter_agent, progress_tracker_agent, strategy_adjuster_agent],
    exit_condition=should_continue_monitoring,
)


# --- Main Execution ---
async def run_goal_monitoring_demo():
    """Demonstrate goal setting and monitoring pattern"""
    print("=" * 80)
    print("Goal Setting and Monitoring Pattern - Project Management")
    print("=" * 80)

    # Initialize services
    session_service = InMemorySessionService()

    # Create runner
    runner = Runner(
        agent=monitoring_loop,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # Create session
    session_id = "sprint_monitoring_001"
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id
    )

    # Initialize session state
    session = await session_service.get_session(APP_NAME, USER_ID, session_id)
    session.state.update({
        "iteration": 0,
        "continue_monitoring": True,
        "active_goal_ids": []
    })
    await session_service.save_session(session)

    # Display initial project state
    print("\n📊 Initial Project State:")
    print(json.dumps(project_env.get_project_snapshot(), indent=2))

    # User message to start monitoring
    user_message = Content(
        parts=[Part(text=f"""Start goal-based project monitoring for our 2-week sprint.

Set SMART goals for:
1. Overall sprint completion (target: 80% of story points)
2. Blocked tasks (target: 0 blocked tasks)
3. Daily velocity (target: maintain at least 4 story points per day)

Monitor progress and adjust strategy as needed to achieve these goals.""")],
        role="user"
    )

    print("\n🎯 Starting Goal-Based Monitoring")
    print("=" * 80)

    # Run the monitoring loop
    iteration = 0
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=user_message
    ):
        if event.content and event.content.parts:
            text = event.content.parts[0].text
            if text:
                print(f"\n[{event.author}] {text[:600]}")

        # After each strategy adjustment, advance time and update iteration
        if event.author == "StrategyAdjuster":
            iteration += 1
            session = await session_service.get_session(APP_NAME, USER_ID, session_id)
            session.state["iteration"] = iteration
            await session_service.save_session(session)

            # Simulate time passing between monitoring cycles
            if iteration < 5:
                project_env.advance_time(MONITORING_INTERVAL_HOURS)
                print(f"\n⏰ Time advanced by {MONITORING_INTERVAL_HOURS} hours...")
                print(f"   Current time: {project_env.current_time.strftime('%Y-%m-%d %H:%M')}")

    # Final results
    print("\n" + "=" * 80)
    print("Monitoring Complete - Final Results")
    print("=" * 80)

    final_evaluation = project_env.evaluate_all_goals()
    print("\n📈 Final Goal Status:")
    print(json.dumps(final_evaluation, indent=2))

    print("\n📊 Final Project State:")
    print(json.dumps(project_env.get_project_snapshot(), indent=2))

    print("\n🔧 Strategy Adjustments Made:")
    for i, adjustment in enumerate(project_env.strategy_adjustments, 1):
        print(f"\n{i}. {adjustment['description']}")
        print(f"   Actions: {', '.join(adjustment['actions'])}")

    print("\n" + "=" * 80)
    print("Pattern Demonstration Complete")
    print("=" * 80)
    print(f"""
Key Observations:
1. SMART Goals: All goals are Specific, Measurable, Achievable, Relevant, Time-bound
2. Continuous Monitoring: Progress tracked every {MONITORING_INTERVAL_HOURS} hours
3. Dynamic Adjustment: Strategy adapted when goals at risk
4. Multi-Metric Tracking: Monitors completion rate, velocity, and blockers
5. Proactive Management: Identifies and resolves issues before deadline

Performance Metrics:
- Total Goals Set: {len(project_env.goals)}
- Monitoring Cycles: {iteration}
- Strategy Adjustments: {len(project_env.strategy_adjustments)}
- Goals Achieved: {final_evaluation['achieved']}
- Goals On Track: {final_evaluation['on_track']}
- Goals At Risk: {final_evaluation['at_risk']}

Production Considerations:
- Integrate with project management tools (Jira, Asana)
- Set up real-time dashboards for stakeholders
- Implement predictive analytics for early risk detection
- Add automated notifications for goal status changes
- Track historical data for velocity predictions
- Include team capacity and resource allocation in goal setting
""")


if __name__ == "__main__":
    # Set up Google Cloud credentials before running
    # export GOOGLE_CLOUD_PROJECT="your-project-id"
    # export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

    asyncio.run(run_goal_monitoring_demo())
