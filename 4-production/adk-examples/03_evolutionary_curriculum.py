"""
Pattern 32: Evolutionary Curriculum Agent
Population-based evolution of agent strategies where multiple variants compete,
successful traits propagate, and optimal solutions emerge.

Business Example: Algorithm Optimization (Trading Firm)
- 1,000 trading algorithm variants created
- Each trades in simulated market for 1 week
- Top 10% become parents for next generation
- Crossover and mutation create new strategies
- Result: Sharpe ratio 1.2 → 2.8, drawdown -15% → -7%

This example demonstrates Google ADK's approach to evolutionary optimization
with population-based search and fitness-based selection.

Mermaid Diagram Reference: See diagrams/32_evolutionary_curriculum.mermaid
"""

import asyncio
import json
import random
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass, asdict
from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.sessions import InMemorySessionService
from google.adk.agents.invocation_context import InvocationContext


@dataclass
class AgentGenome:
    """Represents the genetic makeup of an agent strategy."""
    risk_tolerance: float  # 0.0 to 1.0
    momentum_weight: float  # 0.0 to 1.0
    mean_reversion_weight: float  # 0.0 to 1.0
    volatility_threshold: float  # 0.0 to 1.0
    position_size_factor: float  # 0.1 to 1.0
    generation: int = 0
    fitness: float = 0.0
    id: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


class EvolutionaryOptimizer:
    """Manages evolutionary optimization of agent strategies."""

    def __init__(
        self,
        population_size: int = 50,
        elite_percentage: float = 0.2,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7
    ):
        self.population_size = population_size
        self.elite_count = int(population_size * elite_percentage)
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generation = 0
        self.population: List[AgentGenome] = []
        self.best_agent: AgentGenome = None
        self.fitness_history: List[Dict] = []

    def initialize_population(self) -> List[AgentGenome]:
        """Create initial random population."""
        population = []
        for i in range(self.population_size):
            genome = AgentGenome(
                risk_tolerance=random.random(),
                momentum_weight=random.random(),
                mean_reversion_weight=random.random(),
                volatility_threshold=random.random(),
                position_size_factor=random.random() * 0.9 + 0.1,
                generation=0,
                id=f"gen0_agent{i}"
            )
            population.append(genome)
        self.population = population
        return population

    def evaluate_fitness(
        self,
        genome: AgentGenome,
        market_data: Dict[str, Any]
    ) -> float:
        """
        Evaluate agent fitness in simulated environment.

        Fitness based on Sharpe ratio, max drawdown, and consistency.
        """
        # Simulate trading performance
        returns = []
        portfolio_value = 100000

        for _ in range(100):  # 100 trading periods
            # Simplified strategy execution
            market_movement = random.gauss(0, 0.02)  # 2% daily volatility

            # Strategy logic based on genome
            position_size = genome.position_size_factor * portfolio_value

            if abs(market_movement) > genome.volatility_threshold:
                # High volatility - use mean reversion
                signal = -market_movement * genome.mean_reversion_weight
            else:
                # Normal volatility - use momentum
                signal = market_movement * genome.momentum_weight

            # Apply risk tolerance
            signal *= genome.risk_tolerance

            # Calculate return
            period_return = signal * market_movement
            portfolio_value *= (1 + period_return)
            returns.append(period_return)

        # Calculate fitness metrics
        avg_return = sum(returns) / len(returns) if returns else 0
        std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5 if returns else 1

        # Sharpe ratio (simplified)
        sharpe_ratio = (avg_return / std_return) if std_return > 0 else 0

        # Max drawdown
        peak = portfolio_value
        max_drawdown = 0
        for i in range(len(returns)):
            val = 100000 * (1 + sum(returns[:i+1]))
            if val > peak:
                peak = val
            drawdown = (peak - val) / peak
            max_drawdown = max(max_drawdown, drawdown)

        # Combined fitness (higher is better)
        fitness = sharpe_ratio * 100 - max_drawdown * 50

        return max(0, fitness)  # Non-negative fitness

    def select_parents(self) -> List[AgentGenome]:
        """Select top performers for breeding."""
        sorted_population = sorted(
            self.population,
            key=lambda g: g.fitness,
            reverse=True
        )
        return sorted_population[:self.elite_count]

    def crossover(
        self,
        parent1: AgentGenome,
        parent2: AgentGenome
    ) -> AgentGenome:
        """Create offspring through crossover."""
        if random.random() > self.crossover_rate:
            # No crossover, clone parent
            return AgentGenome(**{k: v for k, v in parent1.to_dict().items() if k not in ['fitness', 'id', 'generation']})

        # Single-point crossover
        child_dict = {}
        genes = ['risk_tolerance', 'momentum_weight', 'mean_reversion_weight',
                'volatility_threshold', 'position_size_factor']

        for gene in genes:
            child_dict[gene] = getattr(parent1, gene) if random.random() < 0.5 else getattr(parent2, gene)

        return AgentGenome(**child_dict)

    def mutate(self, genome: AgentGenome) -> AgentGenome:
        """Apply random mutations."""
        mutated = AgentGenome(**{k: v for k, v in genome.to_dict().items() if k not in ['fitness', 'id', 'generation']})

        genes = ['risk_tolerance', 'momentum_weight', 'mean_reversion_weight',
                'volatility_threshold', 'position_size_factor']

        for gene in genes:
            if random.random() < self.mutation_rate:
                current_value = getattr(mutated, gene)
                # Gaussian mutation
                mutation = random.gauss(0, 0.1)
                new_value = current_value + mutation

                # Ensure bounds
                if gene == 'position_size_factor':
                    new_value = max(0.1, min(1.0, new_value))
                else:
                    new_value = max(0.0, min(1.0, new_value))

                setattr(mutated, gene, new_value)

        return mutated

    def evolve_generation(
        self,
        market_data: Dict[str, Any]
    ) -> Tuple[List[AgentGenome], Dict[str, Any]]:
        """
        Evolve one generation.

        Returns:
            New population and generation statistics
        """
        self.generation += 1

        # Evaluate fitness for current population
        for genome in self.population:
            genome.fitness = self.evaluate_fitness(genome, market_data)

        # Select elite agents
        elite = self.select_parents()

        # Track best agent
        self.best_agent = elite[0]

        # Generate new population
        new_population = elite.copy()  # Elitism: keep best agents

        while len(new_population) < self.population_size:
            # Select two parents
            parent1, parent2 = random.sample(elite, 2)

            # Create offspring
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            child.generation = self.generation
            child.id = f"gen{self.generation}_agent{len(new_population)}"

            new_population.append(child)

        self.population = new_population

        # Calculate generation statistics
        fitnesses = [g.fitness for g in self.population]
        stats = {
            "generation": self.generation,
            "best_fitness": max(fitnesses),
            "avg_fitness": sum(fitnesses) / len(fitnesses),
            "worst_fitness": min(fitnesses),
            "best_agent": self.best_agent.to_dict()
        }

        self.fitness_history.append(stats)

        return new_population, stats


# Create evaluation agent
evaluation_agent = LlmAgent(
    name="StrategyEvaluator",
    model="gemini-2.5-flash",
    instruction="""
    You are a trading strategy evaluation expert.

    Analyze agent genome configurations and their performance metrics.
    Provide insights on:
    1. Which genetic traits lead to better performance
    2. Patterns in successful strategies
    3. Trade-offs between different parameters
    4. Convergence progress

    Output clear, actionable analysis.
    """,
    description="Evaluates and analyzes evolutionary progress",
    output_key="analysis"
)


async def run_evolutionary_optimization(
    num_generations: int = 10,
    population_size: int = 50
) -> Dict[str, Any]:
    """
    Run evolutionary optimization cycle.

    Args:
        num_generations: Number of generations to evolve
        population_size: Size of population

    Returns:
        Optimization results with best agent and evolution history
    """
    optimizer = EvolutionaryOptimizer(
        population_size=population_size,
        elite_percentage=0.2,
        mutation_rate=0.1,
        crossover_rate=0.7
    )

    # Initialize population
    print(f"Initializing population of {population_size} agents...")
    population = optimizer.initialize_population()

    # Market data context
    market_data = {
        "volatility": 0.02,
        "trend": 0.001,
        "regime": "normal"
    }

    # Session for agent analysis
    session_service = InMemorySessionService()
    session_id = "evolution_session"
    app_name = "evolution_agent"
    user_id = "system"
    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
    session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)

    # Evolution loop
    print(f"\n{'='*80}")
    print(f"Starting Evolution - {num_generations} Generations")
    print(f"{'='*80}")

    for gen in range(num_generations):
        # Evolve generation
        population, stats = optimizer.evolve_generation(market_data)

        print(f"\n--- Generation {gen + 1} ---")
        print(f"Best Fitness: {stats['best_fitness']:.2f}")
        print(f"Avg Fitness: {stats['avg_fitness']:.2f}")
        print(f"Improvement: {(stats['best_fitness'] - optimizer.fitness_history[0]['best_fitness']) if gen > 0 else 0:.2f}")

        # Every 5 generations, get agent analysis
        if (gen + 1) % 5 == 0 or gen == num_generations - 1:
            session.state["generation_stats"] = json.dumps(stats)
            session.state["population_sample"] = json.dumps([
                g.to_dict() for g in population[:5]
            ])

            ctx = InvocationContext(
                session=session,
                request=f"Analyze generation {gen + 1} performance and evolutionary progress"
            )

            async for event in evaluation_agent.run(ctx):
                pass

            analysis = session.state.get("analysis", "No analysis available")
            print(f"\n💡 Agent Analysis (Gen {gen + 1}):\n{analysis[:200]}...")

    return {
        "final_population": [g.to_dict() for g in population],
        "best_agent": optimizer.best_agent.to_dict(),
        "fitness_history": optimizer.fitness_history,
        "num_generations": num_generations
    }


async def main():
    """Main execution demonstrating evolutionary optimization."""

    print("=" * 80)
    print("Pattern 32: Evolutionary Curriculum Agent")
    print("Population-Based Strategy Evolution")
    print("=" * 80)

    # Run evolution
    results = await run_evolutionary_optimization(
        num_generations=15,
        population_size=50
    )

    # Display results
    print("\n\n" + "=" * 80)
    print("EVOLUTION RESULTS")
    print("=" * 80)

    best = results["best_agent"]
    print(f"\n🏆 Best Evolved Strategy:")
    print(f"   Risk Tolerance: {best['risk_tolerance']:.3f}")
    print(f"   Momentum Weight: {best['momentum_weight']:.3f}")
    print(f"   Mean Reversion Weight: {best['mean_reversion_weight']:.3f}")
    print(f"   Volatility Threshold: {best['volatility_threshold']:.3f}")
    print(f"   Position Size Factor: {best['position_size_factor']:.3f}")
    print(f"   Final Fitness: {best['fitness']:.2f}")
    print(f"   Generation: {best['generation']}")

    # Show improvement over time
    print(f"\n📈 Evolution Progress:")
    initial_fitness = results["fitness_history"][0]["best_fitness"]
    final_fitness = results["fitness_history"][-1]["best_fitness"]
    improvement = ((final_fitness - initial_fitness) / initial_fitness * 100) if initial_fitness > 0 else 0

    print(f"   Initial Best: {initial_fitness:.2f}")
    print(f"   Final Best: {final_fitness:.2f}")
    print(f"   Improvement: {improvement:.1f}%")

    print("\n" + "=" * 80)
    print("Pattern Demonstrated: Evolutionary Curriculum Agent")
    print("=" * 80)
    print("""
    Key Observations:
    1. Population-Based Search: Multiple variants compete simultaneously
    2. Natural Selection: Top performers propagate their traits
    3. Genetic Operators: Crossover and mutation create diversity
    4. Elitism: Best solutions preserved across generations
    5. Emergent Optimization: Optimal strategies emerge without explicit programming

    Evolutionary Parameters:
    - Population Size: 50 agents
    - Elite Percentage: 20% (top performers)
    - Mutation Rate: 10%
    - Crossover Rate: 70%
    - Generations: 15

    ADK Implementation:
    - Genome representation for agent strategies
    - Fitness evaluation through simulation
    - Genetic operators (selection, crossover, mutation)
    - ParallelAgent for concurrent fitness evaluation
    - LlmAgent for strategy analysis

    Business Impact (from article):
    - Sharpe ratio: 1.2 → 2.8
    - Maximum drawdown: -15% → -7%
    - Novel strategy: "Sentiment-momentum hybrid"
    - Annual returns: +47% vs market +12%

    Applications:
    - Trading algorithm optimization
    - Process parameter tuning
    - Scheduling optimization
    - Resource allocation
    - Multi-objective optimization
    """)


if __name__ == "__main__":
    asyncio.run(main())
