"""
Pattern 34: Maker-Checker Loop
Formal verification with strict turn-based creation and validation.

Business Example: Regulatory Compliance (Investment Bank)
- Regulatory violations: -97%
- Deployment time: 2 weeks → 2 days
- Saved $25M in potential fines

This example demonstrates CrewAI's iterative process for maker-checker validation.

Mermaid Diagram Reference: See diagrams/34_maker_checker.mermaid
"""

from typing import Dict, Any, List
from crewai import Agent, Task, Crew, Process


class MakerCheckerWorkflow:
    """Manages maker-checker validation workflow."""

    def __init__(self):
        self.audit_trail: List[Dict] = []
        self.max_iterations = 5

    def create_maker_checker_crew(self) -> Crew:
        """Create maker-checker crew."""

        maker = Agent(
            role="Algorithm Creator",
            goal="Design trading algorithms that meet requirements",
            backstory="""You design trading algorithms. When you receive
            compliance feedback, you refine your designs to address violations.
            You create clear, well-structured algorithms with proper risk controls.""",
            verbose=True
        )

        checker = Agent(
            role="Compliance Validator",
            goal="Ensure algorithms comply with all regulations",
            backstory="""You are a regulatory compliance expert. You validate
            trading algorithms against strict rules:
            - Position size ≤ 10% portfolio
            - Stop loss present and ≤ 5%
            - Leverage ≤ 2x
            - Circuit breaker for volatility
            - Audit logging enabled

            You provide specific, actionable feedback for violations.""",
            verbose=True
        )

        return Crew(
            agents=[maker, checker],
            tasks=[],  # Created dynamically
            process=Process.sequential,
            verbose=True
        )

    def run_maker_checker_cycle(
        self,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run maker-checker validation cycle."""

        crew = self.create_maker_checker_crew()
        approved = False
        iteration = 0
        feedback_history = []

        print(f"\n{'='*80}")
        print("MAKER-CHECKER LOOP")
        print(f"{'='*80}")

        while not approved and iteration < self.max_iterations:
            iteration += 1

            print(f"\n--- Iteration {iteration} ---")

            # MAKER TASK
            maker_description = f"""
            {'Create' if iteration == 1 else 'Refine'} a trading algorithm:

            Requirements:
            {requirements}

            {'Previous Feedback: ' + feedback_history[-1] if feedback_history else ''}

            Design algorithm with:
            - Entry/exit rules
            - Risk management
            - Position sizing
            - Stop loss mechanism
            - Compliance features

            Output structured algorithm specification.
            """

            maker_task = Task(
                description=maker_description,
                agent=crew.agents[0],
                expected_output="Complete algorithm specification with all required components"
            )

            crew.tasks = [maker_task]
            algorithm_result = crew.kickoff()

            print(f"   MAKER: {'Algorithm created' if iteration == 1 else 'Algorithm refined'}")

            # CHECKER TASK
            checker_description = f"""
            Validate this trading algorithm for compliance:

            Algorithm:
            {algorithm_result}

            Check against regulations:
            1. Position size ≤ 10% portfolio
            2. Stop loss present and ≤ 5%
            3. Leverage ≤ 2x
            4. Circuit breaker for volatility
            5. Audit logging enabled

            Output JSON with:
            - approved: true/false
            - violations: [list of issues]
            - feedback: specific fixes needed

            Be thorough and specific in feedback.
            """

            checker_task = Task(
                description=checker_description,
                agent=crew.agents[1],
                expected_output="Compliance validation with approval status and feedback"
            )

            crew.tasks = [checker_task]
            validation_result = crew.kickoff()

            # Parse validation (simplified)
            result_str = str(validation_result).lower()
            approved = "approved: true" in result_str or "\"approved\": true" in result_str

            print(f"   CHECKER: {'✓ APPROVED' if approved else '✗ REJECTED'}")

            # Record audit trail
            self.audit_trail.append({
                "iteration": iteration,
                "algorithm": str(algorithm_result),
                "validation": str(validation_result),
                "approved": approved
            })

            if not approved:
                feedback_history.append(str(validation_result))

            if approved:
                print(f"\n✓ Algorithm APPROVED after {iteration} iterations")
                break

        return {
            "approved": approved,
            "iterations": iteration,
            "audit_trail": self.audit_trail,
            "final_algorithm": self.audit_trail[-1]["algorithm"] if self.audit_trail else None
        }


def main():
    """Demonstrate maker-checker pattern."""

    print("=" * 80)
    print("Pattern 34: Maker-Checker Loop (CrewAI)")
    print("Iterative Compliance Validation")
    print("=" * 80)

    workflow = MakerCheckerWorkflow()

    scenarios = [
        {
            "name": "Momentum Strategy",
            "requirements": {
                "type": "momentum",
                "target_return": "15% annual",
                "risk_tolerance": "medium"
            }
        },
        {
            "name": "Arbitrage Strategy",
            "requirements": {
                "type": "arbitrage",
                "target_return": "8% annual",
                "risk_tolerance": "low"
            }
        }
    ]

    results = []

    for scenario in scenarios:
        print(f"\n\n{'='*80}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"{'='*80}")

        result = workflow.run_maker_checker_cycle(scenario["requirements"])
        results.append(result)

        print(f"\n📊 Results:")
        print(f"   Status: {'✓ APPROVED' if result['approved'] else '✗ FAILED'}")
        print(f"   Iterations: {result['iterations']}")
        print(f"   Audit Entries: {len(result['audit_trail'])}")

    # Summary
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    approved = sum(1 for r in results if r['approved'])
    total_iters = sum(r['iterations'] for r in results)

    print(f"\n📊 Overall:")
    print(f"   Scenarios: {len(results)}")
    print(f"   Approved: {approved}/{len(results)}")
    print(f"   Avg Iterations: {total_iters/len(results):.1f}")

    print("\n" + "=" * 80)
    print("Pattern Demonstrated: Maker-Checker Loop")
    print("=" * 80)
    print("""
    Key Observations:
    1. Iterative Refinement: Feedback drives improvements
    2. Formal Approval: Explicit validation decisions
    3. Audit Trail: Complete history preserved
    4. Role Separation: Clear maker vs checker roles
    5. Quality Assurance: Rigorous compliance checking

    CrewAI Advantages:
    - Natural role-based separation
    - Sequential task flow
    - Easy feedback integration
    - Clear iteration control
    - Intuitive workflow design

    Business Impact:
    - Regulatory violations: -97%
    - Deployment: 2 weeks → 2 days
    - Audit success: 100%
    - Savings: $25M in fines prevented

    Applications:
    - Financial compliance
    - Code review
    - Legal document validation
    - Medical protocol verification
    """)


if __name__ == "__main__":
    main()
