"""
Exploration and Discovery Pattern - CrewAI Implementation

This pattern demonstrates agents operating in open and complex domains,
generating new hypotheses and solutions through exploration.

Business Use Case: Scientific Research (Cross-functional)
Agent generates new research hypotheses by analyzing unrelated data sources
and discovering hidden patterns and correlations.

Pattern: Exploration and Discovery
Section: IV - Advanced and Learning Patterns
Framework: CrewAI
"""

import json
import random
from typing import Dict, List, Any
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


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


# --- Custom Tools ---
class FetchClimateDataTool(BaseTool):
    name: str = "fetch_climate_data"
    description: str = "Fetch climate-related research data including temperature trends, CO2 levels, and extreme weather events"

    def _run(self) -> str:
        """Fetch climate data"""
        return json.dumps({
            "domain": "climate_science",
            "data": research_db.climate_data,
            "time_period": "2019-2023",
            "source": "Global Climate Research Institute"
        }, indent=2)


class FetchAgricultureDataTool(BaseTool):
    name: str = "fetch_agriculture_data"
    description: str = "Fetch agricultural data including crop yields, pest outbreaks, and irrigation requirements"

    def _run(self) -> str:
        """Fetch agriculture data"""
        return json.dumps({
            "domain": "agriculture",
            "data": research_db.agriculture_data,
            "time_period": "2019-2023",
            "source": "Agricultural Research Center"
        }, indent=2)


class FetchEconomicDataTool(BaseTool):
    name: str = "fetch_economic_data"
    description: str = "Fetch economic indicators including food prices, insurance claims, and migration patterns"

    def _run(self) -> str:
        """Fetch economic data"""
        return json.dumps({
            "domain": "economics",
            "data": research_db.economic_data,
            "time_period": "2019-2023",
            "source": "Global Economic Database"
        }, indent=2)


class FetchHealthDataTool(BaseTool):
    name: str = "fetch_health_data"
    description: str = "Fetch public health data including heat-related illness, vector-borne diseases, and respiratory issues"

    def _run(self) -> str:
        """Fetch health data"""
        return json.dumps({
            "domain": "public_health",
            "data": research_db.health_data,
            "time_period": "2019-2023",
            "source": "World Health Organization Database"
        }, indent=2)


class CalculateCorrelationInput(BaseModel):
    """Input schema for calculate_correlation tool"""
    dataset1_key: str = Field(..., description="Key for first dataset (e.g., 'climate.temperature_trends')")
    dataset2_key: str = Field(..., description="Key for second dataset (e.g., 'agriculture.crop_yields')")


class CalculateCorrelationTool(BaseTool):
    name: str = "calculate_correlation"
    description: str = "Calculate correlation coefficient between two datasets from different domains"

    def _run(self, dataset1_key: str, dataset2_key: str) -> str:
        """Calculate correlation between two datasets"""
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


class GenerateHypothesisInput(BaseModel):
    """Input schema for generate_hypothesis tool"""
    findings: str = Field(..., description="Description of discovered patterns and correlations")


class GenerateHypothesisTool(BaseTool):
    name: str = "generate_hypothesis"
    description: str = "Generate and record a research hypothesis based on discovered patterns"

    def _run(self, findings: str) -> str:
        """Generate and record hypothesis"""
        hypothesis_id = f"HYP-{random.randint(1000, 9999)}"
        return f"Hypothesis {hypothesis_id} generated and recorded: {findings}"


# Initialize tools
climate_tool = FetchClimateDataTool()
agriculture_tool = FetchAgricultureDataTool()
economic_tool = FetchEconomicDataTool()
health_tool = FetchHealthDataTool()
correlation_tool = CalculateCorrelationTool()
hypothesis_tool = GenerateHypothesisTool()


# --- Agents ---
def create_climate_explorer() -> Agent:
    """Create Climate Explorer agent"""
    return Agent(
        role="Climate Data Explorer",
        goal="Explore climate data and identify key trends in temperature, CO2, and weather patterns",
        backstory="""You are a Climate Science researcher specializing in climate
        change data analysis. You explore climate datasets to identify significant
        trends and patterns in temperature changes, greenhouse gas levels, and
        extreme weather events.""",
        tools=[climate_tool],
        verbose=True,
        allow_delegation=False
    )


def create_agriculture_explorer() -> Agent:
    """Create Agriculture Explorer agent"""
    return Agent(
        role="Agriculture Data Explorer",
        goal="Explore agricultural data and identify trends in crop yields, pest outbreaks, and irrigation",
        backstory="""You are an Agricultural Research specialist focused on
        understanding farming trends and challenges. You analyze data on crop
        performance, pest management, and water resource needs.""",
        tools=[agriculture_tool],
        verbose=True,
        allow_delegation=False
    )


def create_economic_explorer() -> Agent:
    """Create Economic Explorer agent"""
    return Agent(
        role="Economic Data Explorer",
        goal="Explore economic indicators related to food prices, insurance, and migration",
        backstory="""You are an Economic Analyst specializing in agricultural
        economics and climate-related economic impacts. You track food price
        trends, insurance claims, and population migration patterns.""",
        tools=[economic_tool],
        verbose=True,
        allow_delegation=False
    )


def create_health_explorer() -> Agent:
    """Create Health Explorer agent"""
    return Agent(
        role="Public Health Data Explorer",
        goal="Explore health data trends in heat illness, diseases, and respiratory issues",
        backstory="""You are a Public Health researcher studying environmental
        health impacts. You analyze data on heat-related illnesses, vector-borne
        diseases, and respiratory health conditions.""",
        tools=[health_tool],
        verbose=True,
        allow_delegation=False
    )


def create_pattern_discoverer() -> Agent:
    """Create Pattern Discoverer agent"""
    return Agent(
        role="Cross-Domain Pattern Discoverer",
        goal="Discover hidden correlations and patterns across different research domains",
        backstory="""You are an interdisciplinary researcher with expertise in
        systems thinking and data science. You excel at finding unexpected
        connections between seemingly unrelated datasets from climate, agriculture,
        economics, and health domains. You use statistical methods to validate
        discovered patterns.""",
        tools=[correlation_tool],
        verbose=True,
        allow_delegation=False
    )


def create_hypothesis_generator() -> Agent:
    """Create Hypothesis Generator agent"""
    return Agent(
        role="Research Hypothesis Generator",
        goal="Generate novel, testable research hypotheses based on discovered patterns",
        backstory="""You are a creative research scientist who excels at
        formulating innovative hypotheses that explain observed patterns. You
        generate hypotheses that connect multiple domains and propose causal
        relationships that can be tested through further research.""",
        tools=[hypothesis_tool],
        verbose=True,
        allow_delegation=False
    )


# --- Tasks ---
def create_exploration_tasks() -> List[Task]:
    """Create parallel exploration tasks for each domain"""
    climate_explorer = create_climate_explorer()
    agriculture_explorer = create_agriculture_explorer()
    economic_explorer = create_economic_explorer()
    health_explorer = create_health_explorer()

    climate_task = Task(
        description="""Explore climate science data and identify key trends:
        1. Fetch climate data using fetch_climate_data
        2. Analyze temperature trends over the 2019-2023 period
        3. Examine CO2 level changes
        4. Identify patterns in extreme weather events
        5. Summarize the most significant climate trends observed""",
        agent=climate_explorer,
        expected_output="Summary of key climate trends including temperature, CO2, and extreme weather patterns"
    )

    agriculture_task = Task(
        description="""Explore agricultural data and identify key trends:
        1. Fetch agriculture data using fetch_agriculture_data
        2. Analyze crop yield changes over time
        3. Examine pest outbreak trends
        4. Review irrigation needs evolution
        5. Summarize the most significant agricultural challenges observed""",
        agent=agriculture_explorer,
        expected_output="Summary of agricultural trends including crop yields, pest outbreaks, and irrigation needs"
    )

    economic_task = Task(
        description="""Explore economic indicators and identify key trends:
        1. Fetch economic data using fetch_economic_data
        2. Analyze food price index changes
        3. Examine insurance claims trends
        4. Review migration pattern evolution
        5. Summarize the most significant economic impacts observed""",
        agent=economic_explorer,
        expected_output="Summary of economic trends including food prices, insurance claims, and migration patterns"
    )

    health_task = Task(
        description="""Explore public health data and identify key trends:
        1. Fetch health data using fetch_health_data
        2. Analyze heat-related illness trends
        3. Examine vector-borne disease patterns
        4. Review respiratory issue evolution
        5. Summarize the most significant health trends observed""",
        agent=health_explorer,
        expected_output="Summary of health trends including heat illness, diseases, and respiratory issues"
    )

    return [climate_task, agriculture_task, economic_task, health_task]


def create_discovery_task() -> Task:
    """Create pattern discovery task"""
    discoverer = create_pattern_discoverer()

    return Task(
        description="""Based on all exploration findings, discover hidden patterns:
        1. Identify at least 3 potential correlations between different domains
        2. Use calculate_correlation to test these correlations:
           - climate.temperature_trends vs agriculture.crop_yields
           - climate.co2_levels vs health.respiratory_issues
           - agriculture.pest_outbreaks vs economics.food_prices
           - climate.extreme_weather_events vs economics.insurance_claims
        3. Document correlation strengths and directions
        4. Identify the most significant cross-domain patterns

        Focus on unexpected connections that might reveal causal relationships.""",
        agent=discoverer,
        expected_output="List of discovered correlations with strength metrics and analysis of cross-domain patterns",
        context=create_exploration_tasks()
    )


def create_hypothesis_task() -> Task:
    """Create hypothesis generation task"""
    generator = create_hypothesis_generator()

    return Task(
        description="""Generate novel research hypotheses based on discovered patterns:
        1. Review all discovered correlations and patterns
        2. Generate 2-3 testable hypotheses that explain the patterns
        3. Each hypothesis should:
           - Connect multiple domains (climate, agriculture, economics, health)
           - Propose a causal mechanism
           - Be testable through further research
        4. Use generate_hypothesis to formally record each hypothesis

        Be creative and look for non-obvious causal relationships.
        Consider both direct and indirect effects.""",
        agent=generator,
        expected_output="2-3 novel research hypotheses with IDs, explaining cross-domain causal relationships",
        context=[create_discovery_task()]
    )


# --- Main Execution ---
def run_exploration_discovery_demo():
    """Demonstrate exploration and discovery pattern"""
    print("=" * 80)
    print("Exploration and Discovery Pattern - Research Hypothesis Generation")
    print("=" * 80)

    print("\nObjective: Discover hidden patterns across research domains")
    print("Data Sources: Climate, Agriculture, Economics, Public Health")
    print(f"\n{'=' * 80}")
    print("Starting Discovery Process...")
    print(f"{'=' * 80}\n")

    # Create all agents
    climate_explorer = create_climate_explorer()
    agriculture_explorer = create_agriculture_explorer()
    economic_explorer = create_economic_explorer()
    health_explorer = create_health_explorer()
    pattern_discoverer = create_pattern_discoverer()
    hypothesis_generator = create_hypothesis_generator()

    # Create all tasks
    exploration_tasks = create_exploration_tasks()
    discovery_task = create_discovery_task()
    hypothesis_task = create_hypothesis_task()

    # Combine all tasks
    all_tasks = exploration_tasks + [discovery_task, hypothesis_task]

    # Create crew with sequential process
    # Note: In CrewAI, even with sequential process, tasks with context dependency
    # will wait for their context tasks to complete
    crew = Crew(
        agents=[
            climate_explorer,
            agriculture_explorer,
            economic_explorer,
            health_explorer,
            pattern_discoverer,
            hypothesis_generator
        ],
        tasks=all_tasks,
        process=Process.sequential,
        verbose=True
    )

    # Execute the crew
    try:
        result = crew.kickoff()
        print(f"\n{'=' * 80}")
        print("Discovery Process Complete!")
        print(f"{'=' * 80}")
        print("\n[Final Result]")
        print(result)
    except Exception as e:
        print(f"\n[Error during discovery]: {e}")
        return

    print("\nExploration and Discovery Pattern demonstrated successfully!")
    print("Multiple domains explored, patterns discovered, and novel hypotheses generated.")


if __name__ == "__main__":
    run_exploration_discovery_demo()
