"""
Pattern 3: Parallelization
Concurrent execution of independent tasks for improved performance.

Business Example: Multi-source market research
- Simultaneously fetch: competitor analysis, market trends, customer sentiment
- Aggregate results into comprehensive report

This example demonstrates Google ADK's ParallelAgent for concurrent execution
with significant performance improvements.

Mermaid Diagram Reference: See diagrams/03_parallelization.mermaid
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import time
from typing import Any
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types


# Parallel Research Agents
competitor_analyst = LlmAgent(
    name="CompetitorAnalyst",
    model="gemini-2.5-flash",
    instruction="""
    You are a competitive intelligence analyst. Analyze the competitive landscape
    for the company/topic provided in the request.

    Provide:
    1. Top 3 main competitors
    2. Their key strengths
    3. Their weaknesses or gaps
    4. Market positioning
    5. Competitive threats

    Focus on actionable insights. Keep analysis concise (3-4 sentences per competitor).
    """,
    description="Analyzes competitive landscape",
    output_key="competitor_analysis"
)

market_trends_analyst = LlmAgent(
    name="MarketTrendsAnalyst",
    model="gemini-2.5-flash",
    instruction="""
    You are a market trends researcher. Analyze current market trends and dynamics
    for the industry/topic provided in the request.

    Identify:
    1. 3-5 key current trends
    2. Emerging technologies or approaches
    3. Market growth indicators
    4. Regulatory or industry changes
    5. Future outlook (6-12 months)

    Provide data-driven insights with specific examples.
    """,
    description="Researches market trends and dynamics",
    output_key="market_trends"
)

customer_sentiment_analyst = LlmAgent(
    name="CustomerSentimentAnalyst",
    model="gemini-2.5-flash",
    instruction="""
    You are a customer insights specialist. Analyze customer sentiment and feedback
    for the industry/product mentioned in the request.

    Assess:
    1. Overall customer sentiment (positive/negative/neutral)
    2. Key pain points customers express
    3. Most valued features or aspects
    4. Unmet needs or gaps
    5. Sentiment trends over time

    Provide qualitative and quantitative insights.
    """,
    description="Analyzes customer sentiment and feedback",
    output_key="customer_sentiment"
)

financial_analyst = LlmAgent(
    name="FinancialAnalyst",
    model="gemini-2.5-flash",
    instruction="""
    You are a financial analyst. Analyze the financial landscape and opportunities
    for the industry/company mentioned in the request.

    Evaluate:
    1. Market size and growth rate
    2. Investment trends
    3. Pricing dynamics
    4. Revenue opportunities
    5. Financial risks

    Focus on financial metrics and business implications.
    """,
    description="Analyzes financial aspects and opportunities",
    output_key="financial_analysis"
)

# Parallel execution of all research
parallel_research = ParallelAgent(
    name="ParallelResearchTeam",
    sub_agents=[
        competitor_analyst,
        market_trends_analyst,
        customer_sentiment_analyst,
        financial_analyst
    ]
)

# Aggregator to synthesize results
report_synthesizer = LlmAgent(
    name="ReportSynthesizer",
    model="gemini-2.5-flash",
    instruction="""
    You are a strategic analyst who synthesizes research into executive summaries.

    Using the research results from:
    - state['competitor_analysis']
    - state['market_trends']
    - state['customer_sentiment']
    - state['financial_analysis']

    Create a comprehensive executive summary with:
    1. Executive Overview (2-3 sentences)
    2. Key Findings (5-7 bullet points)
    3. Strategic Opportunities
    4. Risks and Challenges
    5. Recommended Next Steps

    Format clearly with headers and bullet points.
    """,
    description="Synthesizes research into executive report",
    output_key="executive_report"
)

# Complete pipeline: Parallel research � Sequential synthesis
research_pipeline = SequentialAgent(
    name="MarketResearchPipeline",
    sub_agents=[
        parallel_research,
        report_synthesizer
    ]
)


async def run_market_research(topic: str) -> dict[str, Any]:
    """
    Run parallel market research and synthesize results.

    Args:
        topic: The company, product, or industry to research

    Returns:
        Dictionary containing all research outputs and synthesis
    """
    start_time = time.time()

    # Create session
    session_service = InMemorySessionService()
    app_name = "agentic_patterns"
    user_id = "demo_user"
    session_id = f"research_{hash(topic)}"

    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    # Run the pipeline
    runner = Runner(
        agent=research_pipeline,
        app_name=app_name,
        session_service=session_service
    )

    content = types.Content(role='user', parts=[types.Part(text=topic)])
    events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content)

    async for event in events:
        if event.is_final_response():
            pass

    elapsed_time = time.time() - start_time

    # Get updated session to access state
    updated_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)

    return {
        "topic": topic,
        "elapsed_time": elapsed_time,
        "research": {
            "competitor_analysis": updated_session.state.get("competitor_analysis"),
            "market_trends": updated_session.state.get("market_trends"),
            "customer_sentiment": updated_session.state.get("customer_sentiment"),
            "financial_analysis": updated_session.state.get("financial_analysis")
        },
        "executive_report": updated_session.state.get("executive_report")
    }


async def main():
    """Main execution function demonstrating parallelization."""

    topics = [
        "AI-powered customer service platforms",
        "Electric vehicle charging infrastructure"
    ]

    for topic in topics:
        print("=" * 80)
        print(f"Market Research: {topic}")
        print("=" * 80)

        result = await run_market_research(topic)

        print(f"\n�  Total Execution Time: {result['elapsed_time']:.2f} seconds")
        print(f"\n=� Research Results:")
        print(f"\n1� Competitor Analysis:")
        print(result['research']['competitor_analysis'])
        print(f"\n2� Market Trends:")
        print(result['research']['market_trends'])
        print(f"\n3� Customer Sentiment:")
        print(result['research']['customer_sentiment'])
        print(f"\n4� Financial Analysis:")
        print(result['research']['financial_analysis'])
        print(f"\n=� Executive Report:")
        print(result['executive_report'])
        print("\n")

    print("=" * 80)
    print("Pattern Demonstrated: Parallelization")
    print("=" * 80)
    print("""
    Key Observations:
    1. Concurrent Execution: All 4 research agents run simultaneously
    2. Performance Gain: ~4x faster than sequential execution
    3. Independence: Research tasks don't depend on each other
    4. Shared State: All agents write to same session state (different keys)
    5. Fan-out/Fan-in: ParallelAgent fans out, Synthesizer fans in

    Performance Metrics:
    - Sequential Time: ~4 � individual agent time
    - Parallel Time: ~max(individual agent time)
    - Speedup: Nearly linear with number of agents
    - Best For: Independent, I/O-bound tasks

    ADK Advantages:
    - Native ParallelAgent support
    - Thread-safe state management
    - Easy composition with SequentialAgent
    - Deterministic aggregation

    Best Practices:
    - Ensure tasks are truly independent
    - Use different output_keys to avoid conflicts
    - Aggregate results with a synthesis agent
    - Monitor for rate limiting with many parallel agents
    """)


if __name__ == "__main__":
    # Set up Google Cloud credentials before running
    # export GOOGLE_CLOUD_PROJECT="your-project-id"
    # export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

    asyncio.run(main())
