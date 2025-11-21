"""
Pattern 1: Prompt Chaining
Sequential task decomposition where each step's output becomes the next step's input.

Business Example: Customer onboarding flow
- Extract user information -> Validate data -> Personalize welcome -> Send confirmation

This example demonstrates Google ADK's SequentialAgent for orchestrating a
customer onboarding pipeline where each agent's output feeds into the next.

Mermaid Diagram Reference: See diagrams/01_prompt_chaining.mermaid
"""

import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Load environment variables
load_dotenv()


# ========================================
# STEP 1: Extract user information
# ========================================
extract_agent = LlmAgent(
    name="InformationExtractor",
    model="gemini-2.5-flash",
    instruction="""
    You are a data extraction specialist. Extract user information from the input text.

    Extract and structure the following fields:
    - full_name: The person's full name
    - email: Email address
    - company: Company name
    - role: Job role/title
    - country: Country location

    Output ONLY a JSON object with these fields. If any field is missing, use null.
    """,
    description="Extracts structured user information from raw input",
    output_key="extracted_data"
)


# ========================================
# STEP 2: Validate the extracted data
# ========================================
validate_agent = LlmAgent(
    name="DataValidator",
    model="gemini-2.5-flash",
    instruction="""
    You are a data validation expert. Validate the extracted data from state['extracted_data'].

    Check:
    - Email format is valid
    - All required fields (full_name, email) are present
    - Company and role are provided (warn if missing but don't fail)

    Output a JSON with:
    {{
        "is_valid": true/false,
        "errors": ["list of errors if any"],
        "warnings": ["list of warnings if any"]
    }}
    """,
    description="Validates extracted user data for completeness and format",
    output_key="validation_result"
)


# ========================================
# STEP 3: Personalize welcome message
# ========================================
personalize_agent = LlmAgent(
    name="WelcomePersonalizer",
    model="gemini-2.5-flash",
    instruction="""
    Create a personalized welcome message based on the validated data.

    Use data from:
    - state['extracted_data'] - User information
    - state['validation_result'] - Validation status

    If validation has errors, create a friendly message asking for missing information.
    If validation is successful, create an enthusiastic welcome message that mentions
    their company and role.

    Output ONLY the welcome message text.
    """,
    description="Generates personalized welcome message",
    output_key="welcome_message"
)


# ========================================
# STEP 4: Generate confirmation
# ========================================
confirmation_agent = LlmAgent(
    name="ConfirmationGenerator",
    model="gemini-2.5-flash",
    instruction="""
    Generate a final onboarding confirmation summary.

    Review the complete onboarding flow:
    - Extracted data: {extracted_data}
    - Validation: {validation_result}
    - Welcome message: {welcome_message}

    Create a brief confirmation that summarizes:
    1. What information was collected
    2. Next steps for the user
    3. How to get help

    Output ONLY the confirmation text.
    """,
    description="Generates final onboarding confirmation",
    output_key="final_confirmation"
)


# ========================================
# PIPELINE: Chain all steps together
# ========================================
onboarding_pipeline = SequentialAgent(
    name="CustomerOnboardingPipeline",
    sub_agents=[
        extract_agent,
        validate_agent,
        personalize_agent,
        confirmation_agent
    ],
    description="Complete customer onboarding pipeline with prompt chaining"
)


async def run_onboarding(user_input: str):
    """
    Run the customer onboarding pipeline.

    Args:
        user_input: Raw user information text
    """
    # Create InMemoryRunner - it handles everything automatically
    runner = InMemoryRunner(agent=onboarding_pipeline, app_name="onboarding_app")

    # Create session (await it!)
    session = await runner.session_service.create_session(
        app_name="onboarding_app",
        user_id="demo_user"
    )

    # Prepare user message
    content = types.Content(role='user', parts=[types.Part(text=user_input)])

    # Run the pipeline
    events = runner.run_async(
        user_id="demo_user",
        session_id=session.id,
        new_message=content
    )

    print(f"\n{'='*80}")
    print("Processing through pipeline...")
    print(f"{'='*80}\n")

    # Process events
    async for event in events:
        if event.is_final_response() and event.content:
            final_response = event.content.parts[0].text
            print(f"Final Response:\n{final_response}\n")

    # Get updated session to show intermediate results
    updated_session = await runner.session_service.get_session(
        app_name="onboarding_app",
        user_id="demo_user",
        session_id=session.id
    )

    print(f"{'='*80}")
    print("Pipeline Results (Intermediate Outputs):")
    print(f"{'='*80}\n")
    print(f"1. Extracted Data:\n{updated_session.state.get('extracted_data')}\n")
    print(f"2. Validation Result:\n{updated_session.state.get('validation_result')}\n")
    print(f"3. Welcome Message:\n{updated_session.state.get('welcome_message')}\n")
    print(f"4. Final Confirmation:\n{updated_session.state.get('final_confirmation')}\n")


async def main():
    """Main execution function demonstrating prompt chaining."""

    print(f"\n{'='*80}")
    print("Pattern 1: Prompt Chaining with Google ADK")
    print(f"{'='*80}\n")

    # Example 1: Complete user information
    print("\nExample 1: Complete User Information")
    print("-" * 80)

    complete_input = """
    Hi, I'm Sarah Johnson from TechCorp. I'm the Senior Product Manager there.
    You can reach me at sarah.johnson@techcorp.com. I'm based in the United States.
    """

    await run_onboarding(complete_input)

    # Example 2: Incomplete user information
    print(f"\n\n{'='*80}")
    print("Example 2: Incomplete User Information")
    print(f"{'='*80}\n")

    incomplete_input = """
    Hey, I'm John. I work at some company but I forgot to mention which one.
    """

    await run_onboarding(incomplete_input)

    print(f"\n{'='*80}")
    print("Pattern Demonstrated: Prompt Chaining")
    print(f"{'='*80}")
    print("""
Key Concepts:
1. SequentialAgent runs sub-agents in order
2. Each agent uses output_key to save results to session state
3. Next agents access previous results via {state_key} in instructions
4. InMemoryRunner simplifies session and state management
5. All intermediate results are preserved in session.state
    """)


if __name__ == "__main__":
    asyncio.run(main())
