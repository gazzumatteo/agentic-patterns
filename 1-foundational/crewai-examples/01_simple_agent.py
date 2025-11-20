"""
Pattern 1: Simple Agent (Single-agent)
The atomic unit of agent systems. One agent, one task, zero complexity.

Business Example: Automated Documentation Generator
- Company: TechCorp (SaaS, 500 employees)
- Challenge: Engineers spending 4 hours/week updating API documentation
- Solution: Single agent monitoring code commits, auto-generating OpenAPI specs
- Results: 92% reduction in documentation lag, $180K annual savings

This example demonstrates the simplest form of an AI agent using CrewAI.

Mermaid Diagram Reference: See diagrams/01_simple_agent.mermaid
"""

from crewai import Agent, Task, Crew


# ========================================
# SIMPLE AGENT DEFINITION
# ========================================

documentation_agent = Agent(
    role="Technical Documentation Expert",
    goal="Generate clear, professional technical documentation",
    backstory="""
    You are an expert technical writer with years of experience creating
    API documentation, code documentation, and technical guides.
    You excel at explaining complex technical concepts clearly and concisely.
    """,
    verbose=False
)


# ========================================
# USAGE EXAMPLES
# ========================================

def generate_docs(code_or_api_info: str) -> str:
    """Generate documentation using the simple agent."""

    task = Task(
        description=f"""
        Generate professional technical documentation for the following:

        {code_or_api_info}

        Requirements:
        - Use proper markdown formatting
        - Include code examples where appropriate
        - Document all parameters and return values
        - Add usage examples
        - Be concise but complete
        """,
        agent=documentation_agent,
        expected_output="Complete markdown documentation"
    )

    crew = Crew(
        agents=[documentation_agent],
        tasks=[task],
        verbose=False
    )

    result = crew.kickoff()
    return result.raw if hasattr(result, 'raw') else str(result)


def main():
    """Main execution demonstrating the simple agent pattern."""

    print(f"\n{'='*80}")
    print("Pattern 1: Simple Agent (Single-agent) - CrewAI")
    print(f"{'='*80}\n")

    # Example 1: Document a Python function
    print("Example 1: Documenting a Python Function")
    print("-" * 80)

    python_function = """
    def calculate_total_price(items: list[dict], tax_rate: float = 0.08) -> float:
        '''Calculate total price including tax'''
        subtotal = sum(item['price'] * item['quantity'] for item in items)
        tax = subtotal * tax_rate
        return subtotal + tax
    """

    docs = generate_docs(python_function)
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

    docs = generate_docs(api_info)
    print(f"\nGenerated Documentation:\n{docs}\n")

    print(f"{'='*80}")
    print("Pattern Demonstrated: Simple Agent")
    print(f"{'='*80}")
    print("""
Key Concepts:
1. Single agent handles one well-defined task
2. No complex orchestration or state management
3. Direct input -> processing -> output flow
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
    main()
