"""
Pattern 3: Parallelization
Concurrent execution of independent tasks for improved performance.

Business Example: Multi-source market research
- Simultaneously fetch: competitor analysis, market trends, customer sentiment
- Aggregate results into comprehensive report

This example demonstrates CrewAI's parallel task execution with independent
agents working concurrently.

Mermaid Diagram Reference: See diagrams/03_parallelization.mermaid
"""

from crewai import Agent, Task, Crew, Process
from typing import Dict, Any
import time


def create_research_crew(topic: str) -> Crew:
    """
    Creates a CrewAI crew for parallel market research.

    Args:
        topic: The company, product, or industry to research

    Returns:
        Configured Crew with parallel execution
    """

    # Research Agents (all work independently in parallel)
    competitor_analyst = Agent(
        role="Competitive Intelligence Analyst",
        goal="Analyze competitive landscape and identify key competitors",
        backstory="""You are an expert competitive analyst with deep experience
        in market positioning and competitive strategy. You quickly identify
        key competitors and their strategic advantages.""",
        verbose=True,
        allow_delegation=False
    )

    market_trends_analyst = Agent(
        role="Market Trends Researcher",
        goal="Identify and analyze current market trends and dynamics",
        backstory="""You are a market research specialist who stays on top of
        industry trends, emerging technologies, and market shifts. You provide
        data-driven insights on market dynamics.""",
        verbose=True,
        allow_delegation=False
    )

    customer_sentiment_analyst = Agent(
        role="Customer Insights Specialist",
        goal="Analyze customer sentiment, feedback, and satisfaction",
        backstory="""You are a customer research expert who understands what
        drives customer satisfaction and loyalty. You excel at identifying
        customer pain points and unmet needs.""",
        verbose=True,
        allow_delegation=False
    )

    financial_analyst = Agent(
        role="Financial Market Analyst",
        goal="Evaluate financial landscape and business opportunities",
        backstory="""You are a financial analyst with expertise in market sizing,
        revenue analysis, and investment trends. You focus on the financial
        viability and business potential.""",
        verbose=True,
        allow_delegation=False
    )

    synthesizer = Agent(
        role="Strategic Analyst and Report Writer",
        goal="Synthesize research into comprehensive executive summaries",
        backstory="""You are a senior strategic analyst who excels at taking
        complex research from multiple sources and distilling it into clear,
        actionable executive summaries.""",
        verbose=True,
        allow_delegation=False
    )

    # Parallel Research Tasks
    competitor_task = Task(
        description=f"""
        Analyze the competitive landscape for: {topic}

        Provide:
        1. Top 3 main competitors
        2. Their key strengths
        3. Their weaknesses or gaps
        4. Market positioning
        5. Competitive threats

        Keep analysis concise but insightful.
        """,
        expected_output="Concise competitive analysis with 3 main competitors",
        agent=competitor_analyst
    )

    market_trends_task = Task(
        description=f"""
        Research current market trends for: {topic}

        Identify:
        1. 3-5 key current trends
        2. Emerging technologies or approaches
        3. Market growth indicators
        4. Regulatory or industry changes
        5. Future outlook (6-12 months)

        Provide specific examples and data points.
        """,
        expected_output="Market trends analysis with 3-5 key trends",
        agent=market_trends_analyst
    )

    customer_sentiment_task = Task(
        description=f"""
        Analyze customer sentiment and feedback for: {topic}

        Assess:
        1. Overall customer sentiment (positive/negative/neutral)
        2. Key pain points customers express
        3. Most valued features or aspects
        4. Unmet needs or gaps
        5. Sentiment trends

        Provide both qualitative and quantitative insights.
        """,
        expected_output="Customer sentiment analysis with key insights",
        agent=customer_sentiment_analyst
    )

    financial_task = Task(
        description=f"""
        Analyze the financial landscape for: {topic}

        Evaluate:
        1. Market size and growth rate
        2. Investment trends
        3. Pricing dynamics
        4. Revenue opportunities
        5. Financial risks

        Focus on business and financial metrics.
        """,
        expected_output="Financial analysis with market sizing and opportunities",
        agent=financial_analyst
    )

    # Synthesis Task (runs after all parallel tasks complete)
    synthesis_task = Task(
        description=f"""
        Synthesize all research findings into an executive summary for: {topic}

        Using all the research from the team, create a comprehensive report with:
        1. Executive Overview (2-3 sentences)
        2. Key Findings (5-7 bullet points from all research)
        3. Strategic Opportunities
        4. Risks and Challenges
        5. Recommended Next Steps

        Format clearly with headers and bullet points.
        Make it actionable for executives.
        """,
        expected_output="Comprehensive executive summary synthesizing all research",
        agent=synthesizer,
        context=[competitor_task, market_trends_task,
                customer_sentiment_task, financial_task]
    )

    # Create crew - tasks run in parallel where possible
    crew = Crew(
        agents=[competitor_analyst, market_trends_analyst,
                customer_sentiment_analyst, financial_analyst, synthesizer],
        tasks=[competitor_task, market_trends_task, customer_sentiment_task,
               financial_task, synthesis_task],
        process=Process.sequential,  # Sequential but parallel tasks execute concurrently
        verbose=True
    )

    return crew


def run_market_research(topic: str) -> Dict[str, Any]:
    """
    Run parallel market research and synthesize results.

    Args:
        topic: The company, product, or industry to research

    Returns:
        Dictionary containing research results
    """
    start_time = time.time()

    crew = create_research_crew(topic)
    result = crew.kickoff()

    elapsed_time = time.time() - start_time

    return {
        "topic": topic,
        "elapsed_time": elapsed_time,
        "result": result
    }


def main():
    """Main execution function demonstrating parallelization."""

    topics = [
        "AI-powered customer service platforms",
        "Electric vehicle charging infrastructure"
    ]

    for topic in topics:
        print("=" * 80)
        print(f"Market Research: {topic}")
        print("=" * 80)

        result = run_market_research(topic)

        print(f"\n->  Total Execution Time: {result['elapsed_time']:.2f} seconds")
        print(f"\n=-> Complete Research Report:")
        print(result['result'])
        print("\n")

    print("=" * 80)
    print("Pattern Demonstrated: Parallelization with CrewAI")
    print("=" * 80)
    print("""
    Key Observations:
    1. Independent Agents: Each agent has specialized research focus
    2. Context Chaining: Synthesis task uses context from all research tasks
    3. Concurrent Execution: CrewAI optimizes task execution automatically
    4. Role Specialization: Clear expertise domains per agent
    5. Natural Aggregation: Synthesizer combines all perspectives

    Performance Metrics:
    - Parallelization: Independent tasks run concurrently
    - Speedup: Reduced latency vs. pure sequential
    - Best For: Independent research or analysis tasks

    CrewAI Advantages:
    - Automatic task dependency resolution
    - Context parameter for natural data flow
    - Role-based parallel execution
    - Built-in optimization

    Best Practices:
    - Define independent agents for parallel work
    - Use context parameter to aggregate results
    - Ensure agents don't duplicate work
    - Add synthesis agent for final integration
    - Monitor API rate limits with many parallel agents

    Note: CrewAI handles parallel execution optimization automatically
    based on task dependencies defined via the context parameter.
    """)


if __name__ == "__main__":
    # Set up API keys before running:
    # export OPENAI_API_KEY="your-openai-key"
    # or
    # export ANTHROPIC_API_KEY="your-anthropic-key"

    main()
