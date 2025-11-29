"""
Pattern 32: Evolutionary Curriculum Agent
Population-based evolution of agent strategies where multiple variants compete,
successful traits propagate, and optimal solutions emerge.

Business Example: Algorithm Optimization (Trading Firm)
- 1,000 trading algorithm variants created
- Each trades in simulated market
- Top 10% become parents for next generation
- Result: Sharpe ratio 1.2 → 2.8, drawdown -15% → -7%

This example demonstrates CrewAI's competitive process for evolutionary
optimization with role-based evolution agents.

Mermaid Diagram Reference: See diagrams/32_evolutionary_curriculum.mermaid
"""

import json
import random
from typing import Any, Dict, List
from dataclasses import dataclass, asdict
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool


@dataclass
class StrategyGenome:
    """Agent strategy genome."""
    risk_tolerance: float
    momentum_weight: float
    mean_reversion_weight: float
    volatility_threshold: float
    position_size_factor: float
    generation: int = 0
    fitness: float = 0.0
    id: str = ""


class EvolutionManager:
    """Manages evolutionary process."""

    def __init__(self, population_size: int = 30):
        self.population_size = population_size
        self.population: List[StrategyGenome] = []
        self.generation = 0
        self.evolution_history: List[Dict] = []

    def initialize_population(self) -> List[StrategyGenome]:
        """Create initial random population."""
        self.population = []
        for i in range(self.population_size):
            genome = StrategyGenome(
                risk_tolerance=random.random(),
                momentum_weight=random.random(),
                mean_reversion_weight=random.random(),
                volatility_threshold=random.random(),
                position_size_factor=random.random() * 0.9 + 0.1,
                id=f"gen0_strat{i}"
            )
            self.population.append(genome)
        return self.population

    def evaluate_fitness(self, genome: StrategyGenome) -> float:
        """Evaluate strategy fitness."""
        returns = []
        portfolio = 100000

        for _ in range(100):
            market_move = random.gauss(0, 0.02)

            if abs(market_move) > genome.volatility_threshold:
                signal = -market_move * genome.mean_reversion_weight
            else:
                signal = market_move * genome.momentum_weight

            signal *= genome.risk_tolerance
            period_return = signal * market_move
            portfolio *= (1 + period_return)
            returns.append(period_return)

        avg_return = sum(returns) / len(returns)
        std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
        sharpe = (avg_return / std_return) if std_return > 0 else 0

        peak = portfolio
        max_dd = 0
        for i, ret in enumerate(returns):
            val = 100000 * (1 + sum(returns[:i+1]))
            peak = max(peak, val)
            dd = (peak - val) / peak
            max_dd = max(max_dd, dd)

        fitness = sharpe * 100 - max_dd * 50
        return max(0, fitness)

    def select_and_evolve(self) -> Dict[str, Any]:
        """Select best and create next generation."""
        self.generation += 1

        # Evaluate all
        for genome in self.population:
            genome.fitness = self.evaluate_fitness(genome)

        # Sort by fitness
        sorted_pop = sorted(self.population, key=lambda g: g.fitness, reverse=True)

        # Elite (top 20%)
        elite_count = max(2, int(self.population_size * 0.2))
        elite = sorted_pop[:elite_count]

        # Create new generation
        new_pop = elite.copy()

        while len(new_pop) < self.population_size:
            # Select parents
            p1, p2 = random.sample(elite, 2)

            # Crossover
            child_dict = {}
            for attr in ['risk_tolerance', 'momentum_weight', 'mean_reversion_weight',
                        'volatility_threshold', 'position_size_factor']:
                child_dict[attr] = getattr(p1, attr) if random.random() < 0.5 else getattr(p2, attr)

                # Mutate
                if random.random() < 0.1:
                    child_dict[attr] += random.gauss(0, 0.1)
                    if attr == 'position_size_factor':
                        child_dict[attr] = max(0.1, min(1.0, child_dict[attr]))
                    else:
                        child_dict[attr] = max(0.0, min(1.0, child_dict[attr]))

            child = StrategyGenome(**child_dict, generation=self.generation, id=f"gen{self.generation}_strat{len(new_pop)}")
            new_pop.append(child)

        self.population = new_pop

        stats = {
            "generation": self.generation,
            "best_fitness": elite[0].fitness,
            "avg_fitness": sum(g.fitness for g in self.population) / len(self.population),
            "best_genome": asdict(elite[0])
        }

        self.evolution_history.append(stats)
        return stats


# Global evolution manager
evolution_mgr = EvolutionManager(population_size=30)


@tool("Initialize population")
def initialize_evolution_population(population_size: int) -> str:
    """Initialize population of strategy genomes."""
    evolution_mgr.population_size = population_size
    population = evolution_mgr.initialize_population()

    return json.dumps({
        "population_size": len(population),
        "sample_genomes": [asdict(g) for g in population[:3]],
        "message": f"Initialized {len(population)} strategy variants"
    }, indent=2)


@tool("Evolve generation")
def evolve_next_generation() -> str:
    """Run one generation of evolution (selection, crossover, mutation)."""
    stats = evolution_mgr.select_and_evolve()

    return json.dumps({
        "generation": stats["generation"],
        "best_fitness": round(stats["best_fitness"], 2),
        "avg_fitness": round(stats["avg_fitness"], 2),
        "improvement": round(stats["best_fitness"] - evolution_mgr.evolution_history[0]["best_fitness"], 2) if len(evolution_mgr.evolution_history) > 1 else 0,
        "best_strategy": {
            k: round(v, 3) if isinstance(v, float) else v
            for k, v in stats["best_genome"].items()
        }
    }, indent=2)


@tool("Get evolution summary")
def get_evolution_summary() -> str:
    """Get summary of evolutionary progress."""
    if not evolution_mgr.evolution_history:
        return json.dumps({"error": "No evolution history"})

    initial = evolution_mgr.evolution_history[0]
    latest = evolution_mgr.evolution_history[-1]
    improvement = ((latest["best_fitness"] - initial["best_fitness"]) / initial["best_fitness"] * 100) if initial["best_fitness"] > 0 else 0

    return json.dumps({
        "total_generations": len(evolution_mgr.evolution_history),
        "initial_best_fitness": round(initial["best_fitness"], 2),
        "final_best_fitness": round(latest["best_fitness"], 2),
        "improvement_percent": round(improvement, 1),
        "convergence_trend": "improving" if improvement > 0 else "stable",
        "best_strategy": latest["best_genome"]
    }, indent=2)


def create_evolution_crew() -> Crew:
    """Create crew for evolutionary optimization."""

    # Population manager
    population_manager = Agent(
        role="Population Manager",
        goal="Manage evolution population and ensure diversity",
        backstory="""You manage populations of strategy variants. You initialize
        diverse populations and ensure genetic diversity throughout evolution.
        You understand the importance of exploration vs exploitation.""",
        tools=[initialize_evolution_population],
        verbose=True
    )

    # Evolution engine
    evolution_engine = Agent(
        role="Evolution Engine",
        goal="Execute evolutionary cycles with selection, crossover, and mutation",
        backstory="""You are the core evolution engine. You evaluate fitness,
        select top performers, perform crossover between parents, and apply
        mutations. You drive the optimization process through natural selection.""",
        tools=[evolve_next_generation],
        verbose=True
    )

    # Strategy analyzer
    strategy_analyzer = Agent(
        role="Strategy Performance Analyzer",
        goal="Analyze evolved strategies and identify winning patterns",
        backstory="""You analyze evolved strategies to understand what makes
        them successful. You identify patterns in genetic traits, track
        convergence, and explain why certain strategies outperform others.""",
        tools=[get_evolution_summary],
        verbose=True
    )

    return Crew(
        agents=[population_manager, evolution_engine, strategy_analyzer],
        tasks=[],
        process=Process.sequential,
        verbose=True
    )


def run_evolution_experiment(crew: Crew, num_generations: int = 10):
    """Run complete evolution experiment."""

    print(f"\n{'='*80}")
    print(f"EVOLUTIONARY OPTIMIZATION EXPERIMENT")
    print(f"Generations: {num_generations}")
    print(f"{'='*80}")

    # Initialize
    init_task = Task(
        description="""
        Initialize a population of 30 trading strategy variants.

        Each strategy has genetic parameters:
        - Risk tolerance
        - Momentum weight
        - Mean reversion weight
        - Volatility threshold
        - Position size factor

        Create a diverse initial population for evolution.
        """,
        agent=crew.agents[0],
        expected_output="Population initialization summary with sample genomes"
    )

    crew.tasks = [init_task]
    init_result = crew.kickoff()
    print(f"\n✓ Population Initialized\n{init_result}")

    # Evolution loop
    for gen in range(1, num_generations + 1):
        evolution_task = Task(
            description=f"""
            Execute generation {gen} of evolutionary optimization:

            1. Evaluate fitness of all strategies in population
            2. Select top 20% as elite (parents)
            3. Create offspring through crossover
            4. Apply mutations (10% mutation rate)
            5. Form new generation

            Report:
            - Best fitness achieved
            - Average population fitness
            - Improvement from generation 1
            - Best strategy parameters
            """,
            agent=crew.agents[1],
            expected_output=f"Generation {gen} evolution results with fitness metrics"
        )

        crew.tasks = [evolution_task]
        result = crew.kickoff()
        print(f"\n--- Generation {gen} Complete ---")
        print(result)

        # Analysis every 5 generations
        if gen % 5 == 0 or gen == num_generations:
            analysis_task = Task(
                description=f"""
                Analyze evolutionary progress after {gen} generations:

                1. Compare initial vs current best fitness
                2. Calculate improvement percentage
                3. Identify patterns in successful strategies
                4. Assess convergence trend
                5. Recommend if more generations needed

                Provide actionable insights on the evolution process.
                """,
                agent=crew.agents[2],
                expected_output=f"Analysis of evolution progress through generation {gen}"
            )

            crew.tasks = [analysis_task]
            analysis = crew.kickoff()
            print(f"\n💡 Evolution Analysis (Gen {gen}):")
            print(analysis)

    return evolution_mgr.evolution_history


def main():
    """Main execution demonstrating evolutionary optimization."""

    print("=" * 80)
    print("Pattern 32: Evolutionary Curriculum Agent (CrewAI)")
    print("Competitive Evolution of Trading Strategies")
    print("=" * 80)

    crew = create_evolution_crew()
    history = run_evolution_experiment(crew, num_generations=12)

    print("\n\n" + "=" * 80)
    print("FINAL EVOLUTION RESULTS")
    print("=" * 80)

    if history:
        initial = history[0]
        final = history[-1]
        improvement = ((final["best_fitness"] - initial["best_fitness"]) / initial["best_fitness"] * 100) if initial["best_fitness"] > 0 else 0

        print(f"\n📊 Performance:")
        print(f"   Initial Best Fitness: {initial['best_fitness']:.2f}")
        print(f"   Final Best Fitness: {final['best_fitness']:.2f}")
        print(f"   Improvement: {improvement:.1f}%")

        print(f"\n🏆 Best Evolved Strategy:")
        best = final["best_genome"]
        print(f"   Risk Tolerance: {best['risk_tolerance']:.3f}")
        print(f"   Momentum Weight: {best['momentum_weight']:.3f}")
        print(f"   Mean Reversion: {best['mean_reversion_weight']:.3f}")
        print(f"   Volatility Threshold: {best['volatility_threshold']:.3f}")
        print(f"   Position Size: {best['position_size_factor']:.3f}")

    print("\n" + "=" * 80)
    print("Pattern Demonstrated: Evolutionary Curriculum Agent")
    print("=" * 80)
    print("""
    Key Observations:
    1. Role Specialization: Population manager, evolution engine, analyzer
    2. Natural Selection: Top performers breed next generation
    3. Genetic Operators: Crossover and mutation create variants
    4. Fitness-Based: Performance drives selection
    5. Emergent Solutions: Optimal strategies evolve naturally

    CrewAI Advantages:
    - Clear role-based evolution agents
    - Natural workflow for evolutionary cycles
    - Easy to understand and modify
    - Built-in memory for tracking progress
    - Scalable to different optimization problems

    Business Impact (from article):
    - Sharpe ratio: 1.2 → 2.8 (133% improvement)
    - Max drawdown: -15% → -7% (53% improvement)
    - Novel strategy: Sentiment-momentum hybrid
    - Annual returns: +47% vs market +12%

    Applications:
    - Trading algorithm optimization
    - Hyperparameter tuning
    - Process optimization
    - Resource scheduling
    - Multi-objective optimization
    """)


if __name__ == "__main__":
    main()
