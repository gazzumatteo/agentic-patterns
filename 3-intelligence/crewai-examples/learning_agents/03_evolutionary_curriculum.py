"""
Evolutionary Curriculum Agent Pattern - CrewAI Implementation

This pattern uses population-based search to iteratively generate and evaluate
algorithms or code, evolving solutions over multiple generations.

Business Use Case: Algorithm Optimization (Manufacturing)
Automatic generation and evaluation of algorithmic changes for machine
scheduling efficiency in a production environment.

Pattern: Evolutionary Curriculum Agent
Section: IV - Advanced and Learning Patterns
Framework: CrewAI
"""

import json
import random
from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# --- Constants ---
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


# --- Custom Tools ---
class InitializePopulationTool(BaseTool):
    name: str = "initialize_population"
    description: str = "Initialize the first generation of scheduling algorithms with diverse strategies"

    def _run(self) -> str:
        """Initialize population"""
        population = evolution_engine.initialize_population()
        return json.dumps({
            "message": "Population initialized",
            "generation": 0,
            "population_size": len(population),
            "algorithms": [alg.to_dict() for alg in population]
        }, indent=2)


class EvaluatePopulationTool(BaseTool):
    name: str = "evaluate_population"
    description: str = "Evaluate fitness of all algorithms in current population"

    def _run(self) -> str:
        """Evaluate population fitness"""
        for algorithm in evolution_engine.population:
            evolution_engine.evaluate_fitness(algorithm)

        stats = evolution_engine.get_statistics()
        return json.dumps(stats, indent=2)


class EvolveGenerationTool(BaseTool):
    name: str = "evolve_next_generation"
    description: str = "Evolve to the next generation using selection, crossover, and mutation"

    def _run(self) -> str:
        """Evolve to next generation"""
        new_population = evolution_engine.evolve_generation()
        return json.dumps({
            "message": f"Generation {evolution_engine.generation} created",
            "generation": evolution_engine.generation,
            "population_size": len(new_population),
            "algorithms": [alg.to_dict() for alg in new_population]
        }, indent=2)


class CheckConvergenceTool(BaseTool):
    name: str = "check_convergence"
    description: str = "Check if evolutionary process has converged or should continue"

    def _run(self) -> str:
        """Check convergence"""
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


# Initialize tools
init_tool = InitializePopulationTool()
evaluate_tool = EvaluatePopulationTool()
evolve_tool = EvolveGenerationTool()
convergence_tool = CheckConvergenceTool()


# --- Agents ---
def create_initializer_agent() -> Agent:
    """Create Population Initializer agent"""
    return Agent(
        role="Population Initializer",
        goal="Initialize the first generation of scheduling algorithms with diverse strategies",
        backstory="""You are an Evolutionary Algorithm specialist responsible
        for creating the initial population of scheduling algorithms. You ensure
        diversity by including different strategies: FIFO, Priority-based,
        Shortest Job First, and Hybrid approaches.""",
        tools=[init_tool],
        verbose=True,
        allow_delegation=False
    )


def create_evaluator_agent() -> Agent:
    """Create Fitness Evaluator agent"""
    return Agent(
        role="Fitness Evaluator",
        goal="Evaluate all algorithms in the population and calculate their fitness scores",
        backstory="""You are a Performance Evaluation expert who tests scheduling
        algorithms against simulated workloads. You calculate fitness scores based
        on throughput, average wait time, and fairness metrics.""",
        tools=[evaluate_tool],
        verbose=True,
        allow_delegation=False
    )


def create_evolution_agent() -> Agent:
    """Create Evolution Engine agent"""
    return Agent(
        role="Evolution Engine",
        goal="Create new generations through selection, crossover, and mutation",
        backstory="""You are a Genetic Algorithm specialist who evolves the
        population toward optimal solutions. You select the best performers,
        combine their traits through crossover, and introduce variations through
        mutation to explore the solution space.""",
        tools=[evolve_tool],
        verbose=True,
        allow_delegation=False
    )


def create_convergence_agent() -> Agent:
    """Create Convergence Checker agent"""
    return Agent(
        role="Convergence Checker",
        goal="Determine if the evolutionary process should continue or has converged",
        backstory="""You are an Optimization Analysis expert who monitors the
        evolutionary process. You determine when to stop evolution based on
        convergence criteria: reaching the target fitness score or maximum
        generations.""",
        tools=[convergence_tool],
        verbose=True,
        allow_delegation=False
    )


# --- Main Execution ---
def run_evolutionary_curriculum_demo():
    """Demonstrate evolutionary curriculum pattern"""
    print("=" * 80)
    print("Evolutionary Curriculum Agent Pattern - Algorithm Optimization")
    print("=" * 80)

    print(f"\nObjective: Evolve optimal scheduling algorithm")
    print(f"Population Size: {POPULATION_SIZE}")
    print(f"Max Generations: {MAX_GENERATIONS}")
    print(f"\n{'=' * 80}")

    # Phase 1: Initialize population
    print("Phase 1: Initializing Population...")
    print(f"{'=' * 80}\n")

    initializer = create_initializer_agent()
    init_task = Task(
        description="Initialize the population of scheduling algorithms with diverse strategies",
        agent=initializer,
        expected_output="Population initialized with 4 diverse scheduling algorithms"
    )

    init_crew = Crew(
        agents=[initializer],
        tasks=[init_task],
        process=Process.sequential,
        verbose=True
    )

    try:
        init_result = init_crew.kickoff()
        print(f"\n[Initialization Result] {init_result}\n")
    except Exception as e:
        print(f"\n[Error during initialization]: {e}")
        return

    # Phase 2: Evolution cycles
    print(f"\n{'=' * 80}")
    print("Phase 2: Starting Evolution...")
    print(f"{'=' * 80}\n")

    evaluator = create_evaluator_agent()
    evolver = create_evolution_agent()
    convergence_checker = create_convergence_agent()

    for gen in range(MAX_GENERATIONS):
        print(f"\n{'=' * 80}")
        print(f"Generation {gen + 1}/{MAX_GENERATIONS}")
        print(f"{'=' * 80}")

        # Create tasks for this generation
        eval_task = Task(
            description=f"Evaluate all algorithms in generation {gen} and report fitness scores",
            agent=evaluator,
            expected_output="Fitness evaluation with best, average, and worst scores"
        )

        convergence_task = Task(
            description="Check if evolution has converged or should continue",
            agent=convergence_checker,
            expected_output="Convergence status with should_continue flag",
            context=[eval_task]
        )

        # Create crew for evaluation and convergence check
        eval_crew = Crew(
            agents=[evaluator, convergence_checker],
            tasks=[eval_task, convergence_task],
            process=Process.sequential,
            verbose=True
        )

        try:
            eval_result = eval_crew.kickoff()
            print(f"\n[Evaluation Result] {eval_result}")

            # Check convergence
            stats = evolution_engine.get_statistics()
            if stats.get("best_fitness", 0) > 150 or gen >= MAX_GENERATIONS - 1:
                print(f"\nConvergence achieved or max generations reached!")
                break

            # Evolve to next generation
            print(f"\nEvolving to Generation {gen + 2}...")
            evolve_task = Task(
                description=f"Create generation {gen + 1} through selection, crossover, and mutation",
                agent=evolver,
                expected_output=f"New generation {gen + 1} created with {POPULATION_SIZE} algorithms"
            )

            evolve_crew = Crew(
                agents=[evolver],
                tasks=[evolve_task],
                process=Process.sequential,
                verbose=True
            )

            evolve_result = evolve_crew.kickoff()
            print(f"\n[Evolution Result] {evolve_result}")

        except Exception as e:
            print(f"\n[Error during generation {gen + 1}]: {e}")
            continue

    # Final results
    print(f"\n{'=' * 80}")
    print("Evolution Complete!")
    print(f"{'=' * 80}")

    stats = evolution_engine.get_statistics()
    print(f"\nFinal Statistics:")
    print(f"   Generations: {stats['generation']}")
    print(f"   Best Fitness: {stats['best_fitness']}")
    print(f"   Average Fitness: {stats['average_fitness']:.2f}")

    if evolution_engine.best_ever:
        print(f"\nBest Algorithm Ever:")
        print(f"   ID: {evolution_engine.best_ever.algorithm_id}")
        print(f"   Strategy: {evolution_engine.best_ever.strategy}")
        print(f"   Parameters: {evolution_engine.best_ever.parameters}")
        print(f"   Fitness: {evolution_engine.best_ever.fitness_score}")

    print("\nEvolutionary Curriculum Pattern demonstrated successfully!")
    print("Algorithm population evolved to optimize scheduling performance.")


if __name__ == "__main__":
    run_evolutionary_curriculum_demo()
