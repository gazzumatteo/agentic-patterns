"""
Learning and Adaptation Pattern - Google ADK Implementation

This pattern demonstrates how agents modify their strategy or knowledge base
to improve performance based on experience and feedback.

Business Use Case: Process Optimizer (Manufacturing)
The agent dynamically adapts production parameters (e.g., cutting speed)
based on Quality Control results.

Pattern: Learning and Adaptation
Section: IV - Advanced and Learning Patterns
Framework: Google ADK
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, Any, List
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.tools import FunctionTool
from google.genai.types import Content, Part, FunctionCall


# --- Constants ---
APP_NAME = "learning_adaptation_app"
USER_ID = "manufacturing_user"
MODEL = "gemini-2.5-flash-exp"


# --- Simulated Manufacturing Environment ---
class ManufacturingEnvironment:
    """Simulates a manufacturing process with quality metrics"""

    def __init__(self):
        self.optimal_cutting_speed = 450  # Optimal speed in RPM
        self.optimal_feed_rate = 0.15  # Optimal feed rate in mm/rev
        self.history: List[Dict[str, Any]] = []

    def run_production(self, cutting_speed: float, feed_rate: float) -> Dict[str, Any]:
        """
        Simulate production run and return quality metrics.
        Quality decreases as parameters deviate from optimal values.
        """
        speed_deviation = abs(cutting_speed - self.optimal_cutting_speed) / self.optimal_cutting_speed
        feed_deviation = abs(feed_rate - self.optimal_feed_rate) / self.optimal_feed_rate

        # Calculate quality score (0-100)
        quality_score = max(0, 100 - (speed_deviation * 50 + feed_deviation * 50))

        # Calculate defect rate
        defect_rate = min(20, speed_deviation * 10 + feed_deviation * 10)

        result = {
            "cutting_speed": cutting_speed,
            "feed_rate": feed_rate,
            "quality_score": round(quality_score, 2),
            "defect_rate": round(defect_rate, 2),
            "throughput": round(cutting_speed * feed_rate * 10, 2)  # Units per hour
        }

        self.history.append(result)
        return result

    def get_performance_trends(self) -> Dict[str, Any]:
        """Analyze historical performance trends"""
        if not self.history:
            return {"message": "No historical data available"}

        recent_runs = self.history[-5:] if len(self.history) >= 5 else self.history
        avg_quality = sum(r["quality_score"] for r in recent_runs) / len(recent_runs)
        avg_defects = sum(r["defect_rate"] for r in recent_runs) / len(recent_runs)

        return {
            "total_runs": len(self.history),
            "recent_avg_quality": round(avg_quality, 2),
            "recent_avg_defects": round(avg_defects, 2),
            "best_quality": max(r["quality_score"] for r in self.history),
            "improvement_trend": "improving" if len(self.history) > 1 and
                                 self.history[-1]["quality_score"] > self.history[0]["quality_score"]
                                 else "needs_improvement"
        }


# Initialize manufacturing environment
manufacturing_env = ManufacturingEnvironment()


# --- Tools ---
def run_production_cycle(cutting_speed: float, feed_rate: float) -> str:
    """
    Run a production cycle with specified parameters and return quality metrics.

    Args:
        cutting_speed: Cutting speed in RPM (recommended range: 300-600)
        feed_rate: Feed rate in mm/rev (recommended range: 0.10-0.20)

    Returns:
        JSON string with production results and quality metrics
    """
    result = manufacturing_env.run_production(cutting_speed, feed_rate)
    return json.dumps(result, indent=2)


def analyze_performance_trends() -> str:
    """
    Analyze historical performance data to identify trends and improvement opportunities.

    Returns:
        JSON string with performance analysis
    """
    trends = manufacturing_env.get_performance_trends()
    return json.dumps(trends, indent=2)


def update_strategy_knowledge(learned_insights: str) -> str:
    """
    Store learned insights in the knowledge base for future reference.

    Args:
        learned_insights: Description of what was learned from recent experiments

    Returns:
        Confirmation message
    """
    # In production, this would write to a persistent knowledge base
    return f"Knowledge updated: {learned_insights}"


# Create FunctionTools
production_tool = FunctionTool(func=run_production_cycle)
analysis_tool = FunctionTool(func=analyze_performance_trends)
knowledge_tool = FunctionTool(func=update_strategy_knowledge)


# --- Agents ---
# Agent 1: Executor - Runs production with current parameters
executor_agent = LlmAgent(
    model=MODEL,
    name="ProductionExecutor",
    instruction="""You are a Production Executor agent. Your role is to:
    1. Run production cycles with the parameters from session state (cutting_speed, feed_rate)
    2. Report the results clearly
    3. Store results in session state under 'last_production_result'

    Use the run_production_cycle tool with the current parameters.""",
    tools=[production_tool],
)

# Agent 2: Analyzer - Analyzes results and suggests improvements
analyzer_agent = LlmAgent(
    model=MODEL,
    name="PerformanceAnalyzer",
    instruction="""You are a Performance Analyzer agent. Your role is to:
    1. Review the last production result from session state
    2. Analyze performance trends using the analysis tool
    3. Identify if quality is below 90 or defect rate is above 5%
    4. Suggest parameter adjustments to improve quality
    5. Store your analysis in 'performance_analysis' in state

    Be specific with numerical suggestions for cutting_speed and feed_rate adjustments.""",
    tools=[analysis_tool],
)

# Agent 3: Learning Agent - Updates strategy based on feedback
learning_agent = LlmAgent(
    model=MODEL,
    name="StrategyLearner",
    instruction="""You are a Strategy Learning agent. Your role is to:
    1. Review the performance analysis and production history
    2. Decide if parameters should be adjusted based on quality metrics
    3. Update cutting_speed and feed_rate in session state if improvement is needed
    4. Store learned insights using the knowledge tool
    5. Set 'continue_learning' to true if quality < 95, false otherwise

    Learn from trends: if quality is improving, make smaller adjustments.
    If quality is declining, try different parameter combinations.""",
    tools=[knowledge_tool],
)


# --- Loop Workflow ---
def should_continue_learning(session: Session) -> bool:
    """Exit condition: stop when quality reaches target or max iterations"""
    continue_flag = session.state.get("continue_learning", True)
    iteration = session.state.get("iteration", 0)
    return continue_flag and iteration < 10


learning_loop = LoopAgent(
    name="LearningLoop",
    sub_agents=[executor_agent, analyzer_agent, learning_agent],
    exit_condition=should_continue_learning,
)


# --- Main Execution ---
async def run_learning_adaptation_demo():
    """Demonstrate learning and adaptation pattern"""
    print("=" * 80)
    print("Learning and Adaptation Pattern - Manufacturing Process Optimization")
    print("=" * 80)

    # Initialize services
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()

    # Create runner
    runner = Runner(
        agent=learning_loop,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )

    # Create session
    session_id = "learning_session_001"
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id
    )

    # Initialize session state with starting parameters (suboptimal)
    session = await session_service.get_session(APP_NAME, USER_ID, session_id)
    session.state.update({
        "cutting_speed": 300,  # Start with suboptimal speed
        "feed_rate": 0.10,  # Start with suboptimal feed rate
        "iteration": 0,
        "continue_learning": True
    })
    await session_service.save_session(session)

    # User message to start learning
    user_message = Content(
        parts=[Part(text="Start the learning process to optimize production parameters for maximum quality.")],
        role="user"
    )

    print("\n🎯 Objective: Optimize production parameters to achieve quality score > 95%")
    print(f"📊 Starting parameters: Speed=300 RPM, Feed=0.10 mm/rev")
    print("\n" + "=" * 80)
    print("Starting Learning Loop...")
    print("=" * 80 + "\n")

    # Run the learning loop
    iteration = 0
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=user_message
    ):
        if event.content and event.content.parts:
            text = event.content.parts[0].text
            if text:
                print(f"\n[{event.author}] {text}")

        # Track iterations
        if event.author == "StrategyLearner":
            iteration += 1
            session = await session_service.get_session(APP_NAME, USER_ID, session_id)
            session.state["iteration"] = iteration
            await session_service.save_session(session)

    # Final results
    print("\n" + "=" * 80)
    print("Learning Process Complete!")
    print("=" * 80)

    final_session = await session_service.get_session(APP_NAME, USER_ID, session_id)
    print(f"\n📈 Final Parameters:")
    print(f"   Cutting Speed: {final_session.state.get('cutting_speed')} RPM")
    print(f"   Feed Rate: {final_session.state.get('feed_rate')} mm/rev")

    print(f"\n🎯 Performance History:")
    trends = manufacturing_env.get_performance_trends()
    print(f"   Total Runs: {trends['total_runs']}")
    print(f"   Best Quality Achieved: {trends['best_quality']}%")
    print(f"   Recent Average Quality: {trends['recent_avg_quality']}%")
    print(f"   Recent Average Defects: {trends['recent_avg_defects']}%")
    print(f"   Trend: {trends['improvement_trend']}")

    print("\n✅ Learning and Adaptation Pattern demonstrated successfully!")
    print("   The agent learned to optimize parameters through iterative feedback.")


if __name__ == "__main__":
    asyncio.run(run_learning_adaptation_demo())
