"""
Pattern 31: Exploration and Discovery
Agents venture beyond programmed boundaries to generate and test hypotheses,
enabling breakthrough discoveries in complex domains.

Business Example: Drug Interaction Discovery
- Agent analyzes 10M patient records
- Explores correlations beyond predetermined hypotheses
- Tests novel drug combination theories
- Validates findings against clinical trials

This example demonstrates CrewAI's competitive and exploratory capabilities
for hypothesis generation, testing, and breakthrough discovery.

Mermaid Diagram Reference: See diagrams/31_exploration_discovery.mermaid
"""

import json
import random
from typing import Any, Dict, List
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool


class DiscoveryTracker:
    """Tracks exploration progress and discoveries."""

    def __init__(self):
        self.hypotheses = []
        self.discoveries = []
        self.exploration_stats = {
            "total_tested": 0,
            "valid": 0,
            "novel": 0,
            "high_significance": 0
        }

    def record_hypothesis(self, hypothesis: Dict[str, Any]) -> None:
        """Record a tested hypothesis."""
        self.hypotheses.append(hypothesis)
        self.exploration_stats["total_tested"] += 1

        if hypothesis.get("is_valid"):
            self.exploration_stats["valid"] += 1
        if hypothesis.get("is_novel"):
            self.exploration_stats["novel"] += 1
        if hypothesis.get("significance", 0) > 0.8:
            self.exploration_stats["high_significance"] += 1

        # Track discoveries
        if (hypothesis.get("is_valid") and
            hypothesis.get("is_novel") and
            hypothesis.get("significance", 0) > 0.75):
            self.discoveries.append(hypothesis)

    def get_metrics(self) -> Dict[str, Any]:
        """Get exploration metrics."""
        total = self.exploration_stats["total_tested"]
        return {
            "total_hypotheses": total,
            "success_rate": self.exploration_stats["valid"] / total if total > 0 else 0,
            "novelty_rate": self.exploration_stats["novel"] / total if total > 0 else 0,
            "discoveries": len(self.discoveries),
            "discovery_rate": len(self.discoveries) / total if total > 0 else 0
        }


# Global tracker
discovery_tracker = DiscoveryTracker()


@tool("Explore data patterns")
def explore_data_patterns(data_context: str, exploration_mode: str) -> str:
    """
    Explore data to find patterns and generate hypotheses.

    Args:
        data_context: JSON string with data context
        exploration_mode: 'creative' for novel ideas, 'systematic' for thorough

    Returns:
        JSON with discovered patterns and hypothesis suggestions
    """
    context = json.loads(data_context)

    # Simulate pattern discovery
    pattern_types = [
        "correlation", "interaction_effect", "non_linear",
        "conditional_dependency", "anomaly", "temporal_pattern"
    ]

    num_patterns = random.randint(2, 5) if exploration_mode == "creative" else random.randint(3, 6)

    patterns = []
    for i in range(num_patterns):
        pattern = {
            "id": f"pattern_{i+1}",
            "type": random.choice(pattern_types),
            "strength": round(random.random(), 2),
            "novelty": round(random.random(), 2),
            "description": f"Pattern {i+1}: Potential {random.choice(pattern_types)} detected",
            "suggested_hypothesis": f"Test if {random.choice(['variable A', 'factor X', 'condition Y'])} "
                                   f"influences {random.choice(['outcome B', 'metric Z', 'result W'])}"
        }
        patterns.append(pattern)

    return json.dumps({
        "patterns_found": len(patterns),
        "patterns": patterns,
        "exploration_mode": exploration_mode,
        "data_volume": context.get("sample_size", 0)
    }, indent=2)


@tool("Test hypothesis")
def test_hypothesis(hypothesis: str) -> str:
    """
    Test a hypothesis against data and return validation results.

    Args:
        hypothesis: The hypothesis statement to test

    Returns:
        JSON with test results, validity, novelty, and significance
    """
    # Simulate hypothesis testing
    is_valid = random.random() > 0.4  # 60% validation rate
    is_novel = random.random() > 0.5  # 50% novelty rate
    significance = random.random()

    # Boost significance for valid + novel
    if is_valid and is_novel:
        significance = random.random() * 0.3 + 0.7  # 0.7-1.0 range

    test_result = {
        "hypothesis": hypothesis,
        "is_valid": is_valid,
        "is_novel": is_novel,
        "significance": round(significance, 2),
        "confidence_interval": [0.85, 0.95] if is_valid else [0.3, 0.6],
        "p_value": round(random.random() * 0.05, 4) if is_valid else round(random.random() * 0.3 + 0.05, 4),
        "effect_size": round(random.random(), 2),
        "statistical_power": round(random.random() * 0.3 + 0.7, 2) if is_valid else round(random.random() * 0.4 + 0.3, 2)
    }

    # Record in tracker
    discovery_tracker.record_hypothesis(test_result)

    if is_valid and is_novel and significance > 0.75:
        test_result["discovery_flag"] = "🎉 BREAKTHROUGH DISCOVERY"
        test_result["potential_impact"] = random.choice([
            "Could reduce adverse events by 15-20%",
            "Potential for new treatment protocol",
            "May enable personalized medicine approach",
            "Suggests novel therapeutic combination",
            "Enables early risk prediction"
        ])

    return json.dumps(test_result, indent=2)


@tool("Get exploration metrics")
def get_exploration_metrics() -> str:
    """
    Get current exploration and discovery metrics.

    Returns:
        JSON with exploration performance statistics
    """
    metrics = discovery_tracker.get_metrics()

    return json.dumps({
        "metrics": metrics,
        "discoveries": discovery_tracker.discoveries,
        "total_hypotheses": discovery_tracker.exploration_stats["total_tested"],
        "insights": f"Discovery rate: {metrics['discovery_rate']:.1%}, "
                   f"Success rate: {metrics['success_rate']:.1%}"
    }, indent=2)


def create_exploration_crew() -> Crew:
    """
    Create a crew specialized for exploration and discovery.

    Returns:
        Configured Crew with exploratory agents
    """

    # Agent 1: Creative Explorer (generates diverse hypotheses)
    creative_explorer = Agent(
        role="Creative Hypothesis Explorer",
        goal="Generate novel, creative hypotheses that go beyond obvious patterns",
        backstory="""You are an innovative thinker who excels at making
        unexpected connections. You look at data from unique angles and propose
        hypotheses that others wouldn't think of. You're not afraid of
        unconventional ideas and often find breakthrough insights in overlooked
        correlations.""",
        tools=[explore_data_patterns],
        verbose=True,
        allow_delegation=False
    )

    # Agent 2: Systematic Explorer (thorough, methodical)
    systematic_explorer = Agent(
        role="Systematic Hypothesis Generator",
        goal="Generate comprehensive hypotheses through methodical data analysis",
        backstory="""You are a thorough and systematic researcher who leaves no
        stone unturned. You methodically explore data spaces, generating
        hypotheses based on rigorous statistical analysis. Your strength is
        comprehensive coverage of the hypothesis space.""",
        tools=[explore_data_patterns],
        verbose=True,
        allow_delegation=False
    )

    # Agent 3: Hypothesis Validator
    hypothesis_validator = Agent(
        role="Rigorous Scientific Validator",
        goal="Test hypotheses with scientific rigor and identify true discoveries",
        backstory="""You are a meticulous scientist who validates hypotheses
        against data with unwavering rigor. You assess validity, novelty, and
        significance. You separate signal from noise and identify genuine
        discoveries. Your validation ensures scientific integrity.""",
        tools=[test_hypothesis, get_exploration_metrics],
        verbose=True,
        allow_delegation=False
    )

    # Agent 4: Discovery Synthesizer
    discovery_synthesizer = Agent(
        role="Discovery Synthesis Specialist",
        goal="Identify breakthrough discoveries and synthesize insights",
        backstory="""You are an expert at seeing the bigger picture. You review
        all tested hypotheses, identify the most significant discoveries, and
        synthesize them into actionable insights. You understand both the
        scientific and business implications of discoveries.""",
        tools=[get_exploration_metrics],
        verbose=True,
        allow_delegation=False
    )

    return Crew(
        agents=[creative_explorer, systematic_explorer, hypothesis_validator, discovery_synthesizer],
        tasks=[],  # Tasks created dynamically
        process=Process.sequential,
        verbose=True,
        memory=True
    )


def run_discovery_iteration(
    crew: Crew,
    data_context: Dict[str, Any],
    iteration: int
) -> Dict[str, Any]:
    """
    Run a single exploration iteration.

    Args:
        crew: The exploration crew
        data_context: Current data context
        iteration: Iteration number

    Returns:
        Results from this iteration
    """
    print(f"\n{'='*80}")
    print(f"EXPLORATION ITERATION {iteration}")
    print(f"{'='*80}")

    # Task 1: Creative exploration
    creative_task = Task(
        description=f"""
        Explore the data creatively to find novel patterns and generate hypotheses.

        Data Context:
        {json.dumps(data_context, indent=2)}

        Use creative exploration mode. Look for:
        - Unexpected correlations
        - Non-obvious interactions
        - Edge cases and anomalies
        - Cross-domain patterns

        Generate at least 3 creative hypotheses that go beyond conventional thinking.
        """,
        agent=crew.agents[0],
        expected_output="List of creative hypotheses with rationale and novelty scores"
    )

    # Task 2: Systematic exploration
    systematic_task = Task(
        description=f"""
        Explore the data systematically to ensure comprehensive coverage.

        Data Context:
        {json.dumps(data_context, indent=2)}

        Use systematic exploration mode. Cover:
        - All major variable combinations
        - Interaction effects
        - Conditional dependencies
        - Temporal patterns

        Generate at least 3 systematic hypotheses based on thorough analysis.
        """,
        agent=crew.agents[1],
        expected_output="List of systematic hypotheses with statistical backing"
    )

    # Task 3: Validate hypotheses
    validation_task = Task(
        description=f"""
        Test all generated hypotheses from creative and systematic exploration.

        For each hypothesis:
        1. Test against data
        2. Assess validity (is it supported?)
        3. Assess novelty (is it new?)
        4. Calculate significance
        5. Flag potential discoveries

        Provide summary of:
        - Valid hypotheses
        - Novel findings
        - High-significance discoveries
        - Current exploration metrics
        """,
        agent=crew.agents[2],
        expected_output="Validation results for all hypotheses with discovery flags",
        context=[creative_task, systematic_task]
    )

    # Task 4: Synthesize discoveries
    synthesis_task = Task(
        description=f"""
        Synthesize the exploration results from this iteration.

        Review all validation results and:
        1. Identify breakthrough discoveries (valid + novel + high significance)
        2. Summarize key patterns across hypotheses
        3. Assess exploration efficiency
        4. Recommend next exploration directions

        Provide:
        - List of major discoveries with impact assessment
        - Emerging patterns
        - Exploration performance summary
        - Strategic recommendations
        """,
        agent=crew.agents[3],
        expected_output="Synthesis of discoveries with strategic recommendations",
        context=[validation_task]
    )

    # Execute tasks
    crew.tasks = [creative_task, systematic_task, validation_task, synthesis_task]
    result = crew.kickoff()

    return {
        "iteration": iteration,
        "result": str(result),
        "metrics": discovery_tracker.get_metrics()
    }


def main():
    """Main execution function demonstrating exploration and discovery."""

    print("=" * 80)
    print("Pattern 31: Exploration and Discovery (CrewAI)")
    print("Multi-Agent Hypothesis Exploration System")
    print("=" * 80)

    # Create exploration crew
    crew = create_exploration_crew()

    # Data context for drug interaction discovery
    data_contexts = [
        {
            "domain": "drug interactions",
            "sample_size": 10000000,
            "drug_combinations": 5000,
            "adverse_events": 1200,
            "positive_outcomes": 8500,
            "iteration": 1
        },
        {
            "domain": "drug interactions",
            "sample_size": 10500000,
            "drug_combinations": 5200,
            "adverse_events": 1250,
            "positive_outcomes": 8750,
            "iteration": 2
        },
        {
            "domain": "drug interactions",
            "sample_size": 11000000,
            "drug_combinations": 5400,
            "adverse_events": 1300,
            "positive_outcomes": 9000,
            "iteration": 3
        }
    ]

    # Run exploration iterations
    all_results = []
    for idx, context in enumerate(data_contexts, 1):
        result = run_discovery_iteration(crew, context, idx)
        all_results.append(result)

        # Print iteration metrics
        metrics = result["metrics"]
        print(f"\n📊 Iteration {idx} Metrics:")
        print(f"   Success Rate: {metrics['success_rate']:.1%}")
        print(f"   Novelty Rate: {metrics['novelty_rate']:.1%}")
        print(f"   Discoveries: {metrics['discoveries']}")
        print(f"   Discovery Rate: {metrics['discovery_rate']:.1%}")

    # Final summary
    print("\n\n" + "=" * 80)
    print("EXPLORATION CAMPAIGN RESULTS")
    print("=" * 80)

    final_metrics = discovery_tracker.get_metrics()
    print(f"\n📊 Overall Performance:")
    print(f"   Total Hypotheses: {final_metrics['total_hypotheses']}")
    print(f"   Success Rate: {final_metrics['success_rate']:.1%}")
    print(f"   Novelty Rate: {final_metrics['novelty_rate']:.1%}")
    print(f"   Total Discoveries: {final_metrics['discoveries']}")
    print(f"   Discovery Rate: {final_metrics['discovery_rate']:.1%}")

    print(f"\n🎉 Breakthrough Discoveries:")
    for idx, discovery in enumerate(discovery_tracker.discoveries, 1):
        print(f"\n   Discovery {idx}:")
        print(f"   - Significance: {discovery['significance']:.2f}")
        print(f"   - P-value: {discovery.get('p_value', 'N/A')}")
        if discovery.get('potential_impact'):
            print(f"   - Impact: {discovery['potential_impact']}")

    print("\n" + "=" * 80)
    print("Pattern Demonstrated: Exploration and Discovery")
    print("=" * 80)
    print("""
    Key Observations:
    1. Dual Exploration: Creative + systematic approaches combined
    2. Competitive Generation: Multiple agents generate diverse hypotheses
    3. Rigorous Validation: Scientific testing with multiple criteria
    4. Discovery Synthesis: Patterns identified across hypotheses
    5. Continuous Learning: Memory enables pattern recognition across iterations

    CrewAI Advantages:
    - Role-based specialization (creative vs systematic exploration)
    - Natural collaboration between explorer types
    - Built-in memory for pattern learning
    - Easy scaling to more exploration strategies
    - Clear separation of generation and validation

    Business Impact (from article):
    - 3 beneficial drug interactions identified
    - 7 dangerous interactions previously unknown
    - 2 patents filed
    - Estimated value: $500M over 5 years

    Applications:
    - Drug discovery and safety analysis
    - Market opportunity identification
    - Scientific research acceleration
    - Risk pattern discovery
    - Innovation and R&D optimization
    """)


if __name__ == "__main__":
    # Set up API keys before running:
    # export OPENAI_API_KEY="your-openai-key"
    # or
    # export ANTHROPIC_API_KEY="your-anthropic-key"

    main()
