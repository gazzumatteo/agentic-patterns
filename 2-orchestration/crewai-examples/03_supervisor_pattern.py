"""
Pattern 2: Routing
Dynamic workflow selection based on input characteristics.

Business Example: Content classification system
- Analyze input -> Determine category -> Route to specialist handler

This example demonstrates CrewAI's hierarchical process for intelligent
routing with a manager agent delegating to specialists.

Mermaid Diagram Reference: See diagrams/02_routing.mermaid
"""

from crewai import Agent, Task, Crew, Process
from typing import Dict, Any
import json


def create_routing_crew(user_request: str) -> Crew:
    """
    Creates a CrewAI crew with routing capabilities.

    Args:
        user_request: The user's support request

    Returns:
        Configured Crew with router and specialist agents
    """

    # Router Agent
    router = Agent(
        role="Request Classification Specialist",
        goal="Accurately classify and route customer requests to the right specialist",
        backstory="""You are an experienced customer service manager with years
        of experience in triaging support requests. You quickly understand the
        nature of each request and know exactly which specialist should handle it.""",
        verbose=True,
        allow_delegation=True  # Can delegate to specialists
    )

    # Specialist Agents
    technical_specialist = Agent(
        role="Senior Technical Support Engineer",
        goal="Resolve technical issues and provide expert troubleshooting",
        backstory="""You are a senior technical support engineer with deep knowledge
        of systems, APIs, and debugging. You excel at diagnosing issues quickly and
        providing clear, actionable solutions.""",
        verbose=True,
        allow_delegation=False
    )

    billing_specialist = Agent(
        role="Billing and Payments Specialist",
        goal="Handle billing inquiries with accuracy and empathy",
        backstory="""You are a billing specialist who understands payment systems,
        subscription management, and financial policies. You handle sensitive
        billing matters with care and professionalism.""",
        verbose=True,
        allow_delegation=False
    )

    sales_specialist = Agent(
        role="Sales Representative",
        goal="Help customers find the right products and close deals",
        backstory="""You are an enthusiastic sales representative who loves helping
        customers discover solutions that meet their needs. You're knowledgeable
        about products, pricing, and value propositions.""",
        verbose=True,
        allow_delegation=False
    )

    general_specialist = Agent(
        role="Customer Service Representative",
        goal="Provide friendly, helpful support for general inquiries",
        backstory="""You are a friendly customer service representative who handles
        a wide variety of questions. You're patient, helpful, and always ready to
        assist customers with their needs.""",
        verbose=True,
        allow_delegation=False
    )

    # Routing Task
    routing_task = Task(
        description=f"""
        Analyze this customer request and determine the best specialist to handle it:

        REQUEST: {user_request}

        Classify the request into one of these categories:
        - technical: Technical issues, bugs, errors, API problems
        - billing: Payment, invoices, subscriptions, refunds
        - sales: Product inquiries, demos, new purchases
        - general: General questions, feedback, other

        Provide your classification as JSON:
        {{
            "category": "technical|billing|sales|general",
            "confidence": 0.0-1.0,
            "reasoning": "brief explanation",
            "specialist_needed": "name of specialist role"
        }}

        Then delegate to the appropriate specialist to handle the request.
        """,
        expected_output="""A JSON classification followed by the specialist's
        response to the customer request.""",
        agent=router
    )

    # Specialist Tasks (will be dynamically selected via delegation)
    technical_task = Task(
        description=f"""
        Handle this technical support request: {user_request}

        Provide:
        1. Issue classification
        2. Severity assessment
        3. Suggested solution or troubleshooting steps
        4. Estimated resolution time
        5. Whether escalation is needed
        """,
        expected_output="Comprehensive technical support response",
        agent=technical_specialist
    )

    billing_task = Task(
        description=f"""
        Handle this billing request: {user_request}

        Provide:
        1. Issue type
        2. Required information to proceed
        3. Resolution steps
        4. Estimated processing time
        5. Relevant policies
        """,
        expected_output="Clear billing support response",
        agent=billing_specialist
    )

    sales_task = Task(
        description=f"""
        Respond to this sales inquiry: {user_request}

        Provide:
        1. Understanding of customer needs
        2. Product/service recommendations
        3. Key benefits and features
        4. Pricing information
        5. Next steps
        """,
        expected_output="Helpful sales response",
        agent=sales_specialist
    )

    general_task = Task(
        description=f"""
        Respond to this general request: {user_request}

        Provide:
        1. Understanding of the inquiry
        2. Helpful information or guidance
        3. Additional resources
        4. Routing suggestion if needed
        """,
        expected_output="Friendly general support response",
        agent=general_specialist
    )

    # Create crew with hierarchical process (enables delegation/routing)
    # Note: manager_agent should NOT be included in agents list
    crew = Crew(
        agents=[technical_specialist, billing_specialist,
                sales_specialist, general_specialist],
        tasks=[routing_task, technical_task, billing_task,
               sales_task, general_task],
        process=Process.hierarchical,  # Enables manager-worker pattern
        manager_agent=router,  # Router acts as manager
        verbose=True
    )

    return crew


def route_and_handle(user_request: str) -> Dict[str, Any]:
    """
    Route a user request to the appropriate specialist.

    Args:
        user_request: The user's support request

    Returns:
        Dictionary containing routing info and response
    """
    crew = create_routing_crew(user_request)
    result = crew.kickoff()

    return {
        "status": "completed",
        "request": user_request,
        "result": result
    }


def main():
    """Main execution function demonstrating routing pattern."""

    test_requests = [
        {
            "name": "Technical Issue",
            "request": "Our API is returning 500 errors when we try to authenticate. "
                      "This started happening after the latest deployment."
        },
        {
            "name": "Billing Question",
            "request": "I was charged twice this month for my subscription. "
                      "Can you please refund the duplicate charge?"
        },
        {
            "name": "Sales Inquiry",
            "request": "We're interested in upgrading from the Basic plan to Enterprise. "
                      "Can you provide pricing for 50 users?"
        },
        {
            "name": "General Question",
            "request": "How do I reset my password? I can't find the option in settings."
        }
    ]

    for idx, test in enumerate(test_requests, 1):
        print("=" * 80)
        print(f"Request {idx}: {test['name']}")
        print("=" * 80)
        print(f"User Request: {test['request']}")
        print()

        result = route_and_handle(test['request'])

        print(f"=� Complete Response:")
        print(f"{result['result']}")
        print()

    print("=" * 80)
    print("Pattern Demonstrated: Routing with CrewAI")
    print("=" * 80)
    print("""
    Key Observations:
    1. Hierarchical Process: Manager agent (router) delegates to specialists
    2. Allow Delegation: Router has allow_delegation=True to route tasks
    3. Specialist Expertise: Each specialist has domain-specific knowledge
    4. Dynamic Selection: Manager chooses appropriate specialist based on request
    5. Natural Flow: Feels like real team collaboration

    Performance Metrics:
    - Routing: Manager agent analyzes and delegates
    - Execution: Specialist handles the request
    - Latency: Manager analysis + Specialist response

    CrewAI Advantages:
    - Natural hierarchical structure
    - Built-in delegation mechanism
    - Role-based specialization
    - Easy to add new specialists

    Best Practices:
    - Define clear specialist roles
    - Use hierarchical process for routing
    - Enable delegation on manager/router
    - Provide clear category definitions
    """)


if __name__ == "__main__":
    # Set up API keys before running:
    # export OPENAI_API_KEY="your-openai-key"
    # or
    # export ANTHROPIC_API_KEY="your-anthropic-key"

    main()
