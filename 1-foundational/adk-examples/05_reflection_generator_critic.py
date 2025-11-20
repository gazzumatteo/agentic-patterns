"""
Pattern 4: Reflection
Generator-Critic pattern with iterative refinement through self-evaluation.

Business Example: Quality assurance system
- Generate content ' Evaluate quality ' Refine based on feedback ' Repeat until acceptable

This example demonstrates Google ADK's LoopAgent for implementing a reflection pattern
where a generator creates content and a critic evaluates it, driving iterative improvements.

Mermaid Diagram Reference: See diagrams/04_reflection.mermaid
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from typing import Any
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools import exit_loop
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types


# Generator Agent: Creates content based on requirements
generator_agent = LlmAgent(
    name="ContentGenerator",
    model="gemini-2.5-flash",
    instruction="""
    You are a creative content generator specializing in product descriptions.

    Your task:
    1. If this is the first iteration, create a new product description based on the requirements
    2. If you receive feedback from state['critic_feedback'], improve the description by addressing the issues
    3. Focus on being persuasive, clear, and highlighting key features
    4. Make sure the description is between 100-150 words

    Output ONLY the product description text (no metadata, no JSON).
    """,
    description="Generates product descriptions based on requirements and feedback",
    output_key="generated_content"
)

# Critic Agent: Evaluates content quality and provides feedback
critic_agent = LlmAgent(
    name="QualityCritic",
    model="gemini-2.5-flash",
    instruction="""
    You are a quality assurance specialist evaluating product descriptions.

    Review the content from state['generated_content'] and evaluate:
    1. Clarity: Is the message clear and easy to understand?
    2. Persuasiveness: Does it effectively sell the product?
    3. Completeness: Are all key features highlighted?
    4. Length: Is it within 100-150 words?
    5. Grammar: Are there any grammatical errors?

    Provide output as JSON:
    {
        "quality_score": <number 1-10>,
        "issues": ["list of specific issues found"],
        "strengths": ["list of what works well"],
        "feedback": "Detailed feedback for improvement",
        "approved": <true if score >= 8, false otherwise>
    }

    Be constructive but thorough in your critique.
    """,
    description="Evaluates content quality and provides improvement feedback",
    output_key="critic_feedback"
)

# Decision Agent: Decides whether to continue refining or exit the loop
decision_agent = LlmAgent(
    name="DecisionMaker",
    model="gemini-2.5-flash",
    instruction="""
    You are a decision maker in a quality assurance workflow.

    Review the critic's feedback from state['critic_feedback'].

    If the content is approved (approved: true), call the exit_loop function.
    If not approved, explain what needs improvement and continue iteration.

    Output your decision as plain text.
    """,
    description="Decides when quality is acceptable and exits the loop",
    tools=[exit_loop],
    output_key="decision"
)


# Create the reflection loop
reflection_loop = LoopAgent(
    name="ReflectionLoop",
    description="Iteratively generate and refine content through reflection",
    sub_agents=[
        generator_agent,
        critic_agent,
        decision_agent
    ],
    max_iterations=5  # Prevent infinite loops
)


async def run_reflection(product_requirements: str) -> dict[str, Any]:
    """
    Run the reflection pattern for content generation and refinement.

    Args:
        product_requirements: Description of product features and requirements

    Returns:
        Dictionary containing all iterations and final approved content
    """
    # Create session service
    session_service = InMemorySessionService()
    app_name = "agentic_patterns"
    user_id = "demo_user"
    session_id = "reflection_001"

    # Initialize session
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    # Track iterations
    iterations = []

    # Run the reflection loop
    runner = Runner(
        agent=reflection_loop,
        app_name=app_name,
        session_service=session_service
    )

    content = types.Content(role='user', parts=[types.Part(text=product_requirements)])
    events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content)

    iteration_count = 0
    async for event in events:
        if event.is_final_response():
            # Track each iteration's results
            iteration_count += 1
            # Get current session state
            current_session = await session_service.get_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            current_iteration = {
                "iteration": iteration_count,
                "generated_content": current_session.state.get("generated_content"),
                "critic_feedback": current_session.state.get("critic_feedback"),
                "decision": current_session.state.get("decision")
            }
            iterations.append(current_iteration)

    # Get final session state
    final_session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    # Return complete history
    return {
        "total_iterations": iteration_count,
        "iterations": iterations,
        "final_content": final_session.state.get("generated_content"),
        "final_feedback": final_session.state.get("critic_feedback")
    }


async def main():
    """Main execution function demonstrating reflection pattern."""

    # Example 1: Product description that needs refinement
    print("=" * 80)
    print("Example 1: E-commerce Product Description - Wireless Headphones")
    print("=" * 80)

    product_requirements = """
    Product: Premium Wireless Noise-Cancelling Headphones

    Key Features:
    - Active noise cancellation (ANC)
    - 30-hour battery life
    - Premium leather cushions
    - Bluetooth 5.3
    - Quick charge (10 min = 5 hours)
    - Foldable design
    - Multiple color options

    Target Audience: Professionals and commuters
    Price Point: Premium ($299)
    Tone: Professional, emphasize quality and value
    """

    print("\nRequirements:")
    print(product_requirements)

    result = await run_reflection(product_requirements)

    print(f"\nTotal Iterations: {result['total_iterations']}")
    print("\n" + "=" * 80)

    # Show each iteration
    for iteration in result['iterations']:
        print(f"\nIteration {iteration['iteration']}:")
        print(f"\nGenerated Content:")
        print(iteration['generated_content'])
        print(f"\nCritic Feedback:")
        print(iteration['critic_feedback'])
        print(f"\nDecision:")
        print(iteration['decision'])
        print("\n" + "-" * 80)

    print(f"\nFinal Approved Content:")
    print(result['final_content'])

    # Example 2: Technical documentation
    print("\n\n" + "=" * 80)
    print("Example 2: API Documentation - Authentication Endpoint")
    print("=" * 80)

    api_requirements = """
    API Endpoint: POST /auth/login

    Purpose: Authenticate users and return JWT token

    Parameters:
    - email (string, required): User's email address
    - password (string, required): User's password
    - remember_me (boolean, optional): Keep user logged in

    Response: JWT token, user profile, expiration time

    Target Audience: Developer documentation
    Tone: Technical, clear, concise
    Length: 120-150 words
    """

    print("\nRequirements:")
    print(api_requirements)

    result = await run_reflection(api_requirements)

    print(f"\nTotal Iterations: {result['total_iterations']}")
    print(f"\nFinal Approved Documentation:")
    print(result['final_content'])

    print("\n" + "=" * 80)
    print("Pattern Demonstrated: Reflection (Generator-Critic)")
    print("=" * 80)
    print("""
    Key Observations:
    1. Iterative Refinement: Content improves through multiple cycles
    2. Self-Evaluation: Critic agent provides objective quality assessment
    3. Adaptive Generation: Generator responds to specific feedback
    4. Quality Threshold: Loop exits when quality score meets criteria
    5. Loop Control: max_iterations prevents infinite refinement

    Performance Metrics:
    - Iterations: Typically 2-4 cycles for good results
    - Quality Improvement: Each iteration addresses specific issues
    - Convergence: Quality score increases monotonically
    - Cost Trade-off: More iterations = higher token cost but better quality

    Best Practices:
    1. Set clear quality criteria (score thresholds)
    2. Provide specific, actionable feedback from critic
    3. Limit max iterations to control costs
    4. Track iteration history for analysis
    5. Use different models for generator vs critic (optional optimization)

    Business Applications:
    - Content creation with QA review
    - Code generation with static analysis
    - Report writing with compliance checking
    - Marketing copy with brand guidelines validation
    - Customer response refinement

    ADK Advantages:
    - LoopAgent provides native iteration support
    - exit_loop tool gives precise control over termination
    - State persistence across iterations
    - Clean separation of generator/critic concerns
    """)


if __name__ == "__main__":
    # Set up Google Cloud credentials before running
    # export GOOGLE_CLOUD_PROJECT="your-project-id"
    # export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

    asyncio.run(main())
