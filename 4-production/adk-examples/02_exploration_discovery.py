"""
Pattern 31: Exploration and Discovery
Agents venture beyond programmed boundaries to generate and test hypotheses,
enabling breakthrough discoveries in complex domains.

Business Example: Drug Interaction Discovery
- Agent analyzes 10M patient records
- Explores correlations beyond predetermined hypotheses
- Tests novel drug combination theories
- Validates findings against clinical trials

This example demonstrates Google ADK's exploration capabilities with
hypothesis generation, testing, and discovery of novel patterns.

Mermaid Diagram Reference: See diagrams/31_exploration_discovery.mermaid
"""

import asyncio
import json
import random
from typing import Any, Dict, List, Tuple
from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types


class HypothesisSpace:
    """Manages hypothesis generation and testing for exploration."""

    def __init__(self):
        self.hypotheses: List[Dict] = []
        self.tested_hypotheses: List[Dict] = []
        self.discoveries: List[Dict] = []
        self.exploration_budget = 100

    def generate_hypothesis(
        self,
        data_context: Dict[str, Any],
        exploration_strategy: str = "epsilon_greedy",
        epsilon: float = 0.3
    ) -> Dict[str, Any]:
        """
        Generate a hypothesis to test based on data context.

        Args:
            data_context: Current data and patterns
            exploration_strategy: Strategy for exploration vs exploitation
            epsilon: Exploration rate (0.0 = pure exploitation, 1.0 = pure exploration)

        Returns:
            Generated hypothesis dictionary
        """
        # Epsilon-greedy: explore new areas vs exploit known patterns
        explore = random.random() < epsilon

        if explore or len(self.discoveries) == 0:
            # Generate novel hypothesis (exploration)
            hypothesis_type = random.choice([
                "correlation_discovery",
                "interaction_effect",
                "non_linear_relationship",
                "conditional_dependency",
                "anomaly_pattern"
            ])
        else:
            # Refine existing successful patterns (exploitation)
            hypothesis_type = "refinement"

        hypothesis = {
            "id": f"hyp_{len(self.hypotheses) + 1}",
            "type": hypothesis_type,
            "is_exploration": explore,
            "data_context": data_context,
            "status": "generated",
            "novelty_score": random.random() if explore else 0.3
        }

        self.hypotheses.append(hypothesis)
        return hypothesis

    def test_hypothesis(
        self,
        hypothesis: Dict[str, Any],
        test_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Test a hypothesis and record results.

        Args:
            hypothesis: The hypothesis to test
            test_results: Results from testing

        Returns:
            Updated hypothesis with test results
        """
        is_valid = test_results.get("valid", False)
        is_novel = test_results.get("novel", False)
        significance = test_results.get("significance", 0.0)

        hypothesis["status"] = "tested"
        hypothesis["test_results"] = test_results
        hypothesis["is_valid"] = is_valid
        hypothesis["is_novel"] = is_novel
        hypothesis["significance"] = significance

        self.tested_hypotheses.append(hypothesis)

        # If valid and novel, it's a discovery
        if is_valid and is_novel and significance > 0.8:
            discovery = {
                "hypothesis_id": hypothesis["id"],
                "type": hypothesis["type"],
                "significance": significance,
                "description": test_results.get("description", ""),
                "potential_impact": test_results.get("impact", "Unknown")
            }
            self.discoveries.append(discovery)

        return hypothesis

    def get_exploration_metrics(self) -> Dict[str, Any]:
        """Get current exploration performance metrics."""
        total = len(self.tested_hypotheses)
        valid = sum(1 for h in self.tested_hypotheses if h.get("is_valid", False))
        novel = sum(1 for h in self.tested_hypotheses if h.get("is_novel", False))

        return {
            "total_hypotheses": total,
            "valid_hypotheses": valid,
            "novel_discoveries": len(self.discoveries),
            "success_rate": valid / total if total > 0 else 0.0,
            "novelty_rate": novel / total if total > 0 else 0.0,
            "exploration_efficiency": len(self.discoveries) / total if total > 0 else 0.0
        }


# Create hypothesis generator agent
hypothesis_generator = LlmAgent(
    name="HypothesisGenerator",
    model="gemini-2.5-flash",
    instruction="""
    You are a creative hypothesis generator for scientific discovery.

    Given a data context, generate novel hypotheses to test. Think beyond
    obvious relationships. Consider:
    - Non-linear interactions
    - Conditional dependencies
    - Anomalous patterns
    - Cross-domain correlations

    For each hypothesis, provide:
    1. Clear statement of the hypothesis
    2. Rationale for why it's worth testing
    3. Expected impact if validated
    4. Suggested test methodology

    Be creative and don't be afraid to suggest unconventional ideas.
    Output as structured JSON.
    """,
    description="Generates novel hypotheses for exploration",
    output_key="hypothesis_proposal"
)

# Create hypothesis validator agent
hypothesis_validator = LlmAgent(
    name="HypothesisValidator",
    model="gemini-2.5-flash",
    instruction="""
    You are a rigorous scientific validator.

    Test hypotheses against data and existing knowledge. Evaluate:
    1. Validity: Does the data support this hypothesis?
    2. Novelty: Is this a new finding or already known?
    3. Significance: How important is this discovery?
    4. Reproducibility: Is this result consistent?

    Provide:
    - Validation result (valid/invalid)
    - Novelty assessment (novel/known)
    - Significance score (0.0 to 1.0)
    - Supporting evidence
    - Potential applications

    Be objective and thorough. Output as structured JSON.
    """,
    description="Validates and evaluates hypotheses",
    output_key="validation_result"
)

# Create discovery synthesizer agent
discovery_synthesizer = LlmAgent(
    name="DiscoverySynthesizer",
    model="gemini-2.5-flash",
    instruction="""
    You are a discovery synthesizer who identifies breakthrough insights.

    Review validated hypotheses and identify:
    1. Major discoveries with high impact
    2. Patterns across multiple hypotheses
    3. Unexpected connections
    4. Practical applications

    Synthesize findings into:
    - Key discoveries
    - Overarching patterns
    - Recommended next steps
    - Potential business/scientific value

    Output clear, actionable insights.
    """,
    description="Synthesizes discoveries into insights",
    output_key="synthesis"
)


async def run_exploration_cycle(
    data_domain: str,
    num_iterations: int = 5,
    epsilon: float = 0.3
) -> Dict[str, Any]:
    """
    Run an exploration and discovery cycle.

    Args:
        data_domain: The domain being explored (e.g., "drug interactions")
        num_iterations: Number of exploration iterations
        epsilon: Exploration rate (0.0-1.0)

    Returns:
        Dictionary with discoveries and exploration metrics
    """
    hypothesis_space = HypothesisSpace()
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()
    session_id = "exploration_session_001"
    app_name = "exploration_agent"
    user_id = "system"

    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
    session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)

    discoveries_log = []

    for iteration in range(num_iterations):
        print(f"\n{'='*80}")
        print(f"EXPLORATION ITERATION {iteration + 1}/{num_iterations}")
        print(f"{'='*80}")

        # Simulate data context (in real scenario, would be actual data analysis)
        data_context = generate_data_context(data_domain, iteration)

        # Generate hypothesis
        hypothesis = hypothesis_space.generate_hypothesis(
            data_context=data_context,
            epsilon=epsilon
        )

        print(f"\n📋 Generated Hypothesis (ID: {hypothesis['id']})")
        print(f"   Type: {hypothesis['type']}")
        print(f"   Mode: {'🔍 EXPLORATION' if hypothesis['is_exploration'] else '🎯 EXPLOITATION'}")
        print(f"   Novelty Score: {hypothesis['novelty_score']:.2f}")

        # Agent 1: Generate detailed hypothesis proposal
        session.state["data_context"] = json.dumps(data_context)
        session.state["hypothesis"] = json.dumps(hypothesis)

        ctx = InvocationContext(
            session=session,
            request=f"Generate a detailed hypothesis proposal for {data_domain} "
                    f"based on the current data context and exploration strategy."
        )

        async for event in hypothesis_generator.run(ctx):
            pass

        hypothesis_proposal = session.state.get("hypothesis_proposal", "{}")

        # Agent 2: Validate hypothesis
        # Simulate test results
        test_results = simulate_hypothesis_test(hypothesis, data_context)

        session.state["test_results"] = json.dumps(test_results)

        ctx = InvocationContext(
            session=session,
            request=f"Validate the hypothesis based on test results and assess "
                    f"validity, novelty, and significance."
        )

        async for event in hypothesis_validator.run(ctx):
            pass

        # Record test results
        hypothesis = hypothesis_space.test_hypothesis(hypothesis, test_results)

        print(f"\n✓ Hypothesis Tested")
        print(f"   Valid: {hypothesis['is_valid']}")
        print(f"   Novel: {hypothesis['is_novel']}")
        print(f"   Significance: {hypothesis['significance']:.2f}")

        if hypothesis['is_valid'] and hypothesis['is_novel']:
            print(f"   🎉 DISCOVERY MADE!")
            discoveries_log.append({
                "iteration": iteration + 1,
                "hypothesis": hypothesis,
                "test_results": test_results
            })

        # Update exploration metrics
        metrics = hypothesis_space.get_exploration_metrics()
        print(f"\n📊 Exploration Metrics:")
        print(f"   Success Rate: {metrics['success_rate']:.1%}")
        print(f"   Novelty Rate: {metrics['novelty_rate']:.1%}")
        print(f"   Discoveries: {metrics['novel_discoveries']}")

    # Agent 3: Synthesize discoveries
    session.state["all_discoveries"] = json.dumps([
        d["hypothesis"] for d in discoveries_log
    ])

    ctx = InvocationContext(
        session=session,
        request=f"Synthesize all discoveries from this exploration cycle. "
                f"Identify key patterns, breakthrough insights, and "
                f"recommendations for next steps."
    )

    async for event in discovery_synthesizer.run(ctx):
        pass

    synthesis = session.state.get("synthesis", "No synthesis available")

    return {
        "discoveries": hypothesis_space.discoveries,
        "metrics": hypothesis_space.get_exploration_metrics(),
        "tested_hypotheses": hypothesis_space.tested_hypotheses,
        "synthesis": synthesis,
        "discoveries_log": discoveries_log
    }


def generate_data_context(domain: str, iteration: int) -> Dict[str, Any]:
    """Generate simulated data context for exploration."""
    contexts = {
        "drug interactions": {
            "patient_records": 10000000 + (iteration * 100000),
            "drug_combinations": 5000 + (iteration * 50),
            "adverse_events": 1200 + (iteration * 30),
            "positive_outcomes": 8500 + (iteration * 100),
            "data_quality": 0.85 + (iteration * 0.02),
            "known_interactions": 150 + (iteration * 5)
        },
        "market patterns": {
            "transactions": 500000 + (iteration * 10000),
            "customer_segments": 50 + iteration,
            "product_categories": 100,
            "seasonal_factors": 12,
            "correlation_matrix_size": 1000,
            "known_patterns": 25 + iteration
        }
    }
    return contexts.get(domain, {})


def simulate_hypothesis_test(
    hypothesis: Dict[str, Any],
    data_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Simulate hypothesis testing (in real scenario, would perform actual analysis).
    """
    # Simulate varying success rates based on hypothesis type
    type_success_rates = {
        "correlation_discovery": 0.6,
        "interaction_effect": 0.4,
        "non_linear_relationship": 0.3,
        "conditional_dependency": 0.5,
        "anomaly_pattern": 0.35,
        "refinement": 0.7
    }

    base_rate = type_success_rates.get(hypothesis["type"], 0.5)

    # Exploration tends to find more novel but less valid results
    if hypothesis["is_exploration"]:
        valid_prob = base_rate * 0.7
        novel_prob = 0.8
    else:
        valid_prob = base_rate * 1.2
        novel_prob = 0.3

    is_valid = random.random() < valid_prob
    is_novel = random.random() < novel_prob
    significance = random.random() * 0.5 + 0.5 if (is_valid and is_novel) else random.random() * 0.5

    descriptions = [
        "Strong correlation found between variables with p-value < 0.001",
        "Interaction effect observed under specific conditions",
        "Non-linear relationship identified in subpopulation",
        "Conditional dependency discovered with high confidence",
        "Anomalous pattern detected in edge cases"
    ]

    impacts = [
        "Could reduce adverse events by 15-20%",
        "Potential for new treatment protocol",
        "May inform dosage optimization",
        "Suggests personalized medicine approach",
        "Enables early risk detection"
    ]

    return {
        "valid": is_valid,
        "novel": is_novel,
        "significance": significance,
        "description": random.choice(descriptions) if is_valid else "Hypothesis not supported by data",
        "impact": random.choice(impacts) if (is_valid and is_novel) else "Limited impact",
        "confidence_interval": (0.85, 0.95) if is_valid else (0.3, 0.6),
        "sample_size": data_context.get("patient_records", 1000000)
    }


async def main():
    """Main execution function demonstrating exploration and discovery."""

    print("=" * 80)
    print("Pattern 31: Exploration and Discovery")
    print("Hypothesis-Driven Discovery with AI Agents")
    print("=" * 80)

    # Run exploration cycle for drug interactions
    results = await run_exploration_cycle(
        data_domain="drug interactions",
        num_iterations=10,
        epsilon=0.3  # 30% exploration, 70% exploitation
    )

    print("\n\n" + "=" * 80)
    print("EXPLORATION RESULTS SUMMARY")
    print("=" * 80)

    metrics = results["metrics"]
    print(f"\n📊 Overall Performance:")
    print(f"   Total Hypotheses Tested: {metrics['total_hypotheses']}")
    print(f"   Valid Hypotheses: {metrics['valid_hypotheses']}")
    print(f"   Novel Discoveries: {metrics['novel_discoveries']}")
    print(f"   Success Rate: {metrics['success_rate']:.1%}")
    print(f"   Novelty Rate: {metrics['novelty_rate']:.1%}")
    print(f"   Exploration Efficiency: {metrics['exploration_efficiency']:.1%}")

    print(f"\n🎉 Breakthrough Discoveries:")
    for idx, discovery in enumerate(results["discoveries"], 1):
        print(f"\n   Discovery {idx}:")
        print(f"   - Type: {discovery['type']}")
        print(f"   - Significance: {discovery['significance']:.2f}")
        print(f"   - Impact: {discovery['potential_impact']}")
        if discovery.get('description'):
            print(f"   - Description: {discovery['description']}")

    print("\n" + "=" * 80)
    print("Pattern Demonstrated: Exploration and Discovery")
    print("=" * 80)
    print("""
    Key Observations:
    1. Hypothesis Generation: Creative generation beyond programmed boundaries
    2. Epsilon-Greedy Strategy: Balances exploration vs exploitation
    3. Rigorous Validation: Multiple criteria for discovery confirmation
    4. Novelty Assessment: Distinguishes new findings from known patterns
    5. Synthesis: Identifies overarching insights from individual discoveries

    Exploration Metrics:
    - Exploration Rate: 30% (epsilon parameter)
    - Validation Criteria: Validity, Novelty, Significance
    - Discovery Threshold: Significance > 0.8
    - Efficiency: Discoveries per hypothesis tested

    ADK Advantages:
    - Parallel hypothesis testing with ParallelAgent
    - State management for hypothesis tracking
    - Memory service for pattern recognition
    - Structured exploration strategies
    - Scalable to large hypothesis spaces

    Business Impact (from article):
    - 3 beneficial drug interactions identified
    - 7 dangerous interactions previously unknown
    - 2 patents filed
    - Estimated value: $500M over 5 years

    Applications:
    - Drug discovery and interaction analysis
    - Market opportunity identification
    - Process optimization in manufacturing
    - Risk pattern discovery in finance
    - Customer behavior insights
    """)


if __name__ == "__main__":
    # Set up Google Cloud credentials before running
    # export GOOGLE_CLOUD_PROJECT="your-project-id"
    # export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

    asyncio.run(main())
