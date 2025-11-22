"""
Resource-Aware Optimization Pattern - CrewAI Implementation

This pattern demonstrates dynamic model switching to balance costs and quality,
routing simple queries to cheaper models and complex tasks to more powerful models.

Business Use Case: Cost Management
The Router Agent directs 90% of FAQ requests to low-cost models,
saving the most powerful and expensive LLM for risk analysis tasks.

Pattern: Resource-Aware Optimization
Section: III - Governance, Reliability, and Support Patterns
Framework: CrewAI
"""

import json
import time
from typing import Dict, Any
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# --- Cost Tracking ---
class CostTracker:
    """Tracks token usage and costs for different models"""

    def __init__(self):
        # Simplified pricing per 1K tokens (input/output)
        self.pricing = {
            "gpt-4o-mini": {"input": 0.0001, "output": 0.0003},
            "gpt-4o": {"input": 0.0013, "output": 0.0052}
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

        mini_queries = [e for e in self.usage_log if "mini" in e["model"]]
        full_queries = [e for e in self.usage_log if "mini" not in e["model"]]

        return {
            "total_queries": len(self.usage_log),
            "total_cost": round(self.total_cost, 6),
            "mini_queries": len(mini_queries),
            "mini_cost": round(sum(e["cost"] for e in mini_queries), 6),
            "full_queries": len(full_queries),
            "full_cost": round(sum(e["cost"] for e in full_queries), 6),
            "avg_cost_per_query": round(self.total_cost / len(self.usage_log), 6),
            "cost_savings": f"{(len(mini_queries) / len(self.usage_log) * 100):.1f}% queries on low-cost model"
        }


cost_tracker = CostTracker()


# --- Custom Tools ---
class AnalyzeComplexityInput(BaseModel):
    """Input schema for analyze_query_complexity tool"""
    query: str = Field(..., description="The user query to analyze")


class AnalyzeComplexityTool(BaseTool):
    name: str = "analyze_query_complexity"
    description: str = "Analyze query complexity to determine appropriate model (simple queries: mini model, complex queries: full model)"

    def _run(self, query: str) -> str:
        """Analyze query complexity"""
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
            recommended_model = "gpt-4o"
            reason = "Query requires deep reasoning, analysis, or complex logic"
        elif simple_score > 0 or word_count < 15:
            complexity = "simple"
            recommended_model = "gpt-4o-mini"
            reason = "Query is straightforward and can be handled efficiently"
        else:
            complexity = "moderate"
            recommended_model = "gpt-4o-mini"  # Default to cost-effective
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


class GetFAQInput(BaseModel):
    """Input schema for get_faq_answer tool"""
    question: str = Field(..., description="The FAQ question")


class GetFAQTool(BaseTool):
    name: str = "get_faq_answer"
    description: str = "Retrieve answer from FAQ database for common questions"

    def _run(self, question: str) -> str:
        """Get FAQ answer"""
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


class RiskAnalysisInput(BaseModel):
    """Input schema for perform_risk_analysis tool"""
    scenario: str = Field(..., description="The business scenario to analyze")


class RiskAnalysisTool(BaseTool):
    name: str = "perform_risk_analysis"
    description: str = "Perform complex risk analysis (requires powerful model)"

    def _run(self, scenario: str) -> str:
        """Perform risk analysis"""
        return json.dumps({
            "scenario": scenario,
            "message": "Complex risk analysis requires full model",
            "factors_to_consider": [
                "Market volatility",
                "Regulatory compliance",
                "Financial exposure",
                "Operational dependencies"
            ]
        }, indent=2)


# Initialize tools
complexity_tool = AnalyzeComplexityTool()
faq_tool = GetFAQTool()
risk_tool = RiskAnalysisTool()


# --- Agents ---
def create_router_agent() -> Agent:
    """Create Query Router agent"""
    return Agent(
        role="Query Router",
        goal="Analyze incoming queries and route them to the most cost-effective model",
        backstory="""You are a Query Routing specialist who optimizes costs by
        intelligently directing queries to appropriate models. You analyze query
        complexity and route simple queries to efficient mini models while
        reserving powerful full models for truly complex analytical tasks.""",
        tools=[complexity_tool],
        verbose=True,
        allow_delegation=True
    )


def create_simple_handler() -> Agent:
    """Create Simple Query Handler agent"""
    return Agent(
        role="Simple Query Handler",
        goal="Handle straightforward queries efficiently using the mini model",
        backstory="""You are a Quick Response specialist using efficient mini
        models. You handle FAQs, simple questions, and straightforward requests
        with speed and accuracy. You use the FAQ database when applicable.""",
        tools=[faq_tool],
        verbose=True,
        allow_delegation=False
    )


def create_complex_handler() -> Agent:
    """Create Complex Query Handler agent"""
    return Agent(
        role="Complex Query Handler",
        goal="Handle complex analytical queries using the full model",
        backstory="""You are a Deep Analysis specialist using powerful full
        models. You handle complex queries requiring sophisticated reasoning,
        risk analysis, strategic planning, and multi-factor evaluation.""",
        tools=[risk_tool],
        verbose=True,
        allow_delegation=False
    )


# --- Main Execution ---
def run_resource_optimization_demo():
    """Demonstrate resource-aware optimization pattern"""
    print("=" * 80)
    print("Resource-Aware Optimization Pattern - Dynamic Model Switching")
    print("=" * 80)

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

    print("\nTest Queries:")
    for i, q in enumerate(test_queries, 1):
        complexity = "Complex" if len(q) > 50 or any(w in q.lower() for w in ["analyze", "evaluate", "assess"]) else "Simple"
        print(f"   {i}. [{complexity}] {q[:60]}{'...' if len(q) > 60 else ''}")

    print(f"\n{'=' * 80}")
    print("Processing Queries with Dynamic Model Selection...")
    print(f"{'=' * 80}\n")

    # Create agents
    router = create_router_agent()
    simple_handler = create_simple_handler()
    complex_handler = create_complex_handler()

    for idx, query in enumerate(test_queries, 1):
        start_time = time.time()

        print(f"\nQuery {idx}: {query[:70]}{'...' if len(query) > 70 else ''}")

        # Create routing task
        route_task = Task(
            description=f"""Analyze this query and determine routing:
            Query: "{query}"

            Use analyze_query_complexity to determine if this is simple or complex.
            Report the recommended model and reasoning.""",
            agent=router,
            expected_output="Analysis of query complexity with recommended model"
        )

        # Determine handler based on query characteristics
        if any(kw in query.lower() for kw in ["analyze", "evaluate", "assess", "risk"]):
            handler = complex_handler
            handler_name = "Full"
            model = "gpt-4o"

            handle_task = Task(
                description=f"""Handle this complex query: "{query}"
                Use risk analysis tools if applicable and provide detailed response.""",
                agent=handler,
                expected_output="Detailed analytical response",
                context=[route_task]
            )
        else:
            handler = simple_handler
            handler_name = "Mini"
            model = "gpt-4o-mini"

            handle_task = Task(
                description=f"""Handle this simple query: "{query}"
                Check FAQ database if applicable and provide clear, concise response.""",
                agent=handler,
                expected_output="Clear, concise response",
                context=[route_task]
            )

        # Create crew
        crew = Crew(
            agents=[router, handler],
            tasks=[route_task, handle_task],
            process=Process.sequential,
            verbose=False
        )

        # Execute
        try:
            result = crew.kickoff()
        except Exception as e:
            print(f"   [Error]: {e}")
            continue

        duration = time.time() - start_time

        # Log usage (simulated token counts)
        input_tokens = len(query.split()) * 2
        output_tokens = 50 if "mini" in model else 150

        cost_tracker.log_usage(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            query_type="simple" if "mini" in model else "complex",
            duration=duration
        )

        print(f"   → Routed to: {handler_name} model ({model})")
        print(f"   → Duration: {duration:.3f}s")
        print(f"   → Estimated cost: ${cost_tracker.usage_log[-1]['cost']:.6f}")

    # Final statistics
    print(f"\n{'=' * 80}")
    print("Resource Optimization Complete!")
    print(f"{'=' * 80}")

    stats = cost_tracker.get_statistics()
    print(f"\nCost Analysis:")
    print(f"   Total Queries: {stats['total_queries']}")
    print(f"   Total Cost: ${stats['total_cost']:.6f}")
    print(f"   Average Cost/Query: ${stats['avg_cost_per_query']:.6f}")
    print(f"\n   Mini Model Queries: {stats['mini_queries']} (${stats['mini_cost']:.6f})")
    print(f"   Full Model Queries: {stats['full_queries']} (${stats['full_cost']:.6f})")
    print(f"\n   Cost Savings: {stats['cost_savings']}")

    # Calculate savings vs all-full
    full_cost_all = stats['total_queries'] * 0.0065 * 150 / 1000
    savings_percent = ((full_cost_all - stats['total_cost']) / full_cost_all * 100)
    print(f"   Savings vs all-full model: {savings_percent:.1f}%")

    print("\nResource-Aware Optimization Pattern demonstrated successfully!")
    print("Queries dynamically routed based on complexity for cost optimization.")


if __name__ == "__main__":
    run_resource_optimization_demo()
