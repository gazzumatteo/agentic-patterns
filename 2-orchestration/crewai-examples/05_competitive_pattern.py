"""
Pattern 13: Competitive Pattern
Multiple agents solve the same problem differently. Best solution wins through evaluation.

Business Example: Creative Campaign Generation - CreativeAI Marketing
- 5 copywriter agents compete on same brief
- Each generates unique campaign concept
- Evaluator agent scores on brand alignment, creativity, conversion potential
- Client receives top 3 options

Results:
- Campaign performance: +43% CTR improvement
- Creative production time: 2 weeks → 2 days
- Client approval rate: 68% → 91%
- Cost per campaign: -55%

This example demonstrates CrewAI's competitive process with parallel agents and evaluation.

Mermaid Diagram Reference: See diagrams/13_competitive_pattern.mermaid
"""

from crewai import Agent, Task, Crew, Process
from typing import Dict, List


def create_competitive_campaign_crew() -> Crew:
    """
    Create a competitive crew with multiple copywriters and an evaluator.

    Returns:
        Configured Crew with competitive process
    """

    # ========================================
    # COMPETING COPYWRITER AGENTS
    # ========================================

    copywriter_1 = Agent(
        role="Emotional Storytelling Copywriter",
        goal="Create campaign concepts that connect emotionally and build human connection",
        backstory="""You specialize in emotional storytelling and authentic human connection.
        You believe the best marketing touches hearts before minds. Your campaigns are
        known for making people feel understood, inspired, and emotionally connected to brands.
        You craft narratives that resonate on a deeply personal level.""",
        verbose=True,
        allow_delegation=False
    )

    copywriter_2 = Agent(
        role="Data-Driven Rational Copywriter",
        goal="Create campaigns based on logic, data, and rational persuasion",
        backstory="""You are a data-driven strategist who builds campaigns on facts,
        statistics, and logical reasoning. You believe customers make rational decisions
        when presented with compelling evidence. Your copy is clear, precise, and
        backed by data that proves value propositions beyond doubt.""",
        verbose=True,
        allow_delegation=False
    )

    copywriter_3 = Agent(
        role="Bold Humor Copywriter",
        goal="Create memorable campaigns using wit, humor, and bold creative risks",
        backstory="""You're the creative rebel who believes humor and boldness cut through
        noise better than anything else. Your campaigns make people laugh, share, and
        remember. You're not afraid to take creative risks that others won't, and your
        wit has won numerous industry awards.""",
        verbose=True,
        allow_delegation=False
    )

    copywriter_4 = Agent(
        role="Aspirational Luxury Copywriter",
        goal="Create premium campaigns that position products as aspirational and exclusive",
        backstory="""You craft campaigns for luxury and premium positioning. Your copy
        makes people aspire to be part of an exclusive club. You understand that luxury
        marketing is about the lifestyle and identity, not just the product. Every word
        conveys sophistication and exclusivity.""",
        verbose=True,
        allow_delegation=False
    )

    copywriter_5 = Agent(
        role="Authentic UGC-Style Copywriter",
        goal="Create campaigns that feel like authentic user-generated content",
        backstory="""You specialize in authentic, relatable, user-generated content style.
        You make brands feel human and approachable. Your campaigns don't feel like ads -
        they feel like recommendations from a trusted friend. You understand modern
        consumers trust peers over polished marketing.""",
        verbose=True,
        allow_delegation=False
    )

    # ========================================
    # EVALUATOR AGENT (CRITIC)
    # ========================================

    evaluator = Agent(
        role="Creative Director and Campaign Evaluator",
        goal="Objectively evaluate and rank campaign concepts to identify the best performers",
        backstory="""You are a veteran creative director with 20 years of experience.
        You've seen thousands of campaigns and know what works. You evaluate based on:
        - Brand alignment (does it fit the brand?)
        - Creativity (is it original and memorable?)
        - Conversion potential (will it drive results?)
        - Target resonance (does it speak to the audience?)
        - Clarity (is the message clear?)

        You're objective, thorough, and your recommendations have helped campaigns
        achieve 43% higher CTR on average. You select winning concepts based on merit,
        not politics.""",
        verbose=True,
        allow_delegation=False
    )

    # ========================================
    # COMPETITIVE TASKS
    # ========================================

    # Each copywriter gets the same brief, competes independently
    copywriter_1_task = Task(
        description="""
        Create a campaign concept for: {creative_brief}

        Generate a complete campaign including:
        1. Headline (attention-grabbing, memorable)
        2. Primary copy (2-3 sentences, compelling value proposition)
        3. Call-to-action (clear, action-oriented)
        4. Target audience insight (who this resonates with)
        5. Key differentiator (what makes this concept unique)

        Use YOUR UNIQUE STYLE: Emotional storytelling and human connection.
        Make this the BEST campaign concept - you're competing against 4 other copywriters.
        """,
        expected_output="""Complete campaign concept with headline, copy, CTA, audience insight,
        and differentiator. Should exemplify emotional storytelling approach.""",
        agent=copywriter_1
    )

    copywriter_2_task = Task(
        description="""
        Create a campaign concept for: {creative_brief}

        Generate a complete campaign with all elements (headline, copy, CTA, insight, differentiator).
        Use YOUR UNIQUE STYLE: Data-driven rational persuasion.
        Compete to win - create the most compelling concept.
        """,
        expected_output="Complete campaign concept exemplifying data-driven approach.",
        agent=copywriter_2
    )

    copywriter_3_task = Task(
        description="""
        Create a campaign concept for: {creative_brief}

        Generate complete campaign with all elements.
        Use YOUR UNIQUE STYLE: Bold humor and memorable wit.
        This is a competition - be bold and win.
        """,
        expected_output="Complete campaign concept with bold humor and creative risk-taking.",
        agent=copywriter_3
    )

    copywriter_4_task = Task(
        description="""
        Create a campaign concept for: {creative_brief}

        Generate complete campaign with all elements.
        Use YOUR UNIQUE STYLE: Aspirational luxury and premium positioning.
        Create the winning premium concept.
        """,
        expected_output="Complete campaign concept with luxury and aspirational positioning.",
        agent=copywriter_4
    )

    copywriter_5_task = Task(
        description="""
        Create a campaign concept for: {creative_brief}

        Generate complete campaign with all elements.
        Use YOUR UNIQUE STYLE: Authentic user-generated content approach.
        Win this competition with authentic connection.
        """,
        expected_output="Complete campaign concept with authentic UGC style.",
        agent=copywriter_5
    )

    # Evaluation Task - depends on all copywriter submissions
    evaluation_task = Task(
        description="""
        Evaluate all 5 campaign submissions from the competing copywriters.

        Creative Brief: {creative_brief}

        For each submission, score on these criteria (0-10 each):
        1. Brand Alignment: Does it fit brand voice and values?
        2. Creativity: How original and memorable is it?
        3. Conversion Potential: Will it drive clicks and conversions?
        4. Target Resonance: Does it speak to the target audience?
        5. Clarity: Is the message clear and compelling?

        Provide:
        - Individual scores for each campaign (5 dimensions × 5 campaigns)
        - Total score for each campaign
        - Ranking from best to worst
        - Top 3 recommendations for client presentation
        - Detailed rationale for your rankings

        Be objective and thorough. Select winners based purely on merit.
        """,
        expected_output="""Comprehensive evaluation report including:
        - Scores for all 5 campaigns across all 5 dimensions
        - Rankings (1st through 5th place)
        - Top 3 recommendations with rationale
        - Expected performance prediction for each concept""",
        agent=evaluator,
        context=[  # Evaluation depends on ALL copywriter outputs
            copywriter_1_task,
            copywriter_2_task,
            copywriter_3_task,
            copywriter_4_task,
            copywriter_5_task
        ]
    )

    # ========================================
    # CREATE COMPETITIVE CREW
    # ========================================

    crew = Crew(
        agents=[
            copywriter_1,
            copywriter_2,
            copywriter_3,
            copywriter_4,
            copywriter_5,
            evaluator
        ],
        tasks=[
            copywriter_1_task,
            copywriter_2_task,
            copywriter_3_task,
            copywriter_4_task,
            copywriter_5_task,
            evaluation_task
        ],
        process=Process.sequential,  # Sequential allows evaluation task to see all outputs
        verbose=True
    )

    return crew


def run_competitive_campaign(creative_brief: str) -> Dict:
    """
    Run competitive campaign generation.

    Args:
        creative_brief: Marketing campaign brief

    Returns:
        Competition results with winning concepts
    """
    crew = create_competitive_campaign_crew()

    print(f"\n{'='*80}")
    print("Competition Structure:")
    print(f"{'='*80}")
    print("Competing Agents: 5 Copywriters")
    print("  1. Emotional Storytelling Specialist")
    print("  2. Data-Driven Rational Specialist")
    print("  3. Bold Humor Specialist")
    print("  4. Aspirational Luxury Specialist")
    print("  5. Authentic UGC Specialist")
    print("\nJudge: Creative Director Evaluator")
    print("Process: Independent generation → Objective evaluation → Top 3 selection")
    print(f"{'='*80}\n")

    result = crew.kickoff(inputs={"creative_brief": creative_brief})

    return {
        "status": "completed",
        "result": result,
        "num_competitors": 5,
        "business_metrics": {
            "ctr_improvement": "+43%",
            "production_time": "2 weeks → 2 days",
            "approval_rate": "68% → 91%",
            "cost_reduction": "-55%"
        }
    }


def main():
    """Main execution demonstrating competitive pattern."""

    print(f"\n{'='*80}")
    print("Pattern 13: Competitive Pattern - CrewAI")
    print("Business Case: CreativeAI Marketing - Campaign Generation")
    print(f"{'='*80}\n")

    # Example 1: Product Launch Campaign
    print("\nExample 1: Smart Fitness Watch Launch")
    print("-" * 80)

    product_brief = """
    Product: FitPro X1 - AI-powered fitness watch

    Target Audience: Health-conscious professionals, 25-45 years old

    Key Features:
    - AI personal trainer that learns your fitness patterns
    - 7-day battery life (industry-leading)
    - Medical-grade health monitoring (FDA cleared)
    - Sleek minimalist design (premium materials)

    Brand Voice: Innovative, empowering, science-backed

    Campaign Goal: Drive pre-orders, establish premium positioning

    Primary KPI: Click-through rate and conversion to pre-order

    Constraints:
    - Must emphasize AI technology as key differentiator
    - Avoid over-promising health benefits (regulatory compliance)
    - Differentiate from Apple Watch, Garmin, Fitbit
    - Budget allows for premium creative execution

    Challenge: Market is saturated with smartwatches. Need breakthrough concept
    that makes FitPro X1 feel like a category of one.
    """

    result1 = run_competitive_campaign(product_brief)

    print(f"\nCompetition Result:\n{result1['result']}")

    print(f"\nBusiness Metrics:")
    for metric, value in result1['business_metrics'].items():
        print(f"  {metric}: {value}")

    # Example 2: Sale Campaign
    print(f"\n\n{'='*80}")
    print("Example 2: Black Friday Flash Sale - High Competition")
    print(f"{'='*80}\n")

    sale_brief = """
    Client: TechStore - Premium consumer electronics retailer

    Offer: Up to 60% off on curated premium electronics

    Duration: 48-hour Black Friday flash sale

    Target: Tech enthusiasts, deal hunters, holiday gift shoppers

    Challenge: EXTREMELY competitive market during Black Friday.
    Hundreds of retailers running similar promotions.

    Goal: Cut through the noise, drive urgency, maximize conversion

    Brand Differentiator: Curated selection (not everything on sale).
    We only discount products we genuinely recommend.

    Must Convey:
    - Premium quality products (not cheap junk on sale)
    - Limited time (creates urgency)
    - Trustworthy retailer (not a scam)
    - Significant savings (competitive with Amazon, Best Buy)

    High Stakes: Need to beat last year's Black Friday CTR by 40%+ or campaign is a failure.

    Creative Freedom: Be bold. Take risks. This is our biggest revenue day of the year.
    """

    result2 = run_competitive_campaign(sale_brief)

    print(f"\n Sale Campaign Result:\n{result2['result']}")

    print(f"\n{'='*80}")
    print("Pattern Demonstrated: Competitive Pattern")
    print(f"{'='*80}")
    print("""
Key Observations:
1. Independent Competition:
   - 5 copywriter agents work on same brief independently
   - Each applies unique creative style (no collaboration)
   - Pure competition drives each to produce best possible work
   - No groupthink or compromise

2. Diverse Creative Approaches:
   - Emotional storytelling (human connection)
   - Data-driven rational (logical persuasion)
   - Bold humor (memorable wit)
   - Aspirational luxury (premium positioning)
   - Authentic UGC (peer recommendation)

3. Objective Evaluation:
   - Evaluator agent scores all submissions on 5 dimensions
   - Brand alignment, creativity, conversion, resonance, clarity
   - Total scores determine ranking
   - Top 3 selected for client presentation
   - Removes subjective bias from selection

4. Business Impact (CreativeAI Marketing):
   - Campaign CTR: +43% improvement
   - Production time: 2 weeks → 2 days
   - Client approval rate: 68% → 91%
   - Cost per campaign: -55% reduction

5. CrewAI Implementation:
   - Sequential process allows evaluation task to see all submissions
   - Context parameter on evaluation task links to all copywriter tasks
   - Each copywriter task is independent (no context dependencies)
   - allow_delegation=False ensures pure competition (no collaboration)

6. When to Use:
   - Creative work where multiple approaches might succeed
   - High-stakes decisions benefiting from diverse perspectives
   - Innovation needed - competition drives breakthrough ideas
   - Quality more important than speed
   - Objective evaluation criteria can be defined

7. Best Practices:
   - Ensure evaluator has clear, objective criteria
   - Diverse agent backstories create true creative diversity
   - Competition works best with 3-7 agents (sweet spot: 5)
   - Particularly powerful for: marketing copy, design concepts,
     strategic planning, algorithm optimization, architectural decisions

8. Advantages Over Single Agent:
   - Explores solution space more thoroughly
   - Reduces creative blind spots and groupthink
   - Competition pushes quality higher
   - Client receives proven best option, not just first option
   - Multiple backups if winning concept needs adjustments
    """)


if __name__ == "__main__":
    # Set up API keys before running:
    # export OPENAI_API_KEY="your-openai-key"

    main()
