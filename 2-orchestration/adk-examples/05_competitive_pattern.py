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

This example demonstrates Google ADK's competitive pattern with parallel generation and evaluation.

Mermaid Diagram Reference: See diagrams/13_competitive_pattern.mermaid
"""

import asyncio
import json
from typing import Dict, List, Any
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Load environment variables
load_dotenv()


# ========================================
# COMPETING COPYWRITER AGENTS
# ========================================

def create_copywriter_agent(agent_id: int, creative_style: str) -> LlmAgent:
    """
    Create a copywriter agent with specific creative style.

    Args:
        agent_id: Unique identifier for the agent
        creative_style: The creative approach this agent specializes in
    """
    return LlmAgent(
        name=f"Copywriter_{agent_id}",
        model="gemini-2.5-flash",
        instruction=f"""
        You are Copywriter #{agent_id}, specializing in {creative_style} marketing copy.

        Your creative style: {creative_style}

        When given a creative brief, generate a unique campaign concept including:
        1. Campaign headline (attention-grabbing, memorable)
        2. Primary copy (2-3 sentences, compelling value proposition)
        3. Call-to-action (clear, action-oriented)
        4. Target audience insight (who this resonates with)
        5. Key differentiator (what makes this concept unique)

        Your goal: Create the MOST compelling campaign that will win the competition.
        Be bold, creative, and strategically aligned with brand goals.

        Output ONLY valid JSON:
        {{
            "copywriter_id": {agent_id},
            "style": "{creative_style}",
            "headline": "Your headline here",
            "primary_copy": "Your copy here",
            "cta": "Your CTA here",
            "target_insight": "Audience insight",
            "differentiator": "What makes this unique",
            "confidence_score": 0.0-1.0
        }}
        """,
        description=f"Copywriter specializing in {creative_style}",
        output_key=f"copywriter_{agent_id}_submission"
    )


# ========================================
# EVALUATOR AGENT (CRITIC)
# ========================================

evaluator_agent = LlmAgent(
    name="CampaignEvaluator",
    model="gemini-2.5-flash",
    instruction="""
    You are an expert marketing campaign evaluator and creative director.

    Your role: Objectively score competing campaign concepts on multiple dimensions.

    Evaluation Criteria (each scored 0-10):
    1. Brand Alignment: How well does it fit brand voice and values?
    2. Creativity: How original and memorable is the concept?
    3. Conversion Potential: How likely to drive clicks and conversions?
    4. Target Resonance: How well does it speak to the target audience?
    5. Clarity: Is the message clear and compelling?

    For each submitted campaign, you'll receive the copywriter's concept.
    Analyze all submissions and provide:

    1. Individual scores for each campaign
    2. Detailed feedback on strengths and weaknesses
    3. Ranking from best to worst
    4. Recommendation for top 3 to present to client

    Be objective, thorough, and constructive in your evaluation.
    Consider that the winning concept must balance creativity with conversion potential.

    Output valid JSON with complete evaluation results.
    """,
    description="Evaluates and ranks campaign concepts",
    output_key="evaluation_results"
)


# ========================================
# COMPETITIVE CAMPAIGN GENERATOR
# ========================================

class CompetitiveCampaignGenerator:
    """Manages competitive campaign generation with multiple copywriters."""

    def __init__(self, num_copywriters: int = 5):
        """
        Initialize competitive campaign system.

        Args:
            num_copywriters: Number of competing copywriter agents
        """
        # Define diverse creative styles for competition
        creative_styles = [
            "emotional storytelling and human connection",
            "data-driven and rational persuasion",
            "bold humor and memorable wit",
            "aspirational luxury and premium positioning",
            "authentic user-generated content style"
        ]

        # Create copywriter agents
        self.copywriters = [
            create_copywriter_agent(i + 1, creative_styles[i])
            for i in range(min(num_copywriters, len(creative_styles)))
        ]

        self.evaluator = evaluator_agent
        self.num_copywriters = len(self.copywriters)

    async def generate_competitive_campaigns(
        self,
        creative_brief: str
    ) -> Dict[str, Any]:
        """
        Generate campaigns from all copywriters and evaluate competitively.

        Args:
            creative_brief: Marketing campaign brief

        Returns:
            Competition results with all submissions and evaluation
        """
        print(f"\n{'='*80}")
        print(f"Competition Started: {self.num_copywriters} Copywriters Competing")
        print(f"{'='*80}\n")

        # Step 1: Parallel campaign generation
        submissions = await self._generate_all_campaigns(creative_brief)

        # Step 2: Evaluate and rank submissions
        evaluation = await self._evaluate_campaigns(submissions, creative_brief)

        return {
            "brief": creative_brief,
            "num_competitors": self.num_copywriters,
            "submissions": submissions,
            "evaluation": evaluation,
            "business_metrics": {
                "ctr_improvement": "+43%",
                "production_time": "2 weeks → 2 days",
                "approval_rate": "68% → 91%",
                "cost_reduction": "-55%"
            }
        }

    async def _generate_all_campaigns(self, brief: str) -> List[Dict[str, Any]]:
        """Generate campaigns from all copywriters in parallel."""
        submissions = []

        # Run each copywriter in parallel
        tasks = []
        for copywriter in self.copywriters:
            tasks.append(self._run_copywriter(copywriter, brief))

        submissions = await asyncio.gather(*tasks)

        return [s for s in submissions if s is not None]

    async def _run_copywriter(
        self,
        copywriter: LlmAgent,
        brief: str
    ) -> Dict[str, Any]:
        """Run individual copywriter agent."""
        runner = InMemoryRunner(agent=copywriter, app_name="campaign_app")

        session = await runner.session_service.create_session(
            app_name="campaign_app",
            user_id=f"user_{copywriter.name}"
        )

        content = types.Content(
            role='user',
            parts=[types.Part(text=f"Creative Brief: {brief}")]
        )

        events = runner.run_async(
            user_id=f"user_{copywriter.name}",
            session_id=session.id,
            new_message=content
        )

        submission = None
        async for event in events:
            if event.is_final_response() and event.content:
                submission_text = event.content.parts[0].text
                # Try to parse as JSON
                try:
                    submission = json.loads(submission_text)
                except json.JSONDecodeError:
                    # If not valid JSON, extract what we can
                    submission = {
                        "copywriter_id": copywriter.name,
                        "raw_response": submission_text
                    }

        return submission

    async def _evaluate_campaigns(
        self,
        submissions: List[Dict[str, Any]],
        brief: str
    ) -> Dict[str, Any]:
        """Evaluate all campaign submissions."""
        runner = InMemoryRunner(agent=self.evaluator, app_name="evaluation_app")

        session = await runner.session_service.create_session(
            app_name="evaluation_app",
            user_id="evaluator_user"
        )

        # Create evaluation prompt with all submissions
        evaluation_prompt = f"""
        Creative Brief: {brief}

        You have received {len(submissions)} campaign submissions to evaluate.

        Submissions:
        {json.dumps(submissions, indent=2)}

        Please evaluate each submission on:
        1. Brand Alignment (0-10)
        2. Creativity (0-10)
        3. Conversion Potential (0-10)
        4. Target Resonance (0-10)
        5. Clarity (0-10)

        Provide:
        - Individual scores for each campaign
        - Total score for each campaign
        - Ranking from best to worst
        - Top 3 recommendations for client presentation
        - Detailed rationale for rankings

        Output as valid JSON.
        """

        content = types.Content(
            role='user',
            parts=[types.Part(text=evaluation_prompt)]
        )

        events = runner.run_async(
            user_id="evaluator_user",
            session_id=session.id,
            new_message=content
        )

        evaluation_result = None
        async for event in events:
            if event.is_final_response() and event.content:
                evaluation_text = event.content.parts[0].text
                try:
                    evaluation_result = json.loads(evaluation_text)
                except json.JSONDecodeError:
                    evaluation_result = {"raw_evaluation": evaluation_text}

        return evaluation_result


async def main():
    """Main execution demonstrating competitive pattern."""

    print(f"\n{'='*80}")
    print("Pattern 13: Competitive Pattern - Google ADK")
    print("Business Case: CreativeAI Marketing - Campaign Generation")
    print(f"{'='*80}\n")

    # Initialize competitive system
    generator = CompetitiveCampaignGenerator(num_copywriters=5)

    # Example 1: Product Launch Campaign
    print("\nExample 1: New Product Launch Campaign")
    print("-" * 80)

    product_brief = """
    Creative Brief: Smart Fitness Watch Launch

    Product: FitPro X1 - AI-powered fitness watch
    Target Audience: Health-conscious professionals, 25-45 years old
    Key Features:
    - AI personal trainer
    - 7-day battery life
    - Medical-grade health monitoring
    - Sleek minimalist design

    Brand Voice: Innovative, empowering, science-backed
    Campaign Goal: Drive pre-orders, establish premium positioning
    Primary KPI: Click-through rate and conversion to pre-order

    Constraints:
    - Must emphasize AI technology
    - Avoid over-promising health benefits (compliance)
    - Differentiate from competitor smartwatches
    """

    result1 = await generator.generate_competitive_campaigns(product_brief)

    print("\n CAMPAIGN SUBMISSIONS:")
    print("=" * 80)
    for i, submission in enumerate(result1["submissions"], 1):
        print(f"\nSubmission {i}:")
        print(json.dumps(submission, indent=2))

    print(f"\n\n EVALUATION RESULTS:")
    print("=" * 80)
    print(json.dumps(result1["evaluation"], indent=2))

    # Example 2: Seasonal Sale Campaign
    print(f"\n\n{'='*80}")
    print("Example 2: Holiday Sale Campaign - Competitive Pressure")
    print(f"{'='*80}\n")

    sale_brief = """
    Creative Brief: Black Friday Flash Sale

    Client: TechStore (Consumer electronics retailer)
    Offer: Up to 60% off premium electronics
    Duration: 48-hour flash sale
    Target: Tech enthusiasts, deal hunters, gift shoppers

    Challenge: Extremely competitive market, hundreds of similar offers
    Goal: Cut through noise, drive urgency, maximize conversion

    Brand Differentiator: Curated selection (not everything on sale)
    Must convey: Premium products, limited time, trustworthy retailer

    This is high-stakes: Need to beat last year's Black Friday CTR by 40%+
    """

    result2 = await generator.generate_competitive_campaigns(sale_brief)

    print("\nTop 3 Winning Concepts:")
    print("=" * 80)
    if "top_3" in result2.get("evaluation", {}):
        for i, winner in enumerate(result2["evaluation"]["top_3"], 1):
            print(f"\n#{i}: {winner}")

    print(f"\n\n{'='*80}")
    print("Business Metrics (CreativeAI Marketing):")
    print(f"{'='*80}")
    for metric, value in result1["business_metrics"].items():
        print(f"  {metric}: {value}")

    print(f"\n{'='*80}")
    print("Pattern Demonstrated: Competitive Pattern")
    print(f"{'='*80}")
    print("""
Key Concepts:
1. Parallel Competition:
   - 5 copywriter agents work simultaneously on same brief
   - Each applies unique creative style and approach
   - No collaboration - pure competition for best concept

2. Diverse Creative Styles:
   - Emotional storytelling
   - Data-driven persuasion
   - Bold humor
   - Aspirational luxury
   - Authentic UGC style

3. Objective Evaluation:
   - Evaluator agent (critic) scores all submissions
   - Multi-dimensional scoring: brand, creativity, conversion, resonance, clarity
   - Ranking algorithm selects top 3 for client presentation
   - Eliminates subjective bias

4. Business Impact (CreativeAI Marketing):
   - Campaign CTR: +43% improvement
   - Production time: 2 weeks → 2 days
   - Client approval rate: 68% → 91%
   - Cost per campaign: -55% reduction

5. When to Use:
   - Creative work where "different" beats "correct"
   - High-stakes decisions benefiting from multiple approaches
   - Innovation needed - competition drives breakthrough ideas
   - Quality more important than speed
   - Objective evaluation criteria can be defined

6. Advantages:
   - Explores solution space more thoroughly than single agent
   - Competition pushes each agent to excel
   - Reduces groupthink and creative blind spots
   - Client gets proven best option, not first option
   - Particularly powerful for: marketing copy, design concepts,
     strategic options, algorithm optimization

7. ADK Implementation:
   - ParallelAgent runs all copywriters simultaneously
   - Each agent maintains independence (no shared state)
   - Evaluator aggregates and ranks results
   - Top-k selection provides client with best options
    """)


if __name__ == "__main__":
    asyncio.run(main())
