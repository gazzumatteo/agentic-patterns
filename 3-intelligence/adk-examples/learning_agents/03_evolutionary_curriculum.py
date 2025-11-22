"""
Evolutionary Curriculum Agent Pattern - Google ADK Implementation

This pattern uses population-based search to iteratively generate and evaluate
algorithms or code, evolving solutions over multiple generations.

Business Use Case: Algorithm Optimization (Manufacturing)
Automatic generation and evaluation of algorithmic changes for machine
scheduling efficiency in a production environment.

Pattern: Evolutionary Curriculum Agent
Section: IV - Advanced and Learning Patterns
Framework: Google ADK
"""

import asyncio
import json
import random
from typing import List, Dict, Any, Tuple
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import FunctionTool
from google.genai.types import Content, Part


# --- Constants ---
APP_NAME = "evolutionary_curriculum_app"
USER_ID = "optimization_user"
MODEL = "gemini-2.5-flash-exp"
POPULATION_SIZE = 4
MAX_GENERATIONS = 5


# --- Evolutionary Algorithm Framework ---
class SchedulingAlgorithm:
    """Represents a scheduling algorithm candidate"""

    def __init__(self, algorithm_id: str, strategy: str, parameters: Dict[str, Any]):
        self.algorithm_id = algorithm_id
        self.strategy = strategy  # e.g., "FIFO", "Priority", "ShortestJob", "Hybrid"
        self.parameters = parameters
        self.fitness_score: float = 0.0
        self.generation: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm_id": self.algorithm_id,
            "strategy": self.strategy,
            "parameters": self.parameters,
            "fitness_score": self.fitness_score,
            "generation": self.generation
        }


class EvolutionaryEngine:
    """Manages the evolutionary process"""

    def __init__(self):
        self.population: List[SchedulingAlgorithm] = []
        self.generation = 0
        self.best_ever: SchedulingAlgorithm = None
        self.history: List[Dict[str, Any]] = []

    def initialize_population(self) -> List[SchedulingAlgorithm]:
        """Create initial population with diverse strategies"""
        strategies = [
            {"strategy": "FIFO", "parameters": {"priority_weight": 0.0}},
            {"strategy": "Priority", "parameters": {"priority_weight": 1.0}},
            {"strategy": "ShortestJob", "parameters": {"time_weight": 1.0}},
            {"strategy": "Hybrid", "parameters": {"priority_weight": 0.5, "time_weight": 0.5}}
        ]

        self.population = [
            SchedulingAlgorithm(
                algorithm_id=f"GEN0_ALG{i}",
                strategy=s["strategy"],
                parameters=s["parameters"]
            )
            for i, s in enumerate(strategies)
        ]
        return self.population

    def evaluate_fitness(self, algorithm: SchedulingAlgorithm) -> float:
        """
        Simulate algorithm performance and calculate fitness score.
        Higher is better. Considers: throughput, wait time, and fairness.
        """
        # Simulate job scheduling with this algorithm
        jobs = [
            {"id": f"J{i}", "priority": random.randint(1, 5), "duration": random.randint(10, 100)}
            for i in range(20)
        ]

        strategy = algorithm.strategy
        params = algorithm.parameters

        # Calculate metrics based on strategy
        if strategy == "FIFO":
            total_wait = sum(i * job["duration"] for i, job in enumerate(jobs))
            throughput = len(jobs) / sum(job["duration"] for job in jobs) * 100
            fairness = 80  # FIFO is fair

        elif strategy == "Priority":
            jobs_sorted = sorted(jobs, key=lambda x: -x["priority"])
            total_wait = sum(i * job["duration"] for i, job in enumerate(jobs_sorted))
            throughput = len(jobs) / sum(job["duration"] for job in jobs) * 120
            fairness = 60  # Less fair

        elif strategy == "ShortestJob":
            jobs_sorted = sorted(jobs, key=lambda x: x["duration"])
            total_wait = sum(i * job["duration"] for i, job in enumerate(jobs_sorted))
            throughput = len(jobs) / sum(job["duration"] for job in jobs) * 140
            fairness = 70

        else:  # Hybrid
            pw = params.get("priority_weight", 0.5)
            tw = params.get("time_weight", 0.5)
            jobs_sorted = sorted(jobs, key=lambda x: -(x["priority"] * pw - x["duration"] * tw / 100))
            total_wait = sum(i * job["duration"] for i, job in enumerate(jobs_sorted))
            throughput = len(jobs) / sum(job["duration"] for job in jobs) * (100 + 40 * tw)
            fairness = 75

        # Fitness = weighted combination
        avg_wait = total_wait / len(jobs)
        fitness = (throughput * 0.4 + (1000 / avg_wait) * 0.3 + fairness * 0.3)

        algorithm.fitness_score = round(fitness, 2)
        return fitness

    def select_parents(self, n: int = 2) -> List[SchedulingAlgorithm]:
        """Select top performing algorithms as parents"""
        sorted_pop = sorted(self.population, key=lambda x: x.fitness_score, reverse=True)
        return sorted_pop[:n]

    def crossover(self, parent1: SchedulingAlgorithm, parent2: SchedulingAlgorithm, child_id: str) -> SchedulingAlgorithm:
        """Create offspring by combining parent strategies"""
        # Combine strategies and parameters
        if random.random() < 0.5:
            strategy = parent1.strategy
        else:
            strategy = parent2.strategy

        # Average parameters
        new_params = {}
        all_keys = set(parent1.parameters.keys()) | set(parent2.parameters.keys())
        for key in all_keys:
            val1 = parent1.parameters.get(key, 0.5)
            val2 = parent2.parameters.get(key, 0.5)
            new_params[key] = (val1 + val2) / 2

        return SchedulingAlgorithm(child_id, strategy, new_params)

    def mutate(self, algorithm: SchedulingAlgorithm) -> SchedulingAlgorithm:
        """Apply random mutations to algorithm parameters"""
        if random.random() < 0.3:  # 30% mutation chance
            for key in algorithm.parameters:
                if random.random() < 0.5:
                    algorithm.parameters[key] += random.uniform(-0.2, 0.2)
                    algorithm.parameters[key] = max(0.0, min(1.0, algorithm.parameters[key]))
        return algorithm

    def evolve_generation(self) -> List[SchedulingAlgorithm]:
        """Create next generation through selection, crossover, and mutation"""
        self.generation += 1

        # Select best parents
        parents = self.select_parents(2)

        # Create new population
        new_population = []

        # Keep best from previous generation (elitism)
        new_population.append(parents[0])

        # Generate offspring
        for i in range(POPULATION_SIZE - 1):
            child_id = f"GEN{self.generation}_ALG{i}"
            child = self.crossover(parents[0], parents[1], child_id)
            child = self.mutate(child)
            child.generation = self.generation
            new_population.append(child)

        self.population = new_population
        return self.population

    def get_statistics(self) -> Dict[str, Any]:
        """Get current generation statistics"""
        if not self.population:
            return {}

        fitness_scores = [alg.fitness_score for alg in self.population]
        best_alg = max(self.population, key=lambda x: x.fitness_score)

        if self.best_ever is None or best_alg.fitness_score > self.best_ever.fitness_score:
            self.best_ever = best_alg

        return {
            "generation": self.generation,
            "population_size": len(self.population),
            "best_fitness": max(fitness_scores),
            "average_fitness": sum(fitness_scores) / len(fitness_scores),
            "worst_fitness": min(fitness_scores),
            "best_algorithm": best_alg.to_dict(),
            "best_ever_fitness": self.best_ever.fitness_score if self.best_ever else 0
        }


# Initialize evolutionary engine
evolution_engine = EvolutionaryEngine()


# --- Tools ---
def initialize_population() -> str:
    """
    Initialize the first generation of scheduling algorithms with diverse strategies.

    Returns:
        JSON string with population details
    """
    population = evolution_engine.initialize_population()
    return json.dumps({
        "message": "Population initialized",
        "generation": 0,
        "population_size": len(population),
        "algorithms": [alg.to_dict() for alg in population]
    }, indent=2)


def evaluate_population() -> str:
    """
    Evaluate fitness of all algorithms in current population.

    Returns:
        JSON string with evaluation results and statistics
    """
    for algorithm in evolution_engine.population:
        evolution_engine.evaluate_fitness(algorithm)

    stats = evolution_engine.get_statistics()
    return json.dumps(stats, indent=2)


def evolve_next_generation() -> str:
    """
    Evolve to the next generation using selection, crossover, and mutation.

    Returns:
        JSON string with new generation details
    """
    new_population = evolution_engine.evolve_generation()
    return json.dumps({
        "message": f"Generation {evolution_engine.generation} created",
        "generation": evolution_engine.generation,
        "population_size": len(new_population),
        "algorithms": [alg.to_dict() for alg in new_population]
    }, indent=2)


def check_convergence() -> str:
    """
    Check if evolutionary process has converged or should continue.

    Returns:
        JSON string with convergence analysis
    """
    stats = evolution_engine.get_statistics()
    converged = (
        evolution_engine.generation >= MAX_GENERATIONS or
        stats.get("best_fitness", 0) > 150  # Target fitness threshold
    )

    return json.dumps({
        "converged": converged,
        "generation": evolution_engine.generation,
        "max_generations": MAX_GENERATIONS,
        "current_best_fitness": stats.get("best_fitness", 0),
        "should_continue": not converged
    }, indent=2)


# Create FunctionTools
init_tool = FunctionTool(func=initialize_population)
evaluate_tool = FunctionTool(func=evaluate_population)
evolve_tool = FunctionTool(func=evolve_next_generation)
convergence_tool = FunctionTool(func=check_convergence)


# --- Agents ---
initialization_agent = LlmAgent(
    model=MODEL,
    name="PopulationInitializer",
    instruction="""You are a Population Initializer agent. Use the initialize_population tool
    to create the first generation of scheduling algorithms. Report the initial population.""",
    tools=[init_tool],
)

evaluation_agent = LlmAgent(
    model=MODEL,
    name="FitnessEvaluator",
    instruction="""You are a Fitness Evaluator agent. Use the evaluate_population tool to
    test all algorithms and calculate their fitness scores. Report the statistics including
    best, average, and worst fitness scores.""",
    tools=[evaluate_tool],
)

evolution_agent = LlmAgent(
    model=MODEL,
    name="EvolutionEngine",
    instruction="""You are an Evolution Engine agent. Use the evolve_next_generation tool to
    create the next generation through selection, crossover, and mutation. Report the new generation.""",
    tools=[evolve_tool],
)

convergence_agent = LlmAgent(
    model=MODEL,
    name="ConvergenceChecker",
    instruction="""You are a Convergence Checker agent. Use the check_convergence tool to
    determine if the evolutionary process should continue. Store 'should_continue' in session state.""",
    tools=[convergence_tool],
)

# Sequential evolution cycle
evolution_cycle = LoopAgent(
    name="EvolutionCycle",
    sub_agents=[evaluation_agent, convergence_agent, evolution_agent],
    exit_condition=lambda session: not session.state.get("should_continue", True)
)


# --- Main Execution ---
async def run_evolutionary_curriculum_demo():
    """Demonstrate evolutionary curriculum pattern"""
    print("=" * 80)
    print("Evolutionary Curriculum Agent Pattern - Algorithm Optimization")
    print("=" * 80)

    # Initialize services
    session_service = InMemorySessionService()

    # Create runner for initialization
    init_runner = Runner(
        agent=initialization_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # Create session
    session_id = "evolution_session_001"
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id
    )

    print("\n🧬 Objective: Evolve optimal scheduling algorithm")
    print(f"📊 Population Size: {POPULATION_SIZE}")
    print(f"🔄 Max Generations: {MAX_GENERATIONS}")
    print("\n" + "=" * 80)

    # Initialize population
    print("Initializing Population...")
    print("=" * 80 + "\n")

    init_message = Content(parts=[Part(text="Initialize the population")], role="user")
    async for event in init_runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=init_message
    ):
        if event.content and event.content.parts and event.content.parts[0].text:
            print(f"[{event.author}] {event.content.parts[0].text}\n")

    # Run evolution cycles
    print("=" * 80)
    print("Starting Evolution...")
    print("=" * 80 + "\n")

    evolution_runner = Runner(
        agent=evolution_cycle,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # Initialize continue flag
    session = await session_service.get_session(APP_NAME, USER_ID, session_id)
    session.state["should_continue"] = True
    await session_service.save_session(session)

    evolve_message = Content(parts=[Part(text="Begin evolutionary optimization")], role="user")
    async for event in evolution_runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=evolve_message
    ):
        if event.content and event.content.parts and event.content.parts[0].text:
            print(f"[{event.author}] {event.content.parts[0].text}\n")

    # Final results
    print("\n" + "=" * 80)
    print("Evolution Complete!")
    print("=" * 80)

    stats = evolution_engine.get_statistics()
    print(f"\n📈 Final Statistics:")
    print(f"   Generations: {stats['generation']}")
    print(f"   Best Fitness: {stats['best_fitness']}")
    print(f"   Average Fitness: {stats['average_fitness']:.2f}")

    if evolution_engine.best_ever:
        print(f"\n🏆 Best Algorithm Ever:")
        print(f"   ID: {evolution_engine.best_ever.algorithm_id}")
        print(f"   Strategy: {evolution_engine.best_ever.strategy}")
        print(f"   Parameters: {evolution_engine.best_ever.parameters}")
        print(f"   Fitness: {evolution_engine.best_ever.fitness_score}")

    print("\n✅ Evolutionary Curriculum Pattern demonstrated successfully!")
    print("   Algorithm population evolved to optimize scheduling performance.")


if __name__ == "__main__":
    asyncio.run(run_evolutionary_curriculum_demo())
