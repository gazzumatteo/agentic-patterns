"""
Exploration and Discovery Pattern - Google ADK Implementation

This pattern demonstrates agents operating in open and complex domains,
generating new hypotheses and solutions through exploration.

Business Use Case: Scientific Research (Cross-functional)
Agent generates new research hypotheses by analyzing unrelated data sources
and discovering hidden patterns and correlations.

Pattern: Exploration and Discovery
Section: IV - Advanced and Learning Patterns
Framework: Google ADK
"""

import asyncio
import json
import random
from typing import Dict, List, Any
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import FunctionTool
from google.genai.types import Content, Part


# --- Constants ---
APP_NAME = "exploration_discovery_app"
USER_ID = "research_user"
MODEL = "gemini-2.5-flash-exp"


# --- Simulated Research Data Sources ---
class ResearchDatabase:
    """Simulates multiple research data sources"""

    def __init__(self):
        # Climate data
        self.climate_data = {
            "temperature_trends": [0.8, 0.9, 1.1, 1.2, 1.3],  # °C increase
            "co2_levels": [380, 390, 400, 410, 420],  # ppm
            "extreme_weather_events": [45, 52, 61, 68, 75]  # annual count
        }

        # Agriculture data
        self.agriculture_data = {
            "crop_yields": [92, 89, 85, 82, 78],  # % of baseline
            "pest_outbreaks": [12, 15, 19, 23, 28],  # incidents per region
            "irrigation_needs": [100, 105, 112, 118, 125]  # % of baseline
        }

        # Economic data
        self.economic_data = {
            "food_prices": [100, 108, 115, 124, 132],  # price index
            "insurance_claims": [2.1, 2.4, 2.9, 3.5, 4.2],  # billions $
            "migration_patterns": [1.2, 1.5, 1.9, 2.4, 3.1]  # millions people
        }

        # Health data
        self.health_data = {
            "heat_related_illness": [1000, 1200, 1500, 1850, 2300],  # cases
            "vector_borne_diseases": [850, 920, 1050, 1200, 1400],  # cases
            "respiratory_issues": [3200, 3450, 3800, 4200, 4650]  # cases
        }


research_db = ResearchDatabase()


# --- Tools ---
def fetch_climate_data() -> str:
    """
    Fetch climate-related research data including temperature trends,
    CO2 levels, and extreme weather events.

    Returns:
        JSON string with climate data
    """
    return json.dumps({
        "domain": "climate_science",
        "data": research_db.climate_data,
        "time_period": "2019-2023",
        "source": "Global Climate Research Institute"
    }, indent=2)


def fetch_agriculture_data() -> str:
    """
    Fetch agricultural data including crop yields, pest outbreaks,
    and irrigation requirements.

    Returns:
        JSON string with agriculture data
    """
    return json.dumps({
        "domain": "agriculture",
        "data": research_db.agriculture_data,
        "time_period": "2019-2023",
        "source": "Agricultural Research Center"
    }, indent=2)


def fetch_economic_data() -> str:
    """
    Fetch economic indicators including food prices, insurance claims,
    and migration patterns.

    Returns:
        JSON string with economic data
    """
    return json.dumps({
        "domain": "economics",
        "data": research_db.economic_data,
        "time_period": "2019-2023",
        "source": "Global Economic Database"
    }, indent=2)


def fetch_health_data() -> str:
    """
    Fetch public health data including heat-related illness,
    vector-borne diseases, and respiratory issues.

    Returns:
        JSON string with health data
    """
    return json.dumps({
        "domain": "public_health",
        "data": research_db.health_data,
        "time_period": "2019-2023",
        "source": "World Health Organization Database"
    }, indent=2)


def calculate_correlation(dataset1_key: str, dataset2_key: str) -> str:
    """
    Calculate correlation coefficient between two datasets.

    Args:
        dataset1_key: Key for first dataset (e.g., "climate.temperature_trends")
        dataset2_key: Key for second dataset (e.g., "agriculture.crop_yields")

    Returns:
        JSON string with correlation analysis
    """
    # Simple correlation calculation
    def get_data(key: str) -> List[float]:
        domain, metric = key.split(".")
        if domain == "climate":
            return research_db.climate_data.get(metric, [])
        elif domain == "agriculture":
            return research_db.agriculture_data.get(metric, [])
        elif domain == "economics":
            return research_db.economic_data.get(metric, [])
        elif domain == "health":
            return research_db.health_data.get(metric, [])
        return []

    data1 = get_data(dataset1_key)
    data2 = get_data(dataset2_key)

    if not data1 or not data2 or len(data1) != len(data2):
        return json.dumps({"error": "Invalid dataset keys or mismatched lengths"})

    # Calculate Pearson correlation
    n = len(data1)
    mean1 = sum(data1) / n
    mean2 = sum(data2) / n

    numerator = sum((data1[i] - mean1) * (data2[i] - mean2) for i in range(n))
    denominator = (
        sum((x - mean1) ** 2 for x in data1) ** 0.5 *
        sum((y - mean2) ** 2 for y in data2) ** 0.5
    )

    correlation = numerator / denominator if denominator != 0 else 0

    return json.dumps({
        "dataset1": dataset1_key,
        "dataset2": dataset2_key,
        "correlation_coefficient": round(correlation, 3),
        "strength": "strong" if abs(correlation) > 0.7 else "moderate" if abs(correlation) > 0.4 else "weak",
        "direction": "positive" if correlation > 0 else "negative"
    }, indent=2)


def generate_hypothesis(findings: str) -> str:
    """
    Generate and record a research hypothesis based on discovered patterns.

    Args:
        findings: Description of discovered patterns and correlations

    Returns:
        Confirmation message with hypothesis ID
    """
    hypothesis_id = f"HYP-{random.randint(1000, 9999)}"
    return f"Hypothesis {hypothesis_id} generated and recorded: {findings}"


# Create FunctionTools
climate_tool = FunctionTool(func=fetch_climate_data)
agriculture_tool = FunctionTool(func=fetch_agriculture_data)
economic_tool = FunctionTool(func=fetch_economic_data)
health_tool = FunctionTool(func=fetch_health_data)
correlation_tool = FunctionTool(func=calculate_correlation)
hypothesis_tool = FunctionTool(func=generate_hypothesis)


# --- Agents ---
# Data Explorers (Parallel) - Each explores a different domain
climate_explorer = LlmAgent(
    model=MODEL,
    name="ClimateExplorer",
    instruction="""You are a Climate Explorer agent. Fetch climate data and
    identify key trends. Store your findings in session state under 'climate_findings'.
    Focus on temperature trends, CO2 levels, and extreme weather patterns.""",
    tools=[climate_tool],
)

agriculture_explorer = LlmAgent(
    model=MODEL,
    name="AgricultureExplorer",
    instruction="""You are an Agriculture Explorer agent. Fetch agriculture data and
    identify key trends. Store your findings in session state under 'agriculture_findings'.
    Focus on crop yield changes, pest outbreaks, and irrigation needs.""",
    tools=[agriculture_tool],
)

economic_explorer = LlmAgent(
    model=MODEL,
    name="EconomicExplorer",
    instruction="""You are an Economic Explorer agent. Fetch economic data and
    identify key trends. Store your findings in session state under 'economic_findings'.
    Focus on food prices, insurance claims, and migration patterns.""",
    tools=[economic_tool],
)

health_explorer = LlmAgent(
    model=MODEL,
    name="HealthExplorer",
    instruction="""You are a Health Explorer agent. Fetch health data and
    identify key trends. Store your findings in session state under 'health_findings'.
    Focus on heat-related illness, vector-borne diseases, and respiratory issues.""",
    tools=[health_tool],
)

# Parallel exploration phase
parallel_explorers = ParallelAgent(
    name="ParallelExplorers",
    sub_agents=[climate_explorer, agriculture_explorer, economic_explorer, health_explorer],
)

# Pattern Discovery Agent
pattern_discoverer = LlmAgent(
    model=MODEL,
    name="PatternDiscoverer",
    instruction="""You are a Pattern Discovery agent. Your role is to:
    1. Review findings from all explorers in session state
    2. Identify at least 3 potential correlations between different domains
    3. Use the correlation tool to calculate correlation coefficients
    4. Store discovered patterns in 'discovered_patterns' in session state

    Look for unexpected connections between climate, agriculture, economics, and health.
    Example correlations to test:
    - climate.temperature_trends vs agriculture.crop_yields
    - climate.co2_levels vs health.respiratory_issues
    - agriculture.pest_outbreaks vs economics.food_prices""",
    tools=[correlation_tool],
)

# Hypothesis Generator Agent
hypothesis_generator = LlmAgent(
    model=MODEL,
    name="HypothesisGenerator",
    instruction="""You are a Hypothesis Generator agent. Your role is to:
    1. Review all discovered patterns and correlations
    2. Generate 2-3 novel research hypotheses that explain the patterns
    3. Each hypothesis should be testable and connect multiple domains
    4. Use the hypothesis tool to formally record each hypothesis
    5. Store hypotheses in 'generated_hypotheses' in session state

    Be creative and look for non-obvious causal relationships.""",
    tools=[hypothesis_tool],
)

# Sequential workflow: Explore → Discover → Hypothesize
discovery_workflow = SequentialAgent(
    name="DiscoveryWorkflow",
    sub_agents=[parallel_explorers, pattern_discoverer, hypothesis_generator],
)


# --- Main Execution ---
async def run_exploration_discovery_demo():
    """Demonstrate exploration and discovery pattern"""
    print("=" * 80)
    print("Exploration and Discovery Pattern - Research Hypothesis Generation")
    print("=" * 80)

    # Initialize services
    session_service = InMemorySessionService()

    # Create runner
    runner = Runner(
        agent=discovery_workflow,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # Create session
    session_id = "discovery_session_001"
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id
    )

    # User message to start discovery
    user_message = Content(
        parts=[Part(text="""Explore multiple research domains and discover hidden patterns
        that could lead to novel research hypotheses. Look for unexpected connections
        between climate, agriculture, economics, and health data.""")],
        role="user"
    )

    print("\n🔬 Objective: Discover hidden patterns across research domains")
    print("📊 Data Sources: Climate, Agriculture, Economics, Public Health")
    print("\n" + "=" * 80)
    print("Starting Discovery Process...")
    print("=" * 80 + "\n")

    # Run the discovery workflow
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=user_message
    ):
        if event.content and event.content.parts:
            text = event.content.parts[0].text
            if text:
                print(f"\n[{event.author}]")
                print(f"{text}")
                print("-" * 80)

    # Final results
    print("\n" + "=" * 80)
    print("Discovery Process Complete!")
    print("=" * 80)

    final_session = await session_service.get_session(APP_NAME, USER_ID, session_id)

    print("\n📈 Discovered Patterns:")
    patterns = final_session.state.get("discovered_patterns", "No patterns recorded")
    print(f"   {patterns}")

    print("\n💡 Generated Hypotheses:")
    hypotheses = final_session.state.get("generated_hypotheses", "No hypotheses recorded")
    print(f"   {hypotheses}")

    print("\n✅ Exploration and Discovery Pattern demonstrated successfully!")
    print("   Multiple domains explored in parallel, patterns discovered,")
    print("   and novel research hypotheses generated.")


if __name__ == "__main__":
    asyncio.run(run_exploration_discovery_demo())
