"""
Pattern 8: Self-Correction
Automatic error detection and fixing through validation and retry mechanisms.

Business Example: Code generation with testing
- Generate code → Run tests → Detect errors → Fix issues → Retry until passing

This example demonstrates Google ADK's self-correction capabilities with validation loops.

Mermaid Diagram Reference: See diagrams/08_self_correction.mermaid
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from typing import Any, Dict
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools import exit_loop
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import json


# Code Generator
code_generator = LlmAgent(
    name="CodeGenerator",
    model="gemini-2.5-flash",
    instruction="""
    You are a Python code generator.
    
    Generate working Python code based on requirements.
    If you receive error feedback from state['test_results'], fix the code.
    
    Output ONLY the Python code (no markdown, no explanations).
    """,
    output_key="generated_code"
)


# Code Validator/Tester
code_validator = LlmAgent(
    name="CodeValidator",
    model="gemini-2.5-flash",
    instruction="""
    You are a code validation specialist.
    
    Analyze the code from state['generated_code']:
    1. Check syntax
    2. Identify logic errors
    3. Verify it meets requirements
    4. Check edge cases
    
    Output as JSON:
    {
        "is_valid": true/false,
        "errors": ["list of errors found"],
        "warnings": ["list of warnings"],
        "test_cases_passed": [...],
        "test_cases_failed": [...],
        "fix_suggestions": ["specific fixes needed"]
    }
    """,
    output_key="test_results"
)


# Self-Correction Decision Agent
correction_agent = LlmAgent(
    name="CorrectionDecider",
    model="gemini-2.5-flash",
    instruction="""
    You are a quality control agent.
    
    Review state['test_results'].
    - If is_valid is true, call exit_loop
    - If is_valid is false, continue iteration for fixes
    
    Output your decision.
    """,
    tools=[exit_loop],
    output_key="correction_decision"
)


# Create self-correction loop
self_correction_loop = LoopAgent(
    name="SelfCorrectionLoop",
    sub_agents=[code_generator, code_validator, correction_agent],
    max_iterations=5
)


async def generate_and_validate_code(requirements: str) -> Dict[str, Any]:
    """Generate code with self-correction."""
    session_service = InMemorySessionService()
    app_name = "agentic_patterns"
    user_id = "demo_user"
    session_id = "selfcorrection_001"

    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    runner = Runner(
        agent=self_correction_loop,
        app_name=app_name,
        session_service=session_service
    )

    content = types.Content(role='user', parts=[types.Part(text=requirements)])
    events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content)

    iterations = []
    iteration_count = 0

    async for event in events:
        if event.is_final_response():
            iteration_count += 1
            # Get current session state
            current_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
            iterations.append({
                "iteration": iteration_count,
                "code": current_session.state.get("generated_code"),
                "test_results": current_session.state.get("test_results"),
                "decision": current_session.state.get("correction_decision")
            })

    # Get final session state
    final_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)

    return {
        "total_iterations": iteration_count,
        "iterations": iterations,
        "final_code": final_session.state.get("generated_code"),
        "final_validation": final_session.state.get("test_results")
    }


async def main():
    """Demonstrate self-correction pattern."""
    print("=" * 80)
    print("Example 1: Generate Binary Search Function")
    print("=" * 80)
    
    requirements = """
    Create a Python function that implements binary search.
    
    Requirements:
    - Function name: binary_search
    - Parameters: sorted_list (list of integers), target (integer)
    - Returns: index of target if found, -1 if not found
    - Must handle empty lists
    - Must handle lists with one element
    - Must be efficient (O(log n))
    """
    
    print("Requirements:", requirements)
    result = await generate_and_validate_code(requirements)
    
    print(f"\nTotal Iterations: {result['total_iterations']}")
    
    for it in result['iterations']:
        print(f"\nIteration {it['iteration']}:")
        print("Code:", it['code'])
        print("Validation:", it['test_results'])
        print("Decision:", it['decision'])
        print("-" * 80)
    
    print("\nFinal Code:")
    print(result['final_code'])
    
    print("\n" + "=" * 80)
    print("Example 2: Data Processing Function")
    print("=" * 80)
    
    requirements2 = """
    Create a function to calculate average from a list of numbers.
    
    Requirements:
    - Function name: calculate_average
    - Parameter: numbers (list of floats)
    - Returns: average as float
    - Handle empty list (return 0)
    - Handle None values in list (skip them)
    - Round to 2 decimal places
    """
    
    result2 = await generate_and_validate_code(requirements2)
    print(f"Iterations needed: {result2['total_iterations']}")
    print("Final Code:", result2['final_code'])
    
    print("\n" + "=" * 80)
    print("Pattern: Self-Correction")
    print("=" * 80)
    print("""
    Key Observations:
    1. Error Detection: Automatic validation catches issues
    2. Iterative Fixing: Code improves with each iteration
    3. Validation Loop: Test-fix cycle until success
    4. Bounded Retries: max_iterations prevents infinite loops
    
    Benefits:
    - Higher quality outputs
    - Reduced manual debugging
    - Automatic error recovery
    - Test-driven generation
    
    Applications:
    - Code generation
    - Data transformation
    - Content creation with quality checks
    - API response validation
    """)


if __name__ == "__main__":
    asyncio.run(main())
