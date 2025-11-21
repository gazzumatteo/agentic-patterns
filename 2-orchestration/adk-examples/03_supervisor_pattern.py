"""
Pattern 2: Routing
Dynamic workflow selection based on input characteristics.

Business Example: Content classification system
- Analyze input -> Determine category -> Route to specialist handler

This example demonstrates Google ADK's supervisor pattern for intelligent
routing of support requests to specialized agents.

Mermaid Diagram Reference: See diagrams/02_routing.mermaid
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from typing import Any
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types


# Router Agent: Analyzes and classifies requests
router_agent = LlmAgent(
    name="RequestRouter",
    model="gemini-2.5-flash",
    instruction="""
    You are an intelligent request classifier. Analyze the input and determine
    the appropriate category for routing.

    Categories:
    - "technical": Technical issues, bugs, errors, API problems
    - "billing": Payment, invoices, subscriptions, refunds
    - "sales": Product inquiries, demos, new purchases
    - "general": General questions, feedback, other

    Analyze the request and output ONLY a JSON object:
    {{
        "category": "technical|billing|sales|general",
        "confidence": 0.0-1.0,
        "reasoning": "brief explanation"
    }}
    """,
    description="Routes requests to appropriate specialist",
    output_key="routing_decision"
)

# Specialist Agents
technical_agent = LlmAgent(
    name="TechnicalSupport",
    model="gemini-2.5-flash",
    instruction="""
    You are a senior technical support engineer.

    Analyze the technical issue from the request: {user_request}

    Provide:
    1. Issue classification (bug, configuration, usage question, etc.)
    2. Severity assessment (low, medium, high, critical)
    3. Suggested solution or troubleshooting steps
    4. Estimated resolution time
    5. Whether escalation to engineering is needed

    Be precise, technical, and solution-oriented.
    """,
    description="Handles technical support requests",
    output_key="response"
)

billing_agent = LlmAgent(
    name="BillingSupport",
    model="gemini-2.5-flash",
    instruction="""
    You are a billing and payments specialist.

    Handle the billing request: {user_request}

    Provide:
    1. Issue type (payment failure, refund request, invoice question, etc.)
    2. Required information to proceed
    3. Resolution steps
    4. Estimated processing time
    5. Any relevant policies or terms

    Be clear, empathetic, and policy-compliant.
    """,
    description="Handles billing and payment requests",
    output_key="response"
)

sales_agent = LlmAgent(
    name="SalesRepresentative",
    model="gemini-2.5-flash",
    instruction="""
    You are an enthusiastic sales representative.

    Respond to the sales inquiry: {user_request}

    Provide:
    1. Understanding of the customer's needs
    2. Relevant product/service recommendations
    3. Key benefits and features
    4. Pricing information (if applicable)
    5. Next steps (demo, trial, quote, etc.)

    Be helpful, consultative, and value-focused.
    """,
    description="Handles sales inquiries",
    output_key="response"
)

general_agent = LlmAgent(
    name="GeneralSupport",
    model="gemini-2.5-flash",
    instruction="""
    You are a friendly customer service representative.

    Respond to the general request: {user_request}

    Provide:
    1. Understanding of the customer's inquiry
    2. Helpful information or guidance
    3. Additional resources if applicable
    4. Suggestion to route to a specialist if needed

    Be friendly, informative, and helpful.
    """,
    description="Handles general support requests",
    output_key="response"
)


async def route_and_handle(user_request: str) -> dict[str, Any]:
    """
    Route a user request to the appropriate specialist agent.

    Args:
        user_request: The user's support request

    Returns:
        Dictionary containing routing decision and specialist response
    """
    # Create session with initial state
    session_service = InMemorySessionService()
    app_name = "agentic_patterns"
    user_id = "demo_user"
    session_id = f"request_{hash(user_request)}"

    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state={"user_request": user_request}
    )

    # Step 1: Route the request
    runner = Runner(
        agent=router_agent,
        app_name=app_name,
        session_service=session_service
    )

    content = types.Content(role='user', parts=[types.Part(text=user_request)])
    events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content)

    async for event in events:
        if event.is_final_response():
            pass

    # Get updated session to access state
    updated_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    routing_decision = updated_session.state.get("routing_decision", "{}")

    # Parse routing decision
    import json
    try:
        decision = json.loads(routing_decision)
        category = decision.get("category", "general")
        confidence = decision.get("confidence", 0.0)
        reasoning = decision.get("reasoning", "")
    except:
        category = "general"
        confidence = 0.0
        reasoning = "Failed to parse routing decision"

    # Step 2: Route to appropriate specialist
    specialist_map = {
        "technical": technical_agent,
        "billing": billing_agent,
        "sales": sales_agent,
        "general": general_agent
    }

    specialist = specialist_map.get(category, general_agent)

    # Run specialist agent
    specialist_runner = Runner(
        agent=specialist,
        app_name=app_name,
        session_service=session_service
    )

    content = types.Content(role='user', parts=[types.Part(text=user_request)])
    events = specialist_runner.run_async(user_id=user_id, session_id=session_id, new_message=content)

    async for event in events:
        if event.is_final_response():
            pass

    # Get final session state
    final_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    response = final_session.state.get("response", "")

    return {
        "routing": {
            "category": category,
            "confidence": confidence,
            "reasoning": reasoning,
            "specialist": specialist.name
        },
        "response": response
    }


async def main():
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

        result = await route_and_handle(test['request'])

        print(f"= Routing Decision:")
        print(f"   Category: {result['routing']['category']}")
        print(f"   Confidence: {result['routing']['confidence']:.2f}")
        print(f"   Specialist: {result['routing']['specialist']}")
        print(f"   Reasoning: {result['routing']['reasoning']}")
        print()
        print(f"=� Specialist Response:")
        print(f"{result['response']}")
        print()

    print("=" * 80)
    print("Pattern Demonstrated: Routing")
    print("=" * 80)
    print("""
    Key Observations:
    1. Dynamic Classification: Router analyzes request content semantically
    2. Specialist Selection: Automatically routes to most appropriate handler
    3. Confidence Scoring: Provides transparency in routing decisions
    4. Modular Specialists: Each specialist has domain expertise
    5. Fallback Handling: Defaults to general agent if uncertain

    Performance Metrics:
    - Routing Accuracy: Depends on router agent quality
    - Latency: Router + Specialist (2 LLM calls)
    - Scalability: Easy to add new specialist categories

    Best Practices:
    - Use clear category definitions
    - Provide examples in router instruction
    - Monitor routing accuracy and adjust
    - Implement confidence thresholds for escalation
    """)


if __name__ == "__main__":
    # Set up Google Cloud credentials before running
    # export GOOGLE_CLOUD_PROJECT="your-project-id"
    # export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

    asyncio.run(main())
