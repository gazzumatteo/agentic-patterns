"""
Pattern 9: Evals (Evaluations)
Performance measurement and benchmarking to assess agent quality and capabilities.

Business Example: Model comparison and benchmarking
- Run test suite → Measure accuracy → Compare models → Optimize performance

This example demonstrates Google ADK's evaluation framework for systematic testing.

Mermaid Diagram Reference: See diagrams/09_evals.mermaid
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from typing import Any, Dict, List
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import json
import time
from datetime import datetime


# Test Agent - Different configurations to evaluate
def create_test_agent(model: str, temperature: float = 0.7) -> LlmAgent:
    """Create an agent with specific configuration for testing."""
    # Create valid identifier name (replace invalid characters)
    safe_name = model.replace('.', '_').replace('-', '_')
    return LlmAgent(
        name=f"TestAgent_{safe_name}",
        model=model,
        instruction="""
        You are a helpful assistant that provides accurate, concise answers.
        Focus on correctness and clarity.
        """,
    )


# Evaluation Test Cases
TEST_CASES = [
    {
        "id": "math_basic",
        "question": "What is 15% of 240?",
        "expected": "36",
        "category": "mathematics"
    },
    {
        "id": "reasoning_logic",
        "question": "If all roses are flowers and some flowers fade quickly, can we conclude that some roses fade quickly?",
        "expected": "No, this is invalid logic",
        "category": "logical_reasoning"
    },
    {
        "id": "knowledge_geography",
        "question": "What is the capital of Australia?",
        "expected": "Canberra",
        "category": "knowledge"
    },
    {
        "id": "summarization",
        "question": "Summarize in one sentence: The Industrial Revolution transformed economies from agrarian to industrial, introduced mass production, and led to urbanization.",
        "expected": "industrial transformation",
        "category": "summarization"
    },
    {
        "id": "classification",
        "question": "Classify this sentiment: \"I absolutely loved this product! Best purchase ever!\"",
        "expected": "positive",
        "category": "classification"
    }
]


async def run_evaluation(agent: LlmAgent, test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single test case and evaluate the result."""
    session_service = InMemorySessionService()
    app_name = "agentic_patterns"
    user_id = "demo_user"
    session_id = f"eval_{test_case['id']}"

    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    # Measure execution time
    start_time = time.time()

    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service
    )

    content = types.Content(role='user', parts=[types.Part(text=test_case['question'])])
    events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content)

    response_parts = []
    async for event in events:
        if event.is_final_response():
            # Get the response text from final event
            if hasattr(event, 'text'):
                response_parts.append(event.text)

    execution_time = time.time() - start_time
    response = ''.join(response_parts)
    
    # Simple correctness check (contains expected answer)
    is_correct = test_case['expected'].lower() in response.lower()
    
    return {
        "test_id": test_case['id'],
        "category": test_case['category'],
        "question": test_case['question'],
        "expected": test_case['expected'],
        "actual": response,
        "correct": is_correct,
        "execution_time": execution_time
    }


async def evaluate_agent(agent: LlmAgent, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run full evaluation suite on an agent."""
    results = []
    
    for test_case in test_cases:
        result = await run_evaluation(agent, test_case)
        results.append(result)
    
    # Calculate metrics
    total_tests = len(results)
    correct_tests = sum(1 for r in results if r['correct'])
    accuracy = correct_tests / total_tests if total_tests > 0 else 0
    avg_time = sum(r['execution_time'] for r in results) / total_tests if total_tests > 0 else 0
    
    # Category breakdown
    category_stats = {}
    for result in results:
        cat = result['category']
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "correct": 0}
        category_stats[cat]["total"] += 1
        if result['correct']:
            category_stats[cat]["correct"] += 1
    
    for cat, stats in category_stats.items():
        stats['accuracy'] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
    
    return {
        "agent_name": agent.name,
        "model": agent.model,
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "correct": correct_tests,
        "accuracy": accuracy,
        "average_execution_time": avg_time,
        "category_breakdown": category_stats,
        "detailed_results": results
    }


async def compare_models(models: List[str]) -> Dict[str, Any]:
    """Compare multiple models using the same test suite."""
    comparison_results = []
    
    for model in models:
        print(f"\nEvaluating {model}...")
        agent = create_test_agent(model)
        results = await evaluate_agent(agent, TEST_CASES)
        comparison_results.append(results)
    
    return {
        "comparison_date": datetime.now().isoformat(),
        "models_tested": models,
        "results": comparison_results
    }


async def main():
    """Demonstrate evaluation pattern."""
    print("=" * 80)
    print("Pattern 9: Evals - Model Performance Benchmarking")
    print("=" * 80)
    
    # Example 1: Single Agent Evaluation
    print("\nExample 1: Evaluate Single Agent")
    print("-" * 80)
    
    agent = create_test_agent("gemini-2.5-flash")
    eval_results = await evaluate_agent(agent, TEST_CASES)
    
    print(f"\nAgent: {eval_results['agent_name']}")
    print(f"Model: {eval_results['model']}")
    print(f"Accuracy: {eval_results['accuracy']:.1%}")
    print(f"Avg Execution Time: {eval_results['average_execution_time']:.3f}s")
    
    print("\nCategory Breakdown:")
    for cat, stats in eval_results['category_breakdown'].items():
        print(f"  {cat}: {stats['accuracy']:.1%} ({stats['correct']}/{stats['total']})")
    
    print("\nDetailed Results:")
    for result in eval_results['detailed_results']:
        status = "✓" if result['correct'] else "✗"
        print(f"  {status} {result['test_id']}: {result['execution_time']:.3f}s")
    
    # Example 2: Model Comparison
    print("\n\n" + "=" * 80)
    print("Example 2: Compare Multiple Models")
    print("=" * 80)
    
    # Note: In practice, you'd compare different actual models
    # Here we simulate with same model for demonstration
    models_to_compare = ["gemini-2.5-flash"]  # Add more models as needed
    
    comparison = await compare_models(models_to_compare)
    
    print("\nModel Comparison Summary:")
    print("-" * 80)
    print(f"{'Model':<25} {'Accuracy':<12} {'Avg Time':<12}")
    print("-" * 80)
    
    for result in comparison['results']:
        print(f"{result['model']:<25} {result['accuracy']:<12.1%} {result['average_execution_time']:<12.3f}s")
    
    print("\n" + "=" * 80)
    print("Pattern: Evals - Systematic Performance Measurement")
    print("=" * 80)
    print("""
    Key Observations:
    1. Systematic Testing: Standardized test suite ensures consistency
    2. Multi-Metric Evaluation: Accuracy, speed, category performance
    3. Comparative Analysis: Side-by-side model comparison
    4. Reproducibility: Same tests, objective measurements
    5. Category Breakdown: Identify strengths and weaknesses
    
    Evaluation Metrics:
    - Accuracy: Correctness of responses
    - Execution Time: Performance/latency
    - Category Performance: Domain-specific accuracy
    - Token Usage: Cost analysis (can be added)
    - Error Rate: Failure patterns
    
    Best Practices:
    1. Diverse Test Cases: Cover different task types
    2. Ground Truth: Clear expected outcomes
    3. Automated Scoring: Objective evaluation criteria
    4. Regular Benchmarking: Track improvements over time
    5. A/B Testing: Compare configurations systematically
    
    Business Applications:
    - Model selection for production
    - Performance regression testing
    - Quality assurance automation
    - Cost-performance optimization
    - SLA compliance monitoring
    
    ADK Advantages:
    - Native async support for parallel testing
    - Session management for isolated tests
    - Flexible agent configuration
    - Built-in performance tracking
    """)


if __name__ == "__main__":
    asyncio.run(main())
