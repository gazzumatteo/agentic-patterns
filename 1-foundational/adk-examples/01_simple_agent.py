"""
Pattern 1: Simple Agent (Single-agent)
The atomic unit of agent systems. One agent, one task, zero complexity.

Business Example: Automated Documentation Generator
- Company: TechCorp (SaaS, 500 employees)
- Challenge: Engineers spending 4 hours/week updating API documentation
- Solution: Single agent monitoring code commits, auto-generating OpenAPI specs
- Results: 92% reduction in documentation lag, $180K annual savings

This example demonstrates the simplest form of an AI agent - perfect for
deterministic workflows where reliability trumps sophistication.

Mermaid Diagram Reference: See diagrams/01_simple_agent.mermaid
"""

import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Load environment variables
load_dotenv()


# ========================================
# SIMPLE AGENT DEFINITION
# ========================================

documentation_agent = LlmAgent(
    name="DocumentationGenerator",
    model="gemini-2.5-flash",
    instruction="""
    You are an expert technical documentation generator.

    Given code or API information, generate clear, professional documentation
    following these guidelines:
    - Use proper markdown formatting
    - Include code examples where appropriate
    - Document all parameters and return values
    - Add usage examples
    - Be concise but complete

    Output ONLY the documentation in markdown format.
    """,
    description="Generates technical documentation from code"
)


# ========================================
# USAGE EXAMPLES
# ========================================

async def generate_docs(code_or_api_info: str):
    """Generate documentation using the simple agent."""

    # Create runner
    runner = InMemoryRunner(
        agent=documentation_agent,
        app_name="doc_generator"
    )

    # Create session
    session = await runner.session_service.create_session(
        app_name="doc_generator",
        user_id="developer"
    )

    # Prepare message
    content = types.Content(
        role='user',
        parts=[types.Part(text=code_or_api_info)]
    )

    # Run agent
    events = runner.run_async(
        user_id="developer",
        session_id=session.id,
        new_message=content
    )

    # Collect response
    async for event in events:
        if event.is_final_response() and event.content:
            documentation = event.content.parts[0].text
            return documentation

    return None


async def main():
    """Main execution demonstrating the simple agent pattern."""

    print(f"\n{'='*80}")
    print("Pattern 1: Simple Agent (Single-agent)")
    print(f"{'='*80}\n")

    # Example 1: Document a Python function
    print("Example 1: Documenting a Python Function")
    print("-" * 80)

    python_function = """
    def calculate_total_price(items: list[dict], tax_rate: float = 0.08) -> float:
        subtotal = sum(item['price'] * item['quantity'] for item in items)
        tax = subtotal * tax_rate
        return subtotal + tax
    """

    docs = await generate_docs(python_function)
    print(f"\nGenerated Documentation:\n{docs}\n")

    # Example 2: Document an API endpoint
    print(f"\n{'='*80}")
    print("Example 2: Documenting an API Endpoint")
    print(f"{'='*80}\n")

    api_info = """
    POST /api/v1/users
    Creates a new user account

    Request Body:
    - email (string, required)
    - password (string, required, min 8 chars)
    - name (string, required)
    - role (string, optional, default: "user")

    Returns: User object with id, email, name, created_at
    """

    docs = await generate_docs(api_info)
    print(f"\nGenerated Documentation:\n{docs}\n")

    print(f"{'='*80}")
    print("Pattern Demonstrated: Simple Agent")
    print(f"{'='*80}")
    print("""
Key Concepts:
1. Single agent handles one well-defined task
2. No complex orchestration or state management
3. Direct input → processing → output flow
4. Perfect for deterministic, repeatable tasks
5. Ideal for automation where reliability matters most

When to Use:
- Repetitive tasks with clear inputs and outputs
- Documentation generation, report creation
- Data transformation, format conversion
- Any task where complexity adds no value

Business Value:
- Quick to implement and deploy
- Easy to maintain and debug
- High reliability and predictability
- Immediate ROI on time-consuming manual tasks
    """)


if __name__ == "__main__":
    asyncio.run(main())
