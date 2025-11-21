"""
Pattern 1: Prompt Chaining
Sequential task decomposition where each step's output becomes the next step's input.

Business Example: Customer onboarding flow
- Extract user information -> Validate data -> Personalize welcome -> Send confirmation

This example demonstrates CrewAI's sequential process for orchestrating a
customer onboarding pipeline with role-based agent collaboration.

Mermaid Diagram Reference: See diagrams/01_prompt_chaining.mermaid
"""

from crewai import Agent, Task, Crew, Process
from typing import Dict, Any


def create_onboarding_crew() -> Crew:
    """
    Creates a CrewAI crew for customer onboarding with prompt chaining.

    Returns:
        Configured Crew with sequential task execution
    """

    # Agent 1: Information Extractor
    extractor = Agent(
        role="Data Extraction Specialist",
        goal="Extract structured user information from raw text input",
        backstory="""You are an expert at parsing unstructured text and extracting
        key information. You have years of experience in data processing and can
        identify relevant details even from conversational input.""",
        verbose=True,
        allow_delegation=False
    )

    # Agent 2: Data Validator
    validator = Agent(
        role="Data Validation Expert",
        goal="Ensure all extracted data is complete, accurate, and properly formatted",
        backstory="""You are a meticulous data quality specialist who ensures
        data integrity. You check for completeness, format validity, and flag
        any potential issues before data enters the system.""",
        verbose=True,
        allow_delegation=False
    )

    # Agent 3: Welcome Message Personalizer
    personalizer = Agent(
        role="Customer Success Specialist",
        goal="Create warm, personalized welcome messages that make users feel valued",
        backstory="""You are a friendly and empathetic customer success expert.
        You excel at crafting personalized communications that make customers
        feel welcomed and understood.""",
        verbose=True,
        allow_delegation=False
    )

    # Agent 4: Confirmation Generator
    confirmer = Agent(
        role="Onboarding Confirmation Specialist",
        goal="Generate comprehensive onboarding confirmations with clear next steps",
        backstory="""You are an expert at summarizing onboarding processes and
        providing clear, actionable next steps to new users. You ensure nothing
        is left ambiguous.""",
        verbose=True,
        allow_delegation=False
    )

    # Task 1: Extract Information
    extract_task = Task(
        description="""
        Extract user information from the following input: {user_input}

        Identify and extract:
        - Full name
        - Email address
        - Company name
        - Job role/title
        - Country location

        Provide the extracted information in a structured JSON format.
        If any field is missing, indicate it as null.
        """,
        expected_output="""JSON object containing: full_name, email, company, role, country.
        Example: {{"full_name": "Sarah Johnson", "email": "sarah@techcorp.com", ...}}""",
        agent=extractor
    )

    # Task 2: Validate Data
    validate_task = Task(
        description="""
        Validate the extracted user data from the previous step.

        Check:
        1. Email address is in valid format (contains @ and domain)
        2. Required fields (full_name, email) are present
        3. Optional fields (company, role, country) are noted if missing

        Provide validation results with:
        - is_valid: boolean
        - errors: list of critical errors (if any)
        - warnings: list of warnings for missing optional fields
        """,
        expected_output="""JSON object with validation results:
        {{"is_valid": true/false, "errors": [], "warnings": []}}""",
        agent=validator,
        context=[extract_task]  # Depends on extraction task output
    )

    # Task 3: Personalize Welcome
    personalize_task = Task(
        description="""
        Create a personalized welcome message based on the validated user data.

        If validation passed:
        - Create an enthusiastic, warm welcome
        - Use the user's name personally
        - Acknowledge their company and role (if available)
        - Make them feel valued as a new member

        If validation failed:
        - Create a friendly message
        - Politely ask for corrections to specific fields
        - Maintain a helpful, non-critical tone

        The message should be professional yet warm.
        """,
        expected_output="""A personalized welcome message (plain text, 3-5 sentences).
        Should feel authentic and tailored to the specific user.""",
        agent=personalizer,
        context=[extract_task, validate_task]  # Needs both previous outputs
    )

    # Task 4: Generate Confirmation
    confirmation_task = Task(
        description="""
        Generate a comprehensive onboarding confirmation summary.

        Include:
        1. Summary of captured user information
        2. Validation status (passed/failed with details)
        3. The personalized welcome message
        4. Clear next steps (e.g., "Check your email for login credentials",
           "Complete your profile in the dashboard", etc.)

        Format as a clear, professional summary that the user can refer back to.
        """,
        expected_output="""A structured confirmation document containing all
        onboarding details, validation status, welcome message, and next steps.
        Should be clear, complete, and actionable.""",
        agent=confirmer,
        context=[extract_task, validate_task, personalize_task]
    )

    # Create the crew with sequential process
    crew = Crew(
        agents=[extractor, validator, personalizer, confirmer],
        tasks=[extract_task, validate_task, personalize_task, confirmation_task],
        process=Process.sequential,  # Sequential execution for chaining
        verbose=True
    )

    return crew


def run_onboarding(user_input: str) -> Dict[str, Any]:
    """
    Run the customer onboarding pipeline with prompt chaining.

    Args:
        user_input: Raw user information text

    Returns:
        Dictionary containing the final result
    """
    crew = create_onboarding_crew()

    # Execute the crew with the user input
    result = crew.kickoff(inputs={"user_input": user_input})

    return {
        "status": "completed",
        "result": result
    }


def main():
    """Main execution function demonstrating prompt chaining."""

    # Example 1: Complete user information
    print("=" * 80)
    print("Example 1: Complete User Information")
    print("=" * 80)

    complete_input = """
    Hi, I'm Sarah Johnson from TechCorp. I'm the Senior Product Manager there.
    You can reach me at sarah.johnson@techcorp.com. I'm based in the United States.
    """

    result = run_onboarding(complete_input)
    print(f"\n Onboarding Result:\n{result['result']}")

    # Example 2: Incomplete user information
    print("\n\n" + "=" * 80)
    print("Example 2: Incomplete User Information")
    print("=" * 80)

    incomplete_input = """
    Hello, I'm John. My email is john@example
    """

    result = run_onboarding(incomplete_input)
    print(f"\n�  Onboarding Result:\n{result['result']}")

    print("\n" + "=" * 80)
    print("Pattern Demonstrated: Prompt Chaining with CrewAI")
    print("=" * 80)
    print("""
    Key Observations:
    1. Sequential Process: Tasks execute in defined order via Process.sequential
    2. Context Passing: Later tasks access earlier outputs via 'context' parameter
    3. Role-Based Agents: Each agent has specific expertise and backstory
    4. Task Dependencies: Context parameter explicitly defines task relationships
    5. Natural Handoffs: Information flows naturally from specialist to specialist

    Performance Metrics:
    - Execution: Sequential (each task waits for previous)
    - Latency: Cumulative across all tasks
    - Best For: Workflows requiring expert role specialization

    CrewAI Advantages:
    - Intuitive role-based design
    - Clear task context relationships
    - Built-in sequential orchestration
    - Easy to understand agent responsibilities
    """)


if __name__ == "__main__":
    # Set up API keys before running:
    # export OPENAI_API_KEY="your-openai-key"
    # or
    # export ANTHROPIC_API_KEY="your-anthropic-key"

    main()
