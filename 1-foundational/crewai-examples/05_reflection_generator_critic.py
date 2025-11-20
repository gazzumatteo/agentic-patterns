"""
Pattern 4: Reflection
Generator-Critic pattern with iterative refinement through self-evaluation.

Business Example: Quality assurance system
- Generate content ' Evaluate quality ' Refine based on feedback ' Repeat until acceptable

This example demonstrates CrewAI's feedback-driven workflow for implementing a reflection
pattern where generators create content and critics evaluate it through multiple iterations.

Mermaid Diagram Reference: See diagrams/04_reflection.mermaid
"""

from crewai import Agent, Task, Crew, Process
from typing import Dict, Any
import json


def create_reflection_crew() -> Crew:
    """
    Creates a CrewAI crew for reflection-based content generation.

    Returns:
        Configured Crew with generator-critic workflow
    """

    # Agent 1: Content Generator
    generator = Agent(
        role="Content Creator",
        goal="Generate high-quality product descriptions that are persuasive and clear",
        backstory="""You are a skilled marketing copywriter with years of experience
        creating compelling product descriptions. You know how to highlight features
        and benefits in a way that resonates with customers. You're also great at
        taking feedback and improving your work iteratively.""",
        verbose=True,
        allow_delegation=False
    )

    # Agent 2: Quality Critic
    critic = Agent(
        role="Quality Assurance Specialist",
        goal="Evaluate content quality and provide constructive, actionable feedback",
        backstory="""You are a meticulous quality assurance expert who has reviewed
        thousands of product descriptions. You have a keen eye for clarity, persuasiveness,
        completeness, and grammar. Your feedback is always specific and actionable,
        helping writers improve their craft.""",
        verbose=True,
        allow_delegation=False
    )

    # Agent 3: Refinement Coordinator
    refiner = Agent(
        role="Refinement Coordinator",
        goal="Coordinate the iterative improvement process and finalize content",
        backstory="""You are an experienced content manager who oversees the quality
        assurance process. You ensure that feedback is addressed and content meets
        all requirements before approval. You know when content is ready for publication.""",
        verbose=True,
        allow_delegation=False
    )

    return Crew(
        agents=[generator, critic, refiner],
        tasks=[],  # Tasks will be added dynamically
        process=Process.sequential,
        verbose=True
    )


def run_reflection(product_requirements: str, max_iterations: int = 3) -> Dict[str, Any]:
    """
    Run the reflection pattern for content generation and refinement.

    Args:
        product_requirements: Description of product features and requirements
        max_iterations: Maximum number of refinement iterations

    Returns:
        Dictionary containing iteration history and final approved content
    """
    crew = create_reflection_crew()
    generator, critic, refiner = crew.agents

    iterations = []
    current_content = None
    current_feedback = None

    for iteration in range(max_iterations):
        print(f"\n{'=' * 80}")
        print(f"ITERATION {iteration + 1}")
        print(f"{'=' * 80}\n")

        # Task 1: Generate or refine content
        if iteration == 0:
            generate_description = f"""
            Create a compelling product description based on these requirements:

            {product_requirements}

            Your description should:
            - Be between 100-150 words
            - Highlight key features and benefits
            - Be persuasive and clear
            - Target the specified audience
            - Match the requested tone

            Output ONLY the product description text.
            """
        else:
            generate_description = f"""
            Improve the following product description based on the critic's feedback:

            CURRENT DESCRIPTION:
            {current_content}

            CRITIC'S FEEDBACK:
            {current_feedback}

            REQUIREMENTS:
            {product_requirements}

            Address all issues mentioned in the feedback while maintaining the description's
            persuasive quality. Output ONLY the improved product description text.
            """

        generation_task = Task(
            description=generate_description,
            expected_output="A product description between 100-150 words that addresses all requirements and feedback.",
            agent=generator
        )

        # Execute generation
        crew.tasks = [generation_task]
        current_content = crew.kickoff()

        # Task 2: Critique the content
        critique_task = Task(
            description=f"""
            Evaluate this product description:

            {current_content}

            REQUIREMENTS:
            {product_requirements}

            Evaluate based on:
            1. Clarity: Is the message clear and easy to understand?
            2. Persuasiveness: Does it effectively sell the product?
            3. Completeness: Are all key features highlighted?
            4. Length: Is it within 100-150 words?
            5. Grammar: Are there any grammatical errors?

            Provide your evaluation as JSON:
            {{
                "quality_score": <number 1-10>,
                "issues": ["list of specific issues found"],
                "strengths": ["list of what works well"],
                "feedback": "Detailed feedback for improvement",
                "approved": <true if score >= 8, false otherwise>
            }}
            """,
            expected_output="JSON evaluation with quality score, issues, strengths, feedback, and approval status.",
            agent=critic
        )

        # Execute critique
        crew.tasks = [critique_task]
        critique_result = crew.kickoff()
        current_feedback = critique_result

        # Try to parse the critique as JSON
        try:
            # Extract JSON from the response
            critique_json = json.loads(str(critique_result))
            quality_score = critique_json.get("quality_score", 0)
            approved = critique_json.get("approved", False)
        except (json.JSONDecodeError, ValueError):
            # If parsing fails, assume it needs more work
            quality_score = 6
            approved = False

        # Record iteration
        iterations.append({
            "iteration": iteration + 1,
            "content": str(current_content),
            "feedback": str(current_feedback),
            "quality_score": quality_score,
            "approved": approved
        })

        # Check if approved
        if approved:
            print(f"\nContent approved with quality score: {quality_score}/10")
            break

    # Task 3: Final refinement and approval
    finalize_task = Task(
        description=f"""
        Review the final content and provide the approved version:

        FINAL CONTENT:
        {current_content}

        FINAL FEEDBACK:
        {current_feedback}

        If the content is approved, output it as-is.
        If minor improvements are needed, make them and output the polished version.
        Output ONLY the final approved product description.
        """,
        expected_output="The final, approved product description ready for publication.",
        agent=refiner
    )

    crew.tasks = [finalize_task]
    final_content = crew.kickoff()

    return {
        "total_iterations": len(iterations),
        "iterations": iterations,
        "final_content": str(final_content),
        "final_quality_score": iterations[-1]["quality_score"] if iterations else 0
    }


def main():
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

    result = run_reflection(product_requirements, max_iterations=3)

    print(f"\n\nTotal Iterations: {result['total_iterations']}")
    print(f"\nFinal Approved Content:")
    print(result['final_content'])
    print(f"\nFinal Quality Score: {result['final_quality_score']}/10")

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

    result = run_reflection(api_requirements, max_iterations=3)

    print(f"\n\nTotal Iterations: {result['total_iterations']}")
    print(f"\nFinal Approved Documentation:")
    print(result['final_content'])
    print(f"\nFinal Quality Score: {result['final_quality_score']}/10")

    print("\n" + "=" * 80)
    print("Pattern Demonstrated: Reflection (Generator-Critic) with CrewAI")
    print("=" * 80)
    print("""
    Key Observations:
    1. Iterative Refinement: Content improves through feedback cycles
    2. Role-Based Critique: Specialized QA agent provides expert evaluation
    3. Dynamic Task Creation: Tasks are created and executed iteratively
    4. Quality Tracking: Scores and feedback logged for each iteration
    5. Flexible Termination: Loop exits when quality threshold is met

    Performance Metrics:
    - Iterations: Typically 2-3 cycles for approval
    - Quality Improvement: Measurable score increases per iteration
    - Expert Feedback: Domain-specific critique from specialized agents
    - Cost Efficiency: Iteration limit prevents runaway costs

    Best Practices:
    1. Define clear quality criteria (score thresholds)
    2. Provide specific, actionable feedback
    3. Set maximum iteration limits
    4. Track quality metrics across iterations
    5. Use specialized agents for generation vs critique

    Business Applications:
    - E-commerce product descriptions
    - Marketing copy refinement
    - Technical documentation review
    - Customer communication templates
    - Brand compliance checking

    CrewAI Advantages:
    - Role-based agent design for natural generator/critic split
    - Dynamic task creation allows flexible iteration
    - Sequential process ensures proper ordering
    - Agent backstories create expert personas
    - Easy integration with existing workflows
    """)


if __name__ == "__main__":
    # Set up API keys before running:
    # export OPENAI_API_KEY="your-openai-key"
    # or
    # export ANTHROPIC_API_KEY="your-anthropic-key"

    main()
