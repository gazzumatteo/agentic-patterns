"""
Resource-Aware Optimization Pattern - Google ADK Implementation

This pattern demonstrates dynamic model switching to balance costs and quality,
routing simple queries to cheaper models and complex tasks to more powerful models.

Business Use Case: Cost Management
The Router Agent directs 90% of FAQ requests to low-cost models,
saving the most powerful and expensive LLM for risk analysis tasks.

Pattern: Resource-Aware Optimization
Section: III - Governance, Reliability, and Support Patterns
Framework: Google ADK
"""

import asyncio
import time
from typing import Dict, Any, Optional
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import FunctionTool
from google.genai.types import Content, Part


# --- Constants ---
APP_NAME = "resource_optimization_app"
USER_ID = "cost_management_user"
MODEL_FLASH = "gemini-2.5-flash-exp"  # Fast, cheap
MODEL_PRO = "gemini-1.5-pro"  # Powerful, expensive


# --- Cost Tracking ---
class CostTracker:
    """Tracks token usage and costs for different models"""

    def __init__(self):
        # Simplified pricing per 1K tokens (input/output)
        self.pricing = {
            "gemini-2.5-flash-exp": {"input": 0.0001, "output": 0.0003},
            "gemini-1.5-pro": {"input": 0.0013, "output": 0.0052}
        }
        self.usage_log = []
        self.total_cost = 0.0

    def log_usage(self, model: str, input_tokens: int, output_tokens: int,
                  query_type: str, duration: float):
        """Log model usage and calculate cost"""
        input_cost = (input_tokens / 1000) * self.pricing[model]["input"]
        output_cost = (output_tokens / 1000) * self.pricing[model]["output"]
        total_cost = input_cost + output_cost

        self.total_cost += total_cost

        entry = {
            "model": model,
            "query_type": query_type,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": round(total_cost, 6),
            "duration": round(duration, 3)
        }
        self.usage_log.append(entry)
        return entry

    def get_statistics(self) -> Dict[str, Any]:
        """Get cost and usage statistics"""
        if not self.usage_log:
            return {"message": "No usage data"}

        flash_queries = [e for e in self.usage_log if "flash" in e["model"]]
        pro_queries = [e for e in self.usage_log if "pro" in e["model"]]

        return {
            "total_queries": len(self.usage_log),
            "total_cost": round(self.total_cost, 6),
            "flash_queries": len(flash_queries),
            "flash_cost": round(sum(e["cost"] for e in flash_queries), 6),
            "pro_queries": len(pro_queries),
            "pro_cost": round(sum(e["cost"] for e in pro_queries), 6),
            "avg_cost_per_query": round(self.total_cost / len(self.usage_log), 6),
            "cost_savings": f"{(len(flash_queries) / len(self.usage_log) * 100):.1f}% queries on low-cost model"
        }


cost_tracker = CostTracker()


# --- Query Complexity Analyzer ---
def analyze_query_complexity(query: str) -> str:
    """
    Analyze query complexity to determine appropriate model.

    Simple queries (FAQs, definitions): Use Flash
    Complex queries (analysis, reasoning): Use Pro

    Args:
        query: The user query to analyze

    Returns:
        JSON string with complexity analysis
    """
    import json

    query_lower = query.lower()

    # Keywords indicating complexity
    simple_keywords = ["what is", "define", "how do i", "where", "when", "faq",
                      "list", "show me", "tell me about"]
    complex_keywords = ["analyze", "evaluate", "compare", "assess", "risk",
                       "predict", "optimize", "recommend", "strategy",
                       "calculate", "forecast", "impact"]

    # Count matches
    simple_score = sum(1 for kw in simple_keywords if kw in query_lower)
    complex_score = sum(1 for kw in complex_keywords if kw in query_lower)

    # Additional complexity factors
    word_count = len(query.split())
    has_numbers = any(char.isdigit() for char in query)
    has_conditions = any(word in query_lower for word in ["if", "when", "assuming", "given"])

    # Decision logic
    if complex_score > 0 or (word_count > 20 and has_conditions):
        complexity = "complex"
        recommended_model = MODEL_PRO
        reason = "Query requires deep reasoning, analysis, or complex logic"
    elif simple_score > 0 or word_count < 15:
        complexity = "simple"
        recommended_model = MODEL_FLASH
        reason = "Query is straightforward and can be handled efficiently"
    else:
        complexity = "moderate"
        recommended_model = MODEL_FLASH  # Default to cost-effective
        reason = "Query complexity is moderate, using cost-effective model"

    return json.dumps({
        "query": query,
        "complexity": complexity,
        "recommended_model": recommended_model,
        "reason": reason,
        "word_count": word_count,
        "has_numbers": has_numbers,
        "has_conditions": has_conditions
    }, indent=2)


# --- Domain Knowledge Tools ---
def get_faq_answer(question: str) -> str:
    """
    Retrieve answer from FAQ database (simulated).

    Args:
        question: The FAQ question

    Returns:
        Answer if found, otherwise guidance to use complex model
    """
    import json

    faq_db = {
        "business hours": "Our business hours are Monday-Friday, 9 AM to 5 PM EST.",
        "return policy": "Items can be returned within 30 days with original receipt.",
        "shipping": "Standard shipping takes 5-7 business days. Express available.",
        "payment methods": "We accept credit cards, PayPal, and bank transfers.",
        "account setup": "Click 'Sign Up' and follow the registration process."
    }

    question_lower = question.lower()
    for key, answer in faq_db.items():
        if key in question_lower:
            return json.dumps({
                "found": True,
                "question": question,
                "answer": answer,
                "source": "FAQ Database"
            }, indent=2)

    return json.dumps({
        "found": False,
        "message": "No FAQ match found. Complex query requires advanced model."
    }, indent=2)


def perform_risk_analysis(scenario: str) -> str:
    """
    Perform complex risk analysis (requires powerful model).

    Args:
        scenario: The business scenario to analyze

    Returns:
        Risk assessment placeholder
    """
    import json

    return json.dumps({
        "scenario": scenario,
        "message": "Complex risk analysis requires Pro model",
        "factors_to_consider": [
            "Market volatility",
            "Regulatory compliance",
            "Financial exposure",
            "Operational dependencies"
        ]
    }, indent=2)


# Create FunctionTools
complexity_tool = FunctionTool(func=analyze_query_complexity)
faq_tool = FunctionTool(func=get_faq_answer)
risk_tool = FunctionTool(func=perform_risk_analysis)


# --- Agents ---
# Router Agent - Analyzes query and routes to appropriate model
router_agent = LlmAgent(
    model=MODEL_FLASH,  # Router itself uses cheap model
    name="QueryRouter",
    instruction="""You are a Query Router agent. Your role is to:
    1. Use the analyze_query_complexity tool to analyze incoming queries
    2. Based on complexity, store the recommended model in session state as 'target_model'
    3. Store the complexity analysis in 'complexity_analysis'
    4. Provide a brief explanation of routing decision

    Be efficient - use the Flash model for most queries, reserve Pro for truly complex tasks.""",
    tools=[complexity_tool],
)

# Simple Query Handler - Uses Flash model
simple_handler = LlmAgent(
    model=MODEL_FLASH,
    name="SimpleQueryHandler",
    instruction="""You are a Simple Query Handler using the Flash model. Your role is to:
    1. Handle straightforward queries efficiently
    2. Use the FAQ tool if the query seems like a common question
    3. Provide clear, concise answers
    4. Store your response in 'handler_response' in session state

    Be quick and efficient.""",
    tools=[faq_tool],
)

# Complex Query Handler - Uses Pro model
complex_handler = LlmAgent(
    model=MODEL_PRO,
    name="ComplexQueryHandler",
    instruction="""You are a Complex Query Handler using the Pro model. Your role is to:
    1. Handle complex analytical queries requiring deep reasoning
    2. Use the risk analysis tool for risk-related queries
    3. Provide detailed, well-reasoned responses
    4. Store your response in 'handler_response' in session state

    Take time to provide thorough analysis.""",
    tools=[risk_tool],
)


# --- Main Execution ---
async def run_resource_optimization_demo():
    """Demonstrate resource-aware optimization pattern"""
    print("=" * 80)
    print("Resource-Aware Optimization Pattern - Dynamic Model Switching")
    print("=" * 80)

    # Initialize services
    session_service = InMemorySessionService()

    # Test queries with varying complexity
    test_queries = [
        "What are your business hours?",
        "How do I return a product?",
        "What payment methods do you accept?",
        "Analyze the financial risk of expanding into the European market considering regulatory compliance, currency fluctuation, and competitive landscape.",
        "What is your shipping policy?",
        "Evaluate the strategic impact of investing in AI automation versus hiring additional staff, considering 5-year ROI, scalability, and market positioning.",
        "Tell me about account setup",
        "Assess the cybersecurity risks associated with our cloud migration strategy and recommend mitigation approaches."
    ]

    print("\n📊 Test Queries:")
    for i, q in enumerate(test_queries, 1):
        complexity = "Complex" if len(q) > 50 or any(w in q.lower() for w in ["analyze", "evaluate", "assess"]) else "Simple"
        print(f"   {i}. [{complexity}] {q[:60]}{'...' if len(q) > 60 else ''}")

    print("\n" + "=" * 80)
    print("Processing Queries with Dynamic Model Selection...")
    print("=" * 80 + "\n")

    for idx, query in enumerate(test_queries, 1):
        session_id = f"query_session_{idx:03d}"

        # Create session
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id
        )

        # Step 1: Route query
        router_runner = Runner(
            agent=router_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )

        start_time = time.time()

        user_message = Content(parts=[Part(text=query)], role="user")

        print(f"🔍 Query {idx}: {query[:70]}{'...' if len(query) > 70 else ''}")

        async for event in router_runner.run_async(
            user_id=USER_ID,
            session_id=session_id,
            new_message=user_message
        ):
            pass  # Process routing silently

        # Step 2: Get routed model and use appropriate handler
        session = await session_service.get_session(APP_NAME, USER_ID, session_id)
        target_model = session.state.get("target_model", MODEL_FLASH)

        if "flash" in target_model:
            handler = simple_handler
            handler_name = "Flash"
        else:
            handler = complex_handler
            handler_name = "Pro"

        handler_runner = Runner(
            agent=handler,
            app_name=APP_NAME,
            session_service=session_service,
        )

        async for event in handler_runner.run_async(
            user_id=USER_ID,
            session_id=session_id,
            new_message=user_message
        ):
            pass  # Process handling silently

        duration = time.time() - start_time

        # Log usage (simulated token counts)
        input_tokens = len(query.split()) * 2
        output_tokens = 50 if "flash" in target_model else 150

        cost_tracker.log_usage(
            model=target_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            query_type="simple" if "flash" in target_model else "complex",
            duration=duration
        )

        print(f"   → Routed to: {handler_name} model ({target_model})")
        print(f"   → Duration: {duration:.3f}s")
        print(f"   → Estimated cost: ${cost_tracker.usage_log[-1]['cost']:.6f}")
        print()

    # Final statistics
    print("=" * 80)
    print("Resource Optimization Complete!")
    print("=" * 80)

    stats = cost_tracker.get_statistics()
    print(f"\n💰 Cost Analysis:")
    print(f"   Total Queries: {stats['total_queries']}")
    print(f"   Total Cost: ${stats['total_cost']:.6f}")
    print(f"   Average Cost/Query: ${stats['avg_cost_per_query']:.6f}")
    print(f"\n   Flash Model Queries: {stats['flash_queries']} (${stats['flash_cost']:.6f})")
    print(f"   Pro Model Queries: {stats['pro_queries']} (${stats['pro_cost']:.6f})")
    print(f"\n   💡 Cost Savings: {stats['cost_savings']}")

    # Calculate savings vs all-Pro
    pro_cost_all = stats['total_queries'] * 0.0065 * 150 / 1000  # Assuming avg 150 tokens
    savings_percent = ((pro_cost_all - stats['total_cost']) / pro_cost_all * 100)
    print(f"   📉 Savings vs all-Pro model: {savings_percent:.1f}%")

    print("\n✅ Resource-Aware Optimization Pattern demonstrated successfully!")
    print("   Queries dynamically routed based on complexity for cost optimization.")


if __name__ == "__main__":
    asyncio.run(run_resource_optimization_demo())
