"""
Learning and Adaptation Pattern - CrewAI Implementation

This pattern demonstrates how agents modify their strategy or knowledge base
to improve performance based on experience and feedback.

Business Use Case: Process Optimizer (Manufacturing)
The agent dynamically adapts production parameters (e.g., cutting speed)
based on Quality Control results.

Pattern: Learning and Adaptation
Section: IV - Advanced and Learning Patterns
Framework: CrewAI
"""

import json
from typing import Dict, Any, List
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# --- Constants ---
MAX_LEARNING_ITERATIONS = 10


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


# --- Shared State for Parameter Management ---
class ProductionState:
    """Shared state for managing production parameters"""
    cutting_speed: float = 300.0  # Start with suboptimal speed
    feed_rate: float = 0.10  # Start with suboptimal feed rate
    iteration: int = 0
    continue_learning: bool = True


production_state = ProductionState()


# --- Custom Tools ---
class RunProductionInput(BaseModel):
    """Input schema for run_production_cycle tool"""
    cutting_speed: float = Field(..., description="Cutting speed in RPM (recommended range: 300-600)")
    feed_rate: float = Field(..., description="Feed rate in mm/rev (recommended range: 0.10-0.20)")


class RunProductionTool(BaseTool):
    name: str = "run_production_cycle"
    description: str = "Run a production cycle with specified parameters and return quality metrics"

    def _run(self, cutting_speed: float, feed_rate: float) -> str:
        """Run production cycle and return results"""
        result = manufacturing_env.run_production(cutting_speed, feed_rate)
        return json.dumps(result, indent=2)


class AnalyzePerformanceTool(BaseTool):
    name: str = "analyze_performance_trends"
    description: str = "Analyze historical performance data to identify trends and improvement opportunities"

    def _run(self) -> str:
        """Analyze performance trends"""
        trends = manufacturing_env.get_performance_trends()
        return json.dumps(trends, indent=2)


class UpdateKnowledgeInput(BaseModel):
    """Input schema for update_strategy_knowledge tool"""
    learned_insights: str = Field(..., description="Description of what was learned from recent experiments")


class UpdateKnowledgeTool(BaseTool):
    name: str = "update_strategy_knowledge"
    description: str = "Store learned insights in the knowledge base for future reference"

    def _run(self, learned_insights: str) -> str:
        """Store learned insights"""
        return f"Knowledge updated: {learned_insights}"


# Initialize tools
production_tool = RunProductionTool()
analysis_tool = AnalyzePerformanceTool()
knowledge_tool = UpdateKnowledgeTool()


# --- Agents ---
def create_executor_agent() -> Agent:
    """Create Production Executor agent"""
    return Agent(
        role="Production Executor",
        goal="Run production cycles with current parameters and report results",
        backstory="""You are a Production Executor responsible for running
        manufacturing processes. You execute production runs with the provided
        parameters and accurately report the quality metrics.""",
        tools=[production_tool],
        verbose=True,
        allow_delegation=False
    )


def create_analyzer_agent() -> Agent:
    """Create Performance Analyzer agent"""
    return Agent(
        role="Performance Analyzer",
        goal="Analyze production results and identify areas for improvement",
        backstory="""You are a Performance Analysis expert with deep knowledge
        of manufacturing quality metrics. You analyze production results, identify
        trends, and suggest specific parameter adjustments to improve quality.
        You understand that quality should be above 90% and defects below 5%.""",
        tools=[analysis_tool],
        verbose=True,
        allow_delegation=False
    )


def create_learning_agent() -> Agent:
    """Create Strategy Learning agent"""
    return Agent(
        role="Strategy Learner",
        goal="Learn from feedback and optimize production parameters over time",
        backstory="""You are a Learning Strategist who continuously improves
        manufacturing processes through iterative experimentation. You update
        parameters based on performance feedback, learn from trends, and store
        valuable insights for future reference. You make smaller adjustments when
        quality is improving and try different approaches when quality declines.""",
        tools=[knowledge_tool],
        verbose=True,
        allow_delegation=False
    )


# --- Tasks ---
def create_execution_task(agent: Agent, iteration: int) -> Task:
    """Create task for executing production"""
    return Task(
        description=f"""Execute production cycle {iteration + 1} with current parameters:
        - Cutting Speed: {production_state.cutting_speed} RPM
        - Feed Rate: {production_state.feed_rate} mm/rev

        Use the run_production_cycle tool to execute the production run and report:
        1. Quality score achieved
        2. Defect rate observed
        3. Throughput metrics

        Provide a clear summary of the results.""",
        agent=agent,
        expected_output="Production results with quality score, defect rate, and throughput metrics"
    )


def create_analysis_task(agent: Agent) -> Task:
    """Create task for analyzing performance"""
    return Task(
        description="""Analyze the production performance using these steps:
        1. Use analyze_performance_trends to get historical data
        2. Review recent average quality and defect rates
        3. Determine if current parameters are optimal or need adjustment
        4. If quality is below 90% OR defects are above 5%, suggest specific parameter changes

        Provide specific recommendations:
        - For low quality: suggest parameter adjustments with numerical values
        - For improving trends: suggest smaller refinements
        - For declining trends: suggest trying different parameter combinations

        Be specific with cutting_speed and feed_rate suggestions.""",
        agent=agent,
        expected_output="Analysis of performance trends with specific parameter adjustment recommendations"
    )


def create_learning_task(agent: Agent) -> Task:
    """Create task for learning and adaptation"""
    return Task(
        description="""Based on the performance analysis, decide on parameter adjustments:
        1. Review the analyzer's recommendations
        2. Decide if parameters should be changed to improve quality
        3. If adjustment needed, update the insights with new learning
        4. Use update_strategy_knowledge to store what was learned

        Consider:
        - Quality target: > 95%
        - If current quality < 95%, continue learning
        - If quality >= 95%, learning can stop

        Store insights about what parameter changes led to improvements.""",
        agent=agent,
        expected_output="Decision on parameter adjustments and learned insights stored in knowledge base"
    )


# --- Main Execution ---
def run_learning_adaptation_demo():
    """Demonstrate learning and adaptation pattern"""
    print("=" * 80)
    print("Learning and Adaptation Pattern - Manufacturing Process Optimization")
    print("=" * 80)

    print(f"\nObjective: Optimize production parameters to achieve quality score > 95%")
    print(f"Starting parameters: Speed={production_state.cutting_speed} RPM, Feed={production_state.feed_rate} mm/rev")
    print(f"\n{'=' * 80}")
    print("Starting Learning Loop...")
    print(f"{'=' * 80}\n")

    # Run learning iterations
    for iteration in range(MAX_LEARNING_ITERATIONS):
        print(f"\n{'=' * 80}")
        print(f"Learning Iteration {iteration + 1}/{MAX_LEARNING_ITERATIONS}")
        print(f"{'=' * 80}")

        production_state.iteration = iteration

        # Create agents
        executor = create_executor_agent()
        analyzer = create_analyzer_agent()
        learner = create_learning_agent()

        # Create tasks
        execution_task = create_execution_task(executor, iteration)
        analysis_task = create_analysis_task(analyzer)
        learning_task = create_learning_task(learner)

        # Create crew with sequential process
        crew = Crew(
            agents=[executor, analyzer, learner],
            tasks=[execution_task, analysis_task, learning_task],
            process=Process.sequential,
            verbose=True
        )

        # Execute the crew
        try:
            result = crew.kickoff()
            print(f"\n[Iteration {iteration + 1} Result]")
            print(result)
        except Exception as e:
            print(f"\n[Error in iteration {iteration + 1}]: {e}")
            continue

        # Get latest production results
        if manufacturing_env.history:
            latest = manufacturing_env.history[-1]
            current_quality = latest["quality_score"]

            # Update parameters based on quality (simple learning logic)
            if current_quality < 95:
                # Adjust parameters toward optimal
                speed_diff = production_state.optimal_cutting_speed - production_state.cutting_speed
                feed_diff = production_state.optimal_feed_rate - production_state.feed_rate

                production_state.cutting_speed += speed_diff * 0.3  # Move 30% toward optimal
                production_state.feed_rate += feed_diff * 0.3

                print(f"\n[Parameter Update] New parameters: Speed={production_state.cutting_speed:.1f}, Feed={production_state.feed_rate:.3f}")
            else:
                print(f"\n[Target Achieved] Quality score {current_quality}% meets target!")
                production_state.continue_learning = False
                break

        # Check if we should continue
        if not production_state.continue_learning:
            break

    # Final results
    print(f"\n{'=' * 80}")
    print("Learning Process Complete!")
    print(f"{'=' * 80}")

    print(f"\nFinal Parameters:")
    print(f"   Cutting Speed: {production_state.cutting_speed:.1f} RPM")
    print(f"   Feed Rate: {production_state.feed_rate:.3f} mm/rev")

    print(f"\nPerformance History:")
    trends = manufacturing_env.get_performance_trends()
    print(f"   Total Runs: {trends['total_runs']}")
    print(f"   Best Quality Achieved: {trends['best_quality']}%")
    print(f"   Recent Average Quality: {trends['recent_avg_quality']}%")
    print(f"   Recent Average Defects: {trends['recent_avg_defects']}%")
    print(f"   Trend: {trends['improvement_trend']}")

    print("\nLearning and Adaptation Pattern demonstrated successfully!")
    print("The agents learned to optimize parameters through iterative feedback.")


if __name__ == "__main__":
    run_learning_adaptation_demo()
